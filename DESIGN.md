---
name: AI Courses — Graphite & Lime
description: "Многоязычный профессиональный интерфейс обучения"
colors:
  graphite: "#101210"
  carbon: "#1C211D"
  dark-raised: "#29312B"
  paper: "#F4F5F0"
  white: "#FFFFFF"
  light-raised: "#E8ECE2"
  lime: "#C4F56A"
  light-ink: "#182019"
  light-link: "#355B16"
  dark-muted: "#B0BAAA"
  light-muted: "#4E5B4B"
typography:
  heading:
    fontFamily: "Noto Sans, system-ui, sans-serif"
    fontWeight: 700
    lineHeight: 1.16
    letterSpacing: "-0.025em"
  body:
    fontFamily: "Noto Sans, system-ui, sans-serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.65
  label:
    fontFamily: "Noto Sans, system-ui, sans-serif"
    fontSize: "0.875rem"
    fontWeight: 600
    lineHeight: 1.45
  caption:
    fontFamily: "Noto Sans, system-ui, sans-serif"
    fontSize: "0.8125rem"
    fontWeight: 600
    lineHeight: 1.45
  technical:
    fontFamily: "IBM Plex Mono, ui-monospace, monospace"
    fontWeight: 400
rounded:
  small: "4px"
  control: "8px"
  card: "12px"
  dialog: "16px"
spacing:
  small: "8px"
  medium: "16px"
  large: "24px"
  section: "40px"
components:
  button-primary:
    backgroundColor: "{colors.lime}"
    textColor: "{colors.graphite}"
    rounded: "{rounded.control}"
    padding: "10px 18px"
    height: "44px"
---

## Overview

**Creative North Star: «Точность без тяжести».**

Graphite & Lime — технологичный, спокойный визуальный язык профессионального обучения. Выразительность создают типографика, ясная иерархия и редкий акцент; учебный текст и рабочие формы остаются удобными для длительной работы. Это реализация D2 по направлению владельца, а не утверждение о завершённом редизайне всех страниц или пользовательском одобрении каждого пикселя.

**Key Characteristics:** нейтральные поверхности, заметное основное действие, читаемые многоязычные подписи, различимые состояния, сдержанное движение.

Источник значений — `frontend/src/styles/v2-tokens.css`; `--color-*` описывает семантику, существующие `--v2-*` и aliases в `index.css` сохраняют совместимость. Не удалять старые имена до переноса потребителей. PRODUCT.md определяет продуктовые ограничения. D3–D7 заменят композиции страниц отдельно; исторические CSS-файлы и оригинальные SVG сейчас сохраняются.

## Colors

| Роль | Dark | Light |
|---|---|---|
| Background | #101210 | #F4F5F0 |
| Surface / elevated | #1C211D / #29312B | #FFFFFF / #E8ECE2 |
| Primary text | #F4F5F0 | #182019 |
| Secondary text | #B0BAAA | #4E5B4B |
| Accent fill / on accent | #C4F56A / #101210 | #C4F56A / #101210 |
| Accent text / link | #C4F56A | #355B16 |
| Hover / active fill | #D3FF86 / #B0DE57 | #B0E451 / #A0D344 |
| Decorative border / control border | #3D493E / #82917E | #CAD2C3 / #66735E |
| Focus | #C4F56A | #41691B |
| Disabled background / text | #29312B / #B0BAAA | #E8ECE2 / #56634F |
| Success | #81D4A6 | #23623B |
| Warning | #F5CF87 | #81520C |
| Error | #FFB4A9 | #A72F32 |
| Info | #A7CBFA | #275D8A |

Полные status backgrounds, hero compatibility и состояния находятся в CSS. `#929B90` исходного брифа заменён для второстепенного текста более контрастными оттенками. Декоративная граница не обязана иметь контраст интерактивного контрола: для input/button используйте отдельный control-border.

**The Accent Rule.** Lime — заливка ключевого действия и dark-ссылки; обычный текст и ссылки на светлой поверхности используют тёмный зелёный. Не писать lime-текст на Paper/white. Успех, ошибка и предупреждение имеют подпись/контекст, а не только цвет. Текст ≥4.5:1, meaningful control/focus/progress ≥3:1 относительно соседней поверхности; проверять реальные пары с opacity и каскадом.

## Typography

Noto Sans локально: variable normal 400–800, WOFF2 latin/latin-ext/cyrillic/cyrillic-ext, `font-display: swap`. IBM Plex Mono Regular 400 локально для code/kbd/samp/pre, коротких технических обозначений и будущего ASCII. Моноширинный шрифт не заменяет основной учебный текст. OFL notices и exact-byte provenance в `frontend/public/fonts/`.

Проверены реальные cmap: RU, EN, Әә Ғғ Ққ Ңң Өө Ұұ Үү Һһ Іі в обеих гарнитурах. Рассмотренная сборка Manrope не содержит Ә/Ғ/Қ/Ң/Ұ и не поставляется: системный fallback внутри казахского слова недопустим. При изменении файлов повторить проверку покрытия, не доверять одному ярлыку Cyrillic Extended.

