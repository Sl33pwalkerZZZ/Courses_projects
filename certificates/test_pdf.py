"""PDF checks do not create certificate records or access the development DB."""
import importlib.util
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from unittest import skipUnless

from django.test import SimpleTestCase, override_settings

from .pdf import CertificatePDFUnavailable, render_certificate


def sample_certificate(**changes):
    fields = dict(learner_name='SAMPLE — Әлия Қасымқызы',
                  course_title='SAMPLE — Как выбрать нейросеть под свою задачу',
                  issuer_name='SAMPLE / DEMONSTRATION — not an approved issuer',
                  issued_at=datetime(2026, 10, 22, tzinfo=timezone.utc),
                  verification_code='sample-not-a-real-certificate', revoked_at=None)
    fields.update(changes)
    return SimpleNamespace(**fields)


class CertificatePDFGuardTests(SimpleTestCase):
    def test_revoked_certificate_is_not_downloadable(self):
        with self.assertRaises(ValueError):
            render_certificate(sample_certificate(revoked_at=datetime.now(timezone.utc)), 'https://example.invalid/verify/sample')

    def test_nonpublic_or_unsafe_link_is_rejected(self):
        for url in ('javascript:alert(1)', '/relative', 'https://user:secret@example.invalid'):
            with self.subTest(url=url), self.assertRaises(ValueError):
                render_certificate(sample_certificate(), url)

    def test_missing_dependency_is_an_explicit_deployment_blocker(self):
        if importlib.util.find_spec('reportlab'):
            self.skipTest('ReportLab is provisioned in this runtime.')
        with self.assertRaises(CertificatePDFUnavailable):
            render_certificate(sample_certificate(), 'https://example.invalid/verify/sample')


@skipUnless(importlib.util.find_spec('reportlab'), 'ReportLab must be provisioned for rendering checks.')
class CertificatePDFRenderingTests(SimpleTestCase):
    def test_pdf_unicode_text_and_verification_link(self):
        url = 'https://example.invalid/certificates/verify/sample-not-a-real-certificate'
        pdf = render_certificate(sample_certificate(), url)
        self.assertTrue(pdf.startswith(b'%PDF-'))
        self.assertIn(url.encode(), pdf)  # PDF URI annotation, independent of QR.
        if not shutil.which('pdftotext'):
            self.skipTest('pdftotext unavailable for Unicode extraction.')
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'sample.pdf'
            path.write_bytes(pdf)
            text = subprocess.check_output(['pdftotext', str(path), '-'], text=True)
            if shutil.which('pdftoppm'):
                raster = Path(directory) / 'rendered'
                subprocess.run(['pdftoppm', '-scale-to', '800', '-png', '-singlefile', str(path), str(raster)], check=True, capture_output=True)
                self.assertTrue(raster.with_suffix('.png').is_file())
        for expected in ('Әлия Қасымқызы', 'Как выбрать нейросеть', '22.10.2026', 'SAMPLE'):
            self.assertIn(expected, text)

    @override_settings(CERTIFICATE_FONT_REGULAR='/missing/unicode-font.ttf')
    def test_missing_font_is_explicit_blocker(self):
        with self.assertRaises(CertificatePDFUnavailable):
            render_certificate(sample_certificate(), 'https://example.invalid/verify/sample')

    def test_qr_contains_exact_public_verification_url(self):
        # Exercise the real ReportLab encoder, rather than a placeholder image.
        from unittest.mock import patch
        from reportlab.graphics.barcode.qr import QrCodeWidget
        observed = []
        def qr(value, **kwargs):
            observed.append(value)
            return QrCodeWidget(value, **kwargs)
        url = 'https://example.invalid/verify/sample'
        with patch('reportlab.graphics.barcode.qr.QrCodeWidget', side_effect=qr):
            render_certificate(sample_certificate(), url)
        self.assertEqual(observed, [url])
