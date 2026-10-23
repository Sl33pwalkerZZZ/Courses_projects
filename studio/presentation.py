from django.urls import reverse
from courses.models import Lesson
from .services import requirements, fingerprint


def quiz_data(quiz):
    return {'id': quiz.pk, 'title': quiz.title, 'instructions': quiz.instructions, 'passing_percentage': quiz.passing_percentage,
            'is_published': quiz.is_published, 'locked': quiz.is_published or quiz.attempts.exists(),
            'questions': [{'id': q.pk, 'text': q.text, 'type': q.type, 'order': q.order, 'explanation': q.explanation,
                           'choices': list(q.choices.values('id', 'text', 'order', 'is_correct'))} for q in quiz.questions.all()]}


def assignment_data(assignment):
    return {'id': assignment.pk, 'type': assignment.type, 'description': assignment.description, 'learning_activity': assignment.learning_activity}


def lesson_data(lesson):
    learning = getattr(lesson, 'learning_content', None)
    images = []
    for image in lesson.images.all():
        description = getattr(image, 'studio_description', None)
        images.append({'id': image.pk, 'image': reverse('lesson-image', args=[image.pk]), 'order': image.order,
                       'alt_text': description.alt_text if description else {}, 'decorative': description.decorative if description else False})
    return {'id': lesson.pk, 'title': lesson.title, 'order': lesson.order, 'text_content': lesson.text_content, 'module': lesson.module_id,
            'learning_content': {'content_language': learning.content_language, 'source_sections': learning.source_sections, 'objectives': learning.objectives, 'interactions': learning.interactions} if learning else None,
            'assignments': [assignment_data(a) for a in lesson.assignments.all()], 'images': images,
            'quiz': quiz_data(lesson.quiz) if hasattr(lesson, 'quiz') else None}


def publication_data(request):
    return {'id': request.pk, 'course': request.course_id, 'course_title': request.course.title, 'status': request.status,
            'source_reviewed': request.source_reviewed, 'assessment_reviewed': request.assessment_reviewed,
            'requested_by': request.requested_by.username, 'reviewed_by': request.reviewed_by.username if request.reviewed_by else None,
            'created_at': request.created_at, 'reviewed_at': request.reviewed_at, 'note': request.note,
            'events': [{'decision': e.decision, 'actor': e.actor.username, 'note': e.note, 'created_at': e.created_at} for e in request.events.select_related('actor')]}


def publication_status(course):
    latest = course.publication_requests.first()
    current = bool(latest and latest.status in ('pending', 'approved') and latest.fingerprint == fingerprint(course))
    return {'is_published': course.is_published,
            'requirements': requirements(course, source_reviewed=bool(current and latest.source_reviewed), assessment_reviewed=bool(current and latest.assessment_reviewed)),
            'requests': [publication_data(r) for r in course.publication_requests.select_related('course', 'requested_by', 'reviewed_by')]}


def course_data(course, *, detail=False):
    imported = getattr(course, 'content_import', None)
    settings = getattr(course, 'studio_settings', None)
    data = {'id': course.pk, 'title': course.title, 'slug': course.slug, 'description': course.description,
            'direction': {'id': course.direction_id, 'name': course.direction.name, 'slug': course.direction.slug},
            'author': {'id': course.author_id, 'username': course.author.username}, 'level': course.level,
            'enrollment_mode': course.enrollment_mode, 'is_published': course.is_published,
            'language': settings.language if settings else imported.content_language if imported else 'ru',
            'module_count': course.modules.count(), 'lesson_count': Lesson.objects.filter(module__course=course).count(),
            'imported': bool(imported), 'created_at': course.created_at}
    if detail:
        data['modules'] = [{'id': m.pk, 'title': m.title, 'order': m.order, 'lessons': [lesson_data(l) for l in m.lessons.order_by('order', 'pk')]} for m in course.modules.order_by('order', 'pk')]
        data['publication'] = publication_status(course)
        data['source'] = {'source_name': imported.source_name, 'source_sha256': imported.source_sha256, 'review_approved': imported.review_approved} if imported else None
    return data


def submission_data(submission, reviewer=None):
    from django.contrib.auth import get_user_model
    from certificates.services import approved_submission
    course = submission.assignment.lesson.module.course
    last = submission.review_history[-1] if submission.review_history else {}
    reviewer_name = get_user_model().objects.filter(pk=last.get('reviewer_id')).values_list('username', flat=True).first() if isinstance(last, dict) else None
    verifiable = approved_submission(submission.student, submission.assignment) if submission.status == 'approved' else None
    return {'course_id': course.pk, 'course_title': course.title, 'lesson_id': submission.assignment.lesson_id,
            'student_username': submission.student.username, 'reviewer_username': reviewer_name,
            'can_review': submission.status == 'pending' and reviewer is not None and reviewer.pk != submission.student_id,
            'review_is_verifiable': bool(verifiable and verifiable.pk == submission.pk),
            'id': submission.pk, 'assignment': submission.assignment_id, 'assignment_description': submission.assignment.description,
            'lesson_title': submission.assignment.lesson.title, 'student': {'id': submission.student_id, 'username': submission.student.username},
            'status': submission.status, 'payload': submission.payload, 'content': submission.content, 'revision': submission.revision,
            'reviewer_comment': submission.reviewer_comment, 'submitted_at': submission.submitted_at, 'reviewed_at': submission.reviewed_at,
            'review_history': submission.review_history, 'is_structured': submission.is_structured, 'file_available': bool(submission.file)}
