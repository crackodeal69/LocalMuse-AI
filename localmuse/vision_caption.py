from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from PIL import Image


class FlorenceCaptioner:
    """Generate LoRA dataset captions with Florence-2."""

    SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
    DEFAULT_MODEL_ID = "microsoft/Florence-2-large"
    TASK = "<DETAILED_CAPTION>"

    def __init__(
        self,
        trigger_token: str,
        model_id: str = DEFAULT_MODEL_ID,
        device: str | None = None,
        cache_dir: str | Path | None = None,
    ) -> None:
        if not trigger_token.strip():
            raise ValueError("trigger_token must not be empty")

        if cache_dir is not None:
            os.environ["HF_HOME"] = str(Path(cache_dir).resolve())

        try:
            import torch
            from transformers import AutoModelForCausalLM, AutoProcessor
        except ImportError as error:
            raise ImportError(
                "FlorenceCaptioner requires torch and transformers. "
                "Use the project's captioning environment."
            ) from error

        self.trigger_token = trigger_token.strip()
        self._torch = torch
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        dtype = torch.float16 if self.device.startswith("cuda") else torch.float32
        model_kwargs: dict[str, Any] = {
            "torch_dtype": dtype,
            "trust_remote_code": True,
            "attn_implementation": "eager",
        }
        if cache_dir is not None:
            model_kwargs["cache_dir"] = str(cache_dir)

        processor_kwargs: dict[str, Any] = {"trust_remote_code": True}
        if cache_dir is not None:
            processor_kwargs["cache_dir"] = str(cache_dir)

        self.processor = AutoProcessor.from_pretrained(model_id, **processor_kwargs)
        self.model = AutoModelForCausalLM.from_pretrained(model_id, **model_kwargs)
        self.model.to(self.device).eval()

    def caption_image(self, image_path: str | Path) -> str:
        """Return a trigger-prefixed caption for one image."""
        image_path = Path(image_path)
        if not image_path.is_file():
            raise FileNotFoundError(f"Image not found: {image_path}")
        if image_path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(f"Unsupported file type: {image_path.suffix}")

        with Image.open(image_path) as image:
            image = image.convert("RGB")
            inputs = self.processor(text=self.TASK, images=image, return_tensors="pt")

        inputs["input_ids"] = inputs["input_ids"].to(self.device)
        inputs["pixel_values"] = inputs["pixel_values"].to(
            device=self.device,
            dtype=next(self.model.parameters()).dtype,
        )

        with self._torch.inference_mode():
            generated_ids = self.model.generate(
                **inputs,
                max_new_tokens=80,
                num_beams=1,
                use_cache=False,
            )

        raw_text = self.processor.batch_decode(generated_ids, skip_special_tokens=False)[0]
        result = self.processor.post_process_generation(
            raw_text,
            task=self.TASK,
            image_size=image.size,
        )
        caption = str(result[self.TASK]).strip()
        return f"{self.trigger_token}, {caption}"

    def write_prompt_file(
        self,
        image_path: str | Path,
        output_path: str | Path | None = None,
    ) -> Path:
        """Write a trigger-prefixed caption to a same-name TXT file."""
        image_path = Path(image_path)
        output_path = Path(output_path) if output_path is not None else image_path.with_suffix(".txt")
        output_path.write_text(self.caption_image(image_path) + "\n", encoding="utf-8")
        return output_path

    def write_prompts_for_directory(self, directory: str | Path) -> list[Path]:
        """Caption every supported image in a directory."""
        directory = Path(directory)
        if not directory.is_dir():
            raise NotADirectoryError(f"Directory not found: {directory}")

        prompt_paths = []
        for image_path in sorted(directory.iterdir()):
            if image_path.is_file() and image_path.suffix.lower() in self.SUPPORTED_EXTENSIONS:
                prompt_paths.append(self.write_prompt_file(image_path))
        return prompt_paths