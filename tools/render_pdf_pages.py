"""Render scanned textbook PDF pages to PNG so they can be read visually.

The Sindh Board PDFs have no text layer, so topic verification is done by
inspecting rendered page images.

Usage:
    python tools/render_pdf_pages.py <pdf> <first-page> <last-page> [dpi] [outdir]

Pages are 1-based (book pages as a student would count them); the output file
name carries the 1-based number so it can be cited as a textbook reference.
"""
import sys
from pathlib import Path

import pymupdf


def main() -> None:
    pdf = Path(sys.argv[1])
    first, last = int(sys.argv[2]), int(sys.argv[3])
    dpi = int(sys.argv[4]) if len(sys.argv) > 4 else 150
    outdir = Path(sys.argv[5]) if len(sys.argv) > 5 else pdf.parent / "pages"
    outdir.mkdir(parents=True, exist_ok=True)

    doc = pymupdf.open(pdf)
    zoom = dpi / 72
    written = []
    for page_no in range(first, last + 1):
        if not (1 <= page_no <= doc.page_count):
            continue
        page = doc[page_no - 1]
        pix = page.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom), colorspace=pymupdf.csGRAY)
        out = outdir / f"p{page_no:03d}.png"
        if not out.exists():
            pix.save(out)
        written.append(str(out))
    doc.close()
    print(f"rendered {len(written)} pages @ {dpi}dpi -> {outdir}")
    for w in written:
        print(w)


if __name__ == "__main__":
    main()
