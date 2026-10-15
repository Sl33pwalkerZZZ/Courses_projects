# AI Courses V2 — reference analysis and proposed design system

Date: 2026-10-15. Status: **design proposal; implementation requires review**.
Working branch: `design/ai-courses-v2`. No application or database changes are part
of this analysis. Earlier uncommitted UX fixes are preserved.

## 1. Evidence and scope

Firefox inspected the [live reference](https://edu.astanahub.com/hackathons/df4743f5-c492-415c-b45a-1f13adb78e06)
at 1440×1000 and 375×812. Screenshots are in `.playwright-mcp/`.

The exact requested `http://localhost:5173/` renders blank: optimized Vite imports
fail with `NS_ERROR_CORRUPTED_CONTENT` and empty/disallowed MIME types. Its desktop
and mobile screenshots document that failure. To study the existing UI, a separate
preview serves this same checkout at `http://127.0.0.1:5175/` with an isolated
temporary cache and a read-only proxy to the real public course APIs. The proxy
permits only GET/HEAD `/api/courses/**`; it rejects other API methods/paths. No fake
course data, authentication sessions, source/config edits, or dependency installs
are used. Preview screenshots must not be presented as proof that port 5173 works.

LessonView and Profile are reviewed from source because no authorized student
session is supplied. Their V2 layouts below are proposals, not observed protected
screens. No registration, application, review, quiz or completion is submitted.

### Measured reference observations

| Area | Observed in Firefox |
|---|---|
| Structure | White product canvas; persistent desktop left rail approximately 255px; sticky section navigation. |
| Hero | Approximately 448px high, near-black `#07080A`, 28px desktop corner radius, static blue bitmap artwork. |
| Type | Golos Text; desktop H1 60/60px, weight 800; section titles 30/36px, 700; body 16/24px. |
| Surfaces | White cards, `#F2F2F2` secondary surfaces; card radius 20px, padding 20px, `#D1D1D1` borders. |
| Mobile | 12px side margins; 351px hero, radius 24px; H1 26/27.3px; slide-out navigation and fixed 64px bottom section tabs. |
| Motion | Navigation hover 150ms; FAQ grid expansion and chevron rotation 300ms. No continuous hero motion or elaborate scroll reveal observed. |
| Caveats | FAQ buttons lacked `aria-expanded`; drawer did not close with Escape and kept transitions under reduced motion. These are not patterns to reproduce. |

Interpretation: borrow decisive hierarchy, grouped metadata and restrained depth.
Do not reuse logos, partner marks, hero bitmap, event copy, prizes or other assets.
The reference's dark hero is an inverse surface inside a light site; a complete
dark theme was not observed. Do not label proposed scroll effects as reference
behavior or infer its animation library from appearance.

The reference rendered despite a public `/api/g` 401, speculative login request
404 and analytics cookie warnings. These are observed requests, not evidence that
its visible layout is broken. Non-visible lazy sponsor images were not classified
as missing assets.

### Existing AI Courses observations and constraints

The working preview uses a cream/graphite/gold palette, Georgia headings and
system UI text. Measured homepage H1 is approximately 63/72px desktop, 34/39px
mobile; desktop content is 1200px wide, with 20px mobile gutters. The measured
mobile header occupies approximately 206px across several rows. A long sticky
KnowledgeJourney separates the hero and catalog. Sticky scenes can produce
misleading blank regions in full-page screenshots; evaluate real scroll viewports.
CourseDetail's desktop title is Georgia at 72px; course cards repeat orbit/book
artwork and use approximately 240ms 3D tilt/lift feedback. V2 proposes simpler
two-dimensional feedback and clearer subject differentiation.

Current homepage and catalog share `/` and `#course-library`. Preserve that route
contract for the first V2 release. A dedicated `/catalog` route is an optional,
separate review decision, not a prerequisite or an implicit API change.

## 2. Direction: AI Signal Studio

A confident technology learning product: crisp typography, an ice-white or ink
canvas, one strong inverse hero, precise blue actions and restrained teal signal
graphics. Learning content receives calmer treatment than discovery pages.

Distinctive elements:

- An original SVG signal map connecting **explore → learn → practice**, using thin
  paths and a few solid nodes. No borrowed bitmap, repeated orbit artwork or logos.
- Subject identifiers generated from real direction/level metadata: a short label,
  a controlled geometric motif and consistent course numbering/position only where
  meaningful. Never fabricate lesson counts, durations or outcomes.
- Large, readable headings and disciplined card interiors rather than more glow.
- One obvious primary action per section; course access state always takes priority
  over promotional styling.

The homepage is expressive; LessonView is a quiet working surface. Blue indicates
an action, green indicates confirmed success, amber indicates pending/warning, and
rose indicates failure/rejection. Status always includes text and, where useful,
an icon. Progress is never implied by decorative animation.

## 3. Proposed tokens

Machine-readable proposal: [ai-courses-v2.tokens.json](./ai-courses-v2.tokens.json).
These tokens are not imported by the application.

| Semantic color | Light | Dark |
|---|---|---|
| Canvas | `#F4F7FC` | `#0B1020` |
| Surface / raised | `#FFFFFF` / `#EAF0F9` | `#121A2C` / `#182338` |
| Primary text | `#101828` | `#EEF4FF` |
| Supporting text | `#46566F` | `#A9B7D0` |
| Decorative divider | `#D7DFEB` | `#35445F` |
| Essential control border | `#74829A` | `#667995` |
| Primary action | `#1255D9` | `#84B7FF` |
| Primary hover | `#0B42B4` | `#A3CAFF` |
| Text on primary | `#FFFFFF` | `#07101F` |
| Focus | `#1255D9` | `#84B7FF` |
| Teal accent | `#0B7A75` | `#51D6C5` |
| Success | `#087052` | `#6CE5B7` |
| Pending/warning | `#865200` | `#F5C16C` |
| Error/danger | `#B4233A` | `#FF9AAE` |

Inverse hero in both themes: background `#0B1224`, text `#F5F8FF`, supporting text
`#BAC7DD`, button `#84B7FF` with `#07101F` text. Use these explicit inverse roles;
do not allow a light-theme dark label to inherit onto the dark hero.

Computed flat-color contrast examples: light body/surface **17.75:1**, light
supporting text **7.44:1**, light primary button text **6.31:1**; dark body/surface
**15.72:1**, dark supporting text **8.57:1**, dark primary button text **9.25:1**.
Essential control borders are approximately **3.9:1** against their surfaces.
These samples are not a complete compliance audit. Validate composed overlays,
focus indicators and every status treatment in implementation. Target at least
4.5:1 for ordinary text and 3:1 for relevant non-text controls, following
[W3C text contrast guidance](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html)
and [non-text contrast guidance](https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html).
Decorative dividers are not substitutes for control boundaries.

The JSON includes semantic recipes for primary, secondary, ghost, destructive,
disabled and busy controls; default/error/disabled fields; neutral/success/pending/
error badges; and inverse-hero buttons. Status backgrounds use the raised surface
with explicit foreground colors, labels and icons. Disabled controls retain readable
labels without global opacity. Busy controls retain their variant and accessible
name, with `aria-busy` and a non-disruptive indicator. Never dilute the light teal
text on the raised surface: its approximately 4.52:1 contrast leaves little margin.

### Typography

Use **Noto Sans variable** for UI and headings; keep a system fallback until fonts
are intentionally approved and self-hosted. Its [official metadata](https://github.com/google/fonts/blob/main/ofl/notosans/METADATA.pb)
lists Kazakh Cyrillic coverage. Verify the shipped subset with
`Ә Ғ Қ Ң Ө Ұ Ү Һ І ә ғ қ ң ө ұ ү һ і`, Russian and English samples. Keep license
notices. Do not install fonts during this analysis.

| Role | Desktop size/line | Mobile size/line | Weight |
|---|---|---|---|
| Homepage display | 64/72px | 36/42px | 750 |
| Page title | 40/48px | 28/36px | 700 |
| Section title | 28/36px | 24/32px | 700 |
| Card title | 20/28px | 20/28px | 700 |
| Body | 16/26px | 16/26px | 400 |
| Lesson reading | 18/30px | 18/30px | 400 |
| Controls | 14/20px | 14/20px | 600 |
| Supporting metadata | 14/22px | 14/22px | 400–500 |

Reserve 12/18px only for nonessential captions; never use it for access status,
errors or form instructions. Use tabular numerals for progress and analytics.
Use monospace only for code/technical identifiers, not multilingual navigation.
Allow natural line wrapping: hero titles are not images or letter-by-letter text.

### Geometry and layout

- Spacing scale: **4, 8, 12, 16, 20, 24, 32, 40, 48, 64, 80, 96px**.
- Radius: **8px** small surfaces; **12px** controls; **16px** cards; **24px** hero;
  pill rounding only for compact chips.
- Content max-width **1280px**; centered with 16px mobile, 24px tablet, 32px desktop
  minimum gutters. Lesson text stays at **65–75ch** independently of shell width.
- Grids: 4 columns mobile, 8 tablet, 12 desktop; gaps 16/24/24px.
- Header height: **64px mobile**, **72px desktop**. Controls 48px high; ordinary
  touch targets at least 44×44px.
- Shadows: light card `0 8px 24px rgb(16 24 40 / 6%)`; overlay
  `0 16px 48px rgb(16 24 40 / 16%)`. Dark equivalents use black at 18% and 35%.
  Use borders first; shadows primarily communicate raised interaction layers.
- Layer order: content 0, sticky section 10, header 20, popover 30, drawer 40,
  dialog 50, skip link 60. A skip link must remain visible above all overlays.
- Icons: retain existing Lucide icons; 16px metadata, 20px controls, 24px navigation,
  consistent 1.75px stroke. Hide decorative icons from assistive technology;
  icon-only actions need translated accessible names and full-size hit areas.
- Anchor clearance: actual rendered header height plus **16px**. Use that measured
  value for scroll padding/margins rather than assuming the nominal header height.
  Catalog, curriculum, reviews and keyboard focus must remain visible after jumps.
  Keep one page scroll owner; do not introduce nested full-page scrolling.

## 4. Shell and page composition

Use one global top navigation, not a permanent public left rail. Desktop: brand,
catalog anchor, authenticated Profile or existing sign-in/register actions, theme
toggle and RU/KZ/EN controls. Mobile: brand, theme, current-language control and
Menu in one 64px row. The language control opens an accessible three-language
choice; the existing i18n/theme persistence remains authoritative.

The 64px mobile bar is a normal-size target, not a fixed-height constraint. At
320px or enlarged text, move theme/language preferences into the accessible Menu
before shrinking controls; preserve their names, current values and 44px targets.
If necessary, allow natural header height growth and recalculate anchor clearance.
Keep the brand and Menu reachable without horizontal overflow.

The mobile menu must move focus appropriately, close with Escape, restore focus,
and make its background inert. Keep only one modal navigation layer open. Lesson
curriculum on small screens is an in-flow disclosure, not a second modal drawer.
Do not introduce fixed bottom navigation over quiz or application controls.

### Homepage

1. Compact top navigation.
2. Dark, rounded hero: concise original proposition, one catalog CTA and an
   optional existing registration CTA, with decorative signal-map illustration.
   Text precedes illustration in DOM; art is hidden from assistive technology.
3. Short direction chooser sourced from existing course directions.
4. Catalog heading and filters, reachable within approximately two viewport
   heights. The catalog CTA jumps there immediately.
5. Optional short three-step explanation of the existing learning/access workflow,
   with no forced scroll scene, followed by the existing project/footer content.

No invented participant counts, testimonials, awards, completion guarantees or
course outcomes. If showing totals, derive them from fields already available.
Retire the long pinned introduction when approved; preserve its useful message as
short, readable content. This is a proposed animation/content arrangement, not a
claim about the reference's behavior.

The direction chooser updates the existing catalog direction filter, with one
source of state and no additional endpoint. Verify the catalog heading begins
within two viewport heights at 375px in RU/KK with normal motion as well as reduced
motion. Cap optional mobile illustration height at 160px and omit it if needed;
the title, actions and catalog access take priority over decorative space.

### Course catalog

Keep `#course-library`, client-side search/direction/level filtering and public
request independence. Use three columns at wide desktop, two when cards would
otherwise fall below roughly 300px, and one on mobile. Each card has a consistent
art band, direction/level, title, readable excerpt, author, real rating/count only
when available, and a clear course link. Avoid nested interactive controls inside
a whole-card anchor.

Use equal-height cards with natural text growth. No fixed two-line title clipping
that hides translated titles. Mobile filters wrap in normal flow; a later filter
popover is optional, not necessary for the first release. Preserve query text on
account changes and announce result counts without announcing every keystroke
aggressively. Keep loading, no courses, no results/reset, and recoverable errors.

### CourseDetail

Use a readable overview header with breadcrumb, title, description and real course
metadata. An access panel sits to the right on wide screens and directly below
the title/summary on mobile. On desktop it may stick below the single global
header; on mobile it remains in flow. About/curriculum/reviews retain native anchor
links and existing hash behavior, not a new tab state that hides deep-linked content.

Make the actual access state prominent: anonymous sign-in, open enrollment,
pending, rejected/reapply with explanation, approved-refresh, enrolled/continue,
loading and recoverable failure. Preserve application Open/Cancel focus movement.
Public visitors see module and lesson-title previews without protected links.
Keep moderated reviews and private `my_review` behavior. Retain genuine 404 versus
translated network/server Retry states.

### LessonView

Treat this as a learning workspace, not another marketing hero. At desktop use a
288px curriculum rail plus a centered reading pane; avoid an additional global
left rail or mandatory right sidebar. The article has module/lesson position,
title, completion state, material, protected images, assignments, quizzes,
completion action and previous/next navigation in a predictable order.

Below the rail breakpoint, show curriculum as an accessible in-flow disclosure
before the article. Keep reading controls and current lesson visible without
pinning multiple bars. Collapse long outlines; preserve current lesson and
completed-item semantics. Long URLs/code wrap or scroll internally.

Use existing protected blob-image loading and authored alt-language behavior;
never insert public storage URLs. A quiz stays a semantic form with native
radio/checkbox groups, explicit submit confirmation, correct error focus,
server-graded results and accessible attempt history. Lesson completion and quiz
passing remain separate, server-confirmed facts. No optimistic progress success.

### Profile

Use a compact account header, real analytics cards, then the activity calendar.
Place **My Learning** and **My Applications** in clearly separate sections.
Learning cards prioritize confirmed progress and next lesson; applications show
status and existing reviewer explanations. Keep useful refresh/error states.

Preserve the GitHub-style annual overview and roving keyboard navigation. The
calendar owns its horizontal scroll inside the card, with an accessible name and
visible scroll affordance; the page itself never overflows. Dense day targets
should be at least 24px, with a readable selected-day detail and 44px previous/next
controls on mobile. Do not invent streak awards, rankings or mastery scores.
All private UI still resets on session generation, not on ordinary JWT refresh.
The annual grid will intentionally be wider than mobile (53 columns at 24px is
at least 1272px before gaps). Previous/next view controls scroll that existing grid
only; they do not request data, change analytics or replace current Arrow/Home/End
keyboard semantics. Preserve the selected day and its readable detail.

## 5. Component inventory

| Family | Reuse/evolve | Required states and contracts |
|---|---|---|
| Shell | Header, Footer, ThemeToggle, LanguageSwitcher, skip/main focus | Public/authenticated; both themes; compact menu with focus return; document language. |
| Foundations | Button, IconButton, Link, Field, Textarea, Select, Badge, Surface | Primary/secondary/ghost/danger; default/hover/focus/active/disabled/busy; labels and errors. |
| Feedback | LoadingStatus, Skeleton, EmptyState, ErrorState, Retry, dialog | Distinguish missing/forbidden/expired/offline/server states; preserve recovery and focus. |
| Discovery | Hero, SignalGraphic, DirectionChip, CatalogFilters, CourseCard | Original/decorative art; real data; no-data/no-results/reset; keyboard navigation. |
| Course | CourseSummary, AccessPanel, CourseEnrollment, CourseCurriculum | All existing policy/application states, public preview, enrolled links, disclosure semantics. |
| Reviews | CourseReviews, rating display, own-review form, DeleteDialog | Anonymous/enrolled; moderated pending; edit/delete confirmation; session-bound data. |
| Learning | LessonCourseSidebar, reading header/material, ProtectedLessonImage | Current/completed/locked; protected fetching/loading/error/retry; alt + `lang`; cleanup. |
| Assessment | LessonQuiz, QuizQuestion, results, attempt history | Unpublished/unavailable; answering/submitting/error; server feedback; separate lesson completion. |
| Profile | AccountHeader, analytics cards, LearningActivityCalendar, learning/applications | Real metrics, empty/error/refresh, accessible day detail, session reset. |
| Motion | Existing Reveal and Motion foundation | Optional entrance/hover/disclosure; static reduced motion; no auth-state animations. |

Primitives should be presentation wrappers around current behavior, not rewrites of
API utilities or form state machines. Keep the existing dependencies; no new UI,
animation, charting or 3D library is necessary for this proposal.

## 6. Responsive and accessibility strategy

| Width | Proposed behavior |
|---|---|
| 320–639px | One column; 16px gutters; 64px header; natural-flow filters/access panel; full-width primary action where useful; compact decorative art. |
| 640–1023px | Two catalog columns when 300px/card fits; stacked course access; in-flow lesson curriculum; 24px gutters. |
| 1024–1439px | 12-column shell; two or three catalog columns by available width; course access aside; lesson rail only when at least 65ch reading width fits. |
| 1440px+ | 1280px max-width; three catalog columns; generous page rhythm without stretching reading text. |

At 200% text zoom, allow the layout to collapse based on available content width.
Test EN/RU/KK, 30–40% expanded labels, long real titles and names, browser font
fallback, and 320/375/768/1024/1440px. Avoid fixed heights on text-bearing cards.
Use native controls first, persistent labels, semantic headings, meaningful
alternatives and visible 3px focus outlines with 3px offset. No essential hover-only
information; hover effects require a fine pointer. Status is not color-only.

Preserve current theme choice and system preference logic. Do not force existing
users into a new default theme. Both themes get a full design review; changing
the canvas alone is insufficient. Every new UI string belongs in all three
dictionaries, with dates/numbers continuing through Intl/i18next. Course content
is not translated or rewritten by this work.

## 7. Animation plan — proposed, not observed reference effects

| Interaction | Proposed motion | Reduced-motion/mobile behavior |
|---|---|---|
| Buttons/links | 120ms color/border feedback | Immediate feedback; no movement required. |
| Course card hover | 160ms, lift at most 3px, modest border emphasis | No lift on touch or reduced motion; focus remains obvious. |
| New section entrance | 240ms opacity + at most 12px translate; 40ms stagger, total delay ≤160ms | Visible immediately; never gate access to content or anchors. |
| Hero signal illustration | Optional single 480ms line/node appearance after text is visible | Static complete graphic; no loop or blocking sequence. |
| Curriculum/disclosure | 200ms with `aria-expanded`, `aria-controls`, inert hidden panel | Immediate open/close with intact semantics and focus. |
| Mobile menu | 240ms transform/opacity with focus management | Immediate presentation; Escape/inert/return-focus work identically. |
| Progress/results | Optional 200ms fill after confirmed response | Immediately render true value; no fabricated counter roll-up. |
| Theme switch | 120ms color transition if comfortable | Instant under reduced motion; preserve focus and layout. |

Primary easing: `cubic-bezier(0.2, 0.8, 0.2, 1)`. Avoid scroll-jacking, magnetic
buttons, pointer followers, looping decorative motion, text-scramble effects,
expensive full-screen blur, and authentication-dependent exit transitions.
Do not hold old private UI onscreen while an exit animation runs after logout.

Use the already-installed Motion library and CSS. Content must be usable before
animation setup. Prefer transform/opacity, cancel on unmount, animate neither
scroll position nor layout on every React render, and stop offscreen work.
Entrance effects run once per relevant mount; a token refresh must not retrigger
them. Keep the page readable if animation setup fails.

## 8. Functional preservation and acceptance

- Keep all backend URLs, payloads, authorization, approval and grading logic.
- Retain App's session-generation boundaries on Profile/CourseDetail/LessonView,
  old-response/retry guards and same-account refresh behavior.
- Keep public course reads anonymous; reviews, progress, images and quiz data
  remain session-bound. Do not encode tokens in image links.
- Keep enrollment applications/history, reviewer notes, completion timestamps,
  next-lesson behavior and profile metrics sourced from existing responses.
- Preserve authored alt text, decorative alternatives and the optional private
  metadata workflow from the pending UX fixes.
- Do not create or modify courses, lessons, attempts, enrollment or progress as
  part of implementation or browser validation. Use intercepted fixtures and
  isolated Django test databases for stateful regression tests.

Performance gates for implementation: no new mandatory 3D/video asset or library;
hero artwork budget around 40KB compressed; intentionally subset/self-host font
assets without dropping Kazakh glyphs; reserve artwork dimensions; keep the hero
text/CTA immediately available. Target p75 LCP ≤2.5s, CLS ≤0.1 and INP ≤200ms when
field data becomes available. These are future targets, not measurements of either
site today; see [Core Web Vitals definitions](https://web.dev/articles/vitals).
Establish repeatable lab baselines before setting regression budgets.

## 9. Step-by-step implementation after review

1. **Approve the direction and evidence.** Review desktop/mobile shell, palette,
   actual Kazakh typography samples, the five page compositions and motion/static
   alternatives. Preserve the earlier uncommitted UX work before beginning V2.
2. **Freeze behavior baselines.** Capture fixture states for authentication changes,
   API errors, every enrollment state, lesson/completion/quiz results, reviews and
   profile analytics. Record screenshots in both themes and three locales.
3. **Add V2 semantic tokens and primitives.** Map legacy aliases temporarily;
   migrate one scoped component at a time. Avoid a global CSS replacement that
   changes Catalog/Profile/shared `.academic-course-grid` unexpectedly.
4. **Deliver the shared shell.** Compact desktop/mobile navigation, language/theme
   controls, dialogs/focus and loading/error components. Keep route contracts.
5. **Homepage and catalog.** Introduce the original hero/short workflow, immediate
   catalog entry, filters and subject-differentiated cards. Confirm query state
   persists across account switches and ordinary refresh does not refetch.
6. **CourseDetail.** Migrate overview, curriculum and access panel while testing all
   existing policy states, genuine 404/Retry, application focus and moderated reviews.
7. **LessonView.** Migrate the reading workspace, curriculum and assessment surfaces;
   rerun protected-image, session-isolation, completion and quiz regressions first.
8. **Profile.** Migrate account/learning/application sections and real analytics;
   preserve calendar keyboard interaction, day detail, source counts and empty states.
9. **Motion and hardening.** Add optional motion only after the static pages pass.
   Run keyboard, screen-reader-oriented semantics, reduced-motion, zoom, locale,
   touch, contrast and overflow checks. Finish frontend tests/lint/build and relevant
   Django checks. Ask frontend/security/browser specialists to review the final diff.
10. **Approve release.** Review representative actual screenshots and regression
    results. No commit, push or deployment is implied by this planning task.

Each step must remain reviewable and reversible. A route split, additional data
field, remote media delivery change or unsupported product claim is a separate
decision, not a dependency hidden in a styling phase.

## 10. Independent critique and final evidence

Native `frontend_reviewer` and `browser_qa` agents ran independently. Neither found
a blocker to reviewing this direction. Their proposal refinements were accepted:

- **Frontend reviewer:** explicit narrow/zoomed-header fallback; mobile typography
  and semantic state recipes; calendar controls scroll existing content only;
  direction chooser reuses existing filter state. Its flat-color review confirmed
  stated functional contrast targets, with light teal/raised at approximately 4.52:1.
- **Browser QA:** mobile section-heading and inverse-hover tokens; measured anchor
  clearance; two-viewport catalog goal tested with long RU/KK and normal motion;
  cap/omit decorative mobile art. It confirmed the separation of observed reference
  transitions from proposed effects.

The public preview showed seven real courses and the existing 15-lesson/five-module
AI Fundamentals overview, with anonymous curriculum previews and locked lesson
links. No horizontal overflow was observed at 1440px or 375px. Fresh proxied public
pages had no console/network errors; that does not clear the separate port-5173
failure. EN dark and KK dark/reduced-motion public views were also inspected.
Protected-page visual validation, assistive-technology testing and future V2
performance measurements remain implementation-stage checks.

### Screenshot index

All files below are Firefox captures of existing sites, not V2 mockups. Desktop
captures use 1440×1000 and mobile captures 375×812. The same-checkout preview uses
real anonymous public API responses through the temporary GET-only proxy.
Final catalog screenshots use reduced motion to show settled cards; normal-motion
hover behavior was inspected separately. This does not prove the future V2
two-viewport goal or mobile animation behavior.

| Capture | Desktop | Mobile |
|---|---|---|
| Reference hero | [Desktop](../../.playwright-mcp/v2-2026-10-15-reference-desktop-hero.png) | [Mobile](../../.playwright-mcp/v2-2026-10-15-reference-mobile-hero.png) |
| Requested localhost:5173 — blank/import failure | [Desktop](../../.playwright-mcp/v2-2026-10-15-local-desktop-hero.png) | [Mobile](../../.playwright-mcp/v2-2026-10-15-local-mobile-hero.png) |
| Same-checkout preview: homepage | [Desktop](../../.playwright-mcp/v2-2026-10-15-local-preview-desktop-hero.png) | [Mobile](../../.playwright-mcp/v2-2026-10-15-local-preview-mobile-hero.png) |
| Same-checkout preview: catalog | [Desktop](../../.playwright-mcp/v2-2026-10-15-local-preview-desktop-catalog.png) | [Mobile](../../.playwright-mcp/v2-2026-10-15-local-preview-mobile-catalog.png) |
| Same-checkout preview: CourseDetail | [Desktop](../../.playwright-mcp/v2-2026-10-15-local-preview-desktop-course-detail.png) | [Mobile](../../.playwright-mcp/v2-2026-10-15-local-preview-mobile-course-detail.png) |
| Same-checkout preview: curriculum | [Desktop](../../.playwright-mcp/v2-2026-10-15-local-preview-desktop-curriculum.png) | [Mobile](../../.playwright-mcp/v2-2026-10-15-local-preview-mobile-curriculum.png) |

Additional reference evidence: [mobile menu](../../.playwright-mcp/v2-2026-10-15-reference-mobile-menu.png),
[mobile description](../../.playwright-mcp/v2-2026-10-15-reference-mobile-description.png),
[desktop schedule](../../.playwright-mcp/v2-2026-10-15-reference-desktop-schedule.png),
[FAQ collapsed](../../.playwright-mcp/v2-2026-10-15-reference-desktop-faq-before.png)
and [FAQ expanded](../../.playwright-mcp/v2-2026-10-15-reference-desktop-faq-after.png).

Local preference evidence: [EN dark hero](../../.playwright-mcp/v2-2026-10-15-local-preview-mobile-hero-en-dark.png),
[dark CourseDetail](../../.playwright-mcp/v2-2026-10-15-local-preview-mobile-course-detail-dark.png)
and [KK dark reduced-motion journey](../../.playwright-mcp/v2-2026-10-15-local-preview-mobile-journey-kk-dark-reduced.png).

The two `*-catalog-cors-error.png` files are diagnostic captures from an earlier
temporary-preview configuration, not representative working catalog screens.
Use the indexed final catalog captures for comparison.

This document is not authorization to start implementation. No application source,
course content, database records, dependencies or running user server were changed.
The temporary preview was stopped after capture. A SHA-256 comparison of 197
baseline source/document/database/media files found no changes. Proposal JSON
parsing and all local document links were validated. Existing uncommitted UX fixes
remain untouched; builds/tests were not run for this documentation-only phase.
