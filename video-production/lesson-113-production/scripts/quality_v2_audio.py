"""Inspect old sources; prepare clean versioned audio without altering any original."""
from array import array
import argparse
import json
import math
from pathlib import Path
import subprocess
import sys

from prepare_music_preview import ROOT, RATE, sha, read_stereo, write_wav, db

OUT = ROOT/'out/quality-v2'
DURATION=46
EVENTS=[{'frame':246,'sound':'select'}, {'frame':513,'sound':'place'},
        {'frame':993,'sound':'select'}, {'frame':1320,'sound':'finish'}]


def decode(path, filters=None):
    args=['ffmpeg','-v','error','-i',str(path),'-map','0:a:0']
    if filters:args+=['-af',filters]
    args+=['-ar',str(RATE),'-ac','2','-f','f32le','-']
    a=array('f');a.frombytes(subprocess.check_output(args))
    if sys.byteorder!='little':a.byteswap()
    return a


def rms(x):return math.sqrt(sum(v*v for v in x)/len(x))
def log(x):return 20*math.log10(max(x,1e-12))


def inspect(path):
    a=decode(path);hf=decode(path,'highpass=f=4000:p=2')
    return {'file':str(path.relative_to(ROOT)),'sha256':sha(path),
            'peak_dbfs':round(log(max(map(abs,a))),2),
            'rms_dbfs':round(log(rms(a)),2),
            'above_4khz_rms_relative_db':round(log(rms(hf)/rms(a)),2),
            'max_same_channel_sample_step':round(max(abs(a[i]-a[i-2]) for i in range(2,len(a))),6),
            'first_sample_absolute':max(abs(a[0]),abs(a[1])),
            'last_sample_absolute':max(abs(a[-1]),abs(a[-2]))}


def soft_sound(name):
    duration={'select':.16,'place':.26,'finish':.55}[name]
    out=array('f',[0])*round(duration*RATE)
    for i in range(len(out)):
        t=i/RATE
        if name=='select':notes=[(0,520,.012,.055,1)]
        elif name=='place':notes=[(0,260,.025,.095,1),(0,390,.025,.10,.25)]
        else:notes=[(0,390,.03,.17,.7),(.13,520,.035,.16,.55)]
        value=0
        for start,freq,attack,decay,gain in notes:
            u=t-start
            if u<0:continue
            envelope=math.sin(min(1,u/attack)*math.pi/2)**2 * math.exp(-u/decay)
            envelope*=math.sin(min(1,max(0,(duration-t)/.07))*math.pi/2)**2
            value+=gain*envelope*(math.sin(math.tau*freq*u)+.04*math.sin(math.tau*freq*2*u))
        out[i]=value
    # Comfortable fixed source peak; no broadband noise or swept pitch.
    peak=max(map(abs,out));target={'select':.095,'place':.115,'finish':.085}[name]
    return array('f',(x/peak*target for x in out))


def prepare():
    targets=[OUT/'music-clean.wav',OUT/'sfx-clean.wav',OUT/'audio-provenance.json']
    targets += [OUT/'sfx'/(name+'.wav') for name in ['select','place','finish']]
    for p in targets:
        if p.exists():raise SystemExit('Refusing overwrite: '+str(p))
    OUT.mkdir(parents=True,exist_ok=True);(OUT/'sfx').mkdir(exist_ok=True)
    master=ROOT/'out/audio-preview/minimal-tech-ambient-v1-theme-64s.wav'
    # Retain approved harmony/melody and tempo; gently remove spectral extremes.
    subprocess.run(['ffmpeg','-v','error','-n','-i',str(master),'-af',
                    'atrim=duration=46,highpass=f=70:p=2,lowpass=f=1800:p=2,afade=t=out:st=44.2:d=1.8:curve=hsin',
                    '-ar',str(RATE),'-ac','2','-c:a','pcm_s24le',str(OUT/'music-clean.wav')],check=True)
    stereo=array('f',[0])*(DURATION*RATE*2);sounds={}
    for name in ['select','place','finish']:
        sound=soft_sound(name);sounds[name]=sound
        write_wav(OUT/'sfx'/(name+'.wav'),sound,sound)
    for event in EVENTS:
        offset=round(event['frame']/30*RATE)*2
        for j,value in enumerate(sounds[event['sound']]):
            stereo[offset+2*j]+=value;stereo[offset+2*j+1]+=value
    write_wav(OUT/'sfx-clean.wav',stereo[::2],stereo[1::2])
    report={'duration_seconds':46,'sample_rate':RATE,'channels':2,
            'master_source':{'path':str(master.relative_to(ROOT)),'sha256':sha(master)},
            'music_processing':'Exact approved master; 70 Hz high-pass, 1800 Hz low-pass, 1.8s end fade. No regeneration, tempo change or stretching.',
            'sfx_processing':'New original sine/harmonic tones, raised-cosine attacks (12–35ms), 70ms releases; no noise, sweeps or abrupt note onsets.',
            'removed':'Five repeated scene whooshes, decorative first pop, click on noninteractive rights text; 11 old cues reduced to 4 purposeful cues.',
            'events':EVENTS,'mix':{'music_db':-9,'sfx_db':0,'music_duck_db':5,'duck_attack_ms':60,'duck_release_ms':220},
            'note':'SFX gain is independent; spectral/envelope and cue-count changes repair sources, rather than lowering the master to conceal artifacts.',
            'outputs':[{'path':str(p.relative_to(ROOT)),'sha256':sha(p)} for p in targets if p.suffix=='.wav']}
    (OUT/'audio-provenance.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Prepared clean music and four purpose-timed gentle effects')


