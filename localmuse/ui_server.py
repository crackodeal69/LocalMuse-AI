from __future__ import annotations

import base64
import json
import mimetypes
import os
import shutil
import subprocess
import threading
import time
import uuid
import urllib.error
import urllib.request
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from .presets import PresetStore
from .dataset_workflow import TRAINING_PROFILES, prepare_training_dataset, scan_dataset, write_training_config


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PRESET_PATH = PROJECT_ROOT / "configs" / "generation_presets.json"
USER_PRESET_PATH = PROJECT_ROOT / "configs" / "user_presets.json"
OUTPUT_ROOT = PROJECT_ROOT / "outputs" / "localmuse_ui"
FORGE_ROOT = Path(os.environ.get("LOCALMUSE_FORGE_ROOT", r"E:\ai_work\webui"))
FORGE_LORA_DIR = Path(os.environ.get("LOCALMUSE_FORGE_LORA_DIR", str(FORGE_ROOT / "models" / "Lora")))
FORGE_API_URL = os.environ.get("LOCALMUSE_FORGE_API_URL", "http://127.0.0.1:7860")
WEB_ROOT = PROJECT_ROOT / "localmuse" / "web"
DATASET_ROOT = PROJECT_ROOT / "data" / "lora_dataset_ui"
PROJECT_LORA_DIR = PROJECT_ROOT / "models" / "lora"
KOHYA_ROOT = Path(os.environ.get("LOCALMUSE_KOHYA_ROOT", r"E:\ai_work\kohya_ss\sd-scripts"))
KOHYA_VENV = Path(os.environ.get("LOCALMUSE_KOHYA_VENV", str(KOHYA_ROOT.parent / ".venv")))
CAPTION_PYTHON = Path(os.environ.get("LOCALMUSE_CAPTION_PYTHON", str(KOHYA_VENV / "Scripts" / "python.exe")))
ACCELERATE = Path(os.environ.get("LOCALMUSE_ACCELERATE", str(KOHYA_VENV / "Scripts" / "accelerate.exe")))
JOBS: dict[str, subprocess.Popen[str]] = {}


def available_loras() -> list[str]:
    """Return project-owned and Forge-installed LoRAs without duplicates."""
    names = {
        path.name
        for directory in (PROJECT_LORA_DIR, FORGE_LORA_DIR)
        if directory.is_dir()
        for path in directory.glob("*.safetensors")
    }
    return sorted(names, key=str.casefold)


def request_json(path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        f"{FORGE_API_URL}{path}",
        data=data,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=600) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Forge API {error.code}: {detail}") from error


def interrupt_generation() -> None:
    request_json("/sdapi/v1/interrupt", {})


