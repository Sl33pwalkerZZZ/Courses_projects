"""Manifest-driven, create-only import of approved private lesson materials."""
import hashlib
import json
import warnings
from io import BytesIO
from pathlib import Path

from PIL import Image, PngImagePlugin
from django.conf import settings
from django.core.exceptions import ValidationError, ObjectDoesNotExist, MultipleObjectsReturned
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from courses.attachments import attachments_ready, store_attachment
from courses.management.commands.import_media_module import create_backup
from courses.models import Course, LessonImage
from studio.models import LessonImageDescription
from studio.serializers import LessonWriteSerializer


def load_assets(manifest, assets_dir):
    try:
        data = json.loads(Path(manifest).read_text(encoding='utf-8'))
        prepared, skipped, seen = [], [], set()
        root = Path(assets_dir).resolve()
        for entry in data['assets']:
            if entry['status'] not in ('ready_local_not_imported', 'approved'):
                skipped.append(entry['filename'])
                continue
            name = entry['filename']
            if not isinstance(name, str) or Path(name).name != name or '\\' in name or name in seen:
                raise ValueError('Unsafe or duplicate asset name.')
            seen.add(name)
            path = (root / name).resolve()
            if not path.is_relative_to(root) or not path.is_file() or path.stat().st_size > 20*1024*1024:
                raise ValueError(f'Missing, escaping or oversized asset: {name}')
            raw = path.read_bytes()
            if (not isinstance(entry.get('caption_ru'),str) or len(entry['caption_ru']) > 2000
                    or not isinstance(entry.get('alternative_ru'),str) or not entry['alternative_ru'].strip()
                    or not isinstance(entry.get('label_ru'),str) or not entry['label_ru'].strip()):
                raise ValueError('Invalid authored media descriptions.')
            if entry['kind'] == 'image':
                if len(entry['alternative_ru']) > 1000:
                    raise ValueError('Image alternative is too long.')
                if len(raw) > 5*1024*1024 or not name.lower().endswith('.png'):
                    raise ValueError('Image import requires a PNG up to 5 MB.')
                with warnings.catch_warnings():
                    warnings.simplefilter('error', Image.DecompressionBombWarning)
                    with Image.open(BytesIO(raw)) as image:
                        if image.format != 'PNG' or image.width*image.height > 16000000 or getattr(image,'n_frames',1) != 1:
                            raise ValueError('Invalid PNG.')
                        image.verify()
                    with Image.open(BytesIO(raw)) as image:
                        image.load()
                        out = BytesIO()
                        info = PngImagePlugin.PngInfo()
                        info.add_itxt('Description', entry['caption_ru'])
                        image.convert('RGB').save(out, format='PNG', pnginfo=info)
                        raw = out.getvalue()
                if len(raw) > 5*1024*1024:
                    raise ValueError('Decoded PNG too large.')
            elif entry['kind'] not in ('audio','srt'):
                raise ValueError('Unsupported media kind.')
            prepared.append((entry, raw))
        if not prepared:
            raise ValueError('No ready/approved local assets to import.')
        return data, prepared, skipped
    except (OSError, KeyError, ValueError, TypeError, Image.DecompressionBombError, Image.DecompressionBombWarning) as exc:
        raise CommandError(f'Invalid media manifest/assets: {exc}') from exc


def import_plan(data, assets, *, lock=False):
    try:
        qs = Course.objects.select_for_update() if lock else Course.objects.all()
        course = qs.get(slug=data['course_slug'])
        if course.is_published or course.publication_requests.filter(status='pending').exists():
            raise ValueError('Only draft courses without pending publication may be changed.')
        module = course.modules.get(order=data['module_order'], title=data['module_title'])
        plan = []
        for entry, raw in assets:
            lesson = module.lessons.get(order=entry['lesson_order'], title=entry['lesson_title'])
            anchor = entry['after_section']
            learning = lesson.learning_content
            if anchor not in learning.source_sections or lesson.text_content.split('\n\n').count(anchor) != 1:
                raise ValueError('Missing or ambiguous placement anchor.')
            metadata = dict(label=entry['label_ru'],caption=entry['caption_ru'],
                            transcript=entry['alternative_ru'],provenance=entry['provenance'],after_section=anchor)
            if entry['kind'] != 'image':
                # Also validate before migration, without touching its absent table.
                from courses.attachments import validate_file, validate_metadata
                kind, _ = validate_file(entry['filename'], raw)
                if kind != entry['kind']:
                    raise ValueError('Declared media kind conflicts with file signature.')
                validate_metadata(lesson, kind, metadata)
                row, create = store_attachment(lesson,entry['filename'],raw,metadata,[],dry_run=True) if attachments_ready() else (None,True)
                plan.append(dict(lesson=lesson,entry=entry,raw=raw,metadata=metadata,create=create,row=row))
                continue
            filename = f"lessons/{course.slug}/module-{module.order}/{entry['filename']}"
            rows = list(lesson.images.filter(image__endswith='/'+entry['filename']))
            if len(rows) > 1:
                raise ValueError('Duplicate image associations.')
            row = rows[0] if rows else None
            storage = LessonImage._meta.get_field('image').storage
            if row:
                desc = getattr(row,'studio_description',None)
                if row.image.name != filename or not desc or desc.decorative or desc.alt_text != {'ru':entry['alternative_ru']}:
                    raise ValueError('Image metadata conflict.')
                with row.image.storage.open(row.image.name,'rb') as stored:
                    if hashlib.sha256(stored.read()).digest()!=hashlib.sha256(raw).digest():
                        raise ValueError('Image bytes conflict.')
                placement = {'type':'image_placement','image_id':row.pk,'after_section':anchor,'caption':entry['caption_ru']}
                current = [i for i in learning.interactions if i.get('type')=='image_placement' and i.get('image_id')==row.pk]
                if current != [placement]:
                    raise ValueError('Existing image placement conflict.')
            elif storage.exists(filename) or LessonImage.objects.filter(image=filename).exists():
                raise ValueError('Image destination conflict.')
            plan.append(dict(lesson=lesson,entry=entry,raw=raw,filename=filename,create=row is None,row=row))
        return plan
    except (OSError, ValueError, KeyError, TypeError, ObjectDoesNotExist, MultipleObjectsReturned, ValidationError) as exc:
        raise CommandError(f'Media import conflict: {exc}') from exc


