"""Reviewed, create-only or exact-state replacement of Module 4 private media.

No deletion of old storage files. Default dry-run makes no backups or writes.
"""
import hashlib
import json
import os
from pathlib import Path
from uuid import uuid4

from django.conf import settings
from django.core.exceptions import ValidationError, ObjectDoesNotExist, MultipleObjectsReturned
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError
from django.db import connection, transaction
from django.forms.models import model_to_dict
from django.utils.text import get_valid_filename

from courses.attachments import store_attachment, validate_file, validate_metadata
from courses.management.commands.import_lesson_media import import_plan, load_assets
from courses.management.commands.import_media_module import create_backup
from courses.models import Course, LessonAttachment

FIELDS = ('id','lesson','kind','file','filename','mime_type','sha256','label','caption','transcript','provenance','after_section','order')


def snapshot(row):
    data = model_to_dict(row, fields=FIELDS)
    data['id'] = row.pk
    data['lesson_id'] = data.pop('lesson')
    data['file'] = row.file.name
    return data


def private_bytes(row):
    root = (Path(settings.MEDIA_ROOT)/'lessons/attachments').resolve()
    name = row.file.name
    path = Path(row.file.storage.path(name)).resolve()
    if not name.startswith('lessons/attachments/') or not path.is_relative_to(root):
        raise CommandError('Stored attachment escapes private attachment directory.')
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != row.sha256:
        raise CommandError('Stored attachment bytes differ from the expected checksum.')
    return raw


def replacement_plan(data, assets):
    if data['course_slug'] != 'ai-media-content' or data['module_order'] != 4:
        raise CommandError('This reviewed finalizer is restricted to AI Media Module 4.')
    required = {'tts-demonstration','stt-demonstration','srt-example','srt-synchronized','processing-comparison','processing-comparison-filtered','workflow-diagram'}
    if len(data['assets'])!=7 or {e['key'] for e in data['assets']}!=required:
        raise CommandError('Expected exactly the seven reviewed production asset keys.')
    course = Course.objects.get(slug=data['course_slug'])
    if course.is_published or course.publication_requests.filter(status='pending').exists():
        raise CommandError('Course must remain draft without pending publication.')
    module = course.modules.get(order=4, title=data['module_title'])
    plan, claimed = [], set()
    for entry, raw in assets:
        if entry['kind'] == 'image':
            item = import_plan(data, [(entry,raw)])[0]
            # This finalization retains the already imported workflow image, never edits theory.
            if item['create']:
                raise CommandError('Expected existing workflow image is missing; review before proceeding.')
            item['action'] = 'KEEP'
            plan.append(item)
            continue
        lesson = module.lessons.get(order=entry['lesson_order'], title=entry['lesson_title'])
        kind, mime = validate_file(entry['filename'], raw)
        if kind != entry['kind']:
            raise CommandError('File type conflicts with manifest.')
        metadata = dict(label=entry['label_ru'],caption=entry['caption_ru'],transcript=entry['alternative_ru'],
                        provenance=entry['provenance'],after_section=entry['after_section'])
        validate_metadata(lesson, kind, metadata)
        digest = hashlib.sha256(raw).hexdigest()
        canonical = list(lesson.attachments.filter(filename=entry['filename']))
        expected = entry.get('replacement_expected')
        legacy = list(lesson.attachments.filter(pk=expected['id'])) if expected else []
        if len(canonical)>1:
            raise CommandError('Duplicate canonical attachment records.')
        row = canonical[0] if canonical else (legacy[0] if legacy else None)
        if row is not None:
            if row.pk in claimed:
                raise CommandError('Two planned assets claim the same attachment.')
            claimed.add(row.pk)
            private_bytes(row)
            exact = (row.filename==entry['filename'] and row.sha256==digest and row.kind==kind
                     and row.mime_type==mime and all(getattr(row,k)==v for k,v in metadata.items()))
            if exact:
                if expected and (row.pk != expected['id'] or row.lesson_id != expected['lesson_id'] or row.order != expected['order']):
                    raise CommandError('Canonical attachment has an unexpected ID; possible duplicate replacement.')
                action = 'KEEP'
            elif expected and snapshot(row)==expected:
                action = 'REPLACE'
            else:
                raise CommandError(f'Unexpected attachment state for {entry["key"]}; no overwrite allowed.')
        else:
            # Creation is allowed only in a deliberately reviewed empty target, not after losing a pinned row.
            if expected:
                raise CommandError('Pinned legacy attachment is missing; refusing automatic recreation.')
            action = 'CREATE'
        collision = lesson.attachments.filter(sha256=digest)
        if row is not None: collision = collision.exclude(pk=row.pk)
        if collision.exists():
            raise CommandError('Duplicate target content already attached under another record.')
        plan.append(dict(action=action,lesson=lesson,entry=entry,raw=raw,row=row,metadata=metadata,mime=mime))
    existing_ids = set(LessonAttachment.objects.filter(lesson__module=module).values_list('pk',flat=True))
    if existing_ids != claimed:
        raise CommandError('Unexpected extra/duplicate Module 4 attachments; review before replacing.')
    return plan


