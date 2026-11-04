"""Fail-closed MP4 profile checks using an existing system ffprobe executable."""
import json
import math
import shutil
import subprocess
import tempfile
import re
from fractions import Fraction
from django.conf import settings
from django.core.exceptions import ValidationError


def video_limit():
    return int(getattr(settings, 'LESSON_VIDEO_MAX_BYTES', 250 * 1024 * 1024))


def validate_video(raw):
    if len(raw) < 16 or raw[4:8] != b'ftyp' or raw[8:12] not in (b'isom', b'iso2', b'mp41', b'mp42', b'avc1'):
        raise ValidationError('Expected an ISO MP4 file.')
    executable = getattr(settings, 'LESSON_FFPROBE', None) or shutil.which('ffprobe')
    if not executable:
        raise ValidationError('MP4 validation requires the system ffprobe executable; video upload is disabled.')
    try:
        with tempfile.NamedTemporaryFile(suffix='.mp4') as stream:
            stream.write(raw)
            stream.flush()
            result = subprocess.run([executable, '-v', 'error', '-protocol_whitelist', 'file', '-show_streams', '-show_format', '-of', 'json', stream.name], capture_output=True, timeout=20, check=True)
        info = json.loads(result.stdout)
        streams = info['streams']
        videos = [s for s in streams if s['codec_type'] == 'video']
        audio = [s for s in streams if s['codec_type'] == 'audio']
        duration = float(info['format']['duration'])
        if (not math.isfinite(duration) or duration <= 0 or len(videos) != 1 or len(audio) > 1
                or len(streams) != len(videos)+len(audio)
                or videos[0]['codec_name'] != 'h264' or videos[0].get('pix_fmt') != 'yuv420p'
                or videos[0].get('profile') not in ('Baseline', 'Constrained Baseline', 'Main', 'High')
                or not 0 < int(videos[0].get('level', 0)) <= 51
                or not 0 < float(Fraction(videos[0].get('avg_frame_rate', '0'))) <= 60
                or not 0 < int(videos[0]['width']) <= 3840 or not 0 < int(videos[0]['height']) <= 2160
                or any(s['codec_name'] != 'aac' or int(s.get('channels', 0)) not in (1, 2) or s.get('profile') != 'LC' or int(s.get('sample_rate', 0)) not in (44100, 48000) for s in audio)):
            raise ValidationError('Use one H.264/yuv420p video stream (up to 3840×2160), optional mono/stereo AAC audio.')
    except (OSError, subprocess.SubprocessError, ValueError, KeyError, TypeError, AttributeError, IndexError, ZeroDivisionError, OverflowError) as exc:
        raise ValidationError('MP4 metadata could not be safely validated.') from exc


def validate_vtt(raw):
    try:
        text = raw.decode('utf-8-sig').replace('\r\n', '\n')
    except UnicodeDecodeError as exc:
        raise ValidationError('WebVTT must be UTF-8.') from exc
    if (not text.startswith('WEBVTT\n\n') or '<' in text
            or any(ord(c) < 32 and c not in '\n\t' for c in text)):
        raise ValidationError('Expected plain-text WebVTT cues without embedded markup.')
    blocks = re.split(r'\n\s*\n', text.strip())
    if len(blocks) < 2 or blocks[0] != 'WEBVTT':
        raise ValidationError('WebVTT requires a header and at least one cue.')
    last = -1
    for block in blocks[1:]:
        lines = block.splitlines()
        if '-->' not in lines[0]:
            lines = lines[1:]  # Optional cue identifier.
        if len(lines) < 2 or not ''.join(lines[1:]).strip() or any('-->' in line for line in lines[1:]):
            raise ValidationError('Each WebVTT cue requires timestamps and readable text.')
        line = lines[0]
        match = re.fullmatch(r'(\d{2}):(\d{2}):(\d{2})\.(\d{3}) --> (\d{2}):(\d{2}):(\d{2})\.(\d{3})', line)
        if not match:
            raise ValidationError('Use HH:MM:SS.mmm WebVTT timestamps.')
        v = list(map(int, match.groups()))
        if any(v[i] >= 60 for i in (1, 2, 5, 6)):
            raise ValidationError('Invalid WebVTT timestamps.')
        start = ((v[0]*60+v[1])*60+v[2])*1000+v[3]
        end = ((v[4]*60+v[5])*60+v[6])*1000+v[7]
        if start < last or end <= start:
            raise ValidationError('WebVTT cues must be ordered and nonoverlapping.')
        last = end
