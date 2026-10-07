from django.contrib.auth import get_user_model
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase

from courses.models import Course, Direction, Lesson, Module

from .models import Enrollment, LessonProgress


class MyEnrollmentProgressTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.student = User.objects.create_user(username="student", email="student@example.com")
        cls.other_student = User.objects.create_user(username="other-student")
        cls.author = User.objects.create_user(username="author", role="author")
        cls.direction = Direction.objects.create(name="AI", slug="ai")
        cls.course = Course.objects.create(
            title="AI foundations", slug="ai-foundations", description="Learn AI",
            direction=cls.direction, author=cls.author, is_published=True,
        )
        # Creation order and lesson order differ from the course's curriculum order.
        later_module = Module.objects.create(course=cls.course, title="Later module", order=20)
        first_module = Module.objects.create(course=cls.course, title="First module", order=10)
        cls.last_lesson = Lesson.objects.create(
            module=later_module, title="Last lesson", text_content="", order=1,
        )
        cls.second_lesson = Lesson.objects.create(
            module=first_module, title="Second lesson", text_content="", order=20,
        )
        cls.first_lesson = Lesson.objects.create(
            module=first_module, title="First lesson", text_content="", order=10,
        )
        cls.enrollment = Enrollment.objects.create(student=cls.student, course=cls.course)
        cls.other_enrollment = Enrollment.objects.create(student=cls.other_student, course=cls.course)
        cls.empty_course = Course.objects.create(
            title="Coming soon", slug="coming-soon", description="",
            direction=cls.direction, author=cls.author, is_published=True,
        )
        cls.empty_enrollment = Enrollment.objects.create(student=cls.student, course=cls.empty_course)
        cls.url = reverse("my-enrollments")

    def setUp(self):
        self.client.force_authenticate(user=self.student)

    def enrollment_data(self, enrollment=None):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        target_id = (enrollment or self.enrollment).id
        return next(row for row in response.data if row["id"] == target_id)

    def complete(self, lesson, enrollment=None):
        return LessonProgress.objects.create(
            enrollment=enrollment or self.enrollment, lesson=lesson, completed_at=timezone.now(),
        )

    def test_requires_authentication_and_only_returns_the_current_students_enrollments(self):
        response = self.client.get(self.url)
        self.assertEqual({row["id"] for row in response.data}, {self.enrollment.id, self.empty_enrollment.id})
        self.client.force_authenticate(user=self.other_student)
        response = self.client.get(self.url)
        self.assertEqual([row["id"] for row in response.data], [self.other_enrollment.id])
        self.client.force_authenticate(user=None)
        self.assertEqual(self.client.get(self.url).status_code, 401)

    def test_response_shape_and_curriculum_order_for_an_unstarted_course(self):
        data = self.enrollment_data()
        self.assertEqual(set(data), {
            "id", "course", "granted_at", "total_lessons", "completed_lessons",
            "progress_percent", "is_completed", "next_lesson_id", "next_lesson_title",
        })
        self.assertEqual(data["course"]["slug"], self.course.slug)
        self.assertEqual(data["course"]["author"], self.author.username)
        self.assertIn("direction", data["course"])
        self.assertEqual(data["total_lessons"], 3)
        self.assertEqual(data["completed_lessons"], 0)
        self.assertEqual(data["progress_percent"], 0)
        self.assertFalse(data["is_completed"])
        self.assertEqual(data["next_lesson_id"], self.first_lesson.id)
        self.assertEqual(data["next_lesson_title"], self.first_lesson.title)

    def test_only_completed_rows_in_this_enrollment_and_course_are_counted(self):
        self.complete(self.first_lesson)
        LessonProgress.objects.create(enrollment=self.enrollment, lesson=self.second_lesson)
        self.complete(self.last_lesson, self.other_enrollment)
        foreign_module = Module.objects.create(course=self.empty_course, title="Other course", order=1)
        foreign_lesson = Lesson.objects.create(module=foreign_module, title="Foreign lesson", text_content="", order=1)
        self.complete(foreign_lesson)
        data = self.enrollment_data()
        self.assertEqual(data["total_lessons"], 3)
        self.assertEqual(data["completed_lessons"], 1)
        self.assertAlmostEqual(data["progress_percent"], 100 / 3)
        self.assertFalse(data["is_completed"])
        self.assertEqual(data["next_lesson_id"], self.second_lesson.id)

    def test_next_lesson_is_the_first_incomplete_even_if_later_lessons_are_completed(self):
        self.complete(self.last_lesson)
        data = self.enrollment_data()
        self.assertEqual(data["completed_lessons"], 1)
        self.assertEqual(data["next_lesson_id"], self.first_lesson.id)

    def test_empty_course_is_zero_percent_and_not_completed(self):
        self.complete(self.first_lesson, self.empty_enrollment)
        data = self.enrollment_data(self.empty_enrollment)
        self.assertEqual(data["total_lessons"], 0)
        self.assertEqual(data["completed_lessons"], 0)
        self.assertEqual(data["progress_percent"], 0)
        self.assertFalse(data["is_completed"])
        self.assertIsNone(data["next_lesson_id"])
        self.assertIsNone(data["next_lesson_title"])

    def test_existing_completion_endpoint_updates_the_summary_until_finished(self):
        for index, lesson in enumerate((self.first_lesson, self.second_lesson, self.last_lesson), start=1):
            response = self.client.post(reverse("lesson-complete", args=[lesson.id]))
            self.assertEqual(response.status_code, 200)
            data = self.enrollment_data()
            self.assertEqual(data["completed_lessons"], index)
            self.assertAlmostEqual(data["progress_percent"], index / 3 * 100)
            self.assertEqual(data["is_completed"], index == 3)
        self.assertIsNone(data["next_lesson_id"])
        self.assertIsNone(data["next_lesson_title"])

    def test_ordering_ties_are_resolved_consistently(self):
        tie_lesson = Lesson.objects.create(
            module=self.first_lesson.module, title="Same order", text_content="", order=self.first_lesson.order,
        )
        self.complete(self.first_lesson)
        self.assertEqual(self.enrollment_data()["next_lesson_id"], tie_lesson.id)

    def test_existing_enroll_post_response_is_unchanged(self):
        response = self.client.post(reverse("course-enroll", args=[self.course.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(set(response.data), {"id", "course", "granted_at"})

    def test_query_count_does_not_grow_with_enrollments(self):
        with CaptureQueriesContext(connection) as initial_queries:
            self.client.get(self.url)
        for index in range(3):
            course = Course.objects.create(
                title=f"Extra course {index}", slug=f"extra-{index}", description="",
                direction=self.direction, author=self.author, is_published=True,
            )
            module = Module.objects.create(course=course, title="Module", order=1)
            lesson = Lesson.objects.create(module=module, title="Lesson", text_content="", order=1)
            enrollment = Enrollment.objects.create(student=self.student, course=course)
            self.complete(lesson, enrollment)
        with CaptureQueriesContext(connection) as expanded_queries:
            response = self.client.get(self.url)
        self.assertEqual(len(response.data), 5)
        self.assertEqual(len(expanded_queries), len(initial_queries))
