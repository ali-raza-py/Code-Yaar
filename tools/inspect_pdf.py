"""Inspect a textbook PDF: page count, text-layer coverage, embedded images.

Usage: python inspect_pdf.py <path-to-pdf>
"""
import sys

import fitz  # PyMuPDF


def main(path: str) -> None:
    doc = fitz.open(path)
    print(f"pages         : {doc.page_count}")
    print(f"metadata      : {doc.metadata.get('title')!r}")

    totals = []
    empty_pages = []
    for i, page in enumerate(doc):
        txt = page.get_text("text")
        chars = len(txt.strip())
        images = len(page.get_images(full=True))
        totals.append(chars)
        if chars == 0:
            empty_pages.append((i, images))

    seeded = sum(1 for c in totals if c > 0)
    print(f"pages w/ text : {seeded}/{doc.page_count}")
    print(f"text chars    : total={sum(totals)} max={max(totals)}")
    print(f"blank-text    : {len(empty_pages)} pages (first 10: {empty_pages[:10]})")

    # Does the text look like real Urdu/English or garbage from a bad OCR layer?
    sample_pages = [p for p in (0, 1, 5, 20) if p < doc.page_count]
    for p in sample_pages:
        s = doc[p].get_text("text").strip()
        print(f"\n--- page index {p} (first 300 chars) ---\n{s[:300]!r}")

    # Page geometry helps pick a render DPI later.
    r = doc[0].rect
    print(f"\npage size     : {r.width:.0f}x{r.height:.0f} pt")
    doc.close()


if __name__ == "__main__":
    main(sys.argv[1])
