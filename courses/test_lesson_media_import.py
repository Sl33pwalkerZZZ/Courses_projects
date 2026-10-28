import io
import json
import tempfile
from pathlib import Path
from unittest.mock import patch

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase, override_settings

from courses.models import Course, Direction, Lesson, LessonAttachment, LessonImage, LessonLearningContent, Module
from courses.management.commands.import_media_module_4 import load_content
from courses.management.commands.import_first_course import curriculum_snapshot


class LessonMediaImportTests(TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.override=override_settings(MEDIA_ROOT=self.root/'private')
        self.override.enable();self.addCleanup(self.override.disable)
        self.manifest=self.root/'manifest.json'
        data=json.loads((Path(settings.BASE_DIR)/'docs/courses/media-module-4-assets.json').read_text())
        self.manifest.write_text(json.dumps(data))
        author=get_user_model().objects.create_user(username='fixture-owner',role='author')
        direction=Direction.objects.create(name='Fixture',slug='fixture')
        self.course=Course.objects.create(title='Fixture draft',slug='ai-media-content',author=author,direction=direction)
        module=Module.objects.create(course=self.course,title=data['module_title'],order=4)
        for order,entry in enumerate(load_content()['lessons'],1):
            lesson=Lesson.objects.create(module=module,title=entry['title'],text_content=entry['text_content'],order=order)
            LessonLearningContent.objects.create(lesson=lesson,objectives=entry['objectives'],source_sections=entry['source_sections'])
        self.before=curriculum_snapshot(self.course)
        self.backup_patch=patch('courses.management.commands.import_lesson_media.create_backup',return_value=Path('/verified-fixture-backup'))
        self.backup=self.backup_patch.start();self.addCleanup(self.backup_patch.stop)

    def run_import(self,*args):
        output=io.StringIO()
        call_command('import_lesson_media','--manifest',str(self.manifest),*args,stdout=output)
        return output.getvalue()

    def test_dry_run_creates_neither_records_nor_files(self):
        self.assertIn('"create": 2',self.run_import())
        self.backup.assert_not_called()
        self.assertEqual(LessonAttachment.objects.count(),0)
        self.assertEqual(LessonImage.objects.count(),0)
        self.assertFalse((self.root/'private').exists())
        self.assertEqual(curriculum_snapshot(self.course),self.before)

    def test_srt_and_diagram_only_idempotent_preserves_theory(self):
        self.run_import('--apply')
        self.assertEqual(LessonAttachment.objects.count(),1)
        self.assertEqual(LessonAttachment.objects.get().kind,'srt')
        self.assertEqual(LessonImage.objects.count(),1)
        attachment=LessonAttachment.objects.get()
        self.assertIn('5. SRT',attachment.after_section)
        self.assertEqual(self.backup.call_count,1)
        self.assertIn('"create": 0',self.run_import('--apply'))
        self.assertEqual(self.backup.call_count,1)
        after=curriculum_snapshot(self.course)
        for module in after['modules']:
            for lesson in module['lessons']:
                lesson['images']=[]
                lesson['learning_content']['interactions']=[]
        self.assertEqual(after,self.before)

    def test_metadata_conflict_stops_without_modifying_existing_assets(self):
        self.run_import('--apply')
        asset=LessonAttachment.objects.get();asset.caption='Teacher change';asset.save()
        with self.assertRaises(CommandError):self.run_import('--apply')
        asset.refresh_from_db();self.assertEqual(asset.caption,'Teacher change')
        self.assertEqual(self.backup.call_count,1)

    def test_atomic_rollback_removes_only_new_files(self):
        with patch('courses.models.LessonLearningContent.save',side_effect=RuntimeError('fixture failure')):
            with self.assertRaises(RuntimeError):self.run_import('--apply')
        self.assertEqual(LessonAttachment.objects.count(),0)
        self.assertEqual(LessonImage.objects.count(),0)
        self.assertFalse([p for p in (self.root/'private').rglob('*') if p.is_file()])
        self.assertEqual(curriculum_snapshot(self.course),self.before)

    def test_missing_migration_apply_rejected_before_backup(self):
        with patch('courses.management.commands.import_lesson_media.attachments_ready',return_value=False):
            self.assertIn('"migration_required": true',self.run_import())
            with self.assertRaises(CommandError):self.run_import('--apply')
        self.backup.assert_not_called()

    def test_invalid_anchor_rejected_before_backup(self):
        data=json.loads(self.manifest.read_text());data['assets'][2]['after_section']='Missing'
        self.manifest.write_text(json.dumps(data))
        with self.assertRaises(CommandError):self.run_import('--apply')
        self.backup.assert_not_called()
