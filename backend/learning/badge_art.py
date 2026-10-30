"""Official Code Yaar badge artwork — premium circular medallions.

Both renderers (SVG for vector download, PNG for raster download/previews)
build the *same* composition from shared constants, so a badge always looks
identical wherever it appears:

    navy rim → accent ring → gold hairline → warm field
    top arc brand · level chevrons · category emblem
    ribbon title · category · recipient · date · level · badge id
    bottom arc tagline

Nothing here is decorative-only: the credential id and the encoded level come
from the real earned-achievement row, and category colour comes from the
official palette below — never from client input.
"""

import html
import io
import math

from PIL import Image, ImageDraw, ImageFilter, ImageFont

# ─── Palette ────────────────────────────────────────────────────────────────

NAVY = '#111827'
GOLD = '#C4A35A'
GOLD_DEEP = '#9A7B32'
PURPLE = '#7528E8'
INK = '#1F2937'
MUTED = '#6B7280'
PAPER = '#FFFDF9'

CATEGORY_PALETTE = {
    'course': ('#047857', '#ECFDF5', 'Course Completion'),
    'chapter': ('#0369A1', '#F0F9FF', 'Chapter Completion'),
    'streak': ('#C2410C', '#FFF7ED', 'Dedication'),
    'exercise': ('#7528E8', '#F5F3FF', 'Problem Solver'),
    'skill': ('#B45309', '#FFFBEB', 'Skill'),
    'special': ('#111827', '#F3F4F6', 'Distinction'),
    'excellence': ('#9A7B32', '#FBF8F0', 'Excellence Award'),
    'project': ('#1D4ED8', '#EFF6FF', 'Project Builder'),
}

SLUG_PALETTE = {
    'python-foundations-complete': ('#2563EB', '#EFF6FF', 'Python Fundamentals'),
    'git-foundations-complete': ('#EA580C', '#FFF7ED', 'Version Control'),
    'first-lesson': ('#7528E8', '#F5F3FF', 'Getting Started'),
    'chapter-master': ('#0369A1', '#F0F9FF', 'Chapter Mastery'),
    'streak-7': ('#C2410C', '#FFF7ED', 'Consistency'),
    'problem-solver': ('#7528E8', '#F5F3FF', 'Code Mastery'),
    'project-builder': ('#1D4ED8', '#EFF6FF', 'Project Builder'),
    'excellence-award': ('#9A7B32', '#FBF8F0', 'Excellence Award'),
}

# ─── Geometry (512 × 512 canvas) ───────────────────────────────────────────

SIZE = 512
CX = CY = SIZE / 2

R_RIM = 252          # outer navy rim
R_ACCENT = 243       # category accent ring
R_GOLD = 233         # gold hairline
R_FIELD = 224        # warm inner field
R_ARC_TOP = 196      # brand arc baseline
R_ARC_BOTTOM = 190   # tagline arc baseline

LEVEL_Y = 116        # level chevrons
EMBLEM_C = (256, 172)  # emblem centre
EMBLEM_BOX = 88      # emblem bounding box

RIBBON_TOP, RIBBON_BOT = 244, 292

# Baselines below the ribbon
Y_CATEGORY = 320
Y_NAME = 348
Y_META = 374
Y_ID = 402


def level_label(achievement) -> str:
    xp = getattr(achievement, 'xp_bonus', 0) or 0
    if xp >= 400:
        return 'Distinction'
    if xp >= 200:
        return 'Advanced'
    if xp >= 50:
        return 'Intermediate'
    return 'Foundational'


def level_fills(achievement) -> int:
    """Number of gold chevrons shown on the medallion (1–4)."""
    return {
        'Distinction': 4,
        'Advanced': 3,
        'Intermediate': 2,
        'Foundational': 1,
    }.get(level_label(achievement), 1)


def palette_for(achievement):
    slug = getattr(achievement, 'slug', '')
    if slug in SLUG_PALETTE:
        return SLUG_PALETTE[slug]
    return CATEGORY_PALETTE.get(achievement.category, CATEGORY_PALETTE['special'])


# ─── Emblems ────────────────────────────────────────────────────────────────
# Geometric, single-colour glyphs on a 0–64 grid. `lines` are drawn in the
# badge's wash colour so they read as engraving on the filled shape.

