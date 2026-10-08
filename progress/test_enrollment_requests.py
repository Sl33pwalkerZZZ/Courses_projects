from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import IntegrityError, transaction
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase

from courses.models import Assignment, Course, Direction, Lesson, Module

from .models import Enrollment, EnrollmentRequest, LessonProgress
from .services import review_enrollment_request, submit_enrollment_request


class EnrollmentRequestTests(APITestCase):
    """All users and curriculum here exist only in Django's temporary test database."""

    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.student = User.objects.create_user(username="student")
        cls.other = User.objects.create_user(username="other")
        cls.author = User.objects.create_user(username="author", role=User.Role.AUTHOR)
        cls.admin = User.objects.create_user(username="administrator", is_staff=True, is_superuser=True)
        cls.staff = User.objects.create_user(username="reviewer", is_staff=True)
        direction = Direction.objects.create(name="Test direction", slug="test-direction")
        cls.course = Course.objects.create(
            title="Existing course", slug="existing-course", description="Public description",
            direction=direction, author=cls.author, is_published=True,
        )
        module = Module.objects.create(course=cls.course, title="Public module title", order=1)
        cls.lesson = Lesson.objects.create(
            module=module, title="Public lesson title", order=1, text_content="Protected lesson body",
        )
        Assignment.objects.create(lesson=cls.lesson, type="text", description="Protected assignment")
        cls.message = "I want to study this topic for my next project."
        cls.apply_url = reverse("course-enrollment-requests", args=[cls.course.slug])
        cls.requests_url = reverse("my-enrollment-requests")
        cls.enroll_url = reverse("course-enroll", args=[cls.course.slug])
        cls.lesson_url = reverse("lesson-detail", args=[cls.lesson.pk])
        cls.complete_url = reverse("lesson-complete", args=[cls.lesson.pk])

    def setUp(self):
        self.client.force_authenticate(self.student)

    def apply(self, **extra):
        return self.client.post(self.apply_url, {"message": self.message, **extra}, format="json")

    def application(self, student=None):
        return submit_enrollment_request(student=student or self.student, course=self.course, message=self.message)

    def review(self, application, approve=True, note=""):
        return review_enrollment_request(
            application_id=application.pk, reviewer=self.admin, approve=approve, note=note,
        )

    def test_authenticated_submission_defaults_to_pending_without_granting_access(self):
        self.assertEqual(self.course.enrollment_mode, Course.EnrollmentMode.APPROVAL)
        response = self.apply(message=f"  {self.message}  ")
        self.assertEqual(response.status_code, 201)
        application = EnrollmentRequest.objects.get(pk=response.data["id"])
        self.assertEqual(application.student, self.student)
        self.assertEqual(application.course, self.course)
        self.assertEqual(application.message, self.message)
        self.assertEqual(application.status, EnrollmentRequest.Status.PENDING)
        self.assertIsNone(application.reviewed_at)
        self.assertIsNone(application.reviewed_by)
        self.assertFalse(Enrollment.objects.exists())
        self.assertEqual(response.data["course"]["enrollment_mode"], "approval")

    def test_anonymous_visitors_can_preview_but_cannot_apply_or_list_requests(self):
        self.client.force_authenticate(None)
        self.assertEqual(self.apply().status_code, 401)
        self.assertEqual(self.client.get(self.requests_url).status_code, 401)
        self.assertEqual(self.client.post(self.enroll_url).status_code, 401)
        self.assertEqual(self.client.get(reverse("course-list")).status_code, 200)
        self.assertEqual(self.client.get(reverse("course-detail", args=[self.course.slug])).status_code, 200)
        self.assertFalse(EnrollmentRequest.objects.exists())

    def test_invalid_messages_are_rejected_before_writing(self):
        for message in ("", " " * 30, "a" * 19, "a" * 1001, None, [], " " * 20 + "short"):
            with self.subTest(message=message):
                response = self.apply(message=message)
                self.assertEqual(response.status_code, 400)
                self.assertIn("message", response.data)
        self.assertEqual(self.client.post(self.apply_url, {}, format="json").status_code, 400)
        self.assertFalse(EnrollmentRequest.objects.exists())

    def test_message_length_boundaries_are_accepted(self):
        for student, length in ((self.student, 20), (self.other, 1000)):
            self.client.force_authenticate(student)
            self.assertEqual(self.apply(message="a" * length).status_code, 201)

    def test_students_cannot_submit_server_controlled_fields(self):
        for field, value in (
            ("status", "approved"), ("student", self.other.pk), ("course", self.course.pk),
            ("reviewed_by", self.admin.pk), ("reviewed_at", timezone.now().isoformat()),
            ("admin_note", "Grant access"),
        ):
            with self.subTest(field=field):
                response = self.apply(**{field: value})
                self.assertEqual(response.status_code, 400)
                self.assertIn(field, response.data)
        self.assertFalse(EnrollmentRequest.objects.exists())

    def test_missing_or_unpublished_course_returns_404(self):
        missing = reverse("course-enrollment-requests", args=["missing"])
        self.assertEqual(self.client.post(missing, {"message": self.message}, format="json").status_code, 404)
        self.course.is_published = False
        self.course.save(update_fields=["is_published"])
        self.assertEqual(self.apply().status_code, 404)

    def test_duplicate_pending_application_returns_conflict(self):
        self.assertEqual(self.apply().status_code, 201)
        duplicate = self.apply()
        self.assertEqual(duplicate.status_code, 409)
        self.assertEqual(duplicate.data["code"], "duplicate_pending")
        self.assertEqual(EnrollmentRequest.objects.count(), 1)

    def test_database_prevents_duplicate_pending_rows(self):
        self.application()
        with self.assertRaises(IntegrityError), transaction.atomic():
            EnrollmentRequest.objects.create(student=self.student, course=self.course, message=self.message)
        self.assertEqual(EnrollmentRequest.objects.count(), 1)

    def test_database_rejects_invalid_status_and_incomplete_decisions(self):
        for status in ("invalid", "approved", "rejected"):
            with self.subTest(status=status), self.assertRaises(IntegrityError), transaction.atomic():
                EnrollmentRequest.objects.create(
                    student=self.student, course=self.course, message=self.message, status=status,
                )
        self.assertFalse(EnrollmentRequest.objects.exists())

    def test_duplicate_race_returns_same_clear_conflict(self):
        self.application()
        with patch("progress.views.submit_enrollment_request", side_effect=IntegrityError):
            response = self.apply()
        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.data["code"], "duplicate_pending")

    def test_already_enrolled_students_cannot_apply(self):
        Enrollment.objects.create(student=self.student, course=self.course)
        response = self.apply()
        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.data["code"], "already_enrolled")
        with self.assertRaises(ValidationError):
            EnrollmentRequest(student=self.student, course=self.course, message=self.message).full_clean()
        self.assertFalse(EnrollmentRequest.objects.exists())

    def test_rejection_keeps_history_and_allows_a_new_pending_application(self):
        original = self.application()
        self.review(original, approve=False, note="Please describe a specific learning goal.")
        original.refresh_from_db()
        decision_time = original.reviewed_at
        response = self.apply()
        self.assertEqual(response.status_code, 201)
        self.assertNotEqual(response.data["id"], original.pk)
        self.assertEqual(response.data["status"], "pending")
        original.refresh_from_db()
        self.assertEqual(original.status, "rejected")
        self.assertEqual(original.reviewed_at, decision_time)
        self.assertEqual(original.admin_note, "Please describe a specific learning goal.")
        history = self.client.get(self.requests_url)
        self.assertEqual([row["status"] for row in history.data], ["pending", "rejected"])
        self.assertFalse(Enrollment.objects.exists())

    def test_approval_grants_access_and_preserves_progress_endpoints(self):
        application, changed = self.review(self.application())
        self.assertTrue(changed)
        self.assertEqual(application.status, "approved")
        self.assertEqual(application.reviewed_by, self.admin)
        self.assertIsNotNone(application.reviewed_at)
        self.assertEqual(Enrollment.objects.filter(student=self.student, course=self.course).count(), 1)
        body = self.client.get(self.lesson_url)
        self.assertEqual(body.status_code, 200)
        self.assertEqual(body.data["text_content"], "Protected lesson body")
        self.assertEqual(self.client.post(self.complete_url).status_code, 200)
        progress = self.client.get(reverse("my-enrollments")).data[0]
        self.assertEqual(progress["completed_lessons"], 1)
        self.assertTrue(progress["is_completed"])

    def test_approval_reuses_existing_enrollment(self):
        application = self.application()
        existing = Enrollment.objects.create(student=self.student, course=self.course)
        self.review(application)
        self.assertEqual(Enrollment.objects.get(student=self.student, course=self.course).pk, existing.pk)

    def test_repeated_or_opposite_decisions_cannot_replace_an_existing_decision(self):
        for student, approve in ((self.student, True), (self.other, False)):
            application, _ = self.review(self.application(student), approve=approve, note="Original decision")
            timestamp = application.reviewed_at
            for next_decision in (approve, not approve):
                repeated, changed = self.review(application, approve=next_decision, note="Changed decision")
                self.assertFalse(changed)
                self.assertEqual(repeated.status, "approved" if approve else "rejected")
                self.assertEqual(repeated.reviewed_at, timestamp)
                self.assertEqual(repeated.admin_note, "Original decision")
        self.assertEqual(Enrollment.objects.count(), 1)

    def test_failed_decision_write_rolls_back_enrollment_creation(self):
        application = self.application()
        with patch.object(EnrollmentRequest, "save", side_effect=RuntimeError("Write failed")):
            with self.assertRaises(RuntimeError):
                self.review(application)
        application.refresh_from_db()
        self.assertEqual(application.status, "pending")
        self.assertIsNone(application.reviewed_at)
        self.assertFalse(Enrollment.objects.exists())

    def test_review_requires_staff_permission_not_a_display_role(self):
        application = self.application()
        self.other.role = get_user_model().Role.ADMIN
        self.other.save(update_fields=["role"])
        for reviewer in (self.student, self.other, self.staff):
            with self.assertRaises(PermissionDenied):
                review_enrollment_request(application_id=application.pk, reviewer=reviewer, approve=True)
        self.staff.user_permissions.add(Permission.objects.get(
            content_type__app_label="progress", codename="change_enrollmentrequest",
        ))
        reviewer = get_user_model().objects.get(pk=self.staff.pk)
        reviewed, changed = review_enrollment_request(application_id=application.pk, reviewer=reviewer, approve=True)
        self.assertTrue(changed)
        self.assertEqual(reviewed.reviewed_by, reviewer)

    def test_request_list_is_owner_scoped_and_hides_draft_notes_and_reviewer_identity(self):
        own = self.application()
        own.admin_note = "Unfinished decision note"
        own.save(update_fields=["admin_note"])
        other = self.application(self.other)
        response = self.client.get(self.requests_url, {"student": self.other.pk})
        self.assertEqual(response.status_code, 200)
        self.assertEqual([row["id"] for row in response.data], [own.pk])
        self.assertEqual(response.data[0]["admin_note"], "")
        self.assertNotIn("student", response.data[0])
        self.assertNotIn("reviewed_by", response.data[0])
        self.review(own, approve=False, note="A permitted rejection explanation")
        self.assertEqual(self.client.get(self.requests_url).data[0]["admin_note"], "A permitted rejection explanation")
        self.client.force_authenticate(self.other)
        self.assertEqual([row["id"] for row in self.client.get(self.requests_url).data], [other.pk])
        self.assertEqual(self.client.patch(self.apply_url, {"status": "approved"}, format="json").status_code, 405)

    def test_approval_course_cannot_bypass_application_for_any_unapproved_state(self):
        self.assertEqual(self.client.post(self.enroll_url).status_code, 403)
        application = self.application()
        self.assertEqual(self.client.post(self.enroll_url).status_code, 403)
        self.review(application, approve=False)
        self.assertEqual(self.client.post(self.enroll_url).status_code, 403)
        self.assertFalse(Enrollment.objects.exists())

    def test_existing_enrollment_is_preserved_for_approval_courses(self):
        existing = Enrollment.objects.create(student=self.student, course=self.course)
        response = self.client.post(self.enroll_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], existing.pk)
        self.assertEqual(set(response.data), {"id", "course", "granted_at"})
        self.assertEqual(self.client.get(self.lesson_url).status_code, 200)

    def test_open_enrollment_remains_immediate_and_idempotent(self):
        self.course.enrollment_mode = Course.EnrollmentMode.OPEN
        self.course.save(update_fields=["enrollment_mode"])
        application = self.apply()
        self.assertEqual(application.status_code, 409)
        self.assertEqual(application.data["code"], "open_enrollment")
        self.assertEqual(self.client.post(self.enroll_url).status_code, 201)
        self.assertEqual(self.client.post(self.enroll_url).status_code, 200)
        self.assertEqual(Enrollment.objects.count(), 1)
        self.assertEqual(self.client.get(self.lesson_url).status_code, 200)
        self.assertFalse(EnrollmentRequest.objects.exists())

    def test_unapproved_students_cannot_read_or_complete_lessons(self):
        for state in ("not_applied", "pending", "rejected"):
            if state == "pending":
                application = self.application()
            elif state == "rejected":
                self.review(application, approve=False)
            with self.subTest(state=state):
                self.assertEqual(self.client.get(self.lesson_url).status_code, 403)
                self.assertEqual(self.client.post(self.complete_url).status_code, 403)
        self.client.force_authenticate(None)
        self.assertEqual(self.client.get(self.lesson_url).status_code, 401)
        self.assertEqual(self.client.post(self.complete_url).status_code, 401)
        self.assertFalse(LessonProgress.objects.exists())

    def test_staff_lesson_preview_requires_django_permission(self):
        self.client.force_authenticate(self.staff)
        self.assertEqual(self.client.get(self.lesson_url).status_code, 403)
        self.staff.user_permissions.add(Permission.objects.get(content_type__app_label="courses", codename="view_lesson"))
        self.client.force_authenticate(get_user_model().objects.get(pk=self.staff.pk))
        self.assertEqual(self.client.get(self.lesson_url).status_code, 200)
        # Previewing is not a personal enrollment and must not manufacture progress.
        self.assertEqual(self.client.post(self.complete_url).status_code, 403)
        self.client.force_authenticate(self.admin)
        self.assertEqual(self.client.get(self.lesson_url).status_code, 200)
        self.assertFalse(Enrollment.objects.exists())

    def test_public_curriculum_never_exposes_protected_lesson_material(self):
        self.client.force_authenticate(None)
        response = self.client.get(reverse("course-detail", args=[self.course.slug]))
        self.assertEqual(response.status_code, 200)
        preview = response.data["modules"][0]["lessons"][0]
        self.assertEqual(set(preview), {"id", "title", "order"})
        self.assertNotIn("Protected lesson body", response.content.decode())
        self.assertNotIn("Protected assignment", response.content.decode())

    def test_admin_change_form_approves_and_reuses_enrollment(self):
        application = self.application()
        enrollment = Enrollment.objects.create(student=self.student, course=self.course)
        self.client.force_login(self.admin)
        url = reverse("admin:progress_enrollmentrequest_change", args=[application.pk])
        page = self.client.get(url)
        self.assertContains(page, 'name="_approve"')
        self.assertContains(page, 'name="_reject"')
        decision = self.client.post(url, {"admin_note": "Welcome to the course.", "_approve": "Approve application"})
        self.assertEqual(decision.status_code, 302)
        application.refresh_from_db()
        self.assertEqual(application.status, "approved")
        self.assertEqual(application.reviewed_by, self.admin)
        self.assertEqual(application.admin_note, "Welcome to the course.")
        self.assertEqual(Enrollment.objects.get(student=self.student, course=self.course).pk, enrollment.pk)
        reviewed_page = self.client.get(url)
        self.assertNotContains(reviewed_page, 'name="_approve"')
        self.client.post(url, {"admin_note": "Replace decision", "_reject": "Reject application"})
        application.refresh_from_db()
        self.assertEqual(application.status, "approved")
        self.assertEqual(application.admin_note, "Welcome to the course.")

    def test_admin_rejection_saves_reason_and_student_can_reapply(self):
        application = self.application()
        self.client.force_login(self.admin)
        url = reverse("admin:progress_enrollmentrequest_change", args=[application.pk])
        response = self.client.post(url, {"admin_note": "Please clarify your goals.", "_reject": "Reject application"})
        self.assertEqual(response.status_code, 302)
        application.refresh_from_db()
        self.assertEqual(application.status, "rejected")
        self.assertEqual(application.admin_note, "Please clarify your goals.")
        self.assertIsNotNone(application.reviewed_at)
        self.assertFalse(Enrollment.objects.exists())
        self.assertEqual(self.apply().status_code, 201)
        self.assertEqual(EnrollmentRequest.objects.count(), 2)

    def test_admin_bulk_actions_skip_decided_applications(self):
        application = self.application()
        other = self.application(self.other)
        self.client.force_login(self.admin)
        url = reverse("admin:progress_enrollmentrequest_changelist")
        for _ in range(2):
            response = self.client.post(url, {"action": "approve_applications", "_selected_action": [application.pk]})
            self.assertEqual(response.status_code, 302)
        response = self.client.post(url, {
            "action": "reject_applications", "_selected_action": [application.pk, other.pk],
        })
        self.assertEqual(response.status_code, 302)
        application.refresh_from_db()
        other.refresh_from_db()
        self.assertEqual(application.status, "approved")
        self.assertEqual(other.status, "rejected")
        self.assertEqual(Enrollment.objects.count(), 1)

    def test_admin_view_permission_does_not_allow_decisions(self):
        application = self.application()
        self.staff.user_permissions.add(Permission.objects.get(
            content_type__app_label="progress", codename="view_enrollmentrequest",
        ))
        self.client.force_login(self.staff)
        url = reverse("admin:progress_enrollmentrequest_change", args=[application.pk])
        page = self.client.get(url)
        self.assertEqual(page.status_code, 200)
        self.assertNotContains(page, 'name="_approve"')
        self.assertEqual(self.client.post(url, {"_approve": "Approve application"}).status_code, 403)
        application.refresh_from_db()
        self.assertEqual(application.status, "pending")
        self.assertFalse(Enrollment.objects.exists())
