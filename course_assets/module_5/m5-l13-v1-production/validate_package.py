"""Read-only package integrity checks; no Django or synthesis required."""
import argparse
from pathlib import Path
import hashlib,json,wave,array,xml.etree.ElementTree as ET
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--require-preview', action='store_true',
                    help='Also require the local, deliberately unversioned preview WAV.')
args = parser.parse_args()
p=Path(__file__).resolve().parent
root=p.parents[2]
video=json.loads((root/'docs/courses/media-module-5-storyboards.json').read_text())['videos'][0]
assert json.loads((p/'storyboard-source.json').read_text())==video
text=(p/'narration-script-ru.txt').read_text().strip()
assert text==video['narration_script_ru']=='\n\n'.join(s['narration_ru'] for s in video['storyboard'])
r=json.loads((p/'narration-provenance.json').read_text())
assert r['transcript']==text and len(r['cues'])==6
preview=p/'narration-preview.wav'
expected_samples=round(r['duration_seconds']*r['sample_rate'])
if args.require_preview and not preview.is_file():
 raise SystemExit('Local preview WAV is missing; source-only validation is still available.')
if preview.is_file():
 assert hashlib.sha256(preview.read_bytes()).hexdigest()==r['sha256']
 with wave.open(str(preview)) as w:
  assert (w.getnchannels(),w.getsampwidth(),w.getframerate())==(1,2,24000)
  assert w.getnframes()/24000==r['duration_seconds']
  samples=array.array('h',w.readframes(w.getnframes()))
  assert 0<max(map(abs,samples))<32767
for cue in r['cues']:
 assert cue['synthesis_input'].replace('+','')==cue['text']
 assert 0<=cue['start_sample']<cue['end_sample']<=expected_samples
for f in (p/'originals').glob('*.svg'):
 ET.parse(f)
 assert 'Вымышленный пример' in f.read_text()
assert len(list((p/'originals').glob('*.svg')))==2
helper=root/'course_assets/module_4/voice_candidates/prepare_roman_module4.py'
assert hashlib.sha256(helper.read_bytes()).hexdigest()==r['pipeline_sha256']
assert (p/'LICENSE_CIS').read_bytes()==(root/'course_assets/module_4/voice_candidates/LICENSE_CIS').read_bytes()
assert not list(p.rglob('*.mp4')) and not list(p.rglob('*.vtt'))
assert (p/'five-scene-storyboard.md').read_text().count('## Сцена ')==5
print('PASS: source narration, synthesis metadata, helper hash, storyboard, 2 SVGs, license, no fake final video/subtitles.')
print('PASS: local WAV checksum/PCM/duration/nonclipping.' if preview.is_file() else
      'SKIP: local preview WAV is not versioned; no playback validation claimed.')
