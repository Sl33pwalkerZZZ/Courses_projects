"""Cache boundaries for public and authorized unpublished curricula."""
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase

from courses.models import Course, Direction, Module, Lesson
from progress.models import Enrollment


class CourseCacheTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.student = User.objects.create_user(username='cache-learner')
        cls.other = User.objects.create_user(username='cache-other')
        cls.author = User.objects.create_user(username='cache-author', role='author')
        direction = Direction.objects.create(name='Cache fixture', slug='cache-fixture')
        cls.public = Course.objects.create(title='Public', slug='cache-public', direction=direction,
            author=cls.author, is_published=True)
        cls.draft = Course.objects.create(title='Draft', slug='cache-draft', direction=direction,
            author=cls.author, is_published=False)
        module = Module.objects.create(course=cls.draft, title='Private curriculum', order=1)
        Lesson.objects.create(module=module, title='Private lesson', order=1)
        Enrollment.objects.create(student=cls.student, course=cls.draft)

    def detail(self, course):
        return self.client.get(reverse('course-detail', args=[course.slug]))

    def assert_private(self, response, status):
        self.assertEqual(response.status_code, status)
        self.assertEqual(response['Cache-Control'], 'private, no-store')
        self.assertTrue({'authorization', 'cookie'} <= {
            value.strip().lower() for value in response['Vary'].split(',')})

    def test_anonymous_public_detail_remains_public_variant(self):
        response = self.detail(self.public)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('Cache-Control', response)
        self.assertTrue({'authorization', 'cookie'} <= {
            value.strip().lower() for value in response['Vary'].split(',')})

    def test_authenticated_public_detail_is_not_stored(self):
        self.client.force_authenticate(self.student)
        self.assert_private(self.detail(self.public), 200)

    def test_enrolled_draft_is_not_stored(self):
        self.client.force_authenticate(self.student)
        response = self.detail(self.draft)
        self.assert_private(response, 200)
        self.assertEqual(len(response.data['modules'][0]['lessons']), 1)

    def test_owning_author_preview_is_not_stored(self):
        self.client.force_authenticate(self.author)
        self.assert_private(self.client.get(reverse('instructor-course-preview', args=[self.draft.slug])), 200)
        # Ownership alone does not grant access via the learner endpoint.
        self.assert_private(self.detail(self.draft), 404)

    def test_unauthorized_draft_and_preview_are_not_stored(self):
        self.client.force_authenticate(self.other)
        self.assert_private(self.detail(self.draft), 404)
        self.assert_private(self.client.get(reverse('instructor-course-preview', args=[self.draft.slug])), 403)

    def test_account_switch_and_logout_do_not_disclose_draft(self):
        self.client.force_authenticate(self.student)
        self.assert_private(self.detail(self.draft), 200)
        self.client.force_authenticate(self.other)
        self.assert_private(self.detail(self.draft), 404)
        self.client.force_authenticate(None)
        self.assert_private(self.detail(self.draft), 404)

    def test_invalid_credentials_are_not_stored(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer invalid-test-token')
        self.assert_private(self.detail(self.public), 401)

    def test_head_has_same_private_policy(self):
        self.client.force_authenticate(self.student)
        self.assert_private(self.client.head(reverse('course-detail', args=[self.draft.slug])), 200)
