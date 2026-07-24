from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps, UnidentifiedImageError

try:
    from .common import natural_key
except ImportError:
    from common import natural_key

IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".webp"}


def _font(size: int) -> ImageFont.ImageFont:
    candidates = [
        Path("C:/Windows/Fonts/msyh.ttc"),
        Path("C:/Windows/Fonts/arial.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    ]
    for candidate in candidates:
        if candidate.is_file():
            try:
                return ImageFont.truetype(str(candidate), size=size)
            except OSError:
                continue
    return ImageFont.load_default()


def make_contact_sheet(
    input_dir: Path,
    output: Path,
    *,
    columns: int = 4,
    thumb_width: int = 360,
    thumb_height: int = 203,
    caption_height: int = 42,
    margin: int = 18,
) -> Path:
    input_dir = input_dir.resolve()
    output = output.resolve()
    if not input_dir.is_dir():
        raise FileNotFoundError(f"Input directory not found: {input_dir}")
    files = sorted(
        [path for path in input_dir.iterdir() if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES],
        key=lambda path: natural_key(path.name),
    )
    if not files:
        raise ValueError(f"No supported images found in: {input_dir}")
    columns = max(1, columns)
    rows = math.ceil(len(files) / columns)
    cell_width = thumb_width + margin * 2
    cell_height = thumb_height + caption_height + margin * 2
    canvas = Image.new("RGB", (cell_width * columns, cell_height * rows), "white")
    draw = ImageDraw.Draw(canvas)
    caption_font = _font(17)
    for index, path in enumerate(files):
        row, column = divmod(index, columns)
        x = column * cell_width + margin
        y = row * cell_height + margin
        try:
            with Image.open(path) as source:
                image = ImageOps.exif_transpose(source).convert("RGB")
                fitted = ImageOps.contain(image, (thumb_width, thumb_height))
        except (UnidentifiedImageError, OSError) as exc:
            raise ValueError(f"Cannot decode {path}: {exc}") from exc
        image_x = x + (thumb_width - fitted.width) // 2
        image_y = y + (thumb_height - fitted.height) // 2
        canvas.paste(fitted, (image_x, image_y))
        draw.rectangle((x, y, x + thumb_width, y + thumb_height), outline="#A7B0BE", width=1)
        caption = f"{index + 1:03d}  {path.name}"
        if len(caption) > 48:
            caption = caption[:45] + "…"
        draw.text((x, y + thumb_height + 9), caption, font=caption_font, fill="#172033")
    output.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output, quality=92, optimize=True)
    return output


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build a labeled contact sheet from a directory of rendered slides or evidence images.")
    parser.add_argument("input_dir", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--columns", type=int, default=4)
    parser.add_argument("--thumb-width", type=int, default=360)
    parser.add_argument("--thumb-height", type=int, default=203)
    args = parser.parse_args(argv)
    try:
        result = make_contact_sheet(
            args.input_dir,
            args.output,
            columns=args.columns,
            thumb_width=args.thumb_width,
            thumb_height=args.thumb_height,
        )
    except (FileNotFoundError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
