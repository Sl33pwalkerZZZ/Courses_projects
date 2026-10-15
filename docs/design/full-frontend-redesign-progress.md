# Complete frontend rebuild — Digital Playground

**Status: implemented and validated.** Branch: `design/ai-courses-v2`. All changes remain uncommitted for review. No commit, push or merge.

## Preservation and recovery

- [x] Existing unfinished authentication work inspected and preserved.
- [x] Source-only checkpoint: `.local-redesign-checkpoints/frontend-20261015-112926.tar.gz`, adjacent SHA256 manifest.113 intended source/test/doc files; no database, media, secrets, screenshots or environment files. Checkpoint directory ignored by Git.
- [x]107 protected baseline files unchanged, including byte-identical `db.sqlite3`; backend and dependency manifests unchanged. No migrations, seeds, content/progress/enrollment/quiz mutations or installations.
- [x] Critical frontend API/auth/session/protected-image/enrollment/review logic and quiz validators/submission utilities remain byte-identical to the source checkpoint.

## Existing feature/state inventory — preserved

| Area | Contracts / states |
|---|---|
| Global | Session-generation keyed private trees, cross-tab account isolation, single-flight JWT refresh, obsolete response/retry rejection, main focus/skip link, lazy pages, RU/KK/EN + Intl, persisted light/dark preferences, mobile modal Esc/focus return. |
| Catalog | Public real course API, title+description search, direction/level filters and locale sorting, counts/reset, skeleton, no courses/no matches, network Retry, course links. |
| Auth | Native required/length/email checks; optional email; autocomplete, password visibility, busy/disabled, HTTP/network errors; registration then JWT login; existing redirects. |
| Course | Public description/direction/author/rating/module/lesson metadata; true404 distinct recoverable errors; anchors; curriculum/all expansion; preview locked vs confirmed enrollment links. |
| Enrollment | Anonymous, loading/error/Retry; open immediate; pending; approved-needs-refresh; rejected/reason/reapply; enrolled/no lessons; 20–1000 message; explicit form open/cancel focus; server-confirmed updates/history. |
| Reviews | Public approved + private own review; no rating; enrolled-only native rating+text form; pending/approved/rejected; owner edit/delete and modal confirmation; error/Retry; edited reviews pending again. |
| Lessons | Signed out/403/404/network; authenticated blob images/localized informative or decorative alt; reading/assignments; outline/progress separate errors; native mobile disclosure/current/completed; completion only after server confirmation; independent quiz; previous/next/end links; authorized staff preview cannot complete without enrollment. |
| Quizzes | None/unpublished/load/access/errors; single/multiple native choices, question navigation/focus, answer progress, missing-answer focus; confirmation; stable UUID retry; server-only grading/feedback; pass/fail/retry; owner latest/best/count/paginated history. |
| Profile | Account/email/role/refresh; real enrolled progress/next/completed/no lessons; separate application history/dates/reasons/reapply; independent activity load/error; real totals/streak/days/timezone; annual grid/internal scroll/roving keyboard. |


## Completed implementation

- [x] Shared token bridge and global components; dark/light palette, sans typography, consistent controls/cards/dialogs, translated loading/error boundary/404.
- [x] Homepage/catalog: original interactive network, transform-only title/route entrances, generated per-course subject SVGs, card/filter position transitions, clear discovery/workflow, existing search/filter/reset/retry states.
- [x] Authentication: preserved unfinished V2 forms/handlers, cohesive signal scene, native validation/autocomplete/password visibility, loading/error/focus feedback and redirects.
- [x] CourseDetail: inverse hero, real-module journey anchors, curriculum accordion, access/application states, ratings/reviews/forms/dialogs.
- [x] Lesson workspace: calm reading surface, header-aware sidebar, mobile disclosure, protected images, assignments, independent reading-position cue and server-confirmed completion feedback.
- [x] Quiz: native single/multiple choices, tactile selected states, question-text entrance, progress/confirmation/errors, real score ring/pass celebration, retry and attempt history.
- [x] Profile: account header, real course-progress rings, activity/streak metrics, real28-day activity pulse with daily-data disclosure, accessible24px annual calendar and separate application history.
- [x] Unified all-route header/footer/navigation, RU/KK/EN, both themes, reduced-motion handling and responsive layouts.
- [x] Full frontend tests, lint, build, Django check and actual Firefox verification.
- [x] Independent native frontend, security and browser reviews completed.