EMBLEMS = {
    # Mortarboard
    'course': {
        'polys': [
            [(32, 10), (60, 24), (32, 38), (4, 24)],
            [(17, 31), (47, 31), (47, 50), (35, 44), (35, 54), (29, 54),
             (29, 44), (17, 50)],
            [(56, 26), (58, 26), (58, 43), (56, 43)],
        ],
        'circles': [(57, 46, 3.4)],
    },
    # Open book
    'chapter': {
        'polys': [
            [(4, 15), (30, 20), (30, 50), (4, 46)],
            [(60, 15), (34, 20), (34, 50), (60, 46)],
            [(30, 20), (34, 20), (34, 50), (30, 50)],
        ],
        'circles': [],
    },
    # Lightning bolt (streak / dedication)
    'streak': {
        'polys': [
            [(37, 4), (15, 33), (27, 33), (23, 60), (49, 29), (35, 29)],
        ],
        'circles': [],
    },
    # Code chevrons
    'exercise': {
        'polys': [
            [(21, 14), (7, 32), (21, 50), (28, 50), (14, 32), (28, 14)],
            [(43, 14), (57, 32), (43, 50), (36, 50), (50, 32), (36, 14)],
            [(30, 44), (30, 50), (34, 50), (34, 44)],
        ],
        'circles': [(32, 16, 3)],
    },
    # Gem / diamond
    'skill': {
        'polys': [
            [(32, 6), (52, 24), (32, 58), (12, 24)],
            [(12, 24), (52, 24), (32, 31)],
        ],
        'circles': [],
    },
    # Four-point sparkle
    'special': {
        'polys': [
            [(32, 3), (38, 26), (61, 32), (38, 38), (32, 61), (26, 38),
             (3, 32), (26, 26)],
        ],
        'circles': [],
    },
    # Trophy
    'excellence': {
        'polys': [
            [(18, 8), (46, 8), (42, 28), (22, 28)],
            [(9, 11), (19, 11), (19, 15), (15, 19), (9, 19)],
            [(55, 11), (45, 11), (45, 15), (49, 19), (55, 19)],
            [(30, 28), (34, 28), (34, 42), (30, 42)],
            [(20, 42), (44, 42), (44, 52), (20, 52)],
        ],
        'circles': [],
    },
    # Isometric cube
    'project': {
        'polys': [
            [(32, 5), (57, 19), (57, 45), (32, 59), (7, 45), (7, 19)],
        ],
        'lines': [
            ((32, 5), (32, 32)),
            ((32, 32), (57, 45)),
            ((32, 32), (7, 45)),
        ],
        'circles': [],
    },
}

DEFAULT_EMBLEM = EMBLEMS['special']


def _hex_to_rgb(value: str):
    value = value.lstrip('#')
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


def _blend(a, b, t: float):
    """Linear blend of two (r, g, b) tuples."""
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def _emblem_for(achievement):
    category = getattr(achievement, 'category', 'special')
    if category in ('course', 'skill') and getattr(achievement, 'icon', '') == 'braces':
        return EMBLEMS['exercise']
    return EMBLEMS.get(category, DEFAULT_EMBLEM)


# ─── SVG renderer ───────────────────────────────────────────────────────────

def _poly_points(points) -> str:
    return ' '.join(f'{x},{y}' for x, y in points)


def _emblem_svg(emblem, accent: str, wash: str) -> str:
    parts = ['<g>']
    for poly in emblem.get('polys', []):
        parts.append(
            f'<polygon points="{_poly_points(poly)}" fill="{accent}"/>'
        )
    for cx, cy, r in emblem.get('circles', []):
        parts.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{accent}"/>')
    for (x1, y1), (x2, y2) in emblem.get('lines', []):
        parts.append(
            f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
            f'stroke="{wash}" stroke-width="3.4" stroke-linecap="round"/>'
        )
    parts.append('</g>')
    return ''.join(parts)


def _esc(value: str) -> str:
    return html.escape(value, quote=True)


def _svg_fit(text: str, max_width: float, font_size: float, bold: bool = True) -> str:
    """Truncate with an ellipsis so long titles never escape the medallion.

    Measured with the same font metrics the PNG renderer uses, so the vector
    and raster badges truncate at the same place.
    """
    font = _pil_font(int(round(font_size)), bold=bold)
    probe = ImageDraw.Draw(Image.new('RGBA', (8, 8)))
    if probe.textlength(text, font=font) <= max_width:
        return text
    while text and probe.textlength(text + '…', font=font) > max_width:
        text = text[:-1]
    return (text + '…').strip() if text else '…'


