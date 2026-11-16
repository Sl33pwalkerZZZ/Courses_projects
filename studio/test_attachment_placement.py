"""Disposable database records and synthetic file names; no production storage writes."""
from unittest.mock import patch
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from courses.models import Course, Direction, Module, Lesson, LessonLearningContent, LessonAttachment


class AttachmentPlacementTests(TestCase):
    def setUp(self):
        self.owner = get_user_model().objects.create_user(username='move-author', role='author')
        direction = Direction.objects.create(name='Test', slug='move-test')
        self.course = Course.objects.create(title='Draft', slug='move-test', author=self.owner, direction=direction)
        self.module = Module.objects.create(course=self.course, title='Module', order=1)
        self.lesson = Lesson.objects.create(module=self.module, title='Lesson', order=1, text_content='First\n\nExplanation\n\nSecond\n\nEnd')
        self.learning = LessonLearningContent.objects.create(lesson=self.lesson, content_language='ru', source_sections=['First', 'Second'], objectives=['Goal'], interactions=[])
        self.video = self.asset('video', 'First')
        self.track = self.asset('vtt', 'First')
        self.srt = self.asset('srt', 'First')
        self.client = APIClient()
        self.client.force_authenticate(self.owner)

    def asset(self, kind, anchor, lesson=None):
        n = LessonAttachment.objects.count() + 1
        return LessonAttachment.objects.create(lesson=lesson or self.lesson, kind=kind, after_section=anchor, file=f'private/fixture-{n}.{kind}', filename=f'fixture-{n}.{kind}', label=f'Fixture {n}', order=n, sha256=f'{n:064x}', provenance='Original synthetic fixture')

    def url(self, asset=None):
        return f'/api/studio/lessons/{self.lesson.pk}/attachments/{(asset or self.video).pk}/placement/'

    def payload(self, asset=None, **kwargs):
        asset = asset or self.video
        return {'after_section': 'Second', 'expected_after_section': asset.after_section, 'expected_sections': ['First', 'Second'], 'expected_subtitle_id': self.track.pk if asset == self.video and asset.after_section else None, **kwargs}

    def move(self, asset=None, **kwargs):
        return self.client.patch(self.url(asset), self.payload(asset, **kwargs), format='json')

    def test_video_track_move_reload_and_student_preview(self):
        before = list(self.lesson.attachments.values())
        result = self.move()
        self.assertEqual(result.status_code, 200, result.data)
        self.assertIn('private', result['Cache-Control'])
        for old, new in zip(before, self.lesson.attachments.values()):
            self.assertEqual(new, {**old, 'after_section': 'Second'} if old['kind'] in ('video', 'vtt') else old)
        lesson = self.client.get(f'/api/lessons/{self.lesson.pk}/').data
        self.assertEqual({a['id']: a['after_section'] for a in lesson['attachments']}, {self.video.pk: 'Second', self.track.pk: 'Second', self.srt.pk: 'First'})
        self.assertEqual(lesson['text_content'], self.lesson.text_content)
        self.assertEqual(lesson['learning_content']['source_sections'], ['First', 'Second'])
        self.assertEqual(self.move().status_code, 400)  # stale old source

    def test_invalid_or_stale_headings_leave_every_record_intact(self):
        before = list(self.lesson.attachments.values())
        for changes in [{'after_section': 'Missing'}, {'expected_sections': ['Second', 'First']}, {'expected_after_section': 'Old'}, {'expected_subtitle_id': None}]:
            with self.subTest(changes=changes):
                self.assertEqual(self.move(**changes).status_code, 400)
                self.assertEqual(list(self.lesson.attachments.values()), before)
        self.lesson.text_content += '\n\nSecond'
        self.lesson.save()
        self.assertEqual(self.move().status_code, 400)

    def test_reader_fallback_lessons_are_not_given_inline_move_targets(self):
        self.lesson.text_content = 'Introduction\n\n' + self.lesson.text_content
        self.lesson.save()
        self.assertEqual(self.move().data['placement_error'], 'invalid')
        self.lesson.text_content = self.lesson.text_content.removeprefix('Introduction\n\n')
        self.lesson.save()
        self.learning.interactions = [{'type': 'llm_steps', 'steps': []}]
        self.learning.save()
        self.assertEqual(self.move().data['placement_error'], 'invalid')

    def test_destination_video_or_track_rejected(self):
        for kind in ['video', 'vtt']:
            extra = self.asset(kind, 'Second')
            before = list(self.lesson.attachments.values())
            result = self.move()
            self.assertEqual(result.status_code, 400)
            self.assertEqual(result.data['placement_error'], 'ambiguous')
            self.assertEqual(list(self.lesson.attachments.values()), before)
            extra.delete()

    def test_ambiguous_source_and_direct_track_rejected(self):
        self.assertEqual(self.move(self.track).data['placement_error'], 'track')
        self.asset('vtt', 'First')
        self.assertEqual(self.move().data['placement_error'], 'ambiguous')

    def test_standalone_srt_audio_and_legacy_orphan_pair(self):
        self.assertEqual(self.move(self.srt).status_code, 200)
        audio = self.asset('audio', 'Legacy missing anchor')
        self.assertEqual(self.move(audio).status_code, 200)
        self.video.after_section = 'Legacy'
        self.video.save()
        self.track.after_section = 'Legacy'
        self.track.save()
        self.assertEqual(self.move().status_code, 200)
        self.assertEqual(self.lesson.attachments.get(pk=self.srt.pk).after_section, 'Second')

    def test_unpaired_video_does_not_capture_destination_track_or_empty_source_track(self):
        self.track.after_section = 'Second'
        self.track.save()
        self.assertEqual(self.move(expected_subtitle_id=None).status_code, 400)
        self.video.after_section = ''
        self.video.save()
        self.track.after_section = ''
        self.track.save()
        self.assertEqual(self.move(expected_subtitle_id=None).status_code, 200)
        self.track.refresh_from_db()
        self.assertEqual(self.track.after_section, '')

    def test_same_lesson_ownership_roles_and_published_lock(self):
        other_lesson = Lesson.objects.create(module=self.module, title='Other', order=2)
        foreign = self.asset('audio', 'First', other_lesson)
        self.assertEqual(self.client.patch(self.url(foreign), self.payload(foreign), format='json').status_code, 404)
        for role, expected in [('student', 403), ('author', 404)]:
            user = get_user_model().objects.create_user(username=f'other-move-{role}', role=role)
            self.client.force_authenticate(user)
            self.assertEqual(self.move().status_code, expected)
        self.client.force_authenticate(None)
        self.assertEqual(self.move().status_code, 401)
        self.client.force_authenticate(self.owner)
        self.course.is_published = True
        self.course.save()
        self.assertEqual(self.move().data['placement_error'], 'locked')

    def test_rollback_on_failure_and_repeated_current_destination_is_noop(self):
        before = list(self.lesson.attachments.values())
        from django.db.models.query import QuerySet
        original = QuerySet.update
        changed = []
        def fail_after_placement(queryset, **kwargs):
            count = original(queryset, **kwargs)
            if queryset.model is LessonAttachment:
                changed.append(count)
                raise RuntimeError('fixture fail after paired update')
            return count
        with patch('django.db.models.query.QuerySet.update', autospec=True, side_effect=fail_after_placement):
            with self.assertRaises(RuntimeError):
                self.move()
        self.assertEqual(changed, [2])
        self.assertEqual(list(self.lesson.attachments.values()), before)
        self.assertEqual(self.move(after_section='First').status_code, 200)
        self.assertEqual(list(self.lesson.attachments.values()), before)
