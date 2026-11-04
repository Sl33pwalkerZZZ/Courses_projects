# Instructor Studio — cinematic workspace, Phase 2

2026-11-03 · `design/amethyst-motion`

## Scope and recovery

Verified frontend archive before editing:
`.local-redesign-checkpoints/frontend-before-studio-phase2-20261103-110050.tar.gz`.
No Git reset/restore/clean, backend/database changes, migrations, account changes,
new course records, commits, pushes or deployment. Unslop was not invoked.
Existing Phase1 landing is preserved; its components/styles compare byte-for-byte
with the archive. RU/KK/EN dictionaries retain all existing values; only the new
`studioVisual` namespace was appended.

## Existing functionality inventory

The baseline already used top navigation, not a permanent sidebar. This phase
refines that architecture rather than claiming a sidebar was removed.

Preserved destinations:

| Route | Availability / action |
|---|---|
| `/instructor` | Authorized Studio users; dashboard |
| `/instructor/courses` | Own courses for authors, all scoped courses for moderators |
| `/instructor/courses/new` | Existing course creation form |
| `/instructor/submissions` | Existing ownership-scoped student-work review |
| `/instructor/import` | Existing safe DOCX import workflow |
| `/instructor/enrollment-requests` | Moderator navigation/route only |
| `/instructor/reviews` | Moderator publication-review navigation/route only |
| `/instructor/instructors` | Navigation requires `can_manage_instructors`; existing route/backend checks retained |

Course workspace edit, curriculum, assessment, submissions and publication tabs,
preview link, form validation, save/import actions and request cancellation remain
unchanged. The entire `CourseWorkspace` and subsequent form/settings functions
compare exactly with the archive. The `StudioAccessGuard` implementation is also
unchanged. No student, staff-only or unauthorized instructor capability is added.

## Direction

A course-production workbench: compact command navigation, a clear creation action,
actual scoped course records and a prominent lead project. Amethyst is used for
selection and primary actions, not every surface. Management content remains
readable and stable; no heavy parallax or fabricated activity charts.

