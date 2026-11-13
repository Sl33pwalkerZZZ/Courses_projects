# P1E — безопасный Git checkpoint: preflight

## P1M — staged whitespace resolution (2026-11-13)

Текущий план:273 unique staged paths, группы31/21/18/176/27. Добавлен только `.gitattributes` в группу4. Исправлены исключительно trailing whitespace/EOF blanks в11 неприкреплённых к byte-exact hashes source/docs/transcript/storyboard файлах; semantic tokens неизменны. Исходные13 affected files и план/memory сохранены в проверенном private backup вне репозитория до правок.

Два VTT Lesson114 сохранены побайтно: `content/m5-l14-v2-narration-balance-quality-v2.vtt` и `content/m5-l14-v3-caption-review-quality-v2.vtt` внутри `video-production/lesson-114-production/`. Их SHA-256 закреплены в `courses/management/lesson114_quality_v2.json`, production `content/final-assets.json`, asset manifest и существующих protected attachments. Точные root-anchored `.gitattributes` paths отключают только `blank-at-eof` для этих двух файлов; trailing whitespace и проверки остальных файлов не отключаются. Хеши/approval records не переписывались. Это сохраняет утверждённые media bytes, а не скрывает media mutation.

P1L index review:272 paths были staged, secret scan дал только два заведомо synthetic example.invalid URL; static security reviewer не нашёл подтверждённых блокеров. P1L whitespace claim был исправлен: отдельный cached check выявил25 findings. P1M final results: cached check exit0; все9MP4/5VTT source hashes и14 protected attachment hashes совпали; DB/settings unchanged.27 isolated Django113/114/115 integration tests passed;115 content checks +4music+5verifier tests passed; все5VTT valid. Дополнительные114 production tests:5pass/1fail — `test_frozen_lesson_and_canonical_source` сравнивает historical pre-edit snapshot с утверждённым post-edit canonical. Read-only проверка доказала snapshot==proposal.before, canonical==proposal.after. Это существующая устаревшая проверка, не whitespace regression; в P1M тест/контент не исправлялись. Перед commits нужен отдельный review этого failure; commits/push по-прежнему не разрешены.


## P1K — актуализация 2026-11-13

Этот раздел и пять explicit staging-команд ниже являются текущим планом; численные снимки P1E/P1H ниже сохранены как история. Никакие команды staging не выполнялись.

- Добавлены `certificates/pdf.py`, `certificates/test_pdf.py` в группу1; P1I report в группу5. Private PDF не зависит от public origin; `CERTIFICATE_PUBLIC_ORIGIN` остаётся отдельной конфигурационной задачей публичной verification, не blocker owner download.
- В группу4 добавлены Lesson115 lockfile, read-only verifier и его тесты; README115 уже включён. В группу5 добавлен P1K report.
- P1J recovery archive содержит DB/media/source/history и проверенную sample restoration; он предшествует P1K. Новые P1K sources следует включить в дополнительный source backup либо сохранить утверждённым checkpoint. Ничего не загружать публично.
- Строгие исключения прежние: settings.py, SQLite/backups, protected media, secrets, node_modules, previews/intermediates и неизвестные локальные файлы. Полный allowlist scan и результаты: `docs/courses/checkpoint-readiness-p1k.md`.


Первичный аудит P1E: 2026-11-12. Актуализация P1H: **2026-11-13, Asia/Almaty**. Изменён только этот план; приложение/настройки/БД/индекс не менялись. Команды ниже **не выполнялись**; требуется разрешение владельца.

## Текущее состояние — перепроверено P1H

- `design/amethyst-motion`; HEAD `e1ae750ef14244c56ca92c547bf5e51ca444ae2e`; ahead4 относительно локального origin. Fetch не выполнялся, состояние GitHub не подтверждено.
- **44 modified tracked,751 untracked** (полный NUL-delimited file inventory); staged0; unmerged0. Diff:1920 insertions/325 deletions. `git diff --check` прошёл. P1E было43/747 до создания самого отчёта.
- С P1E добавились пути: `certificates/templates/admin/certificates/change_list.html` (tracked modification), `certificates/test_profile_visibility.py`, `docs/courses/missing-certificate-p1f.md`, `docs/courses/certificates-read-only-p1g.md`, этот план (untracked). Исходные пути не исчезли. Изменения внутри уже dirty Certificate views/services/admin, React Certificate components/тестов/переводов и memory включены текущими whole-file списками.
- Четыре existing commits: `28ff315` — protected video; `ca684c3` — Module5 source/import; `42455ca` — cinematic phases1–3; `e1ae750` — checkpoint tests/docs. Повторный staging их неизменённых файлов не нужен.
- Единственный изменённый tracked-файл вне staging-плана: **`config/settings.py`**, намеренная локальная конфигурация. Значения не выводились. Ignore не защищает tracked-файлы.

## Что исправлено в плане P1H

1. Группа1 пополнена admin template и `certificates/test_profile_visibility.py`; группа5 — отчётами P1F/P1G и самим планом. Новые пути больше не остаются за пределами allowlist.
2. **Исправлена опасная ошибка P1E:** две symlink-зависимости `video-production/lesson-114-production/node_modules` и `video-production/lesson-115-production/node_modules` были ошибочно включены в Remotion source-команду. Обе ведут на `../lesson-113-production/node_modules`. Они исключены из staging, переклассифицированы I/local, на диске сохранены. Не фиксировать локальную установку через symlink.
3. Теперь пять групп содержат **265 уникальных explicit paths**:43 tracked modifications +222 untracked. Размер выбранных файлов около7.45MiB до изменения этого отчёта. Дубликатов между группами нет. Группа4:172 файлов вместо174.
4. P1F/P1G сохраняются целиком: корректный unavailable/empty Profile UI, private certificate reads, отключённые issuance/revoke/admin policy writes, owned/legacy/JWT/PDF security tests. Старые документы P1F/P1E — исторические, текущее поведение описано отчётом P1G.
5. **CERTIFICATE_PUBLIC_ORIGIN остаётся не настроен** по проверке P1G. Не менять settings в checkpoint. Историческая блокировка PDF устранена в P1I: private owner preview/download не требуют origin; владелец сообщил об успешной проверке Firefox. Origin нужен для будущей публичной verification, которая остаётся выключенной. Public verification/QR route намеренно404 при global flagFalse; checkpoint не разрешает включение.

## Решение по checkpoint

Сохранить приложение, миграции, тесты, канонические JSON, integration commands и production source. Не смешивать их с536.1MiB неотслеживаемых материалов/кешей, защищённым storage, рабочей БД и историческими кандидатами. Полная таблица ниже классифицирует **каждый** modified/untracked путь; принадлежность к группе — предлагаемое, а не исполненное решение.

Состав tracked diff: certificate name confirmation + scoped requirements; submission attachments/revisions/reopen; rubric review; enrolled-draft CourseDetail + private/no-store; frontend session/refresh, curriculum/progress, submission/certificate UI и локализация. Module5 canonical JSON обновлён для согласования уже утверждённого текста113/114, importer source hash изменён согласованно. Это существующие изменения, аудит их не редактировал.

## Критические зависимости и проверки

1. Три **untracked обязательные миграции** должны попасть вместе с соответствующими моделями:
   - `certificates/migrations/0005_coursecertificatepolicy_required_lessons.py`
   - `progress/migrations/0005_assignmentsubmissionattachment_and_more.py`
   - `users/migrations/0002_user_certificate_name_and_more.py`
   Existing courses0006/0007, предыдущие migration dependencies, requirements и frontend lockfile уже tracked. Миграции в P1E не запускались.
2. Обязательные untracked runtime-файлы: `progress/assignment_views.py`, `progress/submission_files.py`, `frontend/src/components/learning/AssignmentSubmission.jsx`, `frontend/src/utils/assignmentSubmissionDates.js`. Оставить их вне Git при сохранении импортирующего кода нельзя.
3. Для восстановления Module6 нужны `import_media_module_6.py`, `media_module_6.json` и новые schema/model/service файлы. Importer требует существующий draft Course10 с15 lessons/5 modules. Он не создаёт первый–пятый модули и не переносит текущую SQLite. Полностью чистая БД требует отдельных известных импортов1–5 и утверждённых источников; сами ID/учётные записи автоматически не восстановятся.
4. Lesson113/114/115 integration commands используют pinned JSON и точные SHA-256. Все14 входных файлов трёх планов доступны и соответствуют указанным hash. Среди них9 MP4 и5 VTT. Однако финальные MP4 и VTT115 лежат в ignored `out/`; staging source не сохраняет эти bytes. Нужен отдельный media archive.
5. Lesson114 импортирует `lesson-113-production/src/tokens` и `fonts`; Lesson115 — `lesson-113-production/src/primitives`. Не коммитить проекты поодиночке без этих зависимостей. Исходные SVG/fonts/SFX и лицензии входят в группу4.
6. P1K устранил gaps Lesson115: npm lockfile с неизменённым графом Remotion4.0.540; read-only `scripts/verify.py` и regression tests. Полный прогон проверяет pinned finals, source-only явно не является media QA. Установка зависимостей и рендер не выполнялись.
7. Lesson115 mixing ссылается на music master в `lesson-113-production/out/audio-preview/...wav` и composer `scripts/prepare_music_preview.py`. Composer будет в Git; точный утверждённый WAV нужен в архиве (копия115 —18.4MB). Narration требует внешнего MIT checkpoint с документированным hash и отдельного torch/NumPy окружения; не добавлять model weights или .venv. Побитовое повторение синтеза/рендера не гарантируется только наличием исходников.
8. Final-render gate115 читает ignored `out/qa/frame-review.json` и сверяет `review.inputs` с текущими source/audio hashes. Запись утверждения и требуемые аудиостемы должны сохраняться в архиве; checkout только source без них остановится. Не генерировать фиктивное approval и не обходить gate.
9. P1C связанный E2E-harness существует только в `/tmp/p1c_rehearsal.py`; отчёт и existing suites сохраняются, сам connected regression пока не durable. P1D browser harness/screenshots также временные; это не production dependency.
10. Устаревшие ROADMAP/исторические документы сохраняются как история, но на новом checkout нельзя считать их runtime-состоянием. Противоречие: старые секции пишут о несуществующем Module6/неинтегрированном115; поздний CURRENT_STATE и отчёты уточняют состояние. Нужна отдельная точечная редакция, не удаление истории.
11. Статический проход по выбранным source-кандидатам: missing относительных JS/TS/project Python import-path не найдено; Python AST parse ошибок нет. Проверка не исполняет динамические файловые зависимости. По шаблонам private keys/GitHub/OpenAI token/JWT в просмотренных текстовых source-кандидатах совпадений не обнаружено. Это **не полная гарантия отсутствия секретов**: binaries/cache/settings не выводились; перед реальным commit нужен повторный staged review и секрет-сканер по утверждённому списку. В tracked tree не обнаружены DB/.env/private-key filenames или node_modules.
12. Course8: канонические sources и media отсутствуют в изменённых путях. Общие certificate/progress semantics меняются глобально; `progress/test_selection_maps.py` и certificate regression tests обязательны. Отсутствие изменения course bytes не означает отсутствие риска общей логики — результаты P1C сохраняются как доказательство регрессии.

## Проверки P1H и границы уверенности

- Все265 allowlisted paths существуют как обычные файлы; dependency symlinks исключены. Никаких `out/`, `node_modules`, media storage, .venv, databases/backups, settings или MP4 в staging-командах. Не найдено выбранных файлов больше5MiB.
- Небольшие binary inputs в группе4:8 NotoSans TTF (каждый около0.5MB),8 коротких SFX WAV (не более159KB); рядом включены font licenses и SFX provenance. Это source inputs, не video previews. Отдельный music master18.4MB и narration/stems остаются в архиве, не Git.
- Все14 source assets из integration plans113/114/115 присутствуют и совпадают с SHA-256:9 MP4+5 VTT, всего30.52MiB. Эти bytes не включены в265-path source checkpoint.
- В выбранных текстовых файлах нет совпадений с проверенными шаблонами private keys, GitHub/OpenAI tokens и JWT. Нет Python syntax errors или отсутствующих статических relative JS/TS imports. Это ограниченный скан, не сертификат отсутствия всех возможных секретов; staged diff перед будущим commit обязателен. Не анализировались значения settings/credentials, содержимое learner records, backups и model weights.
- Три новые миграции включены явно. `requirements.txt`, frontend package/lock, `authSession.js`, `lessonVideo.js`, импортёры Modules1–4 и их неизменённые dependencies уже tracked. No dependency installation, migration или production script запусков в P1H.
- P1K закрыл lock/verify gaps115. Source113 и archived audio stems по-прежнему обязательны. Новый script меняет хешируемый render input set: исторические approvals не переписаны; будущий рендер требует нового согласованного hash-matched approval.
- Актуальные P1G результаты57 Django tests (56pass/1skip) и2 frontend test files приведены как результаты **предыдущего этапа**, не новый прогон. P1H — preflight без повторного запуска suites; выполнен новый whitespace/import/existence/hash/allowlist scan.
- Рабочая SQLite/control settings hash проверяются до/после только для сохранности файлов, без открытия learner records. Новый backup не создавался. Существующий проверенный P1F backup описан отдельно; он не попадает в Git.

## Локальные и подозрительные файлы

