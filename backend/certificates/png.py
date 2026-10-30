"""High-resolution PNG certificate matching the PDF and on-screen preview.

The composition mirrors ``pdf.py`` element-for-element on the same millimetre
grid (ivory paper, burgundy/gold triple frame, watermark, centred brand band,
serif statement, bottom-left authorisation, bottom-right verification block),
so a certificate looks identical whether it is printed, downloaded as PNG, or
viewed in the browser. Type sizes convert the PDF point sizes at this DPI
(1 pt = DPI / 72 px), keeping the two renderers visually in lockstep.
"""

import io
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from .qrutil import qr_png_bytes

BURGUNDY = (117, 29, 43)
BURGUNDY_SOFT = (140, 47, 63)
GOLD = (196, 154, 72)
GOLD_DEEP = (154, 123, 50)
PURPLE = (117, 40, 232)
INK = (23, 23, 23)
MUTED = (92, 86, 78)
IVORY = (252, 250, 243)
WATERMARK = (246, 241, 231)
WATERMARK_LINE = (236, 229, 214)
WHITE = (255, 255, 255)

BRAND = 'CODE YAAR'
TAGLINE = 'Think. Build. Evolve.'
DESIGNATION = 'CERTIFICATE OF COMPLETION'
ISSUER = 'Code Yaar Academy'

DPI = 220
MM = DPI / 25.4
PT = DPI / 72.0
A4_W_MM, A4_H_MM = 297, 210


def pt(v: float) -> int:
    """PDF points → pixels at the render DPI."""
    return int(round(v * PT))


def _font(size, *, bold=False, italic=False, serif=True, mono=False):
    roots = [
        Path(r'C:\Windows\Fonts'),
        Path('/usr/share/fonts/truetype/dejavu'),
        Path('/usr/share/fonts/truetype/liberation'),
    ]
    if mono:
        names = ['consolab.ttf' if bold else 'consola.ttf',
                 'DejaVuSansMono-Bold.ttf' if bold else 'DejaVuSansMono.ttf']
    elif serif:
        if italic:
            names = ['georgiai.ttf', 'DejaVuSerif-Italic.ttf']
        else:
            names = ['georgiab.ttf' if bold else 'georgia.ttf',
                     'DejaVuSerif-Bold.ttf' if bold else 'DejaVuSerif.ttf']
    else:
        names = ['segoeuib.ttf' if bold else 'segoeui.ttf',
                 'DejaVuSans-Bold.ttf' if bold else 'DejaVuSans.ttf']
    for root in roots:
        for name in names:
            path = root / name
            if path.exists():
                try:
                    return ImageFont.truetype(str(path), size)
                except OSError:
                    continue
    return ImageFont.load_default()


def mm(v: float) -> int:
    return int(round(v * MM))


def render_certificate_png(certificate) -> io.BytesIO:
    width, height = mm(A4_W_MM), mm(A4_H_MM)
    img = Image.new('RGB', (width, height), IVORY)
    d = ImageDraw.Draw(img)

    _draw_watermark(d, width, height)
    _draw_frame(d, width, height)

    inner_left, inner_right = mm(22), width - mm(22)
    footer_base = height - mm(20)      # bottom edge of the footer zone (PIL y grows down)
    footer_top = footer_base - mm(34)  # top edge of the footer zone
    header_bottom = _draw_header(d, width, height)
    _draw_statement(d, certificate, width, header_bottom, footer_top, inner_left, inner_right)
    _draw_authorisation(d, inner_left, footer_base)
    _draw_verification(d, certificate, img, d, inner_right, footer_base)

    buf = io.BytesIO()
    img.save(buf, format='PNG', dpi=(DPI, DPI), optimize=True)
    buf.seek(0)
    return buf


# ─── Composition ───────────────────────────────────────────────────────────