The existing [React Bits](https://reactbits.dev/) and
[Aceternity](https://ui.aceternity.com/) inspiration is interpreted using the
project's own Motion/Lucide primitives. No component library or dependency added.

## Navigation and dashboard changes

- Compact icon/text command bar with a surface/underline active state.
- Below900px, a native expand/collapse button names the current section. Links
  wrap safely, are hidden from keyboard navigation when collapsed, and close on
  selection or Escape. Focus returns to the toggle on mobile selection/Escape.
- Every previous destination retains its capability condition. No new routes.
- Dashboard heading provides existing Create course and Word import actions.
- Metrics use only finite values provided by `/studio/dashboard/`:
  courses, published, drafts, pending_publications, pending_submissions.
  Missing values are omitted, never replaced with invented analytics.
- Dashboard additionally loads existing `/studio/courses/` once through the
  existing session-safe resource hook, displaying up to four returned courses.
  List response order is retained. Course listing displays the full response.
- Lead course spans the editorial grid, with smaller related course panels.
  Real title, description, direction, language, publication boolean and available
  module/lesson counts and level are shown. Pending publication status is not
  inferred from the course list's publication boolean.
- Separate native edit/curriculum links avoid nested interactive cards. Existing
  submission/library destinations remain available as direct shortcuts.
- Loading/error/empty states use readable status/alert text and existing retry,
  Create course and Word import actions.

## Motion

Transform-only .45s view entrance; .2s course hover lift, quiet navigation/selection
color transitions, mobile chevron feedback. Content never starts opacity-hidden.
Reduced-motion disables entrance/lift and CSS transitions. No decorative loops,
new WebGL, per-frame React state or layout animation in dense editors. Phase1
animations and all other page motion remain intact.

## Exact changed files

Modified:
- `frontend/src/pages/instructor/InstructorStudio.jsx` — shell/nav presentation only.
- `frontend/src/pages/instructor/CourseEditor.jsx` — Dashboard/CourseList only.
- `frontend/src/i18n/locales/en.json`
- `frontend/src/i18n/locales/ru.json`
- `frontend/src/i18n/locales/kk.json`
- `frontend/tests/enrollment-requests.test.mjs` — replace old JSX-location regex
  with assertions against rendered author/moderator navigation; route guard
  assertion retained.

Created:
- `frontend/src/components/instructor/StudioNavigation.jsx`
- `frontend/src/components/instructor/StudioDashboard.jsx`
- `frontend/src/components/instructor/StudioCourseCollection.jsx`
- `frontend/src/pages/instructor/studio-command.css`
- `frontend/tests/studio-dashboard-design.test.mjs`
- `frontend/tests/browser/studio-workspace.html`
- `frontend/tests/browser/studio-workspace.jsx`
- This report.

The browser harness is a clearly labeled isolated presentation fixture. Its
synthetic records never reach application APIs or production components as data
outside the harness. It is not a new app route, account, token or authorization
bypass. No fixture is included in the production entrypoint.

## Browser verification — precise limits

The user confirmed **no authorized test session is available**. No login,
registration, injected JWT, borrowed browser session or reading credentials was
attempted. Therefore real signed-in dashboard API loading, actual author ownership,
real course creation/edit/save, submission review and admin permission enforcement
are not claimed as browser-verified.

The main agent used the working project-local Chromium from Phase1 against
`/tests/browser/studio-workspace.html`, with fresh contexts and **all API requests
blocked**. No browser-only CORS adaptation is involved in these Studio checks.
The harness renders actual new presentation components with synthetic data;
links are checked in an isolated MemoryRouter, not by mutating real courses.

Results `.playwright-mcp/studio-phase2/results.json`:
- 30 author layout combinations: RU/KK/EN × light/dark ×1440/1024/768/390/320.
- Five administrator navigation widths, all seven destinations present.
- No horizontal overflow, page/console errors or API requests.
- Mobile menu Escape/selection closes and returns focus to toggle.
- Curriculum route destination reached in the isolated router.
- Loading, empty and error screenshots captured; reduced-motion transforms none.
- Actual normal application `/instructor` without a session redirected to `/login`.
  This last check is a real application guard smoke test, not authenticated QA.

Screenshots (local artifacts, not staged):
- `.playwright-mcp/studio-phase2/author-ru-dark-1440.png`
- `author-ru-dark-320.png`
- `author-kk-light-320.png`
- `admin-ru-dark-1440.png`
- `admin-ru-dark-320.png`
- `state-{loading,empty,error}-320.png`

No real-account before screenshot could be captured without a safe session.
The verified source archive is the pre-change reference. Actual Phase1 homepage
source/styles were rechecked against it; no visual change was introduced there.

## Independent reviews and tests

Native `frontend_reviewer`: read-only source review, initial/final; caught mobile
focus loss and confirmed the fix. Native `security_reviewer`: source/backend-contract
review and existing instructor-permission regression test; no authorization
regression found. Native `browser_qa`: independent review of the parent's actual
Chromium artifacts; no blocking visual finding. Browser agent did not execute an
independent MCP session; its tools were unavailable, so no such claim is made.

Final validation: all **33 frontend test files passed** with
`node --test --test-concurrency=2 tests/*.test.mjs`; `npm run lint` passed
without warnings, `npm run build` passed, and `git diff --check` passed.
Tests cover actual
rendered role-dependent navigation, contextual links, real metric keys only,
omitted missing metadata, escaped course text, translated empty/loading/errors,
plus the existing session/permission, learning, video and cinematic landing suite.

## Remaining work

- Supply an isolated authorized environment later for real teacher/admin workflows,
  ownership denial, published/draft course editing and mutation testing.
- Mobile cards retain generous space around metadata/actions; optional density
  refinement can follow real content review. No redesign of curriculum, assessment
  or publication workflows was attempted.
- Backend, SQLite, certificates, protected media and local `config/settings.py`
  remain unchanged. No deployment, publication, staging, commit or push.
