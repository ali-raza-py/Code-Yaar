"""Premium academic certificate rendering (ReportLab) — A4 landscape.

Design system (mirrored 1:1 by ``png.py`` and the on-screen sheet in
``frontend/src/components/credentials/certificate-artwork.tsx``):

    ivory paper → burgundy/gold/burgundy triple frame → ornamental corners
    faint geometric + wordmark watermark → centred brand band (logo mark,
    CODE YAAR wordmark, tagline) → serif designation → statement, recipient
    name, course → digital authorisation mark bottom-left → ONE compact
    verification block bottom-right (issue date, certificate ID,
    verification code, QR + "scan to verify").

The QR encodes the live public verification URL — never a placeholder —
and no verification datum is ever printed twice.
"""

import io
import os
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from .qrutil import qr_png_bytes

# ─── Certificate palette (brand purple is reserved for the logo mark) ───
BURGUNDY = colors.HexColor('#751D2B')
BURGUNDY_SOFT = colors.HexColor('#8C2F3F')
GOLD = colors.HexColor('#C49A48')
GOLD_DEEP = colors.HexColor('#9A7B32')
PURPLE = colors.HexColor('#7528E8')
INK = colors.HexColor('#171717')
MUTED = colors.HexColor('#5C564E')
IVORY = colors.HexColor('#FCFAF3')
WATERMARK = colors.HexColor('#F6F1E7')  # barely-there tone on ivory paper
WATERMARK_LINE = colors.HexColor('#ECE5D6')

BRAND = 'CODE YAAR'
TAGLINE = 'Think. Build. Evolve.'
DESIGNATION = 'CERTIFICATE OF COMPLETION'
ISSUER = 'Code Yaar Academy'

# Serif/sans families; upgraded to Georgia when the platform ships it.
_SERIF = 'Times-Bold'
_SERIF_REG = 'Times-Roman'
_SERIF_IT = 'Times-Italic'
_SANS = 'Helvetica'
_SANS_BOLD = 'Helvetica-Bold'
_MONO = 'Courier'


def _try_register_fonts():
    """Prefer Georgia (true italic, elegant figures) over core Times."""
    global _SERIF, _SERIF_REG, _SERIF_IT, _SANS, _SANS_BOLD
    candidates = [
        {
            'CYSerif-Bold': r'C:\Windows\Fonts\georgiab.ttf',
            'CYSerif': r'C:\Windows\Fonts\georgia.ttf',
            'CYSerif-Italic': r'C:\Windows\Fonts\georgiai.ttf',
            'CYSans': r'C:\Windows\Fonts\segoeui.ttf',
            'CYSans-Bold': r'C:\Windows\Fonts\segoeuib.ttf',
        },
        {
            'CYSerif-Bold': '/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf',
            'CYSerif': '/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf',
            'CYSerif-Italic': '/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf',
            'CYSans': '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
            'CYSans-Bold': '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
        },
    ]
    for pack in candidates:
        if all(os.path.exists(path) for path in pack.values()):
            try:
                for name, path in pack.items():
                    pdfmetrics.registerFont(TTFont(name, path))
                _SERIF, _SERIF_REG, _SERIF_IT = 'CYSerif-Bold', 'CYSerif', 'CYSerif-Italic'
                _SANS, _SANS_BOLD = 'CYSans', 'CYSans-Bold'
                return
            except Exception:  # noqa: BLE001
                continue


_try_register_fonts()


def render_certificate_pdf(certificate) -> io.BytesIO:
    page = landscape(A4)
    width, height = page
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=page)
    c.setTitle(f'{ISSUER} {DESIGNATION} — {certificate.credential_id}')
    c.setAuthor(ISSUER)
    c.setSubject(certificate.course_title)
    _draw_certificate(c, certificate, width, height)
    c.showPage()
    c.save()
    buf.seek(0)
    return buf


# ─── Composition ────────────────────────────────────────────────────────────

def _draw_certificate(c, certificate, width, height):
    c.setFillColor(IVORY)
    c.rect(0, 0, width, height, fill=1, stroke=0)

    _draw_watermark(c, width, height)
    _draw_frame(c, width, height)

    inner_left, inner_right = 22 * mm, width - 22 * mm
    footer_base = 20 * mm          # baseline zone of the bottom bands
    footer_top = footer_base + 30 * mm
    header_bottom = _draw_header(c, width, height)
    _draw_statement(c, certificate, width, header_bottom, footer_top, inner_left, inner_right)
    _draw_authorisation(c, inner_left, footer_base)
    _draw_verification(c, certificate, inner_right, footer_base)


