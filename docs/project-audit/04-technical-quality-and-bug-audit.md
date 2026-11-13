# AI Courses — Technical Quality, Security & Reliability Audit

**Audit date:** 2026-11-09
**Branch:** `design/amethyst-motion` (four commits ahead of `origin/design/amethyst-motion`)
**Scope:** Static review of Django/DRF application code, React/Vite source, routes, tests, project manifests and active Django check results. This is a code audit, not a penetration test or production-runtime certification.

Evidence labels:

- **CONFIRMED** — directly demonstrated by source or a completed check/test.
- **CONDITIONAL** — confirmed in the active local configuration, but whether it applies to deployment is unknown.
- **NOT OBSERVED** — no issue found in the reviewed code; this is not proof that every runtime state is safe.

No application, configuration, database, course-content or media file was changed. This report is the only file created for this phase.

## Executive summary

No confirmed critical or high-severity application vulnerability was established in this audit. The reviewed student and instructor APIs generally apply owner/enrollment checks at their data and media boundaries. The test coverage includes account roles, enrollment approval, quizzes, assignment review, protected images/video, byte ranges, grants and session isolation.

Three follow-up items are supported by evidence:

1. **Conditional release blocker:** the active local Django configuration fails `check --deploy` because its email backend is development-only, and it emits HTTPS, cookie, host, debug and signing-key warnings. Production settings were not independently available for comparison.
2. **Studio query growth:** list/detail serializers perform per-course and per-record relation queries without corresponding prefetches in the relevant views. This is a source-confirmed scaling risk; production latency/query counts were not measured.
3. **Playback-grant retention:** each authorized playback-grant request persists a row, while no expiry-pruning path was found. Accumulation is a future database-maintenance risk; current database size was not inspected.

## A. Critical bugs

**None confirmed.** Static review and the completed targeted security/workflow tests did not establish a critical defect.

## B. Backend quality and reliability

### AUDIT-01 — Studio response assembly has per-record query growth

- **Severity:** LOW (scalability risk; no current outage measured)
- **Status:** CONFIRMED by source; production impact not measured
- **Files:** `studio/views.py:104-115`, `studio/presentation.py:18-29`, `studio/presentation.py:48-62`, `studio/presentation.py:65-80`
- **Affected paths:** Studio dashboard/course listing, course detail/curriculum, and submission listing.
- **Evidence:** `course_data()` runs separate module and lesson counts for each course (`presentation.py:56`); detail serialization iterates modules and lessons and reads images, assignments, attachments and quiz relations (`18-29`, `59-60`). `submission_data()` looks up reviewer identity and certificate-verifiable approval while serializing each submission (`65-80`). The list views call these serializers without matching `prefetch_related`/annotations for those relations (`studio/views.py:104-115`, `335-348`).
- **Impact:** Query count grows with the number of courses, modules, lessons or submissions. Large instructor collections can make Studio pages slow and increase database load.
- **Reproduction:** Increase the number of owned courses or submissions, then profile query count for `/api/studio/courses/`, `/api/studio/dashboard/`, or `/api/studio/submissions/`. No database-scale benchmark was run here.
- **Suggested correction:** Add query-count tests and use aggregates, `select_related`, and carefully scoped prefetches or batched presenter data. Preserve ownership filtering when optimizing.

### AUDIT-02 — Playback-grant rows have no identified expiry cleanup

- **Severity:** LOW
- **Status:** CONFIRMED code-path gap; accumulated row count is UNKNOWN
- **Files:** `courses/video.py:106-123`, `courses/models.py:143-149`
- **Evidence:** Each successful grant request inserts a `LessonPlaybackGrant` row (`video.py:119`); stream and revoke paths check or update rows, but the repository scan found no scheduled or management-command cleanup for expired/revoked grants. Expiry is indexed on the model (`models.py:148`).
- **Impact:** Repeated playback, abandoned tabs and expired sessions can leave rows indefinitely, increasing storage and maintenance costs over time. This is not evidence of present performance degradation.
- **Suggested correction:** Define a retention/audit policy and add a bounded cleanup job/command for expired grants. Verify backup and retention expectations before deleting historical records.

### Other backend review areas

- **NOT OBSERVED:** Enrollment requests use a database uniqueness rule for pending duplicates and a shared atomic review service; approval reuses an enrollment. Lesson access checks the authenticated user and course enrollment or authorized preview path.
- **NOT OBSERVED:** Quiz scoring uses server-side correct choices, validates that answer sets match the quiz, snapshots questions and answers, and uses an idempotency identifier. The 48 quiz tests passed.
- **NOT OBSERVED:** Certificate issuance is administrator-only and service-gated by server-side eligibility. Verification returns initials rather than the complete learner name. Certificate-specific tests were not completed during this phase, so this is a source observation only.
- **NOT OBSERVED:** Upload code enforces bounded sizes, supported extensions/signatures, protected storage paths, and video metadata checks through `ffprobe`. Negative-path responses in tests include expected `400`, `403`, `404`, and `416` cases.
- **UNKNOWN:** Database-scale query plans, production database contents, organization/tenant isolation requirements and concurrency behavior under the production database engine were not measured. The inspected model architecture has course ownership but no separate organization/tenant model.

