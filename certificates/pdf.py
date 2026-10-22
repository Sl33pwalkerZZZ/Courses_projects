"""Render immutable certificate snapshots; never read or mutate learner records."""
from io import BytesIO
from pathlib import Path
from threading import Lock
from xml.sax.saxutils import escape

from django.conf import settings


class CertificatePDFUnavailable(RuntimeError):
    """The deployment has not provisioned its PDF dependency or Unicode fonts."""


_font_lock = Lock()


def render_certificate(certificate, verification_url):
    """Return a branded PDF for an issued, non-revoked snapshot.

    Authorization belongs to the calling view. Fonts must cover Cyrillic and
    Kazakh; deployments can supply CERTIFICATE_FONT_REGULAR / _BOLD paths.
    """
    if getattr(certificate, 'revoked_at', None):
        raise ValueError('Revoked certificates cannot be downloaded.')
    from urllib.parse import urlsplit
    parsed = urlsplit(verification_url)
    if parsed.scheme not in ('http', 'https') or not parsed.netloc or parsed.username or parsed.password:
        raise ValueError('A public HTTP(S) verification URL is required.')
    try:
        from reportlab.pdfgen import canvas
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        from reportlab.lib.colors import HexColor
        from reportlab.platypus import Paragraph
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.graphics import renderPDF
        from reportlab.graphics.shapes import Drawing
        from reportlab.graphics.barcode.qr import QrCodeWidget
    except ImportError as exc:
        raise CertificatePDFUnavailable('Provision ReportLab before enabling certificate PDF downloads.') from exc

    regular = Path(getattr(settings, 'CERTIFICATE_FONT_REGULAR', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
    bold = Path(getattr(settings, 'CERTIFICATE_FONT_BOLD', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))
    if not regular.is_file() or not bold.is_file():
        raise CertificatePDFUnavailable('Configure Unicode certificate font paths before enabling downloads.')
    # Font names include paths so settings changes cannot reuse an unrelated face.
    import hashlib
    face = 'Certificate-' + hashlib.sha256(str(regular).encode()).hexdigest()[:12]
    face_bold = 'Certificate-' + hashlib.sha256(str(bold).encode()).hexdigest()[:12]
    with _font_lock:
        if face not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(TTFont(face, str(regular)))
        if face_bold not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(TTFont(face_bold, str(bold)))
    for value in (certificate.learner_name, certificate.course_title, certificate.issuer_name):
        if not isinstance(value, str) or not value.strip():
            raise ValueError('Complete certificate snapshots are required.')
    output = BytesIO()
    page = canvas.Canvas(output, pagesize=(842, 595), pageCompression=1)
    page.setTitle('AI Courses — Course completion certificate')
    page.setAuthor(certificate.issuer_name)
    ink, purple, muted = map(HexColor, ('#20172F', '#7045B8', '#625B70'))
    page.setFillColor(HexColor('#FAF8FE'))
    page.rect(0, 0, 842, 595, fill=1, stroke=0)
    page.setStrokeColor(HexColor('#D8C9EE'))
    page.roundRect(22, 22, 798, 551, 14, stroke=1, fill=0)
    page.setStrokeColor(purple)
    page.setLineWidth(3)
    page.line(54, 518, 122, 518)

    def text(value, x, top, width, size=14, strong=False, color=ink, max_height=90):
        style = ParagraphStyle('certificate', fontName=face_bold if strong else face,
                               fontSize=size, leading=size * 1.35, textColor=color)
        paragraph = Paragraph(escape(str(value)), style)
        _, height = paragraph.wrap(width, max_height)
        if height > max_height:
            raise ValueError('Certificate text exceeds the printable layout; review learner/course names.')
        paragraph.drawOn(page, x, top - height)
        return height

    text('AI COURSES', 54, 553, 700, 14, True, purple)
    text('Сертификат об окончании курса', 54, 494, 725, 27, True)
    text('COURSE COMPLETION CERTIFICATE', 54, 450, 725, 10, color=muted)
    text('Подтверждает успешное выполнение требований курса:', 54, 414, 715, 12, color=muted)
    text(certificate.learner_name, 54, 380, 720, 25, True, max_height=70)
    text(certificate.course_title, 54, 295, 720, 19, True, max_height=80)
    text(certificate.issuer_name, 54, 194, 555, 12, True, max_height=34)
    text(certificate.issued_at.strftime('%d.%m.%Y'), 54, 151, 555, 11, color=muted)
    text('Проверка подлинности / Verify authenticity', 54, 125, 555, 10, color=muted)
    text(verification_url, 54, 105, 555, 9, color=purple, max_height=45)
    page.linkURL(verification_url, (54, 58, 610, 111), relative=0)
    widget = QrCodeWidget(verification_url, barLevel='M')
    x0, y0, x1, y1 = widget.getBounds()
    dimension = 104
    drawing = Drawing(dimension, dimension,
                      transform=[dimension/(x1-x0), 0, 0, dimension/(y1-y0), -x0, -y0])
    drawing.add(widget)
    renderPDF.draw(drawing, page, 670, 70)
    page.linkURL(verification_url, (670, 70, 774, 174), relative=0)
    text('Не является документом о высшем образовании или аккредитации.', 54, 48, 720, 8, color=muted, max_height=15)
    page.showPage()
    page.save()
    return output.getvalue()
