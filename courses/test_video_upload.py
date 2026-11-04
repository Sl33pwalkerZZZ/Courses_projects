"""Studio video integration using synthetic MP4 boxes and mocked codec inspection."""
import json
import struct
from copy import deepcopy
from types import SimpleNamespace
from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase, TestCase, override_settings
from django.core.exceptions import ValidationError

from .models import LessonAttachment, LessonImage
from . import test_attachments as fixtures
from .attachments import validate_file


def mp4_boxes():
    def box(kind, payload):
        return struct.pack('>I4s', len(payload) + 8, kind) + payload
    # Container/signature fixture only; no real video or production assets.
    return box(b'ftyp', b'isom\x00\x00\x02\x00isomavc1') + box(b'mdat', b'fixture')


PROFILE = {'streams': [
    {'codec_type': 'video', 'codec_name': 'h264', 'pix_fmt': 'yuv420p',
     'profile': 'Main', 'level': 31, 'avg_frame_rate': '25/1', 'width': 320, 'height': 240},
    {'codec_type': 'audio', 'codec_name': 'aac', 'profile': 'LC', 'channels': 1, 'sample_rate': '48000'},
], 'format': {'duration': '1.0'}}


class VideoProfileSafetyTests(SimpleTestCase):
    def test_unsupported_stream_profiles_and_metadata_are_rejected(self):
        mutations = [
            (0, 'profile', 'High 10'), (0, 'level', 60), (0, 'avg_frame_rate', '120/1'),
            (0, 'width', 100000), (0, 'pix_fmt', 'yuv444p'),
            (1, 'profile', 'HE-AAC'), (1, 'sample_rate', '8000'), (1, 'channels', 6),
        ]
        for stream, key, value in mutations:
            profile = deepcopy(PROFILE)
            profile['streams'][stream][key] = value
            with self.subTest(key=key, value=value), patch('courses.video_validation.shutil.which', return_value='/trusted/ffprobe'), patch('courses.video_validation.subprocess.run', return_value=SimpleNamespace(stdout=json.dumps(profile))), self.assertRaises(ValidationError):
                validate_file('test.mp4', mp4_boxes())

    def test_vtt_rejects_empty_cues_control_characters_and_bad_timing(self):
        for raw in [
            b'WEBVTT\n\n00:00:00.000 --> 00:00:01.000\n',
            b'WEBVTT\n\n00:00:00.000 --> 00:00:01.000\nText\x01',
            b'WEBVTT\n\n00:00:01.000 --> 00:00:00.000\nText',
            b'WEBVTT\n\n00:00:00.000 --> 00:00:02.000\nOne\n\n00:00:01.000 --> 00:00:03.000\nTwo',
        ]:
            with self.subTest(raw=raw), self.assertRaises(ValidationError):
                validate_file('test.vtt', raw)


class StudioVideoUploadTests(TestCase):
    def setUp(self):
        fixtures.AttachmentAPITests.setUp(self)
        self.client.force_authenticate(self.owner)
        self.probe = patch('courses.video_validation.subprocess.run',
                           return_value=SimpleNamespace(stdout=json.dumps(PROFILE)))
        self.probe.start()
        self.addCleanup(self.probe.stop)
        self.binary = patch('courses.video_validation.shutil.which', return_value='/trusted/ffprobe')
        self.binary.start()
        self.addCleanup(self.binary.stop)

    def upload_video(self, **changes):
        payload = dict(file=SimpleUploadedFile('fixture.mp4', mp4_boxes(), content_type='video/mp4'),
                       label='Instructional video', caption='Synthetic integration fixture',
                       transcript='Accessible text equivalent.', provenance='Original test fixture',
                       after_section='Section')
        payload.update(changes)
        return self.client.post(self.upload, payload, format='multipart')

    def test_video_upload_and_idempotent_repeat(self):
        first = self.upload_video()
        self.assertEqual(first.status_code, 201, first.data)
        self.assertEqual(first.data['kind'], 'video')
        self.assertEqual(first.data['mime_type'], 'video/mp4')
        self.assertNotIn('/media/', first.data['url'])
        second = self.upload_video()
        self.assertEqual(second.status_code, 200, second.data)
        self.assertEqual(second.data['id'], first.data['id'])
        self.assertEqual(LessonAttachment.objects.count(), 1)

    def test_video_requires_transcript_and_honest_mime(self):
        for changes in [dict(transcript=''), dict(file=SimpleUploadedFile('fake.mp4', mp4_boxes(), content_type='text/html'))]:
            self.assertEqual(self.upload_video(**changes).status_code, 400)
        self.assertEqual(LessonAttachment.objects.count(), 0)

    @override_settings(LESSON_VIDEO_MAX_BYTES=16)
    def test_configured_limit_applies_to_studio_upload(self):
        self.assertEqual(self.upload_video().status_code, 400)
        self.assertEqual(LessonAttachment.objects.count(), 0)

    def test_owner_boundary_and_published_lock_still_apply(self):
        for user, status in [(self.other, 404), (self.student, 403)]:
            self.client.force_authenticate(user)
            self.assertEqual(self.upload_video().status_code, status)
        self.client.force_authenticate(self.owner)
        self.course.is_published = True
        self.course.save(update_fields=['is_published'])
        self.assertEqual(self.upload_video().status_code, 400)

    def test_poster_must_belong_to_same_lesson_and_anchor(self):
        image = LessonImage.objects.create(lesson=self.lesson, image='lessons/fixture.png')
        content = self.lesson.learning_content
        content.interactions = [{'type': 'image_placement', 'image_id': image.pk, 'after_section': 'Section'}]
        content.save(update_fields=['interactions'])
        result = self.upload_video()
        self.assertEqual(result.status_code, 201, result.data)
        self.assertEqual(result.data['poster_image_id'], image.pk)

    def test_vtt_upload_and_protected_native_delivery(self):
        raw = b'WEBVTT\n\n00:00:00.000 --> 00:00:01.000\nAccessible example\n'
        result = self.upload_video(file=SimpleUploadedFile('fixture.vtt', raw, content_type='text/vtt'), transcript='')
        self.assertEqual(result.status_code, 201, result.data)
        self.assertEqual(result.data['kind'], 'vtt')
        grant = self.client.post(result.data['playback_grant_url'])
        self.assertEqual(grant.status_code, 200)
        response = self.client.get(grant.data['url'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/vtt')
        self.assertEqual(b''.join(response.streaming_content), raw)
        response.close()