def _draw_watermark(c, width, height):
    """Faint original Code Yaar emblem + wordmark behind the content."""
    cx, cy = width / 2, height / 2 - 6 * mm
    _emblem_mark(c, cx, cy + 30 * mm, 26 * mm, WATERMARK)
    c.setFillColor(WATERMARK)
    _spaced_centred(c, cx, cy - 8 * mm, BRAND, _SERIF, 74, 10)


def _draw_frame(c, width, height):
    """Burgundy → gold → burgundy triple rule with ornamental corners."""
    layers = [
        (8.0 * mm, BURGUNDY, 2.6),
        (11.2 * mm, GOLD, 0.9),
        (13.0 * mm, BURGUNDY, 0.5),
    ]
    for margin, colour, line_w in layers:
        c.setStrokeColor(colour)
        c.setLineWidth(line_w)
        c.rect(margin, margin, width - 2 * margin, height - 2 * margin, fill=0, stroke=1)

    # Ornamental corner motifs sitting on the innermost rule.
    x0, y0 = 13.0 * mm, 13.0 * mm
    x1, y1 = width - x0, height - y0
    for cx, cy, sx, sy in ((x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)):
        _corner_flourish(c, cx, cy, sx, sy)


def _corner_flourish(c, x, y, sx, sy):
    arm = 14 * mm
    c.saveState()
    c.translate(x, y)
    c.scale(sx, sy)
    # Twin hairlines along each edge of the corner.
    c.setStrokeColor(BURGUNDY_SOFT)
    c.setLineWidth(0.5)
    c.line(0, 2.2 * mm, arm, 2.2 * mm)
    c.line(2.2 * mm, 0, 2.2 * mm, arm)
    # Gold diamond with a centre dot at the vertex.
    d = 2.6 * mm
    c.setFillColor(GOLD)
    path = c.beginPath()
    path.moveTo(4.6 * mm, 0)
    path.lineTo(4.6 * mm + d / 2, d / 2)
    path.lineTo(4.6 * mm, d)
    path.lineTo(4.6 * mm - d / 2, d / 2)
    path.close()
    c.drawPath(path, fill=1, stroke=0)
    c.setFillColor(BURGUNDY)
    c.circle(4.6 * mm + d / 2, d / 2, 0.45 * mm, fill=1, stroke=0)
    c.restoreState()


def _emblem_mark(c, cx, cy, size, colour):
    """Original Code Yaar logo mark: a diamond holding code chevrons."""
    half = size / 2
    c.saveState()
    c.setStrokeColor(colour)
    c.setFillColor(colour)

    # Diamond outline.
    path = c.beginPath()
    path.moveTo(cx, cy + half)
    path.lineTo(cx + half, cy)
    path.lineTo(cx, cy - half)
    path.lineTo(cx - half, cy)
    path.close()
    c.setLineWidth(max(1.0, size * 0.055))
    c.setStrokeColor(colour if colour is PURPLE else BURGUNDY)
    if colour is WATERMARK:
        c.setStrokeColor(WATERMARK_LINE)
    c.drawPath(path, fill=0, stroke=1)

    # Chevrons < > and a slash inside — proportions keyed to the mark size.
    s = size
    c.setLineWidth(max(1.2, s * 0.06))
    c.setStrokeColor(colour)
    gap = 0.30 * s
    arm = 0.13 * s
    c.line(cx - gap + arm * 0.55, cy + arm, cx - gap - arm * 0.55, cy)
    c.line(cx - gap - arm * 0.55, cy, cx - gap + arm * 0.55, cy - arm)
    c.line(cx + gap - arm * 0.55, cy + arm, cx + gap + arm * 0.55, cy)
    c.line(cx + gap + arm * 0.55, cy, cx + gap - arm * 0.55, cy - arm)
    c.setLineWidth(max(1.0, s * 0.045))
    c.line(cx - 0.045 * s, cy - arm * 1.15, cx + 0.045 * s, cy + arm * 1.15)
    c.restoreState()