## C. Frontend quality

- **NOT OBSERVED:** Broken route imports or build-time rendering failures. Vite production build completed successfully.
- **NOT OBSERVED:** In the source-reviewed auth flow, requests capture session generation, refresh is single-flight, stale responses are rejected, cross-tab storage changes notify the shared session store, and private routes key state to the session generation (`frontend/src/api.js`, `frontend/src/utils/authSession.js`, `frontend/src/App.jsx`). The 34 frontend test files passed, including session-isolation, lesson-video, media, student experience and Studio coverage.
- **UNKNOWN:** Actual responsive rendering, browser console/network behavior, keyboard interaction, assistive-technology behavior and visual state at real device sizes. Neither local server was listening on ports 5173 or 8000, so browser verification was not performed.
- **UNKNOWN:** Memory behavior and avoidable rerenders in a live, long-running session. Source hooks generally include listener/request cleanup, but there was no browser profiler run.
- **Performance observation:** The production build emits a 444.86 kB uncompressed main JavaScript chunk (134.32 kB gzip); Motion is in a separate 122.70 kB chunk (40.03 kB gzip), and lesson/profile pages are split. Vite emitted no size warning. This is a measurement, not a demonstrated user-facing performance defect; test on target devices before prioritizing bundle work.

## D. Security findings

### AUDIT-03 — Active local settings are not deployment-ready under Django deploy checks

- **Severity:** MEDIUM if these settings are used to deploy; otherwise local-development configuration only
- **Status:** CONDITIONAL
- **File:** `config/settings.py` (relevant assignments at lines 24, 27, 29 and 162; values intentionally omitted)
- **Evidence:** `python manage.py check` passed. `python manage.py check --deploy` raised a `SystemCheckError`: one error identified a development-only console email backend; seven warnings concerned HSTS, SSL redirect, signing-key strength, secure session/CSRF cookies, debug mode and empty allowed hosts. No configuration values or secret material are included in this report.
- **Impact:** If the active settings are used in a public deployment, email delivery and recommended HTTPS/session protections are not configured to the deploy-check standard. The audit cannot establish whether a separate production settings module or environment overrides these values.
- **Suggested correction:** Before deployment, verify the actual production settings independently; configure production email delivery, HTTPS/proxy behavior, secure cookies, allowed hosts and signing keys there. Keep local development settings separate and do not blindly enable HSTS on a host that may still serve HTTP.

### Protected media and authorization review

- **NOT OBSERVED:** An unauthenticated direct-media bypass in the reviewed source. `LessonAttachmentView` and lesson-image delivery require authentication and call `can_access_lesson`; the legacy debug media handler rejects `lessons/` and `submissions/` paths. Protected video playback uses a short-lived, attachment-scoped signed cookie plus a server-side grant row, and rechecks grant validity and current lesson access for each stream request (`courses/video.py:106-151`). The endpoint supports bounded single ranges and rejects unsatisfiable ranges. The project tests explicitly cover permissions, expiry, revocation, HEAD and range behavior.
- **NOT OBSERVED:** A client-controlled quiz answer key, score, owner or review status path in the reviewed serializers/services. Tests cover server-side grading and cross-student attempt isolation.
- **UNKNOWN:** Production TLS termination, proxy headers, CORS/CSRF origin policy, deployment secret injection, log redaction and infrastructure-level rate limiting. `check --deploy` is the available local signal; no production environment was inspected.
- **UNKNOWN:** Whether multi-organization isolation is required. The current architecture scopes author data by course ownership and administrator authority; no organization membership model was found.

## E. Educational workflow reliability

Source and tests cover registration/login, published catalog/detail, approval/open enrollment, lesson authorization and completion, profile progress/activity, quiz attempts, assignment draft/review, publication review, certificates and protected media. Completed focused tests found no regression in the tested paths:

- 28 enrollment-request tests passed, including duplicate prevention, open enrollment, approval/rejection/reapplication and access protection.
- 48 quiz tests passed, including answer-key privacy, scoring, ownership, attempt history and idempotency.
- 9 Studio role-security tests passed, including author ownership, student denial, administrator authority and authority revocation.

Actual authenticated student/author/admin browser journeys were not performed. Browser QA was unavailable because the local frontend and API servers were not running; no test credentials were supplied or used. Certificate issuance and full assignment review tests were not independently completed in a finished test run.

