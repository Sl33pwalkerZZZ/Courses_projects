"""Isolated playback fixtures, no real course/media access."""
from pathlib import Path
from unittest.mock import patch
from django.core.exceptions import ValidationError
from django.test import SimpleTestCase, TestCase, override_settings
from rest_framework.test import APIClient
from courses import test_attachments as fixture_helpers
from courses.models import LessonAttachment
from courses.attachments import validate_file
from courses.video_validation import validate_video
from progress.models import Enrollment

class VideoValidationTests(SimpleTestCase):
    def test_signature_and_missing_validator_fail_closed(self):
        with self.assertRaises(ValidationError):
            validate_file('wrong.mp4', b'not video')
        with patch('courses.video_validation.shutil.which', return_value=None), self.assertRaises(ValidationError):
            validate_video(b'\x00\x00\x00\x18ftypisom' + b'\x00'*12)
    @override_settings(LESSON_VIDEO_MAX_BYTES=10)
    def test_upload_limit(self):
        with self.assertRaises(ValidationError):
            validate_file('a.mp4', b'x'*11)
    def test_wrong_codec_rejected(self):
        import json
        from types import SimpleNamespace
        metadata={'streams':[{'codec_type':'video','codec_name':'hevc','pix_fmt':'yuv420p','width':320,'height':240}], 'format':{'duration':'1'}}
        with patch('courses.video_validation.shutil.which',return_value='/fake/ffprobe'), patch('courses.video_validation.subprocess.run',return_value=SimpleNamespace(stdout=json.dumps(metadata))), self.assertRaises(ValidationError):
            validate_video(b'\x00\x00\x00\x18ftypisom'+b'\x00'*12)
    def test_valid_mp4_profile(self):
        import json
        from types import SimpleNamespace
        metadata={'streams':[{'codec_type':'video','codec_name':'h264','profile':'High','level':40,'pix_fmt':'yuv420p','width':320,'height':240,'avg_frame_rate':'25/1'}], 'format':{'duration':'1'}}
        raw=b'\x00\x00\x00\x18ftypisom'+b'\x00'*12
        with patch('courses.video_validation.shutil.which',return_value='/fake/ffprobe'), patch('courses.video_validation.subprocess.run',return_value=SimpleNamespace(stdout=json.dumps(metadata))):
            self.assertEqual(validate_file('a.mp4',raw),('video','video/mp4'))
    def test_probe_timeout_and_malformed_metadata_fail_closed(self):
        import subprocess
        from types import SimpleNamespace
        raw=b'\x00\x00\x00\x18ftypisom'+b'\x00'*12
        with patch('courses.video_validation.shutil.which',return_value='/fake/ffprobe'):
            for failure in [subprocess.TimeoutExpired('ffprobe',20), SimpleNamespace(stdout='not json'), SimpleNamespace(stdout='{}')]:
                with self.subTest(failure=str(failure)):
                    kwargs={'side_effect':failure} if isinstance(failure,Exception) else {'return_value':failure}
                    with patch('courses.video_validation.subprocess.run',**kwargs), self.assertRaises(ValidationError):
                        validate_video(raw)
    def test_vtt(self):
        self.assertEqual(validate_file('a.vtt', b'WEBVTT\n\n00:00:00.000 --> 00:00:01.000\nExample\n'), ('vtt','text/vtt'))
        with self.assertRaises(ValidationError):
            validate_file('a.vtt', b'WEBVTT\n<script>bad</script>')

