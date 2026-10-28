import io
from pathlib import Path
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from courses.management.commands.import_media_module_3 import MODULE_TITLE, TITLES, load_content
from courses.management.commands.import_first_course import curriculum_snapshot
from courses.models import Assignment, Course, Direction, Lesson, LessonImage, LessonLearningContent, Module
from quizzes.models import Quiz
from studio.models import CourseSettings


class MediaModule3Tests(TestCase):
    def setUp(self):
        author = get_user_model().objects.create_user(username='fixture-owner', role='author')
        direction = Direction.objects.create(name='Fixture', slug='fixture')
        self.course = Course.objects.create(pk=10, title='Media draft', slug='ai-media-content', author=author, direction=direction)
        CourseSettings.objects.create(course=self.course, language='ru')
        module = Module.objects.create(course=self.course, title='Основы ИИ в медиапроизводстве', order=1)
        for order in range(1, 4):
            Lesson.objects.create(module=module, title=f'Existing Module 1 lesson {order}', text_content='Preserve exactly', order=order)
        module2 = Module.objects.create(course=self.course, title='Тексты и сценарии с помощью ИИ', order=2)
        for order in range(1, 4):
            Lesson.objects.create(module=module2, title=f'Existing Module 2 lesson {order}', text_content='Preserve this too', order=order)
        self.other = Course.objects.create(pk=8, title='Other published course', slug='other', author=author, direction=direction, is_published=True)
        self.before = curriculum_snapshot(self.course)
        self.other_before = curriculum_snapshot(self.other)

    def run_import(self, *args):
        output = io.StringIO()
        call_command('import_media_module_3', *args, stdout=output)
        return output.getvalue()

    def assert_existing_unchanged(self):
        after = curriculum_snapshot(self.course)
        after['modules'] = [m for m in after['modules'] if m['order'] != 3]
        self.assertEqual(self.before, after)
        self.assertEqual(self.other_before, curriculum_snapshot(self.other))

    def test_default_and_explicit_dry_run_do_not_write(self):
        with patch('courses.management.commands.import_media_module_3.create_backup') as backup:
            for args in [(), ('--dry-run',)]:
                self.assertIn('Dry-run only', self.run_import(*args))
            backup.assert_not_called()
        self.assertEqual(Module.objects.count(), 2)
        self.assertEqual(Lesson.objects.count(), 6)
        self.assert_existing_unchanged()

    @patch('courses.management.commands.import_media_module_3.create_backup', return_value=Path('/temporary-verified-backup'))
    def test_exact_creation_idempotency_content_and_no_assessments(self, backup):
        self.run_import('--apply')
        module = self.course.modules.get(order=3)
        self.assertEqual(module.title, MODULE_TITLE)
        lessons = list(module.lessons.order_by('order'))
        self.assertEqual([l.title for l in lessons], TITLES)
        self.assertEqual([l.order for l in lessons], [1, 2, 3])
        self.assertEqual(Module.objects.count(), 3)
        self.assertEqual(Lesson.objects.count(), 9)
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
        self.assertEqual(LessonImage.objects.count(), 0)
        self.assert_existing_unchanged()

    @patch('courses.management.commands.import_media_module_3.create_backup')
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
        self.assertEqual(Module.objects.count(), 2)
        self.assertEqual(Lesson.objects.count(), 6)
        self.assertEqual(LessonLearningContent.objects.count(), 0)
        self.assert_existing_unchanged()

    @patch('courses.management.commands.import_media_module_3.create_backup')
    def test_backup_failure_stops_before_any_write(self, backup):
        backup.side_effect = CommandError('backup failed')
        with self.assertRaises(CommandError):
            self.run_import('--apply')
        self.assertEqual(Module.objects.count(), 2)
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
        Module.objects.create(course=self.course, title='Other teacher draft', order=3)
        with self.assertRaises(CommandError):
            self.run_import()

    def test_misplaced_target_lesson_rejected(self):
        Lesson.objects.create(module=self.course.modules.get(order=1), title=TITLES[0], text_content='Teacher version', order=3)
        with self.assertRaises(CommandError):
            self.run_import()

    @patch('courses.management.commands.import_media_module_3.create_backup')
    def test_teacher_edits_are_not_overwritten(self, backup):
        self.run_import('--apply')
        lesson = self.course.modules.get(order=3).lessons.get(order=1)
        lesson.text_content = 'Teacher edit'
        lesson.save()
        with self.assertRaises(CommandError):
            self.run_import('--apply')
        lesson.refresh_from_db()
        self.assertEqual(lesson.text_content, 'Teacher edit')
        self.assertEqual(backup.call_count, 1)

    @patch('courses.management.commands.import_media_module_3.target_course')
    @patch('courses.management.commands.import_media_module_3.create_backup')
    def test_target_is_rechecked_inside_transaction(self, backup, target):
        target.side_effect = [self.course, CommandError('Course changed before lock')]
        with self.assertRaises(CommandError):
            self.run_import('--apply')
        self.assertEqual(Module.objects.count(), 2)

    def test_complete_examples_and_assessment_policy(self):
        lessons = load_content()['lessons']
        for lesson in lessons:
            self.assertIn('Ф1', lesson['text_content'])
            import re
            self.assertGreaterEqual(len(re.findall(r'Пример (?:улучшенного )?запроса', lesson['text_content'])), 2)
            self.assertRegex(lesson['text_content'], r'модул[ею] 6')
            self.assertIn('Типичные', lesson['text_content'])
        self.assertIn('Соотношение сторон', lessons[0]['text_content'])
        self.assertIn('Визуальная иерархия', lessons[1]['text_content'])
        self.assertIn('CapCut Desktop', lessons[2]['text_content'])

    def test_visual_manifest_is_complete_and_explicitly_not_imported(self):
        import json
        from django.conf import settings
        manifest = json.loads((Path(settings.BASE_DIR) / 'docs/courses/media-module-3-assets.json').read_text())
        self.assertEqual(manifest['status'], 'planning_only_no_files_created')
        assets = manifest['assets']
        self.assertEqual(len(assets), 6)
        self.assertEqual(len({a['filename'] for a in assets}), 6)
        for order in (1, 2, 3):
            group = [a for a in assets if a['lesson_order'] == order]
            self.assertEqual(len(group), 2)
            for item in group:
                self.assertEqual(item['lesson_title'], TITLES[order-1])
                self.assertFalse(item['decorative'])
                for field in ('learning_purpose', 'must_depict', 'caption_ru', 'provenance', 'licensing_requirement'):
                    self.assertTrue(item[field])
                self.assertTrue(item['alt_text']['ru'])
                self.assertEqual(item['status'], 'awaiting_creation')
                self.assertEqual(item['format'], 'PNG')

    def test_missing_module_2_blocks_import(self):
        module = self.course.modules.get(order=2)
        module.title = 'Unexpected teacher draft'
        module.save()
        with self.assertRaises(CommandError):
            self.run_import()

    def test_objectives_must_be_exactly_three(self):
        import json
        data = load_content()
        data['lessons'][0]['objectives'].pop()
        with patch('courses.management.commands.import_media_module_3.CONTENT_PATH') as path:
            path.read_text.return_value = json.dumps(data)
            with self.assertRaises(CommandError):
                load_content()
