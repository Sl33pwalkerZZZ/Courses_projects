import io
from pathlib import Path
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from courses.management.commands.import_media_module_2 import MODULE_TITLE, TITLES, load_content
from courses.management.commands.import_first_course import curriculum_snapshot
from courses.models import Assignment, Course, Direction, Lesson, LessonLearningContent, Module
from quizzes.models import Quiz
from studio.models import CourseSettings


class MediaModule2Tests(TestCase):
    def setUp(self):
        author = get_user_model().objects.create_user(username='fixture-owner', role='author')
        direction = Direction.objects.create(name='Fixture', slug='fixture')
        self.course = Course.objects.create(pk=10, title='Media draft', slug='ai-media-content', author=author, direction=direction)
        CourseSettings.objects.create(course=self.course, language='ru')
        module = Module.objects.create(course=self.course, title='Основы ИИ в медиапроизводстве', order=1)
        Lesson.objects.create(module=module, title='Existing Module 1 content', text_content='Preserve exactly', order=1)
        self.other = Course.objects.create(pk=8, title='Other published course', slug='other', author=author, direction=direction, is_published=True)
        self.before = curriculum_snapshot(self.course)
        self.other_before = curriculum_snapshot(self.other)

    def run_import(self, *args):
        output = io.StringIO()
        call_command('import_media_module_2', *args, stdout=output)
        return output.getvalue()

    def assert_existing_unchanged(self):
        after = curriculum_snapshot(self.course)
        after['modules'] = [m for m in after['modules'] if m['order'] != 2]
        self.assertEqual(self.before, after)
        self.assertEqual(self.other_before, curriculum_snapshot(self.other))

    def test_default_and_explicit_dry_run_do_not_write(self):
        with patch('courses.management.commands.import_media_module_2.create_backup') as backup:
            for args in [(), ('--dry-run',)]:
                self.assertIn('Dry-run only', self.run_import(*args))
            backup.assert_not_called()
        self.assertEqual(Module.objects.count(), 1)
        self.assertEqual(Lesson.objects.count(), 1)
        self.assert_existing_unchanged()

    @patch('courses.management.commands.import_media_module_2.create_backup', return_value=Path('/temporary-verified-backup'))
    def test_exact_creation_idempotency_content_and_no_assessments(self, backup):
        self.run_import('--apply')
        module = self.course.modules.get(order=2)
        self.assertEqual(module.title, MODULE_TITLE)
        lessons = list(module.lessons.order_by('order'))
        self.assertEqual([l.title for l in lessons], TITLES)
        self.assertEqual([l.order for l in lessons], [1, 2, 3])
        self.assertEqual(Module.objects.count(), 2)
        self.assertEqual(Lesson.objects.count(), 4)
        for lesson, expected in zip(lessons, load_content()['lessons']):
            self.assertEqual(lesson.text_content, expected['text_content'])
            self.assertGreater(len(lesson.text_content), 6000)
            content = lesson.learning_content
            self.assertEqual(content.content_language, 'ru')
            self.assertEqual(content.objectives, expected['objectives'])
            self.assertEqual(len(content.objectives), 3)
            self.assertEqual(content.source_sections, expected['source_sections'])
            self.assertEqual(content.interactions, [])
            self.assertIn('Пример', lesson.text_content)
            self.assertIn('без оценки', lesson.text_content)
            self.assertIn('Итоги урока', lesson.text_content)
        snapshot = curriculum_snapshot(self.course)
        self.assertIn('no-op', self.run_import('--apply'))
        self.assertIn('no-op', self.run_import('--dry-run'))
        self.assertEqual(backup.call_count, 1)
        self.assertEqual(snapshot, curriculum_snapshot(self.course))
        self.assertEqual(Quiz.objects.count(), 0)
        self.assertEqual(Assignment.objects.count(), 0)
        self.assert_existing_unchanged()

    @patch('courses.management.commands.import_media_module_2.create_backup')
    def test_transaction_rolls_back_after_partial_creation(self, backup):
        original = LessonLearningContent.save
        count = 0
        def fail_second(instance, *args, **kwargs):
            nonlocal count
            count += 1
            if count == 2:
                raise RuntimeError('isolated failure')
            return original(instance, *args, **kwargs)
        with patch.object(LessonLearningContent, 'save', fail_second):
            with self.assertRaises(RuntimeError):
                self.run_import('--apply')
        self.assertEqual(Module.objects.count(), 1)
        self.assertEqual(Lesson.objects.count(), 1)
        self.assertEqual(LessonLearningContent.objects.count(), 0)
        self.assert_existing_unchanged()

    @patch('courses.management.commands.import_media_module_2.create_backup')
    def test_backup_failure_stops_before_any_write(self, backup):
        backup.side_effect = CommandError('backup failed')
        with self.assertRaises(CommandError):
            self.run_import('--apply')
        self.assertEqual(Module.objects.count(), 1)
        self.assert_existing_unchanged()

    def test_wrong_course_or_published_course_rejected(self):
        for change in ['slug', 'is_published']:
            with self.subTest(change=change):
                setattr(self.course, change, 'wrong' if change == 'slug' else True)
                self.course.save()
                with self.assertRaises(CommandError):
                    self.run_import()
                self.course.slug = 'ai-media-content'
                self.course.is_published = False
                self.course.save()

    def test_conflicting_module_order_or_title_rejected(self):
        Module.objects.create(course=self.course, title='Other teacher draft', order=2)
        with self.assertRaises(CommandError):
            self.run_import()

    def test_misplaced_target_lesson_rejected(self):
        Lesson.objects.create(module=self.course.modules.get(), title=TITLES[0], text_content='Teacher version', order=2)
        with self.assertRaises(CommandError):
            self.run_import()

    @patch('courses.management.commands.import_media_module_2.create_backup')
    def test_teacher_edits_are_not_overwritten(self, backup):
        self.run_import('--apply')
        lesson = self.course.modules.get(order=2).lessons.get(order=1)
        lesson.text_content = 'Teacher edit'
        lesson.save()
        with self.assertRaises(CommandError):
            self.run_import('--apply')
        lesson.refresh_from_db()
        self.assertEqual(lesson.text_content, 'Teacher edit')
        self.assertEqual(backup.call_count, 1)

    @patch('courses.management.commands.import_media_module_2.target_course')
    @patch('courses.management.commands.import_media_module_2.create_backup')
    def test_target_is_rechecked_inside_transaction(self, backup, target):
        target.side_effect = [self.course, CommandError('Course changed before lock')]
        with self.assertRaises(CommandError):
            self.run_import('--apply')
        self.assertEqual(Module.objects.count(), 1)

    def test_complete_demo_sequence_and_assessment_policy(self):
        lessons = load_content()['lessons']
        self.assertTrue(all('Ф1' in l['text_content'] for l in lessons))
        self.assertIn('Пример улучшенного запроса:', lessons[1]['text_content'])
        self.assertIn('0–10 с', lessons[1]['text_content'])
        self.assertIn('65–75 с', lessons[1]['text_content'])
        self.assertTrue(all(name in lessons[2]['text_content'] for name in ['YouTube', 'Instagram Reels', 'TikTok']))
        self.assertIn('только в модуле 6', lessons[2]['text_content'])
