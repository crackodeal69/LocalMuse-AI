from __future__ import annotations

import argparse
import base64
import json
import shutil
import time
import urllib.error
import urllib.request
from pathlib import Path


DEFAULT_PROMPT = (
    "nag_person, realistic portrait photo, looking at the camera, neutral expression, "
    "soft natural window light, simple indoor background, detailed face"
)
DEFAULT_NEGATIVE_PROMPT = (
    "blurry, low quality, distorted face, deformed eyes, extra fingers, "
    "duplicate person, text, watermark"
)


def request_json(url: str, payload: dict | None = None) -> dict:
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=600) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        details = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Forge API error {error.code} for {url}: {details}") from error


def wait_for_api(api_url: str, timeout_seconds: int = 300) -> None:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        try:
            request_json(f"{api_url}/sdapi/v1/options")
            return
        except (urllib.error.URLError, TimeoutError):
            time.sleep(2)
    raise TimeoutError(f"Forge API did not become available: {api_url}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate fixed-seed images for LoRA checkpoint comparison.")
    parser.add_argument("--checkpoint-dir", type=Path, default=Path("models/lora"))
    parser.add_argument("--forge-lora-dir", type=Path, default=Path(r"E:\ai_work\webui\models\Lora"))
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/generation_comparison"))
    parser.add_argument("--api-url", default="http://127.0.0.1:7860")
    parser.add_argument("--base-model", default="realvisxlV50_v50Bakedvae.safetensors")
    parser.add_argument("--prompt", default=DEFAULT_PROMPT)
    parser.add_argument("--negative-prompt", default=DEFAULT_NEGATIVE_PROMPT)
    parser.add_argument("--seed", type=int, default=241109)
    parser.add_argument("--seeds", nargs="+", type=int, default=None)
    parser.add_argument("--steps", type=int, default=30)
    parser.add_argument("--cfg-scale", type=float, default=6.0)
    parser.add_argument("--width", type=int, default=1024)
    parser.add_argument("--height", type=int, default=1024)
    parser.add_argument("--weight", type=float, default=0.8)
    parser.add_argument("--weights", nargs="+", type=float, default=None)
    parser.add_argument("--hires", action="store_true")
    parser.add_argument("--hr-upscaler", default="R-ESRGAN 4x+")
    parser.add_argument("--hr-steps", type=int, default=10)
    parser.add_argument("--denoising-strength", type=float, default=0.25)
    parser.add_argument("--hr-scale", type=float, default=1.5)
    parser.add_argument("--epochs", nargs="+", type=int, default=[3, 5, 7, 8, 9, 10])
    args = parser.parse_args()

    wait_for_api(args.api_url)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    base_options = request_json(f"{args.api_url}/sdapi/v1/options")
    base_options["sd_model_checkpoint"] = args.base_model
    request_json(f"{args.api_url}/sdapi/v1/options", base_options)

    seeds = args.seeds or [args.seed]
    weights = args.weights or [args.weight]
    for epoch in args.epochs:
        suffix = "" if epoch == 10 else f"-{epoch:06d}"
        checkpoint = f"nag_person_dataset_v01{suffix}.safetensors"
        source = args.checkpoint_dir / checkpoint
        if not source.is_file():
            raise FileNotFoundError(f"Checkpoint not found: {source}")
        installed_checkpoint = args.forge_lora_dir / checkpoint
        if not installed_checkpoint.exists():
            shutil.copy2(source, installed_checkpoint)

        for weight in weights:
            prompt = f"<lora:{Path(checkpoint).stem}:{weight}>, {args.prompt}"
            weight_label = f"{weight:.2f}".replace(".", "_")
            epoch_dir = args.output_dir / f"epoch_{epoch:02d}_weight_{weight_label}"
            epoch_dir.mkdir(parents=True, exist_ok=True)
            for seed in seeds:
                payload = {
                    "prompt": prompt,
                    "negative_prompt": args.negative_prompt,
                    "seed": seed,
                    "steps": args.steps,
                    "cfg_scale": args.cfg_scale,
                    "width": args.width,
                    "height": args.height,
                    "sampler_name": "DPM++ 2M Karras",
                    "batch_size": 1,
                    "n_iter": 1,
                }
                if args.hires:
                    payload.update(
                        {
                            "enable_hr": True,
                            "hr_upscaler": args.hr_upscaler,
                            "hr_second_pass_steps": args.hr_steps,
                            "denoising_strength": args.denoising_strength,
                            "hr_scale": args.hr_scale,
                            "hr_additional_modules": ["Use same choices"],
                        }
                    )
                result = request_json(f"{args.api_url}/sdapi/v1/txt2img", payload)
                for index, encoded in enumerate(result.get("images", []), start=1):
                    image_data = encoded.split(",", 1)[-1]
                    (epoch_dir / f"seed_{seed}_{index}.png").write_bytes(base64.b64decode(image_data))
                (epoch_dir / f"metadata_seed_{seed}.json").write_text(
                    json.dumps(payload, indent=2) + "\n", encoding="utf-8"
                )
                print(f"Generated epoch {epoch}, weight {weight}, seed {seed}: {epoch_dir}")


if __name__ == "__main__":
    main()