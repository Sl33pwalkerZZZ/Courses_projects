"""Create-only Silero ru_roman candidates. No Django, DB, manifest writes or imports."""
import argparse
from array import array
import hashlib
import importlib.util
import io
import json
import math
from pathlib import Path
import resource
import sys
import time
import wave
from xml.sax.saxutils import escape

HERE = Path(__file__).resolve().parent
MODEL_ID = 'v5_cis_base_nostress'
CHECKSUM = '0405777e332906f0644e08a680f7cfdc2137ea864090079c1fdd30a43c1b8761'
SOURCE = 'https://models.silero.ai/models/tts/ru/v5_cis_base_nostress.pt'
RATE = 24000
SPEAKER = 'ru_roman'
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
NAMES = [
    'ru-roman-variant-a-neutral.wav', 'ru-roman-variant-b-clear-pauses.wav',
    'm4-l10-ru-roman-tts-candidate.wav', 'm4-l11-ru-roman-speech-candidate.wav',
    'm4-l11-ru-roman-synchronized-candidate.srt', 'm4-l11-ru-roman-transcript.txt',
    'm4-l12-ru-roman-clean-candidate.wav', 'm4-l12-ru-roman-noisy-candidate.wav',
    'm4-l12-ru-roman-filtered-candidate.wav', 'production-candidates.json',
]


def fingerprint(raw):
    return hashlib.sha256(raw).hexdigest()


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


def notch(noisy, frequency=180, q=12):
    omega = 2 * math.pi * frequency / RATE
    alpha = math.sin(omega) / (2 * q)
    b0 = 1 / (1 + alpha)
    b1 = -2 * math.cos(omega) / (1 + alpha)
    b2 = b0
    a1, a2 = b1, (1 - alpha) / (1 + alpha)
    x1 = x2 = y1 = y2 = 0.0
    filtered = array('h')
    for x in noisy:
        y = b0*x + b1*x1 + b2*x2 - a1*y1 - a2*y2
        if abs(y) >= 32767:
            raise RuntimeError('Filter clipping; no files written.')
        filtered.append(round(y))
        x2, x1, y2, y1 = x1, x, y1, y
    return filtered, {'b': [b0, b1, b2], 'a': [1, a1, a2]}


