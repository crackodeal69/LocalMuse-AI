from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class PresetStore:
    """Load built-in generation presets and save user-owned presets."""

    def __init__(self, built_in_path: str | Path, user_path: str | Path | None = None) -> None:
        self.built_in_path = Path(built_in_path)
        self.user_path = Path(user_path) if user_path is not None else self.built_in_path.with_name("user_presets.json")

    def list_presets(self, include_experimental: bool = False) -> list[dict[str, Any]]:
        presets = self._read(self.built_in_path) + self._read(self.user_path)
        if include_experimental:
            return presets
        return [preset for preset in presets if not preset.get("experimental", False)]

    def get(self, preset_id: str, include_experimental: bool = True) -> dict[str, Any]:
        for preset in self.list_presets(include_experimental=include_experimental):
            if preset.get("id") == preset_id:
                return preset
        raise KeyError(f"Unknown generation preset: {preset_id}")

    def save_user_preset(self, preset: dict[str, Any]) -> Path:
        preset_id = str(preset.get("id", "")).strip()
        label = str(preset.get("label", "")).strip()
        if not preset_id or not label:
            raise ValueError("User presets require non-empty id and label")

        user_presets = self._read(self.user_path)
        user_presets = [item for item in user_presets if item.get("id") != preset_id]
        user_presets.append(dict(preset))
        self.user_path.parent.mkdir(parents=True, exist_ok=True)
        self.user_path.write_text(
            json.dumps({"version": 1, "presets": user_presets}, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        return self.user_path

    @staticmethod
    def _read(path: Path) -> list[dict[str, Any]]:
        if not path.is_file():
            return []
        data = json.loads(path.read_text(encoding="utf-8"))
        return list(data.get("presets", []))