# AI Courses — Graphite & Lime Redesign Roadmap

Дата: 2026-11-24. Ветка `design/graphite-lime`, исходный checkpoint D0 `888317e`. Основание: [PRODUCT.md](../../PRODUCT.md), [D1 audit](D1_VISUAL_AUDIT.md). **D1 и D2 завершены; D3–D8 остаются планом. D2 implementation/evidence: [D2_DESIGN_SYSTEM.md](D2_DESIGN_SYSTEM.md), [DESIGN.md](../../DESIGN.md).**

## Цель и неизменные условия

Профессиональный образовательный продукт для начинающих пользователей ИИ. Graphite & Lime — исходная концепция: нейтральная система, ограниченный акцент, выразительная многоязычная типографика и один предметный ASCII Scroll на главной. В учебном пространстве важнее чтение и действие, в Studio — точность операций. Нельзя распространять декоративный режим hero на урок/форму проверки.

Сохранить архитектуру, маршруты, API/auth/session, роли/владение/зачисление, protected media/grants/Range, captions/downloads, независимость lesson/quiz/assignment completion, историю попыток/версий/отзывов, сертификатные ограничения, RU/KK/EN, обе темы. Курс10 не публиковать, Course8 не менять. Рабочая SQLite, настройки и медиа не являются fixtures. Новые библиотеки — только с конкретным обоснованием и отдельным решением; текущие React/Motion достаточны для первой реализации.

## Последовательность

| Этап | Объём | Выход / критерий завершения |
|---|---|---|
| **D0 — подготовка** | Отдельная ветка, Impeccable init, PRODUCT, code-first | Выполнено владельцем/checkpoint888317e. Существующий UI сохранён как baseline |
| **D1 — визуальный аудит** | Независимые A/B, настоящий изолированный браузер, CSS/themes/Motion, референсы | Выполнено: аудит, этот roadmap,56снимков/manifest; код UI не менялся |
| **D2 — Design System** | Семантика палитры, шрифты RU/KK/EN, spacing/radii/density, primitives/states | Выполнено: DESIGN.md, semantic token map, local fonts и primitives;30 browser combinations,431 frontend tests; D2_DESIGN_SYSTEM.md |
| **D3 — главная и ASCII Scroll** | Новый composition/story/CTA, одна ограниченная ASCII-сцена, сокращение повторных process/featured блоков | Смысл читается без анимации; каталог доступен без обязательного просмотра сцены. Обычный scroll и responsive/reduced-motion fallback |
| **D4 — Dark/Light transitions** | Плавное изменение поверхностей и контраста, системные preferences/storage, статический reduced-motion путь | Theme toggle не remount-ит приложение/урок/редактор; не сбрасывает draft, session, media или scroll/focus. Нет мигания/плохого промежуточного контраста |
| **D5 — каталог и страницы курсов** | Один механизм направления, search/filter states, карточки, hero/модули/access CTA | Реальные данные и состояния, понятный первый шаг; public/enrolled-draft/preview доступ не меняется; длинные названия и пустые/ошибочные состояния работают |
| **D6 — учебное пространство и профиль** | Чтение/TOC/sidebar/media, компактная quiz подача, сканируемые инструкции, приоритет обучения в Profile | Даты/статусы/история/feedback/rubric/threshold сохраняются; мобильный вопрос доступнее; error-copy правдива. Канонический текст не переписывать под видом layout |
| **D7 — Instructor Studio** | Новая визуальная оболочка dashboard/editor/curriculum/attachments/assessment/publication | S2.1–S6 сохранены: dirty-guard, save races, sections/anchors, atomic paired moves, rubric validation, real publication blockers. Нет placeholder действий |
| **D8 — финальная проверка** | Изолированный настоящий API/SQLite/storage + browser; roles, themes, locales, viewports, motion, critical flows | UI regression, frontend tests/lint/build, профильные Django/check, whitespace; сохранность working assets; список оставшихся ограничений. Реальная публикация/сертификаты — отдельное разрешение |

D2 задаёт обе палитры; D4 добавляет поведение их переключения. D3 не ждёт установки WebGL/3D-стека и не запускает альтернативные эффектные сцены одновременно. Каждый этап — отдельное разрешённое задание с проверяемым результатом; этот документ не разрешает автоматически выполнить D3–D8.

## D2 — выполненная основа (подробности в D2_DESIGN_SYSTEM.md)