def verified_bundle(plan, directory):
    """Called inside BEGIN IMMEDIATE, before writes; other SQLite writers are blocked."""
    bundle = Path(directory)/f'module4-media-{uuid4().hex}'
    bundle.mkdir(parents=True, mode=0o700)
    os.chmod(bundle,0o700)
    database = create_backup(settings.DATABASES['default']['NAME'],bundle)
    journal = dict(database=Path(database).name,database_sha256=hashlib.sha256(Path(database).read_bytes()).hexdigest(),
                   records=[],media=[],status='verified_before_replacement')
    for item in plan:
        row = item['row']
        if not row: continue
        if item['entry']['kind']=='image':
            image_path = Path(row.image.storage.path(row.image.name)).resolve()
            if not image_path.is_relative_to((Path(settings.MEDIA_ROOT)/'lessons').resolve()):
                raise CommandError('Workflow image escapes private lesson media.')
            raw = row.image.storage.open(row.image.name,'rb')
            try: payload = raw.read()
            finally: raw.close()
            storage_name = row.image.name
        else:
            payload = private_bytes(row)
            storage_name = row.file.name
            journal['records'].append(snapshot(row))
        path = bundle/'media'/storage_name
        if not path.resolve().is_relative_to((bundle/'media').resolve()):
            raise CommandError('Unsafe media backup path.')
        path.parent.mkdir(parents=True,exist_ok=True)
        with path.open('xb') as file: file.write(payload)
        path.chmod(0o600)
        digest = hashlib.sha256(payload).hexdigest()
        if hashlib.sha256(path.read_bytes()).hexdigest()!=digest:
            raise CommandError('Media backup verification failed.')
        journal['media'].append(dict(storage_name=storage_name,sha256=digest))
    journal_path = bundle/'journal.json'
    with journal_path.open('x',encoding='utf-8') as file: json.dump(journal,file,ensure_ascii=False,indent=2)
    journal_path.chmod(0o600)
    return bundle


def apply_replacement(item, created_files):
    if item['action']=='KEEP': return
    if item['action']=='CREATE':
        store_attachment(item['lesson'],item['entry']['filename'],item['raw'],item['metadata'],created_files)
        return
    row = item['row']
    name = f'lessons/attachments/{uuid4().hex}/{get_valid_filename(item["entry"]["filename"])}'
    name = row.file.storage.save(name,ContentFile(item['raw']))
    created_files.append((row.file.storage,name))
    row.file.name = name
    row.filename = item['entry']['filename']
    row.sha256 = hashlib.sha256(item['raw']).hexdigest()
    row.mime_type = item['mime']
    row.kind = item['entry']['kind']
    for key,value in item['metadata'].items(): setattr(row,key,value)
    row.full_clean()
    row.save(update_fields=['file','filename','sha256','mime_type','kind',*item['metadata']])
    private_bytes(row)


