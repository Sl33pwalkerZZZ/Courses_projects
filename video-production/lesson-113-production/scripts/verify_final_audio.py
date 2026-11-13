"""Full-file video identity, SFX timing, fades and loudness checks for final mixes."""
from array import array
import argparse
import json
import math
import re
import subprocess
import sys

from mix_final_audio import OUT, ROOT, RATE, approved_reference, probe
from prepare_music_preview import sha


def rms(samples):
    return math.sqrt(sum(x*x for x in samples)/len(samples))


def db(value):
    return 20*math.log10(max(1e-12,value))


def decode(path):
    raw = subprocess.check_output(['ffmpeg','-v','error','-i',str(path),'-map','0:a:0',
                                   '-ac','2','-ar',str(RATE),'-f','f32le','-'])
    pcm = array('f'); pcm.frombytes(raw)
    if sys.byteorder != 'little':
        pcm.byteswap()
    return pcm


def frames(path):
    text = subprocess.check_output(['ffmpeg','-v','error','-xerror','-i',str(path),
                                    '-map','0:v:0','-f','framemd5','-'],text=True)
    return [line.split(',')[-1].strip() for line in text.splitlines()
            if line and not line.startswith('#')]


def packets(path):
    return json.loads(subprocess.check_output([
        'ffprobe','-v','error','-select_streams','v:0','-show_packets','-show_data_hash','sha256',
        '-show_entries','packet=pts_time,dts_time,duration_time,data_hash','-of','json',str(path)
    ]))['packets']


def levels(path):
    result = subprocess.run(['ffmpeg','-hide_banner','-nostdin','-i',str(path),
                             '-af','loudnorm=I=-23:TP=-1.5:LRA=11:print_format=json',
                             '-f','null','-'],check=True,capture_output=True,text=True)
    text = result.stderr
    m = json.loads(text[text.rfind('{'):text.rfind('}')+1])
    # Read input measurements only. Nothing is normalized or written.
    return dict(integrated_lufs=float(m['input_i']),true_peak_dbtp=float(m['input_tp']),
                loudness_range_lu=float(m['input_lra']))


def faststart(path):
    boxes = []
    with path.open('rb') as f:
        while header := f.read(8):
            if len(header) != 8:
                break
            size = int.from_bytes(header[:4],'big'); name = header[4:].decode('ascii')
            head = 8
            if size == 1:
                size = int.from_bytes(f.read(8),'big'); head = 16
            boxes.append(name)
            if not size:
                break
            f.seek(size-head,1)
    return boxes.index('moov') < boxes.index('mdat')


