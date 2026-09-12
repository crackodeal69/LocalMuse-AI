from __future__ import annotations

import re
from pathlib import Path


class CaptionCleaner:
    """Remove non-visual and speculative text from generated captions."""

    _DROP_SENTENCE_PATTERNS = (
        "likely discussing",
        "ready to take on",
        "determination and strength",
        "suggesting she is",
        "adding a touch of",
        "she is identified as",
        "identified as",
        "known for her role",
    )

    def clean(self, caption: str, trigger_token: str) -> str:
        """Return a concise caption containing the trigger exactly once."""
        trigger_token = trigger_token.strip()
        if not trigger_token:
            raise ValueError("trigger_token must not be empty")

        text = caption.strip()
        text = re.sub(rf"\b{re.escape(trigger_token)}\s*,?\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"^\s*(?:the image|this image)\s+(?:shows|is|depicts)\s+", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\bhas a human face\b", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s+", " ", text)

        sentences = re.split(r"(?<=[.!?])\s+", text)
        kept_sentences = [
            sentence.strip()
            for sentence in sentences
            if sentence.strip()
            and not any(pattern in sentence.lower() for pattern in self._DROP_SENTENCE_PATTERNS)
        ]
        text = " ".join(kept_sentences)
        text = re.sub(r"\s+([,.!?])", r"\1", text)
        text = re.sub(r",\s*,+", ",", text)
        text = text.strip(" ,")

        return f"{trigger_token}, {text}" if text else trigger_token

    def clean_file(
        self,
        caption_path: str | Path,
        trigger_token: str,
        output_path: str | Path | None = None,
    ) -> Path:
        """Clean one caption sidecar file in place unless output is provided."""
        caption_path = Path(caption_path)
        output_path = Path(output_path) if output_path is not None else caption_path
        cleaned = self.clean(caption_path.read_text(encoding="utf-8"), trigger_token)
        output_path.write_text(cleaned + "\n", encoding="utf-8")
        return output_path

    def clean_directory(self, directory: str | Path, trigger_token: str) -> list[Path]:
        """Clean all TXT sidecar files in a directory."""
        directory = Path(directory)
        if not directory.is_dir():
            raise NotADirectoryError(f"Directory not found: {directory}")

        paths = []
        for caption_path in sorted(directory.glob("*.txt")):
            paths.append(self.clean_file(caption_path, trigger_token))
        return paths