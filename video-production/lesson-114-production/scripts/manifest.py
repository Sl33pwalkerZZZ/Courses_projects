"""Review manifest for real exports; never uploads or updates course content."""
from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
report=json.loads((ROOT/'out/qa/validation.json').read_text());assert report['status']=='PASS'
proposal=json.loads((ROOT/'content/lesson114-sync-proposal.json').read_text());speech=json.loads((ROOT/'content/speech.json').read_text());videos=json.loads((ROOT/'content/series.json').read_text());assets=[]
for i,(v,r) in enumerate(zip(videos,report['videos'])):
 file=ROOT/r['file'];assert sha(file)==r['sha256'];preview=ROOT/'out/previews'/(v['filename']+'.mp4');equivalent=ROOT/'content'/(v['filename']+'.equivalent.ru.txt');vtt=ROOT/'content'/(v['filename']+'.vtt')
 provenance='Original AI Courses schematic diagrams/music; approved QualityV2 tokens/theme/tonal effects reused. No real CapCut recording. '
 if i:provenance+='Existing approved Module4 speech reused unchanged; no ASR execution.\n\n'+speech['provenance']
 meta={'label':['Ф1: черновой монтаж','Ф1: озвучка и баланс','Ф1: проверка субтитров'][i],'caption':'Учебная схема, не запись CapCut Desktop. Ф1 — вымышленный пример. '+('Без диктора; инструкции на экране.' if i==0 else 'Короткая учебная речь Silero CIS Base ru_roman, MIT; инструкции на экране. '+('Ошибка распознавания специально смоделирована, ASR не запускалась.' if i==2 else 'Одинаковый голос; в сравнении изменён только уровень фона.')),'transcript':equivalent.read_text(),'provenance':provenance,'after_section':proposal['placements'][i]['after_section']}
 for key,limit in [('label',255),('caption',2000),('transcript',20000),('provenance',4000),('after_section',255)]:assert 0<len(meta[key])<=limit
 assets.append({'kind':'video','mime_type':'video/mp4','file':r['file'],'sha256':r['sha256'],'seconds':r['seconds'],'metadata':meta,'preview':{'file':str(preview.relative_to(ROOT)),'sha256':sha(preview),'width':960,'height':540},'optional_vtt':{'file':str(vtt.relative_to(ROOT)),'sha256':sha(vtt),'kind':'vtt','after_section':meta['after_section']} if vtt.exists() else None})
(ROOT/'content/final-assets.json').write_text(json.dumps({'status':'READY_FOR_AUTHOR_REVIEW_NOT_UPLOADED','course_id':10,'module_id':39,'lesson_id':114,'batch_importer_compatible':False,'assets':assets},ensure_ascii=False,indent=2)+'\n');print('Review-only final assets manifest prepared.')
