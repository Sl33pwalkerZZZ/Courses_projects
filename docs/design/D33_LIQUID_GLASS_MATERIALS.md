# D3.3 — Genuine Liquid Glass Materials

Дата:2026-11-25. Ветка `design/graphite-lime`, HEAD `bc05bef`. Статус: реализация и техническая проверка завершены; личная визуальная приёмка владельца ожидается. D4 не начат. Продолжена существующая незакоммиченная D3–D3.2 работа, без отката композиции.

## Решение и исходные ограничения

Владелец подтвердил разделение: прозрачные оболочки, карточки и навигация; более плотные учебный текст, оценивание и поля. Obsidian/Frost/Aqua, liquid field, ASCII, оптическая скульптура авторизации и Studio shell сохранены.

Четыре изображения доступны в запросе только как текстовые описания, сами bitmap-референсы в доступном контексте отсутствуют. Поэтому прямое визуальное сравнение с ними не заявляется. `https://freefrontend.com/css-liquid-glass/` повторно вернул403. Код примеров не заимствован; лицензия неполученного кода не предполагалась.

Браузерный аудит обнаружил слишком плотные68/72% поверхности, непрозрачные Course/Profile/reading области, повторные backdrop filters в Studio. Видимый фон и спокойная читаемая иерархия важнее увеличения количества эффектов.

## Материалы

| Роль | Dark | Light | Обработка и назначение |
|---|---|---|---|
| A Workspace |18,28,40 /38%|250,252,254 /38%|blur18px/saturate118%; единая оболочка Studio, hero |
| B Frost |18,28,40 /48%|250,252,254 /48%|blur14px на самостоятельных панелях; внутри A только tint и specular |
| C Optical |18,28,40 /28%|255,255,255 /28%|небольшой floating header backplate; оригинальная edge displacement |
| C fallback |18,28,40 /68%|250,252,254 /64%|Firefox/mobile/reduced: более плотный tint, supported blur12px, мягкий край |
| D Reading |18,28,40 /96%|250,252,254 /96%|учебный текст, таблицы, оценивание, поля, диалоги |

Основные цвета остаются Obsidian `#0B1017`, Frost `#EEF2F5`, Aqua dark `#78DCD5`/light `#167D85`. Второстепенный текст на прозрачных материалах усилен до dark `#C2D1DD`/light `#344D60`. Тонкая светлая кромка и верхний specular формируют глубину без glow. Вложенные панели Studio не создают повторные backdrop roots. В проверенных экранах Studio обнаружены два main-фильтра: общая рабочая область и боковая навигация; строки и внутренние карточки дополнительных фильтров не получают.

Формы, lesson tables, assessment и длинный текст не превращены в прозрачную декоративную сцену. Без поддержки backdrop-filter сначала применяется непрозрачный fallback. Существующие focus, dropdown/dialog semantics, theme persistence и permission flow сохранены.

## Настоящая оптика и совместимость

`glassOptics.js` строит оригинальную статическую128×128 RGBA карту нормалей: нейтральный центр, направленные R/G градиенты у края. `GlassOptics.jsx` создаёт карту один раз и общий SVG `feDisplacementMap` scale14. Применение — только псевдоэлемент header: текст, кнопки и ссылки не фильтруются. Никаких feTurbulence, сторонних изображений, внешних запросов или новых библиотек.

Enhancement включается только на desktop Chromium с>4 logicalCPU, без reduced-motion. Это ограниченный проверенный visual allowlist, не гарантия поддержки произвольного движка. Остальные браузеры получают намеренный frost fallback.

На **одном статическом тестовом фоне**, при одинаковых tint и blur, production-карта в Chromium дала среднюю абсолютную разницу RGB13.816/255 light и13.844/255 dark относительно blur-only. Это пиксельное подтверждение реального искажения, а не проверка CSS.supports. Лабораторный диагональный фон — измерительный оригинальный паттерн, не экран платформы.

