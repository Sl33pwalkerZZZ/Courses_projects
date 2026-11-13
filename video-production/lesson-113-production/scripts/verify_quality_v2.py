"""Technical and preservation checks for the single quality-v2 approval export."""
from array import array
import hashlib,json,math,subprocess
from pathlib import Path
from quality_v2_audio import ROOT,OUT,RATE,EVENTS,inspect,decode,rms,log


def probe(path):
    return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(path)]))


def packet_hashes(path):
    return json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_packets','-show_data_hash','sha256','-show_entries','packet=pts_time,dts_time,data_hash','-of','json',str(path)]))['packets']


def loudness(path):
    p=subprocess.run(['ffmpeg','-hide_banner','-nostdin','-i',str(path),'-af','loudnorm=I=-23:TP=-1.5:LRA=11:print_format=json','-f','null','-'],check=True,capture_output=True,text=True)
    s=p.stderr;r=json.loads(s[s.rfind('{'):s.rfind('}')+1])
    return {'integrated_lufs':float(r['input_i']),'true_peak_dbtp':float(r['input_tp']),'lra_lu':float(r['input_lra'])}


def main():
    video=OUT/'m5-l13-v1-source-organization-quality-v2.mp4';visual=OUT/'video-1-visual-1080p.mp4'
    audio=OUT/'m5-l13-v1-quality-v2-audio.wav';music=OUT/'music-clean-ducked.wav';sfx=OUT/'sfx-clean.wav'
    settings=json.loads((OUT/'mix-settings.json').read_text())
    m=probe(video);v=next(x for x in m['streams'] if x['codec_type']=='video');a=next(x for x in m['streams'] if x['codec_type']=='audio')
    assert (v['codec_name'],v['width'],v['height'],v['r_frame_rate'],v['pix_fmt'],int(v['nb_frames']))==('h264',1920,1080,'30/1','yuv420p',1380)
    assert a['codec_name']=='aac' and a['channels']==2 and int(a['sample_rate'])==RATE
    assert float(v['duration'])==float(a['duration'])==46
    assert float(v['start_time'])==float(a['start_time'])==0
    for p in [video,audio,music,sfx]:
        subprocess.run(['ffmpeg','-v','error','-xerror','-nostdin','-i',str(p),'-f','null','-'],check=True,capture_output=True)
    assert packet_hashes(video)==packet_hashes(visual)
    x=decode(video);reference=decode(audio);music_pcm=decode(music);effects=decode(sfx)
    n=46*RATE*2
    assert len(x)>=n and len(reference)==len(music_pcm)==len(effects)==n
    peak=max(map(abs,x));assert peak<.95
    error=math.sqrt(sum((x[i]-reference[i])**2 for i in range(n))/n);assert error<.001
    gm=10**(settings['music_db']/20);gs=10**(settings['sfx_db']/20)
    durations={'select':.16,'place':.26,'finish':.55};cues=[]
    for e in EVENTS:
        start=round(e['frame']/30*RATE)*2;end=start+round(durations[e['sound']]*RATE)*2
        source=effects[start:end];residual=[x[i]-music_pcm[i]*gm for i in range(start,end)]
        corr=sum(i*j for i,j in zip(source,residual))/math.sqrt(sum(i*i for i in source)*sum(j*j for j in residual))
        assert corr>.95,(e,corr)
        cues.append({**e,'residual_correlation':round(corr,5)})
    edges={}
    for label,p in [('music',music_pcm),('sfx',effects),('mix',x)]:
        edges[label]={'max_same_channel_step':max(abs(p[i]-p[i-2]) for i in range(2,len(p))),
                      'start_50ms_rms_dbfs':round(log(rms(p[:4800])),2),
                      'end_50ms_rms_dbfs':round(log(rms(p[n-4800:n])),2)}
    windows=[rms(music_pcm[i:i+RATE])*gm for i in range(RATE,n-RATE,RATE)]
    assert min(windows)>1e-5,'Unexpected music silence'
    assert edges['music']['end_50ms_rms_dbfs'] < -70
    assert edges['sfx']['max_same_channel_step'] < .03
    assert sum(abs(t)>=1 for t in x)==0
    measured=loudness(video);assert measured['true_peak_dbtp'] < -1
    scenes=json.loads((ROOT/'content/quality-v2/video-1.json').read_text())
    assert len(scenes)==6 and sum(s['seconds'] for s in scenes)==46
    pacing={s['id']:round(len((s['title']+' '+s['instruction']+' '+s['note']).split())/(s['seconds']-.2),2) for s in scenes}
    assert max(pacing.values())<3
    repaired=[inspect(OUT/'sfx'/(name+'.wav')) for name in ['select','place','finish']]
    baseline=json.loads((OUT/'preservation-checkpoint.json').read_text())['hashes']
    altered=[p for p,h in baseline.items() if not Path(p).is_file() or hashlib.sha256(Path(p).read_bytes()).hexdigest()!=h]
    assert not altered,altered
    report={'status':'PASS','video':str(video.relative_to(ROOT)),'sha256':hashlib.sha256(video.read_bytes()).hexdigest(),
            'specification':{'width':1920,'height':1080,'fps':30,'frames':1380,'seconds':46,'video':'h264/yuv420p','audio':'AAC stereo/48000Hz'},
            'full_decode':'PASS','copied_new_visual_packet_hashes':'IDENTICAL','audio_continuity':edges,
            'aac_error_rms_dbfs':round(log(error),2),'peak_dbfs':round(log(peak),2),'clipped_samples':0,
            'music_interior_minimum_500ms_rms_dbfs':round(log(min(windows)),2),'cue_alignment':cues,
            'source_repair_metrics':repaired,'reading_words_per_second':pacing,
            'unchanged_baseline_files':len(baseline),'videos_2_3_rendered':False,
            'human_listening_approval':'PENDING','subjective_artifact_root_cause':'not conclusively identified; likely noisy/abrupt original procedural effects; isolated comparisons provided',**measured}
    (OUT/'validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
