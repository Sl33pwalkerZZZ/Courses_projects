from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.urls import reverse
from rest_framework.test import APITestCase

from courses.models import Assignment, Course, Direction, Lesson, Module
from .models import AssignmentSubmission, Enrollment, EnrollmentRequest, LessonProgress


def complete_map():
    return {
        "working_task": "Compare anonymized report summaries",
        "input_data": "Synthetic, anonymized sample only",
        "expected_result": "A short accurate summary",
        "required_capabilities": "Russian text summaries",
        "data_classification": "internal",
        "services": ["Service A", "Service B"],
        "comparison_criteria": {key: "Check with the same synthetic example" for key in (
            "quality", "features", "cost", "speed", "privacy", "ease",
        )},
        "testing_results": [{"service": name, "result": "Manual comparison observations"}
                            for name in ("Service A", "Service B")],
        "selected_service": "Service B", "final_justification": "Meets task and security requirements",
    }


class SelectionMapTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.student = User.objects.create_user(username="map-student")
        cls.other = User.objects.create_user(username="map-other")
        cls.author = User.objects.create_superuser(username="map-author", password="test-pass")
        direction = Direction.objects.create(name="Map direction", slug="map-direction")
        cls.course = Course.objects.create(title="Map course", slug="map-course", description="draft",
                                          author=cls.author, direction=direction, is_published=False)
        module = Module.objects.create(course=cls.course, title="Module", order=1)
        cls.lesson = Lesson.objects.create(module=module, title="Lesson", text_content="Read", order=1)
        cls.assignment = Assignment.objects.create(lesson=cls.lesson, type="text", description="Practice",
                                                   learning_activity="ai_selection_map")
        cls.legacy = Assignment.objects.create(lesson=cls.lesson, type="text", description="Legacy")
        Enrollment.objects.create(student=cls.student, course=cls.course)
        cls.url = reverse("selection-map", args=[cls.assignment.pk])
        cls.submit_url = reverse("selection-map-submit", args=[cls.assignment.pk])

    def setUp(self):
        self.client.force_authenticate(self.student)

    def save(self, payload=None, revision=0):
        return self.client.put(self.url, {"revision": revision, "payload": payload or {}}, format="json")

    def submit(self, payload=None, revision=0):
        return self.client.post(self.submit_url, {"revision": revision, "payload": payload or complete_map()}, format="json")

    def test_auth_required(self):
        self.client.force_authenticate(None)
        self.assertEqual(self.client.get(self.url).status_code, 401)
        self.assertEqual(self.submit().status_code, 401)

    def test_unenrolled_pending_and_rejected_cannot_access(self):
        self.client.force_authenticate(self.other)
        self.assertEqual(self.client.get(self.url).status_code, 403)
        application = EnrollmentRequest.objects.create(student=self.other, course=self.course, message="Please let me study this course")
        self.assertEqual(self.save().status_code, 403)
        from django.utils import timezone
        application.status = "rejected"
        application.reviewed_at = timezone.now()
        application.save()
        self.assertEqual(self.submit().status_code, 403)

    def test_get_does_not_create_submission(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["revision"], 0)
        self.assertIsNone(response.data["id"])
        self.assertFalse(AssignmentSubmission.objects.exists())

    def test_partial_draft_save_resume(self):
        response = self.save({"working_task": "Draft only"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], "draft")
        self.assertIsNone(response.data["submitted_at"])
        self.assertEqual(self.client.get(self.url).data["payload"], {"working_task": "Draft only"})
        self.assertEqual(self.save({"working_task": "Edited"}, revision=1).data["revision"], 2)

    def test_other_students_cannot_read_or_edit_submission(self):
        self.save({"working_task": "Private student's draft"})
        Enrollment.objects.create(student=self.other, course=self.course)
        self.client.force_authenticate(self.other)
        self.assertEqual(self.client.get(self.url).data["payload"], {})
        self.assertEqual(self.save({"working_task": "Other student draft"}).status_code, 200)
        self.assertEqual(AssignmentSubmission.objects.get(student=self.student).payload["working_task"], "Private student's draft")

    def test_unknown_and_legacy_assignment(self):
        self.assertEqual(self.client.get(reverse("selection-map", args=[999999])).status_code, 404)
        self.assertEqual(self.client.get(reverse("selection-map", args=[self.legacy.pk])).status_code, 404)

    def test_staff_preview_is_read_only(self):
        self.client.force_authenticate(self.author)
        self.assertEqual(self.client.get(self.url).status_code, 200)
        self.assertEqual(self.submit().status_code, 403)
        self.assertFalse(AssignmentSubmission.objects.exists())

    def test_submit_requires_all_ten_fields_without_partial_write(self):
        for field in complete_map():
            payload = complete_map()
            payload.pop(field)
            self.assertEqual(self.submit(payload).status_code, 400, field)
        self.assertFalse(AssignmentSubmission.objects.exists())

    def test_validation_bounds_unknown_fields_and_types(self):
        for payload in ({"working_task": "x" * 4001}, {"working_task": []}, {"unknown": "value"},
                        {"services": ["A", "a"]}, {"services": ["A", "B", "C", "D"]},
                        {"data_classification": "secret"}, {"comparison_criteria": {"unknown": "x"}},
                        {"testing_results": [{"service": "A", "result": "x"}]},
                        {"selected_service": "Absent"}):
            self.assertEqual(self.save(payload).status_code, 400, payload)
        self.assertFalse(AssignmentSubmission.objects.exists())

    def test_submit_rejects_inconsistent_criteria_results_and_selection(self):
        for field, value in (("services", ["Only one"]), ("comparison_criteria", {"quality": "Good"}),
                             ("testing_results", [{"service": "Service A", "result": "Only one"}]),
                             ("selected_service", "Absent")):
            payload = complete_map()
            payload[field] = value
            self.assertEqual(self.submit(payload).status_code, 400)

    def test_successful_submit_is_pending_idempotent_locked_and_does_not_complete_lesson(self):
        response = self.submit()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], "pending")
        self.assertIsNotNone(response.data["submitted_at"])
        self.assertEqual(self.submit().data["revision"], 1)
        self.assertEqual(AssignmentSubmission.objects.count(), 1)
        self.assertEqual(self.save(revision=1).status_code, 409)
        modified = complete_map()
        modified["working_task"] = "Changed"
        self.assertEqual(self.submit(modified, revision=1).status_code, 409)
        self.assertFalse(LessonProgress.objects.exists())

    def test_stale_revision_cannot_overwrite(self):
        self.save({"working_task": "Current"})
        self.assertEqual(self.save({"working_task": "Stale"}, revision=0).status_code, 409)
        self.assertEqual(AssignmentSubmission.objects.get().payload["working_task"], "Current")
        self.assertEqual(self.submit(revision=0).status_code, 409)

    def test_reserved_fields_and_revision_types_rejected(self):
        for envelope in ({"payload": {}, "revision": 0, "student": self.other.pk},
                         {"payload": {}, "revision": True}, {"payload": {}, "revision": -1}):
            self.assertEqual(self.client.put(self.url, envelope, format="json").status_code, 400)

    def test_rejected_can_resume_and_resubmit_without_losing_review(self):
        self.submit()
        submission = AssignmentSubmission.objects.get()
        from django.utils import timezone
        submission.status = "rejected"
        submission.reviewer_comment = "Explain privacy controls"
        submission.reviewed_at = timezone.now()
        submission.revision += 1
        submission.save()
        response = self.save(complete_map(), revision=2)
        self.assertEqual(response.data["status"], "rejected")
        self.assertEqual(response.data["reviewer_comment"], "Explain privacy controls")
        response = self.submit(revision=3)
        self.assertEqual(response.data["status"], "pending")
        self.assertEqual(response.data["reviewer_comment"], "")
        self.assertEqual(response.data["review_history"][0]["reviewer_comment"], "Explain privacy controls")

    def test_legacy_multiple_submissions_and_defaults_unchanged(self):
        for _ in range(2):
            submission = AssignmentSubmission.objects.create(assignment=self.assignment, student=self.student, content="Legacy")
            self.assertEqual(submission.status, "pending")
            self.assertFalse(submission.is_structured)
        self.assertEqual(self.save().status_code, 200)
        self.assertEqual(AssignmentSubmission.objects.count(), 3)
        with self.assertRaises(IntegrityError), transaction.atomic():
            AssignmentSubmission.objects.create(assignment=self.assignment, student=self.student, is_structured=True)

    def test_pending_draft_feedback_is_not_exposed(self):
        self.submit()
        AssignmentSubmission.objects.update(reviewer_comment="Unfinished private review note")
        self.assertEqual(self.client.get(self.url).data["reviewer_comment"], "")

    def test_admin_review_is_readonly_and_links_to_audited_studio(self):
        self.submit()
        submission = AssignmentSubmission.objects.get()
        self.client.force_authenticate(None)
        self.client.force_login(self.author)
        url = reverse("admin:progress_assignmentsubmission_change", args=[submission.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'name="status"')
        for status in ("approved", "rejected"):
            response = self.client.post(url, {"status": status, "reviewer_comment": "Attempted bypass", "expected_revision": 1, "_save": "Save"})
            self.assertEqual(response.status_code, 403)
        submission.refresh_from_db()
        self.assertEqual(submission.status, "pending")
        self.assertEqual(submission.review_history, [])

    def test_student_cannot_use_admin_to_review(self):
        self.submit()
        self.client.force_authenticate(None)
        self.client.force_login(self.student)
        url = reverse("admin:progress_assignmentsubmission_change", args=[AssignmentSubmission.objects.get().pk])
        self.assertEqual(self.client.get(url).status_code, 302)

    def test_studio_approval_is_locked_and_feedback_visible(self):
        self.submit()
        submission = AssignmentSubmission.objects.get()
        self.client.force_authenticate(self.author)
        url = f"/api/studio/submissions/{submission.pk}/review/"
        self.assertEqual(self.client.post(url, {"revision": 0, "status": "approved"}, format="json").status_code, 409)
        response = self.client.post(url, {"revision": 1, "status": "approved", "reviewer_comment": "Accepted"}, format="json")
        self.assertEqual(response.status_code, 200, response.data)
        self.client.force_authenticate(self.student)
        self.assertEqual(self.client.get(self.url).data["reviewer_comment"], "Accepted")
        self.assertEqual(self.save(revision=2).status_code, 409)

    def test_admin_draft_is_not_reviewable_and_structured_deletion_blocked(self):
        self.save({"working_task": "Draft"})
        submission = AssignmentSubmission.objects.get()
        self.client.force_authenticate(None)
        self.client.force_login(self.author)
        url = reverse("admin:progress_assignmentsubmission_change", args=[submission.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)  # Private drafts are absent from admin.
        delete_url = reverse("admin:progress_assignmentsubmission_delete", args=[submission.pk])
        self.assertEqual(self.client.post(delete_url, {"post": "yes"}).status_code, 403)
        self.assertTrue(AssignmentSubmission.objects.filter(pk=submission.pk).exists())

    def test_staff_without_review_model_permission_cannot_review(self):
        self.submit()
        User = get_user_model()
        viewer = User.objects.create_user(username="staff-no-review", is_staff=True)
        self.client.force_authenticate(None)
        self.client.force_login(viewer)
        url = reverse("admin:progress_assignmentsubmission_change", args=[AssignmentSubmission.objects.get().pk])
        self.assertEqual(self.client.post(url, {"status": "approved"}).status_code, 403)
