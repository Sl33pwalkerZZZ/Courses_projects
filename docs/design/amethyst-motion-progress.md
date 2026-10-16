# Amethyst Motion Experience

Branch: `design/amethyst-motion`. Implementation authorized; no commit/push. Existing `.gitignore` recovery rule preserved.

Status: implementation and validation complete. Changes remain uncommitted for review. All three native agents ran: frontend_reviewer, security_reviewer and browser_qa. No remaining blocking source or browser finding.

## Safety and inspection

- [x] Current branch/worktree and existing Digital Playground infrastructure inspected.
- [x] Source-only checkpoint: `.local-redesign-checkpoints/amethyst-before-20261016-101103.tar.gz` (125 files); adjacent SHA256 manifest. No DB/media/secrets included.
- [x] Baseline source/SQLite hashes: `/tmp/amethyst-baseline.json`; no database queries or mutations.
- [x] Native frontend/security reviewers inventoried contrast, palette sources, effect lifecycle and security boundaries. All application edits owned by root.
- [x] Figma nodes 2:2 and 2:37 inspected with screenshots/high-fidelity context; 14 original SVG layers downloaded locally with intrinsic dimensions preserved.
- [x] Actual Firefox live-reference and local-baseline inspection performed by browser_qa.

## Implementation checklist

- [x] Semantic purple palettes across all routes, inverse surfaces, aliases, Canvas, heatmap and overlays. Dark primary buttons use dark ink for readable contrast; text links use the lighter accent.
- [x] Nonblocking first-entry signal sequence; short subsequent entrances.
- [x] Header-aware sticky scroll story with springs/transforms, real directions and readable mobile/reduced fallback.
- [x] Local-asset SVG AI companion: bounded eyes/head springs, button expression, blink/idle pause, static reduced mode.
- [x] Grapheme-safe AnimatedText with unsplit accessible text, bounded spring response and word wrapping.
- [x] Cohesive course/auth/lesson/quiz/Profile/global-state presentation without functional logic changes.
- [x] Regression tests: all 15 frontend test files pass; lint and production build pass; Django check reports zero issues. Actual rendered CSS contrast and grapheme/accessible fallback coverage added.
- [x] Firefox 168-case route/width/locale/theme matrix, actual mouse/scroll/frame sequences and synthetic application/quiz/review/completion/session flows. Supplemental public/auth/accessibility fixtures and visibility-event checks completed, with the real hidden-tab limitation below.
- [x] Independent final frontend/security reviews, integrity comparison, screenshot/file index and limitations.

## Observed references versus our additions

Observed in the actual Astana Hub site: white/black/violet structure, OktaNeue 52/57.2px weight-800 hero, 256px sidebar; hero reveal 850ms with 80/220ms delays; 8s idle glow; 7s/6s floating cards; 5.5s quote progression; 600–750ms slides; 300ms button transitions; violet hover shadow. Body is its scroll container; header/sidebar stick. Forward/back scroll frames saved.

Dribbble: 54.98s video presentation, not a runnable experience. Sampled frames show an evolving violet ring, navigation highlight, lifted card, dark workflow cards, scroll to Contacts/back. No public live portfolio URL found on shot/creator/about. These frames do not establish actual pointer physics or scroll timing.

Our creative additions: host-scoped cursor-watching companion, grapheme letter springs, original SVG constellation entry with a separate ambient Canvas field, evolving learning pathway tied to normal document scroll, theme-aware violet surfaces throughout. No reference branding or screenshot is used as a runtime asset.

## Verification results

