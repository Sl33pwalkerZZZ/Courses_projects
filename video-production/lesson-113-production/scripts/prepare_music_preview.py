"""Original offline ambient theme and one stream-copy approval preview; stdlib only.

Never edits Remotion scenes or approved finals. Run from the package directory.
"""
from array import array
from pathlib import Path
import argparse
import hashlib
import json
import math
import random
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
RATE = 48000
BPM = 72
BEAT = 60 / BPM
SEED = 1132026
OUT = ROOT / 'out/audio-preview'


def db(value):
    return 10 ** (value / 20)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_wav(path, left, right):
    pcm = array('f', (sample for pair in zip(left, right) for sample in pair))
    if sys.byteorder != 'little':
        pcm.byteswap()
    subprocess.run(['ffmpeg', '-v', 'error', '-n', '-f', 'f32le', '-ar', str(RATE),
                    '-ac', '2', '-i', 'pipe:0', '-c:a', 'pcm_s24le', str(path)],
                   input=pcm.tobytes(), check=True)


def read_stereo(path):
    raw = subprocess.check_output(['ffmpeg','-v','error','-i',str(path),'-f','f32le','-ar',str(RATE),'-ac','2','-'])
    pcm = array('f'); pcm.frombytes(raw)
    if sys.byteorder != 'little':
        pcm.byteswap()
    return pcm[::2],pcm[1::2]


def compose(seconds):
    size = round(seconds * RATE)
    left, right = array('f', [0]) * size, array('f', [0]) * size

    def voice(start, duration, frequency, amplitude, pan, kind, phase=0):
        offset = round(start * RATE)
        count = min(round(duration * RATE), size - offset)
        gl, gr = math.sqrt((1-pan)/2), math.sqrt((1+pan)/2)
        for i in range(max(0, count)):
            t = i / RATE
            if kind == 'pad':
                envelope = min(1, t / 1.15) * min(1, (duration-t)/1.45)
                envelope = math.sin(max(0, envelope) * math.pi/2) ** 2
                value = (math.sin(math.tau*frequency*t+phase)
                         + .16*math.sin(math.tau*frequency*2*t+phase)
                         + .22*math.sin(math.tau*frequency*1.0017*t+phase+.7))
                value *= .93+.07*math.sin(math.tau*.09*t+phase)
            elif kind == 'bell':
                envelope = min(1, t/.018) * math.exp(-t/0.55)
                envelope *= min(1, max(0, (duration-t)/.25))
                value = math.sin(math.tau*frequency*t)+.12*math.sin(math.tau*frequency*2.003*t)
            else:
                envelope = min(1, t/.035) * math.exp(-t/.075)
                envelope *= min(1, max(0, (duration-t)/.05))
                value = math.sin(math.tau*frequency*t)
            value *= amplitude * envelope
            left[offset+i] += value*gl
            right[offset+i] += value*gr

    # Original sparse voicings: Dmaj9 -> Bm7 -> Gmaj9 -> Aadd9; no borrowed melody.
    voicings = [(50,57,61,64), (47,57,62,66), (55,59,62,69), (57,61,64,71)]
    motif = [(66,69,76,73), (66,74,69,73), (67,71,74,69), (69,76,73,71)]
    chord_seconds = 8*BEAT
    chord_index = 0
    while chord_index*chord_seconds < seconds:
        start = chord_index*chord_seconds
        notes = voicings[chord_index % 4]
        for j, note in enumerate(notes):
            voice(start, chord_seconds+1.6, 440*2**((note-69)/12),
                  .030 if j < 2 else .022, [-.48,.42,-.22,.26][j], 'pad', j*.43)
        for j, note in enumerate(motif[chord_index % 4]):
            voice(start+(j*2+.5)*BEAT, 2.4, 440*2**((note-69)/12),
                  .027 if j in [0,2] else .020, [-.32,.28,-.12,.36][j], 'bell')
        for j in [1,3,5,7]:
            voice(start+j*BEAT, .45, 440*2**((notes[0]+12-69)/12), .012, 0, 'pulse')
        chord_index += 1
    rng = random.Random(SEED)
    fl = fr = 0
    for i in range(size):
        fl = .985*fl + .015*rng.uniform(-1,1)
        fr = .985*fr + .015*rng.uniform(-1,1)
        left[i] += .0018*fl
        right[i] += .0018*fr
        t = i/RATE
        fade = min(1,t/1.2) * min(1,(seconds-t)/2)
        fade = math.sin(max(0,fade)*math.pi/2)**2
        left[i] *= fade
        right[i] *= fade
    peak = max(max(map(abs,left)),max(map(abs,right)))
    gain = db(-12)/peak
    for channel in [left,right]:
        for i in range(size):
            channel[i] *= gain
    return left,right