## F. API and integration consistency

- URL families were compared with frontend consumers and serializers for courses, enrollment, lessons, quizzes, assignments, Studio, reviews, certificates and attachments.
- No confirmed frontend/backend path or response-shape mismatch was found in this static pass. Existing frontend tests cover representative request contracts and render states.
- The public course endpoints expose published catalog metadata; lesson material and private media use authenticated endpoints. Draft previews use the separate authorized instructor path.
- **UNKNOWN:** Runtime status codes, caching/proxy behavior, browser cookie handling and compatibility with the deployed frontend origin were not exercised because the local servers were stopped.

## G. Performance and maintainability

- The Studio query-growth issue is detailed as AUDIT-01.
- Existing course and enrollment read paths use `select_related`/`prefetch_related` in several student-facing views. No query-count instrumentation or production query log was available to quantify their impact.
- Protected video avoids full-file Blob buffering and streams bounded chunks. MP4 validation invokes `ffprobe` synchronously with a timeout; maximum configured upload size bounds the input, but concurrent upload saturation was not load-tested.
- Motion and page bundles are split, and no Vite size warning appeared. No device-level performance, Core Web Vitals, media bandwidth or caching benchmark was performed.
- No additional dependencies were installed; no dedicated static security scanner was run.

## H. Tests and verification

### Completed

- `python -B manage.py check` — passed, no issues.
- `python -B manage.py makemigrations --check --dry-run` — passed, no migration changes detected.
- Targeted backend test database — SQLite in-memory URI (`file:memorydb_default?mode=memory&cache=shared`), created and destroyed by Django’s test runner; no persistent database was used by those tests.
- `progress.test_enrollment_requests` — 28 passed.
- `quizzes.tests` — 48 passed.
- `studio.test_role_security` — 9 passed.
- Frontend `node --test tests/*.mjs` — 34 test files passed, 0 failures, 0 skips.
- `npm run lint` — passed.
- `npm run build -- --outDir /tmp/ai-courses-audit-build-20261109 --emptyOutDir` — passed. The existing ignored `frontend/dist` directory was not overwritten.
- `git diff --check` — passed before report creation.
- Read-only HTTP probes to `http://localhost:5173/` and `http://127.0.0.1:8000/api/courses/` returned no connection (`000`); no browser session was opened.

### Not completed or blocked

- The full Django suite was started in isolated test-database mode but did not return a final summary; it was manually stopped after prolonged execution. The suite includes optional source-backed Lesson 113/114 tests that read/hash large local assets, but the exact active test at interruption was not identified. No test failure was observed before interruption, but the full suite is **not reported as passing**.
- A broader mixed backend run was also interrupted after it failed to return a completion summary. Only the three completed backend suites above count as passes.
- Browser QA, actual authenticated flows, accessibility-tree inspection and responsive visual checks were not run because the local app servers were unavailable.
- `manage.py check --deploy` did not pass for the active local configuration; see AUDIT-03. This is not evidence that production settings are identical.
- No database contents, learner records, credentials, quiz imports or backups were inspected in this phase.

## I. Prioritized remediation roadmap

1. **Before deployment:** validate the real production settings and clear the deploy-check error/warnings appropriate to the hosting topology. Do not copy local settings blindly or enable HSTS until HTTPS is guaranteed.
2. **Before Studio scales:** add query-count tests for dashboard, course list/detail and submission pages; batch/prefetch the related records identified in AUDIT-01.
3. **Operational maintenance:** agree on playback-grant retention and implement a bounded expiry cleanup only after policy approval.
4. **Before release:** start the app in an isolated environment and run browser checks for public pages plus authorized student/author/admin flows using non-production fixtures; verify protected video seeking, expiry/revocation and mobile accessibility.
5. **CI reliability:** split fast isolated backend tests from optional local-production-media integration tests, so the default suite has a bounded runtime and large media verification runs as an explicitly selected job.
6. **Performance measurement:** collect representative query counts and frontend performance on target devices before splitting or replacing additional components. The current bundle output alone does not justify a redesign.

## Git status before and after

**Before creating this report:** branch `design/amethyst-motion`, four commits ahead of origin; four pre-existing modified tracked files (`config/settings.py`, `courses/management/commands/import_media_module_5.py`, `courses/management/media_module_5.json`, `docs/courses/media-module-5-assets.json`); 603 porcelain entries including existing untracked work; zero staged files. Local settings contents were not included in the report.

**After creating this report:** the same pre-existing working-tree changes remain, plus this report as the only newly created path. Nothing was staged, committed, pushed, deleted or modified outside this report. Final `git diff --check` and status comparison were run after writing it.
