"""Authenticated, ownership-scoped authoring. No bulk deletion or public answer keys."""
import hashlib
import json
from io import BytesIO
from pathlib import Path
from uuid import uuid4
from PIL import Image, UnidentifiedImageError
from django.contrib.auth import get_user_model
from django.core import signing
from django.http import FileResponse, Http404
from courses.media import confined_file
from django.conf import settings
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.files.base import ContentFile
from django.db import IntegrityError, transaction
from django.db.models import Max
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.cache import patch_vary_headers
from rest_framework import status
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from courses.models import Assignment, Course, CourseImport, Direction, Lesson, LessonImage, LessonLearningContent, Module
from progress.models import AssignmentSubmission
from quizzes.models import Quiz, QuizChoice, QuizQuestion
from .models import CourseSettings, ImportPreview, LessonImageDescription, PublicationEvent, PublicationRequest
from .permissions import InstructorPermission, moderator
from .presentation import assignment_data, course_data, lesson_data, publication_data, publication_status, quiz_data, submission_data
from .serializers import AssignmentWriteSerializer, CourseWriteSerializer, LessonWriteSerializer, ModuleWriteSerializer, QuizWriteSerializer, ReviewWriteSerializer
from .services import course_for, decide_publication, fingerprint, owned_courses, requirements, unique_slug


class StudioView(APIView):
    permission_classes = [InstructorPermission]

    def finalize_response(self, request, response, *args, **kwargs):
        response = super().finalize_response(request, response, *args, **kwargs)
        response['Cache-Control'] = 'private, no-store'
        patch_vary_headers(response, ['Authorization', 'Cookie'])
        return response


def validated(serializer_type, data, *, instance=None, partial=False):
    serializer = serializer_type(instance=instance, data=data, partial=partial)
    serializer.is_valid(raise_exception=True)
    return serializer.validated_data


def editable(course):
    if course.is_published:
        raise ValidationError({'course': 'Published content is locked. Contact an administrator to plan a safe revision; student records are preserved.'})
    # A later change invalidates the old editorial acknowledgement.
    CourseImport.objects.filter(course=course, review_approved=True).update(review_approved=False)


def lesson_for(user, pk):
    lesson = get_object_or_404(Lesson.objects.select_related('module__course'), pk=pk, module__course__in=owned_courses(user))
    course = course_for(user, lesson.module.course_id, lock=True)
    return lesson, course


def create_course(user, data):
    language = data.pop('language', 'ru')
    # Savepoints let a rare concurrent slug collision retry without breaking outer atomic.
    for attempt in range(8):
        try:
            with transaction.atomic():
                course = Course(author=user, slug=unique_slug(data['title']), is_published=False, **data)
                course.full_clean(validate_unique=False)
                course.save()
                CourseSettings.objects.create(course=course, language=language)
            return course
        except IntegrityError:
            if attempt == 7:
                raise ValidationError('Could not allocate a unique course slug. Please retry.')


class MeView(StudioView):
    def get(self, request):
        return Response({'id': request.user.pk, 'username': request.user.username, 'role': request.user.role, 'is_moderator': moderator(request.user)})


class MetaView(StudioView):
    def get(self, request):
        return Response({'directions': list(Direction.objects.values('id', 'name', 'slug')),
                         'levels': [{'value': value, 'label': label} for value, label in Course.Level.choices],
                         'enrollment_modes': [{'value': value, 'label': label} for value, label in Course.EnrollmentMode.choices],
                         'languages': ['ru', 'kk', 'en']})


class DashboardView(StudioView):
    def get(self, request):
        courses = owned_courses(request.user)
        return Response({'courses': courses.count(), 'published': courses.filter(is_published=True).count(), 'drafts': courses.filter(is_published=False).count(),
                         'pending_publications': PublicationRequest.objects.filter(course__in=courses, status='pending').count(),
                         'pending_submissions': AssignmentSubmission.objects.filter(assignment__lesson__module__course__in=courses, status='pending').count()})


class CourseListView(StudioView):
    def get(self, request):
        return Response([course_data(course) for course in owned_courses(request.user).select_related('author', 'direction', 'content_import', 'studio_settings').order_by('-created_at', '-pk')])

    @transaction.atomic
    def post(self, request):
        data = validated(CourseWriteSerializer, request.data)
        course = create_course(request.user, dict(data))
        return Response(course_data(course, detail=True), status=status.HTTP_201_CREATED)


