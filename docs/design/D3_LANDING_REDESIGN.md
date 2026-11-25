# D3 — композиционный редизайн главной

Дата: **2026-11-25**, Asia/Almaty. Ветка `design/graphite-lime`, исходный и итоговый HEAD `bc05bef`. Изменения не staged, не committed. D4–D8 не начаты. Владелец подтвердил сценарий: новичок понимает продукт и переходит к доступным курсам; ASCII — «информация → структура → практика», без имитации встроенного ИИ.

## Результат и личный просмотр

Главная переработана композиционно, а не перекрашена. Изолированный preview оставлен для владельца: **http://127.0.0.1:5198/**, настоящий Django API на8198 использует отдельную SQLite-копию в `/tmp/ai-d3-ce_wxhq1/`, отдельные media paths и локальный cache. Рабочая БД браузером не обслуживалась. Это временное dev-окружение, не публикация/деплой; после перезапуска процесса URL может перестать отвечать.

Чтобы посмотреть код обычным frontend dev server: из `frontend/` выполнить `source "$HOME/.nvm/nvm.sh"`, затем `npm run dev`. Это использует обычную конфигурацию проекта; для изолированной проверки использован отдельный временный Vite config с `/api` proxy только на8198. Не выполнять через preview реальные заявки/отправки/публикацию.

**Независимый визуальный verdict: `ship`**, по13переданным реальным screenshots и проверенным исходникам. Это не личная приёмка владельца и не новый полный продуктовый E2E. Следующий шаг — оценка D3 владельцем; только после отдельного разрешения D4.

## Что изменилось в композиции

| Было D1/D2 | Стало D3 |
|---|---|
| Обрамлённый hero с курсом в наклонённой карточке, орбитами и частицами | Открытый асимметричный первый экран: крупная типографика слева, отдельная ASCII-скульптура справа |
| Дублирующий showcase/preview курса перед каталогом | Одна ясная история без повторного показа того же курса |
| Несколько конкурирующих motion-блоков и отдельная SignalStory | Один scroll-визуал; обычный контент не скрывается reveal-анимацией |
| Процесс обучения в одинаковых карточках | Открытая последовательность из трёх шагов, с реальными условиями зачисления |
| Разрозненные декоративные секции | Hero → обучение → доступные курсы → начало работы |
| Два UI выбора направления | Сохранён существующий select, дублирующие direction-chips убраны; глубокий redesign фильтров/карточек оставлен D5 |

Новый hero содержит один h1 «Изучайте ИИ. Создавайте своё.», короткое описание, основной anchor в каталог и вторичный переход к процессу. Нет kicker/badge над заголовком, вымышленных чисел, партнёров, отзывов или обещания встроенного генератора. На всех24top-captures primary action помещается в первый viewport (измеренный bottom374–752px при высоте844/1000px).

Навигация сохраняет каталог, login/register, Profile, Studio и logout по прежним условиям. В Header изменён только route-scoped class, обработчики и role/auth logic не менялись. Header главной спокойнее по оформлению; mobile dialog/языки/theme controls сохранены. Каталог по-прежнему использует `/courses/`, локальные фильтры, реальные loading/error/empty и прежние CourseCard. CourseDetail, уроки, Profile и Studio не редизайнились.

## ASCII Scroll

**Оригинальная геометрия: разрозненная информация собирается в многослойный пространственный куб, затем в упорядоченное «фолио» страниц.** Текстовая подпись объясняет метафору; визуал не изображает работающий AI-продукт и не заменяет образовательный контент.

