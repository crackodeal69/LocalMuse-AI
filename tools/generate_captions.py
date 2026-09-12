from __future__ import annotations

import argparse
from pathlib import Path

from localmuse import FlorenceCaptioner


DEFAULT_CACHE_DIR = Path(__file__).resolve().parents[1] / "models" / "huggingface"


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate LoRA captions for an image directory.")
    parser.add_argument("input_dir", type=Path)
    parser.add_argument("--trigger", default="nag_person")
    parser.add_argument("--model-id", default=FlorenceCaptioner.DEFAULT_MODEL_ID)
    parser.add_argument("--cache-dir", type=Path, default=DEFAULT_CACHE_DIR)
    args = parser.parse_args()

    captioner = FlorenceCaptioner(
        trigger_token=args.trigger,
        model_id=args.model_id,
        cache_dir=args.cache_dir,
    )
    prompt_paths = captioner.write_prompts_for_directory(args.input_dir)
    print(f"Generated {len(prompt_paths)} captions in {args.input_dir}")


if __name__ == "__main__":
    main()