- Root `.gitignore` покрывает `.venv`, pyc, `db.sqlite3`, `media`, `course_sources`, `.local-course-backups`, recovery archives; frontend отдельно игнорирует dependencies/dist. Но `backups/`, root `.vite/`, `.local-video-test/` и многие production outputs114 видны как untracked. Нельзя полагаться на ignore при широком staging.
- `e modules 2-4 and inline learning media"` —4463 bytes, сохранённый цветной Git diff-stat (в начале перечень Module3 PNG). Похоже на случайную shell redirection, **не доказано**, файл оставить и не включать.
- `.agents/` —179 файлов skill/vendor material, `skills-lock.json` — локальная skill-конфигурация. Не требуется Django/React; отдельное решение владельца. `.local-cinematic-qa/.gitignore` не является разрешением коммитить QA-profile.
- Module4 production7 файлов и `LICENSE_CIS` уже tracked: approved narration10/11, before/after12, illustrative/synchronized SRT, workflow PNG. Untracked ElevenLabs/eSpeak, ru_roman candidates, RNNoise/DSP trials не становятся approved от одного наличия. Они остаются локальными/в историческом архиве.
- `courses/test_module4_audio.py` и `scripts/generate_module_4_audio.py` относятся к историческим генерациям/legacy assets. Не удалять; пока удержать вне текущих commit-групп вместе с этими зависимостями и отдельно проверить их scope. Не подменять финальные Silero assets старыми тестовыми кандидатами.

## Отдельное резервирование (план; не выполнено)

Размеры текущих каталогов: `video-production`3151.8MiB/37756files (включая зависимости и ignored), protected `media`34.3MiB, `course_assets`16.9MiB, `.local-course-backups`199.9MiB, `backups`1.2MiB. Наличие каталогов не доказывает свежесть/полноту бэкапа.

Перед будущим checkpoint/cleanup сохранить вне Git:

- Согласованный SQLite backup через SQLite backup API и integrity/FK verification. Не копировать активную БД простым cp при WAL; не печатать learner data.
- Protected media вместе с DB snapshot; зарегистрированные файлы и SHA manifest. Хранить приватно с ограничениями доступа.
- Утверждённые9 MP4/5 VTT из integration plans, music master, speech cues/stems, subtitle timing JSON, source audio и MIT/license/font provenance. Сохранить относительные пути, hashes, sizes и restore instructions. Для точного повторного импорта нужны исходные утверждённые bytes, не только повторный render.
- Исторические кандидаты/превью отдельным recovery archive; не удалять. Оригинальные DOCX/private sources — отдельный приватный архив, не Git.
- Сделать независимую копию вне VM/диска и проверить чтение/хеши. Для media archive записать version/date, relative path, bytes и SHA-256 каждого final MP4/VTT; отделить9 approved videos/5 tracks от preview/intermediate, сохранить exact music/narration masters, frame-review records, timing JSON и license notices. Проверить распаковку в временную папку и совпадение hashes, не восстанавливая поверх рабочего storage. Защищённый storage/SQLite архивировать приватно согласованной парой, не переносить learner data в source archive. Git — резервирование source, не DB или protected media. LFS/object storage можно согласовать позже; не устанавливать и не переписывать историю автоматически.

Новый backup в P1E не создавался, его integrity не заявляется. Рабочая SQLite проверена только через `mode=ro`/`query_only`: integrity ok, FK0, Course10 is_published=False. Текущий hash `f8a79ad1a69953e3725cc58d43a85cc7459d13b0ce6aa3714a4db573e78c3c2e` отличается от исторического P1D hash `3c45b29b552d7b4ef5f9b78c672c8146317b42c6ab0257cc2c2ef4e105e4ecb3`. В начале P1E свежий hash не снимался: нельзя утверждать, когда/почему изменились bytes. Аудит не выполнял DB writes. Перед будущими действиями нужен свежий согласованный backup, а не предположение, что старый snapshot актуален. Производственные файлы не изменялись.

## Предлагаемые группы и точные staging-команды

Ниже только команды **для последующего разрешения владельца**. Списки explicit paths, без directory staging/globs, без force и без дублирования между группами. Все changes в одном файле сохраняются вместе; patch-splitting не требуется. Dependency order1→2→3→4→5. Группа4 может быть отдельным source checkpoint с явно описанными gaps; не заявлять её полной reproducibility до решения пунктов6–7.

Перед выполнением заново проверить status/index и diff: текущий отчёт не является разрешением на commit. После каждого staging:

```bash
git diff --cached --name-status
git diff --cached --stat
git diff --cached --check
git diff --cached
```

Не выполнять commit, если появился путь вне явного списка, DB/settings/cache/private media или неожиданный binary. Не использовать reset для исправления без отдельного разрешения. Перед будущим commit проверить миграции/тесты в isolated DB и frontend; P1E не повторял ранее прошедшие suites.

### Группа1: `feat: secure assignment reviews and preserve private certificate access`

31 файлов. Предлагаемый staging:

```bash
git add -- \
  certificates/admin.py \
  certificates/migrations/0005_coursecertificatepolicy_required_lessons.py \
  certificates/models.py \
  certificates/services.py \
  certificates/templates/admin/certificates/change_list.html \
  certificates/test_admin.py \
  certificates/test_profile_visibility.py \
  certificates/tests.py \
  certificates/urls.py \
  certificates/views.py \
  courses/test_course_cache.py \
  courses/views.py \
  progress/assignment_views.py \
  progress/migrations/0005_assignmentsubmissionattachment_and_more.py \
  progress/models.py \
  progress/services.py \
  progress/submission_files.py \
  progress/test_assignment_submissions.py \
  progress/test_enrollment_requests.py \
  progress/test_selection_maps.py \
  progress/tests.py \
  progress/urls.py \
  studio/presentation.py \
  studio/serializers.py \
  studio/test_assignment_reviews.py \
  studio/urls.py \
  studio/views.py \
  users/migrations/0002_user_certificate_name_and_more.py \
  users/models.py \
  certificates/pdf.py \
  certificates/test_pdf.py
```

### Группа2: `fix: isolate frontend sessions and stabilize learning and review UI`

21 файлов. Предлагаемый staging:

```bash
git add -- \
  frontend/src/api.js \
  frontend/src/components/LessonCourseSidebar.jsx \
  frontend/src/components/certificates/Certificates.jsx \
  frontend/src/components/certificates/certificates.css \
  frontend/src/components/learning/AssignmentSubmission.jsx \
  frontend/src/i18n/locales/en.json \
  frontend/src/i18n/locales/kk.json \
  frontend/src/i18n/locales/ru.json \
  frontend/src/pages/LessonView.css \
  frontend/src/pages/LessonView.jsx \
  frontend/src/pages/Profile.jsx \
  frontend/src/pages/instructor/Submissions.jsx \
  frontend/src/pages/instructor/instructor.css \
  frontend/src/utils/assignmentSubmissionDates.js \
  frontend/src/utils/instructorStudio.js \
  frontend/src/utils/lessons.js \
  frontend/tests/assignment-review.test.mjs \
  frontend/tests/assignment-submission.test.mjs \
  frontend/tests/certificates.test.mjs \
  frontend/tests/lesson-workspace.test.mjs \
  frontend/tests/session-isolation.test.mjs
```

### Группа3: `feat: preserve module 5 media integration and module 6 assessment sources`

18 файлов. Предлагаемый staging:

```bash
git add -- \
  courses/management/commands/import_media_module_5.py \
  courses/management/commands/import_media_module_6.py \
  courses/management/commands/integrate_lesson113_videos.py \
  courses/management/commands/integrate_lesson114_videos.py \
  courses/management/commands/integrate_lesson115_videos.py \
  courses/management/lesson113_quality_v2.json \
  courses/management/lesson114_quality_v2.json \
  courses/management/lesson115_final_video_integration.json \
  courses/management/media_module_5.json \
  courses/management/media_module_6.json \
  courses/test_lesson113_integration.py \
  courses/test_lesson114_integration.py \
  courses/test_lesson115_video_integration.py \
  courses/test_module6_import.py \
  docs/courses/lesson-113-integration-complete.md \
  docs/courses/lesson-113-quality-v2-integration-plan.md \
  docs/courses/lesson-114-integration-complete.md \
  docs/courses/media-module-5-assets.json
```

### Группа4: `feat: preserve reusable Remotion production sources for lessons 113 to 115`

176 файлов. Предлагаемый staging:

```bash
git add -- \
  .gitattributes \
  video-production/lesson-113-production/.gitignore \
  video-production/lesson-113-production/.prettierrc \
  video-production/lesson-113-production/AUDIO-PREVIEW.md \
  video-production/lesson-113-production/FINAL-AUDIO-MIX.md \
  video-production/lesson-113-production/PHASE-5H.md \
  video-production/lesson-113-production/QUALITY-V2.md \
  video-production/lesson-113-production/README.md \
  video-production/lesson-113-production/VALIDATION.md \
  video-production/lesson-113-production/content/provenance.json \
  video-production/lesson-113-production/content/quality-v2/lesson-113-readonly-snapshot.json \
  video-production/lesson-113-production/content/quality-v2/lesson-113-sync-proposal.json \
  video-production/lesson-113-production/content/quality-v2/lesson-113-video-integration.json \
  video-production/lesson-113-production/content/quality-v2/m5-l13-v1-source-organization-quality-v2.equivalent.ru.txt \
  video-production/lesson-113-production/content/quality-v2/m5-l13-v1-source-organization-quality-v2.transcript.ru.md \
  video-production/lesson-113-production/content/quality-v2/m5-l13-v2-project-import-quality-v2.equivalent.ru.txt \
  video-production/lesson-113-production/content/quality-v2/m5-l13-v2-project-import-quality-v2.transcript.ru.md \
  video-production/lesson-113-production/content/quality-v2/m5-l13-v3-timeline-reopen-quality-v2.equivalent.ru.txt \
  video-production/lesson-113-production/content/quality-v2/m5-l13-v3-timeline-reopen-quality-v2.transcript.ru.md \
  video-production/lesson-113-production/content/quality-v2/series.json \
  video-production/lesson-113-production/content/quality-v2/video-1.json \
  video-production/lesson-113-production/content/sfx-cues.json \
  video-production/lesson-113-production/content/sfx-provenance.json \
  video-production/lesson-113-production/content/videos.json \
  video-production/lesson-113-production/eslint.config.mjs \
  video-production/lesson-113-production/package-lock.json \
  video-production/lesson-113-production/package.json \
  video-production/lesson-113-production/public/f1/f1-notepad-diagram.svg \
  video-production/lesson-113-production/public/f1/f1-paper-diagram.svg \
  video-production/lesson-113-production/public/fonts/NOTO-LICENSE.txt \
  video-production/lesson-113-production/public/fonts/NotoSans-Bold.ttf \
  video-production/lesson-113-production/public/fonts/NotoSans-Regular.ttf \
  video-production/lesson-113-production/public/sfx/click.wav \
  video-production/lesson-113-production/public/sfx/complete.wav \
  video-production/lesson-113-production/public/sfx/drop.wav \
  video-production/lesson-113-production/public/sfx/pop.wav \
  video-production/lesson-113-production/public/sfx/whoosh.wav \
  video-production/lesson-113-production/remotion.config.ts \
  video-production/lesson-113-production/scripts/extract_frames.py \
  video-production/lesson-113-production/scripts/extract_phase5h_frames.py \
  video-production/lesson-113-production/scripts/mix_final_audio.py \
  video-production/lesson-113-production/scripts/phase5h_audio.py \
  video-production/lesson-113-production/scripts/prepare_music_preview.py \
  video-production/lesson-113-production/scripts/prepare_package.py \
  video-production/lesson-113-production/scripts/prepare_phase5h_integration.py \
  video-production/lesson-113-production/scripts/prepare_phase5h_plan.py \
  video-production/lesson-113-production/scripts/quality_v2_audio.py \
  video-production/lesson-113-production/scripts/render-package.mjs \
  video-production/lesson-113-production/scripts/render_phase5h.mjs \
  video-production/lesson-113-production/scripts/test_phase5h.py \
  video-production/lesson-113-production/scripts/verify_final_audio.py \
  video-production/lesson-113-production/scripts/verify_music_preview.py \
  video-production/lesson-113-production/scripts/verify_package.py \
  video-production/lesson-113-production/scripts/verify_phase5h.py \
  video-production/lesson-113-production/scripts/verify_quality_v2.py \
  video-production/lesson-113-production/src/Root.tsx \
  video-production/lesson-113-production/src/Tutorial.tsx \
  video-production/lesson-113-production/src/fonts.ts \
  video-production/lesson-113-production/src/index.ts \
  video-production/lesson-113-production/src/primitives.tsx \
  video-production/lesson-113-production/src/quality-v2/QualityVideo.tsx \
  video-production/lesson-113-production/src/quality-v2/SeriesWorkspace.tsx \
  video-production/lesson-113-production/src/quality-v2/index.tsx \
  video-production/lesson-113-production/src/quality-v2/lesson113-series.tsx \
  video-production/lesson-113-production/src/tokens.ts \
  video-production/lesson-113-production/src/types.ts \
  video-production/lesson-113-production/src/visuals.tsx \
  video-production/lesson-113-production/transcripts/m5-l13-v1-source-organization.ru.md \
  video-production/lesson-113-production/transcripts/m5-l13-v2-project-import.ru.md \
  video-production/lesson-113-production/transcripts/m5-l13-v3-timeline-reopen.ru.md \
  video-production/lesson-113-production/tsconfig.json \
  video-production/lesson-114-production/INTEGRATION-PLAN.md \
  video-production/lesson-114-production/LICENSE-SILERO.txt \
  video-production/lesson-114-production/README.md \
  video-production/lesson-114-production/content/final-assets.json \
  video-production/lesson-114-production/content/lesson114-readonly.json \
  video-production/lesson-114-production/content/lesson114-sync-proposal.json \
  video-production/lesson-114-production/content/m5-l14-v1-rough-cut-quality-v2.equivalent.ru.txt \
  video-production/lesson-114-production/content/m5-l14-v1-rough-cut-quality-v2.transcript.ru.md \
  video-production/lesson-114-production/content/m5-l14-v2-narration-balance-quality-v2.equivalent.ru.txt \
  video-production/lesson-114-production/content/m5-l14-v2-narration-balance-quality-v2.transcript.ru.md \
  video-production/lesson-114-production/content/m5-l14-v2-narration-balance-quality-v2.vtt \
  video-production/lesson-114-production/content/m5-l14-v3-caption-review-quality-v2.equivalent.ru.txt \
  video-production/lesson-114-production/content/m5-l14-v3-caption-review-quality-v2.transcript.ru.md \
  video-production/lesson-114-production/content/m5-l14-v3-caption-review-quality-v2.vtt \
  video-production/lesson-114-production/content/original-storyboards.json \
  video-production/lesson-114-production/content/series.json \
  video-production/lesson-114-production/content/speech.json \
  video-production/lesson-114-production/eslint.config.mjs \
  video-production/lesson-114-production/package-lock.json \
  video-production/lesson-114-production/package.json \
  video-production/lesson-114-production/public/f1/f1-notepad-diagram.svg \
  video-production/lesson-114-production/public/f1/f1-paper-diagram.svg \
  video-production/lesson-114-production/public/fonts/NOTO-LICENSE.txt \
  video-production/lesson-114-production/public/fonts/NotoSans-Bold.ttf \
  video-production/lesson-114-production/public/fonts/NotoSans-Regular.ttf \
  video-production/lesson-114-production/scripts/audio.py \
  video-production/lesson-114-production/scripts/frames.py \
  video-production/lesson-114-production/scripts/integration_plan.py \
  video-production/lesson-114-production/scripts/listen.sh \
  video-production/lesson-114-production/scripts/manifest.py \
  video-production/lesson-114-production/scripts/render.mjs \
  video-production/lesson-114-production/scripts/test_production.py \
  video-production/lesson-114-production/scripts/verify.py \
  video-production/lesson-114-production/src/Workspace.tsx \
  video-production/lesson-114-production/src/index.tsx \
  video-production/lesson-114-production/tsconfig.json \
  video-production/lesson-115-production/.gitignore \
  video-production/lesson-115-production/ASSET_REQUIREMENTS.md \
  video-production/lesson-115-production/AUDIO_SUBTITLE_WORKFLOW.md \
  video-production/lesson-115-production/FINAL_QA.md \
  video-production/lesson-115-production/PRODUCTION_READINESS.md \
  video-production/lesson-115-production/README.md \
  video-production/lesson-115-production/RECORDING_CHECKLIST.md \
  video-production/lesson-115-production/REMOTION_GRAPHICS.md \
  video-production/lesson-115-production/V1_PRODUCTION_QA.md \
  video-production/lesson-115-production/V2_V3_COMPARATIVE_QA.md \
  video-production/lesson-115-production/audio/LICENSE_CIS \
  video-production/lesson-115-production/content/audio-bgm-provenance.json \
  video-production/lesson-115-production/content/audio-mix-provenance.json \
  video-production/lesson-115-production/content/audio-sentence-mix-provenance.json \
  video-production/lesson-115-production/content/narration-provenance.json \
  video-production/lesson-115-production/content/narration-sentence-cues-provenance.json \
  video-production/lesson-115-production/content/timings-sentence.json \
  video-production/lesson-115-production/content/timings.json \
  video-production/lesson-115-production/content/videos.json \
  video-production/lesson-115-production/eslint.config.mjs \
  video-production/lesson-115-production/narration/m5-l15-v1-export-check.ru.md \
  video-production/lesson-115-production/narration/m5-l15-v2-vertical-adaptation.ru.md \
  video-production/lesson-115-production/narration/m5-l15-v3-final-review.ru.md \
  video-production/lesson-115-production/package.json \
  video-production/lesson-115-production/public/fonts/NOTO-LICENSE.txt \
  video-production/lesson-115-production/public/fonts/NotoSans-Bold.ttf \
  video-production/lesson-115-production/public/fonts/NotoSans-Regular.ttf \
  video-production/lesson-115-production/public/sfx/finish.wav \
  video-production/lesson-115-production/public/sfx/place.wav \
  video-production/lesson-115-production/public/sfx/select.wav \
  video-production/lesson-115-production/remotion.config.ts \
  video-production/lesson-115-production/scripts/extract_frames.py \
  video-production/lesson-115-production/scripts/generate_narration.py \
  video-production/lesson-115-production/scripts/generate_sentence_narration.py \
  video-production/lesson-115-production/scripts/mix_background_music.py \
  video-production/lesson-115-production/scripts/prepare_audio.py \
  video-production/lesson-115-production/scripts/render.mjs \
  video-production/lesson-115-production/scripts/test_background_music.py \
  video-production/lesson-115-production/scripts/test_content.py \
  video-production/lesson-115-production/src/Lesson115.tsx \
  video-production/lesson-115-production/src/Root.tsx \
  video-production/lesson-115-production/src/SceneVisual.tsx \
  video-production/lesson-115-production/src/fonts.ts \
  video-production/lesson-115-production/src/index.tsx \
  video-production/lesson-115-production/src/tokens.ts \
  video-production/lesson-115-production/storyboards/m5-l15-v1-export-check.storyboard.md \
  video-production/lesson-115-production/storyboards/m5-l15-v2-vertical-adaptation.storyboard.md \
  video-production/lesson-115-production/storyboards/m5-l15-v3-final-review.storyboard.md \
  video-production/lesson-115-production/tsconfig.json \
  video-production/module-5-style-test/.gitignore \
  video-production/module-5-style-test/.prettierrc \
  video-production/module-5-style-test/README.md \
  video-production/module-5-style-test/eslint.config.mjs \
  video-production/module-5-style-test/package-lock.json \
  video-production/module-5-style-test/package.json \
  video-production/module-5-style-test/public/fonts/NOTO-LICENSE.txt \
  video-production/module-5-style-test/public/fonts/NotoSans-Bold.ttf \
  video-production/module-5-style-test/public/fonts/NotoSans-Regular.ttf \
  video-production/module-5-style-test/remotion.config.ts \
  video-production/module-5-style-test/scripts/verify-output.mjs \
  video-production/module-5-style-test/src/Composition.tsx \
  video-production/module-5-style-test/src/Root.tsx \
  video-production/module-5-style-test/src/fonts.ts \
  video-production/module-5-style-test/src/index.ts \
  video-production/module-5-style-test/src/tokens.ts \
  video-production/module-5-style-test/tsconfig.json \
  video-production/lesson-115-production/package-lock.json \
  video-production/lesson-115-production/scripts/verify.py \
  video-production/lesson-115-production/scripts/test_verify.py
```

### Группа5: `docs: preserve project memory and assessment readiness reports`

27 файлов. Предлагаемый staging:

```bash
git add -- \
  AGENTS.md \
  docs/courses/certificates-read-only-p1g.md \
  docs/courses/missing-certificate-p1f.md \
  docs/courses/module-6-e2e-rehearsal.md \
  docs/courses/module-6-ui-readiness.md \
  docs/frontend-unslop-audit.md \
  docs/git-p1e-checkpoint-plan.md \
  docs/project-audit/01-technical-inventory.md \
  docs/project-audit/02-course-content-and-database-audit.md \
  docs/project-audit/03-media-and-production-audit.md \
  docs/project-audit/04-technical-quality-and-bug-audit.md \
  docs/project-memory/AGENTS_INTEGRATION_PROPOSAL.md \
  docs/project-memory/AI_INTEGRATIONS.md \
  docs/project-memory/ARCHITECTURE.md \
  docs/project-memory/CONTEXT_RESTORATION_TEST.md \
  docs/project-memory/COURSE_CONTENT_MAP.md \
  docs/project-memory/CURRENT_STATE.md \
  docs/project-memory/DATABASE_MAP.md \
  docs/project-memory/DECISIONS.md \
  docs/project-memory/FEATURE_FILE_MAP.md \
  docs/project-memory/MEDIA_PIPELINE.md \
  docs/project-memory/PROJECT_OVERVIEW.md \
  docs/project-memory/ROADMAP.md \
  docs/project-memory/TESTING_QA.md \
  video-production/module-6-production/README.md \
  docs/courses/certificate-pdf-p1i.md \
  docs/courses/checkpoint-readiness-p1k.md
```

Сам план уже включён ровно один раз в explicit список группы5; отдельная дополнительная команда не нужна. Все пять staging-команд приведены выше только для последующего разрешения.

## Полная классификация текущего working tree — P1H

A — backend runtime; B — migrations/backend tests; C — frontend source/tests; D — Course10 canonical/importers; E — integration sources; F — docs; G — Remotion source/assets; H — generated media/intermediates; I — DB/cache/local config; J — manual review/history/unknown.

`M` = tracked modification; `??` = untracked. «Архив/локально» означает исключить из предложенного staging, **не удалять**. Ignored files не входят в747 и описаны отдельно выше.

