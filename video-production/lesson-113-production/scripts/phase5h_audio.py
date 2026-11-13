"""Reuse approved Quality V2 music/SFX for Videos 2 and 3 only; no source overwrite."""
from array import array
import argparse,json,subprocess
from prepare_music_preview import ROOT,RATE,read_stereo,write_wav,sha,db

OUT=ROOT/'out/quality-v2'
DATA=ROOT/'content/quality-v2/series.json'


def events_for(video):
    result=[];start=0
    for scene in video['scenes']:
        for event in scene['events']:
            result.append({'frame':round((start+event['at'])*30),'sound':event['sound'],'scene':scene['id']})
        start+=scene['seconds']
    assert start==video['seconds']
    return result


def prepare(video):
    assert video['id'] in ['project-import','timeline-reopen']
    base=video['filename'];seconds=video['seconds'];n=round(seconds*RATE)
    music=OUT/(base+'-music.wav');sfx=OUT/(base+'-sfx.wav')
    manifest=OUT/(base+'-audio.json')
    for p in [music,sfx,manifest]:
        if p.exists():raise SystemExit('Refusing overwrite: '+str(p))
    master=ROOT/'out/audio-preview/minimal-tech-ambient-v1-theme-64s.wav'
    original_provenance=json.loads((ROOT/'out/audio-preview/minimal-tech-ambient-v1-provenance.json').read_text())
    expected=next(x['sha256'] for x in original_provenance['outputs'] if x['path'].endswith('theme-64s.wav'))
    assert sha(master)==expected
    assert seconds<=62, 'Approved master too short before its original fade'
    raw=OUT/(base+'-music-filtered.wav')
    if raw.exists():raise SystemExit('Refusing overwrite: '+str(raw))
    command=['ffmpeg','-v','error','-n','-i',str(master),'-af',f'atrim=duration={seconds},highpass=f=70:p=2,lowpass=f=1800:p=2,afade=t=out:st={seconds-1.8}:d=1.8:curve=hsin','-ar',str(RATE),'-ac','2','-c:a','pcm_s24le',str(raw)]
    subprocess.run(command,check=True)
    l,r=read_stereo(raw);assert len(l)==len(r)==n
    events=events_for(video);left=array('f',[0])*n;right=array('f',[0])*n;sounds={};references=[]
    approved_audio=json.loads((OUT/'audio-provenance.json').read_text())
    for name in {e['sound'] for e in events}:
        path=OUT/'sfx'/(name+'.wav')
        expected=next(x['sha256'] for x in approved_audio['outputs'] if x['path']==str(path.relative_to(ROOT)))
        assert sha(path)==expected
        sounds[name]=read_stereo(path)
        references.append({'path':str(path.relative_to(ROOT)),'sha256':sha(path)})
    for event in events:
        offset=round(event['frame']/30*RATE);a,b=sounds[event['sound']]
        assert offset+len(a)<=n
        for j in range(len(a)):
            left[offset+j]+=a[j];right[offset+j]+=b[j]
    write_wav(sfx,left,right)
    for i in range(n):
        t=i/RATE;attenuation=0.
        for event in events:
            start=event['frame']/30;end=start+len(sounds[event['sound']][0])/RATE
            if start-.06<=t<start:attenuation=max(attenuation,5*(t-start+.06)/.06)
            elif start<=t<=end+.03:attenuation=5
            elif end+.03<t<end+.25:attenuation=max(attenuation,5*(end+.25-t)/.22)
        gain=db(-attenuation);l[i]*=gain;r[i]*=gain
    write_wav(music,l,r)
    report={'video':video['id'],'seconds':seconds,'events':events,'master':{'path':str(master.relative_to(ROOT)),'sha256':sha(master)},'approved_sfx':references,'method':'Exact QualityV2 filter/fade chain and saved tonal effects; no synthesis or altered musical theme','music_db':-9,'sfx_db':0,'duck_db':5,'attack_ms':60,'hold_ms':30,'release_ms':220,'music_fade_out_seconds':1.8,'filter_command':command,'outputs':[{'path':str(p.relative_to(ROOT)),'sha256':sha(p)} for p in [raw,music,sfx]]}
    manifest.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print('Prepared approved audio:',video['id'],flush=True)


def mix(video):
    base=video['filename'];visual=OUT/(base+'-visual.mp4');target=OUT/(base+'.mp4');audio=OUT/(base+'-audio.wav')
    if not visual.exists():raise SystemExit('Render reviewed visual first: '+str(visual))
    for p in [target,audio]:
        if p.exists():raise SystemExit('Refusing overwrite: '+str(p))
    music=OUT/(base+'-music.wav');sfx=OUT/(base+'-sfx.wav')
    filt='[0:a]volume=-9dB[m];[1:a]volume=0dB[s];[m][s]amix=inputs=2:normalize=0:duration=shortest[a]'
    command=['ffmpeg','-v','error','-n','-i',str(music),'-i',str(sfx),'-filter_complex',filt,'-map','[a]','-c:a','pcm_s24le',str(audio)]
    subprocess.run(command,check=True)
    mux=['ffmpeg','-v','error','-n','-i',str(visual),'-i',str(audio),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-ar',str(RATE),'-ac','2','-movflags','+faststart',str(target)]
    subprocess.run(mux,check=True)
    (OUT/(base+'-mix.json')).write_text(json.dumps({'video':video['id'],'commands':[command,mux],'source_visual_sha256':sha(visual),'outputs':[{'path':str(p.relative_to(ROOT)),'sha256':sha(p)} for p in [audio,target]],'approved_video1':'unchanged'},indent=2)+'\n')
    print('Mixed:',target,flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=['prepare','mix']);p.add_argument('--video',default='all',choices=['all','project-import','timeline-reopen']);args=p.parse_args()
    videos=json.loads(DATA.read_text())
    for video in videos:
        if args.video=='all' or args.video==video['id']:
            (prepare if args.action=='prepare' else mix)(video)
