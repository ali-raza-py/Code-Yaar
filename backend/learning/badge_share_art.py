"""LinkedIn-ready achievement share graphics for Code Yaar badges.

A standalone credential graphic — NOT a dashboard screenshot. It composites
the *official* medallion (rendered by ``badge_art``) onto a branded canvas with
the achievement title, recipient, issuing organisation, and a readable
verification-URL footer, so the badge is fully legible inside a LinkedIn post
without ever opening the Code Yaar site.

Two presentation presets are produced from one composition system:

    square  1200 × 1200  — the LinkedIn recommended square achievement card
    wide    1200 × 627   — the Open Graph / link-preview card

Everything drawn here comes from the real earned-achievement row; nothing is
mocked, and the medallion is the identical artwork the download endpoints ship.
"""

import io

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from .badge_art import (
    GOLD,
    GOLD_DEEP,
    NAVY,
    PURPLE,
    _hex_to_rgb,
    _pil_font,
    _pil_serif,
    level_label,
    palette_for,
    render_badge_png,
)

# Canvas presets
SQUARE = (1200, 1200)
WIDE = (1200, 627)

BG_TOP = (11, 17, 32)      # deep near-black navy
BG_BOTTOM = (17, 24, 39)   # NAVY
WHITE = (255, 255, 255)
MUTED = (156, 163, 175)    # slate-400
FAINT = (203, 213, 225)    # slate-300

GOLD_RGB = _hex_to_rgb(GOLD)
GOLD_DEEP_RGB = _hex_to_rgb(GOLD_DEEP)
PURPLE_RGB = _hex_to_rgb(PURPLE)


