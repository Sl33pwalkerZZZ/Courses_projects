# Course 10 — C3: intermittent lesson113 playback403 diagnosis

Дата:2026-11-23. Ветка feat/studio-course-authoring, HEAD76710ba. Задача — диагностика и предложение исправления. Production-код не изменялся, исправление не применено.

## Итог

403 подтверждён на реальном изолированном Django/Chromium и без управляемой задержки. Это гонка общей attachment-scoped cookie между перекрывающимися grant-запросами и корректным отзывом устаревшего grant. Не проблема файла, прав зачисленного студента или истечения TTL в зафиксированном случае. После повторного открытия видео может работать, потому что порядок прихода ответов меняется.

## Реализация и правила

- courses/video.py: PlaybackGrantView POST/DELETE; PlaybackView HEAD/GET; URLs в courses/urls.py; LessonPlaybackGrant в courses/models.py; courses/permissions.py текущий lesson-access; courses/media.py безопасное private path-разрешение.
- frontend/src/utils/lessonVideo.js: authenticated grant POST, same-origin native URLs, cleanup точного nonce; frontend/src/components/learning/LessonVideo.jsx: effect/start/dispose/load и ручной retry; frontend/src/api.js сохраняет P0 stale-session reject/revoke.
- TTL по умолчанию300s, ограничение30–900s, дополнительно min с остатком срока access JWT. Grant нельзя продлить простым Range.
- Подписанная cookie содержит uid,attachment pk,sha,exp,auth hash,nonce; сервер хранит nonce hash и FK user/attachment. Attachment принадлежит уроку, права на текущий урок проверяются при каждом запросе. Cookie HttpOnly/SameSiteStrict/SecureHTTPS, path конкретного attachment playback.
- HEAD/GET повторно проверяет активного пользователя, действующий неотозванный grant, срок, привязку attachment/sha/password hash и текущий enrollment/owning-author/admin-access. Многоразовый grant разрешает несколько Range; Range сам grant не расходует.
- DELETE по подписанному revocation-only proof отзывает только его nonce без подстановки JWT другого аккаунта. Старый DELETE не отзывает новый nonce напрямую.
- При unmount dispose отзывает grant; повторное открытие/полная загрузка страницы создаёт новый. Закрытие документа не гарантирует React cleanup; серверный TTL остаётся защитой.
- expiresAt передаётся frontend, но не используется для автоматического обновления. После реального истечения следующий Range закономерно получает403; это отдельное поведение, не причина раннего403 здесь.

## Установленная гонка

1. Effect запускает POST A.
2. Cleanup помечает A неактивным; новый effect запускает POST B. В development это вызывает React StrictMode (main.jsx20–28); быстрый remount тоже может перекрыть запросы.
3. Ответ B первым устанавливает cookie lesson_playback_<attachment> и даёт URL активному плееру.
4. Поздний ответ A устанавливает cookie с тем же именем/path, заменяя B на A ещё до JS-проверки active.
5. JS отвергает устаревший результат и правильно отзывает A.
6. Активный плеер использует общий URL и отправляет cookie A. Следующий GET/Range получает403, поскольку A уже revoked.

Серверная авторизация работает как написано. Ошибка — совместное cookie-место для разных жизненных циклов плеера. Отключать отзыв, StrictMode или права доступа как решение нельзя. Версия production без StrictMode-двойного effect отдельно не проверялась; нельзя объявлять, что проблема возникает только в development.

## Точное наблюдение без задержки

Все номера grants ниже относятся только к синтетической временной БД; секретные cookies/proofs/JWT не записывались.

| Monotonic time | Событие |
|---|---|
|8960.604573|POST /api/lesson-attachments/10/playback-grant/ →200, новый grant56, ответ отправлен первым|
|8960.620770|Предыдущий POST того же attachment →200, старый grant55, ответ отправлен позже|
|8960.840805|DELETE /api/lesson-attachments/10/playback-grant/ →204, target55|
|8964.318596|GET /api/lesson-attachments/10/playback/, Range: bytes=163840- →403, cookie grant55|

