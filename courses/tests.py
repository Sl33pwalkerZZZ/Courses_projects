from datetime import timedelta

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from progress.models import Enrollment, LessonProgress

from .models import Course, Direction, Lesson, Module


class LessonCompletionStateTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.student = User.objects.create_user(username="student")
        cls.other = User.objects.create_user(username="other")
        direction = Direction.objects.create(name="AI", slug="ai")
        cls.course = Course.objects.create(
            title="AI", slug="ai", description="", direction=direction,
            author=cls.other, is_published=True,
        )
        module = Module.objects.create(course=cls.course, title="Introduction", order=1)
        cls.lesson = Lesson.objects.create(module=module, title="First lesson", text_content="", order=1)
        cls.enrollment = Enrollment.objects.create(student=cls.student, course=cls.course)
        cls.other_enrollment = Enrollment.objects.create(student=cls.other, course=cls.course)
        cls.url = reverse("lesson-detail", args=[cls.lesson.pk])
        cls.complete_url = reverse("lesson-complete", args=[cls.lesson.pk])

    def setUp(self):
        self.client.force_authenticate(self.student)

    def test_unstarted_lesson_returns_null_completion(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.data["completed_at"])
        self.assertTrue({"images", "assignments", "course_slug", "text_content"}.issubset(response.data))

    def test_uncompleted_progress_row_returns_null(self):
        LessonProgress.objects.create(enrollment=self.enrollment, lesson=self.lesson)
        self.assertIsNone(self.client.get(self.url).data["completed_at"])

    def test_completion_is_restored_by_subsequent_get_and_updates_profile(self):
        completed = self.client.post(self.complete_url)
        self.assertEqual(completed.status_code, 200)
        reloaded = self.client.get(self.url)
        self.assertEqual(reloaded.status_code, 200)
        self.assertIsNotNone(reloaded.data["completed_at"])
        self.assertEqual(
            reloaded.data["completed_at"], completed.data["completed_at"].isoformat().replace("+00:00", "Z"),
        )
        summary = self.client.get(reverse("my-enrollments")).data[0]
        self.assertEqual(summary["completed_lessons"], 1)
        self.assertTrue(summary["is_completed"])

    def test_another_students_completion_is_not_exposed(self):
        LessonProgress.objects.create(
            enrollment=self.other_enrollment, lesson=self.lesson, completed_at=timezone.now(),
        )
        self.assertIsNone(self.client.get(self.url).data["completed_at"])

    def test_progress_from_another_course_does_not_mark_this_lesson_completed(self):
        other_course = Course.objects.create(
            title="Other", slug="other", description="", direction=self.course.direction,
            author=self.other, is_published=True,
        )
        wrong_enrollment = Enrollment.objects.create(student=self.student, course=other_course)
        LessonProgress.objects.create(
            enrollment=wrong_enrollment, lesson=self.lesson, completed_at=timezone.now(),
        )
        self.assertIsNone(self.client.get(self.url).data["completed_at"])

    def test_unauthenticated_requests_cannot_read_or_complete(self):
        self.client.force_authenticate(None)
        self.assertEqual(self.client.get(self.url).status_code, 401)
        self.assertEqual(self.client.post(self.complete_url).status_code, 401)
        self.assertFalse(LessonProgress.objects.exists())

    def test_non_enrolled_requests_cannot_read_or_complete(self):
        Enrollment.objects.filter(pk=self.enrollment.pk).delete()
        self.assertEqual(self.client.get(self.url).status_code, 403)
        self.assertEqual(self.client.post(self.complete_url).status_code, 403)
        self.assertFalse(LessonProgress.objects.exists())

    def test_existing_refresh_endpoint_recovers_expired_lesson_access(self):
        refresh = RefreshToken.for_user(self.student)
        expired_access = AccessToken.for_user(self.student)
        expired_access.set_exp(from_time=timezone.now() - timedelta(hours=1), lifetime=timedelta(seconds=1))
        self.client.force_authenticate(None)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {expired_access}")
        self.assertEqual(self.client.get(self.url).status_code, 401)

        self.client.credentials()
        refreshed = self.client.post(reverse("token_refresh"), {"refresh": str(refresh)}, format="json")
        self.assertEqual(refreshed.status_code, 200)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refreshed.data['access']}")
        self.assertEqual(self.client.get(self.url).status_code, 200)
