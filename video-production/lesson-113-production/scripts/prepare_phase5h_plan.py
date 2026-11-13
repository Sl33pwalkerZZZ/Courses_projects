"""Create review-only Lesson113 text proposal/transcripts. Never opens the database."""
import hashlib,json
from pathlib import Path
from prepare_music_preview import ROOT

CONTENT=ROOT/'content/quality-v2'
snapshot=json.loads((CONTENT/'lesson-113-readonly-snapshot.json').read_text())
assert (snapshot['id'],snapshot['course_id'],snapshot['module_id'],snapshot['slug'])==(113,10,39,'ai-media-content')
assert not snapshot['is_published'] and not snapshot['attachments']
learning=snapshot['learning_content'];assert len(learning['objectives'])==3 and len(learning['source_sections'])==9
original=snapshot['text_content'];paragraphs=original.split('\n\n');edits=[]


def exact(prefix):
    matches=[p for p in paragraphs if p.startswith(prefix)]
    assert len(matches)==1,prefix
    return matches[0]


def replace(before,after,reason):
    assert original.count(before)==1
    edits.append({'before':before,'after':after,'reason':reason})


p=exact('Запишите сообщение одним предложением')
replace(p,p+'\n\n'+'В уроке используются три короткие видеодемонстрации без диктора. Музыка и звуки интерфейса не несут обязательной учебной информации; те же действия объяснены текстом. Визуальные рабочие области — схемы, а не запись CapCut Desktop и не подтверждение выполненного сохранения. Названия команд сверяйте со своей версией. Длительности демонстраций 46, 47 и 54 секунды не относятся к 45-секундному ролику Ф1 из упражнения: это отдельные объяснения его подготовки.','Один раз объяснить схематичность, отсутствие диктора и различие длительности упражнения/учебных видео.')
p=exact('Название проекта и папка исходников')
replace(p,'Проект F1_horizontal_v01 и файл f1-paper-approved.png — разные объекты. Переименование проекта не переименовывает исходники. Перемещение или удаление материала может нарушить связь с проектом; поэтому организуйте рабочую папку до импорта и храните исходники отдельно.','Сократить повтор общей последовательности и связать независимые определения с теми же именами, что в видео.')
p=exact('Знакомый интерфейс сервиса')
replace(p,p+'\n\n'+'Посмотрите демонстрацию 1 «Подготовка исходников». Проследите, где находятся рабочие копии и как проверяется происхождение. Имена файлов в схеме — примеры; слово approved само по себе не подтверждает права. После просмотра проверьте свою папку по этим же признакам, не меняя оригиналы.','Приглашение перед плеером после раздела 3; сохранить все исходные объяснения о правах.')
p=exact('Кадровый план — таблица будущих сцен')
replace(p,'После первой демонстрации подготовьте отдельную папку, выберите копии и запишите автора, источник и условия для каждого материала. Неподтверждённое исключите. Теперь сопоставьте подготовленный набор с кадровым планом.\n\n'+p,'Практический шаг расположен в следующем разделе, то есть после inline-плеера раздела 3.')
p=exact('Перенесите первое изображение на видеодорожку')
replace(p,'Перенесите f1-paper-approved.png на начало видеодорожки и поставьте курсор времени внутри клипа. Убедитесь, что предпросмотр показывает тот же лист. Это пока черновой первый кадр; остальные сцены и длительности уточним в разделе 7. Не выбирайте готовый шаблон вместо базовой сборки: он может добавить неподходящую музыку, стиль или условия использования. Для первого опыта достаточно собственных материалов и обычных монтажных действий.\n\n'+'Посмотрите демонстрацию 2 «Проект и импорт». Сначала появляется пустое рабочее пространство, затем библиотека получает подготовленные файлы; изображение выбирают до размещения на таймлайне. Далее показаны первый клип и широкий холст 16:9. Соотношение сторон объясняется подробнее в следующем разделе.','Убрать преждевременное добавление всех сцен, согласовать причинный порядок импорт → выбор → первый клип; пригласить к видео перед разделом 6.')
p=exact('Холст — область итогового изображения')
replace(p,'После второй демонстрации создайте обычный проект со своим узнаваемым именем, импортируйте выбранный набор и проверьте первое изображение на таймлайне. Прослушайте свою озвучку отдельно: учебное видео её не воспроизводит. Затем осознанно выберите форму кадра.\n\n'+p,'Практика после плеера раздела 5; определения холста, пропорций и пикселей полностью сохранены.')
p=exact('После нескольких изменений вернитесь')
replace(p,'После нескольких изменений выполните штатное сохранение или проверьте состояние автоматического сохранения так, как предусмотрено вашей установленной версией. Затем вернитесь к списку проектов и снова откройте F1_horizontal_v01. Сверьте порядок, длительности и доступность исходников. Не считайте отсутствие ошибки или вход в аккаунт доказательством сохранения всех материалов; расположение локальных и облачных проектов проверяйте отдельно.','Явно поставить проверку сохранения перед закрытием/открытием, не выдумывая кнопку, сочетание клавиш или облачную гарантию.')
p=exact('Для существенной новой версии используйте')
replace(p,p+'\n\n'+'Если при открытии материал не найден, сначала проверьте доступность исходной папки. Укажите правильный файл штатным способом своей версии редактора и снова проверьте кадр. Сверяйте не только имя, но и содержимое. Не перемещайте и не удаляйте исходники специально ради повторения ошибки из демонстрации.\n\n'+'Посмотрите демонстрацию 3 «Таймлайн и повторное открытие». Схема показывает порядок клипов, отдельную аудиодорожку, уточнение первого кадра и проверку стыка; затем — сохранение/открытие как принцип и условный пример потерянного исходника. Пустая аудиодорожка не означает ошибку: окончательный ритм с голосом уточняется в следующем уроке.','Добавить недостающую условную проверку исходника и честное описание видео; не терять существующее объяснение резервирования.')
p=exact('Ошибка: сначала импортировать всё')
replace(p,'После третьей демонстрации сохраните свою черновую сборку штатным способом, откройте её заново и проверьте порядок, длительности и доступность исходников. Просмотрите стыки без пустых кадров. При ошибке восстановите правильный источник, не создавая проблему намеренно. Это самопроверка, а не оцениваемая работа.\n\n'+p,'Практическая проверка следует за плеером раздела 7 и не добавляет оценки/условий прохождения.')
p=exact('Главное: до монтажа должны быть понятны')
replace(p,'Главное: сообщение, план, права и структура папок должны быть понятны до монтажа. Успешное повторное открытие подтверждает возможность продолжить работу, но не готовность к публикации. Различие исходника, проекта и экспорта сохраняется: готовый MP4 не заменяет редактируемую сборку и исходные материалы.','Сократить повтор определений, оставив самостоятельные определения раздела 2 и важные предостережения.')

