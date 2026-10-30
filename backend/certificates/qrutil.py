"""QR codes that encode the live public verification URL."""

import base64
import io

import qrcode


def qr_png_bytes(data: str, *, box_size: int = 12, border: int = 2) -> io.BytesIO:
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=box_size,
        border=border,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color='#111827', back_color='white')
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return buf


def qr_data_url(data: str) -> str:
    raw = qr_png_bytes(data, box_size=8, border=1).getvalue()
    return 'data:image/png;base64,' + base64.b64encode(raw).decode('ascii')