def preview_stem(left, right, cues, preview_seconds=19.9):
    # All cue windows derive from the existing animation-frame schedule.
    count = round(preview_seconds*RATE)
    left,right = left[:count],right[:count]
    active_cues = [c for c in cues if c['frame']/30 < preview_seconds]
    for i in range(count):
        t = i/RATE
        attenuation = 0.0
        for cue in active_cues:
            start,end = cue['frame']/30,(cue['frame']+cue['duration'])/30
            if start-.06 <= t < start:
                attenuation = max(attenuation, 8*(t-start+.06)/.06)
            elif start <= t <= end+.03:
                attenuation = 8
            elif end+.03 < t < end+.25:
                attenuation = max(attenuation,8*(end+.25-t)/.22)
        fade = math.sin(min(1,max(0,(preview_seconds-t)/1.8))*math.pi/2)**2
        gain = db(-attenuation)*fade
        left[i] *= gain
        right[i] *= gain
    return left,right


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--music-db', type=float, default=-9)
    parser.add_argument('--sfx-db', type=float, default=4)
    parser.add_argument('--tag', default='v1')
    args = parser.parse_args()
    if not args.tag.replace('-','').isalnum():
        parser.error('tag must be alphanumeric with optional hyphens')
    if not (-60 <= args.music_db <= 0 and -24 <= args.sfx_db <= 12):
        parser.error('Unsafe level: music -60..0 dB; SFX -24..12 dB')
    OUT.mkdir(parents=True,exist_ok=True)
    source = ROOT/'out/final/m5-l13-v1-source-organization.mp4'
    prefix = f'minimal-tech-ambient-{args.tag}'
    master = OUT/f'{prefix}-theme-64s.wav'
    stem = OUT/f'{prefix}-preview-music-stem.wav'
    preview = OUT/f'm5-l13-v1-music-approval-{args.tag}.mp4'
    for path in [master,stem,preview,OUT/f'{prefix}-provenance.json']:
        if path.exists():
            parser.error(f'Refusing overwrite: {path}; use a new --tag')
    original_hash = sha(source)
    left,right = compose(64)
    write_wav(master,left,right)
    cues = json.loads((ROOT/'content/sfx-cues.json').read_text())['source-organization']
    active_cues = [c for c in cues if c['frame']/30 < 19.9]
    left,right = read_stereo(master)
    left,right = preview_stem(left,right,cues)
    write_wav(stem,left,right)
    filters = (f'[0:a:0]atrim=duration=19.9,asetpts=PTS-STARTPTS,volume={args.sfx_db}dB[sfx];'
               f'[1:a:0]volume={args.music_db}dB[music];'
               '[sfx][music]amix=inputs=2:duration=shortest:normalize=0[mix]')
    command = ['ffmpeg','-hide_banner','-v','error','-n','-i',str(source),'-i',str(stem),
               '-filter_complex',filters,'-map','0:v:0','-map','[mix]','-c:v','copy',
               '-c:a','aac','-b:a','192k','-frames:v','597','-t','19.9','-movflags','+faststart',str(preview)]
    subprocess.run(command,check=True)
    assert sha(source) == original_hash, 'Original final changed!'
    report = {
        'title':'Minimal Tech Ambient — original Lesson 113 approval theme',
        'method':'Offline Python standard library additive sine synthesis; deterministic filtered procedural noise; no external audio, pretrained model, borrowed melody or vocals.',
        'sample_rate':RATE,'channels':2,'master_format':'PCM signed 24-bit WAV',
        'tempo_bpm':BPM,'seed':SEED,'harmonic_progression':['Dmaj9','Bm7','Gmaj9','Aadd9'],
        'phrase':'Two bars per chord, eight-bar repeating harmony; four sparse original notes per chord; warm sine pads and soft non-drum pulses.',
        'synthesis':{'pad_attack_seconds':1.15,'pad_release_seconds':1.45,'pad_detune_ratio':1.0017,'bell_attack_seconds':.018,'bell_decay_seconds':.55,'noise_lowpass_coefficient':.985,'master_sample_peak_dbfs':-12},
        'mix':{'music_db':args.music_db,'sfx_db':args.sfx_db,'duck_music_db':8,'duck_attack_seconds':.06,'duck_release_seconds':.22,'intro_fade_seconds':1.2,'preview_outro_fade_seconds':1.8,'compression_or_limiter':'none','normalize_amix':False},
        'source':{'path':str(source.relative_to(ROOT)),'sha256':original_hash,'segment_seconds':[0,19.9]},
        'cue_frames':[c['frame'] for c in active_cues],
        'outputs':[{ 'path':str(p.relative_to(ROOT)),'sha256':sha(p)} for p in [master,stem,preview]],
        'ffmpeg_mix_command':command,
        'approval':'Pending author listening review; not integrated; originals unchanged',
        'reuse':'Change requested synthesis duration and score data for future videos; no time stretching. Retain a separate output tag for every mix experiment.'
    }
    (OUT/f'{prefix}-provenance.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__ == '__main__':
    main()