## Design and motion system

One palette extends the existing V2 tokens: ink `#0B1020`, light canvas `#F4F7FC`, neutral surfaces, blue `#1255D9`/`#84B7FF`, teal `#0B7A75`/`#51D6C5`. Existing semantic aliases point at this palette; old gold/cream/serif presentation is absent from rendered routes. Typography uses the existing Noto Sans/system stack. Controls use48px minimum height; icon controls remain44px; shared card/hero radii20/28px.

New reusable components in `frontend/src/components/playground/`:

- `ParticleField`: Canvas2D constellation with fine-pointer response, capped DPR/density, IntersectionObserver/tab visibility pause and cleanup. Static faint SVG for reduced motion.
- `SubjectGraphic`: deterministic course/direction-based SVG identity.
- `CourseJourney`: native anchors from actual public module metadata.
- `ReadingProgress`: decorative document-position cue, distinct from saved completion.
- `ProgressRing`: localized, bounded animation of actual API percentages.
- `ActivityPulse`: last28 actual daily counts; localized UTC dates and native data disclosure.
- `Celebration`: finite decorative particles mounted only after confirmed completion or server-reported quiz pass.

`GlobalState.jsx` supplies localized route-not-found, loading skeleton and a recoverable page error boundary. Motion route entrances do not retain exiting private trees. Session-generation keys remain intact.

Figma concept and live Astana Hub reference inspected as starting points; existing local editable signal SVGs reused. No reference branding/assets copied into new work. No new dependencies.

## Validation results

| Check | Result |
|---|---|
| `.venv/bin/python manage.py check` | Passed;0 issues |
| `node --test tests/*.test.mjs` |14 test files passed;0 failed, final run after quiz focus fix |
| `npm run lint` | Passed; existing project linter is oxlint; no warnings |
| `npm run build` | Passed; final production bundle generated |
| `git diff --check` | Passed |
| Firefox responsive/localization/themes |168/168 cases:7routes ×1440/768/375/320 ×RU/KK/EN ×light/dark;0 unexpected API routes/React page errors |
| Real public Firefox pages | Home/course/login/register/notfound at1440/375; no overflow, failed requests, console/page errors or mutating requests |
| Existing Firefox fixtures | `design-foundations.mjs`, `auth-design.mjs`, `ux-polish.mjs` all passed |
| Full isolated interaction fixture | Passed;9 synthetic mutations fulfilled locally,0 real API requests |
| Profile/calendar |1440EN,375EN,320RU/KK; disclosure no overflow; Home/End/Arrow navigation correct; weekday rail visible |
| Canvas observations | Desktop24particles/~28draws/s;375px10/~30draws/s;0 draws over500ms offscreen; reduced-motion0canvas/0draws and1staticSVG |
| Integrity |107 protected files unchanged; SQLite and manifests unchanged;0 staged files |

The interaction fixture verifies native radio arrows/Tab, checkbox Space, question/result focus, failed/confirmed quiz submission, pass/fail/retry, no premature answer feedback/celebration, independent completion failure/success/reload, application submit/reload/focus/states, pending review creation/edit/delete dialog, genuine404 versus recoverable500, logout clearing Profile, and lazy-import failure recovery through the error boundary.

Regression tests added in `playground.test.mjs`; browser fixture in `tests/browser/full-rebuild.mjs` intercepts every API endpoint before navigation and fails closed on unknown routes. No mock data is imported into the product or database.

### Findings fixed during review

