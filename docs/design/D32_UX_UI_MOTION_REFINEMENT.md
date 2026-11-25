# D3.2 — UX/UI, motion и завершение проверки

Дата:2026-11-25. Ветка `design/graphite-lime`, HEAD `bc05bef`. D3/D3.1/D3.2 сохранены без отката, staging или commit. Палитра Obsidian/Frost/Aqua одобрена владельцем; композиция D3.2 ожидает личной приёмки. **Настоящая оптическая рефракция — отдельный D3.3, не выполненный в этом отчёте.**

## Восстановление прерванной работы

Найдены готовые Canvas-field, OpticalCompanion, единый Studio shell, тесты и173+диагностических/проверочных файлов. Предыдущий полный frontend run:448passed/0failed, lint/build PASS. Временные процессы/SQLite/логи после перезапуска не сохранились; восстановлены новый isolated API/Vite и SQLite-copy. Реализация не начиналась заново. Ранний браузерный проход не завершил nested-editor QA: часть кадров содержала loading, harness ожидал несуществующий `.instructor-quiz-editor`. Исправлен только временный harness; реальные редакторы ожидались по существующим DOM landmarks. Старые кадры не объявлены passing evidence.

## Независимый аудит и исправления

| Приоритет | Подтверждённое наблюдение | Решение D3.2 |
|---|---|---|
| P1 | Sidebar существовал только на overview, глубокие экраны меняли навигационную модель | Общая Studio оболочка и стабильный Outlet на всех маршрутах |
| P1 | max-width1320 и nav13px терялись на1920/2560 | Ширина до2240px, sidebar248–264px, labels/nav15–16px; плотный читательский текст не растянут специально |
| P1 | Glass84–92% почти скрывал фон | Материалы68/72/52%, dense94%; blur только по назначению, opaque fallback |
| P2 | Ригидные широкие SVG ribbons не деформировались | Оригинальное процедурное поле света Canvas2D |
| P2 | Auth-линии не имели характера | Парная оптическая скульптура с idle и pointer gaze |
| P2 | Длинные hero course cards вытесняли действия | Компактный список, метаданные рядом с названием, действия в общей строке |
| P2 | Казахское слово заканчивалось отдельной буквой | Заголовок18ch, normal word wrapping; повторный реальный KK просмотр подтвердил исправление |

Реально участвовали независимые UX/frontend reviewer, UI/browser reviewer и creative motion+performance reviewer; auth-реализацию выполнил отдельный worker. Первый native browser reviewer не смог запустить настроенный Playwright Firefox1578 (его нет); его выводы ограничены изображениями/кодом. Другие агенты и основной агент использовали уже установленный Chromium. Установка браузеров/зависимостей не выполнялась. Финальные независимые UX и motion/accessibility review повторены после реализации: **SHIP в проверенном объёме**, без материальных UI-блокеров. Studio reviewer проверял13актуальных изображений основного агента, не выдавал их за собственный authenticated interactive E2E. Это не одобрение владельца.

## Фон: установленная причина и граница знания

До изменений Chromium действительно двигал SVG: примерно6px за5s, при неизменных `d` путей. CSS32s/48s, низкая alpha и плотные панели объясняют визуальную слабость. На Home/Auth не найден непрозрачный родитель, перекрывающий фон. **Точная причина полной неподвижности в Firefox владельца неизвестна:** его reduced-motion, cache и runtime не были доступны. Не утверждается, что найден Firefox-specific баг.

Новый `createLiquidPixels` — детерминированные взаимно деформируемые направленные волны и crest highlights, без случайных circles, WebGL, внешних ассетов или API. Canvas160×100/target24fps desktop;96×72/target12fps mobile/≤4CPU, повторное использование ImageData. Один RAF, hidden pause, cleanup/theme/media-query subscriptions; reduced-motion рисует статический кадр. Нет анимируемого blur. Тема и сохранение выбора не изменены; D4 не начат.

Реальная motion evidence без scrolling:

