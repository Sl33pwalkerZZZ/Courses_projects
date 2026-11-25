---
name: AI Courses — Obsidian Frost Aqua
description: "Liquid Glass для профессионального обучения"
colors:
  obsidian: "#0B1017"
  dark-surface: "#121C28"
  dark-elevated: "#1C2A38"
  dark-text: "#EDF3F7"
  dark-muted: "#B1C0CE"
  aqua: "#78DCD5"
  frost: "#EEF2F5"
  light-surface: "#FAFCFE"
  light-elevated: "#DDE7EE"
  light-text: "#17232E"
  light-muted: "#435B6D"
  light-action: "#156B73"
  light-link: "#105F68"
typography:
  heading:
    fontFamily: "Noto Sans, system-ui, sans-serif"
    fontWeight: 600
    lineHeight: 1.12
    letterSpacing: "-0.035em"
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
  technical:
    fontFamily: "IBM Plex Mono, ui-monospace, monospace"
    fontWeight: 400
rounded:
  small: "4px"
  control: "8px"
  panel: "16px"
  navigation: "18px"
spacing:
  small: "8px"
  medium: "16px"
  large: "24px"
  section: "40px"
components:
  button-primary:
    backgroundColor: "{colors.aqua}"
    textColor: "{colors.obsidian}"
    rounded: "{rounded.control}"
    padding: "10px 18px"
    height: "44px"
---

## Overview

**Creative North Star: «Глубина без шума».**

Владелец,2026-11-25: Obsidian / Frost / Aqua, управляемый Liquid Glass. D3 не одобрен. D3.2 развивает одобренную палитру и ожидает личной оценки владельца; архитектура сохранена. D3.3 отдельно усилит оптический материал по новым референсам.

**Key Characteristics:** frosted-поверхности, спокойная глубина, крупная многоязычная типографика, непрерывная оригинальная ASCII-скульптура и отдельный лёгкий parallax. UI служит чтению и действию; эффект не скрывает материал.

Нормативные значения: `frontend/src/styles/v2-tokens.css`, иерархия поверхностей: `frontend/src/styles/liquid-surfaces.css`. `--v2-*` aliases сохранены. PRODUCT.md — продуктовые ограничения. D3.3 и D4–D8 не начаты; основная оболочка Studio перенесена вперёд из D7 в D3.2.

## Colors

| Роль | Dark | Light |
|---|---|---|
| Canvas | #0B1017 | #EEF2F5 |
| Surface / raised | #121C28 / #1C2A38 | #FAFCFE / #DDE7EE |
| Text / secondary | #EDF3F7 / #B1C0CE | #17232E / #435B6D |
| Action / on action | #78DCD5 / #0B1017 | #156B73 / #FFFFFF |
| Link / focus | #90E1DC / #90E1DC | #105F68 / #146C76 |
| Control border | #8199AC | #5D778A |
| Glass surface | rgb(18 28 40 /68%) | rgb(250 252 254 /68%) |
| Floating glass | rgb(28 42 56 /72%) | rgb(255 255 255 /72%) |

**The Readability Rule.** Текст≥4.5:1, крупный текст≥3:1, meaningful control/focus≥3:1. Проверять composited background, а не только исходный цвет стекла. Для обычных light-ссылок — тёмный aqua. Цвета success/warning/error/info сохраняют смысл и подписи; они не заменяются акцентом. Lime/purple не являются активными brand colors.

## Typography

Локальные OFL Noto Sans normal400–800 и IBM Plex Mono400 сохраняются. RU/KK/EN, включая ӘҒҚҢӨҰҮҺІ, проверены по реальным cmap. Бинарные шрифты неизменны. OFL/provenance/SHA: `frontend/public/fonts/`.

Body16px/1.65, рабочие labels15–16px/1.45, captions13–14px; reader token17px, рекомендуемый measure65–75ch. Hero48–76px desktop, mobile40–60px; конкретный responsive clamp — HomeHero.css. Auth intro38–58px. Mono — для символной скульптуры и технических данных, не всего учебного текста. Обычный регистр, без широкого tracking и длинных uppercase-подписей.

## Layout

Ритм4/8/12/16/20/24/32/40/48/64/80/96px. Интерактивная область≥44px. Заголовки и controls могут переноситься; min-width:0 у grid children. Hero-скульптура закреплена в своей композиции, не сопровождает пользователя по всей странице. Mobile упрощает слои.

Studio: единая боковая навигация248–264px на всех маршрутах, расширяемая оболочка до2240px; mobile использует существующий keyboard-friendly disclosure. Внутренние формы и редакторы наследуют общий масштаб16px и поверхности, без изменения save/guard/permission flow. D7 — оставшиеся уточнения и итоговая проверка, не повтор оболочки. Footer группирует только существующие учебные и account destinations; Studio доступен по реальной capability.

## Elevation & Depth