- Inverse-surface light-theme focus contrast: scoped teal outline and inset journey focus.
- New number/date formatting: Intl percentages and UTC-localized dates.
- Reduced-motion fallback artwork: faint stroke preserves text clarity.
- Calendar rail: masks6px scrolling inset; scroll hint visible at all widths. A partially visible column at the scroll edge is normal internal scrolling, with weekday labels and focus unobscured.
- Motion tap labels: explicit negative tabindex prevents extra tab stops beside native controls.
- Quiz Next focus: preserve native fieldset/legend DOM and animate only question text. Actual Firefox regression now passes.

### Independent reviewers that actually ran

- Native `frontend_reviewer`: inventory, source/diff review, desktop/light+dark and375/320 screenshot critique, final native quiz-focus structure review. No remaining supported High/Medium finding.
- Native `security_reviewer`: API/policy inventory and final implementation review; no confirmed security regression. Auth/session keys, protected blobs, server-confirmed completion/grading, enrollment/reviews remain intact.
- Native `browser_qa`: actual Firefox MCP, public/reference screenshots, full matrix, functional fixtures, calendar/disclosure/motion checks. Explicitly closed MCP browser at end to release its profile.

All reviewers were read-only; root owned application edits. No fallback role impersonation or invented browser evidence.

## Firefox screenshots

Protected Lesson/Profile and enrolled Course screenshots below use isolated synthetic responses. Real public course/home/auth screenshots are listed separately. Matrix screenshots are EN; all three locales were validated in the168-case matrix, with extra narrow RU/KK captures.

| Page |1440light |1440dark |768light |768dark |375light |375dark |320light |320dark |
|---|---|---|---|---|---|---|---|---|
|Homepage/catalog |[PNG](../../.playwright-mcp/rebuild-home-1440-light.png) |[PNG](../../.playwright-mcp/rebuild-home-1440-dark.png) |[PNG](../../.playwright-mcp/rebuild-home-768-light.png) |[PNG](../../.playwright-mcp/rebuild-home-768-dark.png) |[PNG](../../.playwright-mcp/rebuild-home-375-light.png) |[PNG](../../.playwright-mcp/rebuild-home-375-dark.png) |[PNG](../../.playwright-mcp/rebuild-home-320-light.png) |[PNG](../../.playwright-mcp/rebuild-home-320-dark.png) |
|CourseDetail/enrollment/reviews |[PNG](../../.playwright-mcp/rebuild-course-1440-light.png) |[PNG](../../.playwright-mcp/rebuild-course-1440-dark.png) |[PNG](../../.playwright-mcp/rebuild-course-768-light.png) |[PNG](../../.playwright-mcp/rebuild-course-768-dark.png) |[PNG](../../.playwright-mcp/rebuild-course-375-light.png) |[PNG](../../.playwright-mcp/rebuild-course-375-dark.png) |[PNG](../../.playwright-mcp/rebuild-course-320-light.png) |[PNG](../../.playwright-mcp/rebuild-course-320-dark.png) |
|Lesson workspace/quiz |[PNG](../../.playwright-mcp/rebuild-lesson-1440-light.png) |[PNG](../../.playwright-mcp/rebuild-lesson-1440-dark.png) |[PNG](../../.playwright-mcp/rebuild-lesson-768-light.png) |[PNG](../../.playwright-mcp/rebuild-lesson-768-dark.png) |[PNG](../../.playwright-mcp/rebuild-lesson-375-light.png) |[PNG](../../.playwright-mcp/rebuild-lesson-375-dark.png) |[PNG](../../.playwright-mcp/rebuild-lesson-320-light.png) |[PNG](../../.playwright-mcp/rebuild-lesson-320-dark.png) |
|Profile/analytics/applications |[PNG](../../.playwright-mcp/rebuild-profile-1440-light.png) |[PNG](../../.playwright-mcp/rebuild-profile-1440-dark.png) |[PNG](../../.playwright-mcp/rebuild-profile-768-light.png) |[PNG](../../.playwright-mcp/rebuild-profile-768-dark.png) |[PNG](../../.playwright-mcp/rebuild-profile-375-light.png) |[PNG](../../.playwright-mcp/rebuild-profile-375-dark.png) |[PNG](../../.playwright-mcp/rebuild-profile-320-light.png) |[PNG](../../.playwright-mcp/rebuild-profile-320-dark.png) |
|Login |[PNG](../../.playwright-mcp/rebuild-login-1440-light.png) |[PNG](../../.playwright-mcp/rebuild-login-1440-dark.png) |[PNG](../../.playwright-mcp/rebuild-login-768-light.png) |[PNG](../../.playwright-mcp/rebuild-login-768-dark.png) |[PNG](../../.playwright-mcp/rebuild-login-375-light.png) |[PNG](../../.playwright-mcp/rebuild-login-375-dark.png) |[PNG](../../.playwright-mcp/rebuild-login-320-light.png) |[PNG](../../.playwright-mcp/rebuild-login-320-dark.png) |
|Register |[PNG](../../.playwright-mcp/rebuild-register-1440-light.png) |[PNG](../../.playwright-mcp/rebuild-register-1440-dark.png) |[PNG](../../.playwright-mcp/rebuild-register-768-light.png) |[PNG](../../.playwright-mcp/rebuild-register-768-dark.png) |[PNG](../../.playwright-mcp/rebuild-register-375-light.png) |[PNG](../../.playwright-mcp/rebuild-register-375-dark.png) |[PNG](../../.playwright-mcp/rebuild-register-320-light.png) |[PNG](../../.playwright-mcp/rebuild-register-320-dark.png) |
|Unknown route |[PNG](../../.playwright-mcp/rebuild-not-found-1440-light.png) |[PNG](../../.playwright-mcp/rebuild-not-found-1440-dark.png) |[PNG](../../.playwright-mcp/rebuild-not-found-768-light.png) |[PNG](../../.playwright-mcp/rebuild-not-found-768-dark.png) |[PNG](../../.playwright-mcp/rebuild-not-found-375-light.png) |[PNG](../../.playwright-mcp/rebuild-not-found-375-dark.png) |[PNG](../../.playwright-mcp/rebuild-not-found-320-light.png) |[PNG](../../.playwright-mcp/rebuild-not-found-320-dark.png) |

