"""Offline, create-only draft synthesis; run with .local-silero-eval/venv/bin/python."""
import argparse
from pathlib import Path
import hashlib
import importlib.util
import json
import wave
import math

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
CHECKPOINT = ROOT / '.local-silero-eval/v5_cis_base_nostress.pt'
EXPECTED = '0405777e332906f0644e08a680f7cfdc2137ea864090079c1fdd30a43c1b8761'
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output-dir', type=Path, required=True,
                    help='Fresh local-only output directory; source files are never overwritten.')
args = parser.parse_args()
OUTPUT = args.output_dir.resolve()
if (OUTPUT/'narration-preview.wav').exists() or (OUTPUT/'narration-provenance.json').exists():
    raise SystemExit('Refusing to overwrite draft audio or provenance.')
assert hashlib.sha256(CHECKPOINT.read_bytes()).hexdigest() == EXPECTED
source = ROOT/'course_assets/module_4/voice_candidates/prepare_roman_module4.py'
spec=importlib.util.spec_from_file_location('existing_silero_pipeline',source)
pipeline=importlib.util.module_from_spec(spec);spec.loader.exec_module(pipeline)
text=(HERE/'narration-script-ru.txt').read_text().strip()
shots=json.loads((HERE/'storyboard-source.json').read_text())['storyboard']
assert text == '\n\n'.join(s['narration_ru'] for s in shots)
# Existing nostress pipeline uses explicit + vowel stress. Unmarked words remain
# model-pronounced; the preview must be listened to before author approval.
marks={'Готовим':'Гот+овим','вымышленный':'в+ымышленный','пример':'прим+ер','Вторая':'Втор+ая','сторона':'сторон+а','листа':'лист+а','материалы':'матери+алы','исходники':'исх+одники','изображения':'изображ+ения','Оригиналы':'Оригин+алы','сохраняем':'сохран+яем','проверяем':'провер+яем','Проверяем':'Провер+яем','CapCut':'CapCut','Разделим':'Разд+елим','Копируем':'Коп+ируем','условия':'усл+овия','использования':'исп+ользования','экономии':'экон+омии','озвучку':'озв+учку','подписи':'п+одписи','папок':'п+апок','распространение':'распростран+ение'}
import re
plain=text.split('\n\n')
marked=[re.sub(r'[A-Za-zА-Яа-яЁё]+',lambda m: marks.get(m.group(),m.group()),s) for s in plain]
assert [s.replace('+','') for s in marked]==plain
import torch
torch.set_num_threads(2);torch.set_num_interop_threads(1);torch.manual_seed(0)
model=torch.package.PackageImporter(str(CHECKPOINT)).load_pickle('tts_models','model')
model.to(torch.device('cpu'));assert 'ru_roman' in model.speakers
pcm,cues=pipeline.assemble(model,torch,plain,marked,94,650)
raw=pipeline.pcm_bytes(pcm)
OUTPUT.mkdir(parents=True, exist_ok=True)
with (OUTPUT/'narration-preview.wav').open('xb') as f:f.write(raw)
peak=max(abs(x) for x in pcm);rms=math.sqrt(sum(x*x for x in pcm)/len(pcm))
assert 0<peak<32767 and rms>50
report=dict(status='draft_pending_human_listening_and_pronunciation_review',model_id='v5_cis_base_nostress',speaker='ru_roman',checkpoint_source=pipeline.SOURCE,checkpoint_sha256=EXPECTED,license='MIT LICENSE_CIS',license_source='https://github.com/snakers4/silero-models/blob/master/LICENSE_CIS',license_notice='LICENSE_CIS',torch_version=torch.__version__,sample_rate=24000,channels=1,format='WAV PCM16',duration_seconds=len(pcm)/24000,planned_storyboard_seconds=110,delta_to_plan_seconds=len(pcm)/24000-110,sha256=hashlib.sha256(raw).hexdigest(),peak_pcm=peak,rms_pcm=rms,rate_percent=94,paragraph_gap_ms=650,postprocessing='none; no artificial timing, pitch shift or time stretch',transcript=text,cues=cues,stress_policy='Selected manual stress hints; unchanged words; remaining pronunciation requires author review.',pipeline_sha256=hashlib.sha256(source.read_bytes()).hexdigest())
with (OUTPUT/'narration-provenance.json').open('x') as f:json.dump(report,f,ensure_ascii=False,indent=2)
print(json.dumps({k:report[k] for k in ['duration_seconds','delta_to_plan_seconds','sha256','peak_pcm','rms_pcm']},indent=2))