class Command(BaseCommand):
    help = 'Preview or explicitly import ready/approved private images, audio and SRT from a course manifest.'

    def add_arguments(self, parser):
        modes=parser.add_mutually_exclusive_group()
        modes.add_argument('--dry-run',action='store_true')
        modes.add_argument('--apply',action='store_true')
        parser.add_argument('--manifest',type=Path,default=Path(settings.BASE_DIR)/'docs/courses/media-module-4-assets.json')
        parser.add_argument('--assets-dir',type=Path,default=Path(settings.BASE_DIR)/'course_assets/module_4')
        parser.add_argument('--backup-dir',type=Path,default=Path(settings.BASE_DIR)/'.local-course-backups')

    def handle(self,*args,**options):
        data, assets, skipped=load_assets(options['manifest'],options['assets_dir'])
        plan=import_plan(data,assets)
        ready=attachments_ready()
        self.stdout.write(json.dumps({'mode':'apply' if options['apply'] else 'dry-run',
            'migration_required':not ready,'create':sum(p['create'] for p in plan),'skipped_unapproved_or_missing_audio':skipped,
            'assets':[{'lesson_id':p['lesson'].pk,'filename':p['entry']['filename'],'kind':p['entry']['kind'],'after_section':p['entry']['after_section']} for p in plan]},ensure_ascii=False))
        if not options['apply'] or not any(p['create'] for p in plan):
            self.stdout.write('No writes (dry-run or unchanged no-op).')
            return
        if not ready:
            raise CommandError('Apply the reviewed courses migration first; no files or records written.')
        if settings.DATABASES['default']['ENGINE']!='django.db.backends.sqlite3':
            raise CommandError('Verified backup workflow requires SQLite.')
        self.stdout.write(f"Verified backup: {create_backup(settings.DATABASES['default']['NAME'],options['backup_dir'])}")
        created_files=[]
        try:
            with transaction.atomic():
                for item in import_plan(data,assets,lock=True):
                    if not item['create']: continue
                    lesson,entry,raw=item['lesson'],item['entry'],item['raw']
                    if entry['kind']!='image':
                        store_attachment(lesson,entry['filename'],raw,item['metadata'],created_files)
                        continue
                    storage=LessonImage._meta.get_field('image').storage
                    name=storage.save(item['filename'],ContentFile(raw))
                    created_files.append((storage,name))
                    if name!=item['filename']:
                        raise CommandError('Storage filename collision; rolling back.')
                    row=LessonImage.objects.create(lesson=lesson,image=name,order=(lesson.images.order_by('-order').values_list('order',flat=True).first() or 0)+1)
                    LessonImageDescription.objects.create(image=row,decorative=False,alt_text={'ru':entry['alternative_ru']})
                    content=lesson.learning_content
                    content.interactions=[*content.interactions,{'type':'image_placement','image_id':row.pk,'after_section':entry['after_section'],'caption':entry['caption_ru']}]
                    validation=LessonWriteSerializer(instance=lesson,data={'learning_content':{'interactions':content.interactions}},partial=True)
                    if not validation.is_valid(): raise CommandError(str(validation.errors))
                    content.save(update_fields=['interactions'])
        except Exception:
            for storage,name in created_files: storage.delete(name)
            raise
        self.stdout.write('Approved local media imported; theory, assessments and publication unchanged.')
