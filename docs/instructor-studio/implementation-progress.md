# Instructor Studio implementation

Status: implementation and verification completed from checkpoint `3e66255` on `design/amethyst-motion`. Existing `.gitignore` edits preserved. No commits, pushes, publication, role changes, content imports or student-data writes were performed on the development database during completion.

## Reused checkpoint functionality

The checkpoint already contained the Studio app, initial migration, ownership-scoped API endpoints, signed Word preview/confirmation, publication transactions and audit models, the React dashboard/editors/routes, and most locale strings. Existing Course/Module/Lesson/Assignment, CourseImport provenance, supplemental teaching metadata, protected media, JWT/session isolation, structured student drafts and backend quiz grading remain in use. This work finishes and validates those implementations instead of replacing them.

## Recovery of the catalog HTTP 500

The actual traceback ended in `django.db.utils.OperationalError: no such table: studio_coursesettings`, reached from `CourseListSerializer.get_content_language()` while serializing the public catalog. Courses/progress migrations 0001–0004 were already applied. The plan showed only `studio.0001_initial`: five new models and the pending-publication uniqueness constraint. No destructive operations or content data migrations were present.

**Backup sequencing incident:** the old `/tmp` safety helper was missing after the interruption. The shell command did not stop on that failure and applied Studio 0001 before a fresh backup was created. This did not meet the requested fresh-before-migration sequence. No rollback or replacement was attempted. The existing pre-migration snapshot was then checksum/integrity verified and every original record compared against it; all records were intact. A fresh post-migration snapshot was created and verified immediately afterwards. This incident must not be described as a fresh backup taken before 0001.

Verified backups (private, Git-ignored):

- Existing pre-Studio snapshot: `.local-course-backups/instructor-studio-20261019-105951/db-before.sqlite3` (checksum matches its `verification.json`).
- Fresh recovery snapshot after 0001: `.local-course-backups/instructor-studio-recovery-20261020-102739/db-after-migration.sqlite3`.
- Fresh verified snapshot **before 0002**: `.local-course-backups/instructor-studio-recovery-20261020-103050/db-after-migration.sqlite3` (the filename reflects the already-applied 0001).
- Verified snapshot after 0002: `.local-course-backups/instructor-studio-recovery-20261020-103051/db-after-migration.sqlite3`.

Snapshots use SQLite's online backup API, read-only source connections, checksum/integrity verification, private directory/file permissions and no printed row contents. Original-table comparison covers every original column and row across 29 tables. Only migration/permission metadata additions are allowed; all original educational, account and student records and counts remain unchanged. SQLite integrity is `ok` and foreign-key violations are zero. Source files and existing media were not changed.

After migration, the **running Django server** at `http://127.0.0.1:8000/api/courses/` returns **HTTP 200** with seven published courses. Course 8 remains hidden publicly. No unrelated server process was killed.

## Backend models, migrations and permissions

New Studio models, all additive:

- CourseSettings: per-course authored language, with existing import-language fallback.
- LessonImageDescription: optional localized alt text/decorative state, retaining legacy private metadata fallback.
- PublicationRequest: requester, source/assessment acknowledgements, content fingerprint, decision, reviewer and timestamps.
- PublicationEvent: immutable decision history.
- ImportPreview: confirmation receipt and original parsed provenance; **no database row is written during upload/preview**.

Applied migrations:

1. `studio.0001_initial`: the five models plus one pending publication request per course.
2. `studio.0002_importpreview_studio_unique_import_source`: unique source hash on confirmed import receipts, preventing concurrent duplicate imports across authors. Announced and reviewed before application; fresh backup verified first. Existing content tables are unaffected.

| Capability | Student | Author | Studio administrator |
| --- | --- | --- | --- |
| Studio/API access | Denied | Allowed | Allowed |
| Private course/lesson/quiz/asset access | Denied | Own courses only | All authorized moderation courses |
| Create draft, edit/reorder curriculum | Denied | Own unpublished courses | Unpublished courses |
| Read/review submitted work | Own student endpoints only | Own courses; never unsubmitted drafts | Moderation courses |
| Request publication | Denied | Own course | Allowed |
| Approve/reject/publish | Denied | Denied | Allowed with validation/audit |
| Grant/revoke author role | Denied | Denied | Allowed for ordinary student/author targets only |

Current role-security policy: a Studio administrator is an active user with trusted `role=admin`, or an active Django superuser with an explicitly displayed override. Staff status or course model permissions alone do not grant Studio authority. Authors manage only their own courses. Registration continues to force student role, and Studio cannot grant administrator/staff/superuser status. See [the role-security audit](role-security-audit.md) for the confirmed account flags, capability contract, recovery verification and limitations. The earlier completion results below describe that implementation checkpoint; the audit records the subsequent 265-test role-security run and current Firefox connection limitation.

