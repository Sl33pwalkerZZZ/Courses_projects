import io
import tempfile
import wave
from pathlib import Path
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, SimpleTestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from courses.attachments import validate_file, validate_mp3, validate_srt
from courses.models import Course, CourseImport, Direction, Lesson, LessonAttachment, LessonLearningContent, Module
from progress.models import Enrollment, EnrollmentRequest
from studio.services import fingerprint


def wav_bytes():
    out=io.BytesIO()
    with wave.open(out,'wb') as audio:
        audio.setnchannels(1);audio.setsampwidth(2);audio.setframerate(8000)
        audio.writeframes(b'\x00\x00'*800)
    return out.getvalue()


SRT=b'1\n00:00:00,000 --> 00:00:01,000\nFixture subtitles\n'


class AttachmentValidationTests(SimpleTestCase):
    def test_wav_srt_and_complete_mp3_headers(self):
        self.assertEqual(validate_file('sample.wav',wav_bytes()),('audio','audio/wav'))
        self.assertEqual(validate_file('sample.srt',SRT),('srt','application/x-subrip'))
        # Structural MP3 frame fixture, not real narration or published audio.
        frames=(b'\xff\xfb\x90\x00'+b'\x00'*413)*2
        self.assertEqual(validate_file('fixture.mp3',frames),('audio','audio/mpeg'))

    def test_fakes_oversize_unsafe_and_unsupported_rejected(self):
        for name,data in [('fake.mp3',b'ID3not audio'),('fake.wav',b'RIFFnot audio'),('bad.wav',wav_bytes()[:-40]),('a.srt',b'<html>bad</html>'),('a.srt',b'\xff'),('../a.srt',SRT),('a.html',SRT),('a.srt',b'x'*(1024*1024+1)),('a.mp3',b'\xff\xfb\x90\x00')]:
            with self.subTest(name=name),self.assertRaises(ValidationError): validate_file(name,data)

    def test_srt_structure_and_positive_ordered_timing(self):
        for data in [SRT.replace(b'01,000',b'00,000'),SRT.replace(b'00:00:00',b'00:70:00'),SRT+b'\n2\n00:00:00,500 --> 00:00:02,000\noverlap',SRT+b'\x00']:
            with self.assertRaises(ValidationError):validate_srt(data)