class VideoPlaybackTests(TestCase):
    def setUp(self):
        fixture_helpers.AttachmentAPITests.setUp(self)
        self.path=Path(self.temp.name)/'private/lessons/attachments/fixture/test.mp4'
        self.path.parent.mkdir(parents=True)
        self.path.write_bytes(b'0123456789')
        self.row=LessonAttachment.objects.create(lesson=self.lesson,kind='video',file='lessons/attachments/fixture/test.mp4',filename='test.mp4',mime_type='video/mp4',sha256='a'*64,label='Synthetic fixture',provenance='test')
        self.grant=f'/api/lesson-attachments/{self.row.pk}/playback-grant/'
        self.play=f'/api/lesson-attachments/{self.row.pk}/playback/'
    def authorize(self):
        self.client.force_authenticate(self.owner)
        self.assertEqual(self.client.post(self.grant).status_code,200)
        browser = APIClient()
        browser.cookies = self.client.cookies
        self.client = browser
    def test_ranges_and_head(self):
        self.authorize()
        for header, expected, data in [(None,200,b'0123456789'),('bytes=2-4',206,b'234'),('bytes=-3',206,b'789'),('bytes=8-',206,b'89')]:
            response=self.client.get(self.play, **({'HTTP_RANGE':header} if header else {}))
            self.assertEqual(response.status_code,expected)
            self.assertEqual(b''.join(response.streaming_content),data)
            self.assertEqual(int(response['Content-Length']),len(data))
        response=self.client.head(self.play,HTTP_RANGE='bytes=2-4')
        self.assertEqual(response.status_code,200)
        self.assertEqual(response['Content-Length'],'10')
        self.assertEqual(response.content,b'')
        for header in ['bytes=20-30','bytes=5-2','bytes=0-1,3-4','invalid','bytes=-0']:
            response=self.client.get(self.play,HTTP_RANGE=header)
            self.assertEqual(response.status_code,416)
            self.assertEqual(response['Content-Range'],'bytes */10')
    def test_no_grant_denied_permission_revoked(self):
        self.assertEqual(self.client.get(self.play).status_code,403)
        self.client.force_authenticate(self.student)
        self.assertEqual(self.client.post(self.grant).status_code,403)
        enrollment=Enrollment.objects.create(student=self.student,course=self.course)
        self.assertEqual(self.client.post(self.grant).status_code,200)
        browser = APIClient()
        browser.cookies = self.client.cookies
        self.client = browser
        enrollment.delete()
        self.assertEqual(self.client.get(self.play).status_code,403)
    def test_expiry_and_changed_password(self):
        self.authorize()
        with patch('courses.video.time.time',return_value=10**11):
            self.assertEqual(self.client.get(self.play).status_code,403)
        self.owner.set_password('changed-test-password'); self.owner.save()
        self.assertEqual(self.client.get(self.play).status_code,403)

    def test_unknown_and_path_traversal(self):
        self.assertEqual(self.client.get('/api/lesson-attachments/999999/playback/').status_code,404)
        self.authorize()
        self.row.file.name='lessons/attachments/../../outside.mp4'
        self.row.save(update_fields=['file'])
        self.assertEqual(self.client.get(self.play).status_code,404)

    def test_exact_revocation_without_authentication(self):
        self.client.force_authenticate(self.owner)
        first=self.client.post(self.grant).data['revoke_token']
        second=self.client.post(self.grant).data['revoke_token']
        browser=APIClient(); browser.cookies=self.client.cookies; self.client=browser
        self.assertEqual(self.client.delete(self.grant, {'revoke_token':first},format='json').status_code,204)
        self.assertEqual(self.client.get(self.play).status_code,200)
        self.assertEqual(self.client.delete(self.grant, {'revoke_token':second},format='json').status_code,204)
        self.assertEqual(self.client.get(self.play).status_code,403)

    def test_grant_bound_to_access_expiry(self):
        import time
        self.client.force_authenticate(self.owner, token={'exp':int(time.time())+45})
        response=self.client.post(self.grant)
        self.assertEqual(response.status_code,200)
        self.assertLessEqual(response.data['expires_in'],45)
        self.assertGreater(response.data['expires_in'],0)
    def test_stream_close(self):
        self.authorize()
        response=self.client.get(self.play,HTTP_RANGE='bytes=1-8')
        iterator=iter(response.streaming_content)
        self.assertEqual(next(iterator),b'12345678')
        response.close()
        self.assertTrue(response.closed)

    def test_missing_or_directory_media_is_404(self):
        self.authorize()
        self.path.unlink()
        self.assertEqual(self.client.get(self.play).status_code,404)
        self.path.mkdir()
        self.assertEqual(self.client.get(self.play).status_code,404)


class AsyncVideoStreamingTests(SimpleTestCase):
    async def test_async_stream_is_bounded_and_close_releases_file(self):
        import io
        from courses.video import async_file_chunks
        stream=io.BytesIO(b'a'*(200*1024))
        iterator=async_file_chunks(stream, 3, 150*1024)
        first=await anext(iterator)
        self.assertEqual(len(first),64*1024)
        await iterator.aclose()
        self.assertTrue(stream.closed)

    async def test_async_stream_exact_bounds(self):
        import io
        from courses.video import async_file_chunks
        stream=io.BytesIO(b'0123456789')
        data=b''.join([block async for block in async_file_chunks(stream,2,4)])
        self.assertEqual(data,b'2345')
        self.assertTrue(stream.closed)
