import io
import struct
import tempfile
import zipfile
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied, ValidationError as DjangoValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.urls import reverse
from PIL import Image
from rest_framework.test import APITestCase

from certificates.services import approved_submission
from courses.models import Assignment, Course, Direction, Lesson, Module
from .models import AssignmentSubmission, AssignmentSubmissionAttachment, Enrollment
from .submission_files import validate_upload, validate_upload_set


def text_file(name="notes.txt", content=b"A plain text response.", mime="application/octet-stream"):
    return SimpleUploadedFile(name, content, content_type=mime)


def image_file(name="diagram.png", image_format="PNG"):
    buffer = io.BytesIO()
    Image.new("RGB", (3, 2), (80, 120, 180)).save(buffer, image_format)
    return SimpleUploadedFile(name, buffer.getvalue(), content_type="text/plain")


def png_file(name="diagram.png"):
    return image_file(name, "PNG")


def ooxml_file(extension):
    part, content_type = {
        ".docx": ("word/document.xml", "application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"),
        ".pptx": ("ppt/presentation.xml", "application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"),
        ".xlsx": ("xl/workbook.xml", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"),
    }[extension]
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", f'<Types><Override ContentType="{content_type}"/></Types>')
        archive.writestr(part, "<root/>")
    return SimpleUploadedFile(f"valid{extension}", buffer.getvalue(), content_type="text/plain")


def mp4_file():
    # Small synthetic ISO-BMFF structure; no codec payload is executed or decoded.
    value = struct.pack(">I4s", 16, b"ftyp") + b"isom0000"
    value += struct.pack(">I4s", 12, b"moov") + b"meta"
    value += struct.pack(">I4s", 9, b"mdat") + b"x"
    return SimpleUploadedFile("clip.mp4", value, content_type="text/plain")


class FakeSizedUpload:
    def __init__(self, name, size):
        self.name, self.size = name, size


class AssignmentSubmissionApiTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        users = get_user_model()
        cls.student = users.objects.create_user(username="submission-student")
        cls.other = users.objects.create_user(username="submission-other")
        cls.owner = users.objects.create_user(username="submission-owner", role="author")
        cls.other_author = users.objects.create_user(username="submission-other-author", role="author")
        cls.admin = users.objects.create_superuser(username="submission-admin", password="test")
        direction = Direction.objects.create(name="Submission", slug="submission-test")
        cls.course = Course.objects.create(title="Submission", slug="submission-test", description="Course",
                                          direction=direction, author=cls.owner, is_published=True)
        module = Module.objects.create(course=cls.course, title="Module", order=1)
        cls.lesson = Lesson.objects.create(module=module, title="Lesson", text_content="Instructions", order=1)
        cls.text_assignment = Assignment.objects.create(lesson=cls.lesson, type="text", description="Write and attach work")
        cls.file_assignment = Assignment.objects.create(lesson=cls.lesson, type="file", description="Attach a document")
        cls.structured = Assignment.objects.create(lesson=cls.lesson, type="text", description="Selection map", learning_activity="ai_selection_map")
        Enrollment.objects.create(student=cls.student, course=cls.course)
        Enrollment.objects.create(student=cls.other, course=cls.course)

    def setUp(self):
        self.client.force_authenticate(self.student)
        self.url = reverse("assignment-submissions", args=[self.text_assignment.pk])

    def post_submission(self, *, content=None, files=(), assignment=None):
        assignment = assignment or self.text_assignment
        url = reverse("assignment-submissions", args=[assignment.pk])
        data = {}
        if content is not None:
            data["content"] = content
        if files:
            data["files"] = list(files)
        return self.client.post(url, data, format="multipart")

    def test_requires_auth_enrollment_and_student_role(self):
        self.client.force_authenticate(None)
        self.assertEqual(self.client.get(self.url).status_code, 401)
        self.client.force_authenticate(self.other_author)
        self.assertEqual(self.client.post(self.url, {"content": "Answer"}, format="multipart").status_code, 403)
        outsider = get_user_model().objects.create_user(username="not-enrolled")
        self.client.force_authenticate(outsider)
        self.assertEqual(self.client.get(self.url).status_code, 403)
        self.assertEqual(self.client.post(self.url, {"content": "Answer"}, format="multipart").status_code, 403)

    def test_text_file_and_combined_submission_are_supported(self):
        result = self.post_submission(content="A considered answer")
        self.assertEqual(result.status_code, 201, result.data)
        self.assertEqual(result.data["status"], "pending")
        self.assertEqual(result.data["content"], "A considered answer")
        self.assertEqual(result["Cache-Control"], "private, no-store")
        self.assertIn("Authorization", result["Vary"])
        self.client.force_authenticate(self.other)
        self.assertEqual(self.client.get(self.url).data["submissions"], [])
        result = self.client.post(reverse("assignment-submissions", args=[self.file_assignment.pk]),
                                  {"files": [png_file()]}, format="multipart")
        self.assertEqual(result.status_code, 201, result.data)
        self.client.force_authenticate(self.student)
        result = self.post_submission(content="Written explanation", files=[text_file()])
        self.assertEqual(result.status_code, 409, result.data)  # The first text submission is still pending.
        self.client.force_authenticate(self.owner)
        from progress.services import review_assignment_submission
        first = AssignmentSubmission.objects.filter(assignment=self.text_assignment, student=self.student).get()
        review_assignment_submission(submission_id=first.pk, reviewer=self.owner, revision=1, status="rejected", comment="Add an example")
        self.client.force_authenticate(self.student)
        result = self.post_submission(content="Written explanation", files=[text_file()])
        self.assertEqual(result.status_code, 201, result.data)
        self.assertEqual(len(result.data["attachments"]), 1)

    def test_upload_validation_extensions_real_signatures_and_limits(self):
        accepted = [text_file(), png_file(), image_file("photo.jpg", "JPEG"), image_file("photo.jpeg", "JPEG"), image_file("figure.webp", "WEBP"),
                    ooxml_file(".docx"), ooxml_file(".pptx"), ooxml_file(".xlsx"), mp4_file(),
                    SimpleUploadedFile("data.csv", b"name,value\nitem,3", content_type="image/png"),
                    SimpleUploadedFile("report.pdf", b"%PDF-1.4\nbody\n%%EOF", content_type="text/html")]
        for upload in accepted:
            with self.subTest(name=upload.name):
                meta = validate_upload(upload)
                self.assertEqual(upload.content_type, "text/plain" if upload.name == "clip.mp4" else upload.content_type)
                self.assertEqual(meta["detected_content_type"], {
                    "notes.txt": "text/plain", "diagram.png": "image/png", "photo.jpg": "image/jpeg", "photo.jpeg": "image/jpeg", "figure.webp": "image/webp",
                    "valid.docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    "valid.pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation", "valid.xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    "clip.mp4": "video/mp4", "data.csv": "text/csv", "report.pdf": "application/pdf",
                }[upload.name])
        for upload in [text_file("bad.zip", b"PK\x03\x04"), text_file("bad.exe"), text_file("bad.html", b"<html>not allowed</html>"),
                       text_file("bad.svg", b"<svg/>"), text_file("fake.jpg", b"not an image"),
                       text_file("fake.docx", b"not a zip"), text_file("fake.mp4", b"not video"),
                       text_file("page.txt", b"<!doctype html><html/>")]:
            with self.subTest(name=upload.name), self.assertRaises(DjangoValidationError):
                validate_upload(upload)
        with self.assertRaises(DjangoValidationError):
            validate_upload(FakeSizedUpload("large.pdf", 10 * 1024 * 1024 + 1))
        with self.assertRaises(DjangoValidationError):
            validate_upload(FakeSizedUpload("large.mp4", 50 * 1024 * 1024 + 1))
        with self.assertRaises(DjangoValidationError):
            validate_upload_set([FakeSizedUpload("a.mp4", 34 * 1024 * 1024), FakeSizedUpload("b.mp4", 34 * 1024 * 1024), FakeSizedUpload("c.mp4", 34 * 1024 * 1024)])
        with self.assertRaises(DjangoValidationError):
            validate_upload_set([text_file(str(index) + ".txt") for index in range(6)])

    def test_rejected_uploads_and_file_count_do_not_create_records(self):
        for invalid in (text_file("archive.zip", b"PK\x03\x04"), text_file("fake.png", b"not image"),
                        text_file("disguised.docx", b"not a package"), text_file("bad.html", b"<html/>") ):
            result = self.post_submission(files=[invalid])
            self.assertEqual(result.status_code, 400, (invalid.name, result.data))
        result = self.post_submission(files=[text_file(f"{index}.txt") for index in range(6)])
        self.assertEqual(result.status_code, 400, result.data)
        self.assertFalse(AssignmentSubmission.objects.filter(assignment=self.text_assignment).exists())

    def test_file_download_is_private_and_scoped_to_learner_assignment(self):
        result = self.post_submission(content="Answer", files=[png_file()])
        self.assertEqual(result.status_code, 201, result.data)
        submission_id, attachment_id = result.data["id"], result.data["attachments"][0]["id"]
        download_url = reverse("assignment-submission-file", args=[self.text_assignment.pk, submission_id, attachment_id])
        response = self.client.get(download_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Disposition"].split("filename=")[-1].strip('"'), "diagram.png")
        self.assertEqual(response["X-Content-Type-Options"], "nosniff")
        stored_name = AssignmentSubmissionAttachment.objects.get(pk=attachment_id).file.name
        self.assertTrue(stored_name.startswith("submissions/"))
        self.assertNotIn("diagram.png", stored_name)
        self.assertEqual(self.client.get("/media/" + stored_name).status_code, 404)
        self.client.force_authenticate(self.owner)
        instructor_url = f"/api/studio/submissions/{submission_id}/files/{attachment_id}/"
        self.assertEqual(self.client.get(instructor_url).status_code, 200)
        self.client.force_authenticate(self.other_author)
        self.assertEqual(self.client.get(instructor_url).status_code, 404)
        other_url = reverse("assignment-submission-file", args=[self.text_assignment.pk, submission_id, attachment_id])
        self.client.force_authenticate(self.other)
        self.assertEqual(self.client.get(other_url).status_code, 404)
        self.client.force_authenticate(None)
        self.assertEqual(self.client.get(download_url).status_code, 401)
        self.assertTrue(AssignmentSubmissionAttachment.objects.filter(pk=attachment_id).exists())

    def test_history_resubmission_and_approval_lock(self):
        first = self.post_submission(content="First version", files=[png_file("first.png")])
        self.assertEqual(first.status_code, 201)
        first_record = AssignmentSubmission.objects.get(pk=first.data["id"])
        original_attachment = first_record.attachments.get()
        original_path = original_attachment.file.name
        self.client.force_authenticate(self.owner)
        from progress.services import review_assignment_submission
        review_assignment_submission(submission_id=first_record.pk, reviewer=self.owner, revision=1, status="rejected", comment="Please explain the source")
        self.client.force_authenticate(self.student)
        second = self.post_submission(content="Revised version", files=[png_file("second.png")])
        self.assertEqual(second.status_code, 201, second.data)
        self.assertEqual(second.data["previous_submission"], first_record.pk)
        self.assertEqual(AssignmentSubmission.objects.get(pk=first_record.pk).content, "First version")
        self.assertEqual(AssignmentSubmissionAttachment.objects.get(pk=original_attachment.pk).file.name, original_path)
        self.assertNotEqual(AssignmentSubmissionAttachment.objects.get(submission_id=second.data["id"]).file.name, original_path)
        history = self.client.get(self.url).data["submissions"]
        self.assertEqual([item["status"] for item in history], ["rejected", "pending"])
        self.client.force_authenticate(self.owner)
        second_record = AssignmentSubmission.objects.get(pk=second.data["id"])
        review_assignment_submission(submission_id=second_record.pk, reviewer=self.owner, revision=1, status="approved", comment="Accepted")
        self.assertIsNotNone(approved_submission(self.student, self.text_assignment))
        self.client.force_authenticate(self.student)
        locked = self.post_submission(content="Attempt to replace approved work")
        self.assertEqual(locked.status_code, 409)
        self.assertEqual(self.client.get(self.url).data["submissions"][-1]["feedback"], "Accepted")

    def test_reopened_approval_creates_new_revision_and_invalidates_old_certificate_evidence(self):
        from progress.services import review_assignment_submission
        from progress.services import reopen_assignment_submission
        submitted = self.post_submission(content="Approved first version")
        record = AssignmentSubmission.objects.get(pk=submitted.data["id"])
        self.client.force_authenticate(self.owner)
        review_assignment_submission(submission_id=record.pk, reviewer=self.owner, revision=1, status="approved", comment="Accepted")
        self.assertEqual(approved_submission(self.student, self.text_assignment).pk, record.pk)
        with self.assertRaises(PermissionDenied):
            reopen_assignment_submission(submission_id=record.pk, reviewer=self.other_author)
        reopened_response = self.client.post(f"/api/studio/submissions/{record.pk}/reopen/", {}, format="json")
        self.assertEqual(reopened_response.status_code, 201, reopened_response.data)
        reopened = AssignmentSubmission.objects.get(pk=reopened_response.data["id"])
        self.assertEqual(reopened.status, "draft")
        self.assertEqual(reopened.previous_submission_id, record.pk)
        self.assertIsNone(approved_submission(self.student, self.text_assignment))
        self.client.force_authenticate(self.student)
        result = self.client.post(self.url, {"content": "New approved version"}, format="multipart")
        self.assertEqual(result.status_code, 201, result.data)
        self.client.force_authenticate(self.owner)
        fresh = AssignmentSubmission.objects.get(pk=result.data["id"])
        review_assignment_submission(submission_id=fresh.pk, reviewer=self.owner, revision=1, status="approved", comment="Reapproved")
        self.assertEqual(approved_submission(self.student, self.text_assignment).pk, fresh.pk)

    def test_rejects_unknown_fields_empty_submission_and_structured_course8_endpoint(self):
        self.assertEqual(self.client.post(self.url, {"status": "approved", "content": "x"}, format="multipart").status_code, 400)
        self.assertEqual(self.client.post(self.url, {}, format="multipart").status_code, 400)
        self.assertEqual(self.client.get(reverse("assignment-submissions", args=[self.structured.pk])).status_code, 404)
        self.assertFalse(AssignmentSubmission.objects.exists())

    def test_failed_database_write_cleans_new_private_file(self):
        with tempfile.TemporaryDirectory() as media_root, override_settings(MEDIA_ROOT=media_root):
            with patch("progress.assignment_views.AssignmentSubmissionAttachment.save", side_effect=RuntimeError("fixture failure")):
                with self.assertRaises(RuntimeError):
                    self.post_submission(content="Answer", files=[png_file()])
            import os
            self.assertFalse([name for root, _, names in os.walk(media_root) for name in names])
        self.assertFalse(AssignmentSubmission.objects.filter(assignment=self.text_assignment).exists())
