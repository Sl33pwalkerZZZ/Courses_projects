# S2.1 — Studio lesson draft stability

2026-11-16, Asia/Almaty. Branch `feat/studio-course-authoring`, based on checkpoint e669aaa. No backend, database, media, enrollment, assessment or publication changes; no staging/commit/push.

## Confirmed root cause and repair

Same-course reload changed `revision`; `useStudioResource` hid course data and `ResourceState` replaced CourseWorkspace's Outlet with a spinner. That unmounted Curriculum/LessonEditor, whose next initialization read saved props. The isolated Chromium **before** fixture reproduced loss after module rename (editor absent).

CourseWorkspace now opts into retained data for the same API path and auth-session generation. Background loading/error/retry is rendered beside the existing subtree, so keyed lesson state remains mounted while outline, images and attachment props update. Initial loading/errors retain their existing full-state behavior. Course/session changes and401/403 do not reuse retained private data.

`useLessonDraft` owns the editable form and saved baseline. PATCH submits a snapshot; only success acknowledges that submitted version. Server-normalized data replaces the form only if no newer raw-field edits exist. Newer edits during PATCH remain dirty; failures retain form/baseline. Save is busy-disabled while text controls remain editable. Each active editor is keyed by lesson ID.

Close/switch and router navigation use the existing native `window.confirm` pattern with RU/KK/EN copy. Staying leaves the form intact; confirming permits the original destination. Tab/reload leave uses browser-owned beforeunload UI. Drafts remain in memory, not browser storage.

## Navigation implementation constraint

BrowserRouter is not a data router, so useBlocker cannot simply be added. A narrow early POP dispatcher is installed in main.jsx before BrowserRouter subscribes; it is inert without an active Studio lesson. Active guards wrap navigator push/replace/go and intercept POP. A cancelled POP and its compensating history movement are hidden from Router, preventing unmount before restoration. Cleanup clears the active handler and restores navigator methods.

Actual Chromium testing caught the first late-listener approach failing Back: Router processed navigation and removed the editor before the later listener ran. Early bootstrap fixed that observed issue. This integration depends on `UNSAFE_NavigationContext` and numeric BrowserRouter `history.state.idx`; retest on router upgrades. Foreign same-document entries without idx are outside this rollback mechanism; leaving the document still uses beforeunload.

## Verification actually executed

- `cd frontend && node --test tests/*.test.mjs`:36/36 test files passed,0fail/skip.
- Focused existing Studio/permissions/dashboard/review files passed; new `studio-draft.test.mjs` has7 utility/SSR regression cases covering refresh/error states, submitted baseline, failure/success, stay/discard, POP rollback and translations. These alone do not prove mounted component lifetime.
- `npm run lint`:passed, no warnings in final run.
- `npm run build`:passed.
- `git diff --check`:passed.
- Native frontend_reviewer independently reviewed lifecycle/guard/source changes and found no confirmed blocker. Native browser_qa reported missing MCP Firefox; no MCP screenshots claimed.

Actual browser evidence was produced separately by the main agent using the **already installed Chromium headless shell**, driven by existing local tooling. Ephemeral Vite fixture used actual CourseWorkspace/Curriculum/hooks/components, with a synthetic in-browser Axios adapter. No real authentication bypass or Django request, database or persistent media write occurred. `window.confirm` answers were automated, not human approvals.

Observed before/after checks: rename/reorder keeps editor DOM identity and unsaved text; upload updates attachment list; failed refresh retains draft and retry updates outline; close/switch stay/discard; distinct lesson drafts; failed save retention; typing during held PATCH survives response+reload; clean save/navigation; native browser Back stay/discard. EN1440dark, RU390light and KK390dark checked translated confirmations; no uncaught page errors observed. These are presentation-fixture results, not real instructor-account/backend integration.

Temporary harness, JSON result and screenshots: `/tmp/s21-browser/` (`run.mjs`, `fixture.jsx`, `report.json`, `after-en-1440-dark.png`, `after-ru-390-light.png`, `after-kk-390-dark.png`). Test logs: `/tmp/s21-final-tests.log`, `/tmp/s21-final-lint.log`, `/tmp/s21-final-build.log`. Native browser reviewer preserved original source copies in `/tmp/s21-before-zrbbo4wy/` for the before fixture. Temporary artifacts are not staged and may expire.

## Manual reproduction checklist

Use an isolated draft course or approved test environment, not real course progress.

1. Open lesson A, change body/objectives without saving. Rename a module, reorder a lesson or upload a permitted attachment. Verify text remains and outline/media list updates.
2. Close A or choose B: Cancel retains A; confirm discard opens the requested destination. Reopen A and verify only its saved content appears.
3. With dirty A, try a workspace tab, preview and browser Back: staying preserves A; discarding continues. Clean editor navigates normally.
4. Simulate PATCH failure: edits remain. Hold a PATCH response, type newer text, release it: newer text remains and leaving still asks. Save again without further changes: navigation should be clean.
5. Repeat refresh failure/retry and RU/KK/EN at mobile/desktop widths. Check tab/reload browser warning manually.

Remaining real-account checks: actual authenticated Studio session, real upload API and native browser prompt appearance. Existing permissions/API contracts unchanged; no section editor, media pairing or assessment changes added.

## Changed files

- `frontend/src/components/instructor/useStudio.js`
- `frontend/src/components/instructor/StudioShared.jsx`
- `frontend/src/components/instructor/useLessonDraft.js` (new)
- `frontend/src/pages/instructor/CourseEditor.jsx`
- `frontend/src/pages/instructor/Curriculum.jsx`
- `frontend/src/utils/studioDraft.js` (new)
- `frontend/src/utils/studioNavigation.js` (new)
- `frontend/src/main.jsx` (early inert POP registration only)
- `frontend/src/i18n/locales/en.json`
- `frontend/src/i18n/locales/ru.json`
- `frontend/src/i18n/locales/kk.json`
- `frontend/tests/studio-draft.test.mjs` (new)
- `docs/project-memory/CURRENT_STATE.md`
- `docs/project-memory/DECISIONS.md`
- This report (new).

Final safety checks: working SQLite SHA-256 matches checkpoint `f8a79ad1a69953e3725cc58d43a85cc7459d13b0ce6aa3714a4db573e78c3c2e`; intentional local settings hash matches `ea683b8b7bf47ca027890feaa09e4ca384a017b48670a87c73b452a923f39931`. All14 pinned final Module5 MP4/VTT sources match their manifests. Course10 remains unpublished. Git index empty; existing excluded files not deleted.