Real public pages (normal motion, anonymous):

- Homepage/catalog: [1440](../../.playwright-mcp/rebuild-public-home-1440.png), [375](../../.playwright-mcp/rebuild-public-home-375.png).
- CourseDetail: [1440](../../.playwright-mcp/rebuild-public-course-1440.png), [375](../../.playwright-mcp/rebuild-public-course-375.png).
- Login: [1440](../../.playwright-mcp/rebuild-public-login-1440.png), [375](../../.playwright-mcp/rebuild-public-login-375.png).
- Register: [1440](../../.playwright-mcp/rebuild-public-register-1440.png), [375](../../.playwright-mcp/rebuild-public-register-375.png).
- Unknown route: [1440](../../.playwright-mcp/rebuild-public-not-found-1440.png), [375](../../.playwright-mcp/rebuild-public-not-found-375.png).

Additional state evidence:

- [rebuild-quiz-passed.png](../../.playwright-mcp/rebuild-quiz-passed.png)
- [rebuild-quiz-retry.png](../../.playwright-mcp/rebuild-quiz-retry.png)
- [rebuild-enrollment-pending.png](../../.playwright-mcp/rebuild-enrollment-pending.png)
- [rebuild-enrollment-rejected.png](../../.playwright-mcp/rebuild-enrollment-rejected.png)
- [rebuild-enrollment-approved.png](../../.playwright-mcp/rebuild-enrollment-approved.png)
- [rebuild-profile-final-1440-en.png](../../.playwright-mcp/rebuild-profile-final-1440-en.png)
- [rebuild-profile-final-375-en.png](../../.playwright-mcp/rebuild-profile-final-375-en.png)
- [rebuild-profile-final-320-ru.png](../../.playwright-mcp/rebuild-profile-final-320-ru.png)
- [rebuild-profile-final-320-kk.png](../../.playwright-mcp/rebuild-profile-final-320-kk.png)

## Changed-file inventory