class CourseDetailView(StudioView):
    def get(self, request, pk):
        return Response(course_data(course_for(request.user, pk), detail=True))

    @transaction.atomic
    def patch(self, request, pk):
        course = course_for(request.user, pk, lock=True)
        editable(course)
        data = validated(CourseWriteSerializer, request.data, instance=course, partial=True)
        language = data.pop('language', None)
        for key, value in data.items():
            setattr(course, key, value)
        course.full_clean()
        course.save(update_fields=list(data))
        if language:
            CourseSettings.objects.update_or_create(course=course, defaults={'language': language})
        return Response(course_data(course, detail=True))


class CourseModulesView(StudioView):
    @transaction.atomic
    def post(self, request, pk):
        course = course_for(request.user, pk, lock=True)
        editable(course)
        data = validated(ModuleWriteSerializer, request.data)
        module = Module.objects.create(course=course, order=(course.modules.aggregate(value=Max('order'))['value'] or 0) + 1, **data)
        return Response({'id': module.pk, 'title': module.title, 'order': module.order, 'lessons': []}, status=201)


class ModuleDetailView(StudioView):
    @transaction.atomic
    def patch(self, request, pk):
        module = get_object_or_404(Module, pk=pk, course__in=owned_courses(request.user))
        course = course_for(request.user, module.course_id, lock=True)
        editable(course)
        data = validated(ModuleWriteSerializer, request.data, instance=module, partial=True)
        for key, value in data.items():
            setattr(module, key, value)
        module.full_clean()
        module.save(update_fields=list(data))
        return Response({'id': module.pk, 'title': module.title, 'order': module.order})


class ReorderView(StudioView):
    kind = 'modules'

    @transaction.atomic
    def post(self, request, pk):
        if self.kind == 'modules':
            course = course_for(request.user, pk, lock=True)
            objects = course.modules
        else:
            module = get_object_or_404(Module, pk=pk, course__in=owned_courses(request.user))
            course = course_for(request.user, module.course_id, lock=True)
            objects = module.lessons
        editable(course)
        ids = request.data.get('ids')
        expected = list(objects.values_list('pk', flat=True))
        if not isinstance(ids, list) or any(type(value) is not int for value in ids) or len(ids) != len(set(ids)) or set(ids) != set(expected):
            raise ValidationError({'ids': 'Provide every sibling ID exactly once; unrelated IDs are not allowed.'})
        for order, object_id in enumerate(ids, 1):
            objects.filter(pk=object_id).update(order=order)
        return Response({'ids': ids})


class LessonReorderView(ReorderView):
    kind = 'lessons'


def save_lesson(lesson, data):
    learning = data.pop('learning_content', None)
    for key, value in data.items():
        setattr(lesson, key, value)
    lesson.full_clean()
    lesson.save()
    if learning is not None:
        LessonLearningContent.objects.update_or_create(lesson=lesson, defaults=learning)
    # Reverse one-to-one caches must reflect a just-created/updated learning record.
    lesson.refresh_from_db()
    return lesson


class ModuleLessonsView(StudioView):
    @transaction.atomic
    def post(self, request, pk):
        module = get_object_or_404(Module, pk=pk, course__in=owned_courses(request.user))
        course = course_for(request.user, module.course_id, lock=True)
        editable(course)
        data = validated(LessonWriteSerializer, request.data)
        lesson = Lesson(module=module, order=(module.lessons.aggregate(value=Max('order'))['value'] or 0) + 1)
        return Response(lesson_data(save_lesson(lesson, dict(data))), status=201)


class LessonDetailView(StudioView):
    def get(self, request, pk):
        lesson = get_object_or_404(Lesson, pk=pk, module__course__in=owned_courses(request.user))
        return Response(lesson_data(lesson))

    @transaction.atomic
    def patch(self, request, pk):
        lesson, course = lesson_for(request.user, pk)
        editable(course)
        data = validated(LessonWriteSerializer, request.data, instance=lesson, partial=True)
        return Response(lesson_data(save_lesson(lesson, dict(data))))


