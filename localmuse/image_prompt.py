from __future__ import annotations

from pathlib import Path
from typing import Any

from PIL import Image


class ImagePromptGenerator:
    """Generate a simple descriptive prompt for a local image."""

    SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

    def generate_for_file(self, image_path: str | Path) -> dict[str, Any]:
        path = Path(image_path)

        if not path.exists():
            raise FileNotFoundError(f"Image not found: {path}")

        if path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(
                f"Unsupported file type: {path.suffix}. Supported: {sorted(self.SUPPORTED_EXTENSIONS)}"
            )

        with Image.open(path) as img:
            width, height = img.size
            fmt = img.format or "UNKNOWN"
            prompt = self._build_prompt(path.name, width, height, fmt)

        return {
            "file_name": path.name,
            "path": str(path),
            "format": fmt,
            "size": (width, height),
            "prompt": prompt,
        }

    def write_prompt_file(
        self,
        image_path: str | Path,
        output_path: str | Path | None = None,
    ) -> Path:
        """Write an image prompt to a same-name TXT sidecar file."""
        image_path = Path(image_path)
        result = self.generate_for_file(image_path)
        prompt_path = Path(output_path) if output_path is not None else image_path.with_suffix(".txt")
        prompt_path.write_text(result["prompt"] + "\n", encoding="utf-8")
        return prompt_path

    def write_prompts_for_directory(self, directory: str | Path) -> list[Path]:
        """Write sidecar TXT prompts for every supported image in a directory."""
        directory = Path(directory)
        if not directory.is_dir():
            raise NotADirectoryError(f"Directory not found: {directory}")

        prompt_paths = []
        for image_path in sorted(directory.iterdir()):
            if image_path.is_file() and image_path.suffix.lower() in self.SUPPORTED_EXTENSIONS:
                prompt_paths.append(self.write_prompt_file(image_path))
        return prompt_paths

    def _build_prompt(self, file_name: str, width: int, height: int, image_format: str) -> str:
        name_stem = Path(file_name).stem.lower()
        orientation = "portrait" if height >= width else "landscape"

        if "person" in name_stem or "face" in name_stem or "portrait" in name_stem:
            subject = "person portrait"
        elif "animal" in name_stem:
            subject = "animal"
        else:
            subject = "subject"

        return (
            f"{subject}, {orientation} composition, high quality, natural lighting, "
            f"detailed image, {width}x{height} pixels, file format {image_format}."
        )
