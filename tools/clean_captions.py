from __future__ import annotations

import argparse
from pathlib import Path

from localmuse import CaptionCleaner


def main() -> None:
    parser = argparse.ArgumentParser(description="Clean generated LoRA caption files.")
    parser.add_argument("input_dir", type=Path)
    parser.add_argument("--trigger", default="nag_person")
    args = parser.parse_args()

    paths = CaptionCleaner().clean_directory(args.input_dir, args.trigger)
    print(f"Cleaned {len(paths)} captions in {args.input_dir}")


if __name__ == "__main__":
    main()