Nested endpoints scope guessed IDs to the current owner. Receipt replay rechecks current course ownership, including after administrator reassignment. Published course content and published/attempted quizzes are locked. Assignment definitions with submissions cannot be changed in place. Historical outcomes and existing student completion behavior are preserved.

## API inventory

All Studio endpoints require existing JWT authentication and return private/no-store responses:

- `GET /api/studio/me/`, `meta/`, `dashboard/`.
- `GET/POST /api/studio/courses/`; `GET/PATCH courses/<id>/`.
- `POST courses/<id>/modules/`, `courses/<id>/reorder/`.
- `PATCH modules/<id>/`; `POST modules/<id>/lessons/`, `modules/<id>/reorder/`.
- `GET/PATCH lessons/<id>/`; `POST lessons/<id>/images/`.
- `GET/PUT lessons/<id>/quiz/`: owner-only answer keys; existing validation; draft writes only, no attempted-quiz replacement.
- `GET/POST lessons/<id>/assignments/`; `PATCH assignments/<id>/`.
- `GET courses/<id>/submissions/`; `POST submissions/<id>/review/`; `GET submissions/<id>/file/` (authenticated confined attachment download, no public URL).
- `GET/POST courses/<id>/publication/`; `GET reviews/`; `POST reviews/<id>/decision/`.
- `GET instructors/`; `POST instructors/<id>/` for authorized student/author role changes.
- `POST imports/preview/`; `POST imports/<uuid>/confirm/` with owner-bound expiring signed token and explicit reviewed mapping.
- Existing `/api/instructor/courses/<slug>/preview/` now permits owning authors and actual Studio administrators with staff status alone granting no access. Student preview responses do not expose quiz keys or create enrollment/progress.

Course creation always starts unpublished; collision-safe slugs respect the actual model field length, including long titles. Curriculum reorder accepts exactly all sibling IDs once. Empty lesson bodies are allowed while drafting but block publication. Django model validation is returned as actionable HTTP 400 instead of an uncaught 500.

Publication approval is atomic, checks administrator authority and the current fingerprint, validates source/assessment acknowledgements and quizzes, then sets CourseImport review approval and publishes the reviewed quizzes/course together. Stale requests require rejection and a fresh review. The existing CourseImport guard is retained. Reviewer, timestamps and decisions are recorded. No course was approved by this implementation.

## DOCX safety and workflow

Generic parsing is bounded to 10 MB compressed, 30 MB expanded, 5 MB per XML member, 2,000 blocks and 100 proposed lessons. Duplicate/path-traversing/encrypted archives, executable/macros, XML DTD/entities (including UTF-16/32 bypasses), corrupt compressed streams and oversized content are rejected. The parser neither extracts files nor makes external requests. Headings, paragraphs, tables and safe references are preserved; unsupported illustrations/formatting and tracked changes produce warnings. No raw HTML is rendered.

Upload and editable preview are read-only. Confirmation validates a signed owner-bound proposal (24-hour expiry), creates the new draft transactionally, preserves source checksum/mapping provenance, and records an idempotent receipt. Duplicate source imports and receipt replay after ownership change are rejected. **Course 8 was not imported again.**

## React routes and completion fixes

- `/instructor`: dashboard.
- `/instructor/courses`: owned courses (moderators can review all).
- `/instructor/courses/new`: draft creation.
- `/instructor/courses/:id/edit`, `/curriculum`, `/assessment`, `/submissions`, `/publication`.
- `/instructor/import`: DOCX upload, source preview, editable mapping, metadata and explicit confirmation.
- `/instructor/reviews`: administrator decisions.
- `/instructor/instructors`: authorized instructor management.
- Existing `/instructor/courses/:slug/preview`: course/lesson preview.

Navigation uses server eligibility. Private routes retain session-generation keys; actions abort on unmount/account changes and work under StrictMode. Transient identity failures have a retry path. Forms preserve unsaved values across language/theme changes; returning to DOCX mapping preserves metadata. Editors support accessible arrow reordering, lesson objectives, teaching items/examples/tables/diagrams, protected illustrations and localized image descriptions, quiz choices/correct answers/explanations and protected submission downloads. Publication errors link to relevant editors. Pending/approved content and historical quizzes remain appropriately read-only.

Frontend additions/updates include `components/instructor/useStudio.js`, `EducationalSections.jsx`, shared primitives, Studio pages, Studio utilities and all three locale dictionaries. All 188 base Studio keys had parity at independent review; subsequent additions are covered by tests. Amethyst themes, reduced motion and session isolation are retained.