class LessonQuizView(StudioView):
    def get(self, request, pk):
        lesson = get_object_or_404(Lesson, pk=pk, module__course__in=owned_courses(request.user))
        return Response(quiz_data(lesson.quiz) if hasattr(lesson, 'quiz') else None)

    @transaction.atomic
    def put(self, request, pk):
        lesson, course = lesson_for(request.user, pk)
        editable(course)
        quiz = Quiz.objects.select_for_update().filter(lesson=lesson).first()
        if quiz and (quiz.is_published or quiz.attempts.exists()):
            raise ValidationError({'quiz': 'Published quizzes and quizzes with attempts are locked to preserve historical outcomes.'})
        data = validated(QuizWriteSerializer, request.data)
        questions = data.pop('questions')
        if quiz is None:
            quiz = Quiz(lesson=lesson)
        for key, value in data.items():
            setattr(quiz, key, value)
        quiz.full_clean()
        quiz.save()
        quiz.questions.all().delete()  # Only an unassessed, unpublished draft may be replaced.
        for order, question in enumerate(questions, 1):
            choices = question.pop('choices')
            saved = QuizQuestion.objects.create(quiz=quiz, order=order, **question)
            QuizChoice.objects.bulk_create([QuizChoice(question=saved, order=index, **choice) for index, choice in enumerate(choices, 1)])
        return Response(quiz_data(quiz))


class LessonAssignmentsView(StudioView):
    def get(self, request, pk):
        lesson = get_object_or_404(Lesson, pk=pk, module__course__in=owned_courses(request.user))
        return Response([assignment_data(a) for a in lesson.assignments.all()])

    @transaction.atomic
    def post(self, request, pk):
        lesson, course = lesson_for(request.user, pk)
        editable(course)
        assignment = Assignment.objects.create(lesson=lesson, **validated(AssignmentWriteSerializer, request.data))
        return Response(assignment_data(assignment), status=201)


class AssignmentDetailView(StudioView):
    @transaction.atomic
    def patch(self, request, pk):
        assignment = get_object_or_404(Assignment, pk=pk, lesson__module__course__in=owned_courses(request.user))
        course = course_for(request.user, assignment.lesson.module.course_id, lock=True)
        editable(course)
        if assignment.submissions.exists():
            raise ValidationError('Assignments with submissions cannot be changed in place.')
        data = validated(AssignmentWriteSerializer, request.data, instance=assignment, partial=True)
        for key, value in data.items():
            setattr(assignment, key, value)
        assignment.full_clean()
        assignment.save(update_fields=list(data))
        return Response(assignment_data(assignment))


class LessonImagesView(StudioView):
    @transaction.atomic
    def post(self, request, pk):
        lesson, course = lesson_for(request.user, pk)
        editable(course)
        upload = request.FILES.get('image')
        if not upload or upload.size > 5 * 1024 * 1024:
            raise ValidationError({'image': 'Upload a PNG, JPEG or WebP image up to 5 MB.'})
        if Path(upload.name).suffix.lower() not in ('.png', '.jpg', '.jpeg', '.webp'):
            raise ValidationError({'image': 'Only PNG, JPEG and WebP images are supported.'})
        try:
            image = Image.open(upload)
            if image.format not in ('PNG', 'JPEG', 'WEBP') or image.width * image.height > 16000000:
                raise ValueError
            image.verify()
            upload.seek(0)
            image = Image.open(upload)
            image.load()
            clean = BytesIO()
            # Re-encode to remove metadata and embedded original payloads.
            image.convert('RGB').save(clean, format='PNG')
        except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError):
            raise ValidationError({'image': 'Invalid or oversized image.'})
        decorative = str(request.data.get('decorative', 'false')).lower() == 'true'
        alt = request.data.get('alt_text', {})
        if isinstance(alt, str):
            try:
                alt = json.loads(alt)
            except ValueError:
                alt = {'ru': alt}
        if not isinstance(alt, dict) or set(alt) - {'ru', 'kk', 'en'} or any(not isinstance(v, str) or len(v) > 1000 for v in alt.values()):
            raise ValidationError({'alt_text': 'Provide RU/KK/EN alternative descriptions.'})
        alt = {key: value.strip() for key, value in alt.items() if value.strip()}
        if not decorative and not alt:
            raise ValidationError({'alt_text': 'Informative images require a description.'})
        stored = LessonImage(lesson=lesson, order=(lesson.images.aggregate(value=Max('order'))['value'] or 0) + 1)
        # All validation precedes the storage write. Clean up a new file on DB failure.
        try:
            stored.image.save(f'{uuid4().hex}.png', ContentFile(clean.getvalue()), save=False)
            stored.save()
            LessonImageDescription.objects.create(image=stored, decorative=decorative, alt_text={} if decorative else alt)
        except Exception:
            if stored.image.name:
                stored.image.storage.delete(stored.image.name)
            raise
        return Response(lesson_data(lesson)['images'][-1], status=201)


