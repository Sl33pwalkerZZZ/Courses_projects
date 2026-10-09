from datetime import datetime, timedelta, timezone as dt_timezone
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.db import connection
from django.test import override_settings
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from courses.models import Course, Direction, Lesson, Module
from .models import Enrollment, LessonProgress


@override_settings(TIME_ZONE="UTC")
class LearningActivityTests(APITestCase):
    now = datetime(2026, 1, 1, 12, tzinfo=dt_timezone.utc)

    @classmethod
    def setUpTestData(cls):
        cls.student = get_user_model().objects.create_user(username="activity-student")
        cls.other = get_user_model().objects.create_user(username="activity-other")
        direction = Direction.objects.create(name="Activity test", slug="activity-test")
        cls.course = Course.objects.create(
            title="Test course", slug="activity-test", description="", direction=direction,
            author=cls.other, is_published=True,
        )
        cls.module = Module.objects.create(course=cls.course, title="Test module", order=1)
        cls.lessons = [Lesson.objects.create(module=cls.module, title=f"Lesson {index}", text_content="", order=index)
                       for index in range(8)]
        cls.enrollment = Enrollment.objects.create(student=cls.student, course=cls.course)
        cls.other_enrollment = Enrollment.objects.create(student=cls.other, course=cls.course)
        cls.url = reverse("my-activity")

    def setUp(self):
        self.client.force_authenticate(self.student)

    def complete(self, index, when, enrollment=None):
        return LessonProgress.objects.create(
            enrollment=enrollment or self.enrollment, lesson=self.lessons[index], completed_at=when,
        )

    def activity(self, now=None, query=""):
        with patch("progress.activity.timezone.now", return_value=now or self.now):
            response = self.client.get(self.url + query)
        self.assertEqual(response.status_code, 200)
        return response.data

    def counts(self, data):
        return {day["date"]: day["count"] for day in data["daily_counts"]}

    def test_anonymous_receives_401(self):
        self.client.force_authenticate(None)
        self.assertEqual(self.client.get(self.url).status_code, 401)

    def test_expired_jwt_recovers_through_the_existing_refresh_endpoint(self):
        refresh = RefreshToken.for_user(self.student)
        access = AccessToken.for_user(self.student)
        access.set_exp(from_time=timezone.now() - timedelta(hours=1), lifetime=timedelta(seconds=1))
        self.client.force_authenticate(None)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        self.assertEqual(self.client.get(self.url).status_code, 401)
        self.client.credentials()
        response = self.client.post(reverse("token_refresh"), {"refresh": str(refresh)}, format="json")
        self.assertEqual(response.status_code, 200)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")
        self.assertEqual(self.client.get(self.url).status_code, 200)

    def test_only_requesting_student_is_counted_even_with_identity_parameters(self):
        self.complete(0, self.now)
        self.complete(1, self.now, self.other_enrollment)
        self.complete(2, self.now - timedelta(days=1), self.other_enrollment)
        data = self.activity(query=f"?student={self.other.pk}&user_id={self.other.pk}")
        self.assertEqual(data["total_completed_lessons"], 1)
        self.client.force_authenticate(self.other)
        self.assertEqual(self.activity()["total_completed_lessons"], 2)

    def test_zero_activity_includes_365_chronological_zero_days(self):
        data = self.activity()
        self.assertEqual(set(data), {
            "timezone", "start_date", "end_date", "total_completed_lessons",
            "active_days_last_365", "current_streak_days", "daily_counts",
        })
        self.assertEqual(data["timezone"], "UTC")
        self.assertEqual(data["start_date"], "2025-01-02")
        self.assertEqual(data["end_date"], "2026-01-01")
        self.assertEqual(len(data["daily_counts"]), 365)
        self.assertTrue(all(day["count"] == 0 for day in data["daily_counts"]))
        self.assertEqual(data["total_completed_lessons"], 0)
        self.assertEqual(data["active_days_last_365"], 0)
        self.assertEqual(data["current_streak_days"], 0)

    def test_multiple_completions_same_day_count_lessons_once_and_one_active_day(self):
        self.complete(0, self.now)
        self.complete(1, self.now - timedelta(hours=1))
        data = self.activity()
        self.assertEqual(self.counts(data)["2026-01-01"], 2)
        self.assertEqual(data["total_completed_lessons"], 2)
        self.assertEqual(data["active_days_last_365"], 1)
        self.assertEqual(data["current_streak_days"], 1)

    def test_calendar_crosses_month_and_year_boundaries(self):
        for index, days in enumerate([0, 1, 2, 32]):
            self.complete(index, self.now - timedelta(days=days))
        data = self.activity()
        for date in ["2026-01-01", "2025-12-31", "2025-12-30", "2025-11-30"]:
            self.assertEqual(self.counts(data)[date], 1)
        self.assertEqual(data["active_days_last_365"], 4)

    def test_all_time_totals_include_history_outside_calendar(self):
        self.complete(0, self.now - timedelta(days=365))
        self.complete(1, self.now - timedelta(days=700))
        self.complete(2, self.now)
        data = self.activity()
        self.assertEqual(data["total_completed_lessons"], 3)
        self.assertEqual(sum(self.counts(data).values()), 1)
        self.assertEqual(data["active_days_last_365"], 1)

    def test_start_midnight_included_and_previous_second_excluded(self):
        start = (self.now - timedelta(days=364)).replace(hour=0)
        self.complete(0, start)
        self.complete(1, start - timedelta(seconds=1))
        data = self.activity()
        self.assertEqual(self.counts(data)["2025-01-02"], 1)
        self.assertEqual(data["total_completed_lessons"], 2)
        self.assertEqual(data["active_days_last_365"], 1)

    def test_completions_across_enrolled_courses_share_the_daily_total(self):
        course = Course.objects.create(
            title="Second course", slug="activity-second", description="", direction=self.course.direction,
            author=self.other,
        )
        module = Module.objects.create(course=course, title="Second module", order=1)
        lesson = Lesson.objects.create(module=module, title="Second course lesson", text_content="", order=1)
        enrollment = Enrollment.objects.create(student=self.student, course=course)
        LessonProgress.objects.create(enrollment=enrollment, lesson=lesson, completed_at=self.now)
        self.complete(0, self.now)
        data = self.activity()
        self.assertEqual(data["total_completed_lessons"], 2)
        self.assertEqual(self.counts(data)["2026-01-01"], 2)

    def test_unfinished_and_future_progress_are_not_activity(self):
        LessonProgress.objects.create(enrollment=self.enrollment, lesson=self.lessons[0])
        self.complete(1, self.now + timedelta(days=1))
        self.complete(2, self.now + timedelta(seconds=1))
        data = self.activity()
        self.assertEqual(data["total_completed_lessons"], 0)
        self.assertEqual(data["active_days_last_365"], 0)

    def test_malformed_foreign_course_progress_is_excluded(self):
        other_course = Course.objects.create(
            title="Other", slug="activity-other", description="", direction=self.course.direction,
            author=self.other,
        )
        wrong_enrollment = Enrollment.objects.create(student=self.student, course=other_course)
        self.complete(0, self.now, wrong_enrollment)
        self.assertEqual(self.activity()["total_completed_lessons"], 0)

    def test_streak_through_today(self):
        for index, days in enumerate([0, 1, 2, 4]):
            self.complete(index, self.now - timedelta(days=days))
        self.assertEqual(self.activity()["current_streak_days"], 3)

    def test_yesterday_keeps_streak_when_today_is_not_yet_active(self):
        for index, days in enumerate([1, 2, 3]):
            self.complete(index, self.now - timedelta(days=days))
        self.assertEqual(self.activity()["current_streak_days"], 3)

    def test_older_activity_has_zero_current_streak(self):
        self.complete(0, self.now - timedelta(days=2))
        self.assertEqual(self.activity()["current_streak_days"], 0)

    def test_streak_is_not_capped_at_365_days(self):
        lessons = Lesson.objects.bulk_create([
            Lesson(module=self.module, title=f"Streak lesson {index}", text_content="", order=index + 10)
            for index in range(370)
        ])
        LessonProgress.objects.bulk_create([
            LessonProgress(enrollment=self.enrollment, lesson=lesson, completed_at=self.now - timedelta(days=index))
            for index, lesson in enumerate(lessons)
        ])
        data = self.activity()
        self.assertEqual(data["current_streak_days"], 370)
        self.assertEqual(data["active_days_last_365"], 365)
        self.assertEqual(data["total_completed_lessons"], 370)

    def test_leap_day_is_included_in_exact_365_day_window(self):
        leap_now = datetime(2024, 3, 1, 12, tzinfo=dt_timezone.utc)
        self.complete(0, datetime(2024, 2, 29, 23, tzinfo=dt_timezone.utc))
        data = self.activity(now=leap_now)
        self.assertEqual(len(data["daily_counts"]), 365)
        self.assertEqual(self.counts(data)["2024-02-29"], 1)
        self.assertEqual(data["current_streak_days"], 1)

    @override_settings(TIME_ZONE="Asia/Almaty")
    def test_configured_timezone_groups_midnight_and_streak_consistently(self):
        now = datetime(2026, 1, 1, 19, 30, tzinfo=dt_timezone.utc)
        self.complete(0, datetime(2026, 1, 1, 19, 5, tzinfo=dt_timezone.utc))
        self.complete(1, datetime(2026, 1, 1, 18, 59, tzinfo=dt_timezone.utc))
        data = self.activity(now=now)
        self.assertEqual(data["timezone"], "Asia/Almaty")
        self.assertEqual(data["end_date"], "2026-01-02")
        self.assertEqual(self.counts(data)["2026-01-02"], 1)
        self.assertEqual(self.counts(data)["2026-01-01"], 1)
        self.assertEqual(data["current_streak_days"], 2)

    def test_activity_is_read_only_and_does_not_leak_course_content(self):
        self.complete(0, self.now)
        models = [Course, Module, Lesson, Enrollment, LessonProgress]
        before = [list(model.objects.order_by("pk").values()) for model in models]
        data = self.activity()
        self.assertEqual(before, [list(model.objects.order_by("pk").values()) for model in models])
        self.assertNotIn("Test course", str(data))
        self.assertNotIn("lesson_id", str(data))

    def test_aggregation_uses_one_query_even_with_many_calendar_days(self):
        self.complete(0, self.now)
        with CaptureQueriesContext(connection) as queries:
            self.activity()
        self.assertEqual(len(queries), 1)

    def test_repeated_completion_preserves_timestamp_and_does_not_add_activity(self):
        original = self.now - timedelta(days=1)
        progress = self.complete(0, original)
        complete_url = reverse("lesson-complete", args=[self.lessons[0].pk])
        with patch("progress.views.timezone.now", return_value=self.now):
            first = self.client.post(complete_url)
            second = self.client.post(complete_url)
        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 200)
        self.assertEqual(first.data["completed_at"], original)
        self.assertEqual(second.data["completed_at"], original)
        progress.refresh_from_db()
        self.assertEqual(progress.completed_at, original)
        self.assertEqual(LessonProgress.objects.count(), 1)
        data = self.activity()
        self.assertEqual(data["total_completed_lessons"], 1)
        self.assertEqual(self.counts(data)["2026-01-01"], 0)
        self.assertEqual(self.counts(data)["2025-12-31"], 1)

    def test_null_progress_receives_first_completion_timestamp(self):
        progress = LessonProgress.objects.create(enrollment=self.enrollment, lesson=self.lessons[0])
        with patch("progress.views.timezone.now", return_value=self.now):
            response = self.client.post(reverse("lesson-complete", args=[self.lessons[0].pk]))
        self.assertEqual(response.status_code, 200)
        progress.refresh_from_db()
        self.assertEqual(progress.completed_at, self.now)
