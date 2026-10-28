import io
import json
import tempfile
from pathlib import Path
from unittest.mock import patch

from PIL import Image
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework.test import APIClient

from courses.management.commands.import_first_course import curriculum_snapshot
from courses.management.commands.import_media_module_3_images import MODULE_TITLE, PREFIX
from courses.models import Course, Direction, Lesson, LessonImage, Module
from studio.models import LessonImageDescription


class Module3ImageTests(TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.private = self.root / 'private'
        self.override = override_settings(MEDIA_ROOT=self.private)
        self.override.enable()
        self.addCleanup(self.override.disable)
        self.assets = self.root / 'assets'
        self.assets.mkdir()
        self.manifest = self.root / 'manifest.json'
        data = json.loads((Path(settings.BASE_DIR) / 'docs/courses/media-module-3-assets.json').read_text())
        self.manifest.write_text(json.dumps(data))
        self.entries = data['assets']
        for entry in self.entries:
            Image.new('RGB', (32, 24), 'purple').save(self.assets / entry['filename'])
        self.author = get_user_model().objects.create_user(username='fixture-owner', role='author')
        direction = Direction.objects.create(name='Fixture', slug='fixture')
        self.course = Course.objects.create(title='Fixture', slug='ai-media-content', author=self.author, direction=direction)
        self.module = Module.objects.create(course=self.course, order=3, title=MODULE_TITLE)
        self.lessons = [Lesson.objects.create(module=self.module, order=i, title=next(e['lesson_title'] for e in self.entries if e['lesson_order']==i), text_content=f'Preserve {i}') for i in (1, 2, 3)]
        previous = Module.objects.create(course=self.course, title='Previous', order=1)
        Lesson.objects.create(module=previous, order=1, title='Old lesson', text_content='Untouched')
        self.before = curriculum_snapshot(self.course)
        self.backup_patch = patch('courses.management.commands.import_media_module_3_images.create_backup', return_value=Path('/isolated-backup'))
        self.backup = self.backup_patch.start()
        self.addCleanup(self.backup_patch.stop)

    def run_import(self, *args):
        output = io.StringIO()
        call_command('import_media_module_3_images', '--assets-dir', str(self.assets), '--manifest', str(self.manifest), *args, stdout=output)
        return output.getvalue()

    def test_default_dry_run_no_database_storage_or_backup_writes(self):
        self.assertIn('"create": 6', self.run_import())
        self.assertFalse(self.private.exists())
        self.assertEqual(LessonImage.objects.count(), 0)
        self.backup.assert_not_called()
        self.assertEqual(curriculum_snapshot(self.course), self.before)

    def test_creation_metadata_filenames_idempotency_and_source_preservation(self):
        source_bytes = {p.name: p.read_bytes() for p in self.assets.iterdir()}
        self.run_import('--apply')
        self.assertEqual(LessonImage.objects.count(), 6)
        self.assertEqual(LessonImageDescription.objects.count(), 6)
        for lesson in self.lessons:
            self.assertEqual(list(lesson.images.values_list('order', flat=True)), [1, 2])
        for entry in self.entries:
            row = LessonImage.objects.get(image=PREFIX+entry['filename'])
            self.assertEqual(row.lesson_id, self.lessons[entry['lesson_order']-1].pk)
            self.assertEqual(row.studio_description.alt_text, entry['alt_text'])
            with Image.open(row.image.path) as stored:
                self.assertEqual(stored.info['Description'], entry['caption_ru'])
        self.assertIn('"unchanged": 6', self.run_import('--apply'))
        self.assertEqual(LessonImage.objects.count(), 6)
        self.assertEqual(self.backup.call_count, 1)
        self.assertEqual(source_bytes, {p.name: p.read_bytes() for p in self.assets.iterdir()})
        after = curriculum_snapshot(self.course)
        for module in after['modules']:
            for lesson in module['lessons']:
                lesson['images'] = []
        self.assertEqual(after, self.before)

    def test_conflicting_alt_or_file_bytes_rejected(self):
        self.run_import('--apply')
        description = LessonImageDescription.objects.first()
        description.alt_text = {'ru': 'Teacher edit'}
        description.save()
        with self.assertRaises(CommandError):
            self.run_import('--apply')
        self.assertEqual(self.backup.call_count, 1)

    def test_missing_or_non_png_file_rejected_before_writes(self):
        path = self.assets / self.entries[0]['filename']
        path.unlink()
        with self.assertRaises(CommandError):
            self.run_import()
        Image.new('RGB', (10, 10)).save(path, format='JPEG')
        with self.assertRaises(CommandError):
            self.run_import()
        self.backup.assert_not_called()

    def test_unregistered_file_conflict_is_preserved(self):
        path = self.private / (PREFIX + self.entries[0]['filename'])
        path.parent.mkdir(parents=True)
        path.write_bytes(b'preserve unrelated destination')
        with self.assertRaises(CommandError):
            self.run_import('--apply')
        self.assertEqual(path.read_bytes(), b'preserve unrelated destination')
        self.backup.assert_not_called()

    def test_rollback_cleans_new_files_and_keeps_existing_attachments(self):
        self.run_import('--apply')
        # Isolated partial fixture: preserve first attachment and its file.
        for row in LessonImage.objects.order_by('pk')[1:]:
            row.image.delete(save=False)
            row.delete()
        original = LessonImage.objects.get()
        original_bytes = Path(original.image.path).read_bytes()
        with patch('courses.management.commands.import_media_module_3_images.LessonImageDescription.objects.create', side_effect=RuntimeError('fixture failure')):
            with self.assertRaises(RuntimeError):
                self.run_import('--apply')
        self.assertEqual(LessonImage.objects.count(), 1)
        self.assertEqual(Path(original.image.path).read_bytes(), original_bytes)
        self.assertEqual(len(list(self.private.rglob('*.png'))), 1)

    def test_path_traversal_and_duplicate_manifest_rejected(self):
        data = json.loads(self.manifest.read_text())
        data['assets'][0]['filename'] = '../outside.png'
        self.manifest.write_text(json.dumps(data))
        with self.assertRaises(CommandError):
            self.run_import()
        data['assets'][0] = data['assets'][1]
        self.manifest.write_text(json.dumps(data))
        with self.assertRaises(CommandError):
            self.run_import()

    def test_published_course_and_wrong_titles_rejected(self):
        self.course.is_published = True
        self.course.save()
        with self.assertRaises(CommandError):
            self.run_import('--apply')
        self.course.is_published = False
        self.course.save()
        self.lessons[0].title = 'Different lesson'
        self.lessons[0].save()
        with self.assertRaises(CommandError):
            self.run_import()
        self.backup.assert_not_called()

    def test_backup_failure_prevents_files_and_records(self):
        self.backup.side_effect = CommandError('backup failed')
        with self.assertRaises(CommandError):
            self.run_import('--apply')
        self.assertFalse(self.private.exists())
        self.assertEqual(LessonImage.objects.count(), 0)

    def test_attachments_use_existing_protected_endpoint(self):
        self.run_import('--apply')
        url = reverse('lesson-image', args=[LessonImage.objects.first().pk])
        client = APIClient()
        self.assertEqual(client.get(url).status_code, 401)
        outsider = get_user_model().objects.create_user(username='fixture-outsider')
        client.force_authenticate(outsider)
        self.assertEqual(client.get(url).status_code, 403)
        client.force_authenticate(self.author)
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        response.close()

    def test_oversized_source_rejected(self):
        path = self.assets / self.entries[0]['filename']
        path.write_bytes(b'x' * (5 * 1024 * 1024 + 1))
        with self.assertRaises(CommandError):
            self.run_import()
        self.backup.assert_not_called()

    def test_changed_destination_bytes_rejected_without_repair(self):
        self.run_import('--apply')
        row = LessonImage.objects.first()
        Path(row.image.path).write_bytes(b'changed by fixture')
        with self.assertRaises(CommandError):
            self.run_import('--apply')
        self.assertEqual(Path(row.image.path).read_bytes(), b'changed by fixture')
        self.assertEqual(self.backup.call_count, 1)
