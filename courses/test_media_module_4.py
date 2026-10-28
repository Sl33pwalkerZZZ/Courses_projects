import io
from pathlib import Path
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from courses.management.commands.import_media_module_4 import MODULE_TITLE, TITLES, load_content
from courses.management.commands.import_first_course import curriculum_snapshot
from courses.models import Assignment, Course, Direction, Lesson, LessonImage, LessonLearningContent, Module
from quizzes.models import Quiz
from studio.models import CourseSettings


class MediaModule4Tests(TestCase):
    def setUp(self):
        author = get_user_model().objects.create_user(username='fixture-owner', role='author')
        direction = Direction.objects.create(name='Fixture', slug='fixture')
        self.course = Course.objects.create(pk=27, title='Media draft', slug='ai-media-content', author=author, direction=direction)
        CourseSettings.objects.create(course=self.course, language='ru')
        module = Module.objects.create(course=self.course, title='Основы ИИ в медиапроизводстве', order=1)
        for order in range(1, 4):
            Lesson.objects.create(module=module, title=f'Existing Module 1 lesson {order}', text_content='Preserve exactly', order=order)
        module2 = Module.objects.create(course=self.course, title='Тексты и сценарии с помощью ИИ', order=2)
        for order in range(1, 4):
            Lesson.objects.create(module=module2, title=f'Existing Module 2 lesson {order}', text_content='Preserve this too', order=order)
        module3 = Module.objects.create(course=self.course, title='Создание изображений и графики с помощью ИИ', order=3)
        for order in range(1, 4):
            lesson = Lesson.objects.create(module=module3, title=f'Existing Module 3 lesson {order}', text_content='Preserve images and inline metadata', order=order)
            image = LessonImage.objects.create(lesson=lesson, image=f'lessons/fixture-{order}.png', order=1)
            LessonLearningContent.objects.create(lesson=lesson, source_sections=['Existing heading'], interactions=[{'type':'image_placement','image_id':image.pk,'after_section':'Existing heading','caption':'Keep caption'}])
        self.other = Course.objects.create(pk=8, title='Other published course', slug='other', author=author, direction=direction, is_published=True)
        self.before = curriculum_snapshot(self.course)
        self.other_before = curriculum_snapshot(self.other)

    def run_import(self, *args):
        output = io.StringIO()
        call_command('import_media_module_4', *args, stdout=output)
        return output.getvalue()

    def assert_existing_unchanged(self):
        after = curriculum_snapshot(self.course)
        after['modules'] = [m for m in after['modules'] if m['order'] != 4]
        self.assertEqual(self.before, after)
        self.assertEqual(self.other_before, curriculum_snapshot(self.other))

    def test_default_and_explicit_dry_run_do_not_write(self):
        with patch('courses.management.commands.import_media_module_4.create_backup') as backup:
            for args in [(), ('--dry-run',)]:
                self.assertIn('Dry-run only', self.run_import(*args))
            backup.assert_not_called()
        self.assertEqual(Module.objects.count(), 3)
        self.assertEqual(Lesson.objects.count(), 9)
        self.assert_existing_unchanged()

    @patch('courses.management.commands.import_media_module_4.create_backup', return_value=Path('/temporary-verified-backup'))
    def test_exact_creation_idempotency_content_and_no_assessments(self, backup):
        self.run_import('--apply')
        module = self.course.modules.get(order=4)
        self.assertEqual(module.title, MODULE_TITLE)
        lessons = list(module.lessons.order_by('order'))
        self.assertEqual([l.title for l in lessons], TITLES)
        self.assertEqual([l.order for l in lessons], [1, 2, 3])
        self.assertEqual(Module.objects.count(), 4)
        self.assertEqual(Lesson.objects.count(), 12)
        for lesson, expected in zip(lessons, load_content()['lessons']):
            self.assertEqual(lesson.text_content, expected['text_content'])
            self.assertGreater(len(lesson.text_content), 6000)
            content = lesson.learning_content
            self.assertEqual(content.content_language, 'ru')
            self.assertEqual(content.objectives, expected['objectives'])
            self.assertEqual(len(content.objectives), 3)
            self.assertEqual(content.source_sections, expected['source_sections'])
            self.assertEqual(content.interactions, [])
            self.assertIn('пример', lesson.text_content.lower())
            self.assertIn('без оценки', lesson.text_content)
            self.assertIn('Итоги урока', lesson.text_content)
        snapshot = curriculum_snapshot(self.course)
        self.assertIn('no-op', self.run_import('--apply'))
        self.assertIn('no-op', self.run_import('--dry-run'))
        self.assertEqual(backup.call_count, 1)
        self.assertEqual(snapshot, curriculum_snapshot(self.course))
        self.assertEqual(Quiz.objects.count(), 0)
        self.assertEqual(Assignment.objects.count(), 0)
        self.assertEqual(LessonImage.objects.count(), 3)
        self.assert_existing_unchanged()

    @patch('courses.management.commands.import_media_module_4.create_backup')
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
        self.assertEqual(Module.objects.count(), 3)
        self.assertEqual(Lesson.objects.count(), 9)
        self.assertEqual(LessonLearningContent.objects.count(), 3)
        self.assert_existing_unchanged()

    @patch('courses.management.commands.import_media_module_4.create_backup')
    def test_backup_failure_stops_before_any_write(self, backup):
        backup.side_effect = CommandError('backup failed')
        with self.assertRaises(CommandError):
            self.run_import('--apply')
        self.assertEqual(Module.objects.count(), 3)
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
        Module.objects.create(course=self.course, title='Other teacher draft', order=4)
        with self.assertRaises(CommandError):
            self.run_import()

    def test_misplaced_target_lesson_rejected(self):
        Lesson.objects.create(module=self.course.modules.get(order=1), title=TITLES[0], text_content='Teacher version', order=4)
        with self.assertRaises(CommandError):
            self.run_import()

    @patch('courses.management.commands.import_media_module_4.create_backup')
    def test_teacher_edits_are_not_overwritten(self, backup):
        self.run_import('--apply')
        lesson = self.course.modules.get(order=4).lessons.get(order=1)
        lesson.text_content = 'Teacher edit'
        lesson.save()
        with self.assertRaises(CommandError):
            self.run_import('--apply')
        lesson.refresh_from_db()
        self.assertEqual(lesson.text_content, 'Teacher edit')
        self.assertEqual(backup.call_count, 1)

    @patch('courses.management.commands.import_media_module_4.target_course')
    @patch('courses.management.commands.import_media_module_4.create_backup')
    def test_target_is_rechecked_inside_transaction(self, backup, target):
        target.side_effect = [self.course, CommandError('Course changed before lock')]
        with self.assertRaises(CommandError):
            self.run_import('--apply')
        self.assertEqual(Module.objects.count(), 3)

    def test_source_content_and_media_demonstration_limits(self):
        lessons = load_content()['lessons']
        for lesson in lessons:
            self.assertIn('Ф1', lesson['text_content'])
            self.assertIn('Итоги урока', lesson['text_content'])
            self.assertIn('Самостоятельная практика без оценки', lesson['text_content'])
            self.assertIn('модулю 6', lesson['text_content'])
        self.assertIn('Text-to-Speech', lessons[0]['text_content'])
        self.assertIn('Speech-to-Text', lessons[1]['text_content'])
        self.assertIn('48 000 Гц', lessons[2]['text_content'])

    def test_missing_module_3_blocks_import(self):
        module = self.course.modules.get(order=3)
        module.title = 'Unexpected teacher draft'
        module.save()
        with self.assertRaises(CommandError):
            self.run_import()

    def test_srt_asset_matches_lesson_and_has_valid_intervals(self):
        import re
        from django.conf import settings
        path = Path(settings.BASE_DIR) / 'course_assets/module_4/m4-l2-f1-example.srt'
        cues = path.read_text(encoding='utf-8').strip().split('\n\n')
        self.assertEqual(len(cues),3)
        last_end = -1
        for number, cue in enumerate(cues,1):
            lines = cue.splitlines()
            self.assertEqual(lines[0], str(number))
            match = re.fullmatch(r'(\d{2}):(\d{2}):(\d{2}),(\d{3}) --> (\d{2}):(\d{2}):(\d{2}),(\d{3})',lines[1])
            self.assertIsNotNone(match)
            values = [int(x) for x in match.groups()]
            def ms(v):
                self.assertLess(v[1],60)
                self.assertLess(v[2],60)
                return ((v[0]*60+v[1])*60+v[2])*1000+v[3]
            begin,end = ms(values[:4]),ms(values[4:])
            self.assertGreater(end,begin)
            self.assertGreaterEqual(begin,last_end)
            last_end=end
            self.assertTrue('\n'.join(lines[2:]).strip())
            self.assertIn(cue,load_content()['lessons'][1]['text_content'])

    def test_manifest_does_not_invent_audio_files(self):
        import json
        from django.conf import settings
        from PIL import Image
        root=Path(settings.BASE_DIR)
        manifest=json.loads((root/'docs/courses/media-module-4-assets.json').read_text())
        self.assertEqual(len(manifest['assets']),5)
        for entry in manifest['assets']:
            self.assertEqual(entry['lesson_title'], TITLES[entry['lesson_order']-1])
            for field in ['purpose','after_section','caption_ru','alternative_ru','provenance']:
                self.assertTrue(entry[field])
            self.assertIn(entry['after_section'],load_content()['lessons'][entry['lesson_order']-1]['source_sections'])
            if entry['status']=='ready_local_not_imported':
                self.assertTrue((root/manifest['asset_directory']/entry['filename']).is_file())
            else:
                self.assertEqual(entry['status'],'awaiting_creation')
        with Image.open(root/'course_assets/module_4/m4-l3-audio-workflow.png') as image:
            self.assertEqual(image.format,'PNG')
            self.assertEqual(image.size,(1600,900))

    def test_objectives_must_be_exactly_three(self):
        import json
        data = load_content()
        data['lessons'][0]['objectives'].pop()
        with patch('courses.management.commands.import_media_module_4.CONTENT_PATH') as path:
            path.read_text.return_value = json.dumps(data)
            with self.assertRaises(CommandError):
                load_content()

    def test_local_asset_generation_is_reproducible_and_create_only(self):
        import importlib.util
        import tempfile
        from django.conf import settings
        path = Path(settings.BASE_DIR) / 'scripts/prepare_media_module_4_assets.py'
        spec = importlib.util.spec_from_file_location('module4_assets_fixture', path)
        generator = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(generator)
        with tempfile.TemporaryDirectory() as directory:
            generator.create_assets(directory)
            before = {p.name:p.read_bytes() for p in Path(directory).iterdir()}
            generator.create_assets(directory)
            self.assertEqual(before,{p.name:p.read_bytes() for p in Path(directory).iterdir()})
            self.assertEqual(before['m4-l2-f1-example.srt'],generator.srt_example())
            target = Path(directory) / 'm4-l2-f1-example.srt'
            target.write_text('Teacher change')
            with self.assertRaises(ValueError):
                generator.create_assets(directory)
            self.assertEqual(target.read_text(),'Teacher change')
