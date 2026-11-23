# Course 10 — C3.1 per-grant cookie isolation

Дата:2026-11-23. Ветка feat/studio-course-authoring, HEAD76710ba. C3 diagnosis preserved in video-playback-c3.md. Исправление выполнено локально, без рабочего DB/media/settings write, staging/commit/push.

## Архитектура

POST /api/lesson-attachments/<attachment>/playback-grant/ остаётся прежним authenticated API. Он создаёт существующую LessonPlaybackGrant без изменений схемы и возвращает:

- URL /api/lesson-attachments/<attachment>/playback/<grant_pk>/;
- срок действия;
- существующее подписанное revocation-only proof в авторизованном JSON, не в URL.

Selector grant_pk — открытый идентификатор, не credential. Cookie называется lesson_playback_<attachment>_<grant_pk>, Path точно равен URL. Значение — подписанный payload gid/nonce/uid/pk/sha/exp/auth, HttpOnly, SameSite=Strict, Secure наHTTPS. Никаких JWT/nonce/signature/revoke proof в URL или публичном ответе.

Для двух grants одного attachment и имя, и Path различаются. Поздний Set-Cookie A не заменяет B. Отдельное имя также исключает затенение новой cookie legacy-cookie с родительским Path.

PlaybackView проверяет gid==selector и PK серверной записи вместе с точным nonce hash, пользователем, attachment, revoked/expiry, file SHA, password auth hash и текущим доступом к уроку. TTL300s по умолчанию с clamp30–900 и ограничением остатком срока access JWT сохранён. Range200/206/416,HEAD,private/no-store,path confinement и bounded streaming не менялись. Это прежняя user/auth-hash/TTL привязка; не добавлена непрерывная проверка JWT blacklist при каждом Range.

DELETE по существующему nonce-specific proof отзывает только его запись, затем удаляет только cookie соответствующих имени/Path. Повторный DELETE безопасен. Общая legacy-cookie не удаляется, поскольку могла обслуживать другого старого плеера; отозванный nonce в ней всё равно не авторизует файл. Отсутствие proof не позволяет выбрать чужую запись.

Frontend safePlaybackPath принимает новый числовой сегмент и прежний защищённый формат; query/cross-origin/token URLs отвергаются. LessonVideo lifecycle,dispose,ручной retry,StrictMode и P0 session-generation rejection/revocation не отключались.

## Обратная совместимость

- Старое имя маршрута lesson-playback и URL .../playback/ сохранены только для legacy signed cookies без gid. Сервер не выпускает новые legacy cookies.
- Старые cookies ограничены первоначальными exp/nonce/DB/current-access проверками. Подстановка нового signed payload в legacy-cookie-name отвергается; старого payload в новый slot — тоже.
- Перенос B-cookie в A-name, другой selector или attachment не даёт доступа. ID без cookie не авторизует запрос.
- Новая версия frontend работает со старым backend URL (unit test). Уже открытые старые native URL работают после обновления backend до исходного TTL.
- Кешированный старый JS bundle не распознаёт новый URL в своём строгом validator: нужен hard refresh/согласованное обновление frontend+backend. Полная прозрачность нового POST для старого JS не заявляется. Обхода через public media/анонимную выдачу не добавлено.
- Миграции и обновление БД/вложений не требуются.

## Regression tests

Django:41passed — courses.test_video,courses.test_attachments,studio.test_attachment_placement. Пять новых C3.1 cases:

1. Ответы B→A доставлены в cookie jar; после отзыва A его URL403, B Range206/HEAD200; DELETE чистит только A-path/name; повторный DELETE не ломает B.
2. Два grants одного attachment, перенос подписанной cookie между selector/name, cross-attachment replay и запрос без cookie.
3. Legacy206, namespace separation и реальный отзыв legacy-доступа.
4. Legacy expiry/inactive-account denial без fallback.
5. HTTPS Secure/HttpOnly и запрет после изменения file SHA.

Существующие scoped Range/416/expiry/password change/enrollment removal/path traversal/stream close tests проходят. Tests используют disposable SQLite и temporary media; настоящий рабочий курс не читается тестами.

Frontend:64passed — lesson-video.test.mjs,session-isolation.test.mjs. Три новых case: strict scoped URL whitelist, A-late-after-B с независимыми slots/cleanup, несколько плееров+VTT с независимым dispose. P0 obsolete-session test проверен с новым URL; старый response не попадает следующему аккаунту и отзывается без егоJWT.

Дополнительно frontend lint,production build,Django check,git diff --check passed. Подготовительный sandbox backend-запуск был прерван; финальный успешный прогон выполнен с доступными async threads. Постоянных failing tests не добавлено.

## Реальный Chromium E2E

