"""Opt-in real MP4 verification, exclusively in the Django test DB/temp storage.

AI_COURSES_TEST_VIDEO can point to a local sample. No sample is committed or
generated. Tests skip clearly when the sample or required system tools are absent.
"""
import hashlib
import os
from datetime import timedelta
from pathlib import Path
import shutil
import subprocess
import unittest

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from . import test_attachments as fixtures
from .models import LessonAttachment, LessonPlaybackGrant
from progress.models import Enrollment


SAMPLE = Path(os.environ.get('AI_COURSES_TEST_VIDEO', Path(settings.BASE_DIR) / '.local-video-test/sample.mp4'))
VTT = ('WEBVTT\n\n00:00:00.000 --> 00:00:06.000\nТестовый видеоряд: 0–6 секунд.\n\n'
       '00:00:06.000 --> 00:00:12.000\nТестовый видеоряд: 6–12 секунд.\n').encode('utf-8')


@unittest.skipUnless(SAMPLE.is_file() and shutil.which('ffprobe'), 'Provide local MP4 sample and ffprobe')
class RealVideoTests(TestCase):
    def setUp(self):
        # Creates only isolated fixture users/course/lesson and temporary MEDIA_ROOT.
        fixtures.AttachmentAPITests.setUp(self)
        self.client = self.authenticated(self.owner)
        self.raw = SAMPLE.read_bytes()
        self.result = self.upload_file('sample.mp4', self.raw, 'video/mp4')
        self.assertEqual(self.result.status_code, 201)
        self.asset = LessonAttachment.objects.get(pk=self.result.data['id'])
        self.grant_url = self.result.data['playback_grant_url']

    @staticmethod
    def authenticated(user):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {RefreshToken.for_user(user).access_token}')
        return client

    def upload_file(self, filename, raw, mime):
        return self.client.post(self.upload, {
            'file': SimpleUploadedFile(filename, raw, content_type=mime),
            'label': 'Isolated playback verification', 'caption': 'Temporary synthetic test material',
            'transcript': 'Synthetic video test pattern; no educational narration asserted.',
            'provenance': 'Local test input; not a production course asset', 'after_section': 'Section',
        }, format='multipart')

    def browser_grant(self, user=None):
        authorized = self.authenticated(user or self.owner)
        response = authorized.post(self.grant_url)
        self.assertEqual(response.status_code, 200)
        browser = APIClient()  # Native media sends cookies, never a JWT header.
        browser.cookies = authorized.cookies
        return browser, response.data

    def body(self, response):
        try:
            return b''.join(response.streaming_content)
        finally:
            response.close()

    def test_actual_ffprobe_upload_and_byte_identical_complete_delivery(self):
        self.assertEqual(self.asset.sha256, hashlib.sha256(self.raw).hexdigest())
        self.assertEqual(self.asset.mime_type, 'video/mp4')
        repeat = self.upload_file('sample.mp4', self.raw, 'video/mp4')
        self.assertEqual(repeat.status_code, 200)
        self.assertEqual(repeat.data['id'], self.asset.pk)
        self.assertEqual(LessonAttachment.objects.count(), 1)
        browser, grant = self.browser_grant()
        response = browser.get(grant['url'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Length'], str(len(self.raw)))
        self.assertEqual(self.body(response), self.raw)

    @unittest.skipUnless(shutil.which('ffmpeg'), 'ffmpeg required for actual decode verification')
    def test_delivered_video_decodes_and_ffmpeg_can_seek(self):
        browser, grant = self.browser_grant()
        received = self.body(browser.get(grant['url']))
        target = Path(self.temp.name) / 'received-owned-fixture.mp4'
        target.write_bytes(received)
        for seek in [[], ['-ss', '8']]:
            result = subprocess.run([
                shutil.which('ffmpeg'), '-v', 'error', '-xerror', '-nostdin', *seek,
                '-i', str(target), '-f', 'null', '-',
            ], capture_output=True, timeout=30)
            self.assertEqual(result.returncode, 0, 'Delivered sample failed real FFmpeg decode/seek')
            self.assertEqual(result.stderr, b'')

    def test_actual_media_ranges_head_and_invalid_ranges(self):
        browser, grant = self.browser_grant()
        size = len(self.raw)
        for header, start, end in [('bytes=0-0', 0, 1), ('bytes=1000-1999', 1000, 2000),
                                   ('bytes=-512', size-512, size), ('bytes=1000000-', 1000000, size)]:
            response = browser.get(grant['url'], HTTP_RANGE=header)
            self.assertEqual(response.status_code, 206)
            self.assertEqual(response['Content-Range'], f'bytes {start}-{end-1}/{size}')
            self.assertEqual(response['Content-Length'], str(end-start))
            self.assertEqual(self.body(response), self.raw[start:end])
        head = browser.head(grant['url'], HTTP_RANGE='bytes=0-1')
        self.assertEqual(head.status_code, 200)
        self.assertEqual(head['Accept-Ranges'], 'bytes')
        self.assertEqual(head['Content-Length'], str(size))
        self.assertEqual(head.content, b'')
        for invalid in [f'bytes={size}-', 'bytes=0-1,3-4', 'bytes=8-2', 'garbage']:
            response = browser.get(grant['url'], HTTP_RANGE=invalid)
            self.assertEqual(response.status_code, 416)
            self.assertEqual(response['Content-Range'], f'bytes */{size}')

    def test_author_admin_and_enrollment_permissions_with_real_jwt(self):
        self.assertEqual(APIClient().post(self.grant_url).status_code, 401)
        for user in [self.student, self.other]:
            self.assertEqual(self.authenticated(user).post(self.grant_url).status_code, 403)
        for user in [self.owner, self.admin]:
            browser, grant = self.browser_grant(user)
            self.assertEqual(browser.head(grant['url']).status_code, 200)
        # Only this test's fixture enrollment is created/removed, never a live row.
        enrollment = Enrollment.objects.create(student=self.student, course=self.course)
        browser, grant = self.browser_grant(self.student)
        self.assertEqual(browser.head(grant['url']).status_code, 200)
        enrollment.delete()
        self.assertEqual(browser.head(grant['url']).status_code, 403)
        self.assertEqual(APIClient().get(grant['url']).status_code, 403)
        self.assertEqual(APIClient().get('/media/' + self.asset.file.name).status_code, 404)

    def test_uploaded_webvtt_is_protected_and_preserves_exact_cues(self):
        result = self.upload_file('sample.vtt', VTT, 'text/vtt')
        self.assertEqual(result.status_code, 201)
        self.assertEqual(result.data['after_section'], self.asset.after_section)
        response = self.client.post(result.data['playback_grant_url'])
        self.assertEqual(response.status_code, 200)
        browser = APIClient()
        browser.cookies = self.client.cookies
        delivered = browser.get(response.data['url'])
        self.assertEqual(delivered.status_code, 200)
        self.assertEqual(delivered['Content-Type'], 'text/vtt')
        self.assertEqual(self.body(delivered), VTT)
        self.assertEqual(APIClient().get(response.data['url']).status_code, 403)

    def test_revoked_cookie_replay_and_replacement_grant(self):
        browser, old = self.browser_grant()
        replacement_browser, replacement = self.browser_grant()
        self.assertEqual(browser.delete(self.grant_url, {'revoke_token': old['revoke_token']}, format='json').status_code, 204)
        self.assertEqual(browser.head(old['url']).status_code, 403)
        self.assertEqual(replacement_browser.head(replacement['url']).status_code, 200)
        self.assertEqual(APIClient().delete(self.grant_url, {'revoke_token': 'forged'}, format='json').status_code, 403)

    def test_server_expiry_and_account_deactivation_deny_playback(self):
        browser, grant = self.browser_grant()
        LessonPlaybackGrant.objects.filter(attachment=self.asset).update(expires_at=timezone.now()-timedelta(seconds=1))
        self.assertEqual(browser.head(grant['url']).status_code, 403)
        browser, grant = self.browser_grant()
        self.owner.is_active = False
        self.owner.save(update_fields=['is_active'])
        self.assertEqual(browser.head(grant['url']).status_code, 403)
