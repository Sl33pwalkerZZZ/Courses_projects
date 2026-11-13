"""Final AV validation; no database connection or application imports."""
from pathlib import Path
import json,sys,subprocess,hashlib,math
ROOT=Path(__file__).resolve().parents[1];OLD=ROOT.parent/'lesson-113-production'
sys.path.insert(0,str(OLD/'scripts'))
from verify_quality_v2 import probe,packet_hashes,loudness
from quality_v2_audio import decode,rms,log
from prepare_music_preview import RATE

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def frames(p):
 raw=subprocess.check_output(['ffmpeg','-v','error','-xerror','-i',str(p),'-map','0:v:0','-f','framemd5','-'],text=True)
 return [x.rsplit(',',1)[-1].strip() for x in raw.splitlines() if x and not x.startswith('#')]
def main():
 results=[]
 for v in json.loads((ROOT/'content/series.json').read_text()):
  print('Validating',v['id'],flush=True);base=v['filename'];file=ROOT/'out/final'/(base+'.mp4');visual=ROOT/'out/final'/(base+'-visual.mp4');p=probe(file)
  video=next(x for x in p['streams'] if x['codec_type']=='video');audio=next(x for x in p['streams'] if x['codec_type']=='audio')
  assert len(p['streams'])==2
  assert (video['codec_name'],video['pix_fmt'],video['width'],video['height'],video['r_frame_rate'],int(video['nb_frames']))==('h264','yuv420p',1920,1080,'30/1',v['seconds']*30)
  assert audio['codec_name']=='aac' and audio['profile']=='LC' and audio['channels']==2 and int(audio['sample_rate'])==48000
  assert float(video['duration'])==float(audio['duration'])==v['seconds']
  assert packet_hashes(file)==packet_hashes(visual)
  assert frames(file)==frames(visual)
  subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(file),'-f','null','-'],check=True)
  final=decode(file);reference=decode(ROOT/'out'/(base+'-mix.wav'));n=v['seconds']*RATE*2
  assert len(final)>=n and len(reference)==n
  error=math.sqrt(sum((final[i]-reference[i])**2 for i in range(n))/n);assert error<.001
  peak=max(map(abs,final));assert peak<.95
  measure=loudness(file);assert measure['true_peak_dbtp']<-1
  music=decode(ROOT/'out'/(base+'-music.wav'));voice=decode(ROOT/'out'/(base+'-speech.wav'));fx=decode(ROOT/'out'/(base+'-sfx.wav'))
  settings=json.loads((ROOT/'out'/(base+'-audio.json')).read_text());cues=[]
  for at,name in settings['events']:
   start=round(at*RATE)*2;end=start+round({'select':.16,'place':.26,'finish':.55}[name]*RATE)*2
   residual=[final[i]-music[i]-voice[i] for i in range(start,end)];src=fx[start:end]
   corr=sum(x*y for x,y in zip(residual,src))/math.sqrt(sum(x*x for x in src)*sum(y*y for y in residual));assert corr>.95
   cues.append({'seconds':at,'sound':name,'correlation':round(corr,5)})
  ab=None
  if v['id']=='narration-balance':
   count=round(8.5625*RATE)*2;offsets=[round(x*RATE)*2 for x in [12.5,23,41]]
   parts=[voice[x:x+count] for x in offsets];assert parts[0]==parts[1]==parts[2]
   a=music[offsets[1]:offsets[1]+count];b=music[offsets[2]:offsets[2]+count]
   expected=10**(14/20);delta=rms([a[i]-b[i]*expected for i in range(count)]);assert delta<1e-6
   ab={'speech_samples_identical_all_three_passes':True,'music_excerpt_same_speech_interval':True,'music_gain_difference_db':14,'music_scaled_residual_dbfs':round(log(delta),2)}
  results.append({'file':str(file.relative_to(ROOT)),'sha256':sha(file),'bytes':file.stat().st_size,'seconds':v['seconds'],'frames':v['seconds']*30,'video':'H264/yuv420p 1920x1080 30fps','audio':'AAC-LC stereo48kHz','video_packets_and_decoded_frames':'identical_to_visual_source','decode':'PASS','clipped_samples':sum(abs(x)>=1 for x in final),'sample_peak_dbfs':round(log(peak),2),'aac_error_dbfs':round(log(error),2),'cues':cues,'AB':ab,**measure})
 preserved=json.loads((ROOT/'out/qa/preservation.json').read_text());changed=[p for p,h in preserved.items() if not Path(p).is_file() or sha(Path(p))!=h];assert not changed,changed
 report={'status':'PASS','videos':results,'preserved_files':len(preserved),'database_application_lesson113_and_old_assets':'UNCHANGED','subjective_listening':'not human approved; author review required'}
 (ROOT/'out/qa/validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
