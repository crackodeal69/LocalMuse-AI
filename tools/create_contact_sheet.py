from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a numbered contact sheet for dataset review.")
    parser.add_argument("input_dir", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    image_paths = sorted(
        path
        for path in args.input_dir.iterdir()
        if path.is_file() and path.suffix.lower() in {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
    )
    columns = 5
    thumbnail_width, thumbnail_height = 180, 240
    label_height = 28
    rows = (len(image_paths) + columns - 1) // columns
    sheet = Image.new("RGB", (columns * thumbnail_width, rows * (thumbnail_height + label_height)), "white")
    draw = ImageDraw.Draw(sheet)

    for index, image_path in enumerate(image_paths, start=1):
        with Image.open(image_path) as image:
            image = image.convert("RGB")
            image.thumbnail((thumbnail_width - 8, thumbnail_height - 8))
            x = ((index - 1) % columns) * thumbnail_width
            y = ((index - 1) // columns) * (thumbnail_height + label_height)
            image_x = x + (thumbnail_width - image.width) // 2
            image_y = y + (thumbnail_height - image.height) // 2
            sheet.paste(image, (image_x, image_y))
        draw.text((x + 6, y + thumbnail_height + 5), f"{index}: {image_path.name}", fill="black")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(args.output)
    print(f"Wrote contact sheet to {args.output}")


if __name__ == "__main__":
    main()