def validate(video):
    base = video['filename']
    manifest = json.loads((OUT/(base+'-mix.json')).read_text())
    source = ROOT/manifest['source']['path']
    output = OUT/(base+'.mp4');stem = OUT/(base+'-music-stem.wav')
    assert sha(source) == manifest['source']['sha256']
    for item in manifest['outputs']:
        assert sha(ROOT/item['path']) == item['sha256']
    assert sha(ROOT/manifest['master']['path']) == manifest['master']['sha256']
    m = probe(output); original_meta = probe(source)
    v = next(s for s in m['streams'] if s['codec_type']=='video')
    a = next(s for s in m['streams'] if s['codec_type']=='audio')
    ov = next(s for s in original_meta['streams'] if s['codec_type']=='video')
    seconds = manifest['nominal_seconds']
    for key in ['codec_name','pix_fmt','width','height','r_frame_rate','nb_frames','duration','start_time']:
        assert v[key] == ov[key], (video['id'],key,v[key],ov[key])
    assert (a['codec_name'],a['channels'],int(a['sample_rate'])) == ('aac',2,RATE)
    assert abs(float(a['duration'])-seconds) < 1/RATE
    assert float(a['start_time']) == float(v['start_time']) == 0
    assert len(m['streams']) == 2
    assert packets(output) == packets(source), 'Compressed video packets or timestamps changed'
    output_frames, source_frames = frames(output), frames(source)
    assert output_frames == source_frames
    assert len(output_frames) == int(v['nb_frames']) == round(seconds*30)
    assert faststart(output), 'moov must precede mdat for browser playback'
    subprocess.run(['ffmpeg','-v','error','-xerror','-nostdin','-i',str(output),'-f','null','-'],
                   check=True,capture_output=True)
    original,music,mixed = decode(source),decode(stem),decode(output)
    n = round(seconds*RATE)*2
    assert len(original) >= n and len(mixed) >= n and len(music) == n
    gm,gs = 10**(-9/20),10**(4/20)
    error = math.sqrt(sum((mixed[i]-original[i]*gs-music[i]*gm)**2 for i in range(n))/n)
    assert error < .001, 'Unexpected mix level or audio offset'
    peak = max(map(abs,mixed));clipped = sum(abs(x)>=1 for x in mixed)
    assert peak < .98 and clipped == 0
    cues=[]
    for cue in manifest['cues']:
        first=round(cue['frame']/30*RATE)*2
        last=round((cue['frame']+cue['duration'])/30*RATE)*2
        x=original[first:last]
        y=[mixed[i]-music[i]*gm for i in range(first,last)]
        correlation=sum(i*j for i,j in zip(x,y))/math.sqrt(sum(i*i for i in x)*sum(j*j for j in y))
        assert correlation>.95, (video['id'],cue,correlation)
        cues.append(dict(frame=cue['frame'],sound=cue['sound'],
                         residual_correlation=round(correlation,5),
                         sfx_over_music_rms_db=round(db(rms(x)*gs)-db(rms(music[first:last])*gm),2)))
    window=RATE # stereo samples in half a second
    windows=[rms(music[i:i+window])*gm for i in range(window,n-window,window)]
    assert min(windows)>1e-5, 'Unintended music silence'
    edge=round(.05*RATE)*2
    start_rms,end_rms=db(rms(music[:edge])*gm),db(rms(music[-edge:])*gm)
    assert start_rms < -70 and end_rms < -70
    # Same-channel adjacent samples, not alternating L/R values.
    max_step=max(abs(music[i]-music[i-2])*gm for i in range(2,n))
    assert max_step < .05, 'Unexpected abrupt music transition'
    regions={}
    for name,time in [('beginning',0),('middle',seconds/2-.5),('ending',seconds-1)]:
        first=round(time*RATE)*2;last=first+RATE*2
        regions[name]={'time_seconds':time,'mix_rms_dbfs':round(db(rms(mixed[first:last])),2),
                       'music_rms_dbfs':round(db(rms(music[first:last])*gm),2),
                       'mix_peak_dbfs':round(db(max(map(abs,mixed[first:last]))),2)}
    prefix_match=None
    if video['id']=='source-organization':
        approved=decode(ROOT/'out/audio-preview/minimal-tech-ambient-v1-preview-music-stem.wav')
        # The approved excerpt's outro starts at 18.1 s; full-length outro is later.
        prefix_samples=round(18.1*RATE)*2
        assert music[:prefix_samples] == approved[:prefix_samples]
        prefix_match=18.1
    loudness=levels(output)
    assert loudness['true_peak_dbtp'] < -1
    report=dict(video=video['id'],file=str(output.relative_to(ROOT)),sha256=sha(output),
                width=v['width'],height=v['height'],fps=30,frames=len(output_frames),
                video_duration=float(v['duration']),audio_duration=float(a['duration']),
                container_duration=float(m['format']['duration']),video_codec=v['codec_name'],
                pixel_format=v['pix_fmt'],audio_codec=a['codec_name'],channels=a['channels'],
                sample_rate=int(a['sample_rate']),audio_bitrate=int(a['bit_rate']),
                decode='PASS',packet_hashes_and_timestamps='IDENTICAL',decoded_pictures='IDENTICAL',
                moov_before_mdat=True,music='continuous exact approved master excerpt; no loop or stretch',
                approved_music_prefix_identical_seconds=prefix_match,
                sample_peak_dbfs=round(db(peak),2),mean_dbfs=round(db(rms(mixed)),2),
                clipped_samples=clipped,aac_mix_error_dbfs=round(db(error),2),
                minimum_sfx_residual_correlation=round(min(c['residual_correlation'] for c in cues),5),
                cues=cues,minimum_music_500ms_rms_dbfs=round(db(min(windows)),2),
                music_start_50ms_rms_dbfs=round(start_rms,2),music_end_50ms_rms_dbfs=round(end_rms,2),
                maximum_music_adjacent_sample_step=round(max_step,6),regions=regions,**loudness)
    (OUT/(base+'-validation.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    return report


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--video',default='all')
    args=parser.parse_args()
    approved_reference()
    videos=json.loads((ROOT/'content/videos.json').read_text())
    selected=[v for v in videos if args.video=='all' or v['id']==args.video]
    if not selected:
        parser.error('Unknown video id')
    reports=[]
    for video in selected:
        print('Validating',video['id'],flush=True)
        reports.append(validate(video))
        print('PASS:',video['id'],flush=True)
    report={'status':'PASS','reference':'Author approved preview; unchanged style and gains',
            'scope':'audio-only copies; no Remotion renderer used','videos':reports}
    name='validation.json' if args.video=='all' else f'validation-{args.video}.json'
    (OUT/name).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':
    main()