- Chromium: менялись time/draw counters и пиксели; independent hidden simulation замораживает Canvas и оптические CSS-переменные. Это `visibilitychange`/document.hidden simulation, не реальная вкладка ОС.
- Firefox143 через встроенный WebDriver BiDi:36→148draws за5.2s, pixel207/222/231→198/216/227, scroll0. Старый Playwright driver несовместим с локальным cached Firefox; native BiDi использован без установки и без обхода execution approval.
- Firefox:8authcases Login/Register×1440/390×light/dark, pointer−5.60→6.94px, idle. Firefox reduced-motion отдельно не выполнен; Chromium reduced проверен после live preference change: счётчики40→40, optic properties очищены.
- [Firefox motion JSON](screenshots/d32/d32-firefox-motion.json), [Firefox matrix](screenshots/d32/firefox-verification.json), [independent settled motion](screenshots/d32/independent-motion-final-settled.json).

## Glass и auth

Материалы: navigation72%, primary workspace68%, secondary hero52%, dialogs94%; контролы/длинный текст сильнее изолированы. Backdrop blur12–24px и saturation115–120%, с непрозрачным fallback до `@supports`. Форма реально вычисляет rgba(...,.68),blur22px saturate1.15 в Chromium и Firefox. Родители прозрачны. Диагностические снимки `glass-material-{normal,blur-disabled-control,opaque-control}.png` сравнивают реальный материал и временные DOM controls; последние не production styling.

Это frosted layering, **не полноценное преломление/искажение**. Усиление материала по новым референсам сознательно отнесено к D3.3, без заявления, что одного CSS blur достаточно.

OpticalCompanion: собственная геометрия двух линз, aqua ядра, отражения, idle breathing и ограниченный gaze. Pointer-код использует только координаты и rect объекта, не читает значения полей/пароли. Hidden/offscreen pause, reduced static, cleanup; mobile190×106. Существующие children/form handlers/password toggles/validation сохранены. Новые UI-строки не понадобились; RU/KK/EN переиспользуются.

## Полная оболочка Studio

Фактически проверены с настоящим API, synthetic admin, desktop1920lightRU/mobile390darkKK:

1. `/instructor` — overview.
2. `/instructor/courses` — список.
3. `/instructor/courses/new` — форма создания.
4. `/instructor/import` — Word import UI.
5. `/instructor/submissions` — общий список; дополнительно synthetic заполненная review form с4полями рубрики.
6. `/instructor/enrollment-requests` — заявки.
7. `/instructor/reviews` — модерация публикации (empty state).
8. `/instructor/instructors` — управление ролями.
9. `/instructor/courses/10/edit` — настройки.
10. `/instructor/courses/10/curriculum` — модули, открытый lesson editor, sections/attachment tools.
11. `/instructor/courses/10/assessment` — quiz/assignment selectors; отдельно lesson116,15question quiz и assignment forms,4критерия отображаются.
12. `/instructor/courses/10/submissions` — course-specific list.
13. `/instructor/courses/10/publication` —7requirements,2acknowledgements, переход в assessment.
14. `/instructor/courses/ai-media-content/preview` — student-facing preview.

Sidebar общий на всех глубоких маршрутах. Course tabs — второй контекстный уровень. Mobile использует существующий disclosure/Escape/focus pattern. Расширена внешняя `.studio-container`, иначе старый main max1320 ограничивал новую оболочку. Outlet не получил path-key; backend/save/permission flow не менялись. Формы/метаданные увеличены избирательно, список курсов компактнее, лишние вложенные borders сняты. Motion: active/hover/pressed controls, menus/dialog entrance и существующие Studio entrances; reduced-motion отключает лишнее движение. Новая полноценная choreography theme switching не реализована.

## Браузерные результаты

[Chromium verification](screenshots/d32/chromium-verification.json):54visits/assertions (включая повтор assessment после исправления harness), из них44основных matrixcases:18public+26Studio. Основной public spot matrix1440/2560/768/390/320, RU/KK/EN, обе темы; прежние1920/2560captures сохранены. Дополнительно independent18cases home/login/register×1440/390/320×light/dark,KK:overflow0,JSerrors0,labels связаны. Не заявляется полное декартово произведение всех маршрутов×размеров×языков.

Реально через UI/API браузера:

- Synthetic admin/student login; реальные fetch/JWT, не mock API.
- Открытие quiz и assignment116,4criterion labels; synthetic submission review4integer inputs наdesktop/mobile, без отправки оценки.
- В lesson editor введён локальный draft; сохранение неизменённого module title вызвало настоящий workspace reload, draft сохранился. Native confirm dismiss сохраняет, accept закрывает/отбрасывает. Рабочие данные не задействованы.
- Publication: статус/блокеры/ссылка в assessment. Реальную заявку не отправляли и курс не публиковали. Отправка/одобрение покрыты отдельным isolated Django test `test_blocker_preview_request_and_moderation`, а не новым UI publication E2E.
- Студент: Profile, enrolled draft Course10, lesson113. Video currentTime0.82→8.28, readyState4 после seek, ошибок нет. У первого113video нет VTT — это не объявлено дефектом. Lesson115 имеет1track, переведён в `showing` при реальном playback.
- Keyboard focus-visible3px, pointer lens, reduced-motion, no horizontal overflow и pageerror0. Отдельный13route console/network probe: consoleErrors0,pageErrors0,HTTP4xx/5xx0;16requestfailed `ERR_ABORTED` при StrictMode cleanup/переходах (существующий AbortController), не замаскированы под server errors. JSON: screenshots/d32/console-network-verification.json.
- Не повторялись полный course completion, реальные submissions/certificates, все9video и все download permutations: они не изменены этим visual patch.

Копия рабочей SQLite создана SQLite backup API. Usernames обезличены, original submissions удалены **только в копии**, синтетические пользователи и одна synthetic review submission существуют только там. Reviewer заметил свободный текст copied enrollment request:4diagnostic PNG сохранены в private `/tmp/.../private-diagnostic-captures/`, вне docs; запросы обезличены в копии,2verifiedзамены пересняты. Ничьи рабочие файлы/медиа/бэкапы не удалены.

## Производительность и доступность

Оригинальные математические эффекты не используют новые dependencies. Raster median4.1–9.6ms,p9510.6–17.9ms на общем8CPU headless host; наблюдалось8–13draws/s при целевых24 под параллельной нагрузкой. Нельзя обещать устойчивые24FPS,60FPS или подтверждённую автономность low-power/mobile devices. Независимый reviewer не нашёл блокера, но аппаратная проверка остаётся в D8. WebGL не требуется.

AA semantic/composited contrast assertions сохранены с alpha68%. Inputs остаются плотными, фокус/labels/native validation сохранены. Полной WCAG-сертификации всего приложения не заявляем. Unsupported-backdrop fallback проверен кодом/тестом, не отдельным старым браузером.

## Регрессии и команды

Предыдущий полный run текущей D3.2 реализации: `cd frontend && node --test tests/*.test.mjs` —448passed/0failed, lint/build PASS. После возобновления логика не переписывалась; после финального CSS переноса KK выполнены:

```sh
cd frontend
node --test tests/auth-design.test.mjs tests/studio-shell-design.test.mjs tests/liquid-field.test.mjs tests/liquid-glass.test.mjs
npm run lint
npm run build
```

22passed/0failed, lint/build PASS. Полный448run не повторялся без необходимости, как просил владелец.

Из корня с временным settings_d32, изолированный test DB:

```sh
PYTHONPATH="/tmp/ai-d32-resume-ibi2xm6_:$PWD" DJANGO_SETTINGS_MODULE=settings_d32 .venv/bin/python -B manage.py test studio.tests studio.test_section_creation studio.test_section_renames studio.test_attachment_placement studio.test_assignment_authoring studio.test_quiz_authoring studio.test_publication_readiness courses.test_video --noinput --verbosity 2
```

**74tests PASS**, Django check0issues, `git diff --check` PASS. Первичный sandbox-run завис на async streaming и был прерван; корректный разрешённый системный запуск завершён. В одном промежуточном53test-run был нестабильный existing DOCX fixture test:201 вместо400. Причина подтверждена отдельно: `studio.tests.document()` создаёт ZIP с текущими timestamps; спустя2s XML одинаков, байты/SHA разные. Сервер правильно сравнивает source SHA, тест предполагает идентичные bytes. Повтор74PASS не скрывает этот риск; исправление fixture отдельно, backend/functionality в D3.2 не менялись.

