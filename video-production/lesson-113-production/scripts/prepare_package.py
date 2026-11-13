"""Original procedural SFX, deterministic cue sheets and reading transcripts.
No third-party samples, speech, model weights or database access.
"""
from pathlib import Path
from array import array
import hashlib,io,json,math,random,sys,wave

ROOT=Path(__file__).resolve().parents[1]
FPS=30
RATE=48000
DURATIONS={'click':.075,'whoosh':.42,'pop':.18,'drop':.14,'complete':.65}

def make_sound(name,duration):
    rng=random.Random('AI-Courses-113-'+name)
    count=round(duration*RATE);samples=[];low=0
    for i in range(count):
        t=i/RATE;u=i/(count-1);noise=rng.uniform(-1,1)
        low+=.13*(noise-low)
        envelope=math.sin(math.pi*u)**2
        if name=='click':value=(math.sin(2*math.pi*1400*t)*.55+noise*.25)*math.exp(-t*70)
        elif name=='whoosh':value=low*math.sin(math.pi*u)**2
        elif name=='pop':value=math.sin(2*math.pi*(520*t-450*t*t))*math.exp(-t*20)
        elif name=='drop':value=(low*.7+math.sin(2*math.pi*240*t)*.3)*math.exp(-t*24)
        else:
            value=math.sin(2*math.pi*660*t)*math.exp(-t*7)
            if t>.12:value+=.7*math.sin(2*math.pi*880*(t-.12))*math.exp(-(t-.12)*9)
        attack=min(1,t/.003)
        tail=min(1,(duration-t)/.025)
        samples.append(value*attack*tail*(envelope if name=='whoosh' else 1))
    peak=max(map(abs,samples));pcm=array('h',(round(v/peak*.46*32767) for v in samples))
    if sys.byteorder!='little':pcm.byteswap()
    output=io.BytesIO()
    with wave.open(output,'wb') as wav:
        wav.setparams((1,2,RATE,0,'NONE','not compressed'));wav.writeframes(pcm.tobytes())
    return output.getvalue(),dict(duration=duration,samples=count,peak=.46,
        rms=math.sqrt(sum(v*v for v in samples)/count)/peak*.46)

assets=ROOT/'public/sfx';assets.mkdir(exist_ok=True)
provenance=dict(origin='Original reproducible procedural synthesis; no external recordings or AI models.',
    method='Python stdlib; deterministic filtered noise, damped sinusoidal transients and two-note completion cue.',
    distribution='Original assets authored for AI Courses educational videos; no third-party sound sample licenses.',
    sample_rate=RATE,channels=1,format='WAV PCM16',generator='scripts/prepare_package.py',files={})
for name,duration in DURATIONS.items():
    raw,metadata=make_sound(name,duration);path=assets/(name+'.wav')
    if path.exists() and path.read_bytes()!=raw:raise SystemExit('Refusing to overwrite unexpected SFX: '+str(path))
    path.write_bytes(raw);metadata['sha256']=hashlib.sha256(raw).hexdigest();provenance['files'][path.name]=metadata
(ROOT/'content/sfx-provenance.json').write_text(json.dumps(provenance,indent=2)+'\n')
videos=json.loads((ROOT/'content/videos.json').read_text());cues={}
for v in videos:
    assert v['seconds']==sum(s['seconds'] for s in v['scenes'])
    start=0;events=[];text=f"# {v['title']}\n\nТекстовый эквивалент видео без диктора, не расшифровка речи и не субтитры.\n\nУрок 113. Ф1 — вымышленный учебный проект. Все интерфейсы — схемы, не запись CapCut. Звуковые сигналы не несут обязательной учебной информации.\n\n"
    for index,s in enumerate(v['scenes']):
        words=len((s['title']+' '+s['instruction']+' '+s['note']).split())
        # ~3 words/sec after the 0.9s entrance; generous pause/read time is deliberate.
        assert words/(s['seconds']-.9)<=3.5,(s['id'],'Too little reading time')
        if index:events.append(dict(frame=round((start+.12)*FPS),duration=math.ceil(DURATIONS['whoosh']*FPS),sound='whoosh',gain=.32,scene=s['id'],sync='Scene entrance'))
        events.append(dict(frame=round((start+s['actionAt'])*FPS),duration=math.ceil(DURATIONS[s['sfx']]*FPS),sound=s['sfx'],gain=.65,scene=s['id'],sync='Visual actionAt marker'))
        assert s['actionAt']+DURATIONS[s['sfx']]<s['seconds']
        def stamp(n):return f'{n//60:02d}:{n%60:02d}'
        text+=f"## {index+1}. {stamp(start)}–{stamp(start+s['seconds'])} — {s['title']}\n\n{s['instruction']}\n\n{s['note']}\n\n**Подробнее:** {s.get('detail','')}\n\n**На иллюстрации:** {s['alternative']}\n\n"
        start+=s['seconds']
    cues[v['id']]=events
    text+='Выполните проверку на своей версии редактора. Схема не подтверждает настоящее сохранение или импорт и не обещает облачное резервирование.\n'
    (ROOT/'transcripts'/f"{v['filename']}.ru.md").write_text(text)
(ROOT/'content/sfx-cues.json').write_text(json.dumps(cues,ensure_ascii=False,indent=2)+'\n')
print('Prepared 5 original SFX, frame-exact action/transition cues and 3 reading transcripts.')
