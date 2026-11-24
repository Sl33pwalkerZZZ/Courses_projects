# D2 — Graphite & Lime Design System

Дата:2026-11-24. Ветка `design/graphite-lime`, HEAD `888317e` сохранён. D0/D1 не откатывались. Этап D2 завершён; D3 не начат. Система реализована по направлению владельца; новая человеческая визуальная приёмка не заявляется.

## Объём и решения

Вместо доминирующего Amethyst — нейтральные Graphite/Carbon/Paper, ограниченный lime для primary-action, тёмно-зелёные ссылки в light. Это общая основа, а не отдельный редизайн каждой страницы. Существующие композиции, анимационные сцены, обработчики, API, маршруты и правила доступа сохранены. Старые SVG и исторические названия CSS не удалялись.

Карта каскада: `v2-tokens.css` → aliases в `index.css` → shared `components/ui/ui.css` → feature CSS. `main.jsx` сохраняет index/v2/playground/amethyst слои; `cinematic-landing.css` остаётся потребителем токенов. Все прежние имена `--v2-*` сохранены; semantic `--color-*` добавлены поверх этого контракта. Автоматической замены каждого цветового литерала не было. Нейтральный фон видео, mask-black и тени оставлены по назначению; старые purple SVG — тема будущих страниц, не причина менять реальные учебные медиа.

### Палитра

| Роль | Dark | Light |
|---|---|---|
| Background | #101210 | #F4F5F0 |
| Surface / elevated | #1C211D / #29312B | #FFFFFF / #E8ECE2 |
| Text / secondary | #F4F5F0 / #B0BAAA | #182019 / #4E5B4B |
| Primary / on-primary | #C4F56A / #101210 | #C4F56A / #101210 |
| Link / focus | #C4F56A / #C4F56A | #355B16 / #41691B |
| Border / control-border | #3D493E / #82917E | #CAD2C3 / #66735E |
| Success / warning | #81D4A6 / #F5CF87 | #23623B / #81520C |
| Error / info | #FFB4A9 / #A7CBFA | #A72F32 / #275D8A |

Hover, active, disabled, progress, status backgrounds, hero aliases и полная спецификация — [DESIGN.md](../../DESIGN.md), нормативные значения — CSS. Исходный muted #929B90 не использован как обычный светлый текст; контраст важнее буквального копирования стартовой палитры.

### Типографика и лицензии