1. Составить карту `v2-tokens.css → index compatibility aliases → component CSS`. Учесть playwright/fixtures/test contracts и исторические playground/amethyst/cinematic слои. Не удалять их до доказанного переноса потребителей.
2. Разделить semantic canvas/surface/raised/text/muted/border/action/focus/selected/success/warning/error. Lime не заменяет автоматически success/focus/link и не должен быть малоконтрастным текстом на белом.
3. Выбрать устойчивую доставку лицензированных шрифтов. Сейчас Linux рендерит системный Noto Sans; это не bundled webfont. Проверить казахские ӘҒҚҢӨҰҮҺІ, кириллицу, латиницу, длинные заголовки и цифры. Mono — акцент/ASCII, не весь reader.
4. Согласовать type scale отдельно для hero, учебного текста и плотного Studio. Система должна быть выразительной без огромных вводных блоков в операционных экранах.
5. Проверить Button/Input/Select/Notice/Badge/Dialog/Progress/Tab/Callout в обеих темах: default/hover/focus/disabled/error/loading, keyboard и 390/320px. Не менять обработчики/валидацию при смене внешнего вида.
6. Зафиксировать новую систему в DESIGN.md **как результат D2**, не документировать нынешний purple как новую целевую систему. Создание файла не равно одобрению всех компонентов.

## D3 — ASCII Scroll: ограниченный договор

- Одна сцена «идея → практика → готовая работа», собственная оригинальная монохромная схема. Не симулировать недоступный встроенный AI-генератор и не использовать чужой ASCII art без лицензии.
- Настоящие заголовок/описание/CTA остаются DOM-контентом. ASCII — вторичный визуальный слой; `aria-hidden` для декора, текстовая альтернатива для смысла.
- Использовать существующие Motion/Canvas/SVG/CSS; ограничить плотность и обновления, останавливать вне viewport/скрытой вкладки. Бюджеты установить по профилированию до усложнения сцены.
- Не перехватывать wheel/touch и не принуждать к горизонтальному скроллу. На mobile и reduced motion — обычная последовательность или статичная схема. Не прятать каталог за «прохождением» hero.
- Fixed3DModel не выбран; Focus-frame Slider и Scroll-triggered Demo остаются альтернативами, не дополнительными обязательными секциями. Layered Parallax не является самостоятельным вторым эффектом.

## Пять проверенных задач для D5/D6

| Приоритет D1 | Задача | Что нельзя потерять |
|---|---|---|
| P2 | Сканируемая инструкция проекта | Единственный canonical description, обязательные материалы, optional adaptation и четыре критерия |
| P2 | Приоритет курса/учебного действия в Profile | Activity, реальные проценты, заявки, имя и существующие сертификаты |
| P2 | Компактное начало мобильного quiz | Все15вопросов/вариантов, threshold70%, focus, подтверждение и история |
| P2 | Условно правдивое сообщение Profile при ошибках | Честное различие unavailable/error и работающих разделов; API/права не расширять |
| P3 | Убрать дублирующий direction control | Существующие search/filter/reset semantics |

## Проверки каждого этапа

- До изменений: Git status и сверка инструкций/контекста; сохранить чужие WIP/untracked. Не смешивать предыдущие локальные настройки с редизайном.
- UI:1440,1024,768,390,320px; light/dark; RU/KK/EN; длинные заголовки, пустые/loading/error/permission states, 200%zoom, keyboard/focus. Проверять реальные pixels, не только computedCSS или отсутствие overflow.
- Motion: reduced preference, document hidden, resize, pointer/touch, медленное устройство. Без scroll traps и потери полезного feedback.
- Accessibility: реальные foreground/background пары и состояния, labels/landmarks, focus restoration, субтитры, текстовые альтернативы; не заявлять WCAG на основании detector.
- Продуктовые границы: draft/anonymous/authorized доступ, playback grant cleanup, Range/seek, subtitles, lesson/progress retry, student submissions/review and quiz attempts. На рабочей БД не выполняются завершение/отправки/оценки.
- Frontend tests/lint/build после UI-правок; Django профильные tests/check если затронут контракт; только изолированная БД. В D1 они не подменяют визуальные доказательства и не были повторены без изменения UI.
- Рекомендуемые D8 цели производительности: определить LCP/INP/CLS и CPU/frame budgets на согласованном устройстве/сети; измерить до и после. D1 не установил эти значения и не обещает их заранее.

## Решения владельца и готовность

Следующий отдельно разрешаемый этап — D3: главная и один ASCII Scroll на основе проверенной D2 системы. Концепция не должна требовать маркетинговых обещаний, новых AI API, фальшивой статистики или изменения учебного материала. Для D3 остаются композиция ASCII в hero и допустимая длина scroll-сцены; Noto Sans/IBM Plex Mono уже поставляются локально в D2; функциональные экраны остаются спокойными.

Не требуется включать сертификаты для редизайна. Описание курса/отметки источников/оценивания и публикация из C5 — отдельный workflow владельца. Не выполнять его вместе с дизайном. Не выполнять автоматический commit/push/merge.
