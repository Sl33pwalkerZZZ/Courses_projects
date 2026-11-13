"""Generate review-only exact text proposal and real spoken-sample VTT; never opens DB."""
from pathlib import Path
import json,hashlib,re
ROOT=Path(__file__).resolve().parents[1]
snapshot=json.loads((ROOT/'content/lesson114-readonly.json').read_text());videos=json.loads((ROOT/'content/series.json').read_text());speech=json.loads((ROOT/'content/speech.json').read_text());before=snapshot['text_content'];paragraphs=before.split('\n\n');edits=[]
def edit(prefix,after,why):
 matches=[x for x in paragraphs if x.startswith(prefix)];assert len(matches)==1
 old=matches[0];new=after(old);assert old!=new;edits.append({'before':old,'after':new,'reason':why})
edit('Работайте с копией проекта',lambda p:p+'\n\nТри видеодемонстрации этого урока — учебные схемы, а не записи интерфейса CapCut Desktop. Они показывают смысл действий без обещания одинакового расположения кнопок во всех версиях. Инструкции даны текстом на экране. Во второй и третьей демонстрациях звучит короткий разрешённый синтезированный пример Ф1 из модуля 4; это образец для сравнения, а не голос инструктора. Под видео доступен текстовый эквивалент.','Честно обозначить схематическую адаптацию исходных планов реальной записи и наличие настоящих звуковых примеров.')
edit('После удаления фрагмента',lambda p:p+'\n\nПосмотрите демонстрацию «Черновой монтаж». Проследите, как выбранный временной клип обрезают, дважды разделяют вокруг паузы, удаляют только выделенную середину и отдельно закрывают разрыв. Затем схема возвращается к неподвижным иллюстрациям Ф1: их упорядочивают и меняют время показа. Ожидаемый результат — понятная последовательность без пустого кадра; исходники сохраняются.','Видео1 после целого раздела3, а не вместо письменной инструкции.')
edit('Кадрирование —',lambda p:'После демонстрации проверьте копию своей сборки. Для временной записи выберите правильный объект, поставьте две смысловые границы и просмотрите результат удаления. Если используете только картинки, измените длительность показа вместо поиска несуществующей записанной паузы. Убедитесь, что не пропали слова, условие использования бумаги или важная подпись. Это необязательная самопроверка.\n\n'+p,'После видео1 следует различающая запись и картинку практика; определение кадрирования сохранено.')
edit('Оставляйте естественные паузы',lambda p:p+'\n\nПосмотрите демонстрацию «Озвучка и баланс». Сначала прозвучит голос без музыки, затем одна и та же реплика с одинаковым музыкальным фрагментом при двух уровнях фона. Уровень и содержание голоса не меняются. Слушайте разборчивость, а не выбирайте значение регулятора как универсальный стандарт. Ожидаемый результат — слышимая целая мысль, поддержанная подходящим изображением.','Видео2 после раздела5; точное описание реального A/B, а не ненаблюдаемой обработки.')
edit('Ручная обрезка и регулировка',lambda p:'После звуковой демонстрации совместите начало разрешённой реплики с нужным кадром, оставьте изображение до конца мысли и прослушайте сначала голос отдельно, затем всю сцену. Если музыка мешает, уменьшите именно её. Проверьте начало и конец слов, паузы и плавность выхода фона. Сохраняйте исходную запись.\n\n'+p,'После видео2 — понятная необязательная практика; исходное различие ИИ/ручных операций сохранено.')
edit('Учебная редакционная ошибка:',lambda p:p.replace('Мы не приводим расчёт экономии','а не измерение экономии').replace('Мы приводим расчёт экономии','а измерение экономии'),'Единственная терминологическая замена: пример соответствует настоящей разрешённой записи, а не отсутствующей новой фразе.')
edit('Проверьте читаемость на светлом',lambda p:p+'\n\nПосмотрите демонстрацию «Проверка субтитров». В ней звучит существующая запись Ф1, а потеря «не» специально смоделирована: ASR-модель для ролика не запускалась. Сравните смысл, запятую и точку, затем время последней реплики — 6,425–8,312 секунды исходной записи. Пример показывает синтаксис SRT и WebVTT; смена расширения не выполняет преобразование. Ожидаемый результат — читаемые блоки, соответствующие реально слышимой речи.','Видео3 после раздела7; никаких вымышленных результатов распознавания или готовых речевых дорожек к беззвучной инструкции.')
edit('Ошибка: разделить не тот клип',lambda p:'После демонстрации субтитров прослушайте короткий разрешённый пример и сравните каждое слово с подписью. Отдельно проверьте отрицание, знаки препинания, начало и конец блока. Повторите просмотр без звука. Если используете смоделированный дефект, подпишите его именно так; это не оцениваемое задание и не результат реального распознавателя.\n\n'+p,'Практика после видео3; все прежние предупреждения и итоги остаются.')
after=before
for e in edits:assert after.count(e['before'])==1;after=after.replace(e['before'],e['after'],1)
headings=snapshot['learning_content']['source_sections']
for h in headings:assert after.split('\n\n').count(h)==1
proposal={'status':'PROPOSED_ONLY_NO_DATABASE_OR_CANONICAL_SOURCE_UPDATE','target':{'course_id':10,'module_id':39,'lesson_id':114},'before_sha256':hashlib.sha256(before.encode()).hexdigest(),'before':before,'after':after,'edits':edits,'preserved_learning_content':snapshot['learning_content'],'placements':[{'video':v['filename']+'.mp4','after_section':headings[[2,4,6][i]],'text_equivalent':v['filename']+'.equivalent.ru.txt','optional_real_spoken_vtt':None if i==0 else v['filename']+'.vtt'} for i,v in enumerate(videos)]}
(ROOT/'content/lesson114-sync-proposal.json').write_text(json.dumps(proposal,ensure_ascii=False,indent=2)+'\n')
def stamp(ms):
 h,rest=divmod(ms,3600000);m,rest=divmod(rest,60000);s,ms=divmod(rest,1000);return f'{h:02}:{m:02}:{s:02}.{ms:03}'
for v in videos:
 text='Учебная схема, не запись CapCut Desktop. Ф1 — вымышленный пример. '+('Без диктора и речевого примера.' if v['id']=='rough-cut' else 'Инструкции на экране; короткая синтезированная речь Ф1 — настоящий разрешённый пример Silero MIT, не диктор урока.')+'\n'
 offset=0;md=f'# {v["filename"]}\n\n'+text+'\n'
 for i,s in enumerate(v['scenes'],1):
  goal=re.sub(r'([а-яА-Я])(\d)',r'\1 \2',s['goal']);text+=f'{i}. {goal}\n';md+=f'## {offset}–{offset+s["seconds"]}с: {s["title"]}\n\n{s["instruction"]} {s["note"]}\n\n{goal}\n\n';offset+=s['seconds']
 (ROOT/'content'/(v['filename']+'.equivalent.ru.txt')).write_text(text)
 (ROOT/'content'/(v['filename']+'.transcript.ru.md')).write_text(md)
 times={'narration-balance':[12.5,23,41],'caption-review':[8,51]}.get(v['id'],[])
 if times:
  vtt='WEBVTT\n\n'
  for start in times:
   for cue in speech['captions']:
    vtt+=f'{stamp(round(start*1000)+cue["startMs"])} --> {stamp(round(start*1000)+cue["endMs"])}\n{cue["text"]}\n\n'
  (ROOT/'content'/(v['filename']+'.vtt')).write_text(vtt)
print('Prepared8 exact proposed edits, preserved3objectives/9headings,3text alternatives,2genuine spoken-sample VTT files. Nothing applied.')
