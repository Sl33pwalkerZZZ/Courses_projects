# D5 — каталог и страницы курсов

Дата: 2026-11-25. Ветка `design/graphite-lime`. Основа: `88a9b85` — принятый владельцем и сохранённый D4. D5 оставлен без staging/commit для визуальной приёмки; D6 не начат.

## Исходное состояние и решение

Каталог повторял обычную трёхколоночную сетку: небольшая графика, длинные названия и действия конкурировали внутри одинаковых вертикальных карточек. Страница курса объединяла крупную рамку hero, декоративную боковую линию, повторную мини-программу, описание и вложенные карточки модулей. Это ослабляло иерархию и повторяло одну информацию.

Владелец подтвердил: сохранить hero/ASCII главной; каталог сделать компактной витриной с горизонтальными карточками; на странице курса — открытый заголовок, самостоятельная панель доступа и читаемая программа без лишнего вложения.

Использован установленный Impeccable: context для CourseDetail, playbook new-work и craft-floor перед редактированием. Независимый native `frontend_reviewer` проверил восемь UI-файлов и реальные Chromium-снимки: блокирующих замечаний нет. Его собственный Playwright MCP не запустил отсутствующий Firefox1578; это не выдаётся за интерактивный browser pass. Отдельный native `browser_qa` использовал установленный Firefox через BiDi. Worker подготовил только временные окружение и fixtures.

## Реализация

- **Каталог:** одна горизонтальная карточка в строке, крупное название, отдельная графическая область, полное API-описание в DOM (визуально до трёх строк), автор, только реальные отзывы, уровень и ясная ссылка открытия. На узком экране графика становится верхней полосой. Цель ссылки не двигается при hover; небольшое движение ограничено стрелкой/внутренним символом.
- **Поиск:** сохранены существующие поиск, направление и уровень, обработчики и локализация. Фильтры собраны в открытую панель с явным сбросом и отдельным результатом/empty/error/retry. Никаких новых неработающих фильтров.
- **Курс:** открытый крупный заголовок и реальные метаданные, автор, навигация по странице. Убраны повторная мини-программа и дублирование описания. Полное описание находится в плотной читаемой поверхности; нет выдуманных learning outcomes.
- **Программа:** единая последовательность модулей с разделителями, комфортнее размер названий и уроков. Сохранены реальный порядок, раскрытие, Expand all, связанные `aria-controls`, скрытые/inert панели и запрет ссылок без подтверждённого доступа.
- **Доступ:** отдельная стеклянная панель, sticky только там, где хватает высоты/ширины. На мобильном она появляется перед описанием; формы и действия остаются полностью доступны. Сохранены все прежние открытое зачисление/заявка/ожидание/продолжение/ошибки.
- **Назад:** ссылка возвращает непосредственно к `/#course-library`, а не к началу hero.

Публичный API не содержит обложку, отдельный список результатов обучения или publication badge. Новая обложка — оригинальная декоративная SVG-геометрия, а не изображение курса или интерфейс программы; она скрыта от accessibility tree. Использованы уже установленные React/Motion/Lucide и локальные шрифты, без новых зависимостей и внешних ассетов. Действующие семантические токены Obsidian/Frost/Aqua, B-material карточек/доступа и D-material чтения сохранены. Hero/ASCII, liquid background, D4 ThemeProvider и темы не переписывались.

## Адаптивность и доступность

1440: графика карточки260px, текст занимает остальную ширину; программа и панель доступа разделены. До900 графика190px; до600 — вертикальная карточка. На850 и ниже access/описание/программа идут в одну колонку; sticky отключён. До600 поиск занимает всю строку, два select стоят рядом, а сброс — отдельной строкой: меньше прокрутки до первого курса. Длинные заголовки переносятся без обрезания; поля на телефоне сохраняют16px.

Сохранены одна именованная ссылка на карточку, явные labels полей, keyboard focus и клавиатурный аккордеон. Все новые подписи используют существующие RU/KK/EN ключи, новых непереведённых строк нет. Используются проверяемые семантические цвета; автоматические contrast-тесты проходят. Полная гарантия контраста всех динамических композиций стекла не заявляется. Reduced-motion отключает добавленные micro-transitions; D4 остаётся существующим механизмом.

## Окружение и проверки

Настоящие Vite `http://127.0.0.1:5205` и Django `http://127.0.0.1:8205`, отдельная SQLite и media/public-media в `/tmp/ai-d5-umm15ffq`. API-прокси и фактический преобразованный `api.js` проверены: только `/api`→8205, не рабочий8000. Учётные записи синтетические; секреты не включены в отчёт. Исходные данные пользователей в копии обезличены. Рабочая БД не используется для записей.

### Автоматические команды

Из `frontend/` после `source "$HOME/.nvm/nvm.sh"`:

```bash
node --test tests/public-catalog.test.mjs tests/course-detail.test.mjs tests/course-errors.test.mjs
node --test tests/*.test.mjs
npm run lint
npm run build
```