proposed=original
for edit in edits:
    assert proposed.count(edit['before'])==1
    proposed=proposed.replace(edit['before'],edit['after'],1)
for heading in learning['source_sections']:
    assert proposed.split('\n\n').count(heading)==1
assert len([p for p in proposed.split('\n\n') if p in learning['source_sections']])==9
source=json.loads((ROOT.parent.parent/'courses/management/media_module_5.json').read_text())['lessons'][0]
assert source['text_content']==original
sha=lambda text:hashlib.sha256(text.encode('utf-8')).hexdigest()
proposal={'status':'PROPOSED_ONLY_REQUIRES_REVIEW_AND_EXPLICIT_DB_APPROVAL','target':{'course_id':10,'slug':'ai-media-content','module_id':39,'lesson_id':113,'learning_content_id':20},'expected_before':{'title':snapshot['title'],'module_id':39,'is_published':False,'text_sha256':sha(original),'source_sections':learning['source_sections'],'objectives':learning['objectives'],'content_language':'ru','interactions':learning['interactions'],'attachment_count':0},'changes':[{'field':'Lesson.text_content','before':original,'after':proposed,'after_sha256':sha(proposed),'edits':edits}],'unchanged':['all three objectives','nine exact section headings','learning-content schema and interactions','F1 educational case','rights/licensing explanations','all other lessons and records'],'source_mirror':{'path':'courses/management/media_module_5.json','existing_text_equals_database':True,'not_modified':True,'future_action':'After approval update only lesson1 text and reviewed pinned importer checksum/tests; do not rerun the create-only importer to patch existing text.'}}
dest=CONTENT/'lesson-113-sync-proposal.json'
if dest.exists():raise SystemExit('Refusing overwrite: '+str(dest))
dest.write_text(json.dumps(proposal,ensure_ascii=False,indent=2)+'\n')
# Accessible text equivalents, deliberately not fabricated spoken captions.
videos=json.loads((CONTENT/'series.json').read_text())
first=json.loads((CONTENT/'video-1.json').read_text())
video1={'id':'source-organization','filename':'m5-l13-v1-source-organization-quality-v2','seconds':46,'scenes':first}
for video in [video1]+videos:
    text='# '+{'source-organization':'Подготовка исходников','project-import':'Проект и импорт','timeline-reopen':'Таймлайн и повторное открытие'}[video['id']]+'\n\n'
    text+='Доступный текстовый эквивалент видео без диктора, не расшифровка речи и не субтитры. Ф1 — вымышленный учебный пример. Все интерфейсы схематичны и не являются записью CapCut. Музыка и сигналы не несут обязательного смысла.\n\n'
    short=[];start=0
    for i,scene in enumerate(video['scenes'],1):
        stamp=lambda n:f'{n//60:02d}:{n%60:02d}'
        text+=f"## {i}. {stamp(start)}–{stamp(start+scene['seconds'])} — {scene['title']}\n\n{scene['instruction']}\n\n{scene['note']}\n\nНа схеме: {scene['goal']}\n\n"
        short.append(f"{i}. {scene['goal']}");start+=scene['seconds']
    text+='\nПовторяйте только безопасные действия в своей версии редактора. Демонстрация не подтверждает реальное сохранение, разрешение на материал, облачную синхронизацию или готовность к публикации.\n'
    path=CONTENT/(video['filename']+'.transcript.ru.md')
    if path.exists():raise SystemExit('Refusing overwrite: '+str(path))
    path.write_text(text)
    (CONTENT/(video['filename']+'.equivalent.ru.txt')).write_text('Видео без диктора; схема, не запись CapCut Desktop. Ф1 — вымышленный учебный пример.\n'+'\n'.join(short)+'\n')
print('Review-only proposal:',len(edits),'exact paragraph edits; objectives3/headings9 preserved; no database opened')