class CourseSubmissionsView(StudioView):
    def get(self, request, pk):
        course = course_for(request.user, pk)
        # Unsubmitted drafts are private to students, including from instructors.
        submissions = AssignmentSubmission.objects.filter(assignment__lesson__module__course=course).exclude(status='draft').select_related('student', 'assignment__lesson')
        return Response([submission_data(s) for s in submissions.order_by('-submitted_at', '-pk')])


class SubmissionReviewView(StudioView):
    @transaction.atomic
    def post(self, request, pk):
        initial = get_object_or_404(AssignmentSubmission, pk=pk, assignment__lesson__module__course__in=owned_courses(request.user))
        course_for(request.user, initial.assignment.lesson.module.course_id, lock=True)
        submission = AssignmentSubmission.objects.select_for_update().select_related('student', 'assignment__lesson').get(pk=pk)
        if submission.status != 'pending':
            raise ValidationError({'status': 'Only pending submissions can be reviewed.'})
        data = validated(ReviewWriteSerializer, request.data)
        if data['revision'] != submission.revision:
            return Response({'revision': 'Submission changed. Reload before reviewing.'}, status=409)
        submission.status = data['status']
        submission.reviewer_comment = data['reviewer_comment']
        submission.reviewed_at = timezone.now()
        submission.revision += 1
        submission.review_history = submission.review_history + [{'reviewer_id': request.user.pk, 'status': submission.status, 'comment': submission.reviewer_comment, 'reviewed_at': submission.reviewed_at.isoformat(), 'revision': submission.revision}]
        submission.save(update_fields=['status', 'reviewer_comment', 'reviewed_at', 'revision', 'review_history'])
        return Response(submission_data(submission))


class PublicationView(StudioView):
    def get(self, request, pk):
        return Response(publication_status(course_for(request.user, pk)))

    @transaction.atomic
    def post(self, request, pk):
        course = course_for(request.user, pk, lock=True)
        if course.is_published:
            raise ValidationError('This course is already published.')
        if course.publication_requests.filter(status='pending').exists():
            raise ValidationError('A publication request is already pending.')
        source = request.data.get('source_reviewed') is True
        assessment = request.data.get('assessment_reviewed') is True
        missing = [item for item in requirements(course, source_reviewed=source, assessment_reviewed=assessment) if not item['met']]
        if missing:
            raise ValidationError({'requirements': missing})
        review = PublicationRequest.objects.create(course=course, requested_by=request.user, source_reviewed=source, assessment_reviewed=assessment, fingerprint=fingerprint(course))
        PublicationEvent.objects.create(request=review, actor=request.user, decision='requested')
        return Response(publication_data(review), status=201)


class ReviewsView(StudioView):
    def get(self, request):
        if not moderator(request.user):
            raise PermissionDenied('Administrator access required.')
        return Response([publication_data(r) for r in PublicationRequest.objects.select_related('course', 'requested_by', 'reviewed_by')])


class ReviewDecisionView(StudioView):
    def post(self, request, pk):
        note = request.data.get('note', '')
        if not isinstance(note, str) or len(note) > 10000:
            raise ValidationError({'note': 'Provide feedback up to 10000 characters.'})
        review = decide_publication(request_id=pk, reviewer=request.user, decision=request.data.get('decision'), note=note)
        return Response(publication_data(review))


class InstructorsView(StudioView):
    def get(self, request):
        if not moderator(request.user):
            raise PermissionDenied('Administrator access required.')
        return Response(list(get_user_model().objects.filter(is_active=True).order_by('username').values('id', 'username', 'role', 'is_staff', 'is_superuser')))


class InstructorRoleView(StudioView):
    @transaction.atomic
    def post(self, request, pk):
        if not moderator(request.user) or not (request.user.is_superuser or request.user.has_perm('users.change_user')):
            raise PermissionDenied('Real user-management permission is required.')
        user = get_object_or_404(get_user_model().objects.select_for_update(), pk=pk, is_active=True)
        role = request.data.get('role')
        if role not in ('author', 'student') or user.is_staff or user.is_superuser or user.role == 'admin':
            raise ValidationError('Only ordinary student/author roles can be changed here. Staff administration remains in Django Admin.')
        user.role = role
        user.full_clean()
        user.save(update_fields=['role'])
        return Response({'id': user.pk, 'username': user.username, 'role': user.role})


