"""Certificate evidence is separate from existing lesson/course completion semantics."""
import re
import unicodedata

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied, ValidationError

from courses.models import Course, Lesson
from progress.models import AssignmentSubmission, Enrollment, LessonProgress
from quizzes.models import QuizAttempt
from studio.permissions import moderator
from .models import Certificate, CourseCertificatePolicy


def valid_name(value):
    if not isinstance(value, str):
        raise ValidationError({'learner_name': 'Provide a learner display name.'})
    value = unicodedata.normalize('NFC', value).strip()
    if not 3 <= len(value) <= 200 or len(value.split()) < 2:
        raise ValidationError({'learner_name': 'Provide a full learner display name (3–200 characters).'}, code='invalid_name')
    if any(not (char.isalpha() or char in " -'’.") for char in value):
        raise ValidationError({'learner_name': 'Use letters, spaces, apostrophes or hyphens.'}, code='invalid_name')
    return re.sub(r'\s+', ' ', value)


def confirmed_certificate_name(student):
    """Return the canonical name only when the learner explicitly confirmed it."""
    stored_name = getattr(student, 'certificate_name', '')
    confirmed_at = getattr(student, 'certificate_name_confirmed_at', None)
    if not stored_name or not confirmed_at:
        return None
    try:
        normalized = valid_name(stored_name)
    except ValidationError:
        return None
    # Confirmation is tied to the exact canonical value, not merely a truthy timestamp.
    return normalized if normalized == stored_name else None


def approved_submission(student, assignment):
    for submission in AssignmentSubmission.objects.filter(
        student=student, assignment=assignment, status='approved', reviewed_at__isnull=False,
        next_revision__isnull=True,
    ):
        history = submission.review_history
        if not isinstance(history, list) or not history or not isinstance(history[-1], dict):
            continue
        decision = history[-1]
        if decision.get('status') != 'approved' or decision.get('revision') != submission.revision or decision.get('reviewed_at') != submission.reviewed_at.isoformat():
            continue
        reviewer_id = decision.get('reviewer_id')
        if isinstance(reviewer_id, bool) or not isinstance(reviewer_id, int):
            continue
        reviewer = get_user_model().objects.filter(pk=reviewer_id, is_active=True).first()
        owner = assignment.lesson.module.course.author_id
        if reviewer and reviewer.pk != student.pk and (moderator(reviewer) or reviewer.role == 'author' and reviewer.pk == owner):
            return submission
    return None


def eligibility(student, course):
    policy = CourseCertificatePolicy.objects.filter(course=course).first()
    requirements = []
    evidence = {}
    def add(key, met):
        requirements.append({'key': key, 'met': bool(met)})
    add('published_course', course.is_published)
    add('enrolled', Enrollment.objects.filter(student=student, course=course).exists())
    add('policy_enabled', policy and policy.enabled)
    add('approved_issuer', policy and policy.issuer_approved and policy.issuer_name.strip())
    confirmed_name = confirmed_certificate_name(student)
    add('certificate_name_confirmed', confirmed_name is not None)
    if confirmed_name:
        evidence['certificate_name_confirmed_at'] = student.certificate_name_confirmed_at.isoformat()
    if policy:
        explicit_lessons = list(policy.required_lessons.values_list('pk', 'module__course_id'))
        if explicit_lessons:
            required_ids = {lesson_id for lesson_id, _ in explicit_lessons}
            scope_is_valid = all(course_id == course.pk for _, course_id in explicit_lessons)
            completed = list(LessonProgress.objects.filter(
                enrollment__student=student, enrollment__course=course,
                lesson_id__in=required_ids, completed_at__isnull=False,
            ).values_list('lesson_id', flat=True))
            add('required_lessons', scope_is_valid and required_ids <= set(completed))
            evidence['required_lesson_ids'] = sorted(required_ids)
            evidence['lesson_ids'] = completed
        elif policy.require_all_lessons:
            lessons = list(Lesson.objects.filter(module__course=course).values_list('pk', flat=True))
            completed = list(LessonProgress.objects.filter(enrollment__student=student, enrollment__course=course, lesson_id__in=lessons, completed_at__isnull=False).values_list('lesson_id', flat=True))
            add('all_lessons', bool(lessons) and set(lessons) <= set(completed))
            evidence['lesson_ids'] = completed
        if policy.final_quiz_id:
            quiz = policy.final_quiz
            attempt = QuizAttempt.objects.filter(student=student, quiz=quiz, passed=True, score__gte=quiz.passing_percentage).first() if quiz.is_published and quiz.lesson.module.course_id == course.pk else None
            add('final_assessment', attempt)
            evidence['quiz_attempt_id'] = attempt.pk if attempt else None
            evidence['passing_percentage'] = quiz.passing_percentage
        assignments = list(policy.required_assignments.select_related('lesson__module__course'))
        evidence['assignment_submission_ids'] = []
        for assignment in assignments:
            submission = approved_submission(student, assignment) if assignment.lesson.module.course_id == course.pk else None
            add('assignment_approved', submission)
            if submission:
                evidence['assignment_submission_ids'].append(submission.pk)
        # Reject accidentally empty policies rather than awarding on enrollment alone.
        add('configured_requirements', bool(explicit_lessons) or policy.require_all_lessons or policy.final_quiz_id or assignments)
    return {'eligible': bool(requirements) and all(item['met'] for item in requirements), 'requirements': requirements, 'evidence': evidence}


@transaction.atomic
def issue_certificate(*, administrator, student, course_id):
    if not moderator(administrator):
        raise PermissionDenied('Administrator access required.')
    if not getattr(settings, 'CERTIFICATES_ENABLED', False):
        raise PermissionDenied('Certificates are not enabled.')
    course = Course.objects.select_for_update().get(pk=course_id)
    student = get_user_model().objects.select_for_update().get(pk=student.pk, is_active=True)
    existing = Certificate.objects.filter(student=student, course=course).first()
    if existing:
        return existing, False
    name = confirmed_certificate_name(student)
    if not name:
        raise ValidationError({'learner_name': 'The learner must confirm a valid certificate name first.'})
    policy = CourseCertificatePolicy.objects.select_for_update().filter(course=course).first()
    result = eligibility(student, course)
    if not result['eligible']:
        raise ValidationError({'requirements': result['requirements']})
    certificate = Certificate.objects.create(student=student, course=course, learner_name=name, course_title=course.title, issuer_name=policy.issuer_name.strip(), evidence=result['evidence'], issued_by=administrator)
    return certificate, True


@transaction.atomic
def revoke_certificate(*, administrator, certificate, reason):
    if not moderator(administrator):
        raise PermissionDenied('Administrator access required.')
    if not getattr(settings, 'CERTIFICATES_ENABLED', False):
        raise PermissionDenied('Certificates are not enabled.')
    certificate = Certificate.objects.select_for_update().get(pk=certificate.pk)
    if not isinstance(reason, str) or not 1 <= len(reason.strip()) <= 2000:
        raise ValidationError({'reason': 'Provide a reason of 1–2000 characters.'})
    if not certificate.revoked_at:
        certificate.revoked_at = timezone.now()
        certificate.revoked_by = administrator
        certificate.revocation_reason = reason.strip()
        certificate.save(update_fields=['revoked_at', 'revoked_by', 'revocation_reason'])
    return certificate