def _draw_header(c, width, height):
    """Brand band: mark, wordmark, tagline, rule, designation. Returns the
    y-coordinate just below the band (ReportLab bottom-up coordinates)."""
    cx = width / 2
    y = height - 20 * mm

    _emblem_mark(c, cx, y - 4.5 * mm, 9.5 * mm, PURPLE)
    y -= 14.5 * mm

    c.setFillColor(INK)
    _spaced_centred(c, cx, y, BRAND, _SERIF, 25, 3.2)
    y -= 7.5 * mm

    c.setFillColor(GOLD_DEEP)
    c.setFont(_SERIF_IT, 11)
    c.drawCentredString(cx, y, TAGLINE)
    y -= 8.5 * mm

    _ornamental_rule(c, cx, y, 84 * mm)
    y -= 11 * mm

    c.setFillColor(BURGUNDY)
    _spaced_centred(c, cx, y, DESIGNATION, _SERIF, 15.5, 3.6)
    y -= 6 * mm
    # Fine gold underline beneath the designation.
    text_w = _spaced_width(DESIGNATION, _SERIF, 15.5, 3.6)
    c.setStrokeColor(GOLD)
    c.setLineWidth(0.7)
    c.line(cx - text_w / 2, y, cx + text_w / 2, y)
    return y - 6 * mm


def _ornamental_rule(c, cx, y, width_):
    c.setStrokeColor(GOLD)
    c.setLineWidth(0.8)
    c.line(cx - width_ / 2, y, cx - 3.2 * mm, y)
    c.line(cx + 3.2 * mm, y, cx + width_ / 2, y)
    # Centre diamond flanked by dots.
    d = 2.4 * mm
    c.setFillColor(BURGUNDY)
    path = c.beginPath()
    path.moveTo(cx, y + d / 2)
    path.lineTo(cx + d / 2, y)
    path.lineTo(cx, y - d / 2)
    path.lineTo(cx - d / 2, y)
    path.close()
    c.drawPath(path, fill=1, stroke=0)
    c.setFillColor(GOLD)
    c.circle(cx - 6.5 * mm, y, 0.7 * mm, fill=1, stroke=0)
    c.circle(cx + 6.5 * mm, y, 0.7 * mm, fill=1, stroke=0)


def _draw_statement(c, certificate, width, header_bottom, footer_top, inner_left, inner_right):
    """Statement, recipient name, course title and (when graded) the score —
    vertically centred inside the band left between header and footer."""
    cx = width / 2
    max_text_w = inner_right - inner_left - 10 * mm

    name = (certificate.student_name or 'Learner').strip()
    course = (certificate.course_title or 'Course').strip()

    course_size = _fit_font(c, course, _SERIF, 17.5, max_text_w, 12)
    course_lines = _wrap(c, course, _SERIF, course_size, max_text_w)[:2]

    block_h = (
        6.5 + 13.5 + 4.5 + 6.5 + 9.5            # statement/name/rule/statement/course
        + (len(course_lines) - 1) * 6.8
        + (8.5 if certificate.final_score is not None else 0)
    ) * mm
    gap = max(header_bottom - footer_top - block_h, 0) / 2
    y = header_bottom - gap

    c.setFillColor(MUTED)
    c.setFont(_SERIF_IT, 11.5)
    c.drawCentredString(cx, y, 'This is to certify that')
    y -= 13.5 * mm

    name_size = _fit_font(c, name, _SERIF, 33, max_text_w, 16)
    c.setFillColor(INK)
    c.setFont(_SERIF, name_size)
    c.drawCentredString(cx, y, name)
    y -= 4.5 * mm

    rule_w = min(max(c.stringWidth(name, _SERIF, name_size) + 24 * mm, 70 * mm), 150 * mm)
    c.setStrokeColor(BURGUNDY)
    c.setLineWidth(1.0)
    c.line(cx - rule_w / 2, y, cx + rule_w / 2, y)
    c.setStrokeColor(GOLD)
    c.setLineWidth(0.5)
    c.line(cx - rule_w / 2, y - 1.2 * mm, cx + rule_w / 2, y - 1.2 * mm)
    y -= 6.5 * mm

    c.setFillColor(MUTED)
    c.setFont(_SERIF_IT, 11.5)
    c.drawCentredString(cx, y, 'has successfully completed')
    y -= 9.5 * mm

    c.setFillColor(BURGUNDY)
    c.setFont(_SERIF, course_size)
    for i, line in enumerate(course_lines):
        c.drawCentredString(cx, y - i * 6.8 * mm, line)
    y -= (len(course_lines) - 1) * 6.8 * mm

    if certificate.final_score is not None:
        y -= 8.5 * mm
        c.setFillColor(MUTED)
        c.setFont(_SANS, 9.5)
        c.drawCentredString(
            cx, y, f'Final assessment score  ·  {certificate.final_score:g}%'
        )


