"""Validate approved Module 4 assets; optional exact reproduction in a fresh directory.

Default is inspection only. No Django, DB, imports, downloads or model execution.
--reproduce uses an externally provisioned isolated CPU PyTorch environment and
an explicitly supplied, SHA-pinned MIT Silero checkpoint. Never overwrite assets.
"""
import argparse
from array import array
import hashlib
import io
import json
import math
from pathlib import Path
import random
import sys
from xml.sax.saxutils import escape

ROOT=Path(__file__).resolve().parents[1]
ASSETS=ROOT/'course_assets/module_4'
RATE=24000
SPEAKER='ru_roman'
SEED=20261029
NFFT=1024
HOP=192
CHECKSUM='0405777e332906f0644e08a680f7cfdc2137ea864090079c1fdd30a43c1b8761'
import wave
NARRATION = [
    'Представьте, что вы готовите короткий видеоролик для университетского медиапроекта.',
    'С помощью искусственного интеллекта можно создать сценарий, подготовить иллюстрации и озвучить текст.',
    'Однако перед публикацией необходимо проверить факты, качество материалов и естественность звучания.',
]

STRESSED_NARRATION = [
    'Предст+авьте, что вы гот+овите кор+откий видеор+олик для университ+етского медиапро+екта.',
    'С п+омощью иск+усственного интелл+екта м+ожно созд+ать сцен+арий, подгот+овить иллюстр+ации и озв+учить текст.',
    'Одн+ако п+еред публик+ацией необход+имо пров+ерить ф+акты, к+ачество матери+алов и ест+ественность звуч+ания.',
]

F1_CUES = [
    'Команда использует чистую сторону листа.',
    'Это пример повторного использования бумаги,',
    'а не измерение экономии.',
]

STRESSED_F1 = [
    'Ком+анда исп+ользует ч+истую ст+орону лист+а.',
    '+Это прим+ер повт+орного исп+ользования бум+аги,',
    'а не измер+ение экон+омии.',
]

