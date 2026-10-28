"""Bounded signature validation and private attachment persistence, no new storage."""
import hashlib
import io
import re
import wave
from pathlib import Path
from uuid import uuid4

from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db import connection
from django.utils.text import get_valid_filename

from .models import LessonAttachment

MAX_AUDIO = 20 * 1024 * 1024
MAX_SRT = 1024 * 1024


def attachments_ready():
    # Deliberate compatibility gate while the additive migration awaits approval.
    # No cache: applying a migration in another process takes effect immediately.
    return LessonAttachment._meta.db_table in connection.introspection.table_names()


def validate_srt(raw):
    try:
        text = raw.decode('utf-8-sig').replace('\r\n', '\n')
    except UnicodeDecodeError as exc:
        raise ValidationError('SRT must be UTF-8.') from exc
    if '\x00' in text or any(ord(c) < 32 and c not in '\n\t\r' for c in text):
        raise ValidationError('Invalid subtitle control characters.')
    blocks = re.split(r'\n\s*\n', text.strip())
    last = -1
    for number, block in enumerate(blocks, 1):
        lines = block.splitlines()
        if len(lines) < 3 or lines[0] != str(number) or not ''.join(lines[2:]).strip():
            raise ValidationError('Invalid SRT cue structure.')
        match = re.fullmatch(r'(\d{2,3}):(\d{2}):(\d{2}),(\d{3}) --> (\d{2,3}):(\d{2}):(\d{2}),(\d{3})', lines[1])
        if not match:
            raise ValidationError('Invalid SRT timestamps.')
        values = list(map(int, match.groups()))
        if any(values[i] >= 60 for i in (1, 2, 5, 6)):
            raise ValidationError('Invalid SRT time values.')
        def millis(v):
            return ((v[0] * 60 + v[1]) * 60 + v[2]) * 1000 + v[3]
        start, end = millis(values[:4]), millis(values[4:])
        if start < last or end <= start:
            raise ValidationError('Subtitle cues must have positive, ordered nonoverlapping intervals.')
        last = end
    return text


def validate_mp3(raw):
    """Check complete MPEG Layer III frame boundaries, not only an ID3 prefix."""
    offset = 0
    if raw.startswith(b'ID3'):
        if len(raw) < 10 or raw[3] not in (2, 3, 4) or any(n & 128 for n in raw[6:10]):
            raise ValidationError('Invalid MP3 tag.')
        size = sum(n << (7 * (3-i)) for i, n in enumerate(raw[6:10]))
        offset = 10 + size + (10 if raw[3] == 4 and raw[5] & 16 else 0)
    end = len(raw) - 128 if raw[-128:-125] == b'TAG' else len(raw)
    frames = 0
    while offset < end:
        if offset + 4 > end:
            raise ValidationError('Truncated MP3 frame.')
        a, b, c, _ = raw[offset:offset+4]
        version, layer, bitrate, rate = (b >> 3) & 3, (b >> 1) & 3, c >> 4, (c >> 2) & 3
        if a != 255 or b & 224 != 224 or version == 1 or layer != 1 or bitrate in (0, 15) or rate == 3:
            raise ValidationError('Unsupported or invalid MP3 frames.')
        rates = [44100, 48000, 32000]
        sample_rate = rates[rate] // (1 if version == 3 else 2 if version == 2 else 4)
        bitrates = [0,32,40,48,56,64,80,96,112,128,160,192,224,256,320] if version == 3 else [0,8,16,24,32,40,48,56,64,80,96,112,128,144,160]
        length = (144 if version == 3 else 72) * bitrates[bitrate] * 1000 // sample_rate + ((c >> 1) & 1)
        if length < 4 or offset + length > end:
            raise ValidationError('Truncated MP3 payload.')
        offset += length
        frames += 1
    if frames < 2:
        raise ValidationError('MP3 requires at least two complete audio frames.')