def _draw_watermark(d, width, height):
    cx, cy = width / 2, height / 2 - mm(6)
    _emblem_mark(d, cx, cy - mm(30), mm(52), WATERMARK, WATERMARK_LINE)
    _center_spaced(d, BRAND, cx, cy + mm(8), _font(pt(74), bold=True), WATERMARK, pt(10))


def _draw_frame(d, width, height):
    for margin, colour, line_w in (
        (mm(8.0), BURGUNDY, max(4, mm(0.9))),
        (mm(11.2), GOLD, max(2, mm(0.32))),
        (mm(13.0), BURGUNDY, max(1, mm(0.18))),
    ):
        d.rectangle(
            [margin, margin, width - margin, height - margin],
            outline=colour, width=line_w,
        )
    inset = mm(13.0)
    for x, y, sx, sy in (
        (inset, inset, 1, 1), (width - inset, inset, -1, 1),
        (inset, height - inset, 1, -1), (width - inset, height - inset, -1, -1),
    ):
        _corner_flourish(d, x, y, sx, sy)


def _corner_flourish(d, x, y, sx, sy):
    arm = mm(14)
    off = mm(2.2)
    d.line([(x, y + sy * off), (x + sx * arm, y + sy * off)], fill=BURGUNDY_SOFT, width=1)
    d.line([(x + sx * off, y), (x + sx * off, y + sy * arm)], fill=BURGUNDY_SOFT, width=1)
    dia = mm(2.6)
    cxx = x + sx * mm(4.6)
    d.polygon(
        [(cxx, y), (cxx + sx * dia / 2, y + sy * dia / 2), (cxx, y + sy * dia), (cxx - sx * dia / 2, y + sy * dia / 2)],
        fill=GOLD,
    )
    r = mm(0.45)
    cx0, cy0 = cxx + sx * dia / 2, y + sy * dia / 2
    d.ellipse([cx0 - r, cy0 - r, cx0 + r, cy0 + r], fill=BURGUNDY)


def _emblem_mark(d, cx, cy, size, colour, line_colour=None):
    """Original Code Yaar logo mark: a diamond holding code chevrons."""
    half = size / 2
    outline = line_colour if line_colour is not None else colour
    d.polygon(
        [(cx, cy - half), (cx + half, cy), (cx, cy + half), (cx - half, cy)],
        outline=outline, width=max(1, int(size * 0.028)),
    )
    lw = max(2, int(size * 0.03))
    gap = 0.30 * size
    arm = 0.13 * size
    d.line([(cx - gap + arm * 0.55, cy - arm), (cx - gap - arm * 0.55, cy)], fill=colour, width=lw)
    d.line([(cx - gap - arm * 0.55, cy), (cx - gap + arm * 0.55, cy + arm)], fill=colour, width=lw)
    d.line([(cx + gap - arm * 0.55, cy - arm), (cx + gap + arm * 0.55, cy)], fill=colour, width=lw)
    d.line([(cx + gap + arm * 0.55, cy), (cx + gap - arm * 0.55, cy + arm)], fill=colour, width=lw)
    d.line(
        [(cx - 0.045 * size, cy + arm * 1.15), (cx + 0.045 * size, cy - arm * 1.15)],
        fill=colour, width=max(1, int(size * 0.022)),
    )


def _draw_header(d, width, height):
    """Brand band. Returns the y just below the designation underline."""
    cx = width / 2
    y = mm(20)

    _emblem_mark(d, cx, y + mm(4.5), mm(9.5), PURPLE)
    y += mm(14.5)

    _center_spaced(d, BRAND, cx, y, _font(pt(25), bold=True), INK, pt(3.2))
    y += mm(7.5)

    _center(d, TAGLINE, cx, y, _font(pt(11), italic=True), GOLD_DEEP)
    y += mm(8.5)

    _ornamental_rule(d, cx, y, mm(84))
    y += mm(11)

    _center_spaced(d, DESIGNATION, cx, y, _font(pt(15.5), bold=True), BURGUNDY, pt(3.6))
    text_w = _spaced_width(d, DESIGNATION, _font(pt(15.5), bold=True), pt(3.6))
    y += mm(6)
    d.line([(cx - text_w / 2, y), (cx + text_w / 2, y)], fill=GOLD, width=2)
    return y + mm(6)