Свежая изолированная SQLite /tmp/course10-c3-se02p8od/test.sqlite3 и private media-копии. Синтетические author/student/outsider, enrollment только в ней. Для reference lesson113/114 скопированы учебные тексты, anchors и восемь attachment records/files, сохранены fixture IDs; рабочие users/progress не копировались. Course10 fixture draft. Настоящие JWT/UI/API, никакого mock backend.

Финальный browser-c31.mjs:

- Студент:113→три запуска/seek20s→114→113,повторное полное открытие и возврат;3быстрых UI-переключения туда/обратно и ещё проверка всех плееров.
- Преподаватель:тот же сценарий через реальный /instructor/courses/ai-media-content/preview и ссылку в урок, сохраняющую preview state.
- Дополнительно delayed first response0.8s в isolated middleware при включённом StrictMode;33 native playback/seek assertions суммарно прошли, media errors отсутствуют.
- Два дополнительных параллельных grants attachment9 с delayed order:после DELETE A, A URL403, B Range206. URL различаются, секреты не выводились.
- Посторонний в отдельной свежей browser session:lesson113403/videos0,POSTgrant403,legacyfile403,scopedfile403.

Отдельный two-tabs.mjs:две реальные вкладки одного студента одновременно открыли113. В обеих три video прошли native play/seek25s с декодированными кадрами. ВкладкаB ушла в114 (cleanup своих113grants), вкладкаA продолжила все три; B вернулась и снова воспроизвела все три. В114 нативные WebVTT включались(showing),загрузили9и6cues и выключились(disabled).

Первоначальная гонка действующего113-плеера НЕ воспроизвелась. Ожидаемые403 для намеренно отозванного A и outsider сохранены. Журнал также фиксировал403 уже отозванных pending preload-запросов114 после быстрых уходов со страницы: эти URL не являются действующим113-player slot, все активные assertions прошли. Не утверждается отсутствие любого403 вообще.

Подготовительные browser-прогоны остановились из-за недостаточных фиксированных ожиданий DOM/metadata. Финальный harness ждёт заголовок целевого урока,HAVE_CURRENT_DATA и фактическое продвижение playback clock; проблем не скрывает ретраями API. Результат acceptance относится к завершённому финальному прогону, не к прерванным.

## Изоляция и артефакты

Каталог /tmp/course10-c3-se02p8od имеет права0700. Тестовые серверы8197/5197 остановлены. Сохранены browser-accepted.log,browser-results-c31.json,two-tabs.log,two-tabs-results.json,server-trace-final.jsonl,backend-final-tests.log,frontend-verified-tests.log,lint.log,build.log,preservation.json. Временный каталог не постоянный архив. Credentials/cookies/proofs/JWT не переносить в Git/отчёты; safe trace содержит только path,status,grant row ID и booleans.

Все117 рабочих SQLite/settings/media/public-media файлов совпали поSHA-256. Working integrity=ok,foreign_key_check=0,Course10 unpublished. C1/C2,Course8,реальные медиа,сертификатные настройки не менялись. Прежний config/settings.py diff и C3 untracked report сохранены. Index пуст, нет commit/push.

## Команды проверок

Временные settings_tests.py наследуют project settings, но направляют default DB/media только в /tmp и отключают диагностический middleware; test runner использует in-memory SQLite.

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/tmp/course10-c3-se02p8od:$PWD DJANGO_SETTINGS_MODULE=settings_tests .venv/bin/python -B manage.py test courses.test_video courses.test_attachments studio.test_attachment_placement --verbosity 1
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/tmp/course10-c3-se02p8od:$PWD DJANGO_SETTINGS_MODULE=settings_tests .venv/bin/python -B manage.py check
cd frontend
node --test tests/lesson-video.test.mjs tests/session-isolation.test.mjs
npm run lint
npm run build
# Из корня:git diff --check
```

## Изменённые файлы

- courses/video.py
- courses/urls.py
- courses/test_video.py
- frontend/src/utils/lessonVideo.js
- frontend/tests/lesson-video.test.mjs
- frontend/tests/session-isolation.test.mjs
- docs/protected-lesson-video.md
- docs/courses/video-playback-c31.md
- docs/project-memory/CURRENT_STATE.md
- docs/project-memory/DECISIONS.md

Native security_reviewer выполнил read-only review фактического diff и namespace/permission границ, блокеров не найдено. Тесты и реальный browser E2E выполнял основной агент.

## Статус

C3 закрыт для подтверждённой cookie-collision гонки в локальном коде и изолированной Chromium-проверке. Нужны совместное обновление backend/frontend и refresh старого bundle при последующем запуске. Автоматическое обновление истёкших grants не добавлялось: ручной Retry и bounded TTL остаются прежними. Внешняя production-топология/реальный Firefox аккаунт не проверялись; это не заявляется результатом данного E2E.