def validate_file(filename, raw):
    if not isinstance(filename, str) or Path(filename).name != filename or '\\' in filename:
        raise ValidationError('Use a plain attachment filename.')
    suffix = Path(filename).suffix.lower()
    limit = MAX_SRT if suffix == '.srt' else MAX_AUDIO
    if not isinstance(raw, bytes) or not raw or len(raw) > limit:
        raise ValidationError('Empty or oversized lesson attachment.')
    if suffix == '.srt':
        validate_srt(raw)
        return 'srt', 'application/x-subrip'
    if suffix == '.wav':
        if not raw.startswith(b'RIFF') or raw[8:12] != b'WAVE':
            raise ValidationError('Expected a RIFF/WAVE file.')
        try:
            with wave.open(io.BytesIO(raw), 'rb') as audio:
                expected = audio.getnframes() * audio.getnchannels() * audio.getsampwidth()
                if (audio.getcomptype() != 'NONE' or audio.getnchannels() not in (1,2)
                        or audio.getsampwidth() not in (1,2,3,4) or not 8000 <= audio.getframerate() <= 192000
                        or expected <= 0 or len(audio.readframes(audio.getnframes())) != expected):
                    raise ValidationError('Unsupported or truncated PCM WAV.')
        except (wave.Error, EOFError) as exc:
            raise ValidationError('Invalid PCM WAV.') from exc
        return 'audio', 'audio/wav'
    if suffix == '.mp3':
        validate_mp3(raw)
        return 'audio', 'audio/mpeg'
    raise ValidationError('Only MP3, PCM WAV and UTF-8 SRT are supported.')


def validate_metadata(lesson, kind, metadata):
    limits = {'label':255,'caption':2000,'transcript':20000,'provenance':4000,'after_section':255}
    if set(metadata) != set(limits):
        raise ValidationError('Unexpected attachment metadata fields.')
    for key, maximum in limits.items():
        if not isinstance(metadata[key], str) or len(metadata[key]) > maximum:
            raise ValidationError(f'Invalid {key}.')
    if not metadata['label'].strip() or not metadata['provenance'].strip() or (kind == 'audio' and not metadata['transcript'].strip()):
        raise ValidationError('A label, provenance and audio transcript/equivalent are required.')
    anchor = metadata['after_section']
    learning = getattr(lesson, 'learning_content', None)
    if anchor and (not learning or anchor not in learning.source_sections or lesson.text_content.split('\n\n').count(anchor) != 1):
        raise ValidationError('Unknown or ambiguous section anchor.')


def store_attachment(lesson, filename, raw, metadata, created_files, *, dry_run=False):
    """Caller owns atomic transaction/course lock and cleans files on rollback."""
    kind, mime = validate_file(filename, raw)
    validate_metadata(lesson, kind, metadata)
    digest = hashlib.sha256(raw).hexdigest()
    existing = LessonAttachment.objects.filter(lesson=lesson, sha256=digest).first()
    if existing:
        if existing.filename != filename or any(getattr(existing,k) != v for k,v in metadata.items()):
            raise ValidationError('Existing attachment bytes have conflicting metadata; no overwrite permitted.')
        if not existing.file.storage.exists(existing.file.name):
            raise ValidationError('Existing attachment file is missing.')
        with existing.file.storage.open(existing.file.name, 'rb') as stored:
            if hashlib.sha256(stored.read()).hexdigest() != digest:
                raise ValidationError('Existing attachment file conflicts.')
        return existing, False
    if LessonAttachment.objects.filter(lesson=lesson, filename=filename).exists():
        raise ValidationError('This lesson already contains a conflicting attachment filename.')
    row = LessonAttachment(lesson=lesson, filename=filename, kind=kind, mime_type=mime, sha256=digest,
                           order=(lesson.attachments.order_by('-order').values_list('order',flat=True).first() or 0)+1, **metadata)
    if dry_run:
        return row, True
    name = f'lessons/attachments/{uuid4().hex}/{get_valid_filename(filename)}'
    name = row.file.storage.save(name, ContentFile(raw))
    created_files.append((row.file.storage,name))
    row.file.name = name
    row.full_clean()
    row.save()
    return row, True
