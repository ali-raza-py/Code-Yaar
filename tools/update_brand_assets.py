"""Regenerate every brand asset from the official Code-Yaar emblem.

Source of truth: ``backend/branding/logo-transparent.png`` — the glyph on a
transparent ground (white artwork). ``backend/branding/logo.png`` (white glyph
on black) remains the contract ``backend/branding.py`` reads for certificates
and badges. From these we derive:

  frontend/public/logo-light.png      black glyph, transparent, square
  frontend/public/logo-dark.png       white glyph, transparent, square
  frontend/public/brand/logo-mark.png black silhouette, transparent (CSS mask)
  frontend/public/brand/logo.png      official white-on-black tile, square
  frontend/public/favicon.svg         transparent white glyph (no tile)
  frontend/public/apple-touch-icon.png 180px dark tile (opaque, per Apple spec)
  frontend/src/app/favicon.ico        multi-size ICO (16–256), transparent bg

Usage:  .venv\\Scripts\\python.exe tools\\update_brand_assets.py
"""

import base64
import io
import os

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'backend', 'branding', 'logo.png')
SRC_TRANSPARENT = os.path.join(ROOT, 'backend', 'branding', 'logo-transparent.png')
PUBLIC = os.path.join(ROOT, 'frontend', 'public')
APP = os.path.join(ROOT, 'frontend', 'src', 'app')

INK = (10, 10, 15)        # brand near-black (#0a0a0f), matches the tile ground
WHITE = (255, 255, 255)
SIDE = 512                # master raster size
MARGIN = 0.10             # share of the canvas left around the glyph


def silhouette() -> Image.Image:
    """Grayscale alpha mask of the glyph, cropped and centred on a square.

    Prefers the transparent artwork (true alpha edges, no thresholding artefacts);
    falls back to the white-on-black tile via luminance, as branding.py does.
    """
    if os.path.exists(SRC_TRANSPARENT):
        im = Image.open(SRC_TRANSPARENT).convert('RGBA').split()[3]
    else:
        im = Image.open(SRC).convert('L')
        im = im.point(lambda p: 255 if p >= 60 else 0)
    bbox = im.getbbox()
    if bbox:
        im = im.crop(bbox)
    w, h = im.size
    # Fit the glyph into the canvas minus margins, preserving its aspect.
    inner = int(SIDE * (1 - 2 * MARGIN))
    scale = min(inner / w, inner / h)
    im = im.resize((max(1, int(w * scale)), max(1, int(h * scale))), Image.LANCZOS)
    out = Image.new('L', (SIDE, SIDE), 0)
    out.paste(im, ((SIDE - im.width) // 2, (SIDE - im.height) // 2))
    return out


def tinted(mask: Image.Image, rgb) -> Image.Image:
    """RGBA glyph tinted to ``rgb`` on a transparent ground."""
    img = Image.new('RGBA', (SIDE, SIDE), (*rgb, 0))
    img.putalpha(mask)
    return img


def favicon_glyph(mask: Image.Image) -> Image.Image:
    """White glyph on full transparency — the favicon artwork itself."""
    return tinted(mask, WHITE)


def write_svg(glyph: Image.Image) -> None:
    """favicon.svg = embedded high-res transparent glyph PNG.

    The PNG rides inside the SVG as base64 so the file stays a single asset:
    modern browsers get crisp scaling up to 512px without external refs.
    """
    buf = io.BytesIO()
    glyph.save(buf, 'PNG', optimize=True)
    b64 = base64.b64encode(buf.getvalue()).decode('ascii')
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"'
        ' viewBox="0 0 64 64" width="64" height="64">\n'
        '  <image width="64" height="64" href="data:image/png;base64,'
        + b64 + '" />\n'
        '</svg>\n'
    )
    with open(os.path.join(PUBLIC, 'favicon.svg'), 'w', encoding='utf-8') as fh:
        fh.write(svg)


def main() -> None:
    mask = silhouette()

    outputs = {
        os.path.join(PUBLIC, 'logo-light.png'): tinted(mask, INK),
        os.path.join(PUBLIC, 'logo-dark.png'): tinted(mask, WHITE),
        os.path.join(PUBLIC, 'brand', 'logo-mark.png'): tinted(mask, INK),
        os.path.join(PUBLIC, 'brand', 'logo.png'): Image.open(SRC).convert('RGB'),
    }
    glyph = favicon_glyph(mask)
    # Apple touch icons must be opaque; seat the glyph on the brand ink ground.
    tile = Image.new('RGB', (SIDE, SIDE), INK)
    tile.paste(glyph.resize((SIDE, SIDE), Image.LANCZOS), (0, 0), glyph)
    outputs[os.path.join(PUBLIC, 'apple-touch-icon.png')] = tile.resize((180, 180), Image.LANCZOS)

    for path, img in outputs.items():
        img.save(path, 'PNG', optimize=True)
        print('wrote', os.path.relpath(path, ROOT))

    write_svg(glyph)
    print('wrote', os.path.relpath(os.path.join(PUBLIC, 'favicon.svg'), ROOT))

    ico_sizes = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    glyph.resize((256, 256), Image.LANCZOS).save(
        os.path.join(APP, 'favicon.ico'), format='ICO', sizes=ico_sizes,
    )
    print('wrote', os.path.relpath(os.path.join(APP, 'favicon.ico'), ROOT))


if __name__ == '__main__':
    main()