-620детерминированных sample points, сетка72×44; часть читаемого ядра видна уже в начале. Реальная progress от координаты hero относительно viewport, ограниченная0..1. Нет autoplay timeline, wheel/touch interception или обязательного прохождения сцены ради доступа к каталогу.
- Одна Canvas2D-сцена, IBM Plex Mono, цвет `--v2-text`; DPR capped1.5. Один RAF только по dirty scroll/resize/theme/font/visibility event, без непрерывного idle-loop.
- IntersectionObserver останавливает перерисовку вне viewport; document.hidden guard и cleanup RAF/listeners/observers сохраняют lifecycle/StrictMode. Источник размеров — ResizeObserver. Смена темы вызывает redraw, но не добавляет D4 transition.
- Mobile≤767px, reduced-motion и SSR используют статичный `<pre>`; no-canvas также сохраняет видимый fallback. CSS container units подгоняют glyph grid по обеим осям; fallback line-height согласован с Canvas-ячейкой, чтобы не обрезать фигуру на мобильном.
- Иллюстрация `aria-hidden`, не ловит pointer/focus; h1/описание/actions и текстовые этапы — обычный DOM. Текст и визуал находятся в отдельных колонках, не перекрываются.
- Первый прототип уточнён после просмотра: больше узнаваемого ядра в начальном состоянии, final morph завершается пока фигура ещё видна, статичный fallback больше не вытянут/обрезан. Промежуточные2кадра сохранены как intermediate, не как final evidence.

Проверенные desktop scroll-позиции: y0 → progress0.000, y190 →0.433, y400 →1.000, в обеих темах. Сцена естественно уходит вместе с hero; нет второй конкурирующей scroll-анимации ниже.

## Референсы и лицензии

Изучены официальные страницы/документация, а не скопированы сайты:

- [Linear](https://linear.app/): краткое предложение и крупный доказательный visual. Для AI Courses — одна образовательная метафора вместо симуляции чужого UI.
- [Vercel](https://vercel.com/): ясное разделение тезиса, продукта и действий; не переносились инфраструктурные claims/метрики.
- [React Bits](https://reactbits.dev/): один настраиваемый эффект вместо наложения нескольких backgrounds. [Текущая лицензия](https://raw.githubusercontent.com/DavidHDev/react-bits/main/LICENSE.md) — **MIT + Commons Clause**, не plain MIT; код/ассеты не импортировались.
- [ascii.rest](https://ascii.rest/), [MIT license](https://raw.githubusercontent.com/bas3line/ascii/main/LICENSE): читаемая символная геометрия. Art/code не копировались.
- [ASCII Things](https://ascii-things.dev/library/), [официальный репозиторий](https://github.com/chuma-beep/ascii-things): lifecycle/pause/determinism как предмет изучения; репозиторий declares MIT, реализации/сцены не заимствованы.

**Новых npm-зависимостей нет.** Использованы существующие React, CSS, lucide-react и API/i18n/theme architecture. Canvas/observer — браузерные API; новый WebGL/3D stack не нужен. Motion сохраняется в приложении/существующих карточках, новая ASCII-сцена работает без дополнительной библиотеки.

Playwright MCP подключён, но его настроенный Firefox отсутствует; установка не выполнялась. Референсы изучены через официальные HTML/docs/repositories, **не заявляется их rendered-browser QA**. Собственное приложение реально проверялось установленным Chromium через существующий Remotion browser driver/CDP; видео не рендерились.

## Визуальные доказательства

[Точный inventory/размеры/SHA-256 и browser metrics](screenshots/d3/verification.json):40JPEG (38final +2intermediate),2grayscalePNG. Baseline D1/D2 не изменены. Новая попытка before-capture упёрлась в sandbox до навигации; она не выдана за baseline. Для сравнения используются существующие реальные D1/D2 снимки, композиция которых совпадает с pre-D3 кодом.

| Вид | Before | After |
|---|---|---|
|1440light|[D2 главная](screenshots/d2/compat-home-1440.jpg)|[RU](screenshots/d3/after-1440-light-ru.jpg)|
|1440dark|[D1](screenshots/d1/home-1440-dark.jpg)|[RU](screenshots/d3/after-1440-dark-ru.jpg)|
|Монохромное сравнение|[D2 grayscale](screenshots/d3/baseline-d2-home-gray.png)|[D3 grayscale](screenshots/d3/after-home-gray.png)|
|768|[D1 audit](D1_VISUAL_AUDIT.md)|[KK/light](screenshots/d3/after-768-light-kk.jpg)|
|390|[D1 mobile](screenshots/d1/home-390-light.jpg)|[RU/light](screenshots/d3/after-390-light-ru.jpg),[KK/dark](screenshots/d3/after-390-dark-kk.jpg)|
|320|—|[EN/light](screenshots/d3/after-320-light-en.jpg),[RU/dark](screenshots/d3/after-320-dark-ru.jpg)|
|Scroll|—|[information](screenshots/d3/ascii-information-light.jpg),[structure](screenshots/d3/ascii-structure-dark.jpg),[practice](screenshots/d3/ascii-practice-light.jpg)|
|Остальная композиция|—|[workflow](screenshots/d3/workflow-light.jpg),[catalog](screenshots/d3/catalog-light.jpg),[closing](screenshots/d3/closing-dark.jpg)|
|Fallback/navigation|—|[reduced motion](screenshots/d3/reduced-motion-1440.jpg),[mobile menu](screenshots/d3/mobile-menu-390.jpg)|

Сравнение без цвета показывает смену topology: исчезли framed hero/карточка/орбиты; заголовок, свободное поле и крупная скульптура теперь формируют первый экран. Это также подтвердил независимый reviewer, а не только автор реализации.

## Фактически выполненные проверки

### Настоящий Chromium + реальный Django

-24top-viewport combinations:1440/768/390/320 ×light/dark×RU/KK/EN. Locale/theme и static/scroll mode проверялись в DOM; scrollWidth≤viewport; headings/visual columns не перекрываются. Шесть дополнительных scroll keyframes в обеих темах.
- Primary anchor прокручивает к каталогу, не требуя interaction с ASCII. API `/api/courses/` реально ответил200,1publiccourse; rendered card count совпал. Заголовок фактического публичного курса: «Как выбрать нейросеть под свою задачу». Course10 не появился как опубликованный.
- Idle draw count12→12, offscreen13→13 при дополнительном скролле: нет постоянного RAF. Reduced-motion переключает режим на static. Keyboard Tab: focus-visible3px; mobile menu открывается и закрывается Escape.
- Geometry microbenchmark100frames: около0.15ms/frame в этом прогоне/окружении. Это **только pure geometry**, не обещание60FPS на любом устройстве и не измерение общего LCP/INP/paint cost.
- JavaScript runtime errors в проверочном прогоне:0. Браузерные проверки не подменялись mock API. Protected student/instructor mutations, progress completion, quiz submission и сертификаты заново не выполнялись — это не новый C4 E2E.

### Автоматические команды

Из `frontend/` после `source "$HOME/.nvm/nvm.sh"`:

```bash
node --test tests/ascii-learning.test.mjs tests/graphite-landing.test.mjs tests/public-catalog.test.mjs
node --test tests/*.test.mjs
npm run lint
npm run build
```

- Focused: **23passed,0failed**. Новые7tests: детерминированность/границы/scroll-геометрия, breathing room; RU/KK/EN narrative/actions/SSR fallback и pinned normalized license/upstream provenance.
- Full: **438passed,0failed,0skipped**. Сохранены session/grant/Studio/assignment/quiz/certificate regressions. Старый hero test теперь проверяет новый контракт (не дублировать catalog и не выдумывать progress), а assertions title/actions/i18n/contrast сохранены. В public-catalog исправлен только устаревший regex `<li `: теперь учитывает `<li>` без атрибутов, по-прежнему требует3шага и прежнее conditional-enrollment explanation. Первый полный прогон обнаружил именно эти3locale failures; исправление проверено повторным полным suite.
- Lint: **0warnings/0errors**. Production build PASS. Backend source/API contract не менялись.
- Из корня: `PYTHONPATH=/tmp/ai-d3-ce_wxhq1:$PWD DJANGO_SETTINGS_MODULE=settings_d3 .venv/bin/python -B manage.py check` — PASS,0issues. `git diff --check` — PASS.
- Sandbox сначала запрещал localhost listeners/Chromium/fc-query; после разрешённого execution проверки выполнены. Это не platform approval rejection и не обход ограничений. Один запуск тестов без нужного execution permission дал fc-query EPERM; успешные результаты выше относятся к корректному повтору.

### Impeccable и независимая оценка

- Прочитаны context, new-work, craft floor, D1/D2/PRODUCT/DESIGN/project-memory. Hooks enabled, `.agents` wired; нативное автоматическое срабатывание не утверждается. Ручной detector выполнен:11legacy findings, ни одного в новом landing/shared change; без blanket suppression. Старые неиспользуемые CSS/art не удалялись ради нулевого detector count.
- Native `browser_qa` дал независимый source/reference/license обзор; честно сообщил об отсутствии MCP Firefox. Worker подготовил только оригинальную ASCII implementation/tests. Native `frontend_reviewer` запущен свежим без истории реализации:13снимков/код/нормативные документы, disposition **ship**, material fixes:none. Не заявлял собственных browser interactions.
- Остаточное замечание reviewer: на320–390light символы тонкие и воспринимаются прежде всего как dotted silhouette. Это некритичный предел mobile static adaptation, не clipping и не повод добавлять конкурирующий эффект. Сильнейшее выражение identity — desktop. Владелец ещё должен лично оценить результат.
- DESIGN.md и существующий untracked `.impeccable/design.json` не переписывались: D3 использует систему D2, а не меняет её world/tokens. Обнаруженный skill setup drift не исправлялся как побочный эффект.

## IBM Plex Mono license

`frontend/public/fonts/IBMPlexMono-OFL.txt`: CRLF→LF, trailing spaces/лишние terminal newlines убраны.4456→4362bytes. До записи сравнение whitespace-token sequence подтвердило неизменность слов лицензии. В provenance сохранены исходные `upstream_sha256`/size и записаны normalized local SHA/size/метод. Тест pin-ит нормализованный текст и upstream identity; остальные font hash tests также проходят. Все5бинарных TTF/WOFF2 совпадают с HEAD, не модифицированы.

## Точные изменённые/новые файлы

Application/translation:
- `frontend/src/pages/CourseCatalog.jsx`
- `frontend/src/components/Header.jsx`
- `frontend/src/components/HomeHero.jsx`
- `frontend/src/components/HomeHero.css`
- `frontend/src/components/LearningWorkflow.jsx`
- `frontend/src/components/landing/ClosingInvitation.jsx`
- `frontend/src/components/landing/AsciiLearning.jsx` (new)
- `frontend/src/components/landing/AsciiLearning.css` (new)
- `frontend/src/utils/asciiLearning.js` (new)
- `frontend/src/styles/graphite-landing.css` (new)
- `frontend/src/i18n/locales/ru.json`
- `frontend/src/i18n/locales/kk.json`
- `frontend/src/i18n/locales/en.json`

License/tests:
- `frontend/public/fonts/IBMPlexMono-OFL.txt`
- `frontend/public/fonts/provenance.json`
- `frontend/tests/design-foundations.test.mjs`
- `frontend/tests/public-catalog.test.mjs`
- `frontend/tests/ascii-learning.test.mjs` (new)
- `frontend/tests/graphite-landing.test.mjs` (new)

Documentation:
- `docs/design/D3_LANDING_REDESIGN.md` (new)
- `docs/design/REDESIGN_ROADMAP.md`
- `docs/project-memory/CURRENT_STATE.md`
- `docs/project-memory/ROADMAP.md`
- `docs/project-memory/DECISIONS.md`
- `docs/design/screenshots/d3/`:42images +verification.json; каждый путь/хеш перечислен в manifest.

## Безопасность и границы

117исходных SHA-256 рабочей SQLite/settings/protected/public media совпадают. Read-only live integrity=ok, FK violations0, Course10 is_published=False. Course8 и Course10/канонический контент/реальные медиа не изменялись. Не менялись authentication/session/grants/permissions, endpoints/routes, прогресс, оценивание, сертификаты или их настройки. `config/settings.py` остаётся прежней локальной правкой, не частью D3. Git index пуст; HEAD/ветка сохранены. Нет staging/commit/push/merge/reset/cleanup и удаления старых файлов.

**Осталось:** личная визуальная оценка владельца, затем отдельное решение о D4. Полная mobile-device/screen-reader/performance/защищённая product E2E-матрица остаётся D8; этот этап не заявляет её повтор. D4 theme transitions и D5 глубокий catalog/card redesign не выполнялись.
