"""Exact, idempotent editorial corrections for finalized Module 4. No media writes."""
import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import connection, transaction

from courses.management.commands.import_media_module import create_backup
from courses.models import Course, LessonAttachment

PATCH = Path(settings.BASE_DIR)/'docs/courses/module-4-editorial-corrections.json'


def corrections():
    data=json.loads(PATCH.read_text(encoding='utf-8'))
    course=Course.objects.get(slug='ai-media-content')
    module=course.modules.get(order=4)
    result=[]
    for entry in data['lessons']:
        lesson=module.lessons.get(order=entry['order'])
        before=lesson.text_content
        after=before
        for edit in entry['replacements']:
            if after.count(edit['before'])==1:
                after=after.replace(edit['before'],edit['after'])
            elif after.count(edit['after'])!=1:
                raise CommandError(f'Unexpected lesson {entry["order"]} text; editorial update stopped.')
        if len(before.split('\n\n'))!=len(after.split('\n\n')):
            raise CommandError('Editorial correction would change lesson structure.')
        for heading in lesson.learning_content.source_sections:
            if before.split('\n\n').count(heading)!=after.split('\n\n').count(heading):
                raise CommandError('Editorial correction would change section headings.')
        if after!=before:result.append((lesson,'text_content',before,after))
    for edit in data['captions']:
        row=LessonAttachment.objects.get(lesson__module=module,filename=edit['filename'])
        if row.caption==edit['after']:continue
        if row.caption!=edit['before']:raise CommandError('Unexpected attachment caption; no overwrite.')
        result.append((row,'caption',row.caption,edit['after']))
    return result


class Command(BaseCommand):
    help='Preview or apply only exact approved Module 4 editorial corrections after verified SQLite backup.'

    def add_arguments(self,parser):
        mode=parser.add_mutually_exclusive_group()
        mode.add_argument('--dry-run',action='store_true')
        mode.add_argument('--apply',action='store_true')
        parser.add_argument('--backup-dir',type=Path,default=Path(settings.BASE_DIR)/'.local-course-backups')

    def handle(self,*args,**options):
        plan=corrections()
        self.stdout.write(json.dumps({'mode':'apply' if options['apply'] else 'dry-run','lesson_updates':sum(f=='text_content' for _,f,_,_ in plan),'caption_updates':sum(f=='caption' for _,f,_,_ in plan)}))
        if not options['apply'] or not plan:return
        if connection.vendor!='sqlite' or connection.in_atomic_block:
            raise CommandError('A standalone SQLite transaction is required.')
        previous=connection.transaction_mode
        try:
            connection.transaction_mode='IMMEDIATE'
            with transaction.atomic():
                plan=corrections()
                if not plan:return
                backup=create_backup(settings.DATABASES['default']['NAME'],options['backup_dir'])
                self.stdout.write(f'Verified SQLite backup: {backup}')
                for row,field,before,after in plan:
                    updated=type(row).objects.filter(pk=row.pk,**{field:before}).update(**{field:after})
                    if updated!=1:raise CommandError('Concurrent editorial change; transaction rolled back.')
                if corrections():raise CommandError('Editorial post-validation failed.')
        finally:
            connection.transaction_mode=previous
