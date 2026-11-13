"""Read-only validation of all three QualityV2 files; never renders Video1."""
from pathlib import Path
import json,hashlib,math,subprocess
from prepare_music_preview import ROOT,RATE,sha
from quality_v2_audio import decode,rms,log,EVENTS
from verify_quality_v2 import probe,packet_hashes,loudness
from phase5h_audio import events_for

OUT=ROOT/'out/quality-v2'
DATA=json.loads((ROOT/'content/quality-v2/series.json').read_text())


def decoded_frames(path):
    result=subprocess.check_output(['ffmpeg','-v','error','-xerror','-i',str(path),'-map','0:v:0','-f','framemd5','-'],text=True)
    return [line.split(',')[-1].strip() for line in result.splitlines() if line and not line.startswith('#')]


def validate(base,seconds,visual,audio,music,sfx,events):
    path=OUT/(base+'.mp4');m=probe(path)
    v=next(s for s in m['streams'] if s['codec_type']=='video');a=next(s for s in m['streams'] if s['codec_type']=='audio')
    assert len(m['streams'])==2
    assert (v['codec_name'],v['pix_fmt'],v['width'],v['height'],v['r_frame_rate'],int(v['nb_frames']))==('h264','yuv420p',1920,1080,'30/1',seconds*30)
    assert a['codec_name']=='aac' and a['profile']=='LC' and a['channels']==2 and int(a['sample_rate'])==RATE
    assert float(v['duration'])==float(a['duration'])==seconds
    assert float(v['start_time'])==float(a['start_time'])==0
    assert packet_hashes(path)==packet_hashes(visual)
    actual,reference=decoded_frames(path),decoded_frames(visual)
    assert actual==reference and len(actual)==seconds*30
    for p in [path,audio,music,sfx]:
        subprocess.run(['ffmpeg','-v','error','-xerror','-nostdin','-i',str(p),'-f','null','-'],capture_output=True,check=True)
    mixed,expected=decode(path),decode(audio);bed,fx=decode(music),decode(sfx)
    n=seconds*RATE*2
    assert len(mixed)>=n and len(expected)==len(bed)==len(fx)==n
    error=math.sqrt(sum((mixed[i]-expected[i])**2 for i in range(n))/n)
    assert error<.001
    peak=max(map(abs,mixed));assert peak<.95
    clipped=sum(abs(x)>=1 for x in mixed);assert not clipped
    cues=[];durations={'select':.16,'place':.26,'finish':.55};gm=10**(-9/20)
    for e in events:
        first=round(e['frame']/30*RATE)*2;last=first+round(durations[e['sound']]*RATE)*2
        source=fx[first:last];residual=[mixed[i]-bed[i]*gm for i in range(first,last)]
        corr=sum(x*y for x,y in zip(source,residual))/math.sqrt(sum(x*x for x in source)*sum(y*y for y in residual))
        assert corr>.95,(base,e,corr)
        cues.append({**e,'correlation':round(corr,5)})
    interior=[rms(bed[i:i+RATE])*gm for i in range(RATE,n-RATE,RATE)]
    assert min(interior)>1e-5
    start,end=log(rms(bed[:4800])*gm),log(rms(bed[n-4800:n])*gm)
    assert start < -70 and end < -70
    assert max(abs(fx[i]-fx[i-2]) for i in range(2,n))<.03
    measured=loudness(path);assert measured['true_peak_dbtp'] < -1
    segments={}
    for name,t in [('beginning',0),('middle',seconds/2-.5),('ending',seconds-1)]:
        i=round(t*RATE)*2;segments[name]={'time':t,'mix_rms_dbfs':round(log(rms(mixed[i:i+RATE*2])),2)}
    return {'file':str(path.relative_to(ROOT)),'sha256':sha(path),'bytes':path.stat().st_size,'seconds':seconds,'frames':len(actual),'width':1920,'height':1080,'fps':30,'video_codec':'h264','pixel_format':'yuv420p','audio_codec':'aac/LC','channels':2,'sample_rate':RATE,'full_decode':'PASS','muxed_video_packets_and_decoded_frames':'IDENTICAL_TO_REVIEWED_VISUAL','aac_error_rms_dbfs':round(log(error),2),'sample_peak_dbfs':round(log(peak),2),'clipped_samples':clipped,'cues':cues,'music_continuity_min_half_second_dbfs':round(log(min(interior)),2),'fade_start_50ms_dbfs':round(start,2),'fade_end_50ms_dbfs':round(end,2),'segments':segments,**measured}


def main():
    results=[]
    print('Inspecting approved Video1, without rendering or modification',flush=True)
    results.append(validate('m5-l13-v1-source-organization-quality-v2',46,OUT/'video-1-visual-1080p.mp4',OUT/'m5-l13-v1-quality-v2-audio.wav',OUT/'music-clean-ducked.wav',OUT/'sfx-clean.wav',EVENTS))
    for video in DATA:
        print('Validating new',video['id'],flush=True)
        base=video['filename']
        manifest=json.loads((OUT/(base+'-mix.json')).read_text())
        for record in manifest['outputs']:assert sha(ROOT/record['path'])==record['sha256']
        results.append(validate(base,video['seconds'],OUT/(base+'-visual.mp4'),OUT/(base+'-audio.wav'),OUT/(base+'-music.wav'),OUT/(base+'-sfx.wav'),events_for(video)))
        scenes=video['scenes'];assert sum(s['seconds'] for s in scenes)==video['seconds']
        assert max(len((s['title']+' '+s['instruction']+' '+s['note']).split())/(s['seconds']-.2) for s in scenes)<3.5
        # Same approved filtered score up to the approved first video's outro.
        raw=decode(OUT/(base+'-music-filtered.wav'));approved=decode(OUT/'music-clean.wav')
        assert raw[:round(44.2*RATE)*2]==approved[:round(44.2*RATE)*2]
    baseline=json.loads((OUT/'phase5h-preservation.json').read_text())['hashes']
    changed=[p for p,h in baseline.items() if not Path(p).is_file() or sha(Path(p))!=h]
    assert not changed,changed
    report={'status':'PASS','videos':results,'preserved_existing_files':len(baseline),'approved_video1_unchanged':True,'video1_rendered':False,'music_and_sfx':'approved QualityV2 sources reused; no narration or new synthesis','human_listening_of_new_full_videos':'not claimed; approved style reused','database_and_application':'unchanged'}
    (OUT/'phase5h-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
