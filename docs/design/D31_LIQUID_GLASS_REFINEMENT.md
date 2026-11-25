# D3.1 — Obsidian / Frost / Aqua, Liquid Glass

Дата: 2026-11-25. Ветка `design/graphite-lime`, HEAD `bc05bef`. D3 сохранён и уточнён без отката. Это результат реализации для личного просмотра владельцем, **не утверждение владельцем дизайна**. D4–D8 не начаты.

## Направление и композиция

Владелец отклонил визуальный результат D3 и заменил исходный Graphite/Lime на Obsidian/Frost/Aqua. Сохранены продуктовые тексты и сценарий «понять платформу → исследовать курсы». На главной открытая типографическая колонка уравновешена одной крупной стеклянной областью со скульптурой. Плавающая навигация отделена от фона; каталог остаётся основной CTA, регистрация — доступным вторичным маршрутом. Workflow и реальные данные каталога сохранены. Это изменение материала, геометрии и иерархии, а не простая перекраска.

| Роль | Dark | Light |
|---|---|---|
| Canvas | #0B1017 | #EEF2F5 |
| Surface | #121C28 | #FAFCFE |
| Raised | #1C2A38 | #DDE7EE |
| Text | #EDF3F7 | #17232E |
| Secondary | #B1C0CE | #435B6D |
| Action | #78DCD5 | #156B73 |
| Link | #90E1DC | #105F68 |
| Focus | #90E1DC | #146C76 |

В светлой теме действие затемнено относительно исходного предложения для контраста; aqua не используется бледным текстом. Семантические success/warning/error/info сохранены. Точная карта, поверхности и типографика — [DESIGN.md](../../DESIGN.md). Локальные Noto Sans и IBM Plex Mono с RU/KK/EN сохранены, бинарные шрифты не менялись.

## Движение и материал

- Оригинальный вращающийся органический ASCII-тор: 9600 точек, буфер глубины, сетка88×48, десять уровней яркости. Движется без прокрутки и остаётся в hero. Desktop target30fps; mobile/низкое число CPU20fps, ограниченный DPR. При отсутствии Canvas есть текстовый fallback.
- Отдельный scroll-эффект — лёгкий ограниченный parallax визуальной области (−32…12px). Passive listener и один RAF при изменении, без scroll hijack, pinning или движения читаемого текста. На mobile/reduced-motion отключён.
- LiquidEnvironment: один связный SVG-поток из трёх путей, медленный transform32s, mobile48s с упрощением. Нет WebGL, случайных blob-систем, анимируемого blur или новых зависимостей. Скрытый документ останавливает фон; ASCII дополнительно останавливается вне экрана. Reduced-motion даёт статические состояния.
- Glass: непрозрачная базовая поверхность, прозрачность/blur только внутри `@supports`. Навигация и floating controls выше карточек; формы и instructional content остаются читаемыми, таблицы не покрываются blur. Это контролируемое frosted glass, не физическая рефракция.

## Auth, Studio и footer

Login/Register: вместо фиолетового персонажа — открытая вводная колонка с оригинальными контурными SVG-линиями и отдельная frosted form surface. Обработчики, required/validation, password toggle и auth/session не менялись. На узких экранах иллюстрация убирается, форма получает приоритет.

Studio overview: desktop sidebar для навигации, единая полоса реальных метрик, список курсов и сгруппированные операции. Новая layout-классификация включается только на `/instructor`; глубокие редакторы не перестроены. Существующие разрешения и операции сохранены. Полный Studio redesign остаётся D7.

Footer: бренд/объяснение, обучение/каталог, аккаунт/доступный Studio. Только существующие маршруты, без придуманных контактов, соцсетей и юридических документов. Desktop3колонки, mobile2/1. Старые декоративные исходники не удалялись.

## Impeccable, референсы и review

Использован установленный Impeccable: context, replacement-world/craft-floor, doctor, detector, документирование и независимый финальный critique. Обновлён `.impeccable/design.json`, соответствующий новой DESIGN.md. Doctor больше не сообщает stale sidecar; остаётся `design-md-sprawl` (8172bytes): это рекомендация компактности, не неисправность runtime. `design-compact --write` не запускался, unrelated настройки/hook wiring не менялись. Наличие конфигурации hooks не выдаётся за доказательство автоматического запуска в клиенте.