This is the complete current working tree, including preserved auth changes that predate this task. `AuthField`, Login/Register handlers, `AuthError`, auth tests/docs and most initial auth layout/footer work came from that unfinished implementation; this rebuild preserves and extends it. No files staged. Checkpoint and screenshots remain ignored.

- `.gitignore`
- `frontend/src/App.jsx`
- `frontend/src/components/AuthField.jsx`
- `frontend/src/components/AuthLayout.css`
- `frontend/src/components/AuthLayout.jsx`
- `frontend/src/components/CourseCard.jsx`
- `frontend/src/components/CourseCurriculum.css`
- `frontend/src/components/CourseEnrollment.css`
- `frontend/src/components/CourseReviews.css`
- `frontend/src/components/Footer.jsx`
- `frontend/src/components/Header.css`
- `frontend/src/components/Header.jsx`
- `frontend/src/components/HomeHero.jsx`
- `frontend/src/components/LearningActivityCalendar.css`
- `frontend/src/components/LearningWorkflow.jsx`
- `frontend/src/components/LessonQuiz.css`
- `frontend/src/components/ProfileLearningActivity.jsx`
- `frontend/src/components/QuizQuestion.jsx`
- `frontend/src/components/QuizResults.jsx`
- `frontend/src/components/Reveal.jsx`
- `frontend/src/components/ui/ui.css`
- `frontend/src/i18n/locales/en.json`
- `frontend/src/i18n/locales/kk.json`
- `frontend/src/i18n/locales/ru.json`
- `frontend/src/index.css`
- `frontend/src/main.jsx`
- `frontend/src/pages/CourseCatalog.css`
- `frontend/src/pages/CourseDetail.css`
- `frontend/src/pages/CourseDetail.jsx`
- `frontend/src/pages/LessonView.css`
- `frontend/src/pages/LessonView.jsx`
- `frontend/src/pages/Login.jsx`
- `frontend/src/pages/Profile.css`
- `frontend/src/pages/Profile.jsx`
- `frontend/src/pages/Register.jsx`
- `frontend/src/styles/v2-tokens.css`
- `docs/design/ai-courses-v2-auth.md`
- `docs/design/full-frontend-redesign-progress.md`
- `frontend/src/components/AuthError.jsx`
- `frontend/src/components/GlobalState.jsx`
- `frontend/src/components/playground/ActivityPulse.jsx`
- `frontend/src/components/playground/Celebration.jsx`
- `frontend/src/components/playground/CourseJourney.jsx`
- `frontend/src/components/playground/ParticleField.jsx`
- `frontend/src/components/playground/ProgressRing.jsx`
- `frontend/src/components/playground/ReadingProgress.jsx`
- `frontend/src/components/playground/SubjectGraphic.jsx`
- `frontend/src/styles/playground.css`
- `frontend/tests/auth-design.test.mjs`
- `frontend/tests/browser/auth-design.mjs`
- `frontend/tests/browser/full-rebuild.mjs`
- `frontend/tests/playground.test.mjs`

## Remaining tasks and practical limits

No blocking implementation task remains. Review the uncommitted source and screenshots before any commit or deployment. If resuming, inspect current Git diff and this report; do not restart or discard completed work.

Protected write flows were exercised through isolated fixtures, never against real accounts or SQLite. Backend authorization was source-reviewed and left unchanged; no live student mutations were attempted. Hidden-tab particle pause is implemented and source-reviewed; runtime instrumentation proved offscreen and reduced-motion behavior, not actual OS tab-visibility suspension. The annual calendar intentionally scrolls horizontally to preserve accessible24px day targets. The font stack falls back to platform UI fonts if Noto Sans is unavailable.

Reproduce automated checks from `frontend/` using existing NVM Node when necessary. SSR tests retain isolated temporary Vite caches and do not invalidate the development server cache. For Firefox matrix batches, set `window.__fullRebuildOptions={widths:[1440],skipInteractions:true}` before invoking `tests/browser/full-rebuild.mjs` through MCP; repeat other widths. `{interactionsOnly:true}` runs the functional fixture. Every synthetic API call remains intercepted. Do not submit real mutating browser flows for regression testing.