- Native frontend and security reviewers completed their final source reviews: no remaining blocking finding. Frontend review identified theme effect ordering and long-word wrapping risks; both fixed.
- Actual Firefox has observed the companion following left/right pointer movement, bounded pupil/head movement, button expression, return to rest, blink, letter lift/rest without heading layout shift, live Canvas palette change, and scroll chapters 01 → 02 → 03 → 02 → 01.
- Live reduced-motion changes use one shared reactive media-query subscription. Firefox verified that Canvas, interactive letters, the entry sequence and sticky story are replaced immediately. Theme DOM updates happen before Canvas palette sampling.
- First full motion fixture encountered a single giant Firefox wheel event that stopped short of its requested document position. The fixture now uses bounded human-sized wheel steps and verifies each scroll position; application scrolling has not been changed to accommodate a test.
- The 320px matrix found a real Kazakh static-story heading overflow: its text extended to x341.73 although the viewport was 320px. Fixed with emergency word wrapping on the static h2 and shrinkable/wrapping stage text beside icons. No clipping or hidden overflow. Independently reviewed by frontend_reviewer; the entire 320px matrix passed after the fix. Historical failure evidence: `.playwright-mcp/amethyst-overflow-320-kk.png`.
- Motion fixture: all 10 interaction groups passed, with 15 actual frame screenshots, zero React errors, zero unexpected APIs and zero real API requests. Includes native scroll ending, offscreen Canvas pause, category chip/select synchronization, mobile ambient mode and a long Kazakh heading at 901px. Entry remained nonblocking throughout (instrumented first-to-ready observation: 1479ms).
- Full 168-case matrix passed: seven routes (home/catalog, CourseDetail, LessonView/quiz, Profile, Login, Register, 404) × four widths (1440/768/375/320) × RU/KK/EN × both themes. Each width passed all 42 cases. Zero React errors, horizontal overflow, unexpected APIs or real API requests. Actual theme buttons were toggled on each EN route in both initial themes, including compact navigation. Saved 56 route/width/theme screenshots.
- Initial actual screenshots: `.playwright-mcp/amethyst-first-home-1440.png`, `amethyst-first-home-1440-dark.png`, `amethyst-first-home-375-dark.png`, `amethyst-first-story-1.png` through `amethyst-first-story-5.png`. Additional entry/eye/letter/story frame sequences use the `amethyst-motion-` prefix.
- Synthetic functional regression passed all five groups: quiz keyboard/focus/errors/pass/fail/retry, independent lesson completion/error/reload, application focus and state restoration, moderated review owner actions and dialog, genuine 404 versus server Retry, cross-tab logout and lazy-import error recovery. Nine mutations were intercepted entirely in the browser; zero real API requests, runtime errors or unrecognized API calls.
- After the 320px wrapping fix: all 15 frontend test files, lint, production build and Django check passed again.
- Targeted fixed Kazakh screenshots: `amethyst-fixed-story-320-kk-light.png` and `amethyst-fixed-story-320-kk-dark.png`. Both document widths are 320px; heading text ends at x278.58 inside its x37–283 content box.
- Actual Canvas instrumentation at device DPR 2: 24 desktop particles, 10 mobile particles; backing widths 1968/515px for 1312/343px hosts, consistent with the 1.5 DPR cap and integer rounding. Mobile drawing measured approximately 29–30 frames/second. Offscreen drawing pause was verified with unchanged Canvas pixels.
- Firefox harness limitation: opening/foregrounding another page leaves the original document `hidden=false` / `visibilityState=visible`. A genuine OS/background-tab visibility transition therefore cannot be verified here. Do not claim a real hidden-tab pass; source cleanup and any synthetic visibility-event result must be reported separately.
- A separately labelled synthetic visibility-event check passed companion/Canvas pause and resume. This exercises the listeners; it is not a real OS-tab visibility transition.
- Existing `design-foundations.mjs` passed all nine public-flow groups: search/direction/level/reset without refetch, no-results, same-hash/cross-page navigation, mobile menu focus/Escape/return, localization, 320px overflow, server Retry and empty state.
- Existing `auth-design.mjs` passed Login/Register native validation, keyboard navigation, password visibility, errors/loading, duplicate submission guards, success redirects and delayed catalog/workflow anchors. Fake credentials only; zero real authentication requests or database writes.
- Existing `ux-polish.mjs` passed all eight groups: server/network Retry versus genuine 404, application/reapplication focus and cancellation, localized informative/decorative image alt, and authenticated blob-image loading without locale refetch (two intercepted image requests).
- Final browser totals: 168 matrix cases, 10 motion groups, 5 functional groups, 9 foundations groups, 4 auth groups and 8 UX groups passed. All mutations were synthetic and intercepted. Firefox `browser_close` returned “No open tabs.” No implementation or required validation remains pending.

## Resume instructions

Read this file and current Git diff; preserve completed work/checkpoint. Root owns edits; reviewers are read-only. Browser agent exclusively owns Firefox MCP. Do not touch API/auth/session/protected-image/quiz utilities, Django or SQLite. Retain private session-generation keys and immediate unmount. Use isolated temporary Vite SSR caches. No real auth/enrollment/review/quiz/progress mutations during browser testing; use fully intercepted synthetic fixtures.

## Changed areas