class Command(BaseCommand):
    help = 'Dry-run or explicitly replace reviewed Module 4 media, retaining attachment IDs and old files.'

    def add_arguments(self,parser):
        mode=parser.add_mutually_exclusive_group()
        mode.add_argument('--dry-run',action='store_true')
        mode.add_argument('--apply',action='store_true')
        parser.add_argument('--manifest',type=Path,default=Path(settings.BASE_DIR)/'docs/courses/media-module-4-assets.json')
        parser.add_argument('--assets-dir',type=Path,default=Path(settings.BASE_DIR)/'course_assets/module_4')
        parser.add_argument('--baseline',type=Path,help='Optional private JSON of exact prior row snapshots, keyed by asset key.')
        parser.add_argument('--backup-dir',type=Path,default=Path(settings.BASE_DIR)/'.local-course-backups')

    def handle(self,*args,**options):
        # PRAGMA query_only is connection-local and never changes the database file.
        if not options['apply'] and connection.vendor=='sqlite':
            with connection.cursor() as cursor:
                previous=cursor.execute('PRAGMA query_only').fetchone()[0]
                cursor.execute('PRAGMA query_only=ON')
            try:
                return self._handle(*args,**options)
            finally:
                with connection.cursor() as cursor: cursor.execute(f'PRAGMA query_only={int(previous)}')
        return self._handle(*args,**options)

    def _handle(self,*args,**options):
        try:
            data,assets,skipped=load_assets(options['manifest'],options['assets_dir'])
            if options.get('baseline'):
                baseline=json.loads(options['baseline'].read_text())
                for entry in data['assets']:
                    if entry['kind']!='image':entry['replacement_expected']=baseline[entry['key']]
            plan=replacement_plan(data,assets)
            summary={action:sum(p['action']==action for p in plan) for action in ('CREATE','REPLACE','KEEP')}
            summary['SKIP']=len(skipped)
            self.stdout.write(json.dumps(dict(mode='apply' if options['apply'] else 'dry-run',counts=summary,
                actions=[dict(action=p['action'],filename=p['entry']['filename'],attachment_id=p['row'].pk if p['row'] else None,
                              lesson_order=p['lesson'].order) for p in plan],skipped=skipped),ensure_ascii=False))
            if not options['apply']:
                self.stdout.write('No database, backup or protected-storage writes (dry-run).')
                return
            if data.get('apply_blocked_reason'): raise CommandError(data['apply_blocked_reason'])
            if skipped: raise CommandError('Partial application with skipped/unapproved assets is forbidden.')
            if not any(p['action']!='KEEP' for p in plan):
                self.stdout.write('Already final: no writes or backup required.')
                return
            if connection.vendor!='sqlite' or connection.in_atomic_block:
                raise CommandError('Replacement requires a standalone SQLite transaction.')
            created_files=[]
            old_mode=connection.transaction_mode
            try:
                # SQLite SELECT FOR UPDATE is a no-op: take the write reservation before
                # replanning and making a consistent DB/media backup. No schema/settings edits.
                connection.transaction_mode='IMMEDIATE'
                with transaction.atomic():
                    plan=replacement_plan(data,assets)
                    bundle=verified_bundle(plan,options['backup_dir'])
                    self.stdout.write(f'Verified SQLite/media backup: {bundle}')
                    for item in plan: apply_replacement(item,created_files)
                    final=replacement_plan(data,assets)
                    if any(p['action']!='KEEP' for p in final):
                        raise CommandError('Post-replacement validation failed.')
                    journal_path=bundle/'journal.json'
                    journal=json.loads(journal_path.read_text())
                    journal.update(status='replacement_verified',after_records=[snapshot(p['row']) for p in final if p['entry']['kind']!='image'],
                                   new_storage_names=[name for _,name in created_files])
                    journal_path.write_text(json.dumps(journal,ensure_ascii=False,indent=2))
            except Exception:
                for storage,name in created_files: storage.delete(name)
                raise
            finally:
                connection.transaction_mode=old_mode
            self.stdout.write('Finalized media atomically; IDs/order/old files preserved.')
        except (OSError,ValueError,KeyError,ValidationError,ObjectDoesNotExist,MultipleObjectsReturned) as exc:
            raise CommandError(str(exc)) from exc
