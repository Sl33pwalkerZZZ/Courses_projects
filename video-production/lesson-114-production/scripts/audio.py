"""Reuse approved QualityV2 score/FX and licensed speech; no synthesis or source overwrite."""
import sys,json,math,hashlib,subprocess
from pathlib import Path
from array import array
ROOT=Path(__file__).resolve().parents[1]
OLD=ROOT.parent/'lesson-113-production'
sys.path.insert(0,str(OLD/'scripts'))
from prepare_music_preview import read_stereo,write_wav,db,RATE
from quality_v2_audio import rms
DATA=json.loads((ROOT/'content/series.json').read_text())
EVENTS={
 'rough-cut':[(2,'select'),(10,'place'),(17,'place'),(19,'place'),(25,'place'),(34,'place'),(41,'place'),(44,'place'),(52,'finish')],
 'narration-balance':[(1,'select'),(7,'place'),(36,'place'),(58,'finish')],
 'caption-review':[(1,'select'),(28,'place'),(30.5,'place'),(37.2,'place'),(44,'select'),(59.4,'finish')]}
SPEECH={'rough-cut':[],'narration-balance':[12.5,23,41],'caption-review':[8,51]}
def hashfile(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ramp(t,start,end,a,b):
 if t<=start:return a
 if t>=end:return b
 return a+(b-a)*(t-start)/(end-start)
def music_gain(id,t):
 if id=='narration-balance':
  if 11.7<=t<12:return ramp(t,11.7,12,-9,-90)
  if 12<=t<21.6:return -90
  if 21.6<=t<22.5:return ramp(t,21.6,22.5,-90,5)
  if 22.5<=t<33:return 5
  if 33<=t<36:return ramp(t,33,36,5,-9)
 if id=='caption-review':
  for start in SPEECH[id]:
   if start-.3<=t<start:return ramp(t,start-.3,start,-9,-17)
   if start<=t<start+8.5625:return -17
   if start+8.5625<=t<start+8.9:return ramp(t,start+8.5625,start+8.9,-17,-9)
 return -9

def prepare(v):
 base=v['filename'];out=ROOT/'out';n=v['seconds']*RATE
 manifest=out/(base+'-audio.json')
 if manifest.exists():raise SystemExit('Refusing overwrite '+str(manifest))
 master=OLD/'out/audio-preview/minimal-tech-ambient-v1-theme-64s.wav'
 approved=json.loads((OLD/'out/audio-preview/minimal-tech-ambient-v1-provenance.json').read_text());assert hashfile(master)==next(x['sha256'] for x in approved['outputs'] if x['path'].endswith('theme-64s.wav'))
 raw=out/(base+'-filtered.wav');subprocess.run(['ffmpeg','-v','error','-n','-i',str(master),'-af',f'atrim=duration={v["seconds"]},highpass=f=70:p=2,lowpass=f=1800:p=2,afade=t=out:st={v["seconds"]-1.8}:d=1.8:curve=hsin','-ar',str(RATE),'-ac','2','-c:a','pcm_s24le',str(raw)],check=True)
 ml,mr=read_stereo(raw)
 # Fair A/B: identical approved-score excerpt under the identical speech.
 # Crossfades sit outside the speech interval, not across words.
 if v['id']=='narration-balance':
  length=round((8.5625+1)*RATE);ca=ml[10*RATE:10*RATE+length];cb=mr[10*RATE:10*RATE+length]
  for start in [22.5,40.5]:
   offset=round(start*RATE)
   for j in range(length):
    blend=min(1,j/(.4*RATE),(length-1-j)/(.4*RATE));i=offset+j
    ml[i]=ml[i]*(1-blend)+ca[j]*blend;mr[i]=mr[i]*(1-blend)+cb[j]*blend
 sl=array('f',[0])*n;sr=array('f',[0])*n;vl=array('f',[0])*n;vr=array('f',[0])*n
 approvedfx=json.loads((OLD/'out/quality-v2/audio-provenance.json').read_text());fx={};sources=[]
 for name in {x[1] for x in EVENTS[v['id']]}:
  p=OLD/'out/quality-v2/sfx'/(name+'.wav');assert hashfile(p)==next(x['sha256'] for x in approvedfx['outputs'] if x['path'].endswith('sfx/'+name+'.wav'));fx[name]=read_stereo(p);sources.append({'file':str(p),'sha256':hashfile(p)})
 for at,name in EVENTS[v['id']]:
  off=round(at*RATE);a,b=fx[name]
  for i in range(min(len(a),n-off)):sl[off+i]+=a[i];sr[off+i]+=b[i]
 voice=ROOT/'public/f1-speech.wav';speech=json.loads((ROOT/'content/speech.json').read_text());assert hashfile(voice)==speech['sha256'];a,b=read_stereo(voice)
 gain=min(db(-20)/rms(a),.7/max(map(abs,a)))
 for at in SPEECH[v['id']]:
  off=round(at*RATE)
  for i in range(len(a)):vl[off+i]+=a[i]*gain;vr[off+i]+=b[i]*gain
 for i in range(n):
  t=i/RATE;duck=0
  for at,name in EVENTS[v['id']]:
   end=at+len(fx[name][0])/RATE
   if at-.06<=t<at:duck=max(duck,5*(t-at+.06)/.06)
   elif at<=t<=end+.03:duck=5
   elif end+.03<t<end+.25:duck=max(duck,5*(end+.25-t)/.22)
  g=db(music_gain(v['id'],t)-duck);ml[i]*=g;mr[i]*=g
 for suffix,l,r in [('music',ml,mr),('sfx',sl,sr),('speech',vl,vr)]:write_wav(out/(base+'-'+suffix+'.wav'),l,r)
 mixl=array('f',(ml[i]+sl[i]+vl[i] for i in range(n)));mixr=array('f',(mr[i]+sr[i]+vr[i] for i in range(n)));assert max(max(map(abs,mixl)),max(map(abs,mixr)))<.95
 write_wav(out/(base+'-mix.wav'),mixl,mixr)
 manifest.write_text(json.dumps({'video':v['id'],'seconds':v['seconds'],'master_sha256':hashfile(master),'sfx':sources,'events':EVENTS[v['id']],'speech_times':SPEECH[v['id']],'speech_source_sha256':hashfile(voice),'speech_gain_db':20*math.log10(gain),'music':'Approved theme unchanged; base-9dB. Video5 solo intentionally muted, A+5dB,B-9dB with ramps. Video6 speech intervals-17dB. All illustrative, not universal targets.','duck_db':5,'outputs':{p.name:hashfile(p) for p in out.glob(base+'-*.wav')}},ensure_ascii=False,indent=2)+'\n');print('Prepared',v['id'],flush=True)
if __name__=='__main__':
 for v in DATA:prepare(v)