| Путь | Статус | Класс | Группа / решение |
|---|---|---|---|
| `.agents/skills/remotion-best-practices/SKILL.md` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/agents/openai.yaml` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/assets/remotion-icon.svg` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-captions/REFERENCE.md` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-captions/agents/openai.yaml` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-captions/assets/remotion-icon.svg` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-captions/display-captions.md` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-captions/import-srt-captions.md` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-captions/transcribe-captions.md` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-create/REFERENCE.md` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-create/agents/openai.yaml` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-create/assets/remotion-icon.svg` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-create/tailwind.md` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-create/video-layout.md` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-docs/REFERENCE.md` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-docs/agents/openai.yaml` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-docs/assets/remotion-icon.svg` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-interactivity/REFERENCE.md` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-interactivity/agents/openai.yaml` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-interactivity/assets/remotion-icon.svg` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-interactivity/inline-effects.md` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-interactivity/timeline-structure.md` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-license/REFERENCE.md` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-license/agents/openai.yaml` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-license/assets/remotion-icon.svg` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-maps/REFERENCE.md` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-maps/agents/openai.yaml` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-maps/assets/remotion-icon.svg` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-maps/techniques/cesium/TECHNIQUE.md` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-maps/techniques/cesium/assets/CesiumFlythrough.tsx` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-maps/techniques/cesium/assets/cesium-path.json` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-maps/techniques/cesium/assets/city-path.json` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-maps/techniques/cesium/assets/example-Root.tsx` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-maps/techniques/cesium/assets/flight-path.ts` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-maps/techniques/cesium/assets/sample-river.geojson` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-maps/techniques/cesium/references/3d-data-sources.md` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-maps/techniques/cesium/references/3d-flyover-architecture.md` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-maps/techniques/cesium/references/3d-troubleshooting.md` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-maps/techniques/cesium/scripts/prep-cesium-path.mjs` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-maps/techniques/mapbox/TECHNIQUE.md` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-maps/techniques/mapbox/references/render-stability.md` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-maps/techniques/maplibre/TECHNIQUE.md` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-maps/techniques/maplibre/references/render-stability.md` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-maps/techniques/maptiler/TECHNIQUE.md` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-maps/techniques/maptiler/assets/CountryLabel.tsx` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-maps/techniques/maptiler/assets/MapTilerVectorElement.ts` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-maps/techniques/maptiler/assets/RiverReveal.tsx` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-maps/techniques/maptiler/assets/example-Root.tsx` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-maps/techniques/maptiler/assets/sample-data/country-meta.json` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-maps/techniques/maptiler/assets/sample-data/yarlung-flow.json` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-maps/techniques/maptiler/assets/tokens.ts` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-maps/techniques/maptiler/references/map-data-sources.md` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-maps/techniques/maptiler/references/map-explainer-architecture.md` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-maps/techniques/maptiler/references/map-geo-prep.md` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-maps/techniques/maptiler/references/render-stability.md` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-maps/techniques/maptiler/scripts/prep-geo.mjs` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-maps/techniques/static-map/TECHNIQUE.md` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-markup/3d.md` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-markup/REFERENCE.md` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-markup/agents/openai.yaml` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-markup/arabic-text.md` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-markup/assets/remotion-icon.svg` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-markup/audio-visualization.md` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-markup/audio.md` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-markup/calculate-metadata.md` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-markup/color-correction.md` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-markup/compositions.md` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-markup/connected-compositions.md` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-markup/cropping.md` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-markup/effects.md` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-markup/embedding-videos.md` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-markup/ffmpeg.md` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-markup/gifs.md` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-markup/google-fonts.md` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-markup/html-in-canvas.md` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-markup/images.md` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-markup/light-leaks.md` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-markup/local-fonts.md` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-markup/lottie.md` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-markup/measuring-dom-nodes.md` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-markup/measuring-text.md` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-markup/motion-blur.md` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-markup/multi-scene-video.md` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-markup/parameters.md` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-markup/remotion-maps/REFERENCE.md` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-markup/remotion-maps/agents/openai.yaml` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-markup/remotion-maps/assets/remotion-icon.svg` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-markup/remotion-maps/techniques/cesium/TECHNIQUE.md` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-markup/remotion-maps/techniques/cesium/assets/CesiumFlythrough.tsx` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-markup/remotion-maps/techniques/cesium/assets/cesium-path.json` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-markup/remotion-maps/techniques/cesium/assets/city-path.json` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-markup/remotion-maps/techniques/cesium/assets/example-Root.tsx` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-markup/remotion-maps/techniques/cesium/assets/flight-path.ts` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-markup/remotion-maps/techniques/cesium/assets/sample-river.geojson` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-markup/remotion-maps/techniques/cesium/references/3d-data-sources.md` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-markup/remotion-maps/techniques/cesium/references/3d-flyover-architecture.md` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-markup/remotion-maps/techniques/cesium/references/3d-troubleshooting.md` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-markup/remotion-maps/techniques/cesium/scripts/prep-cesium-path.mjs` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-markup/remotion-maps/techniques/mapbox/TECHNIQUE.md` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-markup/remotion-maps/techniques/mapbox/references/render-stability.md` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-markup/remotion-maps/techniques/maplibre/TECHNIQUE.md` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-markup/remotion-maps/techniques/maplibre/references/render-stability.md` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-markup/remotion-maps/techniques/maptiler/TECHNIQUE.md` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-markup/remotion-maps/techniques/maptiler/assets/CountryLabel.tsx` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-markup/remotion-maps/techniques/maptiler/assets/MapTilerVectorElement.ts` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-markup/remotion-maps/techniques/maptiler/assets/RiverReveal.tsx` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-markup/remotion-maps/techniques/maptiler/assets/example-Root.tsx` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-markup/remotion-maps/techniques/maptiler/assets/sample-data/country-meta.json` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-markup/remotion-maps/techniques/maptiler/assets/sample-data/yarlung-flow.json` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-markup/remotion-maps/techniques/maptiler/assets/tokens.ts` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-markup/remotion-maps/techniques/maptiler/references/map-data-sources.md` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-markup/remotion-maps/techniques/maptiler/references/map-explainer-architecture.md` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-markup/remotion-maps/techniques/maptiler/references/map-geo-prep.md` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-markup/remotion-maps/techniques/maptiler/references/render-stability.md` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-markup/remotion-maps/techniques/maptiler/scripts/prep-geo.mjs` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-markup/remotion-maps/techniques/static-map/TECHNIQUE.md` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-markup/sequencing.md` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-markup/sfx.md` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-markup/silence-detection.md` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-markup/text-highlights.md` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-markup/timing-props.md` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-markup/timing.md` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-markup/transitions.md` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-markup/video-editing.md` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-markup/voiceover.md` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-multimedia/REFERENCE.md` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-multimedia/agents/openai.yaml` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-multimedia/assets/remotion-icon.svg` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-multimedia/get-audio-duration.md` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-multimedia/get-video-dimensions.md` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-multimedia/get-video-duration.md` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-render/REFERENCE.md` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-render/agents/openai.yaml` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-render/assets/remotion-icon.svg` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-render/transparent-videos.md` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-saas/REFERENCE.md` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-saas/agents/openai.yaml` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-saas/assets/remotion-icon.svg` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-saas/framework.md` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-saas/player.md` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-saas/rendering.md` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-studio/REFERENCE.md` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-studio/agents/openai.yaml` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-studio/assets/remotion-icon.svg` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-upgrade/REFERENCE.md` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-upgrade/agents/openai.yaml` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-best-practices/remotion-upgrade/assets/remotion-icon.svg` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-captions/SKILL.md` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-captions/agents/openai.yaml` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-captions/assets/remotion-icon.svg` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-captions/display-captions.md` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-captions/import-srt-captions.md` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-captions/transcribe-captions.md` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-create/SKILL.md` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-create/agents/openai.yaml` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-create/assets/remotion-icon.svg` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-create/tailwind.md` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-create/video-layout.md` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-render/SKILL.md` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-render/agents/openai.yaml` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-render/assets/remotion-icon.svg` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-render/transparent-videos.md` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-studio/SKILL.md` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-studio/agents/openai.yaml` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/remotion-studio/assets/remotion-icon.svg` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/unslop/SKILL.md` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/unslop/agents/openai.yaml` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/unslop/references/effects.md` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/unslop/references/refs.md` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/unslop/references/refs/beacon-engraving.webp` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/unslop/references/refs/meadow-3d.webp` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/unslop/references/refs/story-dashboard-frames.webp` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/unslop/references/refs/unslop-dashboard-after.webp` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/unslop/references/refs/unslop-hero-after.webp` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/unslop/references/signs.md` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/unslop/references/tokens.md` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/unslop/references/visuals.md` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/unslop/scripts/snapshot.mjs` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.agents/skills/unslop/scripts/story.mjs` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `.local-cinematic-qa/.gitignore` | ?? | I | Архив/локально — только локально; конфигурация/БД/QA/cache |
| `.local-video-test/cleanup-fixture.py` | ?? | I | Архив/локально — только локально; конфигурация/БД/QA/cache |
| `.local-video-test/cleanup-result.json` | ?? | I | Архив/локально — только локально; конфигурация/БД/QA/cache |
| `.local-video-test/prepare-fixture.py` | ?? | I | Архив/локально — только локально; конфигурация/БД/QA/cache |
| `.local-video-test/prepared-fixture.json` | ?? | I | Архив/локально — только локально; конфигурация/БД/QA/cache |
| `.local-video-test/sample.mp4` | ?? | I | Архив/локально — только локально; конфигурация/БД/QA/cache |
| `.vite/deps/_metadata.json` | ?? | I | Архив/локально — только локально; конфигурация/БД/QA/cache |
| `.vite/deps/axios.js` | ?? | I | Архив/локально — только локально; конфигурация/БД/QA/cache |
| `.vite/deps/axios.js.map` | ?? | I | Архив/локально — только локально; конфигурация/БД/QA/cache |
| `.vite/deps/i18next.js` | ?? | I | Архив/локально — только локально; конфигурация/БД/QA/cache |
| `.vite/deps/i18next.js.map` | ?? | I | Архив/локально — только локально; конфигурация/БД/QA/cache |
| `.vite/deps/lucide-react.js` | ?? | I | Архив/локально — только локально; конфигурация/БД/QA/cache |
| `.vite/deps/lucide-react.js.map` | ?? | I | Архив/локально — только локально; конфигурация/БД/QA/cache |
| `.vite/deps/motion_react.js` | ?? | I | Архив/локально — только локально; конфигурация/БД/QA/cache |
| `.vite/deps/motion_react.js.map` | ?? | I | Архив/локально — только локально; конфигурация/БД/QA/cache |
| `.vite/deps/package.json` | ?? | I | Архив/локально — только локально; конфигурация/БД/QA/cache |
| `.vite/deps/react-dom.js` | ?? | I | Архив/локально — только локально; конфигурация/БД/QA/cache |
| `.vite/deps/react-dom.js.map` | ?? | I | Архив/локально — только локально; конфигурация/БД/QA/cache |
| `.vite/deps/react-dom_client.js` | ?? | I | Архив/локально — только локально; конфигурация/БД/QA/cache |
| `.vite/deps/react-dom_client.js.map` | ?? | I | Архив/локально — только локально; конфигурация/БД/QA/cache |
| `.vite/deps/react-i18next.js` | ?? | I | Архив/локально — только локально; конфигурация/БД/QA/cache |
| `.vite/deps/react-i18next.js.map` | ?? | I | Архив/локально — только локально; конфигурация/БД/QA/cache |
| `.vite/deps/react-router-dom.js` | ?? | I | Архив/локально — только локально; конфигурация/БД/QA/cache |
| `.vite/deps/react-router-dom.js.map` | ?? | I | Архив/локально — только локально; конфигурация/БД/QA/cache |
| `.vite/deps/react.js` | ?? | I | Архив/локально — только локально; конфигурация/БД/QA/cache |
| `.vite/deps/react.js.map` | ?? | I | Архив/локально — только локально; конфигурация/БД/QA/cache |
| `.vite/deps/react_jsx-dev-runtime.js` | ?? | I | Архив/локально — только локально; конфигурация/БД/QA/cache |
| `.vite/deps/react_jsx-dev-runtime.js.map` | ?? | I | Архив/локально — только локально; конфигурация/БД/QA/cache |
| `.vite/deps/react_jsx-runtime.js` | ?? | I | Архив/локально — только локально; конфигурация/БД/QA/cache |
| `.vite/deps/react_jsx-runtime.js.map` | ?? | I | Архив/локально — только локально; конфигурация/БД/QA/cache |
| `.vite/deps/rolldown-runtime-DC62tzP2.js` | ?? | I | Архив/локально — только локально; конфигурация/БД/QA/cache |
| `AGENTS.md` | M | F | 5 — проектные инструкции |
| `backups/pre-migrations/db-before-migrations-20261111-091224.sqlite3` | ?? | I | Архив/локально — только локально; конфигурация/БД/QA/cache |
| `certificates/admin.py` | M | A | 1 — backend assignment/certificate/security functionality |
| `certificates/migrations/0005_coursecertificatepolicy_required_lessons.py` | ?? | B | 1 — backend regression/schema; обязательно сохранить |
| `certificates/models.py` | M | A | 1 — backend assignment/certificate/security functionality |
| `certificates/services.py` | M | A | 1 — backend assignment/certificate/security functionality |
| `certificates/templates/admin/certificates/change_list.html` | M | A | 1 — скрывает admin issuance action в disabled mode |
| `certificates/test_admin.py` | M | B | 1 — backend regression/schema; обязательно сохранить |
| `certificates/test_profile_visibility.py` | ?? | B | 1 — P1F/P1G owned/legacy/JWT/PDF/write-denial regressions |
| `certificates/tests.py` | M | B | 1 — backend regression/schema; обязательно сохранить |
| `certificates/urls.py` | M | A | 1 — backend assignment/certificate/security functionality |
| `certificates/views.py` | M | A | 1 — backend assignment/certificate/security functionality |
| `config/settings.py` | M | I | Архив/локально — только локально; конфигурация/БД/QA/cache |
| `course_assets/module_4/m4-audio-production.json` | ?? | J | Архив/локально — исторический Module4/кандидаты; вне текущего checkpoint, не удалять |
| `course_assets/module_4/m4-l1-f1-natural-narration.mp3` | ?? | J | Архив/локально — исторический Module4/кандидаты; вне текущего checkpoint, не удалять |
| `course_assets/module_4/m4-l1-f1-synthetic-narration.wav` | ?? | J | Архив/локально — исторический Module4/кандидаты; вне текущего checkpoint, не удалять |
| `course_assets/module_4/m4-l12-ru-roman-room-after-v2.wav` | ?? | J | Архив/локально — исторический Module4/кандидаты; вне текущего checkpoint, не удалять |
| `course_assets/module_4/m4-l12-ru-roman-room-before-v2.wav` | ?? | J | Архив/локально — исторический Module4/кандидаты; вне текущего checkpoint, не удалять |
| `course_assets/module_4/m4-l2-f1-corrected-transcript.txt` | ?? | J | Архив/локально — исторический Module4/кандидаты; вне текущего checkpoint, не удалять |
| `course_assets/module_4/m4-l2-f1-speech.wav` | ?? | J | Архив/локально — исторический Module4/кандидаты; вне текущего checkpoint, не удалять |
| `course_assets/module_4/m4-l2-f1-synchronized.srt` | ?? | J | Архив/локально — исторический Module4/кандидаты; вне текущего checkpoint, не удалять |
| `course_assets/module_4/m4-l3-f1-clean-reference.wav` | ?? | J | Архив/локально — исторический Module4/кандидаты; вне текущего checkpoint, не удалять |
| `course_assets/module_4/m4-l3-f1-original.wav` | ?? | J | Архив/локально — исторический Module4/кандидаты; вне текущего checkpoint, не удалять |
| `course_assets/module_4/m4-l3-f1-processed.wav` | ?? | J | Архив/локально — исторический Module4/кандидаты; вне текущего checkpoint, не удалять |
| `course_assets/module_4/m4-room-noise-v2.json` | ?? | J | Архив/локально — исторический Module4/кандидаты; вне текущего checkpoint, не удалять |
| `course_assets/module_4/voice_candidates/README.md` | ?? | J | Архив/локально — исторический Module4/кандидаты; вне текущего checkpoint, не удалять |
| `course_assets/module_4/voice_candidates/evaluation.json` | ?? | J | Архив/локально — исторический Module4/кандидаты; вне текущего checkpoint, не удалять |
| `course_assets/module_4/voice_candidates/generate_candidates.py` | ?? | J | Архив/локально — исторический Module4/кандидаты; вне текущего checkpoint, не удалять |
| `course_assets/module_4/voice_candidates/lesson12-self-contained-dsp/README.md` | ?? | J | Архив/локально — исторический Module4/кандидаты; вне текущего checkpoint, не удалять |
| `course_assets/module_4/voice_candidates/lesson12-self-contained-dsp/demonstration.json` | ?? | J | Архив/локально — исторический Module4/кандидаты; вне текущего checkpoint, не удалять |
| `course_assets/module_4/voice_candidates/lesson12-self-contained-dsp/lesson12-room-after-dsp.wav` | ?? | J | Архив/локально — исторический Module4/кандидаты; вне текущего checkpoint, не удалять |
| `course_assets/module_4/voice_candidates/lesson12-self-contained-dsp/lesson12-room-before.wav` | ?? | J | Архив/локально — исторический Module4/кандидаты; вне текущего checkpoint, не удалять |
| `course_assets/module_4/voice_candidates/prepare_filter_v3.py` | ?? | J | Архив/локально — исторический Module4/кандидаты; вне текущего checkpoint, не удалять |
| `course_assets/module_4/voice_candidates/prepare_room_noise_v2.py` | ?? | J | Архив/локально — исторический Module4/кандидаты; вне текущего checkpoint, не удалять |
| `course_assets/module_4/voice_candidates/prepare_self_contained_dsp.py` | ?? | J | Архив/локально — исторический Module4/кандидаты; вне текущего checkpoint, не удалять |
| `course_assets/module_4/voice_candidates/requirements-evaluation.txt` | ?? | J | Архив/локально — исторический Module4/кандидаты; вне текущего checkpoint, не удалять |
| `course_assets/module_4/voice_candidates/ru_roman_refined/README.md` | ?? | J | Архив/локально — исторический Module4/кандидаты; вне текущего checkpoint, не удалять |
| `course_assets/module_4/voice_candidates/ru_roman_refined/m4-l10-ru-roman-tts-candidate.wav` | ?? | J | Архив/локально — исторический Module4/кандидаты; вне текущего checkpoint, не удалять |
| `course_assets/module_4/voice_candidates/ru_roman_refined/m4-l11-ru-roman-speech-candidate.wav` | ?? | J | Архив/локально — исторический Module4/кандидаты; вне текущего checkpoint, не удалять |
| `course_assets/module_4/voice_candidates/ru_roman_refined/m4-l11-ru-roman-synchronized-candidate.srt` | ?? | J | Архив/локально — исторический Module4/кандидаты; вне текущего checkpoint, не удалять |
| `course_assets/module_4/voice_candidates/ru_roman_refined/m4-l11-ru-roman-transcript.txt` | ?? | J | Архив/локально — исторический Module4/кандидаты; вне текущего checkpoint, не удалять |
| `course_assets/module_4/voice_candidates/ru_roman_refined/m4-l12-filter-balanced-v3.wav` | ?? | J | Архив/локально — исторический Module4/кандидаты; вне текущего checkpoint, не удалять |
| `course_assets/module_4/voice_candidates/ru_roman_refined/m4-l12-filter-gentle-v3.wav` | ?? | J | Архив/локально — исторический Module4/кандидаты; вне текущего checkpoint, не удалять |
| `course_assets/module_4/voice_candidates/ru_roman_refined/m4-l12-filter-strong-v3.wav` | ?? | J | Архив/локально — исторический Module4/кандидаты; вне текущего checkpoint, не удалять |
| `course_assets/module_4/voice_candidates/ru_roman_refined/m4-l12-filter-v3-notes.md` | ?? | J | Архив/локально — исторический Module4/кандидаты; вне текущего checkpoint, не удалять |
| `course_assets/module_4/voice_candidates/ru_roman_refined/m4-l12-filter-v3-report.json` | ?? | J | Архив/локально — исторический Module4/кандидаты; вне текущего checkpoint, не удалять |
| `course_assets/module_4/voice_candidates/ru_roman_refined/m4-l12-ru-roman-clean-candidate.wav` | ?? | J | Архив/локально — исторический Module4/кандидаты; вне текущего checkpoint, не удалять |
| `course_assets/module_4/voice_candidates/ru_roman_refined/m4-l12-ru-roman-filtered-candidate.wav` | ?? | J | Архив/локально — исторический Module4/кандидаты; вне текущего checkpoint, не удалять |
| `course_assets/module_4/voice_candidates/ru_roman_refined/m4-l12-ru-roman-noisy-candidate.wav` | ?? | J | Архив/локально — исторический Module4/кандидаты; вне текущего checkpoint, не удалять |
| `course_assets/module_4/voice_candidates/ru_roman_refined/production-candidates.json` | ?? | J | Архив/локально — исторический Module4/кандидаты; вне текущего checkpoint, не удалять |
| `course_assets/module_4/voice_candidates/ru_roman_refined/ru-roman-variant-a-neutral.wav` | ?? | J | Архив/локально — исторический Module4/кандидаты; вне текущего checkpoint, не удалять |
| `course_assets/module_4/voice_candidates/ru_roman_refined/ru-roman-variant-b-clear-pauses.wav` | ?? | J | Архив/локально — исторический Module4/кандидаты; вне текущего checkpoint, не удалять |
| `course_assets/module_4/voice_candidates/test_candidates.py` | ?? | J | Архив/локально — исторический Module4/кандидаты; вне текущего checkpoint, не удалять |
| `course_assets/module_4/voice_candidates/test_filter_v3.py` | ?? | J | Архив/локально — исторический Module4/кандидаты; вне текущего checkpoint, не удалять |
| `course_assets/module_4/voice_candidates/test_roman_module4.py` | ?? | J | Архив/локально — исторический Module4/кандидаты; вне текущего checkpoint, не удалять |
| `course_assets/module_4/voice_candidates/test_room_noise_v2.py` | ?? | J | Архив/локально — исторический Module4/кандидаты; вне текущего checkpoint, не удалять |
| `course_assets/module_4/voice_candidates/test_self_contained_dsp.py` | ?? | J | Архив/локально — исторический Module4/кандидаты; вне текущего checkpoint, не удалять |
| `course_assets/module_4/voice_candidates/v5_cis_base_nostress-ru_marat.wav` | ?? | J | Архив/локально — исторический Module4/кандидаты; вне текущего checkpoint, не удалять |
| `course_assets/module_4/voice_candidates/v5_cis_base_nostress-ru_roman.wav` | ?? | J | Архив/локально — исторический Module4/кандидаты; вне текущего checkpoint, не удалять |
| `course_assets/module_4/voice_candidates/v5_cis_base_nostress-ru_zhadyra.wav` | ?? | J | Архив/локально — исторический Module4/кандидаты; вне текущего checkpoint, не удалять |
| `course_assets/module_5/m5-l13-v1-production/narration-preview.wav` | ?? | J | Архив/локально — исторический Module4/кандидаты; вне текущего checkpoint, не удалять |
| `courses/management/commands/import_media_module_5.py` | M | D | 3 — канонический Module5/6 source + importer |
| `courses/management/commands/import_media_module_6.py` | ?? | D | 3 — канонический Module5/6 source + importer |
| `courses/management/commands/integrate_lesson113_videos.py` | ?? | E | 3 — create-only integration command + pinned plan |
| `courses/management/commands/integrate_lesson114_videos.py` | ?? | E | 3 — create-only integration command + pinned plan |
| `courses/management/commands/integrate_lesson115_videos.py` | ?? | E | 3 — create-only integration command + pinned plan |
| `courses/management/lesson113_quality_v2.json` | ?? | E | 3 — create-only integration command + pinned plan |
| `courses/management/lesson114_quality_v2.json` | ?? | E | 3 — create-only integration command + pinned plan |
| `courses/management/lesson115_final_video_integration.json` | ?? | E | 3 — create-only integration command + pinned plan |
| `courses/management/media_module_5.json` | M | D | 3 — канонический Module5/6 source + importer |
| `courses/management/media_module_6.json` | ?? | D | 3 — канонический Module5/6 source + importer |
| `courses/test_course_cache.py` | ?? | B | 1 — backend regression/schema; обязательно сохранить |
| `courses/test_lesson113_integration.py` | ?? | B | 3 — regression tests интеграции/import |
| `courses/test_lesson114_integration.py` | ?? | B | 3 — regression tests интеграции/import |
| `courses/test_lesson115_video_integration.py` | ?? | B | 3 — regression tests интеграции/import |
| `courses/test_module4_audio.py` | ?? | J | Архив/локально — исторический Module4/кандидаты; вне текущего checkpoint, не удалять |
| `courses/test_module6_import.py` | ?? | B | 3 — regression tests интеграции/import |
| `courses/views.py` | M | A | 1 — backend assignment/certificate/security functionality |
| `docs/courses/certificates-read-only-p1g.md` | ?? | F | 5 — актуальная read/write матрица и ограничения |
| `docs/courses/lesson-113-integration-complete.md` | ?? | E | 3 — план/отчёт интеграции Module5 |
| `docs/courses/lesson-113-quality-v2-integration-plan.md` | ?? | E | 3 — план/отчёт интеграции Module5 |
| `docs/courses/lesson-114-integration-complete.md` | ?? | E | 3 — план/отчёт интеграции Module5 |
| `docs/courses/media-module-4-legacy-assets.json` | ?? | J | Архив/локально — исторический Module4/кандидаты; вне текущего checkpoint, не удалять |
| `docs/courses/media-module-5-assets.json` | M | E | 3 — план/отчёт интеграции Module5 |
| `docs/courses/missing-certificate-p1f.md` | ?? | F | 5 — P1F diagnosis/backup evidence; исторический этап |
| `docs/courses/module-4-audio-demonstrations.md` | ?? | J | Архив/локально — исторический Module4/кандидаты; вне текущего checkpoint, не удалять |
| `docs/courses/module-4-cleanup-inventory.json` | ?? | J | Архив/локально — исторический Module4/кандидаты; вне текущего checkpoint, не удалять |
| `docs/courses/module-4-elevenlabs-provenance.json` | ?? | J | Архив/локально — исторический Module4/кандидаты; вне текущего checkpoint, не удалять |
| `docs/courses/module-4-rnnoise-COPYING.txt` | ?? | J | Архив/локально — исторический Module4/кандидаты; вне текущего checkpoint, не удалять |
| `docs/courses/module-4-rnnoise-license-audit.json` | ?? | J | Архив/локально — исторический Module4/кандидаты; вне текущего checkpoint, не удалять |
| `docs/courses/module-6-e2e-rehearsal.md` | ?? | F | 5 — документация; датированные снимки, не актуальный runtime-контракт |
| `docs/courses/module-6-ui-readiness.md` | ?? | F | 5 — документация; датированные снимки, не актуальный runtime-контракт |
| `docs/frontend-unslop-audit.md` | ?? | F | 5 — документация; датированные снимки, не актуальный runtime-контракт |
| `docs/git-p1e-checkpoint-plan.md` | ?? | F | 5 — P1H allowlist и команды; сам план |
| `docs/project-audit/01-technical-inventory.md` | ?? | F | 5 — документация; датированные снимки, не актуальный runtime-контракт |
| `docs/project-audit/02-course-content-and-database-audit.md` | ?? | F | 5 — документация; датированные снимки, не актуальный runtime-контракт |
| `docs/project-audit/03-media-and-production-audit.md` | ?? | F | 5 — документация; датированные снимки, не актуальный runtime-контракт |
| `docs/project-audit/04-technical-quality-and-bug-audit.md` | ?? | F | 5 — документация; датированные снимки, не актуальный runtime-контракт |
| `docs/project-memory/AGENTS_INTEGRATION_PROPOSAL.md` | ?? | F | 5 — документация; датированные снимки, не актуальный runtime-контракт |
| `docs/project-memory/AI_INTEGRATIONS.md` | ?? | F | 5 — документация; датированные снимки, не актуальный runtime-контракт |
| `docs/project-memory/ARCHITECTURE.md` | ?? | F | 5 — документация; датированные снимки, не актуальный runtime-контракт |
| `docs/project-memory/CONTEXT_RESTORATION_TEST.md` | ?? | F | 5 — документация; датированные снимки, не актуальный runtime-контракт |
| `docs/project-memory/COURSE_CONTENT_MAP.md` | ?? | F | 5 — документация; датированные снимки, не актуальный runtime-контракт |
| `docs/project-memory/CURRENT_STATE.md` | ?? | F | 5 — документация; датированные снимки, не актуальный runtime-контракт |
| `docs/project-memory/DATABASE_MAP.md` | ?? | F | 5 — документация; датированные снимки, не актуальный runtime-контракт |
| `docs/project-memory/DECISIONS.md` | ?? | F | 5 — документация; датированные снимки, не актуальный runtime-контракт |
| `docs/project-memory/FEATURE_FILE_MAP.md` | ?? | F | 5 — документация; датированные снимки, не актуальный runtime-контракт |
| `docs/project-memory/MEDIA_PIPELINE.md` | ?? | F | 5 — документация; датированные снимки, не актуальный runtime-контракт |
| `docs/project-memory/PROJECT_OVERVIEW.md` | ?? | F | 5 — документация; датированные снимки, не актуальный runtime-контракт |
| `docs/project-memory/ROADMAP.md` | ?? | F | 5 — документация; датированные снимки, не актуальный runtime-контракт |
| `docs/project-memory/TESTING_QA.md` | ?? | F | 5 — документация; датированные снимки, не актуальный runtime-контракт |
| `e modules 2-4 and inline learning media"` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `frontend/src/api.js` | M | C | 2 — frontend P0–P1D и assignment/certificate UI; сохранить совместно |
| `frontend/src/components/LessonCourseSidebar.jsx` | M | C | 2 — frontend P0–P1D и assignment/certificate UI; сохранить совместно |
| `frontend/src/components/certificates/Certificates.jsx` | M | C | 2 — frontend P0–P1D и assignment/certificate UI; сохранить совместно |
| `frontend/src/components/certificates/certificates.css` | M | C | 2 — frontend P0–P1D и assignment/certificate UI; сохранить совместно |
| `frontend/src/components/learning/AssignmentSubmission.jsx` | ?? | C | 2 — frontend P0–P1D и assignment/certificate UI; сохранить совместно |
| `frontend/src/i18n/locales/en.json` | M | C | 2 — frontend P0–P1D и assignment/certificate UI; сохранить совместно |
| `frontend/src/i18n/locales/kk.json` | M | C | 2 — frontend P0–P1D и assignment/certificate UI; сохранить совместно |
| `frontend/src/i18n/locales/ru.json` | M | C | 2 — frontend P0–P1D и assignment/certificate UI; сохранить совместно |
| `frontend/src/pages/LessonView.css` | M | C | 2 — frontend P0–P1D и assignment/certificate UI; сохранить совместно |
| `frontend/src/pages/LessonView.jsx` | M | C | 2 — frontend P0–P1D и assignment/certificate UI; сохранить совместно |
| `frontend/src/pages/Profile.jsx` | M | C | 2 — frontend P0–P1D и assignment/certificate UI; сохранить совместно |
| `frontend/src/pages/instructor/Submissions.jsx` | M | C | 2 — frontend P0–P1D и assignment/certificate UI; сохранить совместно |
| `frontend/src/pages/instructor/instructor.css` | M | C | 2 — frontend P0–P1D и assignment/certificate UI; сохранить совместно |
| `frontend/src/utils/assignmentSubmissionDates.js` | ?? | C | 2 — frontend P0–P1D и assignment/certificate UI; сохранить совместно |
| `frontend/src/utils/instructorStudio.js` | M | C | 2 — frontend P0–P1D и assignment/certificate UI; сохранить совместно |
| `frontend/src/utils/lessons.js` | M | C | 2 — frontend P0–P1D и assignment/certificate UI; сохранить совместно |
| `frontend/tests/assignment-review.test.mjs` | M | C | 2 — frontend P0–P1D и assignment/certificate UI; сохранить совместно |
| `frontend/tests/assignment-submission.test.mjs` | ?? | C | 2 — frontend P0–P1D и assignment/certificate UI; сохранить совместно |
| `frontend/tests/certificates.test.mjs` | M | C | 2 — frontend P0–P1D и assignment/certificate UI; сохранить совместно |
| `frontend/tests/lesson-workspace.test.mjs` | M | C | 2 — frontend P0–P1D и assignment/certificate UI; сохранить совместно |
| `frontend/tests/session-isolation.test.mjs` | M | C | 2 — frontend P0–P1D и assignment/certificate UI; сохранить совместно |
| `progress/assignment_views.py` | ?? | A | 1 — backend assignment/certificate/security functionality |
| `progress/migrations/0005_assignmentsubmissionattachment_and_more.py` | ?? | B | 1 — backend regression/schema; обязательно сохранить |
| `progress/models.py` | M | A | 1 — backend assignment/certificate/security functionality |
| `progress/services.py` | M | A | 1 — backend assignment/certificate/security functionality |
| `progress/submission_files.py` | ?? | A | 1 — backend assignment/certificate/security functionality |
| `progress/test_assignment_submissions.py` | ?? | B | 1 — backend regression/schema; обязательно сохранить |
| `progress/test_enrollment_requests.py` | M | B | 1 — backend regression/schema; обязательно сохранить |
| `progress/test_selection_maps.py` | M | B | 1 — backend regression/schema; обязательно сохранить |
| `progress/tests.py` | M | B | 1 — backend regression/schema; обязательно сохранить |
| `progress/urls.py` | M | A | 1 — backend assignment/certificate/security functionality |
| `scripts/generate_module_4_audio.py` | ?? | J | Архив/локально — исторический Module4/кандидаты; вне текущего checkpoint, не удалять |
| `skills-lock.json` | ?? | J | Архив/локально — сохранить; отдельное решение владельца, не приложение |
| `studio/presentation.py` | M | A | 1 — backend assignment/certificate/security functionality |
| `studio/serializers.py` | M | A | 1 — backend assignment/certificate/security functionality |
| `studio/test_assignment_reviews.py` | M | B | 1 — backend regression/schema; обязательно сохранить |
| `studio/urls.py` | M | A | 1 — backend assignment/certificate/security functionality |
| `studio/views.py` | M | A | 1 — backend assignment/certificate/security functionality |
| `users/migrations/0002_user_certificate_name_and_more.py` | ?? | B | 1 — backend regression/schema; обязательно сохранить |
| `users/models.py` | M | A | 1 — backend assignment/certificate/security functionality |
| `video-production/lesson-113-production/.gitignore` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-113-production/.prettierrc` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-113-production/AUDIO-PREVIEW.md` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-113-production/FINAL-AUDIO-MIX.md` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-113-production/PHASE-5H.md` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-113-production/QUALITY-V2.md` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-113-production/README.md` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-113-production/VALIDATION.md` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-113-production/content/provenance.json` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-113-production/content/quality-v2/lesson-113-readonly-snapshot.json` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-113-production/content/quality-v2/lesson-113-sync-proposal.json` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-113-production/content/quality-v2/lesson-113-video-integration.json` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-113-production/content/quality-v2/m5-l13-v1-source-organization-quality-v2.equivalent.ru.txt` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-113-production/content/quality-v2/m5-l13-v1-source-organization-quality-v2.transcript.ru.md` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-113-production/content/quality-v2/m5-l13-v2-project-import-quality-v2.equivalent.ru.txt` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-113-production/content/quality-v2/m5-l13-v2-project-import-quality-v2.transcript.ru.md` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-113-production/content/quality-v2/m5-l13-v3-timeline-reopen-quality-v2.equivalent.ru.txt` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-113-production/content/quality-v2/m5-l13-v3-timeline-reopen-quality-v2.transcript.ru.md` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-113-production/content/quality-v2/series.json` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-113-production/content/quality-v2/video-1.json` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-113-production/content/sfx-cues.json` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-113-production/content/sfx-provenance.json` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-113-production/content/videos.json` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-113-production/eslint.config.mjs` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-113-production/package-lock.json` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-113-production/package.json` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-113-production/public/f1/f1-notepad-diagram.svg` | ?? | G | 4 — малый source asset; вместе с лицензией/провенансом |
| `video-production/lesson-113-production/public/f1/f1-paper-diagram.svg` | ?? | G | 4 — малый source asset; вместе с лицензией/провенансом |
| `video-production/lesson-113-production/public/fonts/NOTO-LICENSE.txt` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-113-production/public/fonts/NotoSans-Bold.ttf` | ?? | G | 4 — малый source asset; вместе с лицензией/провенансом |
| `video-production/lesson-113-production/public/fonts/NotoSans-Regular.ttf` | ?? | G | 4 — малый source asset; вместе с лицензией/провенансом |
| `video-production/lesson-113-production/public/sfx/click.wav` | ?? | G | 4 — малый source asset; вместе с лицензией/провенансом |
| `video-production/lesson-113-production/public/sfx/complete.wav` | ?? | G | 4 — малый source asset; вместе с лицензией/провенансом |
| `video-production/lesson-113-production/public/sfx/drop.wav` | ?? | G | 4 — малый source asset; вместе с лицензией/провенансом |
| `video-production/lesson-113-production/public/sfx/pop.wav` | ?? | G | 4 — малый source asset; вместе с лицензией/провенансом |
| `video-production/lesson-113-production/public/sfx/whoosh.wav` | ?? | G | 4 — малый source asset; вместе с лицензией/провенансом |
| `video-production/lesson-113-production/remotion.config.ts` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-113-production/scripts/extract_frames.py` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-113-production/scripts/extract_phase5h_frames.py` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-113-production/scripts/mix_final_audio.py` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-113-production/scripts/phase5h_audio.py` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-113-production/scripts/prepare_music_preview.py` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-113-production/scripts/prepare_package.py` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-113-production/scripts/prepare_phase5h_integration.py` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-113-production/scripts/prepare_phase5h_plan.py` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-113-production/scripts/quality_v2_audio.py` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-113-production/scripts/render-package.mjs` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-113-production/scripts/render_phase5h.mjs` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-113-production/scripts/test_phase5h.py` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-113-production/scripts/verify_final_audio.py` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-113-production/scripts/verify_music_preview.py` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-113-production/scripts/verify_package.py` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-113-production/scripts/verify_phase5h.py` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-113-production/scripts/verify_quality_v2.py` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-113-production/src/Root.tsx` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-113-production/src/Tutorial.tsx` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-113-production/src/fonts.ts` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-113-production/src/index.ts` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-113-production/src/primitives.tsx` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-113-production/src/quality-v2/QualityVideo.tsx` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-113-production/src/quality-v2/SeriesWorkspace.tsx` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-113-production/src/quality-v2/index.tsx` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-113-production/src/quality-v2/lesson113-series.tsx` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-113-production/src/tokens.ts` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-113-production/src/types.ts` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-113-production/src/visuals.tsx` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-113-production/transcripts/m5-l13-v1-source-organization.ru.md` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-113-production/transcripts/m5-l13-v2-project-import.ru.md` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-113-production/transcripts/m5-l13-v3-timeline-reopen.ru.md` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-113-production/tsconfig.json` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-114-production/INTEGRATION-PLAN.md` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-114-production/LICENSE-SILERO.txt` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-114-production/README.md` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-114-production/content/final-assets.json` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-114-production/content/lesson114-readonly.json` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-114-production/content/lesson114-sync-proposal.json` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-114-production/content/m5-l14-v1-rough-cut-quality-v2.equivalent.ru.txt` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-114-production/content/m5-l14-v1-rough-cut-quality-v2.transcript.ru.md` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-114-production/content/m5-l14-v2-narration-balance-quality-v2.equivalent.ru.txt` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-114-production/content/m5-l14-v2-narration-balance-quality-v2.transcript.ru.md` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-114-production/content/m5-l14-v2-narration-balance-quality-v2.vtt` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-114-production/content/m5-l14-v3-caption-review-quality-v2.equivalent.ru.txt` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-114-production/content/m5-l14-v3-caption-review-quality-v2.transcript.ru.md` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-114-production/content/m5-l14-v3-caption-review-quality-v2.vtt` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-114-production/content/original-storyboards.json` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-114-production/content/series.json` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-114-production/content/speech.json` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-114-production/eslint.config.mjs` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-114-production/node_modules` | ?? | I | Архив/локально — symlink на локальную установку зависимостей; не staging |
| `video-production/lesson-114-production/out/final/m5-l14-v1-rough-cut-quality-v2-visual.mp4` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/final/m5-l14-v1-rough-cut-quality-v2.mp4` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/final/m5-l14-v2-narration-balance-quality-v2-visual.mp4` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/final/m5-l14-v2-narration-balance-quality-v2.mp4` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/final/m5-l14-v3-caption-review-quality-v2-visual.mp4` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/final/m5-l14-v3-caption-review-quality-v2.mp4` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/m5-l14-v1-rough-cut-quality-v2-audio.json` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/m5-l14-v1-rough-cut-quality-v2-filtered.wav` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/m5-l14-v1-rough-cut-quality-v2-mix.wav` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/m5-l14-v1-rough-cut-quality-v2-music.wav` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/m5-l14-v1-rough-cut-quality-v2-sfx.wav` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/m5-l14-v1-rough-cut-quality-v2-speech.wav` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/m5-l14-v2-narration-balance-quality-v2-audio.json` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/m5-l14-v2-narration-balance-quality-v2-filtered.wav` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/m5-l14-v2-narration-balance-quality-v2-mix.wav` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/m5-l14-v2-narration-balance-quality-v2-music.wav` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/m5-l14-v2-narration-balance-quality-v2-sfx.wav` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/m5-l14-v2-narration-balance-quality-v2-speech.wav` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/m5-l14-v3-caption-review-quality-v2-audio.json` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/m5-l14-v3-caption-review-quality-v2-filtered.wav` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/m5-l14-v3-caption-review-quality-v2-mix.wav` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/m5-l14-v3-caption-review-quality-v2-music.wav` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/m5-l14-v3-caption-review-quality-v2-sfx.wav` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/m5-l14-v3-caption-review-quality-v2-speech.wav` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/previews/m5-l14-v1-rough-cut-quality-v2-visual.mp4` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/previews/m5-l14-v1-rough-cut-quality-v2.mp4` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/previews/m5-l14-v2-narration-balance-quality-v2-visual.mp4` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/previews/m5-l14-v2-narration-balance-quality-v2.mp4` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/previews/m5-l14-v3-caption-review-quality-v2-visual.mp4` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/previews/m5-l14-v3-caption-review-quality-v2.mp4` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/aac192-before-final-validation/final/m5-l14-v1-rough-cut-quality-v2.mp4` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/aac192-before-final-validation/final/m5-l14-v2-narration-balance-quality-v2.mp4` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/aac192-before-final-validation/final/m5-l14-v3-caption-review-quality-v2.mp4` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/aac192-before-final-validation/previews/m5-l14-v1-rough-cut-quality-v2.mp4` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/aac192-before-final-validation/previews/m5-l14-v2-narration-balance-quality-v2.mp4` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/aac192-before-final-validation/previews/m5-l14-v3-caption-review-quality-v2.mp4` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/aac192-diagnostic.json` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/aac320-diagnostic.json` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/aac320-remux.json` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/aac320-remux.log` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/ab-stem-verification.json` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/audio-ab-prepare.log` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/audio-before-ab-match/m5-l14-v2-narration-balance-quality-v2-audio.json` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/audio-before-ab-match/m5-l14-v2-narration-balance-quality-v2-filtered.wav` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/audio-before-ab-match/m5-l14-v2-narration-balance-quality-v2-mix.wav` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/audio-before-ab-match/m5-l14-v2-narration-balance-quality-v2-music.wav` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/audio-before-ab-match/m5-l14-v2-narration-balance-quality-v2-sfx.wav` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/audio-before-ab-match/m5-l14-v2-narration-balance-quality-v2-speech.wav` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/audio-prepare.log` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/browser/audit.cjs` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/browser/caption-review-1.png` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/browser/caption-review-2.png` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/browser/caption-review-3.png` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/browser/caption-review-4.png` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/browser/caption-review-5.png` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/browser/caption-review-6.png` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/browser/caption-review-7.png` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/browser/captions-fixed-1.png` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/browser/captions-fixed-2.png` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/browser/final-playback-report.json` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/browser/focused-report.json` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/browser/focused.cjs` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/browser/narration-balance-1.png` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/browser/narration-balance-2.png` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/browser/narration-balance-3.png` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/browser/narration-balance-4.png` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/browser/narration-balance-5.png` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/browser/narration-balance-6.png` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/browser/narration-balance-7.png` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/browser/playback-m5-l14-v1-rough-cut-quality-v2-begin.png` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/browser/playback-m5-l14-v1-rough-cut-quality-v2-end.png` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/browser/playback-m5-l14-v1-rough-cut-quality-v2-middle.png` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/browser/playback-m5-l14-v2-narration-balance-quality-v2-begin.png` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/browser/playback-m5-l14-v2-narration-balance-quality-v2-end.png` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/browser/playback-m5-l14-v2-narration-balance-quality-v2-middle.png` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/browser/playback-m5-l14-v3-caption-review-quality-v2-begin.png` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/browser/playback-m5-l14-v3-caption-review-quality-v2-end.png` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/browser/playback-m5-l14-v3-caption-review-quality-v2-middle.png` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/browser/playback.cjs` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/browser/pre-encoding-playback-report.json` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/browser/reference-studio.png` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/browser/report.json` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/browser/rough-cut-1.png` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/browser/rough-cut-2.png` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/browser/rough-cut-3.png` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/browser/rough-cut-4.png` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/browser/rough-cut-5.png` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/browser/rough-cut-6.png` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/browser/rough-cut-7.png` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/browser/rough-fixed-1.png` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/browser/rough-fixed-2.png` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/browser/selection-fixed-1.png` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/browser/selection-report.json` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/browser/selection.cjs` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/caption-audio-before-cue-fix/m5-l14-v3-caption-review-quality-v2-audio.json` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/caption-audio-before-cue-fix/m5-l14-v3-caption-review-quality-v2-filtered.wav` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/caption-audio-before-cue-fix/m5-l14-v3-caption-review-quality-v2-mix.wav` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/caption-audio-before-cue-fix/m5-l14-v3-caption-review-quality-v2-music.wav` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/caption-audio-before-cue-fix/m5-l14-v3-caption-review-quality-v2-sfx.wav` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/caption-audio-before-cue-fix/m5-l14-v3-caption-review-quality-v2-speech.wav` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/caption-audio-before-cue-fix/m5-l14-v3-caption-review-quality-v2.mp4` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/caption-audio-cue-fix.log` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/course-media-validation-before320.json` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/course-media-validation.json` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/final-batch.log` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/final-caption-review-inputs.json` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/final-caption-review-mux.log` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/final-caption-review-render.log` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/final-frame-extraction.log` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/final-narration-balance-inputs.json` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/final-narration-balance-mux.log` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/final-narration-balance-render.log` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/final-rough-cut-inputs.json` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/final-rough-cut-mux.log` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/final-rough-cut-render.log` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/finish-pipeline.log` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/format.log` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/frame-extraction.log` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/frame-review.json` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/frames-final.json` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/frames-final/caption-review/scene-01.png` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/frames-final/caption-review/scene-02.png` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/frames-final/caption-review/scene-03.png` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/frames-final/caption-review/scene-04.png` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/frames-final/caption-review/scene-05.png` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/frames-final/caption-review/scene-06.png` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/frames-final/caption-review/scene-07.png` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/frames-final/caption-review/transitions.png` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/frames-final/narration-balance/scene-01.png` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/frames-final/narration-balance/scene-02.png` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/frames-final/narration-balance/scene-03.png` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/frames-final/narration-balance/scene-04.png` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/frames-final/narration-balance/scene-05.png` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/frames-final/narration-balance/scene-06.png` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/frames-final/narration-balance/scene-07.png` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/frames-final/narration-balance/transitions.png` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/frames-final/rough-cut/scene-01.png` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/frames-final/rough-cut/scene-02.png` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/frames-final/rough-cut/scene-03.png` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/frames-final/rough-cut/scene-04.png` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/frames-final/rough-cut/scene-05.png` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/frames-final/rough-cut/scene-06.png` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/frames-final/rough-cut/scene-07.png` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/frames-final/rough-cut/transitions.png` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/frames-previews-rough-cut.json` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/frames-previews.json` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/frames-previews/caption-review/contact.png` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/frames-previews/caption-review/scene-01.png` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/frames-previews/caption-review/scene-02.png` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/frames-previews/caption-review/scene-03.png` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/frames-previews/caption-review/scene-04.png` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/frames-previews/caption-review/scene-05.png` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/frames-previews/caption-review/scene-06.png` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/frames-previews/caption-review/scene-07.png` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/frames-previews/caption-review/transitions.png` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/frames-previews/narration-balance/contact.png` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/frames-previews/narration-balance/scene-01.png` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/frames-previews/narration-balance/scene-02.png` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/frames-previews/narration-balance/scene-03.png` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/frames-previews/narration-balance/scene-04.png` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/frames-previews/narration-balance/scene-05.png` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/frames-previews/narration-balance/scene-06.png` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/frames-previews/narration-balance/scene-07.png` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/frames-previews/narration-balance/transitions.png` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/frames-previews/rough-cut/contact.png` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/frames-previews/rough-cut/scene-01.png` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/frames-previews/rough-cut/scene-02.png` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/frames-previews/rough-cut/scene-03.png` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/frames-previews/rough-cut/scene-04.png` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/frames-previews/rough-cut/scene-05.png` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/frames-previews/rough-cut/scene-06.png` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/frames-previews/rough-cut/scene-07.png` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/frames-previews/rough-cut/transitions.png` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/lint.log` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/manifest.log` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/narration-aac320-candidate.mp4` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/preservation.json` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/preview-batch.log` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/previews-caption-review-inputs.json` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/previews-caption-review-mux.log` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/previews-caption-review-render.log` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/previews-narration-balance-inputs.json` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/previews-narration-balance-mux.log` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/previews-narration-balance-render.log` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/previews-rough-cut-inputs.json` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/previews-rough-cut-mux.log` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/previews-rough-cut-render.log` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/proposal.log` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/rough-frame-extract.log` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/tests-final.log` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/tests.log` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/validation.json` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/out/qa/verification-final.log` | ?? | H | Архив/локально — generated outputs/QA; отдельный архив, не обычный staging |
| `video-production/lesson-114-production/package-lock.json` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-114-production/package.json` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-114-production/public/f1-speech.wav` | ?? | H | Архив/локально — аудио-source/промежуточный материал; сохранить в production-архиве |
| `video-production/lesson-114-production/public/f1/f1-notepad-diagram.svg` | ?? | G | 4 — малый source asset; вместе с лицензией/провенансом |
| `video-production/lesson-114-production/public/f1/f1-paper-diagram.svg` | ?? | G | 4 — малый source asset; вместе с лицензией/провенансом |
| `video-production/lesson-114-production/public/fonts/NOTO-LICENSE.txt` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-114-production/public/fonts/NotoSans-Bold.ttf` | ?? | G | 4 — малый source asset; вместе с лицензией/провенансом |
| `video-production/lesson-114-production/public/fonts/NotoSans-Regular.ttf` | ?? | G | 4 — малый source asset; вместе с лицензией/провенансом |
| `video-production/lesson-114-production/scripts/audio.py` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-114-production/scripts/frames.py` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-114-production/scripts/integration_plan.py` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-114-production/scripts/listen.sh` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-114-production/scripts/manifest.py` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-114-production/scripts/render.mjs` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-114-production/scripts/test_production.py` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-114-production/scripts/verify.py` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-114-production/src/Workspace.tsx` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-114-production/src/index.tsx` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-114-production/tsconfig.json` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-115-production/.gitignore` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-115-production/ASSET_REQUIREMENTS.md` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-115-production/AUDIO_SUBTITLE_WORKFLOW.md` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-115-production/FINAL_QA.md` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-115-production/PRODUCTION_READINESS.md` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-115-production/README.md` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-115-production/RECORDING_CHECKLIST.md` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-115-production/REMOTION_GRAPHICS.md` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-115-production/V1_PRODUCTION_QA.md` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-115-production/V2_V3_COMPARATIVE_QA.md` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-115-production/audio/LICENSE_CIS` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-115-production/audio/music/minimal-tech-ambient-v1-theme-64s.wav` | ?? | H | Архив/локально — аудио-source/промежуточный материал; сохранить в production-архиве |
| `video-production/lesson-115-production/audio/narration/m5-l15-v1-export-check/scene-01.wav` | ?? | H | Архив/локально — аудио-source/промежуточный материал; сохранить в production-архиве |
| `video-production/lesson-115-production/audio/narration/m5-l15-v1-export-check/scene-02.wav` | ?? | H | Архив/локально — аудио-source/промежуточный материал; сохранить в production-архиве |
| `video-production/lesson-115-production/audio/narration/m5-l15-v1-export-check/scene-03.wav` | ?? | H | Архив/локально — аудио-source/промежуточный материал; сохранить в production-архиве |
| `video-production/lesson-115-production/audio/narration/m5-l15-v1-export-check/scene-04.wav` | ?? | H | Архив/локально — аудио-source/промежуточный материал; сохранить в production-архиве |
| `video-production/lesson-115-production/audio/narration/m5-l15-v1-export-check/scene-05.wav` | ?? | H | Архив/локально — аудио-source/промежуточный материал; сохранить в production-архиве |
| `video-production/lesson-115-production/audio/narration/m5-l15-v1-export-check/scene-06.wav` | ?? | H | Архив/локально — аудио-source/промежуточный материал; сохранить в production-архиве |
| `video-production/lesson-115-production/audio/narration/m5-l15-v2-vertical-adaptation/scene-01.wav` | ?? | H | Архив/локально — аудио-source/промежуточный материал; сохранить в production-архиве |
| `video-production/lesson-115-production/audio/narration/m5-l15-v2-vertical-adaptation/scene-02.wav` | ?? | H | Архив/локально — аудио-source/промежуточный материал; сохранить в production-архиве |
| `video-production/lesson-115-production/audio/narration/m5-l15-v2-vertical-adaptation/scene-03.wav` | ?? | H | Архив/локально — аудио-source/промежуточный материал; сохранить в production-архиве |
| `video-production/lesson-115-production/audio/narration/m5-l15-v2-vertical-adaptation/scene-04.wav` | ?? | H | Архив/локально — аудио-source/промежуточный материал; сохранить в production-архиве |
| `video-production/lesson-115-production/audio/narration/m5-l15-v2-vertical-adaptation/scene-05.wav` | ?? | H | Архив/локально — аудио-source/промежуточный материал; сохранить в production-архиве |
| `video-production/lesson-115-production/audio/narration/m5-l15-v2-vertical-adaptation/scene-06.wav` | ?? | H | Архив/локально — аудио-source/промежуточный материал; сохранить в production-архиве |
| `video-production/lesson-115-production/audio/narration/m5-l15-v3-final-review/scene-01.wav` | ?? | H | Архив/локально — аудио-source/промежуточный материал; сохранить в production-архиве |
| `video-production/lesson-115-production/audio/narration/m5-l15-v3-final-review/scene-02.wav` | ?? | H | Архив/локально — аудио-source/промежуточный материал; сохранить в production-архиве |
| `video-production/lesson-115-production/audio/narration/m5-l15-v3-final-review/scene-03.wav` | ?? | H | Архив/локально — аудио-source/промежуточный материал; сохранить в production-архиве |
| `video-production/lesson-115-production/audio/narration/m5-l15-v3-final-review/scene-04.wav` | ?? | H | Архив/локально — аудио-source/промежуточный материал; сохранить в production-архиве |
| `video-production/lesson-115-production/audio/narration/m5-l15-v3-final-review/scene-05.wav` | ?? | H | Архив/локально — аудио-source/промежуточный материал; сохранить в production-архиве |
| `video-production/lesson-115-production/audio/narration/m5-l15-v3-final-review/scene-06.wav` | ?? | H | Архив/локально — аудио-source/промежуточный материал; сохранить в production-архиве |
| `video-production/lesson-115-production/audio/narration_sentences/m5-l15-v1-export-check/scene-01-cue-01.wav` | ?? | H | Архив/локально — аудио-source/промежуточный материал; сохранить в production-архиве |
| `video-production/lesson-115-production/audio/narration_sentences/m5-l15-v1-export-check/scene-01-cue-02.wav` | ?? | H | Архив/локально — аудио-source/промежуточный материал; сохранить в production-архиве |
| `video-production/lesson-115-production/audio/narration_sentences/m5-l15-v1-export-check/scene-01-cue-03.wav` | ?? | H | Архив/локально — аудио-source/промежуточный материал; сохранить в production-архиве |
| `video-production/lesson-115-production/audio/narration_sentences/m5-l15-v1-export-check/scene-02-cue-01.wav` | ?? | H | Архив/локально — аудио-source/промежуточный материал; сохранить в production-архиве |
| `video-production/lesson-115-production/audio/narration_sentences/m5-l15-v1-export-check/scene-02-cue-02.wav` | ?? | H | Архив/локально — аудио-source/промежуточный материал; сохранить в production-архиве |
| `video-production/lesson-115-production/audio/narration_sentences/m5-l15-v1-export-check/scene-02-cue-03.wav` | ?? | H | Архив/локально — аудио-source/промежуточный материал; сохранить в production-архиве |
| `video-production/lesson-115-production/audio/narration_sentences/m5-l15-v1-export-check/scene-03-cue-01.wav` | ?? | H | Архив/локально — аудио-source/промежуточный материал; сохранить в production-архиве |
| `video-production/lesson-115-production/audio/narration_sentences/m5-l15-v1-export-check/scene-03-cue-02.wav` | ?? | H | Архив/локально — аудио-source/промежуточный материал; сохранить в production-архиве |
| `video-production/lesson-115-production/audio/narration_sentences/m5-l15-v1-export-check/scene-03-cue-03.wav` | ?? | H | Архив/локально — аудио-source/промежуточный материал; сохранить в production-архиве |
| `video-production/lesson-115-production/audio/narration_sentences/m5-l15-v1-export-check/scene-04-cue-01.wav` | ?? | H | Архив/локально — аудио-source/промежуточный материал; сохранить в production-архиве |
| `video-production/lesson-115-production/audio/narration_sentences/m5-l15-v1-export-check/scene-04-cue-02.wav` | ?? | H | Архив/локально — аудио-source/промежуточный материал; сохранить в production-архиве |
| `video-production/lesson-115-production/audio/narration_sentences/m5-l15-v1-export-check/scene-05-cue-01.wav` | ?? | H | Архив/локально — аудио-source/промежуточный материал; сохранить в production-архиве |
| `video-production/lesson-115-production/audio/narration_sentences/m5-l15-v1-export-check/scene-05-cue-02.wav` | ?? | H | Архив/локально — аудио-source/промежуточный материал; сохранить в production-архиве |
| `video-production/lesson-115-production/audio/narration_sentences/m5-l15-v1-export-check/scene-05-cue-03.wav` | ?? | H | Архив/локально — аудио-source/промежуточный материал; сохранить в production-архиве |
| `video-production/lesson-115-production/audio/narration_sentences/m5-l15-v1-export-check/scene-06-cue-01.wav` | ?? | H | Архив/локально — аудио-source/промежуточный материал; сохранить в production-архиве |
| `video-production/lesson-115-production/audio/narration_sentences/m5-l15-v1-export-check/scene-06-cue-02.wav` | ?? | H | Архив/локально — аудио-source/промежуточный материал; сохранить в production-архиве |
| `video-production/lesson-115-production/audio/narration_sentences/m5-l15-v1-export-check/scene-06-cue-03.wav` | ?? | H | Архив/локально — аудио-source/промежуточный материал; сохранить в production-архиве |
| `video-production/lesson-115-production/audio/narration_sentences/m5-l15-v2-vertical-adaptation/scene-01-cue-01.wav` | ?? | H | Архив/локально — аудио-source/промежуточный материал; сохранить в production-архиве |
| `video-production/lesson-115-production/audio/narration_sentences/m5-l15-v2-vertical-adaptation/scene-01-cue-02.wav` | ?? | H | Архив/локально — аудио-source/промежуточный материал; сохранить в production-архиве |
| `video-production/lesson-115-production/audio/narration_sentences/m5-l15-v2-vertical-adaptation/scene-02-cue-01.wav` | ?? | H | Архив/локально — аудио-source/промежуточный материал; сохранить в production-архиве |
| `video-production/lesson-115-production/audio/narration_sentences/m5-l15-v2-vertical-adaptation/scene-02-cue-02.wav` | ?? | H | Архив/локально — аудио-source/промежуточный материал; сохранить в production-архиве |
| `video-production/lesson-115-production/audio/narration_sentences/m5-l15-v2-vertical-adaptation/scene-02-cue-03.wav` | ?? | H | Архив/локально — аудио-source/промежуточный материал; сохранить в production-архиве |
| `video-production/lesson-115-production/audio/narration_sentences/m5-l15-v2-vertical-adaptation/scene-03-cue-01.wav` | ?? | H | Архив/локально — аудио-source/промежуточный материал; сохранить в production-архиве |
| `video-production/lesson-115-production/audio/narration_sentences/m5-l15-v2-vertical-adaptation/scene-03-cue-02.wav` | ?? | H | Архив/локально — аудио-source/промежуточный материал; сохранить в production-архиве |
| `video-production/lesson-115-production/audio/narration_sentences/m5-l15-v2-vertical-adaptation/scene-04-cue-01.wav` | ?? | H | Архив/локально — аудио-source/промежуточный материал; сохранить в production-архиве |
| `video-production/lesson-115-production/audio/narration_sentences/m5-l15-v2-vertical-adaptation/scene-04-cue-02.wav` | ?? | H | Архив/локально — аудио-source/промежуточный материал; сохранить в production-архиве |
| `video-production/lesson-115-production/audio/narration_sentences/m5-l15-v2-vertical-adaptation/scene-05-cue-01.wav` | ?? | H | Архив/локально — аудио-source/промежуточный материал; сохранить в production-архиве |
| `video-production/lesson-115-production/audio/narration_sentences/m5-l15-v2-vertical-adaptation/scene-05-cue-02.wav` | ?? | H | Архив/локально — аудио-source/промежуточный материал; сохранить в production-архиве |
| `video-production/lesson-115-production/audio/narration_sentences/m5-l15-v2-vertical-adaptation/scene-06-cue-01.wav` | ?? | H | Архив/локально — аудио-source/промежуточный материал; сохранить в production-архиве |
| `video-production/lesson-115-production/audio/narration_sentences/m5-l15-v2-vertical-adaptation/scene-06-cue-02.wav` | ?? | H | Архив/локально — аудио-source/промежуточный материал; сохранить в production-архиве |
| `video-production/lesson-115-production/audio/narration_sentences/m5-l15-v3-final-review/scene-01-cue-01.wav` | ?? | H | Архив/локально — аудио-source/промежуточный материал; сохранить в production-архиве |
| `video-production/lesson-115-production/audio/narration_sentences/m5-l15-v3-final-review/scene-01-cue-02.wav` | ?? | H | Архив/локально — аудио-source/промежуточный материал; сохранить в production-архиве |
| `video-production/lesson-115-production/audio/narration_sentences/m5-l15-v3-final-review/scene-02-cue-01.wav` | ?? | H | Архив/локально — аудио-source/промежуточный материал; сохранить в production-архиве |
| `video-production/lesson-115-production/audio/narration_sentences/m5-l15-v3-final-review/scene-02-cue-02.wav` | ?? | H | Архив/локально — аудио-source/промежуточный материал; сохранить в production-архиве |
| `video-production/lesson-115-production/audio/narration_sentences/m5-l15-v3-final-review/scene-02-cue-03.wav` | ?? | H | Архив/локально — аудио-source/промежуточный материал; сохранить в production-архиве |
| `video-production/lesson-115-production/audio/narration_sentences/m5-l15-v3-final-review/scene-03-cue-01.wav` | ?? | H | Архив/локально — аудио-source/промежуточный материал; сохранить в production-архиве |
| `video-production/lesson-115-production/audio/narration_sentences/m5-l15-v3-final-review/scene-03-cue-02.wav` | ?? | H | Архив/локально — аудио-source/промежуточный материал; сохранить в production-архиве |
| `video-production/lesson-115-production/audio/narration_sentences/m5-l15-v3-final-review/scene-04-cue-01.wav` | ?? | H | Архив/локально — аудио-source/промежуточный материал; сохранить в production-архиве |
| `video-production/lesson-115-production/audio/narration_sentences/m5-l15-v3-final-review/scene-04-cue-02.wav` | ?? | H | Архив/локально — аудио-source/промежуточный материал; сохранить в production-архиве |
| `video-production/lesson-115-production/audio/narration_sentences/m5-l15-v3-final-review/scene-05-cue-01.wav` | ?? | H | Архив/локально — аудио-source/промежуточный материал; сохранить в production-архиве |
| `video-production/lesson-115-production/audio/narration_sentences/m5-l15-v3-final-review/scene-05-cue-02.wav` | ?? | H | Архив/локально — аудио-source/промежуточный материал; сохранить в production-архиве |
| `video-production/lesson-115-production/audio/narration_sentences/m5-l15-v3-final-review/scene-05-cue-03.wav` | ?? | H | Архив/локально — аудио-source/промежуточный материал; сохранить в production-архиве |
| `video-production/lesson-115-production/audio/narration_sentences/m5-l15-v3-final-review/scene-06-cue-01.wav` | ?? | H | Архив/локально — аудио-source/промежуточный материал; сохранить в production-архиве |
| `video-production/lesson-115-production/audio/narration_sentences/m5-l15-v3-final-review/scene-06-cue-02.wav` | ?? | H | Архив/локально — аудио-source/промежуточный материал; сохранить в production-архиве |
| `video-production/lesson-115-production/audio/narration_sentences/m5-l15-v3-final-review/scene-06-cue-03.wav` | ?? | H | Архив/локально — аудио-source/промежуточный материал; сохранить в production-архиве |
| `video-production/lesson-115-production/content/audio-bgm-provenance.json` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-115-production/content/audio-mix-provenance.json` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-115-production/content/audio-sentence-mix-provenance.json` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-115-production/content/narration-provenance.json` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-115-production/content/narration-sentence-cues-provenance.json` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-115-production/content/timings-sentence.json` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-115-production/content/timings.json` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-115-production/content/videos.json` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-115-production/eslint.config.mjs` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-115-production/narration/m5-l15-v1-export-check.ru.md` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-115-production/narration/m5-l15-v2-vertical-adaptation.ru.md` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-115-production/narration/m5-l15-v3-final-review.ru.md` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-115-production/node_modules` | ?? | I | Архив/локально — symlink на локальную установку зависимостей; не staging |
| `video-production/lesson-115-production/package.json` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-115-production/public/fonts/NOTO-LICENSE.txt` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-115-production/public/fonts/NotoSans-Bold.ttf` | ?? | G | 4 — малый source asset; вместе с лицензией/провенансом |
| `video-production/lesson-115-production/public/fonts/NotoSans-Regular.ttf` | ?? | G | 4 — малый source asset; вместе с лицензией/провенансом |
| `video-production/lesson-115-production/public/sfx/finish.wav` | ?? | G | 4 — малый source asset; вместе с лицензией/провенансом |
| `video-production/lesson-115-production/public/sfx/place.wav` | ?? | G | 4 — малый source asset; вместе с лицензией/провенансом |
| `video-production/lesson-115-production/public/sfx/select.wav` | ?? | G | 4 — малый source asset; вместе с лицензией/провенансом |
| `video-production/lesson-115-production/remotion.config.ts` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-115-production/scripts/extract_frames.py` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-115-production/scripts/generate_narration.py` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-115-production/scripts/generate_sentence_narration.py` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-115-production/scripts/mix_background_music.py` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-115-production/scripts/prepare_audio.py` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-115-production/scripts/render.mjs` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-115-production/scripts/test_background_music.py` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-115-production/scripts/test_content.py` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-115-production/src/Lesson115.tsx` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-115-production/src/Root.tsx` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-115-production/src/SceneVisual.tsx` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-115-production/src/fonts.ts` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-115-production/src/index.tsx` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-115-production/src/tokens.ts` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-115-production/storyboards/m5-l15-v1-export-check.storyboard.md` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-115-production/storyboards/m5-l15-v2-vertical-adaptation.storyboard.md` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-115-production/storyboards/m5-l15-v3-final-review.storyboard.md` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/lesson-115-production/tsconfig.json` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/module-5-style-test/.gitignore` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/module-5-style-test/.prettierrc` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/module-5-style-test/README.md` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/module-5-style-test/eslint.config.mjs` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/module-5-style-test/package-lock.json` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/module-5-style-test/package.json` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/module-5-style-test/public/fonts/NOTO-LICENSE.txt` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/module-5-style-test/public/fonts/NotoSans-Bold.ttf` | ?? | G | 4 — малый source asset; вместе с лицензией/провенансом |
| `video-production/module-5-style-test/public/fonts/NotoSans-Regular.ttf` | ?? | G | 4 — малый source asset; вместе с лицензией/провенансом |
| `video-production/module-5-style-test/remotion.config.ts` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/module-5-style-test/scripts/verify-output.mjs` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/module-5-style-test/src/Composition.tsx` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/module-5-style-test/src/Root.tsx` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/module-5-style-test/src/fonts.ts` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/module-5-style-test/src/index.ts` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/module-5-style-test/src/tokens.ts` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/module-5-style-test/tsconfig.json` | ?? | G | 4 — Remotion source/config/lockfile/script/текст/лицензия |
| `video-production/module-6-production/README.md` | ?? | F | 5 — утверждённая спецификация Module6 |

Итого по классам: A: 17, B: 16, C: 21, D: 4, E: 10, F: 25, G: 172, H: 258, I: 35, J: 237.

## Итог

Checkpoint приложения можно подготовить по группам1–3/5 после staged review; источники видео сохранять группой4 с явными ограничениями воспроизводимости. Lockfile/verify115 восстановлены в P1K. Production portability по-прежнему требует P1J media archive, MIT voice environment и согласованного approval для будущего rerender; Git не заменяет private DB/media backup. Никакого staging/commit/push/DB write/публикации в P1E не выполнялось.

P1K allowlist addition: `certificates/pdf.py` — группа1; source/test/document, без production media.

P1K allowlist addition: `certificates/test_pdf.py` — группа1; source/test/document, без production media.

P1K allowlist addition: `video-production/lesson-115-production/package-lock.json` — группа4; source/test/document, без production media.

P1K allowlist addition: `video-production/lesson-115-production/scripts/verify.py` — группа4; source/test/document, без production media.

P1K allowlist addition: `video-production/lesson-115-production/scripts/test_verify.py` — группа4; source/test/document, без production media.

P1K allowlist addition: `docs/courses/certificate-pdf-p1i.md` — группа5; source/test/document, без production media.

P1K allowlist addition: `docs/courses/checkpoint-readiness-p1k.md` — группа5; source/test/document, без production media.
