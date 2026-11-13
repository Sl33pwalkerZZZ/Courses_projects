"""Isolated integration fixtures; never use local course/media/database records."""
import copy
import hashlib
import io
import json
import sqlite3
import tempfile
import tarfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase, override_settings
from django.utils import timezone
from rest_framework.test import APIClient

from courses.management.commands import integrate_lesson113_videos as command
from courses.models import Course, Direction, Lesson, LessonAttachment, LessonLearningContent, Module
from progress.models import EnrollmentRequest


class Lesson113IntegrationTests(TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.override = override_settings(BASE_DIR=self.root, MEDIA_ROOT=self.root/'private')
        self.override.enable(); self.addCleanup(self.override.disable)
        self.plan = copy.deepcopy(command.load_plan())
        self.owner = get_user_model().objects.create_user(username='isolated-owner', role='author')
        self.student = get_user_model().objects.create_user(username='isolated-student')
        direction = Direction.objects.create(name='Fixture', slug='fixture')
        self.course = Course.objects.create(pk=10, slug='ai-media-content', title='Fixture course', author=self.owner, direction=direction)
        for order in range(1, 5):
            module = Module.objects.create(pk=order, course=self.course, title=f'Preserved{order}', order=order)
            for n in range(1, 4):
                Lesson.objects.create(module=module, title=f'Preserved{order}/{n}', order=n, text_content='Untouched')
        module = Module.objects.create(pk=39, course=self.course, title='Module5', order=5)
        self.lesson = Lesson.objects.create(pk=113, module=module, title=self.plan['expected_before']['title'], order=1, text_content=self.plan['change']['before'])
        for pk, order in [(114, 2), (115, 3)]:
            Lesson.objects.create(pk=pk, module=module, title=f'Untouched{pk}', order=order, text_content='Untouched')
        expected = self.plan['expected_before']
        LessonLearningContent.objects.create(pk=20, lesson=self.lesson, objectives=expected['objectives'], source_sections=expected['source_sections'], interactions=[], content_language='ru')
        self.raws = []
        for n, asset in enumerate(self.plan['assets']):
            raw = b'isolated-mp4-fixture-' + str(n).encode(); self.raws.append(raw)
            asset['sha256'] = hashlib.sha256(raw).hexdigest()
            path = self.root/asset['path']; path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(raw)
        self.storage = self.root/'private'; self.storage.mkdir()
        self.preserved = self.storage/'preserved.txt'; self.preserved.write_bytes(b'preserve me')
        for name in ['courses.attachments.validate_file', 'courses.management.commands.integrate_lesson113_videos.validate_file']:
            patcher = patch(name, return_value=('video','video/mp4')); patcher.start(); self.addCleanup(patcher.stop)
        self.loader = patch.object(command, 'load_plan', return_value=self.plan); self.loader.start(); self.addCleanup(self.loader.stop)

    def run_command(self, *args):
        output = io.StringIO(); call_command('integrate_lesson113_videos', *args, stdout=output); return output.getvalue()

    def assert_untouched(self):
        self.assertFalse(Course.objects.get(pk=10).is_published)
        self.assertEqual(Module.objects.filter(course=self.course).count(),5)
        self.assertEqual(Lesson.objects.count(),15)
        self.assertEqual(Lesson.objects.exclude(pk=113).exclude(text_content='Untouched').count(),0)
        self.assertEqual(self.preserved.read_bytes(),b'preserve me')
        self.assertEqual(self.lesson.learning_content.objectives,self.plan['expected_before']['objectives'])

    @patch.object(command, 'verified_backup', return_value=Path('/isolated-backup'))
    def test_creation_and_noop_repeat(self, backup):
        self.assertIn('Dry-run',self.run_command()); backup.assert_not_called()
        self.assertFalse(self.lesson.attachments.exists())
        self.run_command('--apply'); rows=list(self.lesson.attachments.all())
        self.assertEqual([r.order for r in rows],[1,2,3])
        self.assertEqual([r.after_section for r in rows],[a['metadata']['after_section'] for a in self.plan['assets']])
        self.lesson.refresh_from_db(); self.assertEqual(self.lesson.text_content,self.plan['change']['after'])
        self.assertIn('no-op',self.run_command('--apply')); self.assertEqual(backup.call_count,1)
        self.assertEqual(self.lesson.attachments.count(),3); self.assert_untouched()

    def test_unexpected_text_or_attachment_rejected(self):
        Lesson.objects.filter(pk=113).update(text_content='unexpected')
        with self.assertRaises(CommandError):self.run_command('--apply')
        Lesson.objects.filter(pk=113).update(text_content=self.plan['change']['before'])
        LessonAttachment.objects.create(lesson=self.lesson,filename='other.mp4',file='unrelated',sha256='a'*64)
        with self.assertRaises(CommandError):self.run_command('--apply')
        self.assert_untouched()

    def test_missing_or_corrupt_asset_stops_before_backup(self):
        path=self.root/self.plan['assets'][0]['path'];path.write_bytes(b'changed')
        with patch.object(command,'verified_backup') as backup,self.assertRaises(CommandError):self.run_command('--apply')
        backup.assert_not_called();self.assertFalse(self.lesson.attachments.exists())
        path.unlink()
        with self.assertRaises(CommandError):self.run_command('--apply')

    @patch.object(command, 'verified_backup', return_value=Path('/isolated-backup'))
    def test_failure_after_second_file_rolls_back_text_rows_files(self, backup):
        original=command.store_attachment;calls=[]
        def fail(*args,**kwargs):
            result=original(*args,**kwargs);calls.append(result)
            if len(calls)==2:raise RuntimeError('isolated injected failure')
            return result
        with patch.object(command,'store_attachment',side_effect=fail),self.assertRaises(RuntimeError):self.run_command('--apply')
        self.lesson.refresh_from_db();self.assertEqual(self.lesson.text_content,self.plan['change']['before'])
        self.assertFalse(self.lesson.attachments.exists());self.assertEqual([p for p in self.storage.rglob('*') if p.is_file()],[self.preserved]);self.assert_untouched()

    def test_backup_failure_prevents_changes(self):
        with patch.object(command,'verified_backup',side_effect=CommandError('isolated backup failure')),self.assertRaises(CommandError):self.run_command('--apply')
        self.lesson.refresh_from_db();self.assertEqual(self.lesson.text_content,self.plan['change']['before']);self.assertFalse(self.lesson.attachments.exists())

    def test_invalid_anchor_or_publication_rejected(self):
        self.plan['assets'][0]['metadata']['after_section']='missing section'
        with self.assertRaises(CommandError):self.run_command('--apply')
        self.course.is_published=True;self.course.save()
        with self.assertRaises(CommandError):self.run_command('--apply')

    @patch.object(command, 'verified_backup', return_value=Path('/isolated-backup'))
    def test_completed_metadata_or_order_conflict_refused(self, backup):
        self.run_command('--apply');row=self.lesson.attachments.first();row.caption='changed';row.save()
        with self.assertRaises(CommandError):self.run_command('--apply')
        row.caption=self.plan['assets'][0]['metadata']['caption'];row.order=4;row.save()
        with self.assertRaises(CommandError):self.run_command('--apply')

    def test_actual_verified_backup_copies_protected_and_source_files(self):
        db=self.root/'fixture.sqlite3'
        with sqlite3.connect(db) as c:c.execute('CREATE TABLE courses_course(id INTEGER PRIMARY KEY)')
        assets=command.prevalidate(self.plan,self.lesson);self.lesson.refresh_from_db()
        with patch.object(command,'database_health'),patch.object(command,'connection',SimpleNamespace(settings_dict={'NAME':str(db)})):
            folder=command.verified_backup(self.root/'backup',self.lesson,assets)
        snapshot=json.loads((folder/'before-state.json').read_text())
        self.assertEqual(snapshot['lesson']['text_content'],self.plan['change']['before'])
        with tarfile.open(folder/'protected-media-and-approved-sources.tar') as tar:
            self.assertEqual(len(tar.getnames()),4)
            self.assertEqual(tar.extractfile('protected-media/preserved.txt').read(),b'preserve me')
        self.assertTrue(snapshot['verified_integrity_and_foreign_keys'])

    @patch.object(command, 'verified_backup', return_value=Path('/isolated-backup'))
    def test_integrated_files_use_existing_protected_access(self, backup):
        self.run_command('--apply');row=self.lesson.attachments.first();grant=f'/api/lesson-attachments/{row.pk}/playback-grant/';play=f'/api/lesson-attachments/{row.pk}/playback/'
        client=APIClient();self.assertIn(client.post(grant).status_code,[401,403]);self.assertIn(client.get(play).status_code,[401,403])
        for status in ['pending','rejected']:
            EnrollmentRequest.objects.create(student=self.student,course=self.course,status=status, message='Isolated enrollment motivation for permissions test', reviewed_at=timezone.now() if status=='rejected' else None, reviewed_by=self.owner if status=='rejected' else None)
            client.force_authenticate(self.student);self.assertEqual(client.post(grant).status_code,403)
            EnrollmentRequest.objects.all().delete()
        client.force_authenticate(self.owner);self.assertEqual(client.post(grant).status_code,200)
        browser=APIClient();browser.cookies=client.cookies
        response=browser.get(play,HTTP_RANGE='bytes=0-4');self.assertEqual(response.status_code,206);self.assertEqual(b''.join(response.streaming_content),self.raws[0][:5])
        response=browser.head(play);self.assertEqual(response.status_code,200);self.assertEqual(int(response['Content-Length']),len(self.raws[0]))

    @patch.object(command, 'verified_backup', return_value=Path('/isolated-backup'))
    def test_available_approved_mp4s_through_isolated_protected_playback(self, backup):
        from courses.video_validation import validate_video
        from courses.models import LessonPlaybackGrant
        real_root = Path(__file__).resolve().parents[1]
        sources = [real_root/a['path'] for a in self.plan['assets']]
        if not all(p.is_file() for p in sources):
            self.skipTest('Optional local approved-export verification; source MP4s unavailable.')
        for source, asset in zip(sources, self.plan['assets']):
            raw=source.read_bytes(); validate_video(raw)
            asset['sha256']=hashlib.sha256(raw).hexdigest()
            (self.root/asset['path']).write_bytes(raw)
        self.run_command('--apply')
        for row, asset in zip(self.lesson.attachments.all(), self.plan['assets']):
            client=APIClient();client.force_authenticate(self.owner)
            grant=f'/api/lesson-attachments/{row.pk}/playback-grant/'
            play=f'/api/lesson-attachments/{row.pk}/playback/'
            self.assertEqual(client.post(grant).status_code,200)
            browser=APIClient();browser.cookies=client.cookies
            response=browser.get(play);self.assertEqual(response.status_code,200)
            self.assertEqual(hashlib.sha256(b''.join(response.streaming_content)).hexdigest(),asset['sha256'])
            response=browser.head(play);self.assertEqual(response.status_code,200)
            size=int(response['Content-Length'])
            for value, length in [('bytes=0-1023',1024),('bytes=-512',512)]:
                response=browser.get(play,HTTP_RANGE=value);self.assertEqual(response.status_code,206)
                self.assertEqual(len(b''.join(response.streaming_content)),length)
                self.assertEqual(response['Accept-Ranges'],'bytes')
            self.assertEqual(browser.get(play,HTTP_RANGE=f'bytes={size}-').status_code,416)
            LessonPlaybackGrant.objects.filter(attachment=row).update(expires_at=timezone.now()-timezone.timedelta(seconds=1))
            self.assertEqual(browser.get(play).status_code,403)
            self.assertEqual(client.post(grant).status_code,200);browser.cookies=client.cookies
            LessonPlaybackGrant.objects.filter(attachment=row).update(revoked_at=timezone.now())
            self.assertEqual(browser.get(play).status_code,403)
        self.assert_untouched()
