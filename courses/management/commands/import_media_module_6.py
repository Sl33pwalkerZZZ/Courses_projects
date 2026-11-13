"""Create the approved Course 10 final-assessment structure; preview by default."""
import hashlib
import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from certificates.models import CourseCertificatePolicy
from courses.management.commands.import_media_module import create_backup
from courses.models import Assignment, Course, Lesson, LessonLearningContent, Module
from quizzes.models import Quiz, QuizChoice, QuizQuestion

COURSE_ID = 10
COURSE_SLUG = 'ai-media-content'
MODULE_TITLE = 'Итоговая аттестация и получение сертификата'
LESSON_TITLE = 'Итоговая аттестация по курсу'
SOURCE = Path(__file__).resolve().parents[1] / 'media_module_6.json'


def load_source():
    try:
        raw = SOURCE.read_bytes()
        data = json.loads(raw.decode('utf-8'))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CommandError(f'Invalid Module 6 source: {exc}') from exc
    if set(data) != {'module', 'lesson', 'assignment', 'quiz'} or data['module'] != MODULE_TITLE:
        raise CommandError('Unexpected Module 6 source schema.')
    lesson, assignment, quiz = data['lesson'], data['assignment'], data['quiz']
    if (set(lesson) != {'title', 'objectives', 'source_sections', 'text_content'} or lesson['title'] != LESSON_TITLE
            or not isinstance(lesson['objectives'], list) or len(lesson['objectives']) != 3
            or not isinstance(lesson['source_sections'], list) or len(lesson['source_sections']) != 6
            or not all(isinstance(item, str) and item.strip() for item in lesson['objectives'] + lesson['source_sections'])
            or not isinstance(lesson['text_content'], str) or not lesson['text_content'].strip()):
        raise CommandError('Module 6 lesson must have three objectives and six nonempty sections.')
    if assignment != {'type': 'text', 'description': assignment.get('description'), 'learning_activity': 'final_media_project'} or not assignment['description'].strip():
        raise CommandError('Unexpected final assignment schema.')
    questions = quiz.get('questions') if isinstance(quiz, dict) else None
    if (set(quiz) != {'title', 'instructions', 'passing_percentage', 'questions'} or quiz['passing_percentage'] != 70
            or not isinstance(questions, list) or len(questions) != 15):
        raise CommandError('The final quiz must have exactly 15 questions at 70%.')
    for item in questions:
        if set(item) != {'text', 'explanation', 'choices'} or not all(isinstance(item[key], str) and item[key].strip() for key in ('text', 'explanation')):
            raise CommandError('Each final question requires text and explanation.')
        choices = item['choices']
        if not isinstance(choices, list) or len(choices) != 4 or sum(bool(choice[1]) for choice in choices) != 1:
            raise CommandError('Each final question must have four choices and exactly one correct answer.')
        if any(not isinstance(choice, list) or len(choice) != 2 or not isinstance(choice[0], str) or not choice[0].strip() or type(choice[1]) is not bool for choice in choices):
            raise CommandError('Invalid final quiz choice.')
    return data, hashlib.sha256(raw).hexdigest()


def target_course(*, lock=False):
    courses = Course.objects.select_for_update() if lock else Course.objects
    course = courses.filter(pk=COURSE_ID, slug=COURSE_SLUG, is_published=False).first()
    if not course:
        raise CommandError('Expected unpublished Course 10 with its exact slug.')
    orders = list(course.modules.order_by('order').values_list('order', flat=True))
    lesson_count = Lesson.objects.filter(module__course=course).count()
    if (orders, lesson_count) not in (([1, 2, 3, 4, 5], 15), ([1, 2, 3, 4, 5, 6], 16)):
        raise CommandError('Course 10 module ordering changed; no write permitted.')
    return course