def _vertical_gradient(w: int, h: int, top, bottom) -> Image.Image:
    img = Image.new('RGB', (w, h), top)
    d = ImageDraw.Draw(img)
    for y in range(h):
        t = y / max(h - 1, 1)
        col = tuple(round(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
        d.line([(0, y), (w, y)], fill=col)
    return img


def _glow(base: Image.Image, cx, cy, radius, colour, alpha) -> None:
    """Soft blurred colour halo behind the medallion for depth."""
    layer = Image.new('RGBA', base.size, (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    ld.ellipse(
        (cx - radius, cy - radius, cx + radius, cy + radius),
        fill=(*colour, alpha),
    )
    layer = layer.filter(ImageFilter.GaussianBlur(radius=radius * 0.42))
    base.alpha_composite(layer)


def _logo_mark(img: Image.Image, cx, cy, size, rgb) -> None:
    """Code Yaar brand logo, tinted to `rgb` and centred at (cx, cy)."""
    from branding import logo_image  # local import keeps module load lazy

    logo = logo_image(max(8, int(round(size))), rgb)
    img.alpha_composite(logo, (int(round(cx - size / 2)), int(round(cy - size / 2))))


def _draw_spaced_c(d, cx, y, text, font, fill, spacing, anchor='ma'):
    """Centred letter-spaced text (PIL has no tracking)."""
    total = d.textlength(text, font=font) + spacing * (len(text) - 1)
    x = cx - total / 2
    for ch in text:
        d.text((x, y), ch, font=font, fill=fill, anchor=anchor)
        x += d.textlength(ch, font=font) + spacing


def _draw_spaced_l(d, x, y, text, font, fill, spacing, anchor='lm'):
    """Left-aligned letter-spaced text; returns the advance width."""
    for ch in text:
        d.text((x, y), ch, font=font, fill=fill, anchor=anchor)
        x += d.textlength(ch, font=font) + spacing


def _fit(text, font, max_w, d):
    if d.textlength(text, font=font) <= max_w:
        return text
    while text and d.textlength(text + '…', font=font) > max_w:
        text = text[:-1]
    return (text + '…').strip() if text else '…'


def _wrap(d, text, font, max_w, max_lines):
    words, lines, cur = text.split(), [], ''
    for word in words:
        cand = (cur + ' ' + word).strip()
        if d.textlength(cand, font=font) <= max_w or not cur:
            cur = cand
        else:
            lines.append(cur)
            cur = word
            if len(lines) == max_lines:
                break
    if cur and len(lines) < max_lines:
        lines.append(cur)
    if len(lines) == max_lines and d.textlength(lines[-1], font=font) > max_w:
        lines[-1] = _fit(lines[-1], font, max_w, d)
    return lines


def _paste_medallion(base: Image.Image, user_achievement, cx, cy, target_px):
    src = Image.open(render_badge_png(user_achievement)).convert('RGBA')
    src = src.resize((target_px, target_px), Image.Resampling.LANCZOS)
    shadow = Image.new('RGBA', base.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    left, top = cx - target_px // 2, cy - target_px // 2 + 14
    sd.ellipse((left + 30, top + 30, left + target_px - 30, top + target_px - 10),
               fill=(0, 0, 0, 120))
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=26))
    base.alpha_composite(shadow)
    base.alpha_composite(src, (left, top))


def _footer_url(d, url, cx, y, font, *, centered=True, left_x=None):
    pretty = url.replace('https://', '').replace('http://', '')
    label = 'Verify: '
    lw = d.textlength(label, font=font)
    tw = d.textlength(pretty, font=font)
    if centered:
        x = cx - (lw + tw) / 2
    else:
        x = left_x
    d.text((x, y), label, font=font, fill=GOLD_RGB)
    d.text((x + lw, y), pretty, font=font, fill=FAINT)


def render_badge_share_png(user_achievement, preset: str = 'square') -> io.BytesIO:
    achievement = user_achievement.achievement
    accent, _wash, category_label = palette_for(achievement)
    accent_rgb = _hex_to_rgb(accent)

    title = (achievement.title or 'Achievement').strip()
    recipient = (user_achievement.recipient_name or 'Code Yaar Learner').strip()
    level = level_label(achievement)
    url = user_achievement.verification_url()

    w, h = WIDE if preset == 'wide' else SQUARE
    img = _vertical_gradient(w, h, BG_TOP, BG_BOTTOM).convert('RGBA')
    d = ImageDraw.Draw(img)

    # Gold hairline frame + a thin accent inner rule.
    d.rectangle((26, 26, w - 26, h - 26), outline=(*GOLD_RGB, 200), width=2)
    d.rectangle((34, 34, w - 34, h - 34), outline=(*accent_rgb, 90), width=1)

    if preset == 'wide':
        _compose_wide(img, d, w, h, user_achievement, achievement,
                      accent_rgb, title, recipient, level, url, category_label)
    else:
        _compose_square(img, d, w, h, user_achievement, achievement,
                        accent_rgb, title, recipient, level, url, category_label)

    buf = io.BytesIO()
    img.convert('RGB').save(buf, format='PNG', optimize=True)
    buf.seek(0)
    return buf


def _compose_square(img, d, w, h, ua, achievement, accent_rgb,
                    title, recipient, level, url, category_label):
    cx = w / 2

    # Brand header
    _logo_mark(img, cx, 118, 60, GOLD_RGB)
    _draw_spaced_c(d, cx, 168, 'CODE YAAR ACADEMY', _pil_font(26, bold=True), WHITE, 4)
    _draw_spaced_c(d, cx, 200, 'THINK. BUILD. EVOLVE.', _pil_font(13), GOLD_RGB, 3)

    # Medallion with purple halo
    _glow(img, cx, 500, 250, PURPLE_RGB, 70)
    d = ImageDraw.Draw(img)
    _paste_medallion(img, ua, int(cx), 500, 360)
    d = ImageDraw.Draw(img)

    # Achievement title (up to two lines)
    title_font = _pil_serif(52, bold=True)
    lines = _wrap(d, title, title_font, w - 200, 2)
    ty = 748
    for line in lines:
        d.text((cx, ty), line, font=title_font, fill=WHITE, anchor='mm')
        ty += 60

    # Earned-from line
    earned_font = _pil_font(24)
    d.text((cx, ty + 6), f'Earned by {recipient} · {level}',
           font=earned_font, fill=FAINT, anchor='mm')

    # Category chip
    chip_font = _pil_font(18, bold=True)
    chip = (category_label or achievement.category or 'Achievement').upper()
    cw = d.textlength(chip, font=chip_font) + 6 * (len(chip) - 1) + 44
    d.rounded_rectangle(
        (cx - cw / 2, ty + 40, cx + cw / 2, ty + 82), radius=21,
        outline=(*GOLD_RGB, 220), width=2,
    )
    _draw_spaced_c(d, cx, ty + 61, chip, chip_font, GOLD_RGB, 6, anchor='mm')

    # Footer verification URL
    d.line([(120, h - 120), (w - 120, h - 120)], fill=(*GOLD_RGB, 70), width=1)
    _footer_url(d, url, cx, h - 86, _pil_font(22), centered=True)


def _compose_wide(img, d, w, h, ua, achievement, accent_rgb,
                  title, recipient, level, url, category_label):
    # Left: medallion
    _glow(img, 300, h / 2, 220, PURPLE_RGB, 70)
    d = ImageDraw.Draw(img)
    _paste_medallion(img, ua, 300, int(h / 2), 360)
    d = ImageDraw.Draw(img)

    # Right column
    rx = 560
    rw = w - rx - 70

    _logo_mark(img, rx + 24, 120, 40, GOLD_RGB)
    _draw_spaced_l(d, rx + 56, 112, 'CODE YAAR ACADEMY', _pil_font(22, bold=True), WHITE, 3)
    _draw_spaced_l(d, rx + 56, 142, 'THINK. BUILD. EVOLVE.', _pil_font(12), GOLD_RGB, 2.4)

    # Title
    title_font = _pil_serif(46, bold=True)
    lines = _wrap(d, title, title_font, rw, 2)
    ty = 210
    for line in lines:
        d.text((rx, ty), line, font=title_font, fill=WHITE, anchor='lm')
        ty += 54

    earned_font = _pil_font(21)
    d.text((rx, ty + 6), f'Earned by {recipient} · {level}',
           font=earned_font, fill=FAINT, anchor='lm')

    chip_font = _pil_font(15, bold=True)
    chip = (category_label or achievement.category or 'Achievement').upper()
    cy0 = ty + 44
    cw = d.textlength(chip, font=chip_font) + 4 * (len(chip) - 1) + 36
    d.rounded_rectangle((rx, cy0, rx + cw, cy0 + 34), radius=17,
                        outline=(*GOLD_RGB, 220), width=2)
    _draw_spaced_l(d, rx + 18, cy0 + 17, chip, chip_font, GOLD_RGB, 4)

    # Footer URL
    d.line([(rx, h - 96), (w - 70, h - 96)], fill=(*GOLD_RGB, 70), width=1)
    _footer_url(d, url, 0, h - 66, _pil_font(20), centered=False, left_x=rx)
