"""Lesson 115 integration tests use an isolated Django test database and media root."""
import copy
import hashlib
import io
import tempfile
from pathlib import Path
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase, override_settings

from courses.management.commands import integrate_lesson115_videos as command
from courses.models import Course, Direction, Lesson, LessonAttachment, LessonLearningContent, Module


class Lesson115VideoIntegrationTests(TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.media_root = self.root / 'private-media'
        self.media_root.mkdir()
        self.settings = override_settings(MEDIA_ROOT=self.media_root)
        self.settings.enable()
        self.addCleanup(self.settings.disable)
        self.plan = copy.deepcopy(command.load_plan())
        self.owner = get_user_model().objects.create_user(username='isolated-l15-author', role='author')
        direction = Direction.objects.create(name='Fixture', slug='lesson115-fixture')
        expected = self.plan['expected']
        self.course = Course.objects.create(pk=10, slug=expected['course']['slug'], title=expected['course']['title'],
            author=self.owner, direction=direction, is_published=False)
        for order in range(1, 5):
            module = Module.objects.create(pk=30 + order, course=self.course, title=f'Preserved module {order}', order=order)
            for lesson_order in range(1, 4):
                Lesson.objects.create(pk=100 + (order - 1) * 3 + lesson_order, module=module,
                    title=f'Preserved lesson {order}/{lesson_order}', order=lesson_order, text_content='Unchanged fixture.')
        self.module = Module.objects.create(pk=39, course=self.course, title=expected['module']['title'], order=5)
        for lesson_id in (113, 114):
            Lesson.objects.create(pk=lesson_id, module=self.module, title=f'Preserved {lesson_id}', order=lesson_id - 112,
                text_content='Unchanged fixture.')
        self.lesson_text = '\n\n'.join(expected['learning_content']['source_sections'])
        self.lesson = Lesson.objects.create(pk=115, module=self.module, title=expected['lesson']['title'], order=3,
            text_content=self.lesson_text)
        expected['lesson']['text_sha256'] = hashlib.sha256(self.lesson_text.encode()).hexdigest()
        LessonLearningContent.objects.create(pk=22, lesson=self.lesson, content_language='ru',
            objectives=expected['learning_content']['objectives'], source_sections=expected['learning_content']['source_sections'],
            interactions=[])
        self.loader = patch.object(command, 'load_plan', return_value=self.plan)
        self.loader.start()
        self.addCleanup(self.loader.stop)
        self.output = io.StringIO()

    def run_import(self, *args):
        self.output = io.StringIO()
        call_command('integrate_lesson115_videos', *args, stdout=self.output)
        return self.output.getvalue()

    def test_dry_run_plans_exactly_six_without_mutations(self):
        result = self.run_import('--dry-run', '--backup-dir', str(self.root / 'backups'))
        self.assertEqual(result.count('CREATE '), 6)
        self.assertIn('Dry-run: six creates only', result)
        self.assertEqual(self.lesson.attachments.count(), 0)
        self.assertFalse((self.root / 'backups').exists())
        self.assertFalse(Course.objects.get(pk=10).is_published)
        self.assertEqual(self.lesson.text_content, self.lesson_text)

    @patch.object(command, 'verified_backup')
    def test_verified_backup_only_does_not_create_records(self, backup):
        old_asset = self.media_root / 'existing-private.txt'
        old_asset.write_bytes(b'protected existing file')
        backup.return_value = self.root / 'verified-backup'
        result = self.run_import('--backup-only', '--backup-dir', str(self.root / 'backups'))
        self.assertIn('Verified preflight backup:', result)
        backup.assert_called_once()
        self.assertEqual(self.lesson.attachments.count(), 0)

    @patch.object(command, 'verified_backup')
    def test_apply_creates_three_video_vtt_pairs_and_is_idempotent(self, backup):
        old_asset = self.media_root / 'existing-private.txt'
        old_asset.write_bytes(b'preserve this existing media')
        backup.return_value = self.root / 'verified-backup'
        old_row = LessonAttachment.objects.create(lesson_id=113, kind='video', filename='preserved.mp4',
            file='existing-private.txt', mime_type='video/mp4', sha256=hashlib.sha256(old_asset.read_bytes()).hexdigest(),
            label='Preserved fixture', provenance='isolated test fixture', order=1)
        result = self.run_import('--apply', '--backup-dir', str(self.root / 'backups'))
        self.assertIn('Integrated exactly six Lesson 15 attachments', result)
        rows = list(self.lesson.attachments.order_by('order'))
        self.assertEqual(len(rows), 6)
        self.assertEqual([row.kind for row in rows], ['video', 'vtt', 'video', 'vtt', 'video', 'vtt'])
        self.assertEqual([row.after_section for row in rows], [
            self.plan['placement_sections'][0], self.plan['placement_sections'][0],
            self.plan['placement_sections'][1], self.plan['placement_sections'][1],
            self.plan['placement_sections'][2], self.plan['placement_sections'][2],
        ])
        self.assertEqual(LessonAttachment.objects.filter(pk=old_row.pk).count(), 1)
        self.assertEqual(old_asset.read_bytes(), b'preserve this existing media')
        self.assertEqual(self.lesson.text_content, self.lesson_text)
        self.assertEqual(self.lesson.learning_content.source_sections, self.plan['expected']['learning_content']['source_sections'])
        self.assertFalse(Course.objects.get(pk=10).is_published)
        backup.assert_called_once()
        replay = self.run_import('--apply', '--backup-dir', str(self.root / 'backups'))
        self.assertIn('KEEP 6', replay)
        self.assertEqual(self.lesson.attachments.count(), 6)

    def test_changed_lesson_or_partial_attachment_set_stops(self):
        Lesson.objects.filter(pk=115).update(text_content='unexpected change')
        with self.assertRaises(CommandError):
            self.run_import('--dry-run', '--backup-dir', str(self.root / 'backups'))
        Lesson.objects.filter(pk=115).update(text_content=self.lesson_text)
        LessonAttachment.objects.create(lesson=self.lesson, kind='vtt', filename='unexpected.vtt', file='missing.vtt',
            mime_type='text/vtt', sha256='f' * 64, label='Unexpected', provenance='fixture', order=1)
        with self.assertRaises(CommandError):
            self.run_import('--dry-run', '--backup-dir', str(self.root / 'backups'))
        self.assertEqual(self.lesson.attachments.count(), 1)