117контрольных хешей working DB/settings/media совпали; integrityOK/FK0/Course10 unpublished. Index пуст, HEADbc05bef. Live course/user/certificate records не менялись.

## Точные D3.2 исходники

- `frontend/src/App.jsx` — только visual main class для широкого Studio.
- `frontend/src/components/AuthLayout.jsx`, `frontend/src/components/AuthLayout.css`.
- Новые `frontend/src/components/OpticalCompanion.jsx`, `frontend/src/components/OpticalCompanion.css`.
- `frontend/src/components/landing/LiquidEnvironment.jsx`, `frontend/src/components/landing/LiquidEnvironment.css`.
- Новый `frontend/src/utils/liquidField.js`.
- `frontend/src/pages/instructor/InstructorStudio.jsx`, новый `frontend/src/pages/instructor/studio-glass.css`.
- `frontend/src/styles/v2-tokens.css`, `frontend/src/styles/liquid-surfaces.css`.
- `frontend/tests/auth-design.test.mjs`, `frontend/tests/liquid-glass.test.mjs`; новые `frontend/tests/liquid-field.test.mjs`, `frontend/tests/studio-shell-design.test.mjs`.
- `DESIGN.md`, `docs/design/REDESIGN_ROADMAP.md`, этот отчёт; `docs/project-memory/CURRENT_STATE.md`, `DECISIONS.md`, `ROADMAP.md`.
- `docs/design/screenshots/d32/*`: точный path/size/hash inventory в [verification.json](screenshots/d32/verification.json). Не все исторические кадры являются passing QA; роли описаны в inventory.

Остальные D3/D3.1/исторические WIP, включая PRODUCT/locales/Header/Footer/fonts/config/settings.py, сохранены и не приписываются новым D3.2 правкам. Приложение/backend/API/contracts/media manifests не переписаны.

## До/после и запись

- Home: [D3.1 до](screenshots/d32/before-d31-home-1440-light.jpg) → [после](screenshots/d32/verified-home-1440-light-ru.png).
- Auth: [до](screenshots/d32/before-d31-login-1440-dark.jpg) → [после1440RU](screenshots/d32/comparison-login-1440-dark-ru.png).
- Studio: [до](screenshots/d32/before-d31-studio-1440-light.jpg) → [после1440RU](screenshots/d32/comparison-studio-1440-light-ru.png), [широкая оболочка1920](screenshots/d32/verified-instructor-1920-light.png), [редактор](screenshots/d32/verified-instructor-courses-10-edit-1920-light.png), [mobile](screenshots/d32/verified-instructor-courses-10-curriculum-390-dark.png).
- [Короткая motion запись](screenshots/d32/liquid-motion-chromium.mp4): настоящий CDP screencast52frames, исходные timestamps, H.2641440×1000,4.8s, без звука. Это QA интерфейса, не учебное видео. Playwright recorder недоступен из-за отсутствующего bundled FFmpeg; существующий системный FFmpeg использован без установки.

## Следующая стадия и preview

**http://127.0.0.1:5199/** — действующий isolated preview, Django8199. Home/Login/Register доступны без входа. Synthetic credentials хранятся только локально в `/tmp/ai-d32-resume-ibi2xm6_/accounts.json`, здесь не публикуются; реальные пользовательские сессии не переносятся. Серверы временные, не deployment.

Roadmap D3.2→D3.3→D4–D8→F1–F7 сохранён в обоих roadmap. Цель — v1.0 с двумя курсами и course-aware RAG/LLM tutor без выдачи ключей/замены grading; новый tutor, инфраструктура, провайдеры и дополнительные курсы сейчас не реализуются. Новые курсы отложены до запуска. Технический референс D3.3 https://freefrontend.com/css-liquid-glass/ вернул403 при чтении; код/лицензии примеров не проверены и не заимствованы.

Остались: личное визуальное одобрение D3.2; D3.3 optical material; реальный low-power/OS-background-tab spot check; Firefox reduced-motion отдельный прогон; отдельное решение по deterministic DOCX test fixture. D3.3/D4/F1–F7 не начаты. Никаких staging/commit/push/merge/publication/certificate activation.
