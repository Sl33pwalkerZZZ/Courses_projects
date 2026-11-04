# Cinematic landing — Phase 1

2026-11-03, branch `design/amethyst-motion`. Landing-only implementation;
Unslop was not invoked. No backend, SQLite, course content, private page, auth,
protected video or shared Header/Footer changes.

## Recovery

Verified create-only checkpoint:
`.local-redesign-checkpoints/frontend-before-cinematic-20261103-103631.tar.gz`.
It retains source/tests/package files/Vite config including existing uncommitted
video work. Exact file comparison against it identifies the changes below.

## Direction and implementation

A spatial learning desk: oversized Cyrillic-capable Noto Sans type, restrained
Amethyst highlights, fine grid, particles and a course-overview plane. The plane
shows an actual public catalog course, not a fake personal dashboard. On desktop
it responds to the pointer using bounded spring-driven X/Y rotation; on mobile
and reduced-motion it is stable. Empty/loading/error states retain readable
explanations and working catalog CTAs.

The showcase lets students select up to four actual public course summaries.
Native buttons expose aria-pressed, selection announces the course title, and
links include that title in their accessible names. No invented completion,
module counts, reviews, enrollment numbers or outcomes are displayed. Current
local public catalog has one course, so real-data multi-course switching needs
additional published courses; synthetic component tests cover the reusable UI.

Catalog single GET, search, direction/level filtering, reset, retry and CourseCard
navigation remain intact. Existing animated CourseCards, AnimatedText, ParticleField,
SignalStory, LearningWorkflow reveals and shared footer animation are retained.
SignalStory now follows discovery so the existing course catalog remains directly
reachable. Final CTA uses actual catalog and registration routes.

Inspiration was inspected from the official [React Bits](https://reactbits.dev/)
and [Aceternity UI](https://ui.aceternity.com/) sites. The implementation uses the
existing Motion/Lucide stack, not copied templates or installed component libraries.

## Motion and accessibility

- Existing pointer-reactive title typography retained; no per-letter API work.
- Transform-only visual entrance, .8s ease-out.
- Course-plane depth bounded to7/9degrees, fine-pointer desktop only; reset on
  leave/cancel, hidden tab/viewport; reduced-motion gets no depth transform.
- Existing scroll progression and reveal systems retained; no new infinite loops.
- Real text remains rendered, controls are native links/buttons, decorative
  layers do not intercept input. Course title/description wrap on small screens.
- Scoped `.cinematic-landing`/`.cinema-*` CSS; shared theme tokens unchanged.

## Exact implementation files

Modified:
- `frontend/src/components/HomeHero.jsx`
- `frontend/src/pages/CourseCatalog.jsx`
- `frontend/src/i18n/locales/en.json`
- `frontend/src/i18n/locales/ru.json`
- `frontend/src/i18n/locales/kk.json`
- `frontend/tests/design-foundations.test.mjs`

Created:
- `frontend/src/components/landing/DepthSurface.jsx`
- `frontend/src/components/landing/LandingCoursePreview.jsx`
- `frontend/src/components/landing/LearningShowcase.jsx`
- `frontend/src/components/landing/ClosingInvitation.jsx`
- `frontend/src/styles/cinematic-landing.css`
- `frontend/tests/cinematic-landing.test.mjs`
- This document.

Local-only QA files: `.local-cinematic-qa/` (self-ignored, browser binary,
checkpoint preview, scripts); `.playwright-mcp/cinematic/` (screenshots/results).
No application dependencies or project configuration were changed. Do not stage
browser binaries, screenshots or the checkpoint preview.

## Verification

Native `frontend_reviewer` performed read-only initial/final source reviews.
No blocking source regression found; its two link/selection accessibility suggestions
were implemented. Native `browser_qa` reviewed actual Chromium captures/results
without launching a competing Firefox instance. Main agent executed Chromium. Screenshot review found a mobile closing ornament
overlapping CTA labels; the ornament is now hidden below640px and the matrix was
rerun after that correction.

Configured MCP Firefox remains unavailable. For this task only, existing cached
Playwright tools downloaded headless Chromium1252 into `.local-cinematic-qa`.
LMDE7 detection selected unsupported Ubuntu20.04; a supported Ubuntu24.04 build
was explicitly selected for local testing. No system packages or npm application
dependencies were installed. This local QA fallback is not a deployment change.

Before screenshots are the actual checkpoint served separately at5180. After
screenshots are the working frontend served at5174. Those extra ports are outside
local backend CORS allowlists. Browser-only GET interception fetched the actual
public API response and added CORS headers for these preview origins; no mocked
courses and no settings changes. Mutating API requests were blocked. This does
not verify deployment CORS or private/authenticated flows.

Before/after screenshots at1440/768/390/320 and results:
`.playwright-mcp/cinematic/{before,after}-{1440,768,390,320}.png`, `results.json`.
Corrected real-data pass: one course card at every width, no horizontal overflow,
no page/console errors or failed requests; reduced depth transforms `none`.
Early screenshots with unavailable catalog were overwritten by the corrected pass.

A first fullpage capture did not reach every reveal because smooth scrolling
intercepted rapid test scrolls. Final matrix uses explicit instant scrolls and
checks computed visibility of workflow/closing sections; screenshots from that
pass are named `after-{ru,kk,en}-{light,dark}-{1440,320}.png` where captured.
Final matrix: 24 combinations (RU/KK/EN × light/dark ×1440/768/390/320)
passed with no horizontal overflow and no hidden workflow/closing sections.
`matrix-results.json` records no page/console errors, actual pointer matrix3d
response, reduced-motion transforms `none`, working search/clear and a visible
keyboard focus outline. This is a focus smoke check, not an exhaustive keyboard audit.

Tests: established Node runner `node --test --test-concurrency=2 tests/*.test.mjs`
passed32files; `npm run lint`, `npm run build`, `git diff --check` passed.
SSR coverage includes translated actual course fields, escaped text, native
links/buttons and safe loading/empty/error states. Existing session, enrollment,
lesson/video, quiz, Studio and catalog tests remained in the run.

## Limitations

- Real published catalog currently has only one course; multi-course selection
  cannot be demonstrated with real public data without publishing more courses.
- No login, enrollment submission, private preview or database mutation tested.
- Automated screenshots and computed styles do not replace author visual review
  or measure performance across all hardware. Full-page images include long
  existing scroll-story sections, intentionally retained.
- No commits, pushes, publication or deployment; Instructor Studio unchanged.
