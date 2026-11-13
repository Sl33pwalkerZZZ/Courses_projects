"""Decode renders, validate metadata, SFX headroom/correlation, pacing and provenance."""
from array import array
from pathlib import Path
import hashlib,json,math,subprocess,sys,wave
ROOT=Path(__file__).resolve().parents[1]
FPS=30;RATE=48000
videos=json.loads((ROOT/'content/videos.json').read_text())
cues=json.loads((ROOT/'content/sfx-cues.json').read_text())
selected=next((a.split('=',1)[1] for a in sys.argv if a.startswith('--video=')),None)
if selected:videos=[v for v in videos if v['id']==selected]
assert videos,'Unknown video selection'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def decode_audio(path):
    raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(path),'-map','0:a:0','-ac','1','-ar',str(RATE),'-f','f32le','-'])
    pcm=array('f');pcm.frombytes(raw)
    if sys.byteorder!='little':pcm.byteswap()
    return pcm

def sound(name):
    with wave.open(str(ROOT/'public/sfx'/f'{name}.wav'),'rb') as w:
        assert (w.getnchannels(),w.getsampwidth(),w.getframerate())==(1,2,RATE)
        pcm=array('h',w.readframes(w.getnframes()))
    if sys.byteorder!='little':pcm.byteswap()
    return [v/32768 for v in pcm]

sounds={name:sound(name) for name in ['click','whoosh','pop','drop','complete']}
report={'status':'PASS','source_checks':[],'renders':[]}
for v in videos:
    assert v['seconds']==sum(s['seconds'] for s in v['scenes'])
    assert (ROOT/'transcripts'/f"{v['filename']}.ru.md").is_file()
    max_rate=max(len((s['title']+' '+s['instruction']+' '+s['note']).split())/(s['seconds']-.9) for s in v['scenes'])
    assert max_rate<=3.5
    last=-1
    for c in cues[v['id']]:
        assert isinstance(c['frame'],int) and c['frame']>=last
        assert c['frame']+c['duration']<=v['seconds']*FPS
        last=c['frame']+c['duration']
    report['source_checks'].append(dict(video=v['id'],seconds=v['seconds'],scenes=len(v['scenes']),max_words_per_second=round(max_rate,2),cues=len(cues[v['id']]),transcript='PASS'))
    for mode in ['previews','final']:
        path=ROOT/'out'/mode/(v['filename']+('-preview' if mode=='previews' else '')+'.mp4')
        if not path.exists():
            if '--previews-only' in sys.argv and mode=='final':continue
            raise SystemExit('Missing output: '+str(path))
        meta=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(path)]))
        video=next(s for s in meta['streams'] if s['codec_type']=='video')
        audio=next(s for s in meta['streams'] if s['codec_type']=='audio')
        assert len(meta['streams'])==2
        assert video['codec_name']=='h264' and video['pix_fmt']=='yuv420p'
        assert (video['width'],video['height'])==((960,540) if mode=='previews' else (1920,1080))
        assert video['r_frame_rate']=='30/1' and int(video['nb_frames'])==v['seconds']*FPS
        assert abs(float(meta['format']['duration'])-v['seconds'])<.05
        assert audio['codec_name']=='aac'
        subprocess.run(['ffmpeg','-v','error','-xerror','-nostdin','-i',str(path),'-f','null','-'],check=True,capture_output=True)
        pcm=decode_audio(path);peak=max(map(abs,pcm));assert 0<peak<.95
        rms=math.sqrt(sum(x*x for x in pcm)/len(pcm))
        correlations=[]
        for cue in cues[v['id']]:
            start=round(cue['frame']/FPS*RATE)
            reference=sounds[cue['sound']]
            actual=pcm[start:start+len(reference)]
            assert len(actual)==len(reference)
            energy=sum(x*x for x in actual);ref_energy=sum(x*x for x in reference)
            correlation=sum(x*y for x,y in zip(actual,reference))/math.sqrt(energy*ref_energy)
            assert correlation>.8,(v['id'],cue['scene'],cue['sound'],correlation)
            correlations.append(correlation)
        report['renders'].append(dict(file=str(path.relative_to(ROOT)),sha256=sha(path),bytes=path.stat().st_size,
            width=video['width'],height=video['height'],fps=30,frames=int(video['nb_frames']),duration=float(meta['format']['duration']),
            audio_codec=audio['codec_name'],audio_sample_rate=int(audio['sample_rate']),peak_dbfs=round(20*math.log10(peak),2),rms_dbfs=round(20*math.log10(rms),2),clipped_samples=sum(abs(x)>=1 for x in pcm),
            minimum_cue_correlation=round(min(correlations),4),decode='PASS',sfx_frame_alignment='PASS'))
output=ROOT/'out'/(('preview-verification'+('-'+selected if selected else '')+'.json') if '--previews-only' in sys.argv else 'technical-validation.json')
output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False,indent=2))