Тело403:

```json
{"detail":"Playback authorization expired or access denied."}
```

На сервере для отказавшего GET:revoked=True,expires_in=294.57;user_active=True,user_match=True,attachment_match=True,sha_match=True,auth_hash_match=True,lesson_access=True. Подпись успешно разобрана. Не прошёл именно поиск неотозванного grant в PlaybackView.get; валидный grant56 существовал, но браузер отправил cookie55.

Управляемая задержка первого ответа на0.8s только в isolated middleware также воспроизвела гонку для всех трёх видео. Для этих403 remaining expiry267–269s, остальные проверки успешны. Это не изменение приложения или настроек рабочего сервера.

## Реальные браузерные проверки

- Свежая SQLite schema с миграциями только в /tmp; синтетические teacher/student/outsider. Воспроизведены Course10 slug/id и reference lesson113/114 с исходными разделами/attachment IDs и побайтовыми копиями защищённых файлов. Не копировались реальные users/enrollments/progress.
- Chromium + настоящий React/Vite/Django, не mockAPI. Урок113: три видео9/10/11. Два полных открытия и два перехода113→114→113 для студента, аналогично для преподавателя через настоящий Studio preview.
- Студент: все три могут запуститься/перемотаться; в первом открытии второй плеер получил403 на Range, после возврата все три успешно работали. Есть повторные полностью успешные циклы — сбой непостоянный.
- Преподаватель: корректный вход через /instructor/courses/ai-media-content/preview и UI-ссылку в урок; гонка также проявилась при загрузке/перемотке; повторный возврат может восстановить все три плеера.
- Контролируемый прогон с задержкой: все три Range-пути воспроизвели revoked-cookie403. Начало воспроизведения могло использовать уже буферизованные байты, затем Range падал — metadata readyState4 не доказывает успешную перемотку.
- Посторонний в отдельном свежем Chromium: GET lesson113 →403, videos=0; POST grant9 →403 {detail:No access to this lesson.}; GET file9 →403 {detail:Playback authorization expired or access denied.}. Авторизованный JWT без enrollment не даёт grant/файл. Cookies иных аккаунтов не переносились в этот контроль.
- Первый вспомогательный прогон остановился на некорректном обычном маршруте преподавателя (не preview); итоговый прогон использовал правильный preview и независимые browser sessions. Это ошибка тестового маршрута, не новая регрессия курса.

## Проверки

-36Django tests passed: courses.test_video,courses.test_attachments,studio.test_attachment_placement. Подготовительные запуски были прерваны и не учитываются как успешные. Финальный запуск без диагностического middleware:36/36,0failed.
-61frontend tests passed: lesson-video.test.mjs,session-isolation.test.mjs. Они не покрывали позднюю Set-Cookie замену.
- Дополнительный deterministic regression из /tmp:1test,0passed,1failed с EXPECTED ASSERTION actualTrue/expectedFalse «active playback must not send a revoked cookie after an obsolete response». Это подтверждение отсутствующего исправления, не зелёный тест. Первоначальный sandbox-запуск без подробного assertion не считался доказательством; финальный TAP-запуск подтвердил именно assertion.
- Frontend lint passed; production build passed. Django system check и git diff --check passed.
- Native security_reviewer выполнил независимый read-only trace, подтвердил security-ограничения и гипотезу до browser proof; тесты агент не запускал.
- Приложение, модели, миграции, permissions, C1/C2, live media и settings не изменялись.117 защищённых рабочих файлов (SQLite/settings/media/public-media) совпадают поSHA-256. До отчёта git status совпал с исходным. Working integrity=ok,FK0,Course10 unpublished. Нет staging/commit/push.

## Среда/воспроизведение

