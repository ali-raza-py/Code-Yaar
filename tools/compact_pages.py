"""Produce compact, legible page crops for visual textbook verification.

Scanned textbook pages carry ~25% decorative margin. Cropping the content box
and scaling to a fixed width keeps text legible while making each page far
cheaper to read in bulk.

Usage:
    python tools/compact_pages.py <pages-dir> <out-dir> <first> <last> [width]
"""
import sys
from pathlib import Path

from PIL import Image


def main() -> None:
    src = Path(sys.argv[1])
    dst = Path(sys.argv[2])
    first, last = int(sys.argv[3]), int(sys.argv[4])
    width = int(sys.argv[5]) if len(sys.argv) > 5 else 800
    dst.mkdir(parents=True, exist_ok=True)

    made = 0
    for n in range(first, last + 1):
        f = src / f"p{n:03d}.png"
        if not f.exists():
            continue
        im = Image.open(f).convert("L")
        w, h = im.size
        # Trim the decorative border: content sits inside a centered column.
        box = (int(w * 0.10), int(h * 0.055), int(w * 0.925), int(h * 0.965))
        im = im.crop(box)
        im = im.resize((width, int(im.height * width / im.width)), Image.LANCZOS)
        out = dst / f"c{n:03d}.png"
        if not out.exists():
            im.save(out, optimize=True)
        made += 1
    print(f"prepared {made} compact pages -> {dst}")


if __name__ == "__main__":
    main()
