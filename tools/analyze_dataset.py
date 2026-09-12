from __future__ import annotations

import argparse
import json
from pathlib import Path

from localmuse import DatasetAnalyzer


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze an image dataset and its captions.")
    parser.add_argument("input_dir", type=Path)
    parser.add_argument("--trigger", default="nag_person")
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()

    report = DatasetAnalyzer().analyze(args.input_dir, args.trigger)
    payload = json.dumps(report, indent=2, ensure_ascii=False)
    if args.output is None:
        print(payload)
    else:
        args.output.write_text(payload + "\n", encoding="utf-8")
        print(f"Wrote dataset report to {args.output}")


if __name__ == "__main__":
    main()