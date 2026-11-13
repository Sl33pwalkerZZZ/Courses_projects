# AI Courses UI refinement — 2026-11-03

Method: [Unslop](../.agents/skills/unslop/SKILL.md) by
[Damir Sokolovsky (@heydamir)](https://heydamir.design/unslop),
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). This report adapts its
five-part direction and nine-pass methodology. The installed skill was used;
no skill, library, browser or dependency was installed.

## Recovery and assessment

Branch `design/amethyst-motion` had extensive existing Phase 5A video and Phase
5B/C source/import work, Module 4 experiments, intentional settings changes and
local source assets. None were reset, staged or deleted.
Verified recoverable frontend archive:
`.local-redesign-checkpoints/frontend-before-unslop-20261103-100120.tar.gz`.
Archive includes frontend source, tests, package files and Vite config. It is not
a database backup and was not staged. Database and settings checksums match the
start of this task; backend, migrations and course data were not edited.

Assessment: **light slop**, from source review; not a judgment based on invented
browser evidence. Strong foundations retained: Noto Sans, Amethyst accent, dark
canvas #16181c, semantic colors, functional filters/routes, translated controls,
focus rings, native dialogs, protected media and session isolation.

## Original findings and disposition

| Page/component | Evidence in source | Refinement |
|---|---|---|
| Homepage | `HomeHero.jsx`: particle field, letter-reactive heading, companion; `amethyst-motion.css`: radial wash | Static readable title, concrete AI learning copy, numbered learning-format diagram |
| Introduction | `SignalStory.jsx`: opacity-layered chapters, decorative orbit; CSS reserves 240svh | Existing static three chapters on every viewport; no scroll gate or duplicated accessible copy |
| Catalog | `CourseCard.jsx/css`: repeated entrance/layout movement, hover lift and filled accent tiles | Immediate card rendering, quiet icon tiles, border feedback; actual course data/reviews retained |
| Shared controls | `ui.css`: button lacks width/wrapping constraints | Long RU/KK labels wrap inside available space |
| CourseDetail | `CourseDetail.css`: 750-weight tight headings; radial wash | 600-weight headings, calmer tracking and neutral surfaces; enrollment/error logic unchanged |
| Lesson reader | `LessonView.css`: 9.6–12px metadata; sticky sidebar top24 under sticky header | Metadata at least13px, header-aware sticky position and height, 40px reading/sidebar gap |
| Profile | `Profile.css`: tiny metadata and irregular18/22px spacing; radial wash | Readable metadata, 16/24px rhythm, neutral heading surface; real charts and progress retained |
| Instructor Studio/curriculum | `instructor.css`: filled accent navigation, one-off panel radius | Neutral active tabs with accent underline; shared panel radius and consistent navigation padding |
| Login/Register | `AuthLayout.jsx`: particle/companion decoration, vague welcome copy | Learning-format preview, specific translated headings; preview hidden in compact auth layout so form stays prominent |
| Video/attachments | Attachment radius fallbacks diverge from shared system | Shared radii, separated transcript, readable status/error panel; player/auth/subtitles untouched |
| Footer | `Footer.css`: perpetual orbit and 10.56px information | Static mark, readable13px information; branding/links preserved |

These are source-confirmed design traits and potential layout risks, not observed
browser failures. Protected pages were source-reviewed, not logged into.

## Five-part direction

- **Product:** practical AI skills learned through explanations, practice and feedback.
- **Character:** calm, precise, encouraging.
- **World:** a digital study desk, with course material in focus.
- **Moments:** actual learning content and real progress, rather than decorative chrome.
- **Signature:** a numbered learning sequence used in the format preview and existing curriculum.

Amethyst remains the accent. Neutral light surfaces replace pervasive lavender;
no third brand, new font, generated stock visual or unsupported feature claim.

## Nine passes, in order

1. **Spacing:** shared control gap8px; Profile16/24px rhythm; lesson32/64px outer
   spacing, 40px reading gap; Studio12/16px navigation. Existing educational tables
   and dense content retain their useful proportions; this is not a claim that
   every legacy spacing value was normalized.
2. **Color:** light canvas #F8F9FA, white cards, raised #F0F1F4, graphite text;
   purple accent retained. Dark #16181c unchanged. Remove repeated radial washes
   and ambient layer rendering. Existing semantic status colors retained.
