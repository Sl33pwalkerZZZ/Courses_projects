"""Build a review-only upload manifest from validated real exports. No DB/API calls."""
import json,hashlib,subprocess
from pathlib import Path
from prepare_music_preview import ROOT
out=ROOT/'out/quality-v2'
series=json.loads((ROOT/'content/quality-v2/series.json').read_text())
items=[{'filename':'m5-l13-v1-source-organization-quality-v2','title':'Ф1: организация исходников','section':3,'seconds':46},
       {'filename':series[0]['filename'],'title':'Ф1: проект и импорт материалов','section':5,'seconds':47},
       {'filename':series[1]['filename'],'title':'Ф1: таймлайн и повторное открытие','section':7,'seconds':54}]
proposal=json.loads((ROOT/'content/quality-v2/lesson-113-sync-proposal.json').read_text())
records=[]
for n,item in enumerate(items,1):
    path=out/(item['filename']+'.mp4');raw=path.read_bytes()
    info=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(path)]))
    transcript=(ROOT/'content/quality-v2'/(item['filename']+'.equivalent.ru.txt')).read_text()
    metadata={'label':item['title'],'caption':f'Демонстрация {n}. {item["title"]}. Учебная схема, не запись интерфейса CapCut Desktop. Видео без диктора; пояснения показаны на экране. Ф1 — вымышленный пример.',
              'transcript':transcript,'provenance':'Оригинальная учебная схема AI Courses, Remotion; оригинальная процедурная музыка Minimal Tech Ambient и мягкие тональные сигналы Quality V2. Без записи реального CapCut, сторонней музыки и дикторской озвучки. Локальные шрифты Noto Sans; существующие лицензии сохранены. Авторское разрешение на интеграцию необходимо подтвердить.',
              'after_section':proposal['expected_before']['source_sections'][item['section']-1]}
    assert set(metadata)=={'label','caption','transcript','provenance','after_section'}
    for k,limit in [('label',255),('caption',2000),('transcript',20000),('provenance',4000),('after_section',255)]:assert 0<len(metadata[k])<=limit
    assert len(raw)<=250*1024**2
    assert abs(float(info['format']['duration'])-item['seconds'])<.1
    records.append({'order_for_upload':n,'file':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'seconds':item['seconds'],'kind':'video','content_type':'video/mp4','metadata':metadata,'subtitles':None,'subtitles_note':'No spoken narration; accessible visual equivalent supplied, no fabricated spoken VTT.','ffprobe':{'streams':info['streams'],'format':info['format']},'approval':'existing Video1 approved' if n==1 else 'new full export requires author viewing/listening before integration'})
manifest={'status':'REVIEW_ONLY_NO_UPLOAD_OR_DB_CHANGE','target':proposal['target'],'endpoint':'POST /api/studio/lessons/113/attachments/','batch_importer_compatible':False,'requires_explicit_integration_approval':True,'requires_fresh_verified_database_and_media_backup':True,'text_update_proposal':'content/quality-v2/lesson-113-sync-proposal.json','attachments':records}
target=ROOT/'content/quality-v2/lesson-113-video-integration.json'
if target.exists():raise SystemExit('Refusing overwrite: '+str(target))
target.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print('Prepared review-only manifest:',target)
