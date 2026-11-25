# D4 — Animated Liquid Theme Transition: финализация

Дата:2026-11-25. Ветка `design/graphite-lime`, HEAD `f18fda1`. D4 подготовлен к личной визуальной приёмке; это не автоматическое утверждение дизайна. D5 не начат.

## Существовавшая реализация и границы финализации

В checkpoint уже вошли ThemeProvider, Liquid Reveal controller, CSS fallback, Sun/Moon, координация liquid field. Сохранены Obsidian/Frost/Aqua и D3.3 A/B/C/D материалы. Текущий проход продолжил существующие правки, а не перестроил переход. Исходный Git diff: intentional `config/settings.py`, `themeTransition.js`, `liquid-field.test.mjs`; `theme-transition.test.mjs` не отслеживался. Пользовательский внешний safety backup существует: `~/Desktop/ai-courses-d4-safety/`; содержимое архива не читалось и не перезаписывалось.

## Архитектура

- ThemeProvider и дерево маршрутов постоянны. Меняются только theme context и `html[data-theme]`; прежний `ai-courses-theme`, system preference, storage sync и initialization сохранены. DOM не клонируется, route/session keys не меняются, приложение не перезагружается.
- Origin берётся из центра `event.currentTarget.getBoundingClientRect()`, включая Enter. Координаты ограничены viewport; без rect — центр viewport.
- Runtime-проверка `document.startViewTransition` и поддержки polygon. Оригинальный48-точечный органический контур раскрывает новую тему поверх старой. Desktop720ms/mobile560ms, `cubic-bezier(.16,1,.3,1)`. Нет primary whole-page opacity fade, WebGL или новых зависимостей. Sun/Moon вращаются/меняются360ms.
- Firefox143 не имеет native API:420ms интерполяция реальных цветов, границ и теней плюс небольшой декоративный ripple. Отказ native snapshot либо pseudo-element WAAPI также ведёт к этому fallback. Никаких credential/API changes.
- Reduced-motion и скрытый документ: немедленная смена без пространственного эффекта. Генерация callback инвалидирует предыдущие запросы; requestedTheme ref сохраняет чётность rapid toggles. При hidden/reduced interruption применяется последняя запрошенная тема.
- Filled WAAPI после завершения явно `cancel()`, native transition `skipTransition()` освобождает snapshots. Старый `finished` очищает только принадлежащий ему активный transition; не снимает новый fallback. Все timers/ripple/attrs/listeners очищаются.
- Liquid background: физическое движение при native reveal приостановлено; при fallback смешиваются старые/новые пиксели420ms. Дополнительного дорогостоящего full-screen blur нет.

## Исправления и регрессии

1. В исходной версии обработка rejection `ready`/throw `animate` только меняла тему. Исправлена активация polished fallback с apply-once guard; добавлены оба сценария.
2. Filled effect мог удерживать snapshot после окончания. Добавлено явное release/cancel и проверка completion. Реальное окончание подтверждено: `actual-light-dark/state.json` и `actual-dark-light/state.json` содержат `transition:null`, `pseudoAnimations:0`; first-dom→settled не меняет геометрию/материалы.
3. Старый source-assertion liquid-field ожидал ровно один наблюдаемый атрибут. Обновлён до `data-theme` + `data-theme-transition`; cleanup/visibility/reduced проверки сохранены.

Контроллерные тесты покрывают origin/clamp, contour, отсутствие API, reduced/hidden, native completion, rapid stale callbacks, throwing API, visibility interruption, fallback replacement, runtime rejection и освобождение filled effects. Backend/бизнес-логика для обхода тестов не менялись.

## Изолированное окружение

Финальные серверы: Vite5204 → Django8204. Fresh SQLite создана SQLite backup API из read-only подключения. Настройки/SQLite/media/cache и synthetic accounts — только приватный `/tmp/ai-d4-final-*`. Скопированные исходные аккаунты обезличены, submissions удалены только из копии, Course10 author/enrollment назначены синтетическим пользователям в копии. Сертификаты выключены. Пароли/JWT не включены в доказательства.

