"""Issued snapshots are independent of later name confirmation and policy gates."""
from django.contrib.auth import get_user_model
from django.test import override_settings
from django.utils import timezone
from rest_framework.test import APITestCase
from courses.models import Course, Direction
from .models import Certificate, CourseCertificatePolicy


@override_settings(CERTIFICATES_ENABLED=True)
class CertificateProfileVisibilityTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        users = get_user_model()
        cls.owner = users.objects.create_user(username='visibility-owner')
        cls.other = users.objects.create_user(username='visibility-other')
        author = users.objects.create_user(username='visibility-author', role='author')
        course = Course.objects.create(title='Synthetic legacy course', slug='legacy-visibility',
            author=author, direction=Direction.objects.create(name='Fixture', slug='visibility'), is_published=True)
        CourseCertificatePolicy.objects.create(course=course, enabled=False, issuer_approved=False)
        cls.certificate = Certificate.objects.create(student=cls.owner, course=course,
            learner_name='Synthetic Learner', course_title=course.title, issuer_name='Synthetic Issuer',
            evidence={'lesson_ids': []})

    def test_existing_snapshot_visible_without_new_name_confirmation_or_enabled_policy(self):
        self.assertIsNone(self.owner.certificate_name_confirmed_at)
        self.client.force_authenticate(self.owner)
        response = self.client.get('/api/my/certificates/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['verification_code'], self.certificate.verification_code)
        self.assertEqual(response.data[0]['learner_name'], 'Synthetic Learner')
        self.assertFalse(response.data[0]['revoked'])

    def test_empty_and_other_account_do_not_expose_owner_certificate(self):
        self.client.force_authenticate(self.other)
        response = self.client.get('/api/my/certificates/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])
        self.assertEqual(self.client.get(f'/api/certificates/{self.certificate.verification_code}/download/').status_code, 404)

    def test_revoked_record_is_visible_as_revoked_not_silently_filtered(self):
        Certificate.objects.filter(pk=self.certificate.pk).update(revoked_at=timezone.now())
        self.client.force_authenticate(self.owner)
        response = self.client.get('/api/my/certificates/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data[0]['revoked'])
        self.assertEqual(self.client.get(f'/api/certificates/{self.certificate.verification_code}/download/').status_code, 403)

    @override_settings(CERTIFICATES_ENABLED=False)
    def test_disabled_issuance_keeps_owned_snapshot_visible(self):
        self.client.force_authenticate(self.owner)
        response = self.client.get('/api/my/certificates/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['verification_code'], self.certificate.verification_code)
        self.assertEqual(Certificate.objects.count(), 1)

    def test_anonymous_list_denied(self):
        self.assertEqual(self.client.get('/api/my/certificates/').status_code, 401)

    @override_settings(CERTIFICATES_ENABLED=False, CERTIFICATE_PUBLIC_ORIGIN='https://verification.example.invalid')
    def test_disabled_mode_owner_pdf_is_read_only_and_public_verification_stays_disabled(self):
        self.client.force_authenticate(self.owner)
        before = Certificate.objects.values().get(pk=self.certificate.pk)
        response = self.client.get(f'/api/certificates/{self.certificate.verification_code}/download/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertEqual(response['Cache-Control'], 'private, no-store')
        self.assertTrue(response.content.startswith(b'%PDF-'))
        self.assertEqual(Certificate.objects.values().get(pk=self.certificate.pk), before)
        self.assertEqual(Certificate.objects.count(), 1)
        self.assertFalse(CourseCertificatePolicy.objects.get().enabled)
        self.assertEqual(self.client.get(f'/api/certificates/verify/{self.certificate.verification_code}/').status_code, 404)
        self.assertEqual(self.client.get(f'/api/courses/{self.certificate.course_id}/certificate-status/').status_code, 404)

    @override_settings(CERTIFICATES_ENABLED=False, CERTIFICATE_PUBLIC_ORIGIN='https://verification.example.invalid')
    def test_disabled_mode_other_owner_and_revoked_guards(self):
        path = f'/api/certificates/{self.certificate.verification_code}/download/'
        self.client.force_authenticate(self.other)
        self.assertEqual(self.client.get(path).status_code, 404)
        self.assertEqual(self.client.get('/api/my/certificates/').data, [])
        self.client.force_authenticate(self.owner)
        Certificate.objects.filter(pk=self.certificate.pk).update(revoked_at=timezone.now())
        self.assertTrue(self.client.get('/api/my/certificates/').data[0]['revoked'])
        self.assertEqual(self.client.get(path).status_code, 403)

    @override_settings(CERTIFICATES_ENABLED=False, CERTIFICATE_PUBLIC_ORIGIN='')
    def test_disabled_mode_missing_trusted_origin_omits_verification_from_pdf(self):
        self.client.force_authenticate(self.owner)
        response = self.client.get(f'/api/certificates/{self.certificate.verification_code}/download/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.content.startswith(b'%PDF-'))
        self.assertNotIn(b'/URI', response.content)

    @override_settings(CERTIFICATES_ENABLED=False)
    def test_disabled_mode_jwt_missing_expired_and_valid(self):
        from datetime import timedelta
        from rest_framework_simplejwt.tokens import AccessToken
        path = f'/api/certificates/{self.certificate.verification_code}/download/'
        self.assertEqual(self.client.get('/api/my/certificates/').status_code, 401)
        self.assertEqual(self.client.get(path).status_code, 401)
        token = AccessToken.for_user(self.owner)
        token.set_exp(lifetime=timedelta(seconds=-60))
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        self.assertEqual(self.client.get('/api/my/certificates/').status_code, 401)
        self.assertEqual(self.client.get(path).status_code, 401)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {AccessToken.for_user(self.owner)}')
        response = self.client.get('/api/my/certificates/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    @override_settings(CERTIFICATES_ENABLED=False)
    def test_disabled_mode_blocks_api_and_service_mutations(self):
        from rest_framework.exceptions import PermissionDenied
        from .services import issue_certificate, revoke_certificate
        admin = get_user_model().objects.create_superuser(username='visibility-admin', password='synthetic-test')
        self.client.force_authenticate(admin)
        self.assertEqual(self.client.post('/api/certificates/admin/issue/', {
            'student_id': self.owner.pk, 'course_id': self.certificate.course_id, 'confirmation': True,
        }, format='json').status_code, 404)
        self.assertEqual(self.client.post(f'/api/certificates/admin/{self.certificate.verification_code}/revoke/', {'reason': 'Synthetic'}, format='json').status_code, 404)
        with self.assertRaises(PermissionDenied):
            issue_certificate(administrator=admin, student=self.owner, course_id=self.certificate.course_id)
        with self.assertRaises(PermissionDenied):
            revoke_certificate(administrator=admin, certificate=self.certificate, reason='Synthetic')
        self.certificate.refresh_from_db()
        self.assertIsNone(self.certificate.revoked_at)
        self.assertEqual(Certificate.objects.count(), 1)

    @override_settings(CERTIFICATES_ENABLED=False)
    def test_disabled_admin_can_read_but_cannot_mutate_policy_or_revoke(self):
        from django.contrib import admin
        from django.test import RequestFactory
        from django.urls import reverse
        user = get_user_model().objects.create_superuser(username='readonly-admin', password='synthetic-test')
        self.client.force_login(user)
        policy = CourseCertificatePolicy.objects.get()
        url = reverse('admin:certificates_coursecertificatepolicy_change', args=[policy.pk])
        self.assertEqual(self.client.get(url).status_code, 200)
        self.assertEqual(self.client.post(url, {'enabled': 'on', 'issuer_approved': 'on', 'issuer_name': 'Tampered'}).status_code, 403)
        self.assertEqual(self.client.get(reverse('admin:certificates_coursecertificatepolicy_add')).status_code, 403)
        request = RequestFactory().get('/admin/'); request.user = user
        self.assertNotIn('revoke_selected', admin.site._registry[Certificate].get_actions(request))
        policy.refresh_from_db()
        self.assertFalse(policy.enabled)
        self.assertFalse(policy.issuer_approved)

    @override_settings(CERTIFICATES_ENABLED=False)
    def test_disabled_private_read_routes_do_not_accept_mutations(self):
        self.client.force_authenticate(self.owner)
        before = Certificate.objects.values().get(pk=self.certificate.pk)
        for path in ['/api/my/certificates/', f'/api/certificates/{self.certificate.verification_code}/download/']:
            for method in ['post', 'put', 'patch', 'delete']:
                with self.subTest(path=path, method=method):
                    self.assertEqual(getattr(self.client, method)(path, {}, format='json').status_code, 405)
        self.assertEqual(Certificate.objects.values().get(pk=self.certificate.pk), before)


    @override_settings(CERTIFICATES_ENABLED=False, CERTIFICATE_PUBLIC_ORIGIN='')
    def test_owner_preview_and_download_same_pdf_without_mutations_or_host_fallback(self):
        import shutil
        import subprocess
        import tempfile
        from pathlib import Path
        self.client.force_authenticate(self.owner)
        path = f'/api/certificates/{self.certificate.verification_code}/download/'
        before = Certificate.objects.values().get(pk=self.certificate.pk)
        policy_before = CourseCertificatePolicy.objects.values().get()
        download = self.client.get(path)
        preview = self.client.get(path + '?preview=1')
        self.assertEqual(download.status_code, 200)
        self.assertEqual(preview.status_code, 200)
        self.assertEqual(download.content, preview.content)
        for response, disposition in [(download, 'attachment'), (preview, 'inline')]:
            self.assertTrue(response['Content-Disposition'].startswith(disposition + ';'))
            self.assertEqual(response['Content-Type'], 'application/pdf')
            self.assertEqual(response['Cache-Control'], 'private, no-store')
            self.assertEqual(response['X-Content-Type-Options'], 'nosniff')
            self.assertTrue(response.content.startswith(b'%PDF-'))
            self.assertNotIn(b'/URI', response.content)
        with tempfile.TemporaryDirectory(prefix='certificate-read-test-') as directory:
            pdf = Path(directory) / 'owner.pdf'
            pdf.write_bytes(preview.content)
            if shutil.which('pdftotext'):
                text = subprocess.check_output(['pdftotext', str(pdf), '-'], text=True)
                for value in [self.certificate.learner_name, self.certificate.course_title, self.certificate.issuer_name]:
                    self.assertIn(value, text)
            if shutil.which('pdftoppm'):
                subprocess.run(['pdftoppm', '-scale-to', '600', '-png', '-singlefile', str(pdf), directory+'/preview'], check=True, capture_output=True)
                self.assertTrue(Path(directory+'/preview.png').is_file())
        self.assertEqual(Certificate.objects.values().get(pk=self.certificate.pk), before)
        self.assertEqual(CourseCertificatePolicy.objects.values().get(), policy_before)
        self.assertFalse(self.client.get('/api/my/certificates/').data[0]['verification_available'])

    @override_settings(CERTIFICATES_ENABLED=False, CERTIFICATE_PUBLIC_ORIGIN='https://verification.example.invalid')
    def test_disabled_public_verification_never_embedded_even_with_origin(self):
        from unittest.mock import patch
        self.client.force_authenticate(self.owner)
        with patch('reportlab.graphics.barcode.qr.QrCodeWidget') as qr:
            response = self.client.get(f'/api/certificates/{self.certificate.verification_code}/download/?preview=1')
        self.assertEqual(response.status_code, 200)
        qr.assert_not_called()
        self.assertNotIn(b'/URI', response.content)

    @override_settings(CERTIFICATES_ENABLED=True)
    def test_invalid_configured_origins_are_omitted_without_using_host(self):
        self.client.force_authenticate(self.owner)
        path = f'/api/certificates/{self.certificate.verification_code}/download/?preview=1'
        for origin in ['javascript:alert(1)', 'https://user:pass@example.invalid', 'https://example.invalid/path', 'https://example.invalid?query=1', 'https://example.invalid:invalid']:
            with self.subTest(origin=origin), self.settings(CERTIFICATE_PUBLIC_ORIGIN=origin):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200)
                self.assertNotIn(b'/URI', response.content)

    @override_settings(CERTIFICATES_ENABLED=False, CERTIFICATE_PUBLIC_ORIGIN='')
    def test_preview_authorization_and_revocation_match_download(self):
        path = f'/api/certificates/{self.certificate.verification_code}/download/?preview=1'
        self.assertEqual(self.client.get(path).status_code, 401)
        self.client.force_authenticate(self.other)
        self.assertEqual(self.client.get(path).status_code, 404)
        self.client.force_authenticate(self.owner)
        Certificate.objects.filter(pk=self.certificate.pk).update(revoked_at=timezone.now())
        response = self.client.get(path)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response['Cache-Control'], 'private, no-store')
