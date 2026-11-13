"""Full-length audio-only mixes using the approved master and preview envelopes.

No Remotion rendering, synthesis, video encoding or overwrite of existing outputs.
"""
import argparse
from fractions import Fraction
import json
from pathlib import Path
import subprocess

from prepare_music_preview import ROOT, RATE, read_stereo, preview_stem, sha, write_wav

OUT = ROOT / 'out/final-mixed'
REFERENCE = ROOT / 'out/audio-preview/minimal-tech-ambient-v1-provenance.json'


def probe(path):
    return json.loads(subprocess.check_output([
        'ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(path)
    ]))


def approved_reference():
    reference = json.loads(REFERENCE.read_text())
    expected = dict(music_db=-9, sfx_db=4, duck_music_db=8,
                    duck_attack_seconds=.06, duck_release_seconds=.22,
                    intro_fade_seconds=1.2, preview_outro_fade_seconds=1.8,
                    compression_or_limiter='none', normalize_amix=False)
    if reference['mix'] != expected:
        raise ValueError('Approved mixing parameters changed; refusing to guess')
    for item in reference['outputs']:
        if sha(ROOT/item['path']) != item['sha256']:
            raise ValueError('Approved reference checksum mismatch: '+item['path'])
    master = ROOT / 'out/audio-preview/minimal-tech-ambient-v1-theme-64s.wav'
    m = probe(master)
    audio = next(s for s in m['streams'] if s['codec_type'] == 'audio')
    if (int(audio['sample_rate']), audio['channels'], audio['codec_name']) != (RATE, 2, 'pcm_s24le'):
        raise ValueError('Unexpected approved master audio format')
    return reference, master, float(audio['duration'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--video', default='all', help='Video id in content/videos.json, or all')
    args = parser.parse_args()
    reference, master, master_seconds = approved_reference()
    videos = json.loads((ROOT/'content/videos.json').read_text())
    cues = json.loads((ROOT/'content/sfx-cues.json').read_text())
    selected = [v for v in videos if args.video == 'all' or v['id'] == args.video]
    if not selected:
        parser.error('Unknown video id')
    jobs = []
    for video in selected:
        source = ROOT/'out/final'/(video['filename']+'.mp4')
        output = OUT/(video['filename']+'.mp4')
        stem = OUT/(video['filename']+'-music-stem.wav')
        manifest = OUT/(video['filename']+'-mix.json')
        for path in [output, stem, manifest]:
            if path.exists():
                parser.error(f'Refusing overwrite: {path}')
        if output.resolve() == source.resolve():
            parser.error('Output must not be the original input')
        m = probe(source)
        v = next(s for s in m['streams'] if s['codec_type'] == 'video')
        a = next(s for s in m['streams'] if s['codec_type'] == 'audio')
        fps = Fraction(v['r_frame_rate'])
        seconds = float(Fraction(int(v['nb_frames']), 1)/fps)
        if v['codec_name'] != 'h264' or fps != 30 or float(v.get('start_time',0)) != 0:
            raise ValueError('Unexpected source video format/start')
        if (a['codec_name'], int(a['sample_rate']), a['channels']) != ('aac', RATE, 2):
            raise ValueError('Unexpected source SFX audio format')
        if seconds != video['seconds'] or abs(float(v['duration'])-seconds) > 1e-5:
            raise ValueError('Source duration disagrees with scene data')
        if seconds > master_seconds-2:
            raise ValueError('Master is too short before its original fade; obtain an approved longer/looped master')
        for cue in cues[video['id']]:
            if cue['frame'] < 0 or (cue['frame']+cue['duration'])/30 > seconds:
                raise ValueError('Cue outside source duration')
        jobs.append((video, source, output, stem, manifest, seconds, sha(source)))
    OUT.mkdir(parents=True, exist_ok=True)
    left, right = read_stereo(master)
    for video, source, output, stem, manifest, seconds, source_hash in jobs:
        print('Mixing', video['id'], seconds, 'seconds', flush=True)
        # Reuse the exact approved cue envelope and end fade. The saved master
        # already contains the approved intro. No change to composition/tempo.
        l, r = preview_stem(left, right, cues[video['id']], preview_seconds=seconds)
        write_wav(stem, l, r)
        filters = (f'[0:a:0]atrim=duration={seconds},asetpts=PTS-STARTPTS,volume=-0dB,volume=4dB[sfx];'
                   '[1:a:0]volume=-9dB[music];'
                   '[sfx][music]amix=inputs=2:duration=shortest:normalize=0[mix]')
        command = ['ffmpeg','-hide_banner','-v','error','-n','-i',str(source),'-i',str(stem),
                   '-filter_complex',filters,'-map','0:v:0','-map','[mix]',
                   '-c:v','copy','-c:a','aac','-b:a','192k','-ar',str(RATE),'-ac','2',
                   '-movflags','+faststart',str(output)]
        # No -t, -shortest or frame cap: copy the complete original video stream.
        subprocess.run(command, check=True)
        if sha(source) != source_hash:
            raise RuntimeError('Original source changed during mixing')
        report = dict(video=video['id'], nominal_seconds=seconds,
                      source={'path':str(source.relative_to(ROOT)),'sha256':source_hash},
                      master={'path':str(master.relative_to(ROOT)),'sha256':sha(master)},
                      approved_preview='out/audio-preview/m5-l13-v1-music-approval-v1.mp4',
                      approval='User approved reference music/style/balance in Phase 5G',
                      mix=reference['mix'], cues=cues[video['id']],
                      music_adaptation='Trim exact saved master; no loop, synthesis or time stretch',
                      ffmpeg_command=command,
                      outputs=[{'path':str(p.relative_to(ROOT)),'sha256':sha(p)} for p in [stem,output]])
        manifest.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
        print('Complete:', output, flush=True)


if __name__ == '__main__':
    main()