До авторизации проверен фактический transformed `api.js`: `import.meta.env.VITE_API_URL='/api'`, `/api/courses/` через5204 возвращает200; proxy только8204. В Chromium дополнительно перехватывались/запрещались обращения к8000. Ранний ошибочный стенд без этой переменной обращался GET к8000 и не считается успешной изолированной проверкой. Его диагностические файлы сохранены, не смешиваются с final evidence.

## Chromium

Факты и результаты: `screenshots/d4/final/chromium.json` (дополнялся по этапам; отдельные повторения не считаются независимым полным E2E). Главная/вход/регистрация, каталог, mobile768KK/390EN/320RU, course detail/Profile/lessons115–116, Studio проверяются с настоящим API. На320 переключатель находится в mobile menu, а не в скрытой desktop toolbar.

Проверяются оба направления, DOM identity, focus, route, отсутствие horizontal overflow и cleanup; rapid5 + reload/persistence. Ввод логина/регистрации сохраняется. Прокрутка сравнивается после стабилизации предшествующего тестового fill/focus: программный focus и глобальный smooth-scroll иначе продолжали прокрутку уже во время измерения. Отдельный native/fallback контроль с preventScroll сохранил каталог ровно1564px до/после, без scroll events; правки приложения ради этого не делались.

Финальная серия содержит37 записей /31 уникальных проверок, page errors0, запрещённых обращений к8000=0. Подтверждены несданный текст assignment и выбранный radio quiz в116, непрерывное видео115/captions, несохранённый textarea Studio и reduced-motion. При одном Studio прогоне scroll округлился1214→1215CSSpx; допуск1px явно записан, это не объявляется точным нулём. Окончательные результаты — `chromium.json`/`chromium-summary.json`; ранние BLOCKER были ошибками локаторов/предусловий или завершением временного API и не скрыты как успешные исходные прогоны. Не выполнялись отправки работ, quiz attempts, lesson completion или сохранение реального контента. Проверка формы означает сохранение несданного ввода при теме, не повторение всей аттестации.

## Firefox

Реальный Firefox143.0.3 через **native WebDriver BiDi**, не Playwright MCP. MCP инструменты видимы, но их bundled Firefox1578 отсутствует; браузеры не устанавливались.

- Normal18 переключений: home/login/register ×1440RU/390KK/390EN ×оба направления, фактически fallback.
- Reduced ещё18 переключений: preference=true, без reveal/ripple; мгновенная смена.
- В каждой матрице6 проверок ввода + rapid5/reload persistence. Main DOM, route, scroll, focus сохранены; overflow=false, ripple/pseudo=0.
- Финальная стабильная серия7 проверок: Enter сохраняет фокус/ввод; настоящее переключение вкладки даёт `document.hidden=true`, cleanup после возврата корректен; Profile, Lesson115, Studio editor.
- Защищённое видео115:1.637419→3.717728s во время смены темы, тот жеelement, paused=false, readyState4, error=null, captions=`showing`. Несохранённый textarea Studio сохранён. Никаких save/progress/assessment действий.
- Стабильная серия: console errors0. Сырые публичные матрицы содержат aborted lazy imports/fonts из-за немедленного harness reload; ранний преждевременный play дал AbortError. Они не скрыты и не объявляются дефектом приложения; финальная серия ждала готовности media.

Файлы: `firefox-normal.json`, `firefox-reduced.json`, `firefox-state-final.json`, `firefox-evidence-notes.json` в final. FF recording/FPS не измерены. SWGL framebuffer/слабый desktop ASCII видны в headless; связь с D4 не установлена, необходим аппаратный Firefox владельца.

## Автоматические проверки и SQLite-сбой