def diagnose():
    OUT.mkdir(parents=True,exist_ok=True);reports=[]
    files=list((ROOT/'public/sfx').glob('*.wav'))
    files += [ROOT/'out/audio-preview/minimal-tech-ambient-v1-theme-64s.wav']
    files += sorted((ROOT/'out/final').glob('*.mp4'))+sorted((ROOT/'out/final-mixed').glob('*.mp4'))
    for p in files:
        print('Inspecting:',p.name,flush=True);reports.append(inspect(p))
    for label,source in [('original-sfx',ROOT/'out/final/m5-l13-v1-source-organization.mp4'),('original-music',ROOT/'out/audio-preview/minimal-tech-ambient-v1-theme-64s.wav'),('original-mix',ROOT/'out/final-mixed/m5-l13-v1-source-organization.mp4')]:
        destination=OUT/(label+'-listening-20s.wav')
        if not destination.exists():
            subprocess.run(['ffmpeg','-v','error','-n','-i',str(source),'-t','20','-map','0:a:0','-ar',str(RATE),'-ac','2','-c:a','pcm_s24le',str(destination)],check=True)
    report={'measurements':reports,
            'confirmed_source_findings':['Original click mixes unfiltered white noise with a 1400Hz sinusoid and 3ms attack.','Original drop and whoosh deliberately contain random noise; they are not silent decoding errors.','Original completion adds an 880Hz note without its own gradual attack.','All examined streams are native 48kHz; no sample-rate conversion is required by the mixing pipeline.'],
            'uncertainty':'Intentional broadband transients/noisy whooshes are plausible contributors to reported harshness. Measurements alone do not identify the exact subjective glitch or prove listening comfort. Isolated original SFX/music/mix samples are supplied.',
            'not_confirmed':['Aliasing or corrupted decoding as the main cause','Clipping as the cause','Music itself as the principal artifact source'],
            'method':'Stereo waveform differences and 4kHz two-pole high-pass RMS comparison; no claims based only on peak/clipping.'}
    (OUT/'audio-diagnosis.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')


def mix(visual, music_db=-9, sfx_db=0):
    target=OUT/'m5-l13-v1-source-organization-quality-v2.mp4'
    wav=OUT/'m5-l13-v1-quality-v2-audio.wav'
    for p in [target,wav]:
        if p.exists():raise SystemExit('Refusing overwrite: '+str(p))
    # Deterministic short musical dips around the four actual visible actions.
    l,r=read_stereo(OUT/'music-clean.wav')
    for i in range(len(l)):
        t=i/RATE;attenuation=0.0
        for event in EVENTS:
            start=event['frame']/30;end=start+{'select':.16,'place':.26,'finish':.55}[event['sound']]
            if start-.06<=t<start:attenuation=max(attenuation,5*(t-start+.06)/.06)
            elif start<=t<=end+.03:attenuation=5
            elif end+.03<t<end+.25:attenuation=max(attenuation,5*(end+.25-t)/.22)
        gain=db(-attenuation);l[i]*=gain;r[i]*=gain
    stem=OUT/'music-clean-ducked.wav';write_wav(stem,l,r)
    filters=f'[0:a]volume={music_db}dB[m];[1:a]volume={sfx_db}dB[s];[m][s]amix=inputs=2:normalize=0:duration=shortest[a]'
    subprocess.run(['ffmpeg','-v','error','-n','-i',str(stem),'-i',str(OUT/'sfx-clean.wav'),'-filter_complex',filters,'-map','[a]','-c:a','pcm_s24le',str(wav)],check=True)
    subprocess.run(['ffmpeg','-v','error','-n','-i',str(visual),'-i',str(wav),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-ar',str(RATE),'-ac','2','-movflags','+faststart',str(target)],check=True)
    (OUT/'mix-settings.json').write_text(json.dumps({'music_db':music_db,'sfx_db':sfx_db,'events':EVENTS,'filter':filters,'video':'copied rendered quality-v2 visual stream; old videos unchanged'},indent=2)+'\n')
    print('Mixed:',target)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['diagnose','prepare','mix'])
    parser.add_argument('--visual',type=Path,default=OUT/'video-1-visual-1080p.mp4')
    parser.add_argument('--music-db',type=float,default=-9)
    parser.add_argument('--sfx-db',type=float,default=0)
    args=parser.parse_args()
    if not (-60<=args.music_db<=0 and -24<=args.sfx_db<=12):parser.error('Unsafe gain range')
    if args.action=='diagnose':diagnose()
    elif args.action=='prepare':prepare()
    else:mix(args.visual,args.music_db,args.sfx_db)
