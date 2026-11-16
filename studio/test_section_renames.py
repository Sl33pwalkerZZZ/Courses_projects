"""All writes use disposable TestCase fixtures; no protected file writes required."""
from copy import deepcopy
from unittest.mock import patch
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from courses.models import Course, Direction, Module, Lesson, LessonLearningContent, LessonAttachment, LessonImage


class SectionRenameTests(TestCase):
    def setUp(self):
        self.owner = get_user_model().objects.create_user(username='section-author', role='author')
        direction = Direction.objects.create(name='Test', slug='section-test')
        self.course = Course.objects.create(title='Draft', slug='sections-test', author=self.owner, direction=direction)
        module = Module.objects.create(course=self.course, title='Module', order=1)
        self.lesson = Lesson.objects.create(module=module, title='Lesson', order=1, text_content='First\n\nExplanation\n\nSecond\n\nEnd')
        self.learning = LessonLearningContent.objects.create(lesson=self.lesson, content_language='ru', source_sections=['First', 'Second'], objectives=['Goal'], interactions=[])
        self.assets = [LessonAttachment.objects.create(lesson=self.lesson, kind=kind, file=f'private/{kind}', filename=f'fixture.{kind}', after_section='First', order=i, sha256=str(i)*64) for i, kind in enumerate(['video', 'vtt'], 1)]
        self.client = APIClient()
        self.client.force_authenticate(self.owner)
        self.url = f'/api/studio/lessons/{self.lesson.pk}/'
        self.payload = {'text_content': self.lesson.text_content.replace('First', 'Renamed'), 'learning_content': {'content_language': 'ru', 'source_sections': ['Renamed', 'Second'], 'objectives': ['Goal'], 'interactions': []}, 'section_renames': [{'from_title': 'First', 'to_title': 'Renamed'}]}

    def test_rename_reload_preview_preserves_attachment_identity(self):
        before = list(self.lesson.attachments.values())
        result = self.client.patch(self.url, self.payload, format='json')
        self.assertEqual(result.status_code, 200, result.data)
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.learning_content.source_sections, ['Renamed', 'Second'])
        for original, updated in zip(before, self.lesson.attachments.values()):
            self.assertEqual(updated, {**original, 'after_section': 'Renamed'})
        preview = self.client.get(f'/api/instructor/courses/{self.course.slug}/preview/')
        self.assertEqual(preview.status_code, 200)
        lesson = self.client.get(f'/api/lessons/{self.lesson.pk}/').data
        self.assertEqual([a['after_section'] for a in lesson['attachments']], ['Renamed', 'Renamed'])
        self.assertEqual(lesson['learning_content']['source_sections'][0], 'Renamed')
        # Replay/stale editor must not overwrite the new anchor.
        self.assertEqual(self.client.patch(self.url, self.payload, format='json').status_code, 400)

    def test_ambiguous_or_conflicting_rename_is_atomic(self):
        for target in ['Second', 'Explanation', '']:
            payload = deepcopy(self.payload)
            payload['section_renames'][0]['to_title'] = target
            self.assertEqual(self.client.patch(self.url, payload, format='json').status_code, 400)
        self.lesson.refresh_from_db()
        self.assertIn('First', self.lesson.text_content)
        self.assertEqual(list(self.lesson.attachments.values_list('after_section', flat=True)), ['First', 'First'])

    def test_duplicate_body_heading_rejected(self):
        self.lesson.text_content += '\n\nFirst'
        self.lesson.save()
        self.assertEqual(self.client.patch(self.url, self.payload, format='json').status_code, 400)

    def test_unresolved_attachment_preserved_and_target_collision_rejected(self):
        asset = self.assets[0]
        asset.after_section = 'Missing'
        asset.save()
        self.assertEqual(self.client.patch(self.url, self.payload, format='json').status_code, 200)
        asset.refresh_from_db()
        self.assertEqual(asset.after_section, 'Missing')

    def test_orphan_target_collision_rejected(self):
        self.assets[0].after_section = 'Renamed'
        self.assets[0].save()
        self.assertEqual(self.client.patch(self.url, self.payload, format='json').status_code, 400)
        self.lesson.refresh_from_db()
        self.assertTrue(self.lesson.text_content.startswith('First'))

    def test_image_placement_preserved_and_missing_mapping_rejected(self):
        image = LessonImage.objects.create(lesson=self.lesson, image='private/fixture.png')
        placement = {'type': 'image_placement', 'image_id': image.pk, 'after_section': 'First', 'caption': 'Original diagram'}
        self.learning.interactions = [placement]
        self.learning.save()
        self.assertEqual(self.client.patch(self.url, self.payload, format='json').status_code, 400)
        self.payload['learning_content']['interactions'] = [{**placement, 'after_section': 'Renamed'}]
        self.assertEqual(self.client.patch(self.url, self.payload, format='json').status_code, 200)
        self.learning.refresh_from_db()
        self.assertEqual(self.learning.interactions, [{**placement, 'after_section': 'Renamed'}])

    def test_unchanged_unresolved_image_placement_is_not_silently_repaired(self):
        image = LessonImage.objects.create(lesson=self.lesson, image='private/orphan.png')
        placement = {'type': 'image_placement', 'image_id': image.pk, 'after_section': 'Missing', 'caption': 'Orphan diagram'}
        self.learning.interactions = [placement]
        self.learning.save()
        self.payload['learning_content']['interactions'] = [placement]
        self.assertEqual(self.client.patch(self.url, self.payload, format='json').status_code, 200)
        self.learning.refresh_from_db()
        self.assertEqual(self.learning.interactions, [placement])

    def test_rollback_including_content_if_attachment_update_fails(self):
        with patch('django.db.models.query.QuerySet.update', side_effect=RuntimeError('fixture failure')):
            with self.assertRaises(RuntimeError):
                self.client.patch(self.url, self.payload, format='json')
        self.lesson.refresh_from_db()
        self.assertTrue(self.lesson.text_content.startswith('First'))
        self.learning.refresh_from_db()
        self.assertEqual(self.learning.source_sections, ['First', 'Second'])

    def test_plain_lesson_save_and_permissions(self):
        self.learning.delete()
        self.assertEqual(self.client.patch(self.url, {'text_content': 'Plain'}, format='json').status_code, 200)
        student = get_user_model().objects.create_user(username='section-student')
        self.client.force_authenticate(student)
        self.assertEqual(self.client.patch(self.url, self.payload, format='json').status_code, 403)
        other = get_user_model().objects.create_user(username='section-other', role='author')
        self.client.force_authenticate(other)
        self.assertEqual(self.client.patch(self.url, self.payload, format='json').status_code, 404)
        self.client.force_authenticate(self.owner)
        self.course.is_published = True
        self.course.save()
        self.assertEqual(self.client.patch(self.url, self.payload, format='json').status_code, 400)