- Пользовательский прогон:13 focused passed; lint0warnings/0errors200files; buildVite8.2.2/2554modules PASS.
- Повтор в финализации: `cd frontend && node --test --test-reporter=spec tests/theme-transition.test.mjs tests/liquid-field.test.mjs` — **13 passed,0 failed**. `npm run lint`, `npm run build` — PASS.
- Предыдущий полный набор D4: **462 passed,0 failed,0 skipped**. После возобновления полный набор повторно не запускался: исходная реализация сохранена, focused/lint/build выполнены заново. Это различие важно для воспроизводимости результатов.
- Django: affected test отдельно на временной файловой SQLite —1PASS. Пара `test_stream_close`→`test_unknown_and_path_traversal` —2tests/1error, воспроизводится детерминированно.
- Причина по трассе: `HttpResponse.close` → `request_finished` → `close_old_connections` → `close_if_unusable_or_obsolete` → `SQLite.close`. Во внешней atomic транзакции `TestCase` autocommit=False при ожидаемомTrue; файловое соединение закрывается, следующий setUp использует закрытую БД. Стандартный shared-memory SQLite test backend Django намеренно игнорирует close. Это подтверждённая особенность файловой тестовой конфигурации, не выявленная регрессия D4.
- Полный профильный Django-набор на стандартной изолированной in-memory SQLite: **36PASS,0FAIL**, check0issues. Команда ниже. Зависший sandbox async-run остановлен; разрешённый системный запуск прошёл, production code не менялся.

```sh
PYTHONPATH=/tmp/d4-django-investigation-run:$PWD \
DJANGO_SETTINGS_MODULE=settings_probe \
.venv/bin/python -B manage.py test courses.test_video \
studio.test_section_creation studio.test_attachment_placement \
studio.test_publication_readiness --noinput
```

Временный settings_probe задаёт `/tmp/.../unused.sqlite3`, media/tmp, locmem, certfalse; без TEST.NAME Django создаёт независимую shared-memory DB. Рабочая БД не используется тестами.

## Motion evidence, производительность и независимое ревью

Запись: [настоящий Chromium CDP screencast](screenshots/d4/chromium-liquid-reveal.mp4), H.2641000×760,18.96s,102 полученных кадров с исходными timestamps; системный FFmpeg, без установки tooling. Capture overhead велик; это демонстрация, не performance benchmark. В записи forward partial contour пропущен редкими кадрами, поэтому отдельно снята текущая реализация через Impeccable motion-capture: `final/motion-normal`13 кадров. Scrubber останавливает WAAPI, поэтому его последний `viewTransition=true` **не** используется как finish proof. Окончание доказывается отдельной uninterrupted серией `actual-*` и state.json. Reduced counterpart — `impeccable-reduced` (duration0, без VT).

Native `impeccable_motion_reviewer` недоступен (`unknown agent_type`); использован native frontend_reviewer с motion rubric. Первый verdict recapture был обоснован недостаточными ending/forward кадрами. После дополнения контуром и настоящим native-finish evidence: **ship только для снятого login1000×760**, без обещания FPS/общей плавности всех экранов. Отдельное source-review подтвердило cancellation/rapid/fallback invariants.

Реальное измерение на общем headless Chromium1440×1000/8logicalCPU без recording: ready240.9ms, finished1231.7ms; idle RAF median83.3ms/p95216.7ms, transition median133.2ms/p95283.3ms,22liquid draws за3621.8ms,2longtasks max119ms. Это нагруженный software/headless host, а не аппаратный desktop benchmark. Устойчивые24FPS,60FPS, battery/low-end performance не доказаны. На таком окружении статика/редкие кадры заметны; аппаратная личная оценка обязательна. D4 не объявляет проблему производительности D3.2 решённой.

## Impeccable doctor

Входные findings: stale `.impeccable/design.json` и DESIGN.md sprawl. Sidecar локально синхронизирован с D3.3 материалами/тенями и D4 motion; DESIGN.md не перезаписан и не сокращён, добавлены только актуальные D4 правила. BuildPath/code сохранён, глобальная конфигурация/установки не менялись. Итоговый doctor: stale-sidecar устранён; остался только `design-md-sprawl` (рекомендация по объёму DESIGN.md, не отказ runtime). Compaction автоматически не выполнялась. Итоговый doctor report сохранён отдельно в evidence.