def _ornamental_rule(d, cx, y, width_):
    d.line([(cx - width_ / 2, y), (cx - mm(3.2), y)], fill=GOLD, width=2)
    d.line([(cx + mm(3.2), y), (cx + width_ / 2, y)], fill=GOLD, width=2)
    dia = mm(2.4)
    d.polygon(
        [(cx, y - dia / 2), (cx + dia / 2, y), (cx, y + dia / 2), (cx - dia / 2, y)],
        fill=BURGUNDY,
    )
    for dx in (-mm(6.5), mm(6.5)):
        r = mm(0.7)
        d.ellipse([cx + dx - r, y - r, cx + dx + r, y + r], fill=GOLD)


def _draw_statement(d, certificate, width, header_bottom, footer_top, inner_left, inner_right):
    cx = width / 2
    max_text_w = inner_right - inner_left - mm(20)

    name = (certificate.student_name or 'Learner').strip()
    course = (certificate.course_title or 'Course').strip()

    course_font = _fit(course, max_text_w, pt(17.5), pt(12))
    course_lines = _wrap(d, course, course_font, max_text_w)[:2]

    block_h = (
        mm(6.5) + mm(13.5) + mm(4.5) + mm(6.5) + mm(9.5)
        + (len(course_lines) - 1) * mm(6.8)
        + (mm(8.5) if certificate.final_score is not None else 0)
    )
    gap = max(footer_top - header_bottom - block_h, 0) // 2
    y = header_bottom + gap

    _center(d, 'This is to certify that', cx, y, _font(pt(11.5), italic=True), MUTED)
    y += mm(13.5)

    name_font = _fit(name, max_text_w, pt(33), pt(16))
    _center(d, name, cx, y, name_font, INK)
    y += mm(4.5)

    rule_w = min(max(_text_width(d, name, name_font) + mm(24), mm(70)), mm(150))
    d.line([(cx - rule_w / 2, y), (cx + rule_w / 2, y)], fill=BURGUNDY, width=3)
    d.line([(cx - rule_w / 2, y + mm(1.2)), (cx + rule_w / 2, y + mm(1.2))], fill=GOLD, width=1)
    y += mm(6.5)

    _center(d, 'has successfully completed', cx, y, _font(pt(11.5), italic=True), MUTED)
    y += mm(9.5)

    for i, line in enumerate(course_lines):
        _center(d, line, cx, y + i * mm(6.8), course_font, BURGUNDY)
    y += (len(course_lines) - 1) * mm(6.8)

    if certificate.final_score is not None:
        y += mm(8.5)
        _center(
            d, f'Final assessment score  ·  {certificate.final_score:g}%',
            cx, y, _font(pt(9.5), serif=False), MUTED,
        )


def _draw_authorisation(d, x, base):
    """Bottom-left digital authorisation mark — no fabricated person."""
    top = base - mm(34)
    d.text((x + mm(2), top + mm(10)), 'Code Yaar', font=_font(pt(19), italic=True), fill=INK, anchor='lm')
    line_y = top + mm(15)
    d.line([(x, line_y), (x + mm(58), line_y)], fill=BURGUNDY, width=2)
    _left_spaced(d, 'CODE YAAR ACADEMY', x, line_y + mm(3), _font(pt(7.2), bold=True, serif=False), GOLD_DEEP, pt(1.6))
    d.text((x, line_y + mm(8.5)), 'Authorized by  ·  digitally issued credential', font=_font(pt(6.6), serif=False), fill=MUTED, anchor='la')


