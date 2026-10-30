"""Professional, print-friendly PDF certificate rendering.

Uses ReportLab to draw a landscape certificate and qrcode to embed a QR that
points at the *real* public verification URL. No fabricated seals, partner
logos, or invented signatures — only the Code Yaar brand, the verified record,
and the authorized-issuer designation.
"""

import io
from datetime import datetime

import qrcode
from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

# Brand palette (kept in sync with the Code Yaar identity).
INK = colors.HexColor('#0f172a')        # deep slate
ACCENT = colors.HexColor('#6d28d9')     # violet
ACCENT_SOFT = colors.HexColor('#a78bfa')
GOLD = colors.HexColor('#b45309')       # restrained accent rule
PAPER = colors.white

BRAND = 'Code Yaar'
TAGLINE = 'Think. Build. Evolve.'
DESIGNATION = 'Certificate of Completion'
ISSUER = 'Code Yaar Academy'


def _qr_png_bytes(data: str) -> io.BytesIO:
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=2,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color='#0f172a', back_color='white')
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return buf


def render_certificate_pdf(certificate) -> io.BytesIO:
    """Draw the certificate and return a seekable BytesIO of the PDF."""
    page = landscape(A4)
    width, height = page
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=page)
    c.setTitle(f'{BRAND} {DESIGNATION} — {certificate.credential_id}')
    c.setAuthor(ISSUER)

    # ── Background + frame ──
    c.setFillColor(PAPER)
    c.rect(0, 0, width, height, fill=1, stroke=0)

    margin = 14 * mm
    # Outer rule
    c.setFillColor(INK)
    c.rect(margin, margin, width - 2 * margin, height - 2 * margin, fill=1, stroke=0)
    # Inner paper
    pad = 4 * mm
    inner = margin + pad
    c.setFillColor(PAPER)
    c.rect(inner, inner, width - 2 * inner, height - 2 * inner, fill=1, stroke=0)
    # Accent hairline frame
    c.setStrokeColor(ACCENT)
    c.setLineWidth(0.8)
    c.rect(inner + 3 * mm, inner + 3 * mm,
           width - 2 * (inner + 3 * mm), height - 2 * (inner + 3 * mm))

    cx = width / 2

    # ── Brand ──
    c.setFillColor(ACCENT)
    c.setFont('Helvetica-Bold', 26)
    c.drawCentredString(cx, height - inner - 20 * mm, BRAND)
    c.setFillColor(INK)
    c.setFont('Helvetica-Oblique', 10)
    c.drawCentredString(cx, height - inner - 25.5 * mm, TAGLINE)

    # ── Designation ──
    c.setFont('Helvetica-Bold', 18)
    c.setFillColor(INK)
    c.drawCentredString(cx, height - inner - 40 * mm, DESIGNATION.upper())

    # gold rule under designation
    c.setStrokeColor(GOLD)
    c.setLineWidth(1.2)
    rule_w = 60 * mm
    c.line(cx - rule_w / 2, height - inner - 44 * mm,
           cx + rule_w / 2, height - inner - 44 * mm)

    # ── Body copy ──
    c.setFont('Helvetica', 11)
    c.setFillColor(colors.HexColor('#334155'))
    c.drawCentredString(cx, height - inner - 54 * mm, 'This is to certify that')

    # Student name
    name = certificate.student_name or 'Learner'
    c.setFillColor(INK)
    c.setFont('Helvetica-Bold', 30)
    # shrink long names to fit
    name_w = c.stringWidth(name, 'Helvetica-Bold', 30)
    max_w = width - 2 * inner - 40 * mm
    if name_w > max_w:
        c.setFont('Helvetica-Bold', max(14, int(30 * max_w / name_w)))
    c.drawCentredString(cx, height - inner - 68 * mm, name)

    # underline for name
    c.setStrokeColor(ACCENT_SOFT)
    c.setLineWidth(0.6)
    c.line(cx - 60 * mm, height - inner - 72 * mm,
           cx + 60 * mm, height - inner - 72 * mm)

    # Course statement
    c.setFont('Helvetica', 11)
    c.setFillColor(colors.HexColor('#334155'))
    c.drawCentredString(cx, height - inner - 80 * mm, 'has successfully completed the course')
    c.setFont('Helvetica-Bold', 16)
    c.setFillColor(ACCENT)
    c.drawCentredString(cx, height - inner - 89 * mm, certificate.course_title)

    # Score line, if the policy grades one
    if certificate.final_score is not None:
        c.setFont('Helvetica', 10.5)
        c.setFillColor(colors.HexColor('#334155'))
        c.drawCentredString(
            cx, height - inner - 96.5 * mm,
            f'Final assessment score: {certificate.final_score:g}%'
        )

    # ── Footer: dates / credential / issuer (left), QR (right) ──
    foot_y = inner + 20 * mm
    c.setFillColor(INK)
    c.setFont('Helvetica-Bold', 10)
    left_x = inner + 14 * mm
    c.drawString(left_x, foot_y + 12 * mm, 'Issued')
    c.setFont('Helvetica', 10)
    c.drawString(left_x, foot_y + 6 * mm,
                 _fmt_date(certificate.issued_at))

    c.setFont('Helvetica-Bold', 10)
    col2 = left_x + 58 * mm
    c.drawString(col2, foot_y + 12 * mm, 'Credential ID')
    c.setFont('Helvetica', 10)
    c.drawString(col2, foot_y + 6 * mm, certificate.credential_id)

    # Authorized issuer designation (no invented signature)
    c.setFont('Helvetica-Bold', 10)
    c.drawString(left_x, foot_y - 6 * mm, 'Authorized by')
    c.setFont('Helvetica', 10)
    c.drawString(left_x, foot_y - 12 * mm, ISSUER)

    # ── QR verification block (right) ──
    url = certificate.verification_url()
    qr_buf = _qr_png_bytes(url)
    qr_img = ImageReader(qr_buf)
    qr_size = 30 * mm
    qr_x = width - inner - qr_size - 12 * mm
    qr_y = foot_y - 6 * mm
    c.drawImage(qr_img, qr_x, qr_y, width=qr_size, height=qr_size)
    c.setFont('Helvetica', 8)
    c.setFillColor(colors.HexColor('#475569'))
    c.drawCentredString(qr_x + qr_size / 2, qr_y - 5 * mm, 'Scan to verify')
    # Wrap the (possibly long) URL onto two lines under the label.
    _draw_wrapped_centered(c, url, qr_x + qr_size / 2, qr_y - 9.5 * mm,
                           width=qr_size + 20 * mm, font='Helvetica', size=7)

    c.showPage()
    c.save()
    buf.seek(0)
    return buf


def _fmt_date(dt) -> str:
    try:
        return dt.strftime('%d %B %Y')
    except Exception:  # noqa: BLE001
        return datetime.now().strftime('%d %B %Y')


def _draw_wrapped_centered(c, text, cx, y, width, font, size):
    c.setFont(font, size)
    words = text.split('/')
    # Rejoin but allow breaks on '/' boundaries for long URLs.
    pieces = []
    line = ''
    for w in words:
        candidate = (line + '/' + w) if line else w
        if c.stringWidth(candidate + '/', font, size) > width and line:
            pieces.append(line + '/')
            line = w
        else:
            line = candidate
    if line:
        pieces.append(line)
    for i, piece in enumerate(pieces):
        c.drawCentredString(cx, y - i * 4 * mm, piece)
