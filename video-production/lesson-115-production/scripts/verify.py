"""Read-only source and approved-deliverable verification. Never renders or imports."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
from fractions import Fraction

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]


def check(condition, message):
    if not condition:
        raise ValueError(message)


def verify_vtt(text, duration):
    check(text.startswith('WEBVTT'), 'Missing WEBVTT header')
    cues = re.findall(r'(\d{2}:\d{2}:\d{2}\.\d{3}) --> (\d{2}:\d{2}:\d{2}\.\d{3})[^\n]*\n([^\n]+)', text)
    check(bool(cues), 'No valid subtitle cues')
    check(text.count('-->') == len(cues), 'Malformed subtitle timing')
    previous = 0.0
    for start, end, label in cues:
        def seconds(value):
            h, m, s = value.split(':')
            check(int(m) < 60 and float(s) < 60, 'Invalid timestamp')
            return int(h) * 3600 + int(m) * 60 + float(s)
        a, b = seconds(start), seconds(end)
        check(previous <= a < b <= duration + 0.05, 'Overlapping/out-of-bounds subtitles')
        check(bool(label.strip()), 'Empty subtitle')
        previous = b
    return len(cues)


def verify_hash(path, expected):
    check(path.is_file(), f'Missing asset: {path}')
    with path.open('rb') as source:
        digest = hashlib.file_digest(source, 'sha256').hexdigest()
    check(digest == expected, f'Checksum mismatch: {path.name}')


def verify_video(data, asset):
    streams = data['streams']
    video = [s for s in streams if s['codec_type'] == 'video']
    audio = [s for s in streams if s['codec_type'] == 'audio']
    check(len(video) == len(audio) == 1, 'Expected one video and one audio stream')
    v, a = video[0], audio[0]
    check((v['codec_name'], v['width'], v['height'], v['pix_fmt']) == ('h264', 1920, 1080, 'yuv420p'), 'Invalid video profile')
    check(Fraction(v['avg_frame_rate']) == 30, 'Invalid FPS')
    check(int(v['nb_frames']) == asset['duration_frames'], 'Frame count mismatch')
    check((a['codec_name'], int(a['sample_rate']), a['channels']) == ('aac', 48000, 2), 'Invalid audio profile')
    check(abs(float(v['duration']) - asset['duration_seconds']) < .1, 'Video duration mismatch')
    check(abs(float(a['duration']) - float(v['duration'])) < .15, 'Audio/video duration mismatch')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-only', action='store_true', help='No final media required; NOT a deliverable QA pass')
    args = parser.parse_args()
    for script in ('test_content.py', 'test_background_music.py', 'test_verify.py'):
        subprocess.run([sys.executable, '-B', str(ROOT / 'scripts' / script)], cwd=ROOT, check=True)
    package = json.loads((ROOT / 'package.json').read_text())
    lock = json.loads((ROOT / 'package-lock.json').read_text())
    for key in ('dependencies', 'devDependencies', 'engines'):
        check(lock['packages'][''][key] == package[key], f'Lock mismatch: {key}')
    if args.source_only:
        print('PASS source-only; final media NOT verified')
        return
    plan = json.loads((REPO / 'courses/management/lesson115_final_video_integration.json').read_text())
    assets = plan['assets']
    videos = {a['pair_key']: a for a in assets if a['kind'] == 'video'}
    check(len(assets) == 6 and len(videos) == 3, 'Expected three video/subtitle pairs')
    check(len({a['path'] for a in assets}) == 6, 'Duplicate asset path')
    for key in videos:
        pair = [a for a in assets if a['pair_key'] == key]
        check(len(pair) == 2 and sum(a['kind'] == 'video' for a in pair) == 1, 'Invalid subtitle pair')
    for asset in assets:
        path = (REPO / asset['path']).resolve()
        check(path.is_relative_to(ROOT / 'out/final-bgm'), 'Unexpected final asset location')
        verify_hash(path, asset['sha256'])
        if asset['kind'] == 'video':
            probe = subprocess.run(['ffprobe', '-v', 'error', '-show_streams', '-of', 'json', str(path)], capture_output=True, text=True, check=True)
            verify_video(json.loads(probe.stdout), asset)
        else:
            video = videos[asset['pair_key']]
            check(asset['after_section'] == video['after_section'], 'Subtitle placement mismatch')
            count = verify_vtt(path.read_text(), video['duration_seconds'])
            print(f'PASS {path.name}: {count} cues')
    print('PASS six approved assets: SHA-256, Full HD/30, AAC stereo/48 kHz, timing and VTT. No writes.')


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, subprocess.CalledProcessError) as exc:
        print(f'FAIL: {exc}', file=sys.stderr)
        sys.exit(1)