- Heading: 700, line-height 1.16, tracking −0.025em; конкретные размеры зависят от задачи страницы. В specimen h1 `clamp(2rem,4vw,3.5rem)`, h2 1.5rem, h3 1.125rem — это образец, не автоматический размер любого hero.
- Body: 1rem/1.65, 400. Reading token: 1.0625rem. Рекомендуемая ширина читательской колонки 65–75ch, переносы и ограничения должны сохранять таблицы и media.
- Labels/actions: .875rem/1.45, 600. Captions/status: .8125rem/1.45, 600.
- Не использовать uppercase для длинных RU/KK подписей; технические имена и цифры допустимы. Все смысловые строки — существующая RU/KK/EN локализация.

## Layout

Ритм 4/8/12/16/20/24/32/40/48/64/80/96px. Controls min-height 44px, без жёсткой высоты для многострочных названий. Container token 1280px; поля и grid children имеют min-width:0. Specimen 1120px, padding32px desktop/16px mobile, без production route. Границы страниц и responsive sidebar не перепроектированы в D2.

Проверочная матрица:1440/1024/768/390/320px, обе темы, RU/KK/EN. Сохранять естественный скролл, видимый focus и порядок DOM. Для широких учебных таблиц — локальный keyboard-accessible скролл, не обрезка текста.

## Elevation & Depth

Плоские поверхности по умолчанию: border и тональное различие вместо стекла/свечения. Card shadow:none. Отдельная modal elevation: `0 20px 64px rgb(0 0 0 / 38%)` dark / `0 20px 64px rgb(16 22 14 / 20%)` light. Overlay получает отдельный нейтральный scrim. Не накладывать тени на каждую вложенную карточку.

Motion:120ms feedback,180ms обычный переход,260ms более заметный переход; ease-out `cubic-bezier(.2,.8,.2,1)`, ease-in-out `cubic-bezier(.4,0,.2,1)`, distance token4px. Новые shared buttons меняют цвет/границу, не подпрыгивают и не двигают иконку при hover. `prefers-reduced-motion` отключает переходы. Существующие MotionConfig и reduced-motion guard сохранены. ASCII Scroll и согласованный переход тем ещё не реализованы: D3/D4. Не добавлять циклы или motion вокруг учебного текста/видео.

## Shapes

4px status/progress,8px controls,12px shared cards,16px dialogs. Полный border1px на контролах, focus outline3px offset3px. Pill999px остаётся compatibility token для действительно круглых элементов, не универсальная форма каждой карточки. Не вводить декоративные боковые полосы, неон или вложенный glass.

## Components

- **Button:** primary lime/dark ink; secondary surface+control-border; ghost transparent; danger semantic fill+контрастный текст. Hover/active отдельные; disabled читаем и без hover-feedback. Нативные button/link, disabled и обработчики не меняются.
- **Input/Select/Textarea:** surface, border-control,8px, min44px; placeholder muted. Error `aria-invalid` красная граница и текст ошибки. Disabled отдельная поверхность/текст. Сохранять label/hint/required и server validation; стили не меняют логику.
- **Surface:** base/elevated/inset; border и12px. Не создавать ещё одну карточку без смысловой группы.
- **Dialog:** existing native dialog, ширинаmin(520px,viewport−32px), max-height viewport−48px с локальным скроллом,16px,20–32px padding. Сохранять Escape, focus-management и accessible name.
- **Tabs/navigation:** состояние определяется существующими aria/current/router данными. Shared role=tab uses underline+foreground, focus3px. Роуты/handlers и отдельные page nav layouts остаются прежними до профильного этапа.
- **Badge/Notice:** success/pending/error/info с фоновым тоном, текстом и нужным role; badge4px. Внешняя страница может иметь legacy override — проверять при её миграции.
- **Progress:** native progress8px, dark lime / light dark-green fill. Значение всегда из реальных данных; specimen40% явно демонстрационное.
- **Loading/empty/error:** существующие status/alert/retry; поверхность не подменяет состояния. Демо показывает образцы, не добавляет вымышленные данные в продукт.
- **Theme toggle:** существующий ThemeProvider,44px hit-area, контрастные иконка/border. Смена persistence/auth не затрагивается.

## Do's and Don'ts

### Do:
- **Do** использовать semantic roles и проверять контраст в обеих темах.
- **Do** оставлять primary-action заметным, а чтение спокойным.
- **Do** проверять Kazakh glyphs, длинные переводы, focus, disabled/error и реальные экраны.

### Don't:
- **Don't** возвращать доминирующий purple, декоративные градиенты/glow или делать все поверхности одинаково скруглёнными.
- **Don't** переносить hero-анимацию в формы/учебный текст или выдавать D2 за полный редизайн.
- **Don't** менять API/auth, данные курса, прогресс, медиа/субтитры и сертификатные правила ради внешнего вида.