Ручной detector:10 legacy stylistic findings в прежних учебных/Profile/certificate/grid слоях, не в новых D3.1 файлах. Они не подавлены и не объявлены десятью функциональными ошибками.

Изучены [ASCII.rest](https://ascii.rest/), [ASCII Things](https://ascii-things.dev/library/), [React Bits](https://reactbits.dev/), [Linear](https://linear.app/), [Vercel](https://vercel.com/). Это визуальные референсы, не источники скопированных компонентов. React Bits имеет MIT с Commons Clause; никакой сторонний ASCII-код/ассет не включён. Собственные SVG/геометрия, существующие React/Motion; зависимости не установлены. Лицензии OFL шрифтов сохранены.

Реально работали два production workers (auth и ASCII) и отдельный native `frontend_reviewer` на read-only финальном review. Reviewer посмотрел before/after и код, disposition `ship`, material fixes отсутствуют. Это независимая оценка, не согласие владельца и не отдельный браузерный E2E агента.

## Настоящий Chromium и isolated API

Vite5199 → настоящий Django8199 → SQLite-копия `/tmp/ai-d31-e9t10pi5/qa.sqlite3`, отдельное media/cache. Синтетический преподаватель создан только в копии. Автор курса в копии назначен ему для просмотра Studio; тексты/медиа рабочего курса не менялись. Пароли/токены не публикуются.

64 rendered cases:home/login/register/Studio ×16 сочетаний. Полная матрица1440/390 ×light/dark×RU/KK/EN, дополнительно768KK и320RU в обеих темах. Все четыре страницы без horizontal overflow; ни неожиданных console/runtime ошибок, ни HTTP failures в финальном контрольном прогоне. Реальный UI login синтетического автора и переход Studio→editor проверены; регистрации/изменения курсов/прогресса не выполнялись.

Отдельно наблюдались: password toggle, required invalid form, keyboard focus3px, shared controls fixture, несколько scroll positions, static reduced-motion, пауза вне экрана. Hidden-document проверка выполнена через событие visibilitychange с моделированным document.hidden, **не через реальное переключение вкладки ОС**.

Финальный idle-прогон:66 новых кадров примерно за2.27s без scrolling. Browser geometry benchmark100frames:среднее3.019ms на8CPU/DPR1. Это только вычисление геометрии, не гарантия FPS/потребления энергии на слабом устройстве. Аппаратный low-power профиль не измерялся. Backdrop fallback подтверждён кодом/тестами, браузер без поддержки backdrop-filter отдельно не запускался.

Контраст semantic text/action и консервативно composited glass backgrounds покрыт AA assertions. Keyboard/reduced-motion/overflow проверены браузером. Это не полная сертификация WCAG всех существующих экранов. Защищённое видео и assessment E2E заново не выполнялись: их handlers/API не изменены, регрессии покрывает общий frontend-набор.

## Скриншоты до/после

- Главная до: [D3 light](screenshots/d3/after-1440-light-ru.jpg); после: [light](screenshots/d31/after-home-1440-light.jpg), [dark](screenshots/d31/after-home-1440-dark.jpg), [mobile](screenshots/d31/after-home-390-dark.jpg).
- Login: [до](screenshots/d31/before-verified-login-1440-dark.jpg) → [после](screenshots/d31/after-login-1440-dark.jpg).
- Register: [до](screenshots/d31/before-verified-register-1440-light.jpg) → [после](screenshots/d31/after-register-1440-light.jpg).
- Studio: [до](screenshots/d31/before-verified-studio-1440-light.jpg) → [после](screenshots/d31/after-studio-1440-light.jpg).
- Footer: [до](screenshots/d31/before-verified-footer-1440-light.jpg) → [после](screenshots/d31/after-footer-1440-light.jpg).
- Монохромные сравнения: `screenshots/d31/compare-{home,login,studio}-{before,after}-mono.png`.
- Вся матрица/точные файлы/хеши: [verification.json](screenshots/d31/verification.json).

Главная before — фактический D3 capture. Before auth/Studio/footer — замороженные pre-D3.1 presentation sources с тем же isolated API; eager-import из временной App заменён lazy только для обхода несовместимости старого hero/new geometry при восстановлении capture, не в production. Неудачные ранние `before-*` снимки сохранены как исключённая диагностика; валидные имеют префикс `before-verified-*`. After-снимки проверены визуально; обрезания текста/наложения контролов в матрице не обнаружены.

## Выполненные команды

Из frontend, с существующим NVM:

```sh
node --test tests/*.test.mjs
npm run lint
npm run build
```

442passed,0failed,0skipped; oxlint без findings; Vite build PASS. Профильный начальный набор34passed, новые glass-проверки включены в442. Проверки обновлены по реальному контракту: устаревшее ожидание mascot заменено локальными contours, semantic contrast assertions сохранены; geometry tests теперь проверяют time-driven torus.

```sh
PYTHONPATH="/tmp/ai-d31-e9t10pi5:$PWD" DJANGO_SETTINGS_MODULE=settings_d31 .venv/bin/python -B manage.py check
git diff --check
```

Оба PASS. Django0issues, тесты не направлялись на рабочую SQLite.117 исходных SHA-256 DB/settings/media совпадают, live read-only integrity `ok`,FK0,Course10 `is_published=0`. HEADbc05bef, staged paths0. Рабочие config/settings.py и исторические untracked материалы сохранены. Никаких migrations/backend/API/course/certificate changes.

## Точные D3.1 пути

- `PRODUCT.md`, `DESIGN.md`, `.impeccable/design.json`.
- `frontend/src/App.jsx`, `frontend/src/main.jsx`, `frontend/src/styles/v2-tokens.css`, `frontend/src/styles/liquid-surfaces.css`.
- `frontend/src/components/AuthLayout.jsx`, `frontend/src/components/AuthLayout.css`, `frontend/src/components/Footer.jsx`, `frontend/src/components/HomeHero.jsx`, `frontend/src/components/HomeHero.css`.
- `frontend/src/components/landing/AsciiLearning.jsx`, `frontend/src/components/landing/AsciiLearning.css`, `frontend/src/components/landing/LiquidEnvironment.jsx`, `frontend/src/components/landing/LiquidEnvironment.css`.
- `frontend/src/hooks/useHeroDepth.js`, `frontend/src/utils/asciiLearning.js`, `frontend/src/pages/instructor/InstructorStudio.jsx`.
- `frontend/src/i18n/locales/ru.json`, `frontend/src/i18n/locales/kk.json`, `frontend/src/i18n/locales/en.json`.
- `frontend/tests/auth-design.test.mjs`, `frontend/tests/design-foundations.test.mjs`, `frontend/tests/ascii-learning.test.mjs`, `frontend/tests/liquid-glass.test.mjs`, `frontend/tests/fixtures/design-system/main.jsx`.
- Этот отчёт, `docs/design/screenshots/d31/*` (точный inventory/hash/исключения в verification.json), `docs/design/REDESIGN_ROADMAP.md`, `docs/project-memory/CURRENT_STATE.md`, `docs/project-memory/DECISIONS.md`, `docs/project-memory/ROADMAP.md`.

Уже существующие D3 изменения Header/CourseCatalog/LearningWorkflow/ClosingInvitation, graphite-landing.css/tests, license/provenance и D3 report/screenshots сохранены; не выдаются за новые D3.1 доработки. Исторические local-only файлы не удалялись.

## Preview и следующий шаг

Рабочий изолированный preview: **http://127.0.0.1:5199/**. Login `/login`, register `/register`; Studio требует обычного авторизованного входа. Синтетические credentials в отчёте не публикуются. Нормальная сессия владельца на другом origin сюда не переносится. Серверы временные, доступны пока текущая среда работает; рабочая БД ими не используется.

Владелец должен оценить light/dark, idle ASCII, scrolling, формы и mobile. Остались: личное визуальное одобрение, аппаратный low-power/реальный background-tab spot check, полная D7 детализация остальных экранов. D4 transitions не реализованы. Нет staging/commit/push/merge; следующая фаза автоматически не запускается.
