from __future__ import annotations

import argparse
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def natural_page_key(path: Path) -> int:
    return int(path.stem.split("-")[-1])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("render_dir", type=Path)
    parser.add_argument("--columns", type=int, default=2)
    parser.add_argument("--rows", type=int, default=2)
    parser.add_argument("--page-width", type=int, default=700)
    args = parser.parse_args()

    pages = sorted(args.render_dir.glob("page-*.png"), key=natural_page_key)
    if not pages:
        raise SystemExit(f"No rendered pages found in {args.render_dir}")

    out_dir = args.render_dir / "contact_sheets"
    out_dir.mkdir(exist_ok=True)
    batch_size = args.columns * args.rows
    font = ImageFont.load_default()
    margin = 24
    label_height = 28

    for batch_no in range(math.ceil(len(pages) / batch_size)):
        batch = pages[batch_no * batch_size : (batch_no + 1) * batch_size]
        rendered: list[tuple[Path, Image.Image]] = []
        max_height = 0
        for page in batch:
            image = Image.open(page).convert("RGB")
            height = round(image.height * args.page_width / image.width)
            image = image.resize((args.page_width, height), Image.Resampling.LANCZOS)
            rendered.append((page, image))
            max_height = max(max_height, height)

        sheet_width = margin + args.columns * (args.page_width + margin)
        cell_height = label_height + max_height + margin
        sheet_height = margin + args.rows * cell_height
        sheet = Image.new("RGB", (sheet_width, sheet_height), "#e6e7e9")
        draw = ImageDraw.Draw(sheet)

        for index, (page, image) in enumerate(rendered):
            row, col = divmod(index, args.columns)
            x = margin + col * (args.page_width + margin)
            y = margin + row * cell_height
            draw.text((x, y), page.stem, fill="#111111", font=font)
            sheet.paste(image, (x, y + label_height))

        output = out_dir / f"sheet-{batch_no + 1:02d}.png"
        sheet.save(output, quality=92)
        print(output)


if __name__ == "__main__":
    main()