def existing_state(course, source):
    matches = course.modules.filter(order=6) | course.modules.filter(title=MODULE_TITLE)
    if matches.count() > 1:
        raise CommandError('Conflicting Module 6 records; no overwrite permitted.')
    module = matches.first()
    if not module:
        return None
    lesson = module.lessons.filter(order=1, title=LESSON_TITLE).first()
    if module.title != MODULE_TITLE or module.order != 6 or module.lessons.count() != 1 or not lesson:
        raise CommandError('Existing Module 6 conflicts with the approved structure.')
    learning = getattr(lesson, 'learning_content', None)
    assignment = lesson.assignments.filter(learning_activity='final_media_project').first()
    quiz = getattr(lesson, 'quiz', None)
    if (not learning or learning.objectives != source['lesson']['objectives'] or learning.source_sections != source['lesson']['source_sections']
            or lesson.text_content != source['lesson']['text_content'] or not assignment
            or assignment.type != source['assignment']['type'] or assignment.description != source['assignment']['description']
            or not quiz or quiz.title != source['quiz']['title'] or quiz.instructions != source['quiz']['instructions']
            or quiz.passing_percentage != 70 or quiz.is_published or quiz.questions.count() != 15):
        raise CommandError('Existing Module 6 content conflicts; no overwrite permitted.')
    policy = CourseCertificatePolicy.objects.filter(course=course).first()
    if not policy or policy.enabled or policy.issuer_approved or policy.issuer_name or policy.final_quiz_id != quiz.pk:
        raise CommandError('Existing Course 10 certificate policy conflicts; no overwrite permitted.')
    expected_ids = set(Lesson.objects.filter(module__course=course, module__order__lte=5).values_list('pk', flat=True))
    if set(policy.required_lessons.values_list('pk', flat=True)) != expected_ids or set(policy.required_assignments.values_list('pk', flat=True)) != {assignment.pk}:
        raise CommandError('Existing Course 10 certificate scope conflicts; no overwrite permitted.')
    return module


class Command(BaseCommand):
    help = 'Preview or explicitly create Course 10 Module 6 final assessment; never publishes.'

    def add_arguments(self, parser):
        mode = parser.add_mutually_exclusive_group()
        mode.add_argument('--dry-run', action='store_true')
        mode.add_argument('--apply', action='store_true')
        parser.add_argument('--backup-dir', type=Path, default=Path(settings.BASE_DIR) / '.local-course-backups')

    def handle(self, *args, **options):
        source, source_hash = load_source()
        course = target_course()
        existing = existing_state(course, source)
        if existing:
            self.stdout.write('Module 6 already exists unchanged: no-op.')
            return
        self.stdout.write(json.dumps({'mode': 'apply' if options['apply'] else 'dry-run', 'course_id': course.pk,
            'module': MODULE_TITLE, 'module_order': 6, 'lesson': LESSON_TITLE, 'create': {
                'modules': 1, 'lessons': 1, 'learning_content': 1, 'assignments': 1, 'quizzes': 1,
                'questions': 15, 'choices': 60, 'certificate_policies': 1},
            'policy': {'enabled': False, 'issuer_approved': False, 'required_instructional_lessons': 15},
            'source_sha256': source_hash, 'published': False}, ensure_ascii=False))
        if not options['apply']:
            self.stdout.write('Dry-run only: no database or backup writes.')
            return
        if settings.DATABASES['default']['ENGINE'] != 'django.db.backends.sqlite3':
            raise CommandError('A verified SQLite backup is required before import.')
        backup = create_backup(settings.DATABASES['default']['NAME'], options['backup_dir'])
        self.stdout.write(f'Verified SQLite backup: {backup}')
        with transaction.atomic():
            course = target_course(lock=True)
            if existing_state(course, source):
                self.stdout.write('Module 6 already exists unchanged: no-op.')
                return
            module = Module.objects.create(course=course, title=MODULE_TITLE, order=6)
            lesson = Lesson.objects.create(module=module, title=LESSON_TITLE, order=1, text_content=source['lesson']['text_content'])
            LessonLearningContent.objects.create(lesson=lesson, content_language='ru', objectives=source['lesson']['objectives'], source_sections=source['lesson']['source_sections'], interactions=[])
            assignment = Assignment.objects.create(lesson=lesson, **source['assignment'])
            quiz = Quiz.objects.create(lesson=lesson, title=source['quiz']['title'], instructions=source['quiz']['instructions'], passing_percentage=70, is_published=False)
            for order, item in enumerate(source['quiz']['questions'], 1):
                question = QuizQuestion.objects.create(quiz=quiz, text=item['text'], type='single', order=order, explanation=item['explanation'])
                QuizChoice.objects.bulk_create([QuizChoice(question=question, text=text, is_correct=correct, order=choice_order) for choice_order, (text, correct) in enumerate(item['choices'], 1)])
            policy = CourseCertificatePolicy.objects.create(course=course, enabled=False, issuer_name='', issuer_approved=False, final_quiz=quiz)
            policy.required_lessons.add(*Lesson.objects.filter(module__course=course, module__order__lte=5))
            policy.required_assignments.add(assignment)
        self.stdout.write('Created draft Module 6 with a draft quiz and disabled certificate policy. Course publication state is unchanged.')