- **Noto Sans normal variable400–800:** основной интерфейс и headings. Четыре локальных WOFF2-subsets, `font-display:swap`, без runtime-запросов к Google.
- **IBM Plex Mono Regular400:** code/kbd/samp/pre, технические обозначения и будущий ASCII; не весь учебный текст.
- Реальные cmap обоих семейств покрывают RU/EN и `Әә Ғғ Ққ Ңң Өө Ұұ Үү Һһ Іі`. Chromium CDP подтвердил `isCustomFont:true` для Noto Sans и IBM Plex Mono на строке образца.
- Проверенная сборка Manrope `3ae11c49…a9d6ae6` не содержит `ӘәҒғҚқҢңҰұ`. Она **не поставляется**. Выбран Noto Sans, чтобы не смешивать системные fallback внутри казахских слов.
- 5 font binaries:430120bytes суммарно; размеры каждого файла в provenance; файлы загружаются по unicode-range. OFL notices сохранены, шрифты не модифицированы и не переименованы как семейства.
- Источники: [Google Fonts Noto Sans](https://fonts.google.com/noto/specimen/Noto+Sans), [IBM Plex](https://github.com/IBM/plex). Immutable URLs/revision, размеры и SHA-256: `frontend/public/fonts/provenance.json`; лицензии `NotoSans-OFL.txt`, `IBMPlexMono-OFL.txt`. Никаких новых npm-зависимостей.

Scale:body16px/1.65, reading17px token, labels14px/1.45/600, captions13px/1.45/600, headings700/1.16/−.025em. Specimen h1 clamp32–56px. Масштабы отдельных страниц ещё не перепроектированы.

### Компоненты и motion

- Button:44px min-height,8px radius; отдельные primary/secondary/ghost/danger, hover/active/disabled и3px focus. Убрано декоративное движение hover-иконки. Link/button/disabled semantics сохранены.
- Input/select/textarea: full control-border, surface,44px min; placeholder, disabled, aria-invalid и error focus. Нативная валидация и серверные ошибки не менялись.
- Badge4px и semantic notice backgrounds; base/raised/inset Surface12px; native Dialog16px, ограниченная высота со скроллом и нейтральный scrim; flat cards без тени.
- Shared role=tab underline, настоящий native progress8px с контрастным light fill; theme toggle44px. Конкретные feature nav/control overrides сохраняются до D5–D7.
- Motion tokens120/180/260ms, ease-out(.2,.8,.2,1), ease-in-out(.4,0,.2,1), distance4px. Shared controls без бесконечных циклов/сдвига текста. Existing reduced-motion guard/MotionConfig сохранены. ASCII Scroll и theme-transition choreography не реализованы.

## Локальная демонстрация

Файлы: `frontend/tests/fixtures/design-system/{index.html,main.jsx,demo.css}`. Используются настоящие Button, Badge, Surface, Dialog, ThemeToggle, StudioShared Input/Select/Notice и ThemeProvider; локальные RU/KK/EN тексты явно демонстрационные. Нет API-запросов, аккаунтов, фиктивных продуктовых показателей или нового production route.

Запуск из `frontend/`:

```bash
source "$HOME/.nvm/nvm.sh"
npm run dev -- --host 127.0.0.1 --port 5198 --strictPort
```

Открыть `http://127.0.0.1:5198/tests/fixtures/design-system/`. Обычная production-сборка использует основной index.html, specimen в dist отсутствует. Во время проверки использован отдельный Vite server с cache в /tmp и proxy только на изолированный API8198; рабочий backend не вызывался.

## Визуальные доказательства

Все43JPEG с SHA-256/классификацией и browser-метриками: [verification.json](screenshots/d2/verification.json). Два before,33 component after (30 матрица +2state +1dialog),6 успешных compatibility captures и2 сохранённых диагностических probe, исключённых из успешных доказательств.

| Сравнение | До | После |
|---|---|---|
| Общие компоненты,1440/light | [before](screenshots/d2/before-components-1440-light.jpg) | [after RU](screenshots/d2/after-components-1440-light-ru.jpg) |
| Общие компоненты,1440/dark | [before](screenshots/d2/before-components-1440-dark.jpg) | [after RU](screenshots/d2/after-components-1440-dark-ru.jpg) |
| Mobile KK | D1 относится к полным страницам, не идентичному specimen | [320 dark](screenshots/d2/after-components-320-dark-kk.jpg), [390 light](screenshots/d2/after-components-390-light-kk.jpg) |
| Состояния | — | [light](screenshots/d2/after-states-1440-light.jpg), [dark](screenshots/d2/after-states-1440-dark.jpg) |
| Существующий Studio | D1 baseline сохранён отдельно | [loaded curriculum](screenshots/d2/compat-studio-loaded-1440.jpg) |

Изменения видны в палитре действия/поверхностей, читаемом шрифте, прямой геометрии controls, менее округлых badges/cards, полном контуре полей и различимых status backgrounds. Совпадение страницы пиксель-в-пиксель не является целью, но до/после общего specimen показывает именно shared foundation.

## Проверки и их границы

### Настоящий Chromium

-30 combinations:1440/1024/768/390/320 × dark/light × RU/KK/EN. Проверены html locale/theme, scrollWidth≤viewport, видимые labels/переносы. Программных overflow на specimen нет.
- Tab даёт focus-visible outline3px; стрелка переключает tabs; native Dialog открывается и закрывается Escape. Reduced-motion computed transition0s. Forced pseudo states подтверждают разные hover/active primary fill; disabled/error видны в обеих темах.
- Font cmap/hash tests и CDP platform fonts подтверждают локальные webfonts, а не только CSS family declaration.
- На существующей изолированной SQLite/media C4, синтетическими аккаунтами, настоящий login, home/course/lesson115/assessment116/Profile и Studio curriculum. В Lesson115 обнаружены3 video; первый действительно проигрывался (currentTime>1.7s), error:null,1textTrack. Не выполнялись отправка проекта/quiz, завершение урока, сохранение Studio или выдача сертификата. Это smoke, не повтор полного C4 E2E.
- Ожидаемые404 draft reviews и disabled certificate-status сохранены с прежним нейтральным UI. Нельзя заявлять «ноль404». Первый Studio probe ошибочно использовал slug вместо numeric ID; второй захватил loading раньше времени. Оба сохранены с пометкой excluded-probe; успешный снимок сделан после появления instructor-lesson-list на `/instructor/courses/10/curriculum`.
- Не проверены заново все production pages × theme × locale, screen reader, полный200%zoom и полный submission/review/certificate workflow. Это D8/профильные этапы; автоматические feature regressions запускались.

### Контраст

| Пара | Dark | Light |
|---|---:|---:|
| Body/canvas |17.17:1|15.22:1|
| Secondary/elevated |6.66:1|6.00:1|
| Link/surface |12.93:1|7.90:1|
| On-primary/primary |14.89:1|14.89:1|
| Focus/elevated |10.59:1|5.37:1|
| Control-border/surface |4.90:1|5.03:1|
| Error/error-surface |8.41:1|5.71:1|

Тесты проверяют body/muted/link/accent/status на canvas/surface/elevated≥4.5, focus/control≥3, disabled/status surfaces/primary-hover-active/danger-fill≥4.5, progress≥3. Это WCAG AA-проверка определённых непрозрачных пар, **не сертификат соответствия всего приложения**. Legacy opacity/feature overrides требуют последующего визуального аудита.

### Команды и результаты

Все frontend-команды запускались **из frontend/**:

```bash
source "$HOME/.nvm/nvm.sh"
node --test tests/design-foundations.test.mjs tests/graphite-lime-system.test.mjs
node --test tests/*.test.mjs
npm run lint
npm run build
```

- Полный suite: **431 passed,0failed,0skipped**,44 test files обнаружены. Новый focused suite7/7; существующие12foundation checks сохранены, две Amethyst palette-константы обновлены на реальный контракт, контрастные assertions не удалены.
- Lint:0warnings/0errors после добавления export у demo component. Production build PASS; fixture не включён в dist. Изначальный запуск из корня дал path error (тесты/Vite ожидают frontend cwd), затем выполнен корректно. Из sandbox запуск Chromium/fc-query ограничен, проверки успешно повторены с разрешённым local execution; auto-review rejection не было.
- `PYTHONPATH=/tmp/ai-c4-w408exrp:$PWD DJANGO_SETTINGS_MODULE=settings_c4 .venv/bin/python -B manage.py check`: PASS,0issues. Django application/tests не менялись; весь backend suite в D2 не повторялся.
- `git diff --check`: PASS.
- Impeccable context/craft/document/hooks использованы; hooks status enabled/.agents wired. Нативное автоматическое срабатывание hooks не заявляется. Ручной `impeccable detect frontend/src --json` вернул11existing warnings/advisories (exit2), те же legacy side-stripe/grid решения D1, ни одного в изменённых shared foundation files. Они не подавлены и не объявлены функциональными ошибками. D3/D5–D7 рассматривают их при миграции страниц.
- Нативный `frontend_reviewer` read-only actual diff/cascade/font/contrast и сохранённый320px screenshot: подтверждённых D2 blockers нет. Отдельный worker подготовил только изолированный specimen. Browser assertions выполнил основной агент реальным Chromium, не mock и не reviewer-claim.

## Точные новые/изменённые файлы D2

Application CSS:
- `frontend/src/styles/v2-tokens.css`
- `frontend/src/styles/fonts.css` (new)
- `frontend/src/index.css`
- `frontend/src/components/ui/ui.css`

Fonts/provenance (new):
- `frontend/public/fonts/noto-sans-cyrillic-ext.woff2`
- `frontend/public/fonts/noto-sans-cyrillic.woff2`
- `frontend/public/fonts/noto-sans-latin-ext.woff2`
- `frontend/public/fonts/noto-sans-latin.woff2`
- `frontend/public/fonts/ibm-plex-mono-regular.ttf`
- `frontend/public/fonts/NotoSans-OFL.txt`
- `frontend/public/fonts/IBMPlexMono-OFL.txt`
- `frontend/public/fonts/provenance.json`

Tests/specimen:
- `frontend/tests/design-foundations.test.mjs`
- `frontend/tests/graphite-lime-system.test.mjs` (new)
- `frontend/tests/fixtures/design-system/index.html` (new)
- `frontend/tests/fixtures/design-system/main.jsx` (new)
- `frontend/tests/fixtures/design-system/demo.css` (new)

Documentation/evidence:
- `DESIGN.md` (new)
- `.impeccable/design.json` (new; extensions/snippets для skill, не runtime frontend)
- `docs/design/D2_DESIGN_SYSTEM.md` (new)
- `docs/design/REDESIGN_ROADMAP.md`
- `docs/design/screenshots/d2/*.jpg` и `verification.json` (new; точные43 пути в manifest)
- `docs/project-memory/CURRENT_STATE.md`
- `docs/project-memory/ROADMAP.md`
- `docs/project-memory/DECISIONS.md`

## Сохранность и оставшиеся этапы

Сверены117исходных SHA-256 для рабочей SQLite/settings/protected и public media: **0изменений**. Рабочая SQLite read-only integrity=ok, foreign-key violations0, Course10 is_published=False. Предыдущие D1/memory изменения и все локальные untracked материалы сохранены. Backend, API/session, маршруты, БД, course sources/8/10, media и settings D2 не редактировал. Нет staging/commit/push/merge/reset/cleanup. Тестовые серверы остановлены после QA.

Оставшиеся page-specific размеры, старые SVG/градиенты/stripes и каскадные overrides не равны завершённому Graphite-редизайну. Они явно оставлены D3–D7. Следующий этап — **отдельно разрешённый D3**, главная и один ASCII Scroll; D4 theme transitions не запускать автоматически.