def shutdown_localmuse() -> None:
    """Ask the tray owner to stop all services, or stop this UI process."""
    tray_pid = os.environ.get("LOCALMUSE_TRAY_PID")
    if tray_pid and tray_pid.isdigit():
        subprocess.Popen(
            ["powershell.exe", "-NoProfile", "-Command", f"Start-Sleep -Milliseconds 300; Stop-Process -Id {tray_pid} -Force"],
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
    else:
        threading.Thread(target=lambda: (time.sleep(0.3), os._exit(0)), daemon=True).start()


def build_prompt(trigger: str, prompt: str, preset: dict[str, Any]) -> str:
    parts = [trigger.strip(), preset.get("prompt_prefix", "").strip(), prompt.strip()]
    return ", ".join(part for part in parts if part)


def add_eye_color(prompt: str, eye_color: str) -> str:
    eye_color = eye_color.strip().lower()
    if not eye_color or eye_color == "none":
        return prompt
    return f"{prompt}, {eye_color} eyes"


def generate_image(payload: dict[str, Any]) -> dict[str, Any]:
    preset = payload.get("preset", {})
    model = str(payload.get("base_model") or preset.get("base_model", ""))
    options = request_json("/sdapi/v1/options")
    if model:
        options["sd_model_checkpoint"] = model
        request_json("/sdapi/v1/options", options)

    lora_name = str(payload.get("lora_name", "")).strip()
    lora_weight = float(payload.get("lora_weight", preset.get("lora_weight", 0.9)))
    prompt = build_prompt(str(payload.get("trigger", "nag_person")), str(payload.get("prompt", "")), preset)
    prompt = add_eye_color(prompt, str(payload.get("eye_color", "none")))
    if lora_name:
        prompt = f"<lora:{Path(lora_name).stem}:{lora_weight}>, {prompt}"

    batch_size = max(1, min(100, int(payload.get("batch_size", 1))))
    request_payload: dict[str, Any] = {
        "prompt": prompt,
        "negative_prompt": str(payload.get("negative_prompt") or preset.get("negative_prompt", "")),
        "seed": int(payload.get("seed", -1)),
        "steps": int(payload.get("steps", preset.get("steps", 30))),
        "cfg_scale": float(payload.get("cfg_scale", preset.get("cfg_scale", 4.0))),
        "width": int(payload.get("width", preset.get("width", 512))),
        "height": int(payload.get("height", preset.get("height", 912))),
        "sampler_name": str(payload.get("sampler", preset.get("sampler", "DPM++ 2M Karras"))),
        "batch_size": batch_size,
        "n_iter": 1,
    }
    if payload.get("hires", preset.get("hires", False)):
        request_payload.update(
            {
                "enable_hr": True,
                "hr_upscaler": payload.get("hr_upscaler", preset.get("hr_upscaler", "R-ESRGAN 4x+")),
                "hr_second_pass_steps": int(payload.get("hr_steps", preset.get("hr_steps", 10))),
                "denoising_strength": float(
                    payload.get("denoising_strength", preset.get("denoising_strength", 0.25))
                ),
                "hr_scale": float(payload.get("hr_scale", preset.get("hr_scale", 1.5))),
                "hr_additional_modules": ["Use same choices"],
            }
        )

    result = request_json("/sdapi/v1/txt2img", request_payload)
    output_dir = OUTPUT_ROOT / datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir.mkdir(parents=True, exist_ok=True)
    image_paths = []
    for index, encoded in enumerate(result.get("images", []), start=1):
        image_path = output_dir / f"image_{index}.png"
        image_path.write_bytes(base64.b64decode(encoded.split(",", 1)[-1]))
        image_paths.append(str(image_path.relative_to(PROJECT_ROOT)).replace("\\", "/"))
    (output_dir / "metadata.json").write_text(
        json.dumps(request_payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return {"images": image_paths, "folder": str(output_dir), "metadata": request_payload}


def start_caption_job(directory: str, trigger_token: str) -> str:
    job_id = uuid.uuid4().hex[:10]
    process = subprocess.Popen(
        [
            str(CAPTION_PYTHON),
            "-m",
            "tools.generate_captions",
            directory,
            "--trigger",
            trigger_token,
            "--cache-dir",
            str(PROJECT_ROOT / "models" / "huggingface"),
        ],
        cwd=PROJECT_ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
        text=True,
    )
    JOBS[job_id] = process
    return job_id


def start_training_job(config_path: Path) -> str:
    job_id = uuid.uuid4().hex[:10]
    process = subprocess.Popen(
        [str(ACCELERATE), "launch", "--num_cpu_threads_per_process=2", "sdxl_train_network.py", "--config_file", str(config_path)],
        cwd=KOHYA_ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
        text=True,
    )
    JOBS[job_id] = process
    return job_id


def job_status() -> dict[str, str | None]:
    result = {}
    for job_id, process in list(JOBS.items()):
        code = process.poll()
        result[job_id] = "running" if code is None else f"finished:{code}"
    return result


class LocalMuseHandler(BaseHTTPRequestHandler):
    store = PresetStore(PRESET_PATH, USER_PRESET_PATH)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/api/presets":
            self.send_json({"presets": self.store.list_presets(include_experimental=True)})
            return
        if parsed.path == "/api/loras":
            self.send_json({"loras": available_loras()})
            return
        if parsed.path == "/api/health":
            try:
                request_json("/sdapi/v1/options")
                self.send_json({"forge": True})
            except Exception as error:
                self.send_json({"forge": False, "error": str(error)}, status=503)
            return
        if parsed.path == "/api/dataset":
            from urllib.parse import parse_qs

            query = parse_qs(parsed.query)
            self.send_json(scan_dataset(query.get("path", [""])[0]))
            return
        if parsed.path == "/api/jobs":
            self.send_json({"jobs": job_status()})
            return
        if parsed.path == "/api/training/profiles":
            self.send_json({"profiles": TRAINING_PROFILES})
            return
        self.serve_web_file(parsed.path)

    def do_POST(self) -> None:
        try:
            payload = self.read_json()
            if self.path == "/api/presets":
                self.store.save_user_preset(payload)
                self.send_json({"saved": True})
                return
            if self.path == "/api/generate":
                self.send_json(generate_image(payload))
                return
            if self.path == "/api/generate/stop":
                interrupt_generation()
                self.send_json({"stopped": True})
                return
            if self.path == "/api/shutdown":
                self.send_json({"shutdown": True})
                shutdown_localmuse()
                return
            if self.path == "/api/open-folder":
                folder = (PROJECT_ROOT / str(payload["folder"])).resolve()
                output_root = OUTPUT_ROOT.resolve()
                if output_root not in folder.parents or not folder.is_dir():
                    raise ValueError("Only LocalMuse output folders can be opened")
                os.startfile(folder)
                self.send_json({"opened": True})
                return
            if self.path == "/api/open-file":
                file_path = (PROJECT_ROOT / str(payload["path"])).resolve()
                output_root = OUTPUT_ROOT.resolve()
                if output_root not in file_path.parents or not file_path.is_file():
                    raise ValueError("Only LocalMuse output files can be opened")
                os.startfile(file_path)
                self.send_json({"opened": True})
                return
            if self.path == "/api/dataset/captions":
                job_id = start_caption_job(str(payload["directory"]), str(payload["trigger_token"]))
                self.send_json({"job_id": job_id, "status": "started"})
                return
            if self.path == "/api/dataset/prepare":
                result = prepare_training_dataset(
                    payload["directory"],
                    DATASET_ROOT,
                    str(payload["trigger_token"]),
                    int(payload.get("repeats", 10)),
                    str(payload.get("version", "dataset_v02")),
                )
                result["dataset_root"] = str(Path(result["target_directory"]).parent)
                self.send_json(result)
                return
            if self.path == "/api/training/start":
                model_path = Path(str(payload["model_path"])).expanduser().resolve()
                if not model_path.is_file():
                    raise FileNotFoundError(f"Base model not found: {model_path}")
                config_path = write_training_config(
                    PROJECT_ROOT / "configs" / "lora_ui_training.toml",
                    str(model_path),
                    str(payload["dataset_root"]),
                    str(PROJECT_ROOT / "models" / "lora"),
                    str(PROJECT_ROOT / "outputs" / "logs" / "localmuse_training"),
                    int(payload.get("epochs", 0)),
                    str(payload.get("profile_id", "balanced")),
                )
                job_id = start_training_job(config_path)
                self.send_json({"job_id": job_id, "config": str(config_path), "status": "started"})
                return
            self.send_json({"error": "Not found"}, status=404)
        except Exception as error:
            self.send_json({"error": str(error)}, status=500)

    def read_json(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0"))
        return json.loads(self.rfile.read(length).decode("utf-8"))

    def send_json(self, payload: dict[str, Any], status: int = 200) -> None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def serve_web_file(self, path: str) -> None:
        relative_path = "index.html" if path in {"", "/"} else path.lstrip("/")
        if relative_path.startswith("outputs/"):
            file_path = (PROJECT_ROOT / relative_path).resolve()
            allowed_root = (PROJECT_ROOT / "outputs").resolve()
        else:
            file_path = (WEB_ROOT / relative_path).resolve()
            allowed_root = WEB_ROOT.resolve()
        if allowed_root not in file_path.parents or not file_path.is_file():
            self.send_json({"error": "Not found"}, status=404)
            return
        data = file_path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", mimetypes.guess_type(file_path.name)[0] or "application/octet-stream")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def run(host: str = "127.0.0.1", port: int = 7861) -> None:
    server = ThreadingHTTPServer((host, port), LocalMuseHandler)
    print(f"LocalMuse UI: http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    run()