def timestamp(sample):
    millis = sample * 1000 // RATE
    seconds, ms = divmod(millis, 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f'{hours:02}:{minutes:02}:{seconds:02},{ms:03}'

def pcm_bytes(values):
    pcm = array('h', values)
    if sys.byteorder != 'little':
        pcm.byteswap()
    output = io.BytesIO()
    with wave.open(output, 'wb') as wav:
        wav.setnchannels(1); wav.setsampwidth(2); wav.setframerate(RATE)
        wav.writeframes(pcm.tobytes())
    return output.getvalue()

def assemble(model, torch, texts, marked, speed_percent, gap_ms):
    if [t.replace('+', '') for t in marked] != texts:
        raise RuntimeError('Stress annotations changed the approved words.')
    output = array('h', [0]) * (RATE // 5)
    cues = []
    for index, (plain, stressed) in enumerate(zip(texts, marked)):
        ssml = f'<speak><prosody rate="{speed_percent}%">{escape(stressed)}</prosody></speak>'
        with torch.inference_mode():
            audio = model.apply_tts(ssml_text=ssml, speaker=SPEAKER, sample_rate=RATE).detach().cpu().flatten()
        if not bool(torch.isfinite(audio).all()) or audio.numel() < RATE//5:
            raise RuntimeError('Invalid synthesis output.')
        if not 0 < float(audio.abs().max()) < 1:
            raise RuntimeError('Silent/clipped synthesis output.')
        values = array('h', (round(float(x)*32767) for x in audio.tolist()))
        start = len(output)
        output.extend(values)
        cues.append(dict(text=plain, synthesis_input=stressed, ssml=ssml,
                         start_sample=start, end_sample=len(output),
                         segment_pcm_sha256=fingerprint(array_to_le(values))))
        silence_ms = gap_ms if index < len(texts)-1 else 250
        output.extend(array('h', [0]) * (RATE*silence_ms//1000))
    return output, cues

def array_to_le(values):
    result = array('h', values)
    if sys.byteorder != 'little':
        result.byteswap()
    return result.tobytes()

def rms(values):
    return math.sqrt(sum(x*x for x in values)/len(values))

def room_noise(count):
    """Seeded multi-band stochastic ventilation texture; no tones or recordings."""
    rng=random.Random(SEED)
    low=mid=drift=dc=0.0
    values=[]
    for _ in range(count):
        white=rng.gauss(0,1)
        low=0.98*low+0.02*white
        mid=0.70*mid+0.30*white
        drift=0.999*drift+0.001*rng.gauss(0,1)
        # Gentle low-mid body plus broad airflow; stochastic slow modulation.
        raw=(2.5*low+0.65*mid+0.12*white)*(1+0.15*math.tanh(10*drift))
        dc=0.99*dc+0.01*raw
        values.append(raw-dc)  # suppress subsonic rumble, no sinusoidal components
    return values

def add_noise(clean, snr_db=14):
    noise=room_noise(len(clean))
    scale=rms(clean)/(10**(snr_db/20)*rms(noise))
    return array('h',(round(x+n*scale) for x,n in zip(clean,noise))),scale

def denoise(noisy,settings):
 import torch
 import torch.nn.functional as F
 torch.set_num_threads(2)
 signal=torch.tensor(list(noisy),dtype=torch.float64)
 window=torch.hann_window(NFFT,dtype=torch.float64)
 spectrum=torch.stft(signal,n_fft=NFFT,hop_length=HOP,window=window,return_complex=True)
 power=spectrum.abs().square()
 centers=torch.arange(power.shape[1])*HOP
 # Documented preparation has 200 ms leading and 250 ms trailing silence.
 # Include only windows entirely within these intervals; no clean input needed.
 profile_frames=((centers>=NFFT//2)&(centers<=4800-NFFT//2)) | ((centers>=len(noisy)-6000+NFFT//2)&(centers<=len(noisy)-NFFT//2))
 noise=power[:,profile_frames].mean(dim=1,keepdim=True)
 # Short-time averaging stabilizes the estimate without a hard binary gate.
 smooth_power=F.avg_pool1d(power.unsqueeze(0),3,stride=1,padding=1,count_include_pad=False).squeeze(0)
 snr=(smooth_power/settings['oversubtraction']-noise).clamp(min=0)/(noise+1e-12)
 gain=(snr/(1+snr)).pow(settings['exponent']).clamp(min=settings['min_gain'],max=1)
 gain=F.avg_pool1d(gain.T.unsqueeze(1),3,stride=1,padding=1,count_include_pad=False).squeeze(1).T
 gain=F.avg_pool1d(gain.unsqueeze(0),3,stride=1,padding=1,count_include_pad=False).squeeze(0)
 # Open promptly for syllables; release suppression slowly enough to avoid chatter.
 previous=gain[:,0].clone()
 smoothed=[previous]
 for index in range(1,gain.shape[1]):
  target=gain[:,index]
  coefficient=torch.where(target>previous,0.7,0.22)
  previous=coefficient*target+(1-coefficient)*previous
  smoothed.append(previous)
 gain=torch.stack(smoothed,dim=1)
 output=torch.istft(spectrum*gain,n_fft=NFFT,hop_length=HOP,window=window,length=len(noisy))
 if not bool(torch.isfinite(output).all()) or float(output.abs().max())>=32767:raise ValueError('Invalid/clipped output.')
 return array('h',(round(x) for x in output.tolist())),dict(
  min_spectral_gain=float(gain.min()),max_spectral_gain=float(gain.max()),
  max_frame_gain_change=float((gain[:,1:]-gain[:,:-1]).abs().max()),noise_profile_frames=int(profile_frames.sum()))

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reproduce',action='store_true')
    parser.add_argument('--checkpoint',type=Path)
    parser.add_argument('--output-dir',type=Path)
    args=parser.parse_args()
    manifest=json.loads((ROOT/'docs/courses/media-module-4-assets.json').read_text())
    for entry in manifest['assets']:
        raw=(ASSETS/entry['filename']).read_bytes()
        if entry.get('sha256') and hashlib.sha256(raw).hexdigest()!=entry['sha256']:
            raise SystemExit('Canonical asset checksum conflict: '+entry['filename'])
    if not args.reproduce:
        print('Seven approved assets present; recorded checksums verified. No audio generated.')
        return
    if not args.checkpoint or not args.output_dir:
        raise SystemExit('--reproduce requires --checkpoint and a fresh --output-dir.')
    if hashlib.sha256(args.checkpoint.read_bytes()).hexdigest()!=CHECKSUM:
        raise SystemExit('MIT checkpoint checksum conflict.')
    if args.output_dir.exists():
        raise SystemExit('Choose a new output directory; existing files are never overwritten.')
    import torch
    torch.set_num_threads(2);torch.set_num_interop_threads(1);torch.manual_seed(0)
    model=torch.package.PackageImporter(str(args.checkpoint)).load_pickle('tts_models','model')
    model.to(torch.device('cpu'))
    # Preserve the approved synthesis sequence/RNG state; A is never written.
    assemble(model,torch,NARRATION,STRESSED_NARRATION,100,350)
    narration,_=assemble(model,torch,NARRATION,STRESSED_NARRATION,94,650)
    speech,cues=assemble(model,torch,F1_CUES,STRESSED_F1,100,300)
    clean=array('h',(round(x*(12000/max(map(abs,speech)))) for x in speech))
    noisy,_=add_noise(clean,14)
    filtered,_=denoise(noisy,{'oversubtraction':2.3,'exponent':1.0,'min_gain':0.04})
    files={
        'm4-l10-silero-ru-roman-approved.wav':pcm_bytes(narration),
        'm4-l11-silero-ru-roman-approved.wav':pcm_bytes(speech),
        'm4-l12-silero-ru-roman-before.wav':pcm_bytes(noisy),
        'm4-l12-silero-ru-roman-after-dsp.wav':pcm_bytes(filtered),
        'm4-l11-silero-ru-roman-synchronized.srt':('\n\n'.join(f"{i}\n{timestamp(c['start_sample'])} --> {timestamp(c['end_sample'])}\n{c['text']}" for i,c in enumerate(cues,1))+'\n').encode(),
    }
    for entry in manifest['assets']:
        raw=files.get(entry['filename'],(ASSETS/entry['filename']).read_bytes())
        if entry.get('sha256') and hashlib.sha256(raw).hexdigest()!=entry['sha256']:
            raise SystemExit('Runtime did not reproduce approved bytes; no files written. Keep committed approved assets.')
        files[entry['filename']]=raw
    args.output_dir.mkdir(parents=True)
    for name,raw in files.items():
        with (args.output_dir/name).open('xb') as output:output.write(raw)
    print('Reproduced approved bytes in fresh directory; no database or manifest changes.')


if __name__=='__main__':
    main()