def _draw_verification(d, certificate, img, draw, right, base):
    """Bottom-right verification block — the ONLY place credential
    identifiers appear: issue date, certificate ID, verification code, QR."""
    top = base - mm(34)
    url = certificate.verification_url()
    qr_size = mm(24)
    qr_x = right - qr_size
    qr_y = top + mm(4)

    pad = mm(1.2)
    draw.rectangle(
        [qr_x - pad, qr_y - pad, qr_x + qr_size + pad, qr_y + qr_size + pad],
        fill=WHITE, outline=BURGUNDY, width=2,
    )
    qr = Image.open(qr_png_bytes(url, box_size=14, border=2)).convert('RGB')
    qr = qr.resize((qr_size, qr_size), Image.Resampling.NEAREST)
    img.paste(qr, (qr_x, qr_y))

    _center_spaced(
        draw, 'SCAN TO VERIFY', qr_x + qr_size / 2, base - mm(1.5),
        _font(pt(6.2), bold=True, serif=False), MUTED, pt(1.2), anchor='ls',
    )

    value_x = qr_x - mm(5)
    rows = [
        ('ISSUE DATE', _fmt_date(certificate.issued_at), _font(pt(9.5), serif=False)),
        ('CERTIFICATE ID', certificate.credential_id, _font(pt(9.5), bold=True, serif=False)),
        ('VERIFICATION CODE', certificate.public_id, _font(pt(6.8), mono=True)),
    ]
    label_font = _font(pt(6.2), bold=True, serif=False)
    # Label above its value, both right-aligned — a long verification code
    # can never collide with the label column.
    y = top + mm(5)
    for label, value, font in rows:
        lw = _spaced_width(draw, label, label_font, pt(1.0))
        _left_spaced(draw, label, value_x - lw, y, label_font, GOLD_DEEP, pt(1.0), anchor='ls')
        draw.text((value_x, y + mm(3.6)), value, font=font, fill=INK, anchor='rs')
        y += mm(8.6)


# ─── Text helpers ───────────────────────────────────────────────────────────

def _center(d, text, cx, y, font, fill):
    # Middle-middle anchor: (cx, y) is the visual centre of the line.
    d.text((cx, y), text, font=font, fill=fill, anchor='mm')


def _left_spaced(d, text, x, y, font, fill, spacing, anchor='la'):
    """PIL has no char spacing — advance glyph by glyph. ``y`` follows the
    given anchor for the FIRST glyph and is applied per glyph consistently."""
    if spacing <= 0:
        d.text((x, y), text, font=font, fill=fill, anchor=anchor)
        return
    cursor = x
    for ch in text:
        d.text((cursor, y), ch, font=font, fill=fill, anchor=anchor)
        cursor += d.textlength(ch, font=font) + spacing


def _center_spaced(d, text, cx, y, font, fill, spacing, anchor='mm'):
    w = _spaced_width(d, text, font, spacing)
    _left_spaced(d, text, cx - w / 2, y, font, fill, spacing, anchor=anchor)


def _spaced_width(d, text, font, spacing):
    if not text:
        return 0.0
    return d.textlength(text, font=font) + spacing * (len(text) - 1)


def _text_width(d, text, font):
    return d.textlength(text, font=font)


def _fit(text, max_w, start_pt, min_pt, *, serif=True):
    size = int(round(start_pt))
    minimum = int(round(min_pt))
    while size > minimum:
        font = _font(size, bold=True, serif=serif)
        if _probe.textlength(text, font=font) <= max_w:
            return font
        size -= 2
    return _font(minimum, bold=True, serif=serif)


# Shared draw surface purely for measuring text before an image exists.
_probe = ImageDraw.Draw(Image.new('RGB', (8, 8)))


def _wrap(d, text, font, max_w):
    if d.textlength(text, font=font) <= max_w:
        return [text]
    words, lines, current = text.split(), [], ''
    for word in words:
        candidate = (current + ' ' + word).strip()
        if d.textlength(candidate, font=font) <= max_w:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines or [text]


def _fmt_date(dt) -> str:
    try:
        return dt.strftime('%d %B %Y')
    except Exception:  # noqa: BLE001
        return datetime.now().strftime('%d %B %Y')