Приватный каталог0700: /tmp/course10-c3-jqb6x28b. В нём settings_c3.py,settings_tests.py,bootstrap.py,content.json,media/,test.sqlite3,credentials.json,frontend.mjs,browser-final.mjs,c3trace.py. Учётные данные/JWT/cookie/proof не переносить в отчёт или Git. Временные данные не являются постоянным backup.

Доказательства: browser-results-final.json,browser-final.log,server-trace-final.jsonl,backend-verified-tests.log,frontend-tests.log,lint.log,build.log,race-regression-verified.log,preservation.json. Журнал только safe metadata/grant row IDs/booleans, без заголовков Authorization/Cookie и токенов. Оба созданных тестовых сервера остановлены. Прежние QA-артефакты не удалялись.

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/tmp/course10-c3-jqb6x28b:$PWD DJANGO_SETTINGS_MODULE=settings_tests .venv/bin/python -B manage.py test courses.test_video courses.test_attachments studio.test_attachment_placement --verbosity 2
cd frontend
node --test tests/lesson-video.test.mjs tests/session-isolation.test.mjs
npm run lint
npm run build
# Из корня: git diff --check
```

## Минимальное надёжное исправление — предложение, НЕ реализовано

Изолировать playback-cookie по конкретному grant, а не только attachment: новый URL/path-slot с не секретным grant selector и отдельной HttpOnly cookie. Selector сам по себе не авторизует файл; сохранить подпись,nonce,TTL,current access,file hash и P0 session isolation. Существующий grant PK позволяет обойтись без изменения схемы. Поздний Set-Cookie A тогда не заменяет cookie B, а отзыв A не ломает B.

Нужны согласованные небольшие изменения courses/video.py,courses/urls.py,frontend/src/utils/lessonVideo.js и связанных tests. Document-local очередь POST могла бы уменьшить StrictMode-гонку, но не защищает межвкладочные/перезагрузочные перекрытия; один retry только скрывает причину. Отключение revocation или expiry неприемлемо.

Для закрытияC3: реализовать cookie/path isolation; добавить постоянный regression с реальной моделью cookie slots нового протокола и добиться зелёного результата; проверить старый поздний ответ/cleanup после новогоgrant,StrictMode,быструю навигацию/перезагрузку,две вкладки и смену аккаунта; повторить реальные Range/seek три видео и VTT, expiry/revocation/outsider denial, не ослабляя доступ. Автоматическое bounded обновление истёкшего grant — отдельное улучшение, не подмена исправления гонки.

### Временный failing regression

Импорт <REPO> заменить своим абсолютным корнем. Это ожидаемо красный воспроизводитель текущего shared-cookie протокола. Для будущего per-grant протокола regression должен моделировать отдельные cookie paths либо использовать реальный browser/API, а не механически сохранять один cookie-slot в mock.

```javascript
import assert from 'node:assert/strict'
import {test} from 'node:test'
import {requestVideoPlayback} from '<REPO>/frontend/src/utils/lessonVideo.js'
test('late disposed response must not invalidate the active player cookie',async()=>{
 const previous=globalThis.fetch, pending=[], revoked=new Set(),loaded=[];let cookie
 globalThis.fetch=async(_url,options)=>{revoked.add(JSON.parse(options.body).revoke_token);return {ok:true}}
 const client={post:()=>new Promise(resolve=>pending.push(token=>{cookie=token;resolve({data:{url:'/api/lesson-attachments/9/playback/',revoke_token:token}})}))}
 try{
  const old=requestVideoPlayback(client,9,()=>assert.fail('obsolete callback'),()=>assert.fail());old.dispose()
  const current=requestVideoPlayback(client,9,data=>loaded.push(data),()=>assert.fail())
  pending[1]('synthetic-current');await current.promise
  pending[0]('synthetic-old');await old.promise
  assert.equal(loaded.length,1)
  assert.equal(revoked.has(cookie),false,'active playback must not send a revoked cookie after an obsolete response')
 }finally{globalThis.fetch=previous}
})
```