Не каждое поле — стекло. D3.3 заменяет прежнюю68/72% иерархию четырьмя материалами: A workspace38%, B panels48%, C optical backplate28%, D reading/forms96%. Firefox/mobile/reduced C использует более плотный fallback64%light/68%dark. Подробные актуальные правила ниже; opaque fallback объявляется до `@supports`.

Shadow dark:`0 18px 56px rgb(0 6 14 /24%)`; light:`0 18px 56px rgb(43 70 91 /12%)`. Border — тонкий cool outline, не светящийся halo. LiquidEnvironment — оригинальное детерминированное Canvas2D поле деформируемых направленных волн и каустических бликов;160×100,target24fps desktop,96×72,target12fps mobile/≤4CPU. Без WebGL/внешних ассетов. Это целевые частоты, не обещание измеренногоFPS.

Motion feedback120/180/260ms и существующие easing сохранены. ASCII30fpsdesktop/20fpsmobile и≤4CPU, DPR≤1.5/1; pause offscreen/hidden. Один ограниченный parallax−32..12px отдельно от idle-анимации; отключён mobile/reduced motion. Reduced motion статичен. D4 theme-transition choreography ещё не реализована.

## Shapes

Controls8px, основные панели/dialog16px, floating nav18px; hero visual28px/22px tablet. Focus3px offset3px. Без лишних вложенных cards, side stripes и multiple shadows.

## Components

- **Buttons/fields:** прежние нативные semantics/validation/disabled, отдельные hover/active/focus/error. Читаемые opaque inputs в glass-form; password controls44px сохранены.
- **Glass panels:** base/floating/opaque роли не смешивать. Не ставить blur на каждую вложенную строку или таблицу.
- **Dialog/dropdowns:** прежние focus/Escape/roles и permission flow; surface fallback всегда доступен.
- **Tabs/nav:** active aqua tint +foreground, реальные aria/current/router states; не выдумывать доступные actions.
- **Badges/notices/progress:** реальные статусы и значения, подпись важнее цвета. Никакой фиктивной статистики.
- **Auth:** открытый editorial intro +единая frosted-form, с парной оригинальной оптической скульптурой, idle/ограниченным pointer gaze; декоративный код не читает поля или пароли. Login/Register handlers и API неизменны.

## Do's and Don'ts

### Do:
- **Do** проверять оба режима, RU/KK/EN, реальные данные, focus и composited contrast.
- **Do** ограничивать живое движение отдельным ambient layer и скульптурой, сохраняя спокойный текст.
- **Do** сохранять opaque fallback и выключать ненужное движение.

### Don't:
- **Don't** превращать все контейнеры в прозрачное стекло или возвращать dominant purple/lime.
- **Don't** применять blur/glow без иерархии, перехватывать scroll или скрывать content за animation.
- **Don't** менять API/auth/access, прогресс, работы, медиа или сертификаты ради визуального эффекта.

## D3.3 — A/B/C/D material hierarchy (2026-11-25)

Композиция D3.2 сохранена. A: `rgb(18 28 40 /38%)` dark / `rgb(250 252 254 /38%)` light, blur18px. B: те же основы48%, blur14px для самостоятельных панелей. Внутри Studio A панели B имеют только tint/specular, без повторного backdrop-filter. C:28% backplate с отдельным псевдоэлементом; foreground не фильтруется. D:96%, спокойная плотная поверхность для чтения, таблиц, оценивания и полей.

Muted на прозрачных материалах: dark `#C2D1DD`, light `#344D60`. Aqua и основные Obsidian/Frost токены сохранены. Края тонкие, верхний specular и мягкая тень; не добавлять glow.

Оригинальная статическая128×128 edge-normal карта и SVG displacement14 используются только на backplate floating header. Центр нейтрален; R/G задают направление у края. Desktop Chromium с>4 logicalCPU и без reduced-motion допускает enhancement. Это проверенный visual allowlist, не универсальное определение поддержки. Firefox/mobile/reduced/остальные браузеры получают frost с blur12px там, где он фактически поддерживается, прозрачностью64%light/68%dark и бликом. Opaque fallback остаётся без backdrop support.

Пиксельный A/B тест реального фильтра подтвердил искажение Chromium. Firefox143 headless SWGL не показал даже обычный backdrop blur в контрольном тесте: подтверждены читаемый tint/edge fallback и reduced-motion, не оптическая эквивалентность. Ручная проверка аппаратного Firefox владельца остаётся обязательной.

Без новых зависимостей и заимствованного кода. Animated liquid/ASCII/auth sculpture сохранены. `createLiquidPixels`160×100: median2.70ms/p954.10ms в Chromium,100 samples; это вычисление, не итоговый FPS. D3.2 sustained24FPS не установлен; не обещать его. Отчёт: [D33](docs/design/D33_LIQUID_GLASS_MATERIALS.md). Визуальная приёмка владельцем ожидается; D4 не начат.
