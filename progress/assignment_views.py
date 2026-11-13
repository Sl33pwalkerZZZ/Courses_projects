"""Learner-owned generic assignment submissions and protected file downloads."""
from pathlib import PurePosixPath

from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.files.storage import default_storage
from django.db import IntegrityError, transaction
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.cache import patch_vary_headers
from rest_framework import permissions, status
from rest_framework.exceptions import APIException, PermissionDenied, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from courses.models import Assignment
from courses.permissions import can_access_lesson
from .models import AssignmentSubmission, AssignmentSubmissionAttachment, Enrollment
from .submission_files import validate_upload_set


class SubmissionConflict(APIException):
    status_code = 409
    default_detail = "The current submission state does not allow this operation."
    default_code = "submission_conflict"


class PrivateStudentAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def finalize_response(self, request, response, *args, **kwargs):
        response = super().finalize_response(request, response, *args, **kwargs)
        response["Cache-Control"] = "private, no-store"
        patch_vary_headers(response, ["Authorization", "Cookie"])
        return response


def generic_assignment(request, assignment_id):
    assignment = get_object_or_404(
        Assignment.objects.select_related("lesson__module__course"), pk=assignment_id,
    )
    # Course 8's structured interaction and quiz placeholders retain their own semantics.
    if assignment.learning_activity == "ai_selection_map" or assignment.type == Assignment.Type.QUIZ:
        raise Http404("Generic assignment not found.")
    if not can_access_lesson(request.user, assignment.lesson):
        raise PermissionDenied("Access to this lesson is required.")
    if not Enrollment.objects.filter(student=request.user, course_id=assignment.lesson.module.course_id).exists():
        raise PermissionDenied("Preview is read-only. Enroll before submitting an assignment.")
    if request.user.role != "student":
        raise PermissionDenied("Only enrolled learners can access student submissions.")
    return assignment


def attachment_data(item):
    return {"id": item.pk, "filename": item.original_filename, "content_type": item.detected_content_type,
            "size": item.size, "created_at": item.created_at}


def learner_submission_data(submission):
    history = []
    for event in submission.review_history if isinstance(submission.review_history, list) else []:
        if not isinstance(event, dict):
            continue
        history.append({key: event[key] for key in ("action", "status", "comment", "reviewer_comment", "reviewed_at", "reopened_at", "submitted_at", "revision", "rubric_scores") if key in event})
    attachments = list(submission.attachments.all())
    return {
        "id": submission.pk,
        "status": submission.status,
        "content": submission.content,
        "revision": submission.revision,
        "submitted_at": None if submission.status == "draft" else submission.submitted_at,
        "reviewed_at": submission.reviewed_at,
        "feedback": submission.reviewer_comment if submission.status in ("approved", "rejected") else "",
        "rubric_scores": (submission.review_history[-1].get("rubric_scores") if submission.review_history and isinstance(submission.review_history[-1], dict) else None),
        "review_history": history,
        "previous_submission": submission.previous_submission_id,
        "attachments": [attachment_data(item) for item in attachments],
        "legacy_file_available": bool(submission.file),
    }


