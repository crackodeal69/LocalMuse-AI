from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from PIL import Image, UnidentifiedImageError


class DatasetAnalyzer:
    """Inspect image and sidecar-caption health for a local dataset."""

    SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

    def analyze(self, directory: str | Path, trigger_token: str) -> dict[str, Any]:
        directory = Path(directory)
        if not directory.is_dir():
            raise NotADirectoryError(f"Directory not found: {directory}")

        images: list[dict[str, Any]] = []
        errors: list[dict[str, str]] = []
        hashes: dict[str, list[str]] = {}

        for image_path in sorted(directory.iterdir()):
            if not image_path.is_file() or image_path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
                continue

            item: dict[str, Any] = {
                "file_name": image_path.name,
                "caption_file": image_path.with_suffix(".txt").name,
                "caption_exists": image_path.with_suffix(".txt").is_file(),
                "sha256": None,
                "size": None,
                "format": None,
                "warnings": [],
            }
            try:
                with Image.open(image_path) as image:
                    item["size"] = image.size
                    item["format"] = image.format
                    if min(image.size) < 512:
                        item["warnings"].append("small_dimension")
                    image.verify()
                digest = hashlib.sha256(image_path.read_bytes()).hexdigest()
                item["sha256"] = digest
                hashes.setdefault(digest, []).append(image_path.name)
            except (OSError, UnidentifiedImageError) as error:
                errors.append({"file_name": image_path.name, "error": str(error)})
                item["warnings"].append("unreadable")

            caption_path = image_path.with_suffix(".txt")
            if not caption_path.is_file():
                item["warnings"].append("missing_caption")
            else:
                caption = caption_path.read_text(encoding="utf-8").strip()
                if not caption:
                    item["warnings"].append("empty_caption")
                if caption.count(trigger_token) != 1:
                    item["warnings"].append("invalid_trigger")

            images.append(item)

        duplicates = [names for names in hashes.values() if len(names) > 1]
        warning_counts: dict[str, int] = {}
        for item in images:
            for warning in item["warnings"]:
                warning_counts[warning] = warning_counts.get(warning, 0) + 1

        return {
            "directory": str(directory),
            "image_count": len(images),
            "read_error_count": len(errors),
            "duplicate_groups": duplicates,
            "warning_counts": warning_counts,
            "images": images,
            "errors": errors,
        }