def render_badge_svg(user_achievement) -> str:
    achievement = user_achievement.achievement
    accent, wash, category_label = palette_for(achievement)

    title = _svg_fit((achievement.title or 'Achievement').strip(), 300, 25)
    name = _svg_fit((user_achievement.recipient_name or 'Code Yaar Learner').strip(), 330, 19)
    badge_id = (user_achievement.credential_id or '').strip()
    label = _svg_fit(category_label.upper(), 260, 13.5)
    level = level_label(achievement)

    earned = user_achievement.earned_at
    date_text = earned.strftime('%d %b %Y') if earned else '—'
    meta = _svg_fit(f'{date_text}  ·  {level.upper()}', 300, 13, bold=False)

    fills = level_fills(achievement)
    diamonds = []
    start_x = CX - (fills - 1) * 9
    for i in range(fills):
        x = start_x + i * 18
        diamonds.append(
            f'<path d="M {x} {LEVEL_Y - 7} L {x + 6} {LEVEL_Y} '
            f'L {x} {LEVEL_Y + 7} L {x - 6} {LEVEL_Y} Z" fill="{GOLD}"/>'
        )

    emblem = _emblem_for(achievement)
    scale = EMBLEM_BOX / 64
    ex, ey = EMBLEM_C
    emblem_svg = (
        f'<g transform="translate({ex - EMBLEM_BOX / 2} {ey - EMBLEM_BOX / 2}) '
        f'scale({scale:.4f})">{_emblem_svg(emblem, accent, wash)}</g>'
    )

    ribbon = (
        f'<polygon points="86,{RIBBON_TOP} 426,{RIBBON_TOP} 446,{(RIBBON_TOP + RIBBON_BOT) // 2} '
        f'426,{RIBBON_BOT} 86,{RIBBON_BOT} 66,{(RIBBON_TOP + RIBBON_BOT) // 2}" '
        f'fill="{accent}"/>'
        f'<polygon points="86,{RIBBON_BOT} 104,{RIBBON_BOT} 86,{RIBBON_BOT + 16}" '
        f'fill="{GOLD_DEEP}" opacity="0.55"/>'
        f'<polygon points="426,{RIBBON_BOT} 408,{RIBBON_BOT} 426,{RIBBON_BOT + 16}" '
        f'fill="{GOLD_DEEP}" opacity="0.55"/>'
    )

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {SIZE} {SIZE}" width="{SIZE}" height="{SIZE}" role="img" aria-label="{_esc(achievement.title)} badge issued by Code Yaar Academy">
  <defs>
    <radialGradient id="cy-field" cx="50%" cy="34%" r="72%">
      <stop offset="0%" stop-color="#FFFFFF"/>
      <stop offset="100%" stop-color="{wash}"/>
    </radialGradient>
    <path id="cy-arc-top" d="M {CX - R_ARC_TOP} {CY} A {R_ARC_TOP} {R_ARC_TOP} 0 0 1 {CX + R_ARC_TOP} {CY}"/>
    <path id="cy-arc-bottom" d="M {CX - R_ARC_BOTTOM} {CY} A {R_ARC_BOTTOM} {R_ARC_BOTTOM} 0 0 0 {CX + R_ARC_BOTTOM} {CY}"/>
  </defs>

  <!-- Rim + rings -->
  <circle cx="{CX}" cy="{CY}" r="{R_RIM}" fill="{NAVY}"/>
  <circle cx="{CX}" cy="{CY}" r="{R_ACCENT}" fill="{accent}"/>
  <circle cx="{CX}" cy="{CY}" r="{R_GOLD}" fill="none" stroke="{GOLD}" stroke-width="2.4"/>
  <circle cx="{CX}" cy="{CY}" r="{R_FIELD}" fill="url(#cy-field)"/>
  <circle cx="{CX}" cy="{CY}" r="{R_FIELD - 8}" fill="none" stroke="{accent}" stroke-opacity="0.18" stroke-width="1.2"/>

  <!-- Brand arcs -->
  <text font-family="'Segoe UI', Helvetica, Arial, sans-serif" font-size="21" font-weight="700" letter-spacing="4" fill="{NAVY}">
    <textPath href="#cy-arc-top" startOffset="50%" text-anchor="middle">CODE YAAR ACADEMY</textPath>
  </text>
  <text font-family="'Segoe UI', Helvetica, Arial, sans-serif" font-size="14" font-weight="600" letter-spacing="3.4" fill="{GOLD_DEEP}">
    <textPath href="#cy-arc-bottom" startOffset="50%" text-anchor="middle">THINK. BUILD. EVOLVE.</textPath>
  </text>

  <!-- Level chevrons -->
  {''.join(diamonds)}

  <!-- Emblem -->
  {emblem_svg}

  <!-- Ribbon title -->
  {ribbon}
  <text x="{CX}" y="{(RIBBON_TOP + RIBBON_BOT) // 2 + 9}" text-anchor="middle"
        font-family="'Segoe UI', Helvetica, Arial, sans-serif" font-size="25" font-weight="700"
        fill="#FFFFFF" letter-spacing="0.5">{_esc(title)}</text>

  <!-- Credential facts -->
  <text x="{CX}" y="{Y_CATEGORY}" text-anchor="middle" font-family="'Segoe UI', Helvetica, Arial, sans-serif"
        font-size="13.5" font-weight="700" letter-spacing="3" fill="{accent}">{_esc(label)}</text>
  <text x="{CX}" y="{Y_NAME}" text-anchor="middle" font-family="Georgia, 'Times New Roman', serif"
        font-size="20" font-weight="700" fill="{INK}">{_esc(name)}</text>
  <text x="{CX}" y="{Y_META}" text-anchor="middle" font-family="'Segoe UI', Helvetica, Arial, sans-serif"
        font-size="13" font-weight="500" fill="{MUTED}" letter-spacing="1">{_esc(meta)}</text>
  <text x="{CX}" y="{Y_ID}" text-anchor="middle" font-family="Consolas, 'DejaVu Sans Mono', monospace"
        font-size="13" font-weight="600" fill="{NAVY}" letter-spacing="0.6">{_esc(badge_id)}</text>

  <!-- Seal accent under the id -->
  <circle cx="{CX}" cy="{Y_ID + 16}" r="2.6" fill="{GOLD}"/>
