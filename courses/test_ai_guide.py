import json
import os
from tempfile import TemporaryDirectory
from pathlib import Path
from unittest.mock import patch, MagicMock
from urllib.error import HTTPError, URLError

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import SimpleTestCase, override_settings
from django.urls import reverse
from rest_framework.test import APITestCase

from progress.models import Enrollment
from .ai_guide import environment_value, generate_answer, GuideUnavailable, MAX_CONTEXT_CHARS
from .models import Course, Direction, Module, Lesson


class GuideAPITests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.author = User.objects.create_user(username='guide-author', role='author')
        cls.student = User.objects.create_user(username='guide-student')
        cls.other = User.objects.create_user(username='guide-other')
        direction = Direction.objects.create(name='Guide', slug='guide')
        cls.course = Course.objects.create(title='Guide', slug='guide', direction=direction, author=cls.author)
        module = Module.objects.create(title='Module', course=cls.course, order=1)
        cls.lesson = Lesson.objects.create(module=module, title='Safe title', text_content='Safe lesson', order=1)
        Enrollment.objects.create(student=cls.student, course=cls.course)

    def setUp(self):
        cache.clear()
        self.client.force_authenticate(self.student)
        self.url = reverse('ai-guide')
        self.payload = {'lesson_id': self.lesson.pk, 'question': 'Explain this', 'language': 'en'}

    @patch('courses.ai_guide_views.generate_answer', return_value='Explanation')
    def test_enrolled_draft_access_and_private_answer(self, provider):
        response = self.client.post(self.url, self.payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {'answer': 'Explanation'})
        self.assertEqual(response['Cache-Control'], 'private, no-store')
        self.assertIn('Authorization', response['Vary'])
        self.assertEqual(provider.call_args.args[0].pk, self.lesson.pk)
        self.assertFalse(Course.objects.get(pk=self.course.pk).is_published)

    def test_guide_endpoint_does_not_shadow_course_slug(self):
        self.course.slug = 'ai-guide'
        self.course.is_published = True
        self.course.save(update_fields=['slug', 'is_published'])
        self.client.force_authenticate(None)
        response = self.client.get('/api/courses/ai-guide/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['id'], self.course.pk)

    @patch('courses.ai_guide_views.generate_answer', return_value='Hint')
    def test_author_uses_same_lesson_preview_permission(self, provider):
        self.client.force_authenticate(self.author)
        self.assertEqual(self.client.post(self.url, self.payload).status_code, 200)

    @patch('courses.ai_guide_views.generate_answer')
    def test_unauthorized_has_no_provider_call(self, provider):
        self.client.force_authenticate(self.other)
        self.assertEqual(self.client.post(self.url, self.payload).status_code, 403)
        provider.assert_not_called()

    @patch('courses.ai_guide_views.generate_answer')
    def test_anonymous_denied(self, provider):
        self.client.force_authenticate(None)
        self.assertEqual(self.client.post(self.url, self.payload).status_code, 401)
        provider.assert_not_called()

    @patch('courses.ai_guide_views.generate_answer')
    def test_inactive_denied(self, provider):
        self.student.is_active = False
        self.assertEqual(self.client.post(self.url, self.payload).status_code, 403)
        provider.assert_not_called()

    @patch('courses.ai_guide_views.generate_answer')
    def test_validation_and_missing_lesson(self, provider):
        for fields in ({'question': ' '}, {'question': 'x' * 2001}, {'language': 'de'}, {'lesson_id': -1}):
            with self.subTest(fields=fields):
                self.assertEqual(self.client.post(self.url, {**self.payload, **fields}).status_code, 400)
        self.assertEqual(self.client.post(self.url, {**self.payload, 'lesson_id': 999999}).status_code, 404)
        provider.assert_not_called()

    @patch('courses.ai_guide_views.generate_answer', return_value='Hint')
    def test_each_supported_language(self, provider):
        for language in ['ru', 'kk', 'en']:
            self.assertEqual(self.client.post(self.url, {**self.payload, 'language': language}).status_code, 200)
            self.assertEqual(provider.call_args.args[2], language)

    @patch('courses.ai_guide_views.generate_answer', return_value='Hint')
    def test_user_rate_limit(self, provider):
        for _ in range(12):
            self.assertEqual(self.client.post(self.url, self.payload).status_code, 200)
        self.assertEqual(self.client.post(self.url, self.payload).status_code, 429)
        self.assertEqual(provider.call_count, 12)

    @patch('courses.ai_guide_views.generate_answer', side_effect=GuideUnavailable('guide_timeout', 504))
    def test_sanitized_provider_failure(self, provider):
        response = self.client.post(self.url, self.payload)
        self.assertEqual(response.status_code, 504)
        self.assertEqual(response.data, {'code': 'guide_timeout'})


class GuideClientTests(SimpleTestCase):
    def setUp(self):
        self.environment = patch.dict(os.environ, {'GROQ_API_KEY': 'synthetic-key', 'GROQ_MODEL': 'openai/gpt-oss-20b'})
        self.environment.start()
        self.addCleanup(self.environment.stop)
        self.lesson = Lesson(title='Current', text_content='Educational context')

    @patch('courses.ai_guide.urlopen')
    def test_provider_payload_uses_only_allowed_context_and_hides_reasoning(self, open_url):
        response = MagicMock()
        response.read.return_value = json.dumps({'choices': [{'message': {'content': 'Answer', 'reasoning': 'private'}}]}).encode()
        open_url.return_value.__enter__.return_value = response
        self.lesson.text_content = 'x' * (MAX_CONTEXT_CHARS + 1000)
        self.lesson.private_notes = 'PRIVATE_NOTES'
        self.assertEqual(generate_answer(self.lesson, 'Question', 'kk'), 'Answer')
        request = open_url.call_args.args[0]
        payload = json.loads(request.data)
        self.assertEqual(request.get_header('User-agent'), 'AI-Courses-Guide/1.0')
        self.assertEqual(open_url.call_args.kwargs['timeout'], 25)
        self.assertEqual(payload['model'], 'openai/gpt-oss-20b')
        self.assertFalse(payload['include_reasoning'])
        self.assertIn('Kazakh', payload['messages'][0]['content'])
        self.assertIn('general model knowledge', payload['messages'][0]['content'])
        self.assertIn('quiz answer keys', payload['messages'][0]['content'])
        self.assertNotIn('PRIVATE_NOTES', str(payload))
        self.assertNotIn('synthetic-key', str(payload))
        self.assertLess(len(payload['messages'][1]['content']), MAX_CONTEXT_CHARS + 100)

    def test_missing_key(self):
        with patch('courses.ai_guide.environment_value', return_value=''):
            with self.assertRaises(GuideUnavailable) as caught:
                generate_answer(self.lesson, 'Question', 'ru')
        self.assertEqual(caught.exception.code, 'guide_not_configured')

    @patch('courses.ai_guide.urlopen')
    def test_provider_errors_are_sanitized(self, open_url):
        for error, code, status in [
            (HTTPError('https://provider', 429, 'sensitive body', {}, None), 'guide_rate_limited', 429),
            (HTTPError('https://provider', 401, 'sensitive key', {}, None), 'guide_provider_error', 502),
            (URLError('sensitive network info'), 'guide_provider_error', 502),
            (URLError(TimeoutError('private timeout')), 'guide_timeout', 504),
            (TimeoutError('private'), 'guide_timeout', 504),
        ]:
            open_url.side_effect = error
            with self.assertRaises(GuideUnavailable) as caught:
                generate_answer(self.lesson, 'Question', 'ru')
            self.assertEqual((str(caught.exception), caught.exception.status), (code, status))

    @patch('courses.ai_guide.urlopen')
    def test_malformed_empty_and_oversized_provider_answers(self, open_url):
        for raw in [b'not json', b'{}', b'{"choices": [{"message": {"content": ""}}]}', b'x' * 100001]:
            response = MagicMock()
            response.read.return_value = raw
            open_url.return_value.__enter__.return_value = response
            with self.assertRaises(GuideUnavailable):
                generate_answer(self.lesson, 'Question', 'en')

    def test_allowlisted_dotenv_and_environment_precedence(self):
        with TemporaryDirectory() as directory, override_settings(BASE_DIR=Path(directory)):
            (Path(directory) / '.env').write_text('GROQ_API_KEY="local-synthetic"\nGROQ_MODEL=openai/gpt-oss-20b\nOTHER=private\n')
            self.assertEqual(environment_value('GROQ_API_KEY'), 'synthetic-key')
            with patch.dict(os.environ, {}, clear=True):
                self.assertEqual(environment_value('GROQ_API_KEY'), 'local-synthetic')
                self.assertEqual(environment_value('GROQ_MODEL'), 'openai/gpt-oss-20b')
            with self.assertRaises(ValueError):
                environment_value('OTHER')
