"""Small ownership-aware transactions shared by Studio and Django Admin."""
import hashlib
import json
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.text import slugify
from rest_framework.exceptions import PermissionDenied, ValidationError
from courses.models import Course, CourseImport, Lesson
from quizzes.validation import validate_quiz
from .models import PublicationRequest, PublicationEvent
from .permissions import instructor, moderator


def owned_courses(user):
    courses = Course.objects.all()
    if not instructor(user):
        return courses.none()
    return courses if moderator(user) else courses.filter(author=user)


def course_for(user, pk, *, lock=False):
    qs = owned_courses(user)
    if lock:
        qs = qs.select_for_update()
    return get_object_or_404(qs, pk=pk)


def unique_slug(title):
    maximum = Course._meta.get_field('slug').max_length
    base = slugify(title)[:maximum] or 'course'
    slug = base
    suffix = 1
    while Course.objects.filter(slug=slug).exists():
        suffix += 1
        tail = f'-{suffix}'
        slug = f'{base[:maximum - len(tail)]}{tail}'
    return slug


def fingerprint(course):
    # Includes assessment keys and source provenance; never return the digest payload.
    from courses.attachments import attachments_ready
    include_attachments = attachments_ready()
    modules = []
    for module in course.modules.order_by('order', 'pk'):
        lessons = []
        for lesson in module.lessons.order_by('order', 'pk'):
            learning = getattr(lesson, 'learning_content', None)
            quiz = getattr(lesson, 'quiz', None)
            lessons.append({
                'id': lesson.pk, 'title': lesson.title, 'text': lesson.text_content, 'order': lesson.order,
                'learning': {'language': learning.content_language, 'sections': learning.source_sections, 'objectives': learning.objectives, 'interactions': learning.interactions} if learning else None,
                'images': list(lesson.images.values('id', 'image', 'order', 'studio_description__alt_text', 'studio_description__decorative')),
                'assignments': list(lesson.assignments.values('id', 'type', 'description', 'learning_activity')),
                'quiz': {'id': quiz.pk, 'title': quiz.title, 'instructions': quiz.instructions, 'passing': quiz.passing_percentage,
                         'questions': [{'id': q.pk, 'text': q.text, 'type': q.type, 'explanation': q.explanation, 'order': q.order,
                                        'choices': list(q.choices.values('id', 'text', 'is_correct', 'order'))} for q in quiz.questions.all()]} if quiz else None,
            })
        if include_attachments:
            for row, lesson in zip(lessons, module.lessons.order_by('order', 'pk')):
                assets = list(lesson.attachments.values('id', 'kind', 'sha256', 'filename', 'label', 'caption', 'transcript', 'provenance', 'after_section', 'order'))
                # Preserve existing publication fingerprints for lessons without assets.
                if assets:
                    row['attachments'] = assets
        modules.append({'id': module.pk, 'title': module.title, 'order': module.order, 'lessons': lessons})
    imported = getattr(course, 'content_import', None)
    payload = {'title': course.title, 'description': course.description, 'direction': course.direction_id, 'level': course.level,
               'enrollment_mode': course.enrollment_mode, 'modules': modules,
               'language': getattr(getattr(course, 'studio_settings', None), 'language', None),
               'source': [imported.source_sha256, imported.manifest_sha256, imported.version] if imported else None}
    return hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def requirements(course, *, source_reviewed=False, assessment_reviewed=False):
    lessons = list(Lesson.objects.filter(module__course=course).select_related('quiz'))
    quizzes = [lesson.quiz for lesson in lessons if hasattr(lesson, 'quiz')]
    assessment_ok = bool(quizzes)
    for quiz in quizzes:
        try:
            validate_quiz(quiz)
        except DjangoValidationError:
            assessment_ok = False
    imported = getattr(course, 'content_import', None)
    return [{'key': key, 'label': label, 'met': bool(met)} for key, label, met in [
        ('title', 'Course title is complete', course.title.strip()),
        ('description', 'Course description is complete', course.description.strip()),
        ('curriculum', 'At least one module and lesson', bool(lessons) and all(module.lessons.exists() for module in course.modules.all())),
        ('lesson_content', 'Every lesson has educational content', bool(lessons) and all(l.title.strip() and l.text_content.strip() for l in lessons)),
        ('assessment', 'Quiz questions and correct answers pass validation', assessment_ok),
        ('source_reviewed', 'Imported source facts and references reviewed', not imported or source_reviewed or imported.review_approved),
        ('assessment_reviewed', 'Assessment questions and answers reviewed', assessment_reviewed),
    ]]


@transaction.atomic
def decide_publication(*, request_id, reviewer, decision, note=''):
    if not moderator(reviewer):
        raise PermissionDenied('Only administrators may review publication.')
    # All Studio mutations lock the course first, then child rows.
    initial = get_object_or_404(PublicationRequest, pk=request_id)
    course = Course.objects.select_for_update().get(pk=initial.course_id)
    review = PublicationRequest.objects.select_for_update().get(pk=request_id)
    if review.status != 'pending':
        raise ValidationError({'status': 'This request has already been reviewed.'})
    if decision not in ('approve', 'reject'):
        raise ValidationError({'decision': 'Choose approve or reject.'})
    if decision == 'reject' and not note.strip():
        raise ValidationError({'note': 'Provide an actionable rejection explanation.'})
    if decision == 'approve':
        if fingerprint(course) != review.fingerprint:
            raise ValidationError({'requirements': 'Course changed after review was requested. Reject and request a fresh review.'})
        unmet = [item for item in requirements(course, source_reviewed=review.source_reviewed, assessment_reviewed=review.assessment_reviewed) if not item['met']]
        if unmet:
            raise ValidationError({'requirements': unmet})
        imported = getattr(course, 'content_import', None)
        if imported:
            imported.review_approved = True
            imported.save(update_fields=['review_approved'])
        # Publication uses existing validation gates, including CourseImport.
        for lesson in Lesson.objects.filter(module__course=course).select_related('quiz'):
            quiz = getattr(lesson, 'quiz', None)
            if quiz:
                quiz.is_published = True
                quiz.full_clean()
                quiz.save(update_fields=['is_published'])
        course.is_published = True
        course.full_clean()
        course.save(update_fields=['is_published'])
    review.status = 'approved' if decision == 'approve' else 'rejected'
    review.note = note
    review.reviewed_by = reviewer
    review.reviewed_at = timezone.now()
    review.save(update_fields=['status', 'note', 'reviewed_by', 'reviewed_at'])
    PublicationEvent.objects.create(request=review, actor=reviewer, decision=review.status, note=note)
    return review
