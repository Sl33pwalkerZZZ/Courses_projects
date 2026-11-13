"""Validate audio preview, unchanged compressed pictures and preserved SFX; stdlib."""
from array import array
from pathlib import Path
import hashlib
import json
import math
import re
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'out/audio-preview'
TAG=sys.argv[1] if len(sys.argv)>1 else 'v1'
if not TAG.replace('-','').isalnum():
    raise SystemExit('Invalid tag')
metadata=json.loads((OUT/f'minimal-tech-ambient-{TAG}-provenance.json').read_text())
source=ROOT/metadata['source']['path']
preview=OUT/f'm5-l13-v1-music-approval-{TAG}.mp4'
stem=OUT/f'minimal-tech-ambient-{TAG}-preview-music-stem.wav'
master=OUT/f'minimal-tech-ambient-{TAG}-theme-64s.wav'
RATE=48000


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def probe(p):
    return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(p)]))


def decode(p):
    raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-t','20','-map','0:a:0','-ac','2','-ar',str(RATE),'-f','f32le','-'])
    a=array('f');a.frombytes(raw)
    if sys.byteorder!='little':a.byteswap()
    return a


def db(x):
    return 20*math.log10(max(x,1e-12))


def rms(x):
    return math.sqrt(sum(v*v for v in x)/len(x))


def analysis(p):
    result=subprocess.run(['ffmpeg','-hide_banner','-nostdin','-i',str(p),'-af','volumedetect','-f','null','-'],capture_output=True,text=True,check=True)
    mean=float(re.search(r'mean_volume: ([-\d.]+) dB',result.stderr)[1])
    peak=float(re.search(r'max_volume: ([-\d.]+) dB',result.stderr)[1])
    result=subprocess.run(['ffmpeg','-hide_banner','-nostdin','-i',str(p),'-af','loudnorm=I=-23:TP=-1.5:LRA=11:print_format=json','-f','null','-'],capture_output=True,text=True,check=True)
    # Analysis only: no normalization is applied to any saved asset.
    loud=json.loads(result.stderr[result.stderr.rfind('{'):result.stderr.rfind('}')+1])
    return dict(mean_dbfs=mean,sample_peak_dbfs=peak,integrated_lufs=float(loud['input_i']),true_peak_dbtp=float(loud['input_tp']),lra_lu=float(loud['input_lra']))


def packets(p):
    m=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_packets','-show_data_hash','sha256','-show_entries','packet=pts_time,dts_time,data_hash','-of','json',str(p)]))
    return m['packets']


assert sha(source)==metadata['source']['sha256']
for item in metadata['outputs']:
    assert sha(ROOT/item['path'])==item['sha256']
report={'status':'PASS','files':{},'checks':{}}
for p in [source,master,stem,preview]:
    m=probe(p)
    subprocess.run(['ffmpeg','-v','error','-xerror','-nostdin','-i',str(p),'-f','null','-'],check=True,capture_output=True)
    report['files'][p.name]={'sha256':sha(p),'duration':float(m['format']['duration']),'audio':next(s for s in m['streams'] if s['codec_type']=='audio'),**analysis(p)}
original_packets=packets(source);mixed_packets=packets(preview)
assert mixed_packets==original_packets[:len(mixed_packets)],'Video packet/timestamp mismatch'
report['checks']['copied_video_packets_identical']=len(mixed_packets)
# Also compare actual decoded pictures, not only compressed packets.
def frames(p):
    text=subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-map','0:v:0','-f','framemd5','-'],text=True)
    return [line.split(',')[-1].strip() for line in text.splitlines() if line and not line.startswith('#')]
a,b=frames(source),frames(preview)
assert b==a[:len(b)],'Decoded visual mismatch'
report['checks']['decoded_pictures_identical']=len(b)
m=probe(preview);v=next(s for s in m['streams'] if s['codec_type']=='video');audio=next(s for s in m['streams'] if s['codec_type']=='audio')
assert (v['codec_name'],v['width'],v['height'],v['r_frame_rate'],v['pix_fmt'])==('h264',1920,1080,'30/1','yuv420p')
assert audio['codec_name']=='aac' and audio['channels']==2 and int(audio['sample_rate'])==RATE
assert 19.85<=float(m['format']['duration'])<=20.05
assert abs(float(v.get('start_time',0))-float(audio.get('start_time',0)))<1/30
sfx=decode(source);music=decode(stem);mixed=decode(preview)
n=min(len(sfx),len(music),len(mixed));gain_music=10**(metadata['mix']['music_db']/20);gain_sfx=10**(metadata['mix']['sfx_db']/20)
expected=array('f',(sfx[i]*gain_sfx+music[i]*gain_music for i in range(n)))
error=rms([mixed[i]-expected[i] for i in range(n)])
report['checks']['aac_mix_error_rms_dbfs']=round(db(error),2)
assert error<.001,'Unexpected mix or alignment error'
assert max(map(abs,mixed))<.98
report['checks']['clipped_samples']=sum(abs(x)>=1 for x in mixed)
assert report['checks']['clipped_samples']==0
cue_report=[]
for c in json.loads((ROOT/'content/sfx-cues.json').read_text())['source-organization']:
    if c['frame']/30>=20:continue
    start=round(c['frame']/30*RATE)*2;end=min(n,round((c['frame']+c['duration'])/30*RATE)*2)
    original=sfx[start:end]
    residual=[mixed[i]-music[i]*gain_music for i in range(start,end)]
    corr=sum(x*y for x,y in zip(original,residual))/math.sqrt(sum(x*x for x in original)*sum(y*y for y in residual))
    assert corr>.9,(c,corr)
    music_rms=rms(music[start:end])*gain_music
    assert db(rms(original)*gain_sfx)-db(music_rms)>1, 'SFX masked by music in cue window'
    cue_report.append({'frame':c['frame'],'sound':c['sound'],'sfx_residual_correlation':round(corr,4),'sfx_rms_dbfs':round(db(rms(original)*gain_sfx),2),'music_rms_dbfs_during_cue':round(db(music_rms),2)})
report['checks']['sfx_cues']=cue_report
# Check non-cue music continuity and smooth endpoints, without claiming listening approval.
window=RATE*2//2
music_windows=[rms(music[i:i+window])*gain_music for i in range(window,n-window,window)]
assert min(music_windows)>1e-5,'Unexpected silent music gap'
report['checks']['interior_music_500ms_rms_range_dbfs']=[round(db(min(music_windows)),2),round(db(max(music_windows)),2)]
edge=round(.05*RATE)*2
report['checks']['music_start_50ms_rms_dbfs']=round(db(rms(music[:edge])*gain_music),2)
report['checks']['music_end_50ms_rms_dbfs']=round(db(rms(music[-edge:])*gain_music),2)
report['checks']['fade_in_and_out']='raised-cosine gain envelopes; measured endpoints near silence'
report['checks']['human_listening_approval']='PENDING'
report['original_finals']=[{'file':str(p.relative_to(ROOT)),'sha256':sha(p),'levels':analysis(p)} for p in sorted((ROOT/'out/final').glob('*.mp4'))]
(OUT/f'validation-{TAG}.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False,indent=2))
