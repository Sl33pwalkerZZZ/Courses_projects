"""Explicit C2 exception: reorder existing choices, never use Studio's replacement PUT."""
import json
from collections import Counter
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import connection, transaction

from courses.management.commands.import_media_module import create_backup
from courses.models import Course
from quizzes.models import Quiz, QuizChoice

MAP = Path(__file__).resolve().parents[1] / 'course10_quiz5_order.json'
SOURCE = MAP.with_name('media_module_6.json')


def load_map():
    data = json.loads(MAP.read_text(encoding='utf-8'))
    if (data['course_id'], data['slug'], data['module_order'], data['lesson_order'], data['lesson_id'], data['quiz']['id']) != (10, 'ai-media-content', 6, 1, 116, 5):
        raise CommandError('C2 map is restricted to Course 10 / Quiz 5 / lesson 116.')
    source = json.loads(SOURCE.read_text(encoding='utf-8'))['quiz']
    expected = {'title': data['quiz']['title'], 'instructions': data['quiz']['instructions'],
                'passing_percentage': 70, 'questions': []}
    positions = []
    for entry in data['questions']:
        rows = entry['choices']
        if (len(rows) != 4 or sorted(v['before']['order'] for v in rows) != [1, 2, 3, 4]
                or sorted(v['after_order'] for v in rows) != [1, 2, 3, 4]
                or sum(bool(v['before']['is_correct']) for v in rows) != 1
                or any(v['before']['question_id'] != entry['question']['id'] for v in rows)):
            raise CommandError('Invalid C2 permutation; nothing changed.')
        positions.extend(v['after_order'] for v in rows if v['before']['is_correct'])
        expected['questions'].append({'text': entry['question']['text'], 'explanation': entry['question']['explanation'],
            'choices': [[v['before']['text'], bool(v['before']['is_correct'])] for v in sorted(rows, key=lambda v: v['after_order'])]})
    if len(data['questions']) != 15 or sorted(Counter(positions).values()) != [3, 4, 4, 4] or source != expected:
        raise CommandError('C2 map/canonical quiz conflict; nothing changed.')
    return data


def plan_reorder():
    data = load_map()
    if not Course.objects.filter(pk=10, slug='ai-media-content', is_published=False).exists():
        raise CommandError('Expected unpublished Course 10.')
    quiz = Quiz.objects.filter(pk=5, lesson_id=116, lesson__module__course_id=10,
                               lesson__module__order=6, lesson__order=1).first()
    if not quiz or Quiz.objects.filter(pk=5).values().get() != data['quiz']:
        raise CommandError('Quiz identity/metadata changed; no overwrite permitted.')
    questions = list(quiz.questions.values())
    if questions != [v['question'] for v in data['questions']]:
        raise CommandError('Question IDs/text/keys/ordering changed; no overwrite permitted.')
    current = list(QuizChoice.objects.filter(question__quiz=quiz).order_by('pk').values())
    before = sorted([v['before'] for q in data['questions'] for v in q['choices']], key=lambda v: v['id'])
    after = sorted([{**v['before'], 'order': v['after_order']} for q in data['questions'] for v in q['choices']], key=lambda v: v['id'])
    if current == after:
        return quiz, [], data
    if current != before:
        raise CommandError('Choice IDs/text/keys/links/order conflict or partial permutation; stopped.')
    # Narrow operation reviewed for an unattempted quiz. New attempts require a fresh review.
    if quiz.attempts.exists():
        raise CommandError('Attempts now exist. Preserve history; obtain a new C2 review before changing order.')
    return quiz, [(a['id'], a['order'], b['order']) for a, b in zip(before, after) if a['order'] != b['order']], data


def write_orders(plan):
    for pk, before, after in plan:
        if QuizChoice.objects.filter(pk=pk, order=before).update(order=after) != 1:
            raise CommandError('Concurrent choice change; transaction rolled back.')


class Command(BaseCommand):
    help = 'Preview/apply pinned Quiz 5 choice order only, with verified backup. No other fields or history writes.'

    def add_arguments(self, parser):
        mode = parser.add_mutually_exclusive_group()
        mode.add_argument('--dry-run', action='store_true')
        mode.add_argument('--apply', action='store_true')
        parser.add_argument('--backup-dir', type=Path, default=Path(settings.BASE_DIR) / '.local-course-backups')

    def handle(self, *args, **options):
        quiz, plan, data = plan_reorder()
        self.stdout.write(json.dumps({'mode': 'apply' if options['apply'] else 'dry-run', 'quiz': quiz.pk,
            'attempt_count': quiz.attempts.count(), 'choice_order_updates': len(plan),
            'other_field_updates': 0, 'status': 'UPDATE' if plan else 'KEEP',
            'correct_positions': [{'question_order': q['question']['order'],
                'before': next(v['before']['order'] for v in q['choices'] if v['before']['is_correct']),
                'after': next(v['after_order'] for v in q['choices'] if v['before']['is_correct'])} for q in data['questions']]}, ensure_ascii=False))
        if not options['apply'] or not plan:
            return
        if connection.vendor != 'sqlite' or connection.in_atomic_block:
            raise CommandError('A standalone SQLite transaction is required.')
        previous = connection.transaction_mode
        try:
            connection.transaction_mode = 'IMMEDIATE'
            with transaction.atomic():
                _, plan, _ = plan_reorder()
                if not plan:
                    return
                backup = create_backup(settings.DATABASES['default']['NAME'], options['backup_dir'])
                self.stdout.write(f'Verified SQLite backup: {backup}')
                write_orders(plan)
                if plan_reorder()[1]:
                    raise CommandError('C2 post-validation failed; rolled back.')
        finally:
            connection.transaction_mode = previous