def comparison(speech):
    gain = 12000 / max(map(abs, speech))
    clean = array('h', (round(x*gain) for x in speech))
    # Deliberately artificial, audible low-mid tone; no real field recording claim.
    noisy = array('h', (round(x + 4000*math.sin(2*math.pi*180*i/RATE)) for i, x in enumerate(clean)))
    filtered, coefficients = notch(noisy)
    def error_rms(values):
        return math.sqrt(sum((x-y)**2 for x, y in zip(values, clean))/len(clean))
    return clean, noisy, filtered, dict(
        method='conventional DSP biquad notch; not AI noise reduction',
        artificial_noise={'kind': 'deterministic sinusoid', 'frequency_hz': 180, 'peak_pcm': 4000},
        common_source_gain=gain, q=12, coefficients=coefficients,
        before_error_rms=error_rms(noisy), after_error_rms=error_rms(filtered),
        same_source=True, time_stretch=False, pitch_shift=False,
        note='Filtered noisy recording, not replacement with clean reference. Speech near 180 Hz may also be attenuated.',
    )


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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--checkpoint', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, default=HERE/'ru_roman_refined')
    args = parser.parse_args()
    if any((args.output_dir/name).exists() for name in NAMES):
        raise SystemExit('Refusing to overwrite existing candidate files. Use a fresh output directory.')
    if fingerprint(args.checkpoint.read_bytes()) != CHECKSUM:
        raise SystemExit('Checkpoint hash mismatch.')
    import torch
    torch.set_num_threads(2); torch.set_num_interop_threads(1); torch.manual_seed(0)
    model = torch.package.PackageImporter(str(args.checkpoint)).load_pickle('tts_models', 'model')
    model.to(torch.device('cpu'))
    if SPEAKER not in model.speakers:
        raise SystemExit('Selected Russian speaker unavailable.')
    started = time.monotonic()
    a, a_cues = assemble(model, torch, NARRATION, STRESSED_NARRATION, 100, 350)
    b, b_cues = assemble(model, torch, NARRATION, STRESSED_NARRATION, 94, 650)
    speech, speech_cues = assemble(model, torch, F1_CUES, STRESSED_F1, 100, 300)
    clean, noisy, filtered, processing = comparison(speech)
    arrays = {NAMES[0]: a, NAMES[1]: b, NAMES[2]: a, NAMES[3]: speech,
              NAMES[6]: clean, NAMES[7]: noisy, NAMES[8]: filtered}
    files = {name: pcm_bytes(values) for name, values in arrays.items()}
    files[NAMES[4]] = ('\n\n'.join(f"{i}\n{timestamp(c['start_sample'])} --> {timestamp(c['end_sample'])}\n{c['text']}" for i,c in enumerate(speech_cues, 1))+'\n').encode('utf-8')
    files[NAMES[5]] = (' '.join(F1_CUES)+'\n').encode('utf-8')
    # Common metadata describes this proposed candidate set only, not the live manifest.
    report = dict(model_id=MODEL_ID, checkpoint_source=SOURCE, checkpoint_sha256=CHECKSUM,
                  license='MIT', license_source='https://github.com/snakers4/silero-models/blob/master/LICENSE_CIS',
                  license_notice='Silero Team, Copyright (c) 2025-present; see ../LICENSE_CIS',
                  speaker=SPEAKER, sample_rate=RATE, torch_version=torch.__version__,
                  device='cpu', threads=2, seed=0, status='candidates_pending_author_listening_approval',
                  scripts={
                      'lesson10': dict(text='\n\n'.join(NARRATION), approval='Exact transcript previously confirmed by author; new performance awaits listening approval.', source='Author-confirmed narration, identical to voice evaluation text.'),
                      'lesson11': dict(text=' '.join(F1_CUES), approval='Existing educational source text retained exactly; new performance awaits listening approval.', source='Real saved Module 4 lesson order 2, section 3 and existing illustrative SRT.'),
                      'lesson12': dict(text=' '.join(F1_CUES), approval='Existing educational source text retained exactly; new performance awaits listening approval.', source='Real saved Module 4 lesson order 3, workflow step 1.'),
                  },
                  variants={'A': dict(rate_percent=100, gap_ms=350, cues=a_cues),
                            'B': dict(rate_percent=94, gap_ms=650, cues=b_cues)},
                  lesson10_candidate_variant='A provisional, not final author selection',
                  lesson11_cues=speech_cues,
                  subtitle_method='Exact separately synthesized PCM segment boundaries, including internal model pauses; 300 ms inter-cue gaps. Not reused eSpeak timings; not phoneme-level alignment.',
                  processing=processing,
                  production_plan={'lesson10': NAMES[2], 'lesson11': [NAMES[3], NAMES[4]],
                                   'lesson12': [NAMES[7], NAMES[8]], 'reference_only': [NAMES[6]],
                                   'legacy_audio_selected': False,
                                   'note': 'Proposal only. No live media manifest or attachments were changed. ElevenLabs and eSpeak are excluded from this proposed set.'},
                  files={name: dict(sha256=fingerprint(raw), size_bytes=len(raw),
                                   **(dict(samples=len(arrays[name]), duration_seconds=len(arrays[name])/RATE,
                                           format='WAV PCM mono signed 16-bit', peak_pcm=max(map(abs, arrays[name]))) if name in arrays else {})) for name,raw in files.items()},
                  generation_seconds=time.monotonic()-started,
                  peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                  review_required=['Listen to all words, especially negation and stress.', 'Check joins and last syllables.', 'Choose A or B before final lesson10 replacement.', 'Judge audible noise and filtering artifacts; signal checks do not establish perceptual quality.'])
    if len(b) <= len(a):
        raise RuntimeError('Slower variant is unexpectedly shorter.')
    if len({len(clean),len(noisy),len(filtered),len(speech)}) != 1:
        raise RuntimeError('Comparison lengths differ.')
    for name, values in arrays.items():
        if not 0 < max(map(abs, values)) < 32767:
            raise RuntimeError(f'Invalid PCM: {name}')
    files[NAMES[9]] = (json.dumps(report, ensure_ascii=False, indent=2)+'\n').encode('utf-8')
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for name, raw in files.items():
        with (args.output_dir/name).open('xb') as target:
            target.write(raw)
    print(json.dumps(report['files'],ensure_ascii=False,indent=2))


if __name__ == '__main__':
    main()