3. **Icons:** use existing Lucide set; learning preview18px/1.5stroke, replace
   auth sparkle with BookOpen, quiet subject tile fills. Not a global icon rewrite.
4. **Copy:** translated, specific AI study/work headline replaces generic slogan;
   meaningful auth headings, no internal DIGITAL PLAYGROUND / AMETHYST label.
   Preview caveat makes course-dependent formats explicit. No course text changed.
5. **Typography:** preserve Noto Sans; supporting headings600, less tight Cyrillic
   tracking; increase small Profile/lesson/Footer metadata. No new font downloads.
6. **Layout:** static three-step introduction eliminates240svh scroll narrative;
   shared wrapping guards narrow actions; lesson outline accounts for header.
7. **Details:** shared16px cards/20px hero/8px badges; Studio selection is a quiet
   surface and underline; transcript/error framing improves attachment hierarchy.
8. **Visuals:** a real learning-format diagram replaces generic hero/auth companion
   and particles; no fake learner data, invented success metrics or stock assets.
   Original companion and SVG files remain available locally and in existing tests.
9. **Motion:** remove per-card entrance/reflow animation and hover lift, animated
   hero lettering and scroll-bound story; static ambient/footer. Preserve purposeful
   auth entrance, menu/input feedback and reduced-motion support. Existing unrelated
   educational animations remain intact.

## Exact files changed by this task

Frontend source:
- `frontend/src/components/AmbientBackground.jsx`
- `frontend/src/components/AuthLayout.jsx`, `AuthLayout.css`
- `frontend/src/components/CourseCard.jsx`, `CourseCard.css`
- `frontend/src/components/Footer.css`
- `frontend/src/components/Header.css`
- `frontend/src/components/HomeHero.jsx`, `HomeHero.css`
- `frontend/src/components/LearningPreview.jsx`, `LearningPreview.css` (new)
- `frontend/src/components/learning/lessonAttachments.css` (preserves existing video additions)
- `frontend/src/components/motion/SignalStory.jsx`
- `frontend/src/components/ui/ui.css`
- `frontend/src/i18n/locales/{ru,kk,en}.json` (preserves existing video translations)
- `frontend/src/index.css`
- `frontend/src/pages/{CourseDetail,LessonView,Profile}.css`
- `frontend/src/pages/instructor/instructor.css`
- `frontend/src/styles/{amethyst-motion,v2-tokens}.css`

Tests: `frontend/tests/auth-design.test.mjs`,
`frontend/tests/design-foundations.test.mjs`, `frontend/tests/unslop.test.mjs` (new).
Documentation: this report. No application API/auth code changed by this task.

## Verification and evidence limits

Native `frontend_reviewer` ran initial and post-change read-only source reviews.
Its mobile auth-preview regression was corrected: preview hidden <=900px.
Native `browser_qa` actually attempted Playwright MCP Firefox. It failed because
configured revision1569 is missing. An existing revision1553 was tried without
installation; it is incompatible with the installed Playwright protocol
(`Browser.setDownloadOptions.legacyInterceptor`). No screenshots were captured.
The dev server also cannot bind localhost in the sandbox (EPERM).

Therefore no live1440/768/390/320px screenshots, responsive overflow assertions,
keyboard traversal, console/network clearance or real private-flow passes are
claimed. Screenshots/browser artifacts were not staged. Browser checks need a
compatible Firefox/Playwright pair and running local servers; no automatic setup
changes were made.

SSR regressions cover actual translated components in RU/KK/EN, immediately
readable preview/story, native form/link semantics and existing protected-media
logic. Shared palette tests enforce4.5:1 normal text/link/button contrast and
existing tests retain3:1 control-border contrast. These checks cannot establish
contrast over external images or prove visual layout in a browser.

Final validation: `node --test tests/*.test.mjs` passed all 32 test files;
`npm run lint` passed; `npm run build` passed; `git diff --check` passed.
No npm `test` script exists, so the established Node test runner was invoked directly.
Tests use isolated SSR caches, not the development optimized-dependency cache.

## Remaining work

- Run real viewport/theme/language and keyboard checks with compatible Firefox,
  including authenticated Profile, Studio/curriculum and real video seeking/subtitles.
- Consider further consolidation of legacy small labels/radii only after visual
  inspection; avoid flattening useful learning content or activity-chart semantics.
- No course data, educational materials, accounts, publication or certificates
  were changed. No commit/push/deploy performed.