def _draw_authorisation(c, x, base):
    """Bottom-left digital authorisation mark — no fabricated person."""
    c.setFillColor(INK)
    c.setFont(_SERIF_IT, 19)
    c.drawString(x + 2 * mm, base + 10 * mm, 'Code Yaar')

    c.setStrokeColor(BURGUNDY)
    c.setLineWidth(0.8)
    c.line(x, base + 7.6 * mm, x + 58 * mm, base + 7.6 * mm)

    c.setFillColor(GOLD_DEEP)
    _spaced_left(c, x, base + 4.0 * mm, 'CODE YAAR ACADEMY', _SANS_BOLD, 7.2, 1.6)

    c.setFillColor(MUTED)
    c.setFont(_SANS, 6.6)
    c.drawString(x, base + 0.6 * mm, 'Authorized by  ·  digitally issued credential')


def _draw_verification(c, certificate, right, base):
    """Bottom-right verification block — the ONLY place credential
    identifiers appear: issue date, certificate ID, verification code, QR."""
    url = certificate.verification_url()
    qr_size = 24 * mm
    qr_x = right - qr_size
    qr_y = base + 5.5 * mm

    c.setFillColor(colors.white)
    c.setStrokeColor(BURGUNDY)
    c.setLineWidth(0.5)
    c.rect(qr_x - 1.2 * mm, qr_y - 1.2 * mm, qr_size + 2.4 * mm, qr_size + 2.4 * mm, fill=1, stroke=1)
    c.drawImage(ImageReader(qr_png_bytes(url)), qr_x, qr_y, width=qr_size, height=qr_size, mask='auto')

    c.setFillColor(MUTED)
    _spaced_centred(c, qr_x + qr_size / 2, base + 1.4 * mm, 'SCAN TO VERIFY', _SANS_BOLD, 6.2, 1.2)

    # Right-aligned label/value rows to the left of the QR: the small-caps
    # label sits above its value so a long verification code can never
    # collide with the label column.
    value_x = qr_x - 5 * mm
    rows = [
        ('ISSUE DATE', _fmt_date(certificate.issued_at), _SANS, 9.5),
        ('CERTIFICATE ID', certificate.credential_id, _SANS_BOLD, 9.5),
        ('VERIFICATION CODE', certificate.public_id, _MONO, 6.8),
    ]
    y = base + 27 * mm
    for label, value, font, size in rows:
        c.setFillColor(GOLD_DEEP)
        label_w = _spaced_width(label, _SANS_BOLD, 6.2, 1.0)
        _spaced_left(c, value_x - label_w, y, label, _SANS_BOLD, 6.2, 1.0)
        c.setFillColor(INK)
        c.setFont(font, size)
        c.drawRightString(value_x, y - 3.4 * mm, value)
        y -= 8.6 * mm


# ─── Text helpers ───────────────────────────────────────────────────────────

def _spaced_width(text, font, size, spacing):
    return pdfmetrics.stringWidth(text, font, size) + spacing * max(len(text) - 1, 0)


def _spaced_left(c, x, y, text, font, size, spacing):
    """drawString with letter spacing (canvas has no setCharSpace)."""
    c.setFont(font, size)
    cursor = x
    for ch in text:
        c.drawString(cursor, y, ch)
        cursor += c.stringWidth(ch, font, size) + spacing


def _spaced_centred(c, cx, y, text, font, size, spacing):
    total = _spaced_width(text, font, size, spacing)
    _spaced_left(c, cx - total / 2, y, text, font, size, spacing)


def _fit_font(c, text, font, size, max_width, min_size):
    while size > min_size and c.stringWidth(text, font, size) > max_width:
        size -= 0.5
    return size


def _wrap(c, text, font, size, max_width):
    if c.stringWidth(text, font, size) <= max_width:
        return [text]
    words = text.split()
    lines, current = [], ''
    for word in words:
        candidate = (current + ' ' + word).strip()
        if c.stringWidth(candidate, font, size) <= max_width:
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