Firefox143.0.3 проверен нативным WebDriver BiDi. В headless SWGL даже обычное backdrop blur не было визуально подтверждено в контрольном тесте, хотя computed CSS его принимает. Подтверждены читаемый tint/edge fallback, темы, layout и reduced-motion; **эквивалентность оптики Chromium и Firefox не заявляется**. Нужна личная проверка аппаратного Firefox владельца. См. [MDN backdrop-filter](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/backdrop-filter), [Mozilla issue1995195](https://bugzilla.mozilla.org/show_bug.cgi?id=1995195); результат конкретного окружения описан отдельно от общей поддержки стандарта.

## Реальная браузерная проверка

Использованы настоящие Vite5199 и Django8199, SQLite/media в `/tmp`, синтетические аккаунты, без mock API. Исходные пользовательские данные тестовой копии обезличены; пароли/токены не включены в доказательства.

- Chromium: первоначальная расширенная матрица26 случаев; финальная22 случая после локального исправления foreground CTA. Главная/вход/регистрация, Studio overview/curriculum/editor, Profile, course detail, lessons113/115. Light/dark,1440/768/390/320, RU/KK/EN, reduced-motion. В финальной матрице нет pageerror и горизонтального overflow.
- Защищённое видео115: play → seek8s → ожидание seeked → текущая позиция9.19043s, readyState4, WebVTT `showing`, без media error. Это тест изолированного синтетического студента, не реального аккаунта.
- Каталог проверен на реальном `/#course-library`, затем footer обеих тем. Bare `/courses` не использован как доказательство существующего каталога. При принудительном scrollIntoView верх заголовка может уходить под sticky header — существующая особенность якорной навигации, вне материального изменения; не скрыта как идеальная композиция.
- Клавиатура: Tab даёт видимый solid outline; ввод в поле логина работает. Сохранение/dirty-editor функционально проверялись D3.2; D3.3 не повторяет полный authoring E2E и не заявляет повторную проверку каждой операции.
- Firefox:12 реальных публичных экранов home/login/register ×1440lightRU,1440darkEN,768lightKK,390darkRU. Тема/язык соответствуют, optics=frost, overflow нет. Отдельно normal/reduced обе темы в material fixture. Reduced login: media preference true, liquid static, один draw.
- Авторизованные Studio и защищённое видео в Firefox **в этом проходе не проверены**; Chromium evidence не подменяет их.

## Производительность и доступность

Новый filter не имеет RAF и не пересоздаёт карту каждый кадр. Mobile/reduced/≤4CPU исключены из SVG-enhancement. Существующие hidden/offscreen/reduced ограничения liquid и ASCII сохранены.

100 вычислений `createLiquidPixels(160×100)` в Chromium: median2.70ms, p954.10ms. Это CPU-компонент генерации, без canvas upload/compositing; не доказательство итоговых24FPS. Ранее D3.2 headless показывал8–13draws/s. Sustained FPS, батарея, аппаратный GPU и low-end телефон в D3.3 не измерены. Уменьшение повторных фильтров предпочтено добавлению тяжёлого renderer.

Автотест проверяет AA для основных/усиленных muted foreground на консервативных composited A/B/D парах. Это не полная сертификация WCAG всех пикселей интерфейса. Focus не фильтруется, поля плотные, reduced-motion статичен в обоих браузерах. В ходе финального просмотра устранено локальное переопределение цвета header CTA: белый текст на light Aqua, тёмный на dark Aqua.

## Проверки

Команды frontend выполнялись из `frontend/`, Node из существующего NVM:

- `node --test tests/*.test.mjs`:452 passed,0 failed,0 skipped.
- `node --test tests/auth-design.test.mjs tests/glass-materials.test.mjs tests/liquid-glass.test.mjs tests/studio-shell-design.test.mjs`: финальные focused23 passed,0 failed.
- `npm run lint`:PASS; `npm run build`:PASS.
- `PYTHONPATH="<isolated-settings-dir>:$PWD" DJANGO_SETTINGS_MODULE=settings_d32 .venv/bin/python -B manage.py test courses.test_video studio.test_section_creation studio.test_attachment_placement studio.test_publication_readiness --noinput`:36 passed, отдельная test DB,0 system-check issues.
- `git diff --check`:PASS. Index пуст, staging/commit не выполнялись.
-117 SHA-256 рабочей SQLite, settings и защищённых медиа совпадают с pre-D3.3; SQLite integrity=ok, FK violations=0, Course10.is_published=0. Секреты и содержимое пользовательских файлов не публиковались.

## Скриншоты и независимые проверки

Все доказательства: `docs/design/screenshots/d33/`.

| Экран | До D3.3 | Финальный D3.3 |
|---|---|---|
| Home light |[before](screenshots/d33/before-home-1440-light.png)|[final](screenshots/d33/final-home-1440-light.png)|
| Home dark |[before](screenshots/d33/before-home-1440-dark.png)|[final](screenshots/d33/final-home-1440-dark.png)|
| Login light |[before](screenshots/d33/before-login-1440-light.png)|[final](screenshots/d33/final-login-1440-light.png)|
| Login dark |[before](screenshots/d33/before-login-1440-dark.png)|[final](screenshots/d33/final-login-1440-dark.png)|
| Register light |[before](screenshots/d33/before-register-1440-light.png)|[final](screenshots/d33/final-register-1440-light.png)|
| Register dark |[before](screenshots/d33/before-register-1440-dark.png)|[final](screenshots/d33/final-register-1440-dark.png)|
| Studio light |[before](screenshots/d33/before-studio-1440-light.png)|[final](screenshots/d33/final-studio-1440-light.png)|
| Studio dark |[before](screenshots/d33/before-studio-1440-dark.png)|[final](screenshots/d33/final-studio-1440-dark.png)|

`after-*` — промежуточная расширенная матрица до последнего CTA fix; для приёмки использовать `final-*`. JSON: `chromium-materials.json`, `chromium-final.json`, `interaction-check.json`, `firefox-app-public.json`, `material-chromium-probe.json`, `material-firefox-{normal,reduced}.json`, `independent-optical-notes.json`. Before сняты до изменений материалов. Анимированный фон не обязан совпадать по фазе на разных кадрах; оптический A/B выше использует статический контроль.

Независимый native frontend_reviewer `/root/d33_material_review` выполнил16 public visits, source/screenshot review и финальную критику: material blockers не нашёл, готово к показу владельцу. Независимый `/root/d33_optics_probe` выполнил production-map pixel A/B, нативные Firefox normal/reduced и12 app cases. Защищённые Chromium проверки выполнены основным агентом; reviews не объявляются повторным полным продуктовым E2E.

## Точные файлы D3.3

Новые:

- `frontend/src/components/GlassOptics.jsx`
- `frontend/src/utils/glassOptics.js`
- `frontend/src/styles/glass-materials.css`
- `frontend/tests/glass-materials.test.mjs`
- `frontend/tests/fixtures/glass-materials/index.html`
- `frontend/tests/fixtures/glass-materials/main.jsx`
- `frontend/tests/fixtures/glass-materials/style.css`
- `docs/design/D33_LIQUID_GLASS_MATERIALS.md`
- `docs/design/screenshots/d33/` — только PNG/JSON доказательства; полный перечень в `evidence-manifest.json`.

Изменены относительно начала D3.3:

- `frontend/src/App.jsx` — один общий GlassOptics, без маршрутов/контрактов.
- `frontend/src/main.jsx` — подключение material CSS.
- `frontend/src/pages/instructor/InstructorStudio.jsx` — material-класс общей оболочки, стабильный Outlet.
- `frontend/tests/studio-shell-design.test.mjs` — ожидаемый material-класс; прежние guards сохранены.
- `DESIGN.md`
- `docs/design/REDESIGN_ROADMAP.md`
- `docs/project-memory/CURRENT_STATE.md`
- `docs/project-memory/DECISIONS.md`
- `docs/project-memory/ROADMAP.md`

Другие видимые в Git изменения принадлежат более ранней работе и сохранены. Новых зависимостей, изменений API, данных, маршрутов, шрифтов, медиа или настроек в D3.3 нет.

## Приёмка

Изолированный preview: **http://127.0.0.1:5199/**; material lab: **http://127.0.0.1:5199/tests/fixtures/glass-materials/**. Временные серверы оставлены для личного просмотра, после перезапуска окружения URL может потребовать восстановления.

Владельцу проверить аппаратный Firefox: home/login/register в обеих темах, scroll под header, Studio оболочку, читаемость длинного урока и меню. Проверить, достаточно ли выражена прозрачность на спокойном ambient фоне. D3.3 не считается визуально утверждённым без этого решения. D4–F7 сохранены в roadmap, не начаты.
