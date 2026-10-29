"""Exact editorial patch lifecycle in isolated databases only."""
import io
import json
from pathlib import Path
from unittest.mock import patch

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TransactionTestCase

from courses.management.commands.import_media_module_4 import load_content
from courses.models import Course, Direction, Module, Lesson, LessonLearningContent, LessonAttachment


class Module4EditorialTests(TransactionTestCase):
    def setUp(self):
        data=json.loads((Path(settings.BASE_DIR)/'docs/courses/module-4-editorial-corrections.json').read_text())
        self.edits=data
        author=get_user_model().objects.create_user(username='editorial-fixture',role='author')
        direction=Direction.objects.create(name='Fixture',slug='fixture')
        self.course=Course.objects.create(title='Draft',slug='ai-media-content',author=author,direction=direction)
        module=Module.objects.create(course=self.course,title=load_content()['module'],order=4)
        for index,entry in enumerate(load_content()['lessons'],1):
            text=entry['text_content']
            for edit in data['lessons'][index-1]['replacements']:text=text.replace(edit['after'],edit['before'])
            lesson=Lesson.objects.create(module=module,title=entry['title'],text_content=text,order=index)
            LessonLearningContent.objects.create(lesson=lesson,objectives=entry['objectives'],source_sections=entry['source_sections'])
        for index,edit in enumerate(data['captions']):
            LessonAttachment.objects.create(lesson=module.lessons.get(order=2+index),filename=edit['filename'],caption=edit['before'],
                                            sha256=str(index)*64,kind='srt' if index==0 else 'audio')
        other=Module.objects.create(course=self.course,title='Preserve Module 1',order=1)
        self.other=Lesson.objects.create(module=other,title='Preserve',text_content='Unchanged educational text',order=1)
        self.module=module
        self.before=list(module.lessons.values_list('pk','title','order'))
        self.learning=list(LessonLearningContent.objects.filter(lesson__module=module).values())

    def run_command(self,*args):
        output=io.StringIO();call_command('correct_module4_editorial',*args,stdout=output);return output.getvalue()

    def test_exact_edits_preserve_structure_and_idempotency(self):
        with patch('courses.management.commands.correct_module4_editorial.create_backup',return_value=Path('/verified-test-backup')) as backup:
            self.assertIn('"lesson_updates": 3',self.run_command('--dry-run'));backup.assert_not_called()
            self.run_command('--apply');self.assertEqual(backup.call_count,1)
            self.assertIn('"lesson_updates": 0',self.run_command('--apply'));self.assertEqual(backup.call_count,1)
        self.assertEqual(list(self.module.lessons.values_list('pk','title','order')),self.before)
        self.assertEqual(list(LessonLearningContent.objects.filter(lesson__module=self.module).values()),self.learning)
        for lesson,expected in zip(self.module.lessons.order_by('order'),load_content()['lessons']):
            self.assertEqual(lesson.text_content,expected['text_content'])
        self.other.refresh_from_db();self.assertEqual(self.other.text_content,'Unchanged educational text')
        self.course.refresh_from_db();self.assertFalse(self.course.is_published)

    def test_unexpected_text_rejects_before_backup(self):
        lesson=self.module.lessons.get(order=1);lesson.text_content='Unexpected teacher change';lesson.save()
        with patch('courses.management.commands.correct_module4_editorial.create_backup') as backup:
            with self.assertRaises(CommandError):self.run_command('--apply')
            backup.assert_not_called()
        lesson.refresh_from_db();self.assertEqual(lesson.text_content,'Unexpected teacher change')

    def test_backup_failure_does_not_change_lessons(self):
        before=list(self.module.lessons.values_list('pk','text_content'))
        with patch('courses.management.commands.correct_module4_editorial.create_backup',side_effect=CommandError('fixture backup failure')):
            with self.assertRaises(CommandError):self.run_command('--apply')
        self.assertEqual(list(self.module.lessons.values_list('pk','text_content')),before)
