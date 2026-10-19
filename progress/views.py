from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView

from courses.models import Course, Lesson, Module

from .models import Enrollment, EnrollmentRequest, LessonProgress
from .activity import student_activity
from .serializers import (
    EnrollmentProgressSerializer, EnrollmentRequestCreateSerializer,
    EnrollmentRequestSerializer, EnrollmentSerializer,
)
from .services import submit_enrollment_request


class MyEnrollmentRequestsView(generics.ListAPIView):
    serializer_class = EnrollmentRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return EnrollmentRequest.objects.filter(student=self.request.user).select_related(
            "course", "course__direction", "course__author", "course__content_import",
        )


class MyActivityView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(student_activity(request.user))


class CourseEnrollmentRequestsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, slug):
        course = get_object_or_404(Course, slug=slug, is_published=True)
        serializer = EnrollmentRequestCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            application = submit_enrollment_request(
                student=request.user, course=course, message=serializer.validated_data["message"],
            )
        except ValidationError as error:
            return Response(
                {"code": getattr(error, "code", "invalid_request"), "detail": " ".join(error.messages)},
                status=status.HTTP_409_CONFLICT,
            )
        except IntegrityError:
            # The partial unique constraint also handles concurrent submissions.
            if EnrollmentRequest.objects.filter(student=request.user, course=course, status="pending").exists():
                return Response(
                    {"code": "duplicate_pending", "detail": "You already have a pending application."},
                    status=status.HTTP_409_CONFLICT,
                )
            raise
        return Response(EnrollmentRequestSerializer(application).data, status=status.HTTP_201_CREATED)


class MyEnrollmentsView(generics.ListAPIView):
    serializer_class = EnrollmentProgressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        modules = Module.objects.order_by("order", "pk").prefetch_related(
            Prefetch("lessons", queryset=Lesson.objects.order_by("order", "pk"))
        )
        return (
            Enrollment.objects.filter(student=self.request.user)
            .select_related("course", "course__direction", "course__author", "course__content_import")
            .prefetch_related(
                Prefetch("course__modules", queryset=modules),
                Prefetch(
                    "lesson_progress",
                    queryset=LessonProgress.objects.filter(completed_at__isnull=False).only(
                        "enrollment_id", "lesson_id", "completed_at"
                    ),
                ),
            )
        )


class EnrollView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, slug):
        with transaction.atomic():
            course = get_object_or_404(Course.objects.select_for_update(), slug=slug, is_published=True)
            enrollment = Enrollment.objects.filter(student=request.user, course=course).first()
            if enrollment is None and course.enrollment_mode == Course.EnrollmentMode.APPROVAL:
                return Response(
                    {"code": "approval_required", "detail": "Request enrollment and wait for approval."},
                    status=status.HTTP_403_FORBIDDEN,
                )
            created = enrollment is None
            if created:
                enrollment, created = Enrollment.objects.get_or_create(student=request.user, course=course)
        serializer = EnrollmentSerializer(enrollment)
        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


class CompleteLessonView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, lesson_id):
        lesson = get_object_or_404(Lesson, id=lesson_id)
        try:
            enrollment = Enrollment.objects.get(student=request.user, course=lesson.module.course)
        except Enrollment.DoesNotExist:
            raise PermissionDenied("Нет доступа к этому курсу — сначала запишитесь на курс.")

        progress, _ = LessonProgress.objects.get_or_create(enrollment=enrollment, lesson=lesson)
        if progress.completed_at is None:
            # Preserve the first completion time, including concurrent retries.
            LessonProgress.objects.filter(pk=progress.pk, completed_at__isnull=True).update(
                completed_at=timezone.now(),
            )
            progress.refresh_from_db(fields=["completed_at"])
        return Response({"lesson_id": lesson.id, "completed_at": progress.completed_at})