## Точные файлы и будущий checkpoint

Уже tracked в f18fda1, повторно не нужно включать: `ThemeProvider.jsx`, `ThemeToggle.jsx`, `theme-transition.css`, `LiquidEnvironment.jsx`. Они проверены, а не переписаны заново.

Предлагаемый **явный** список будущего D4 commit — только следующие10 путей:

```text
.impeccable/design.json
DESIGN.md
frontend/src/theme/themeTransition.js
frontend/tests/liquid-field.test.mjs
frontend/tests/theme-transition.test.mjs
docs/design/D4_THEME_TRANSITIONS.md
docs/design/REDESIGN_ROADMAP.md
docs/project-memory/CURRENT_STATE.md
docs/project-memory/DECISIONS.md
docs/project-memory/ROADMAP.md
```

Это предложение, staging не выполнялся. Нельзя добавлять `config/settings.py`, SQLite, media, backups, node_modules, все `screenshots/d4/` автоматически либо generated MP4. Evidence отдельно архивировать; при необходимости owner-approved выбранные малые PNG/JSON добавить отдельным решением. Пользовательский safety archive сохранён.

D4 QA artifacts: `docs/design/screenshots/d4/` (PNG/JSON/MP4); полный инвентарь размеров/хешей в `final/evidence-manifest.json`. Они untracked и **исключены из10-file плана**, как и остальные исторические media/QA/untracked. Никакого удаления/перемещения/реорганизации.

## Приёмка и ограничения

Preview: **http://127.0.0.1:5204/**, API8204 изолирован. Временные процессы оставлены для owner review; после перезапуска окружения их нужно поднять заново.

Владельцу: Firefox light↔dark на главной, входе,320px mobile menu; прокрученный каталог/урок; видео115 с captions; несохранённый Studio textarea; rapid toggles и повторное открытие. Оценить качество fallback и аппаратную плавность, не только техническое прохождение.

Никакой рабочей SQLite/settings/media/course mutation, выдачи сертификатов, staging/commit/push/merge. Course10 остаётся unpublished, Course8 сохранён. D4 готов к ручной оценке в описанных пределах; дизайн считается принятым только после решения владельца. D5 не выполнялся.

## Сохранность и итоговый Git review

117 контрольных SHA-256 (SQLite/settings/media) совпали; integrity=ok/FK0, Course10published=false. Course8 неизменён по byte-exact сохранности всей рабочей БД. Предложенные10файлов проверены по пути/размеру и high-confidence secret patterns: совпадений0, файлов>1MiB нет. Это целевой scan, не формальное доказательство отсутствия всех возможных секретов. Index пуст. Снимок ниже включает и исторические local-only/untracked материалы; он не является списком staging.

