import io
import json
import tempfile
from pathlib import Path
from unittest.mock import patch

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase, override_settings

from courses.management.commands.import_first_course import curriculum_snapshot
from courses.management.commands.import_media_module_3 import load_content
from courses.models import Course, Direction, Lesson, LessonImage, LessonLearningContent, Module
from studio.serializers import LessonWriteSerializer


class PlacementTests(TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.override = override_settings(MEDIA_ROOT=self.temp.name)
        self.override.enable()
        self.addCleanup(self.override.disable)
        self.manifest = Path(self.temp.name) / 'manifest.json'
        self.data = json.loads((Path(settings.BASE_DIR) / 'docs/courses/media-module-3-assets.json').read_text())
        self.manifest.write_text(json.dumps(self.data))
        author = get_user_model().objects.create_user(username='fixture-author', role='author')
        direction = Direction.objects.create(name='Fixture', slug='fixture')
        self.course = Course.objects.create(title='Fixture', slug='ai-media-content', author=author, direction=direction)
        module = Module.objects.create(course=self.course, order=3, title='Создание изображений и графики с помощью ИИ')
        for order, source in enumerate(load_content()['lessons'], 1):
            lesson = Lesson.objects.create(module=module, order=order, title=source['title'], text_content=source['text_content'])
            LessonLearningContent.objects.create(lesson=lesson, objectives=source['objectives'], source_sections=source['source_sections'])
            for gallery_order, entry in enumerate([a for a in self.data['assets'] if a['lesson_order']==order],1):
                image = LessonImage(lesson=lesson, order=gallery_order)
                image.image.save(entry['filename'], ContentFile(b'fixture file; no pixel decoding in placement operation'))
        self.before = curriculum_snapshot(self.course)
        self.backup_patch = patch('courses.management.commands.place_media_module_3_images.create_backup', return_value=Path('/fixture-backup'))
        self.backup = self.backup_patch.start()
        self.addCleanup(self.backup_patch.stop)

    def run_command(self, *args):
        output = io.StringIO()
        call_command('place_media_module_3_images', '--manifest', str(self.manifest), *args, stdout=output)
        return output.getvalue()

    def test_dry_run_preserves_every_record(self):
        self.assertIn('"learning_content_updates": 3', self.run_command())
        self.assertEqual(curriculum_snapshot(self.course), self.before)
        self.backup.assert_not_called()

    def test_apply_only_placement_metadata_then_noop(self):
        self.run_command('--apply')
        for lesson in Lesson.objects.all():
            entries = lesson.learning_content.interactions
            self.assertEqual(len(entries), 2)
            self.assertTrue(all(p['image_id'] in set(lesson.images.values_list('id', flat=True)) for p in entries))
        after = curriculum_snapshot(self.course)
        for module in after['modules']:
            for lesson in module['lessons']:
                lesson['learning_content']['interactions'] = []
        self.assertEqual(after, self.before)
        self.assertIn('"learning_content_updates": 0', self.run_command('--apply'))
        self.assertEqual(self.backup.call_count, 1)
        self.assertEqual(LessonImage.objects.count(), 6)

    def test_conflicting_anchor_or_existing_placements_fail(self):
        self.data['assets'][0]['placement']['after_section'] = 'Unknown section'
        self.manifest.write_text(json.dumps(self.data))
        with self.assertRaises(CommandError): self.run_command('--apply')
        self.backup.assert_not_called()

    def test_foreign_image_reference_and_duplicate_id_rejected_by_api_serializer(self):
        first, second = list(Lesson.objects.order_by('order'))[:2]
        base = {'type':'image_placement', 'image_id':second.images.first().pk,
                'after_section':first.learning_content.source_sections[0], 'caption':'Fixture caption'}
        serializer = LessonWriteSerializer(instance=first, data={'learning_content':{'interactions':[base]}}, partial=True)
        self.assertFalse(serializer.is_valid())
        base['image_id'] = first.images.first().pk
        serializer = LessonWriteSerializer(instance=first, data={'learning_content':{'interactions':[base,base]}}, partial=True)
        self.assertFalse(serializer.is_valid())

    def test_transaction_rolls_back_all_metadata(self):
        original = LessonLearningContent.save
        count = 0
        def fail(instance, *args, **kwargs):
            nonlocal count
            count += 1
            if count == 2: raise RuntimeError('fixture failure')
            return original(instance, *args, **kwargs)
        with patch.object(LessonLearningContent, 'save', fail):
            with self.assertRaises(RuntimeError): self.run_command('--apply')
        self.assertEqual(curriculum_snapshot(self.course), self.before)

    def test_existing_conflict_preserved(self):
        self.run_command('--apply')
        content = LessonLearningContent.objects.first()
        content.interactions[0]['caption'] = 'Teacher edit'
        content.save()
        with self.assertRaises(CommandError): self.run_command('--apply')
        content.refresh_from_db()
        self.assertEqual(content.interactions[0]['caption'], 'Teacher edit')