- New motion components: `frontend/src/components/motion/{AICompanion,AnimatedText,DiscoveryDirections,EntrySignal,SignalStory}.jsx`, `useSceneActivity.js`; reactive preference hook `frontend/src/hooks/useMotionPreferences.js`; segmentation helper `frontend/src/utils/motionText.js`.
- Shared presentation: `frontend/src/styles/{v2-tokens,amethyst-motion,playground}.css`, `index.css`, `main.jsx`; palette sampling in `components/playground/ParticleField.jsx`; theme DOM update ordering in `theme/ThemeProvider.jsx`.
- Integrations: homepage hero/catalog; authentication illustration; generic CourseDetail/Profile headings. Existing Motion users now share the reactive preference hook, including cards, fields/errors, curriculum/sidebar, quiz questions, progress/reading/activity visuals and reveal/theme controls.
- Semantic text/fill/overlay/heatmap fixes in component/page styles: Header, Footer, AuthLayout, CourseCard, CourseReviews, HomeHero, LearningActivityCalendar, LessonQuiz, shared UI, catalog, course overview and Profile.
- Fourteen local dark/light SVG layers in `frontend/src/assets/amethyst/`; original intrinsic dimensions retained. RU/KK/EN marketing/story strings updated in the three locale dictionaries.
- Tests: `frontend/tests/amethyst-motion.test.mjs`, updated design/auth test suites, `frontend/tests/browser/{amethyst-motion,amethyst-regression}.mjs`.
- This progress report. The pre-existing `.gitignore` change was preserved, not authored by this task.

## Safety verification

Baseline hash comparison confirms all backend files and `db.sqlite3` are byte-for-byte unchanged. Dependency manifests are unchanged. `api.js`, `useAuth.js`, `App.jsx`, Login/Register logic, LessonView, ProtectedLessonImage, CourseEnrollment, LessonQuiz and CourseReviews logic are unchanged. No migrations, dependency installs, database writes, commits or pushes were performed. Source and security reviews found no new authorization/session/media exposure.

## Validation commands

Use the existing NVM Node binary directory in PATH if needed. Run from `frontend/`:

```sh
node --test tests/*.test.mjs
npm run lint
npm run build
```

All pass on the current implementation (15 frontend test files; project lint uses Oxlint). From the repository root, `.venv/bin/python manage.py check` passes with zero issues. Browser fixtures are evaluated by Playwright MCP in Firefox, not by the Node test runner. `amethyst-regression.mjs` supports width chunks using `window.__fullRebuildOptions = { widths: [375], skipInteractions: true }`, and `{ interactionsOnly: true }` for the synthetic functional flows. Browser routes block unknown API calls and prevent any fixture data from reaching Django.

## Screenshot and frame index

All paths below are under `.playwright-mcp/` in this repository. These are actual Firefox captures, not mockups. Protected routes use synthetic intercepted fixtures; no student records are shown.

| Page | Desktop light | Desktop dark | Mobile dark |
| --- | --- | --- | --- |
| Home/catalog | `amethyst-home-1440-light.png` | `amethyst-home-1440-dark.png` | `amethyst-home-375-dark.png` |
| CourseDetail | `amethyst-course-1440-light.png` | `amethyst-course-1440-dark.png` | `amethyst-course-375-dark.png` |
| Lesson/quiz | `amethyst-lesson-1440-light.png` | `amethyst-lesson-1440-dark.png` | `amethyst-lesson-375-dark.png` |
| Profile | `amethyst-profile-1440-light.png` | `amethyst-profile-1440-dark.png` | `amethyst-profile-375-dark.png` |
| Login | `amethyst-login-1440-light.png` | `amethyst-login-1440-dark.png` | `amethyst-login-375-dark.png` |
| Register | `amethyst-register-1440-light.png` | `amethyst-register-1440-dark.png` | `amethyst-register-375-dark.png` |
| 404 | `amethyst-not-found-1440-light.png` | `amethyst-not-found-1440-dark.png` | `amethyst-not-found-375-dark.png` |

The same route names also have 768px and 320px screenshots in both themes.

- First-entry frames: `amethyst-motion-entry-0.png`, `amethyst-motion-entry-1.png`, `amethyst-motion-entry-2.png`.
- Real pointer positions: `amethyst-motion-eyes-left.png`, `amethyst-motion-eyes-right.png`.
- Letter response and settling: `amethyst-motion-letters-hover.png`, `amethyst-motion-letters-rest.png`.
- Actual forward/backward scroll frames: `amethyst-motion-story-0.png` through `amethyst-motion-story-4.png` (chapters 01 → 02 → 03 → 02 → 01).
- Mobile ambient: `amethyst-motion-mobile-ambient.png`; long Kazakh animated title: `amethyst-motion-long-title-901.png`.
- Corrected narrow Kazakh layout: `amethyst-fixed-story-320-kk-light.png`, `amethyst-fixed-story-320-kk-dark.png`.
- Functional states: `amethyst-quiz-passed.png`, `amethyst-quiz-retry.png`, `amethyst-enrollment-{pending,rejected,approved}.png`.
- Reference captures: `amethyst-reference-astana-*` and `amethyst-reference-dribbble-video-{0,2,4,7,18,30,42,52}.png`. Dribbble captures are presentation frames, not live-site interaction evidence.

Historical `amethyst-motion-failure.png` and `amethyst-overflow-320-kk.png` predate the passing reruns and are retained as diagnostic evidence.