class SelectionMapView(APIView):
    """A private, opt-in structured assignment, separate from lesson completion."""
    permission_classes = [permissions.IsAuthenticated]
    submitting = False

    def assignment(self, request, assignment_id, *, writing=False):
        from courses.models import Assignment
        from courses.permissions import can_access_lesson
        assignment = get_object_or_404(
            Assignment.objects.select_related("lesson__module__course"),
            pk=assignment_id, learning_activity="ai_selection_map",
        )
        if not can_access_lesson(request.user, assignment.lesson):
            raise PermissionDenied("Enrollment is required for this assignment.")
        if writing and not Enrollment.objects.filter(
            student=request.user, course_id=assignment.lesson.module.course_id,
        ).exists():
            raise PermissionDenied("Preview is read-only. Enroll before submitting practice.")
        return assignment

    def get(self, request, assignment_id):
        from .models import AssignmentSubmission
        from .serializers import SelectionMapSubmissionSerializer
        assignment = self.assignment(request, assignment_id)
        submission = AssignmentSubmission.objects.filter(
            assignment=assignment, student=request.user, is_structured=True,
        ).first()
        if submission:
            return Response(SelectionMapSubmissionSerializer(submission).data)
        return Response({
            "id": None, "assignment": assignment.pk, "status": "draft", "revision": 0,
            "payload": {}, "reviewer_comment": "", "reviewed_at": None,
            "submitted_at": None, "review_history": [],
        })

    def put(self, request, assignment_id):
        return self.write(request, assignment_id, complete=False)

    def post(self, request, assignment_id):
        if not self.submitting:
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return self.write(request, assignment_id, complete=True)

    def write(self, request, assignment_id, *, complete):
        from .models import AssignmentSubmission
        from .selection_maps import SelectionMapWriteSerializer
        from .serializers import SelectionMapSubmissionSerializer
        assignment = self.assignment(request, assignment_id, writing=True)
        serializer = SelectionMapWriteSerializer(data=request.data, context={"complete": complete})
        serializer.is_valid(raise_exception=True)
        payload, revision = serializer.validated_data["payload"], serializer.validated_data["revision"]
        with transaction.atomic():
            submission = AssignmentSubmission.objects.select_for_update().filter(
                assignment=assignment, student=request.user, is_structured=True,
            ).first()
            if submission and submission.status in ("pending", "approved"):
                # Retrying a successful submit is safe; it cannot alter stored data.
                if complete and payload == submission.payload and revision in (submission.revision, submission.revision - 1):
                    return Response(SelectionMapSubmissionSerializer(submission).data)
                return Response({"code": "submission_locked", "detail": "This submission is already under review or approved."}, status=409)
            if revision != (submission.revision if submission else 0):
                return Response({"code": "revision_conflict", "detail": "The draft changed. Reload before saving."}, status=409)
            if submission is None:
                # Locking the student's existing enrollment serializes first creation.
                Enrollment.objects.select_for_update().get(
                    student=request.user, course_id=assignment.lesson.module.course_id,
                )
                try:
                    with transaction.atomic():
                        submission = AssignmentSubmission.objects.create(
                            assignment=assignment, student=request.user, is_structured=True,
                            status="draft", revision=0,
                        )
                except IntegrityError:
                    return Response({"code": "revision_conflict", "detail": "The draft changed. Reload before saving."}, status=409)
            history = list(submission.review_history)
            if complete and submission.status == "rejected":
                history.append({
                    "revision": submission.revision, "status": "rejected",
                    "reviewer_comment": submission.reviewer_comment,
                    "reviewed_at": submission.reviewed_at.isoformat() if submission.reviewed_at else None,
                })
            updates = {"payload": payload, "revision": revision + 1}
            if complete:
                updates.update(status="pending", submitted_at=timezone.now(), reviewed_at=None,
                               reviewer_comment="", review_history=history)
            # A rejected draft stays rejected while editing so its feedback survives reloads.
            changed = AssignmentSubmission.objects.filter(
                pk=submission.pk, revision=revision, status__in=["draft", "rejected"],
            ).update(**updates)
            if not changed:
                return Response({"code": "revision_conflict", "detail": "The draft changed. Reload before saving."}, status=409)
            submission.refresh_from_db()
        return Response(SelectionMapSubmissionSerializer(submission).data)


class SelectionMapSubmitView(SelectionMapView):
    submitting = True
    http_method_names = ["post", "options"]
