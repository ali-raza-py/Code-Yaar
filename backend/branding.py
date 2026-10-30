"""Shared brand mark (the Code Yaar logo) for certificates and badges.

The logo ships as a white glyph on a black ground (``branding/logo.png``). We
derive a clean silhouette from its luminance, crop it to the glyph, and re-tint
that silhouette to any colour, so a single asset can appear as a purple mark on
an ivory certificate, a faint watermark, a gold mark on a navy share graphic,
or a navy stamp inside a medallion — always the identical shape.

The same silhouette is exported to ``frontend/public/brand/logo-mark.png`` and
tinted with a CSS mask in the on-screen certificate, keeping the browser, PDF
and PNG renderers visually in lockstep.
"""

import functools
import io
import os

from PIL import Image

_LOGO_PATH = os.path.join(os.path.dirname(__file__), 'branding', 'logo.png')


@functools.lru_cache(maxsize=1)
def _silhouette() -> Image.Image:
    """Grayscale alpha mask of the glyph, cropped and centred on a square."""
    im = Image.open(_LOGO_PATH).convert('L')
    # Hard threshold: bright glyph becomes opaque, black ground transparent.
    im = im.point(lambda p: 255 if p >= 60 else 0)
    bbox = im.getbbox()
    if bbox:
        im = im.crop(bbox)
    w, h = im.size
    side = max(w, h)
    out = Image.new('L', (side, side), 0)
    out.paste(im, ((side - w) // 2, (side - h) // 2))
    return out


def logo_image(size_px: int, rgb) -> Image.Image:
    """RGBA PIL image of the logo tinted to ``rgb`` (0–255), ``size_px`` square."""
    mask = _silhouette().resize((size_px, size_px), Image.LANCZOS)
    img = Image.new('RGBA', (size_px, size_px), (rgb[0], rgb[1], rgb[2], 0))
    img.putalpha(mask)
    return img


def logo_png_bytes(size_px: int, rgb) -> bytes:
    """PNG bytes of the tinted logo — for embedding (base64) or ReportLab."""
    buf = io.BytesIO()
    logo_image(size_px, rgb).save(buf, 'PNG')
    return buf.getvalue()