class AssignmentSubmissionsView(PrivateStudentAPIView):
    def get(self, request, assignment_id):
        assignment = generic_assignment(request, assignment_id)
        submissions = AssignmentSubmission.objects.filter(
            assignment=assignment, student=request.user, is_structured=False,
        ).prefetch_related("attachments").order_by("submitted_at", "pk")
        return Response({
            "assignment": {"id": assignment.pk, "type": assignment.type, "description": assignment.description},
            "submissions": [learner_submission_data(item) for item in submissions],
        })

    def post(self, request, assignment_id):
        assignment = generic_assignment(request, assignment_id)
        allowed_fields = {"content", "files"}
        if set(request.data.keys()) - allowed_fields:
            raise ValidationError({"detail": "Only assignment text and files may be submitted."})
        content = request.data.get("content", "")
        if not isinstance(content, str) or len(content) > 100_000:
            raise ValidationError({"content": "Text must be 100,000 characters or fewer."})
        content = content.strip()
        uploads = request.FILES.getlist("files")
        if not content and not uploads:
            raise ValidationError({"detail": "Add meaningful text, at least one file, or both."})
        if assignment.type == Assignment.Type.FILE_UPLOAD and not uploads:
            raise ValidationError({"files": "Attach at least one file for this assignment."})
        try:
            validated_files = validate_upload_set(uploads)
        except DjangoValidationError as error:
            raise ValidationError({"files": error.messages})

        saved_names = []
        try:
            with transaction.atomic():
                # Serializes submissions on databases with row-level locks; the partial
                # unique index remains the final guard against simultaneous pending work.
                Enrollment.objects.select_for_update().get(student=request.user, course_id=assignment.lesson.module.course_id)
                latest = AssignmentSubmission.objects.select_for_update().filter(
                    assignment=assignment, student=request.user, is_structured=False,
                ).order_by("-submitted_at", "-pk").first()
                if latest and latest.status in ("pending", "approved"):
                    raise SubmissionConflict({"status": "This assignment is already submitted or approved."})
                if latest and latest.status == "draft":
                    history = latest.review_history if isinstance(latest.review_history, list) else []
                    if not history or history[-1].get("action") != "reopened":
                        raise SubmissionConflict({"status": "This draft was not reopened by an instructor."})
                    latest.content = content
                    latest.status = "pending"
                    latest.revision += 1
                    latest.submitted_at = timezone.now()
                    latest.review_history = history + [{"action": "submitted", "submitted_at": timezone.now().isoformat(), "revision": latest.revision}]
                    latest.save(update_fields=["content", "status", "revision", "submitted_at", "review_history"])
                    submission = latest
                else:
                    submission = AssignmentSubmission.objects.create(
                        assignment=assignment, student=request.user, content=content, status="pending", revision=1,
                        previous_submission=latest,
                        review_history=[{"action": "submitted", "submitted_at": timezone.now().isoformat(), "revision": 1}],
                    )
                for upload, metadata in validated_files:
                    attachment = AssignmentSubmissionAttachment(
                        submission=submission, original_filename=metadata["original_filename"],
                        detected_content_type=metadata["detected_content_type"], size=metadata["size"], sha256=metadata["sha256"],
                    )
                    attachment.file.save(metadata["original_filename"], upload, save=False)
                    saved_names.append(attachment.file.name)
                    attachment.save()
        except IntegrityError:
            for name in saved_names:
                default_storage.delete(name)
            return Response({"code": "pending_submission", "detail": "A submission is already awaiting review."}, status=409)
        except Exception:
            for name in saved_names:
                default_storage.delete(name)
            raise
        return Response(learner_submission_data(submission), status=status.HTTP_201_CREATED)


def private_submission_attachment(request, submission, attachment):
    if submission.status == "draft" or attachment.submission_id != submission.pk:
        raise Http404("Submission file not found.")
    name = attachment.file.name
    parts = PurePosixPath(name).parts
    if not parts or parts[0] != "submissions" or any(part in ("", ".", "..") for part in parts) or "\\" in name:
        raise Http404("Submission file not found.")
    try:
        response = FileResponse(default_storage.open(name, "rb"), as_attachment=True,
                                filename=attachment.original_filename, content_type="application/octet-stream")
    except (FileNotFoundError, IsADirectoryError, PermissionError, ValueError):
        raise Http404("Submission file not found.")
    response["X-Content-Type-Options"] = "nosniff"
    response["Cache-Control"] = "private, no-store"
    return response


def private_legacy_submission_file(submission):
    if submission.status == "draft" or not submission.file:
        raise Http404("Submission file not found.")
    name = submission.file.name
    parts = PurePosixPath(name).parts
    if not parts or parts[0] != "submissions" or any(part in ("", ".", "..") for part in parts) or "\\" in name:
        raise Http404("Submission file not found.")
    try:
        response = FileResponse(default_storage.open(name, "rb"), as_attachment=True,
                                filename=PurePosixPath(name).name, content_type="application/octet-stream")
    except (FileNotFoundError, IsADirectoryError, PermissionError, ValueError):
        raise Http404("Submission file not found.")
    response["X-Content-Type-Options"] = "nosniff"
    response["Cache-Control"] = "private, no-store"
    return response


class AssignmentSubmissionFileView(PrivateStudentAPIView):
    def get(self, request, assignment_id, submission_id, attachment_id):
        assignment = generic_assignment(request, assignment_id)
        submission = get_object_or_404(AssignmentSubmission, pk=submission_id, assignment=assignment, student=request.user, is_structured=False)
        attachment = get_object_or_404(AssignmentSubmissionAttachment, pk=attachment_id, submission=submission)
        return private_submission_attachment(request, submission, attachment)


class AssignmentLegacySubmissionFileView(PrivateStudentAPIView):
    def get(self, request, assignment_id, submission_id):
        assignment = generic_assignment(request, assignment_id)
        submission = get_object_or_404(AssignmentSubmission, pk=submission_id, assignment=assignment, student=request.user, is_structured=False)
        return private_legacy_submission_file(submission)