class ImportPreviewView(StudioView):
    def post(self, request):
        from .word import parse_docx
        upload = request.FILES.get('file')
        if not upload or upload.size > 10 * 1024 * 1024:
            raise ValidationError({'file': 'Upload a DOCX file up to 10 MB.'})
        try:
            parsed = parse_docx(upload.read(10 * 1024 * 1024 + 1), upload.name)
        except (ValueError, DjangoValidationError) as error:
            raise ValidationError({'file': str(error)})
        preview_id = str(uuid4())
        token = signing.dumps({'id': preview_id, 'owner': request.user.pk, 'parsed': parsed}, salt='studio-word-preview', compress=True)
        return Response({'id': preview_id, 'preview_token': token, 'parsed': parsed, 'warnings': parsed['warnings']}, status=200)


class ImportConfirmView(StudioView):
    @transaction.atomic
    def post(self, request, pk):
        token = request.data.get('preview_token', '')
        if not isinstance(token, str) or len(token) > 2000000:
            raise ValidationError({'preview_token': 'Invalid preview confirmation.'})
        try:
            signed = signing.loads(token, salt='studio-word-preview', max_age=86400)
        except signing.BadSignature:
            raise ValidationError({'preview_token': 'Preview expired or invalid. Upload and review again.'})
        if signed.get('owner') != request.user.pk or signed.get('id') != str(pk):
            raise ValidationError({'preview_token': 'This preview belongs to another session.'})
        # Serialize confirmations by owner; duplicate confirmation cannot create twice.
        get_user_model().objects.select_for_update().get(pk=request.user.pk)
        preview = ImportPreview.objects.filter(pk=pk, owner=request.user).first()
        if preview and preview.course_id:
            return Response(course_data(preview.course, detail=True))
        parsed = signed['parsed']
        preview = ImportPreview(id=pk, owner=request.user, source_sha256=parsed['source_sha256'], parsed=parsed)
        if CourseImport.objects.filter(source_sha256=preview.source_sha256).exists():
            raise ValidationError('This document has already been imported. Existing content was not changed.')
        fields = {key: value for key, value in request.data.items() if key not in ('lessons', 'preview_token')}
        data = validated(CourseWriteSerializer, fields)
        mapping = request.data.get('lessons')
        original = preview.parsed['lessons']
        if not isinstance(mapping, list) or len(mapping) != len(original) or not mapping:
            raise ValidationError({'lessons': 'Review one lesson mapping per proposed source lesson.'})
        lessons = [dict(validated(LessonWriteSerializer, lesson)) for lesson in mapping]
        course = create_course(request.user, dict(data))
        module = Module.objects.create(course=course, title=preview.parsed.get('title', course.title)[:255], order=1)
        for index, lesson_data_in in enumerate(lessons, 1):
            lesson = save_lesson(Lesson(module=module, order=index), lesson_data_in)
            if not hasattr(lesson, 'learning_content'):
                blocks = original[index-1].get('blocks', [])
                tables = [{'type': 'model_service', 'title': f'Таблица {n+1}', 'headers': block.get('headers', []), 'rows': block.get('rows', [])} for n, block in enumerate(blocks) if block.get('type') == 'table']
                LessonLearningContent.objects.create(lesson=lesson, content_language=course.studio_settings.language, source_sections=[block['text'][:255] for block in blocks if block.get('type') == 'heading'], interactions=tables)
        mapping_digest = hashlib.sha256(json.dumps(mapping, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
        CourseImport.objects.create(course=course, source_name=preview.parsed['source_name'], source_sha256=preview.source_sha256, manifest_sha256=mapping_digest,
                                    content_sha256=fingerprint(course), version='studio-docx-v1', content_language=course.studio_settings.language, review_approved=False)
        preview.course = course
        preview.save()
        return Response(course_data(course, detail=True), status=201)


class SubmissionFileView(StudioView):
    def get(self, request, pk):
        submission = get_object_or_404(AssignmentSubmission, pk=pk, assignment__lesson__module__course__in=owned_courses(request.user))
        if submission.status == 'draft' or not submission.file:
            raise Http404('Submitted file not found.')
        name = submission.file.name
        if not name.startswith('submissions/'):
            raise Http404('Submitted file not found.')
        path = confined_file(settings.MEDIA_ROOT, name)
        root = Path(settings.MEDIA_ROOT).resolve() / 'submissions'
        if not path.is_relative_to(root):
            raise Http404('Submitted file not found.')
        try:
            response = FileResponse(path.open('rb'), as_attachment=True, filename=Path(name).name, content_type='application/octet-stream')
        except (FileNotFoundError, IsADirectoryError, PermissionError):
            raise Http404('Submitted file not found.')
        response['X-Content-Type-Options'] = 'nosniff'
        return response