class AttachmentAPITests(TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.override=override_settings(MEDIA_ROOT=Path(self.temp.name)/'private',PUBLIC_MEDIA_ROOT=Path(self.temp.name)/'public',DEBUG=True)
        self.override.enable();self.addCleanup(self.override.disable)
        User=get_user_model()
        self.owner=User.objects.create_user(username='fixture-owner',role='author')
        self.student=User.objects.create_user(username='fixture-student')
        self.other=User.objects.create_user(username='fixture-other-author',role='author')
        self.admin=User.objects.create_user(username='fixture-admin',role='admin')
        direction=Direction.objects.create(name='Fixture',slug='fixture')
        self.course=Course.objects.create(title='Draft fixture',slug='fixture-course',author=self.owner,direction=direction)
        self.module=Module.objects.create(course=self.course,title='Fixture',order=1)
        self.lesson=Lesson.objects.create(module=self.module,title='Fixture lesson',order=1,text_content='Section\n\nFixture theory')
        LessonLearningContent.objects.create(lesson=self.lesson,source_sections=['Section'])
        self.client=APIClient()
        self.upload=f'/api/studio/lessons/{self.lesson.pk}/attachments/'

    def post(self,kind='wav',**changes):
        raw=SRT if kind=='srt' else wav_bytes()
        payload=dict(file=SimpleUploadedFile(f'fixture.{kind}',raw),label='Fixture audio',caption='Fixture caption',transcript='Fixture spoken text',provenance='Isolated test fixture',after_section='Section')
        payload.update(changes)
        return self.client.post(self.upload,payload,format='multipart')

    def create_asset(self,kind='wav'):
        self.client.force_authenticate(self.owner)
        result=self.post(kind)
        self.assertEqual(result.status_code,201,result.data)
        return LessonAttachment.objects.get(pk=result.data['id'])

    def test_owner_admin_preview_and_enrolled_student_access_metadata_and_files(self):
        asset=self.create_asset()
        url=reverse('lesson-attachment',args=[asset.pk])
        Enrollment.objects.create(student=self.student,course=self.course)
        for user in [self.owner,self.admin,self.student]:
            self.client.force_authenticate(user)
            metadata=self.client.get(reverse('lesson-detail',args=[self.lesson.pk]))
            self.assertEqual(metadata.status_code,200)
            self.assertEqual(metadata.data['attachments'][0]['id'],asset.pk)
            self.assertNotIn('file',metadata.data['attachments'][0])
            response=self.client.get(url)
            self.assertEqual(response.status_code,200)
            self.assertEqual(response['Content-Type'],'audio/wav')
            self.assertEqual(response['Cache-Control'],'private, no-store')
            self.assertEqual(response['X-Content-Type-Options'],'nosniff')
            response.close()

    def test_anonymous_pending_rejected_and_other_author_denied(self):
        asset=self.create_asset()
        url=reverse('lesson-attachment',args=[asset.pk])
        self.client.force_authenticate(None)
        self.assertEqual(self.client.get(url).status_code,401)
        for status in ['pending','rejected']:
            request=EnrollmentRequest.objects.create(student=self.student,course=self.course,message='Fixture application message long enough',status=status,reviewed_at=timezone.now() if status=='rejected' else None)
            self.client.force_authenticate(self.student)
            self.assertEqual(self.client.get(url).status_code,403)
            self.assertEqual(self.client.get(reverse('lesson-detail',args=[self.lesson.pk])).status_code,403)
            request.delete()
        self.client.force_authenticate(self.other)
        self.assertEqual(self.client.get(url).status_code,403)
        self.assertEqual(self.client.get(self.upload).status_code,404)
        self.assertEqual(self.post().status_code,404)
        self.client.force_authenticate(self.student)
        self.assertEqual(self.post().status_code,403)

    def test_srt_is_download_and_legacy_paths_never_bypass_access(self):
        asset=self.create_asset('srt')
        response=self.client.get(reverse('lesson-attachment',args=[asset.pk]))
        self.assertTrue(response['Content-Disposition'].startswith('attachment;'))
        self.assertEqual(response['Content-Type'],'application/x-subrip')
        response.close()
        self.assertEqual(self.client.get('/media/'+asset.file.name).status_code,404)
        self.assertEqual(self.client.get('/api/private-media/'+asset.file.name).status_code,404)
        self.assertEqual(self.client.get('/api/lesson-attachments/999999/').status_code,404)
        asset.file.name='lessons/attachments/../../unrelated.wav';asset.save()
        self.assertEqual(self.client.get(reverse('lesson-attachment',args=[asset.pk])).status_code,404)

    def test_upload_metadata_validation_and_published_lock(self):
        self.client.force_authenticate(self.owner)
        for fields in [dict(transcript=''),dict(after_section='Missing'),dict(provenance=''),dict(file=SimpleUploadedFile('fake.wav',b'not audio'))]:
            self.assertEqual(self.post(**fields).status_code,400)
        self.assertEqual(LessonAttachment.objects.count(),0)
        self.course.is_published=True;self.course.save()
        self.assertEqual(self.post().status_code,400)

    def test_duplicate_upload_no_extra_file_and_preserves_editorial_approval(self):
        asset=self.create_asset()
        receipt=CourseImport.objects.create(course=self.course,source_name='fixture',source_sha256='a'*64,manifest_sha256='b'*64,content_sha256='c'*64,version='fixture',review_approved=True)
        self.assertEqual(self.post().status_code,200)
        receipt.refresh_from_db();self.assertTrue(receipt.review_approved)
        self.assertEqual(self.post(label='Conflicting label').status_code,400)
        self.assertEqual(LessonAttachment.objects.count(),1)
        self.assertEqual(len(list((Path(self.temp.name)/'private').rglob('*.wav'))),1)

    def test_failed_upload_rolls_back_and_removes_new_file(self):
        self.client.force_authenticate(self.owner)
        with patch('courses.attachments.LessonAttachment.save',side_effect=RuntimeError('fixture failure')):
            with self.assertRaises(RuntimeError):self.post()
        self.assertEqual(LessonAttachment.objects.count(),0)
        self.assertFalse(list((Path(self.temp.name)/'private').rglob('*.wav')))

    def test_attachments_invalidate_publication_fingerprint(self):
        before=fingerprint(self.course)
        with patch('courses.attachments.attachments_ready',return_value=False):
            self.assertEqual(before,fingerprint(self.course))
        self.create_asset()
        self.assertNotEqual(before,fingerprint(self.course))

    def test_pre_migration_compatibility(self):
        with patch('courses.attachments.attachments_ready',return_value=False):
            self.client.force_authenticate(self.owner)
            response=self.client.get(reverse('lesson-detail',args=[self.lesson.pk]))
            self.assertEqual(response.status_code,200)
            self.assertEqual(response.data['attachments'],[])
            self.assertEqual(self.post().status_code,503)
            self.assertEqual(self.client.get('/api/lesson-attachments/1/').status_code,503)