Из корня:

```bash
.venv/bin/python manage.py check
git diff --check
```

Результаты: **43/43 initial focused, 466/466 полный suite; после последней мобильной CSS-правки55/55 focused (добавлен design-foundations), 0 failed/skipped; lint exit0; build exit0; Django check0 issues; whitespace exit0.** Первоначальный запуск из корня неверно разрешал Vite SSR `/src`, исправлен рабочий каталог, не приложение. Шесть прежних ожиданий возврата к `/` уточнены до реального каталога `/#course-library`; проверки ошибок/404/повтора сохранены. Добавлены три локализованных теста длинного текста/декоративной графики без выдуманных данных и тест полной доступной программы6/16 без выдуманного прогресса.

Backend/API не изменены, новые Django тесты и миграции не требуются. Доступ дополнительно проверяется настоящим изолированным API и браузером, не mock API.

### Browser evidence

| Проверка | Фактический результат |
|---|---|
| Chromium: каталог + Course8 | 48 комбинаций:1440/768/375/320 × light/dark × RU/KK/EN; фактическая тема проверена, overflow/выходящих контролов0 |
| Финальные мобильные фильтры Chromium | Ещё4 случая375/320 × light/dark после уплотнения; без overflow |
| Chromium: реальные интеракции | Поиск, level, сброс, empty, Enter на модуле, back/forward; D4 сохраняет поиск/раскрытие; reduced-motion подтверждён |
| Chromium: focus | Реальный Tab переводит на SELECT, `:focus-visible=true`, outline3px |
| Изолированный Course10 | Студент:6 модулей/16 ссылок, expand all работает; outsider и обычный admin detail404, без утечки программы; admin Studio preview доступен |
| Изолированное зачисление через UI | Только синтетический QA course12: outsider open→POST201→Continue→урок117; student approval→мотивация→POST201→pending после reload. Mobile390 dark EN без overflow. После проверки QA-курс снова скрыт |
| Loading/empty/error/retry | Только явно изолированные browser fixtures: задержка ответа/skeleton, пустой200, принудительный503→Retry→настоящий API200. Это не реальные сбои сервера |
| Отзывы | Настоящий публичный API; после прокрутки normal и reduced блок видим. Пустая область на раннем full-page capture объясняется ещё не сработавшим существующим Reveal, не потерей отзывов |
| Firefox143, native BiDi | 16 окончательных actual-DOM случаев:2 страницы ×4 ширины ×2 темы, RU1440/320, KK768, EN375. Reduced-motion включён штатным preference только во временном профиле. Actual theme/lang/reduced проверены; overflow0, public lesson links0 |
| Финальные мобильные фильтры Firefox | Ещё2 случая375 light RU/320 dark RU. Select рядом, без пересечений; первый курс на744px при высоте1000. Длинный default внутри узкого native select сокращён, полностью доступен в popup |
| Firefox: тема/клавиатура | Тема сохраняет закрытый модуль и URL. BiDi Tab перевёл focus, но не активировал `:focus-visible`; ручная проверка кольца Firefox остаётся открытой, это не объявлено подтверждённым CSS-дефектом |

Chromium: pageerrors0, запросов к8000 —0. Firefox: console error0, HTTP>=400 —0 в публичной матрице;9 `NS_BINDING_ABORTED` — отменённые запросы CourseDetail при StrictMode/навигации. Ожидаемые404 для запрещённого draft доступа проверены отдельно. Первые harness-прогоны с fixed-light initScript (Chromium), hash-only navigation/фиксированной задержкой (Firefox) отброшены; окончательные результаты учитывают только загрузившийся контент и фактические темы/языки.

Нормальные Firefox desktop captures просмотрены до reduced-прогона; окончательная комбинаторная Firefox-матрица выполнена с reduced-motion. Равенство native Chromium reveal и Firefox fallback или sustainedFPS не заявляется.

Доказательства без токенов, cookies и raw network headers: [browser-evidence.json](screenshots/d5/browser-evidence.json).

### Скриншоты

Одинаковые маршруты и ширина1440; `before` — исходные full-page снимки, `after` — сопоставимые viewport-фрагменты. Дополнительная программа снята после настоящей прокрутки. Это визуальное сравнение, не pixel-diff с одинаковым scroll offset.

| Экран | До | После |
|---|---|---|
| Каталог light1440 | [до](screenshots/d5/before-catalog-1440-light.png) | [после](screenshots/d5/after-catalog-1440-light.png) |
| Каталог dark1440 | [до](screenshots/d5/before-catalog-1440-dark.png) | [после](screenshots/d5/after-catalog-1440-dark.png) |
| Course8 light1440 | [до](screenshots/d5/before-course8-1440-light.png) | [после](screenshots/d5/after-course8-1440-light.png) |
| Course8 dark1440 | [до](screenshots/d5/before-course8-1440-dark.png) | [после](screenshots/d5/after-course8-1440-dark.png) |