Backend completion touches Studio models/views/parser/tests plus shared course/lesson permissions and serialization. Catalog and profile enrollment serializers eagerly load new settings to prevent N+1 queries. Structured feedback is not duplicated when a student resubmits rejected work.

## Test results and independent reviews

- Full Django suite: **256 passed**, temporary database only, including ownership, roles, draft isolation, long-title slug collisions, ordered curriculum, empty drafts, source import rollback/no-op/duplicate receipt, quiz integrity, publication guard/approval/rejection/stale content, media access and submission review/resubmission.
- Django check: no issues; migration consistency: no changes detected; migration plan: no planned operations.
- Frontend: **17 test files passed**, including ten Studio regression cases; lint clean; production build passed (2,509 modules); whitespace check clean.
- Query-only real-data checks: course 8 authorized moderator Studio and preview 200, student 403, unrelated author 404, public draft detail 404; six lessons, 15 draft quiz questions and unapproved source provenance remain intact. Database hash unchanged by successful audit checks. In-memory audit identities were used; no actual account was altered.
- Native `security_reviewer`: identified receipt ownership replay and corrupt-DOCX error handling; both fixed with regressions. Core owner/role/publication/media/quiz boundaries traced read-only.
- Native `frontend_reviewer`: identified locale-triggered unsaved-data loss, Word metadata loss and incorrect image-description language; all fixed by the frontend worker with regressions.
- Native `browser_qa`: **216/216 matrix cases** passed (nine routes × four widths × three languages × two themes), reduced-motion enabled, plus **27 distinct functional checks**. Fifteen mutation requests stayed inside intercepted synthetic APIs; zero unexpected API calls, app console/runtime errors, page overflow or unlabelled controls. Protected teacher CRUD/import/moderation and submission flows were tested with fail-closed fixtures, not real development accounts.
- Actual anonymous Firefox browsing at `http://localhost:5173/` also passed: seven public course cards, course navigation, catalog/detail/review HTTP 200 responses and mobile 375px without overflow/errors. Zero real database mutations. QA contexts were closed.

## Firefox evidence

Saved result artifact: `.playwright-mcp/studio-browser-results.json`. Nineteen actual screenshots include:

- `studio-1440-light-dashboard.png`: light dashboard.
- `studio-1440-dark-instructor.png`, `studio-1440-dark-curriculum.png`, `studio-1440-dark-assessment.png`, `studio-1440-dark-publication.png`.
- Equivalent dark captures at 768, 375 and 320 pixels (`studio-<width>-dark-<page>.png`).
- `studio-public-1440.png` and `studio-public-course-375.png`: real anonymous development-site browsing.

Protected-page captures show synthetic QA content (clearly marked), not actual student records or course changes. Screenshots and fixture scripts remain under ignored `.playwright-mcp/`. Original desktop captures were recaptured at the top to avoid fixed-header full-page capture artifacts.

## How to use and review course 8

1. Use the existing frontend at `http://localhost:5173/` (its current listener uses localhost/IPv6). The separate fixture QA server is `http://127.0.0.1:5174/`; its intercepted tests do not require additional CORS configuration. In Django Admin, edit an existing intended teacher user and set **Role = author**. No staff/superuser checkbox is required. Do not assign unrelated users or change course ownership merely for testing.
2. Sign into React with that user. Eligible users see **Instructor Studio** in the Header; direct entry is `/instructor`. Create a draft, edit settings, add modules/lessons, use arrows to reorder, save teaching content, and build valid draft quiz questions in Assessment.
3. An author sees course 8 only if they are its existing owner. An authorized Studio administrator can open `/instructor/courses/8/edit` and review all six lessons and the assessment without changing ownership.
4. Open `/instructor/courses/8/publication`. Review the original source facts, reference links, lesson material, assignment and all 15 questions/correct answers; complete source/assessment acknowledgements and request publication. Outstanding requirements/errors are shown explicitly.
5. A properly authorized administrator opens `/instructor/reviews`, inspects the material/assessment, and explicitly approves and publishes, or rejects with feedback. Only successful validated approval publishes course 8 and its quiz. The normal public catalog then shows it without student-side workarounds.
6. Current course 8 remains unpublished and unapproved. No real publication request was created for this task's QA.

## Remaining boundaries

Published content is deliberately locked in Studio; versioned live-course revision is outside this implementation. Existing Course has no cover-upload field, so its existing subject artwork remains in use. DOCX embedded images must be uploaded separately after review; unsupported rich formatting is warned about. Course content is not automatically translated, and references/product claims still require human verification. No new libraries were installed.