```text
 M .impeccable/design.json
 M DESIGN.md
 M config/settings.py
 M docs/design/REDESIGN_ROADMAP.md
 M docs/project-memory/CURRENT_STATE.md
 M docs/project-memory/DECISIONS.md
 M docs/project-memory/ROADMAP.md
 M frontend/src/theme/themeTransition.js
 M frontend/tests/liquid-field.test.mjs
?? .agents/
?? .local-cinematic-qa/
?? .local-video-test/
?? .vite/
?? backups/
?? course_assets/module_4/m4-audio-production.json
?? course_assets/module_4/m4-l1-f1-natural-narration.mp3
?? course_assets/module_4/m4-l1-f1-synthetic-narration.wav
?? course_assets/module_4/m4-l12-ru-roman-room-after-v2.wav
?? course_assets/module_4/m4-l12-ru-roman-room-before-v2.wav
?? course_assets/module_4/m4-l2-f1-corrected-transcript.txt
?? course_assets/module_4/m4-l2-f1-speech.wav
?? course_assets/module_4/m4-l2-f1-synchronized.srt
?? course_assets/module_4/m4-l3-f1-clean-reference.wav
?? course_assets/module_4/m4-l3-f1-original.wav
?? course_assets/module_4/m4-l3-f1-processed.wav
?? course_assets/module_4/m4-room-noise-v2.json
?? course_assets/module_4/voice_candidates/README.md
?? course_assets/module_4/voice_candidates/evaluation.json
?? course_assets/module_4/voice_candidates/generate_candidates.py
?? course_assets/module_4/voice_candidates/lesson12-self-contained-dsp/
?? course_assets/module_4/voice_candidates/prepare_filter_v3.py
?? course_assets/module_4/voice_candidates/prepare_room_noise_v2.py
?? course_assets/module_4/voice_candidates/prepare_self_contained_dsp.py
?? course_assets/module_4/voice_candidates/requirements-evaluation.txt
?? course_assets/module_4/voice_candidates/ru_roman_refined/
?? course_assets/module_4/voice_candidates/test_candidates.py
?? course_assets/module_4/voice_candidates/test_filter_v3.py
?? course_assets/module_4/voice_candidates/test_roman_module4.py
?? course_assets/module_4/voice_candidates/test_room_noise_v2.py
?? course_assets/module_4/voice_candidates/test_self_contained_dsp.py
?? course_assets/module_4/voice_candidates/v5_cis_base_nostress-ru_marat.wav
?? course_assets/module_4/voice_candidates/v5_cis_base_nostress-ru_roman.wav
?? course_assets/module_4/voice_candidates/v5_cis_base_nostress-ru_zhadyra.wav
?? course_assets/module_5/m5-l13-v1-production/narration-preview.wav
?? courses/test_module4_audio.py
?? docs/courses/media-module-4-legacy-assets.json
?? docs/courses/module-4-audio-demonstrations.md
?? docs/courses/module-4-cleanup-inventory.json
?? docs/courses/module-4-elevenlabs-provenance.json
?? docs/courses/module-4-rnnoise-COPYING.txt
?? docs/courses/module-4-rnnoise-license-audit.json
?? docs/design/D4_THEME_TRANSITIONS.md
?? docs/design/screenshots/d3/
?? docs/design/screenshots/d31/
?? docs/design/screenshots/d32/
?? docs/design/screenshots/d33/
?? docs/design/screenshots/d4/
?? docs/instructor-studio/e2e-101848f-real-api.md
?? docs/instructor-studio/e2e-c7f9aa7-real-api.md
?? "e modules 2-4 and inline learning media\""
?? frontend/tests/theme-transition.test.mjs
?? scripts/generate_module_4_audio.py
?? skills-lock.json
?? video-production/lesson-114-production/node_modules
?? video-production/lesson-114-production/out/
?? video-production/lesson-114-production/public/f1-speech.wav
?? video-production/lesson-115-production/audio/music/
?? video-production/lesson-115-production/audio/narration/
?? video-production/lesson-115-production/audio/narration_sentences/
?? video-production/lesson-115-production/node_modules
```

Tracked diff-stat (не включает новые файлы; содержит intentional local settings, исключённый из плана):

```text
 .impeccable/design.json               | 39 +++++++++++++++++++++++++++--------
 DESIGN.md                             | 12 +++++++++--
 config/settings.py                    | 12 ++++++++---
 docs/design/REDESIGN_ROADMAP.md       |  2 +-
 docs/project-memory/CURRENT_STATE.md  |  8 +++++++
 docs/project-memory/DECISIONS.md      |  8 +++++++
 docs/project-memory/ROADMAP.md        |  2 +-
 frontend/src/theme/themeTransition.js | 16 +++++++++-----
 frontend/tests/liquid-field.test.mjs  |  2 +-
 9 files changed, 79 insertions(+), 22 deletions(-)
```