Mobile375: [каталог light](screenshots/d5/after-catalog-375-light.png), [dark](screenshots/d5/after-catalog-375-dark.png), [курс light](screenshots/d5/after-course8-375-light.png), [dark](screenshots/d5/after-course8-375-dark.png). [Программа1440 dark](screenshots/d5/after-curriculum-1440-dark.png).

Остальные исходные QA captures находятся в `/tmp/d5-qa/`, `/tmp/d5-final-shots/`, `/tmp/d5-firefox/`; это временные локальные материалы, не proposed production assets.

## Сохранность

Повторно проверены SHA-256 всех117 исходных защищаемых файлов: `db.sqlite3`, `config/settings.py` и115 файлов `media/`; совпадают с preflight. SQLite read-only: integrity `ok`, FK violations0, Course10 `is_published=0`. Course8/content/media, сертификатные настройки и рабочие пользовательские записи не изменялись. Frontend recovery copy создана только в `/tmp/ai-d5-safety-_nnb95ya`.

HEAD остаётся `88a9b85`, ветка `design/graphite-lime`, index пуст. Намеренная локальная правка `config/settings.py` сохранена байт-в-байт. Итоговый `git status -sb`:15 tracked D5 изменений + прежняя локальная правка настроек; новые D5 report и evidence directory. Все59 ранее существовавших untracked status entries сохранены; отсутствующих исходных путей0. Targeted scan16 текстовых файлов на private-key/AWS-key/JWT сигнатуры:0 находок.

Ранее существовавшие untracked пути сохранены; добавлены только D5 отчёт и выбранные доказательства, кроме перечисленных tracked D5 изменений. Никаких staging/commit/push/merge/reset/cleanup не выполнялось.

## Точный предлагаемый набор коммита

Ни одна команда staging/commit не выполнена. Только после визуальной приёмки:

```text
frontend/src/components/CourseCard.jsx
frontend/src/components/CourseCard.css
frontend/src/components/CourseCurriculum.jsx
frontend/src/components/CourseCurriculum.css
frontend/src/pages/CourseCatalog.jsx
frontend/src/pages/CourseCatalog.css
frontend/src/pages/CourseDetail.jsx
frontend/src/pages/CourseDetail.css
frontend/tests/public-catalog.test.mjs
frontend/tests/course-detail.test.mjs
frontend/tests/course-errors.test.mjs
docs/design/D5_CATALOG_COURSE_REDESIGN.md
docs/design/REDESIGN_ROADMAP.md
docs/project-memory/CURRENT_STATE.md
docs/project-memory/DECISIONS.md
docs/project-memory/ROADMAP.md
```

Дополнительно предлагаются13 выбранных PNG и1 компактный evidence JSON (всего около3.2MB; без видео, профилей браузеров или raw HTTP логов):

```text
docs/design/screenshots/d5/after-catalog-1440-dark.png
docs/design/screenshots/d5/after-catalog-1440-light.png
docs/design/screenshots/d5/after-catalog-375-dark.png
docs/design/screenshots/d5/after-catalog-375-light.png
docs/design/screenshots/d5/after-course8-1440-dark.png
docs/design/screenshots/d5/after-course8-1440-light.png
docs/design/screenshots/d5/after-course8-375-dark.png
docs/design/screenshots/d5/after-course8-375-light.png
docs/design/screenshots/d5/after-curriculum-1440-dark.png
docs/design/screenshots/d5/before-catalog-1440-dark.png
docs/design/screenshots/d5/before-catalog-1440-light.png
docs/design/screenshots/d5/before-course8-1440-dark.png
docs/design/screenshots/d5/before-course8-1440-light.png
docs/design/screenshots/d5/browser-evidence.json
```

Итого предлагаемый D5 набор: **30 файлов —16 source/test/documentation +14 evidence**. Это план, не выполненный staging.

Не включать `config/settings.py`, SQLite, `/tmp` окружения/учётные данные, media, backups, node_modules, остальные ранее существовавшие untracked файлы и чужие production outputs. PRODUCT/DESIGN не переписаны: утверждённая система не менялась.

## Личная приёмка владельца и ограничения

Открыть `http://127.0.0.1:5205/#course-library`, затем реальный публичный курс. Сравнить светлую/тёмную темы, поиск/сброс, длинные названия, мобильную вертикальную карточку и панель доступа. В Course10 нужен разрешённый синтетический студент; реальный курс остаётся черновиком. Никаких реальных заявок, уроков, работ, оценок или сертификатов этот этап не меняет.

Firefox headless/SWGL не доказывает качество аппаратного backdrop blur; требуется визуальная оценка владельцем в обычном Firefox. Новая геометрия направлений имеет общий орбитальный мотив — это сознательно компактная система, не уникальные иллюстрации содержания каждого курса. Новых FPS-гарантий или исправления прежнего sustained24FPS ограничения не заявляется. Удалённый deploy не выполнен; preview временный локальный.