</svg>'''


# ─── Fonts (PIL) ────────────────────────────────────────────────────────────

def _pil_font(size: int, *, bold=True, mono=False):
    from pathlib import Path
    roots = [
        Path(r'C:\Windows\Fonts'),
        Path('/usr/share/fonts/truetype/dejavu'),
        Path('/usr/share/fonts/truetype/liberation'),
    ]
    if mono:
        names = ['consolab.ttf' if bold else 'consola.ttf',
                 'DejaVuSansMono-Bold.ttf' if bold else 'DejaVuSansMono.ttf']
    elif bold:
        names = ['segoeuib.ttf', 'arialbd.ttf', 'DejaVuSans-Bold.ttf']
    else:
        names = ['segoeui.ttf', 'arial.ttf', 'DejaVuSans.ttf']
    for root in roots:
        for name in names:
            path = root / name
            if path.exists():
                try:
                    return ImageFont.truetype(str(path), size)
                except OSError:
                    continue
    return ImageFont.load_default()


def _pil_serif(size: int, *, bold=True, italic=False):
    """Georgia (elegant serif) with DejaVu/Liberation fallbacks."""
    from pathlib import Path
    roots = [Path(r'C:\Windows\Fonts'), Path('/usr/share/fonts/truetype/dejavu')]
    if italic:
        names = ['georgiai.ttf', 'DejaVuSerif-Italic.ttf']
    else:
        names = ['georgiab.ttf' if bold else 'georgia.ttf',
                 'DejaVuSerif-Bold.ttf' if bold else 'DejaVuSerif.ttf']
    for root in roots:
        for name in names:
            path = root / name
            if path.exists():
                try:
                    return ImageFont.truetype(str(path), size)
                except OSError:
                    continue
    return _pil_font(size, bold=bold)


def _pil_width(draw, text: str, font) -> float:
    return draw.textlength(text, font=font)


def _fit_text(draw, text: str, font, max_width: float) -> str:
    if _pil_width(draw, text, font) <= max_width:
        return text
    while text and _pil_width(draw, text + '…', font) > max_width:
        text = text[:-1]
    return (text + '…').strip() if text else '…'


def _draw_spaced(draw, xy, text: str, font, fill, spacing: float):
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=font, fill=fill)
        x += draw.textlength(ch, font=font) + spacing


def _spaced_width(draw, text: str, font, spacing: float) -> float:
    if not text:
        return 0.0
    return (_pil_width(draw, text, font) + spacing * (len(text) - 1))


def _arc_text(img, text: str, cx, cy, radius, font, fill, *, top=True, spacing=2.0):
    """Draw text along a circular arc, letters upright (like a seal)."""
    overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
    probe = ImageDraw.Draw(overlay)
    widths = [probe.textlength(ch, font=font) + spacing for ch in text]
    total = sum(widths)
    if total <= 0 or radius <= 0:
        return
    angle_per_px = 1.0 / radius
    angle = -total * angle_per_px / 2
    for ch, w in zip(text, widths):
        a = angle + (w / 2) * angle_per_px
        x = cx + radius * math.sin(a)
        y = (cy - radius * math.cos(a)) if top else (cy + radius * math.cos(a))
        rot = -math.degrees(a) if top else math.degrees(a)

        cw = int(probe.textlength(ch, font=font)) + 8
        chh = int(font.size * 1.6) + 8
        cell = Image.new('RGBA', (max(cw, 8), max(chh, 8)), (0, 0, 0, 0))
        ImageDraw.Draw(cell).text((4, 4), ch, font=font, fill=fill)
        cell = cell.rotate(rot, resample=Image.BICUBIC, expand=True)
        overlay.alpha_composite(cell, (int(x - cell.width / 2), int(y - cell.height / 2)))
        angle += w * angle_per_px
    img.alpha_composite(overlay)


def _fill_of(rgb, alpha: int = 255):
    return (*rgb, alpha)


def _draw_emblem_pil(d, emblem, origin, box, accent_rgb, wash_rgb):
    scale = box / 64
    ox, oy = origin

    def pt(p):
        return (ox + p[0] * scale, oy + p[1] * scale)

    for poly in emblem.get('polys', []):
        d.polygon([pt(p) for p in poly], fill=_fill_of(accent_rgb))
    for cx, cy, r in emblem.get('circles', []):
        px, py, pr = ox + cx * scale, oy + cy * scale, r * scale
        d.ellipse((px - pr, py - pr, px + pr, py + pr), fill=_fill_of(accent_rgb))
    lw = max(2, int(round(3.4 * scale)))
    for (x1, y1), (x2, y2) in emblem.get('lines', []):
        d.line([pt((x1, y1)), pt((x2, y2))], fill=_fill_of(wash_rgb), width=lw)


def render_badge_png(user_achievement) -> io.BytesIO:
    achievement = user_achievement.achievement
    accent, wash, category_label = palette_for(achievement)
    accent_rgb, wash_rgb = _hex_to_rgb(accent), _hex_to_rgb(wash)
    navy_rgb, gold_rgb = _hex_to_rgb(NAVY), _hex_to_rgb(GOLD)
    ink_rgb, muted_rgb = _hex_to_rgb(INK), _hex_to_rgb(MUTED)
    gold_deep_rgb = _hex_to_rgb(GOLD_DEEP)

    img = Image.new('RGBA', (SIZE, SIZE), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    def ring(radius, fill):
        d.ellipse((CX - radius, CY - radius, CX + radius, CY + radius), fill=fill)

    # Rim + rings + field
    ring(R_RIM, _fill_of(navy_rgb))
    ring(R_ACCENT, _fill_of(accent_rgb))
    d.ellipse((CX - R_GOLD, CY - R_GOLD, CX + R_GOLD, CY + R_GOLD),
              outline=_fill_of(gold_rgb), width=3)
    ring(R_FIELD, _fill_of(wash_rgb))
    # Soft highlight for depth (white disc, feathered by drawing over field)
    highlight = Image.new('RGBA', (SIZE, SIZE), (0, 0, 0, 0))
    hd = ImageDraw.Draw(highlight)
    hd.ellipse((CX - R_FIELD + 6, CY - R_FIELD + 6, CX + R_FIELD - 6, CY + R_FIELD - 6),
               fill=_fill_of((255, 255, 255), 170))
    img.alpha_composite(highlight)
    # Subtle accent hairline inside the field
    hair = Image.new('RGBA', (SIZE, SIZE), (0, 0, 0, 0))
    ImageDraw.Draw(hair).ellipse(
        (CX - (R_FIELD - 9), CY - (R_FIELD - 9),
         CX + (R_FIELD - 9), CY + (R_FIELD - 9)),
        outline=_fill_of(accent_rgb, 46), width=2)
    img.alpha_composite(hair)
    d = ImageDraw.Draw(img)

    # Arc branding (centred on the glyph box so it matches the SVG baseline)
    arc_font_top = _pil_font(21, bold=True)
    arc_font_bottom = _pil_font(14, bold=True)
    _arc_text(img, 'CODE YAAR ACADEMY', CX, CY, R_ARC_TOP + 7, arc_font_top,
              _fill_of(navy_rgb), top=True, spacing=4.0)
    _arc_text(img, 'THINK. BUILD. EVOLVE.', CX, CY, R_ARC_BOTTOM - 5,
              arc_font_bottom, _fill_of(gold_deep_rgb), top=False, spacing=3.0)
    d = ImageDraw.Draw(img)

    # Level chevrons
    fills = level_fills(achievement)
    start_x = CX - (fills - 1) * 9
    for i in range(fills):
        x = start_x + i * 18
        d.polygon([(x, LEVEL_Y - 7), (x + 6, LEVEL_Y), (x, LEVEL_Y + 7),
                   (x - 6, LEVEL_Y)], fill=_fill_of(gold_rgb))

    # Emblem
    emblem = _emblem_for(achievement)
    _draw_emblem_pil(d, emblem,
                     (EMBLEM_C[0] - EMBLEM_BOX / 2, EMBLEM_C[1] - EMBLEM_BOX / 2),
                     EMBLEM_BOX, accent_rgb, wash_rgb)

    # Ribbon
    mid_y = (RIBBON_TOP + RIBBON_BOT) // 2
    d.polygon([(86, RIBBON_TOP), (426, RIBBON_TOP), (446, mid_y),
               (426, RIBBON_BOT), (86, RIBBON_BOT), (66, mid_y)],
              fill=_fill_of(accent_rgb))
    d.polygon([(86, RIBBON_BOT), (104, RIBBON_BOT), (86, RIBBON_BOT + 16)],
              fill=_fill_of(gold_deep_rgb, 140))
    d.polygon([(426, RIBBON_BOT), (408, RIBBON_BOT), (426, RIBBON_BOT + 16)],
              fill=_fill_of(gold_deep_rgb, 140))

    # Ribbon title
    title_font = _pil_font(25, bold=True)
    title = _fit_text(d, (achievement.title or 'Achievement').strip(), title_font, 300)
    tw = _pil_width(d, title, title_font)
    d.text((CX - tw / 2, mid_y - title_font.size * 0.62), title,
           font=title_font, fill=(255, 255, 255, 255))

    # Facts
    label_font = _pil_font(13, bold=True)
    name_font = _pil_font(20, bold=True)
    meta_font = _pil_font(13, bold=False)
    id_font = _pil_font(13, bold=True, mono=True)

    label = _fit_text(d, category_label.upper(), label_font, 250)
    lw = _spaced_width(d, label, label_font, 3.0)
    _draw_spaced(d, (CX - lw / 2, Y_CATEGORY - label_font.size), label,
                 label_font, _fill_of(accent_rgb), 3.0)

    name = _fit_text(d, (user_achievement.recipient_name or 'Code Yaar Learner').strip(),
                     name_font, 330)
    nw = _pil_width(d, name, name_font)
    d.text((CX - nw / 2, Y_NAME - name_font.size), name, font=name_font,
           fill=_fill_of(ink_rgb))

    earned = user_achievement.earned_at
    date_text = earned.strftime('%d %b %Y') if earned else '—'
    meta = _fit_text(d, f'{date_text}  ·  {level_label(achievement).upper()}',
                     meta_font, 300)
    mw = _pil_width(d, meta, meta_font)
    d.text((CX - mw / 2, Y_META - meta_font.size), meta, font=meta_font,
           fill=_fill_of(muted_rgb))

    badge_id = (user_achievement.credential_id or '').strip()
    iw = _pil_width(d, badge_id, id_font)
    d.text((CX - iw / 2, Y_ID - id_font.size), badge_id, font=id_font,
           fill=_fill_of(navy_rgb))

    # Seal accent
    d.ellipse((CX - 2.6, Y_ID + 14, CX + 2.6, Y_ID + 19), fill=_fill_of(gold_rgb))

    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return buf
