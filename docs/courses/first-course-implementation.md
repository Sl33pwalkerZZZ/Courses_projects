# First source-driven course implementation

Status: implementation complete; imported as an unpublished draft for human review. Source verified and read: `course_sources/Глава_1_Выбор_ИИ_модели_и_сервиса.docx` (43,836 bytes), Chapter 1 only, sections 1.1–1.8 and four tables. Existing seven courses and 90 lessons must remain unchanged. Existing `.gitignore` modification is preserved. No commit, push or publication authorized.

## Mapping

| New lesson | Source |
| --- | --- |
| Что такое искусственный интеллект | Chapter introduction, goals, 1.1 |
| Как работают современные языковые модели | 1.2, limitations |
| Разница между ИИ-моделью и ИИ-сервисом | 1.3 and comparison table |
| Виды нейросетей и обзор популярных сервисов | 1.4–1.5, categories table, original service links |
| Методика выбора ИИ-инструмента | 1.6, five steps, capabilities table, six criteria |
| Практическая работа: карта выбора ИИ | 1.7–1.8, selection map table, example, conclusion, original references and next-chapter transition |

New course: `Как выбрать нейросеть под свою задачу`, slug `kak-vybrat-neyroset-pod-svoyu-zadachu`, beginner, Russian authored content, approval enrollment, unpublished. One module: `Модуль 1. Основы искусственного интеллекта и выбор ИИ-инструмента`. Six lessons; one structured practice on lesson six; one 15-question draft quiz attached to lesson six. No future chapter content.

Source explanations/tables remain faithful. Lesson objectives, visual scaffolding and quiz questions are clearly labelled instructional additions. Current product capabilities, names, plans, costs, integrations and reference URLs need owner verification before publication; no unsupported updates to source claims. Course/quiz publication requires explicit review approval for this import.

## Additive implementation

- CourseImport establishes import ownership/provenance and review acknowledgement; LessonLearningContent stores optional interaction metadata for new lessons.
- Assignment learning-activity identifier and opt-in structured AssignmentSubmission JSON/draft/revision support preserve legacy behavior.
- Staff preview remains authorized and does not enroll anyone or expose draft quiz answers.
- Root owns source-derived manifest, quiz review, backup/import and final integration. Workers own courses backend, progress backend and frontend independently. Review agents are read-only.

## Progress

- [x] A: inspect actual DOCX and existing architecture.
- [x] B: source mapping, structured content and human-reviewable quiz set (`first-course-assessment-review.md`). Actual XML confirms four tables; initial manual five-table count was corrected before import.
- [x] C: safe importer, ownership, structured assignment persistence and tests.
- [x] D: React teaching interactions, server drafts, localization/fallback and preview.
- [x] E: isolated backend/frontend/browser verification and independent reviews (227 Django tests, 16 frontend test files, 144 Firefox matrix cases, 14 functional browser checks).
- [x] F: actual read-only inventory and dry run; no conflicts, no writes.
- [x] G: verified SQLite backup, two additive migrations and isolated draft import; all pre-existing records preserved.

Database changes were limited to the two additive migrations and the isolated new draft import described below. Never run demo seed commands. The verified backup was created with SQLite's online backup API in ignored `.local-course-backups/` before schema/data writes. No existing media metadata file was present. Resulting paths, integrity checks and exact created IDs are recorded below. Do not read private student contents into reports; preservation verification uses aggregate counts and hashes only.

Source SHA-256: `940238198fb563ff9d1d857886f852dcfdf4cbb4b04d5ca2e3c7e8c431721cff`. Manifest contains all original paragraphs and table cells; objectives and all quiz questions are labelled instructional additions. Author review document includes every option, correct answer and explanation; it is never exposed through the student quiz API.

## Implementation and validation checkpoint

- Courses backend: additive migration `courses.0004_assignment_learning_activity_courseimport_and_more`, source ownership/fingerprint, review gate, supplemental content, authorized preview, default-dry-run importer. Existing content is never updated by the importer.
- Practice backend: `progress.0004_structured_assignments` adds opt-in JSON payload, draft status, revision, feedback history and partial uniqueness; legacy defaults remain. GET/PUT `/api/assignments/<id>/selection-map/`, POST `.../submit/`. GET is read-only. Real enrollment required to write. Rejected submissions retain feedback while editing; pending/approved data are locked.
- React: reusable learning interactions, source tables and references, Russian authored-content labels, localized UI, private server-backed drafts, read-only instructor preview at `/instructor/courses/<slug>/preview`, original account-session keys retained.
- Full Django suite: **227 tests passed** in temporary database. Django check passes; `makemigrations --check --dry-run` reports no changes.
- Final frontend run after whitespace/a11y fixes: **16 test files passed**, lint passed, production build passed (2497 modules). No dependencies installed.
- Native security review: no blocker. Operational limitation: importer validates backup integrity/type, not freshness; root must independently create/verify the current online snapshot immediately before local writes.
- Native frontend review follow-up: no blocker after fixing service-name whitespace normalization, live detail announcements, named table regions, invalid-control descriptions, content lang and control contrast.
- Firefox functional run passed hierarchy/steps/category/service/framework/table and draft/save/reload/submit/error/conflict/rejection cases with synthetic intercepted APIs; no real writes. Browser agent `/root/first_course_browser` exclusively owns Firefox; all 144 width/theme/locale/lesson matrix cases passed.
- Actual default importer dry run passed: no slug conflict; create 1 course, 1 module, 6 lessons, 6 supplemental contents, 1 assignment, 1 quiz, 15 questions, 60 choices, 1 ownership record, **0 directions** (reuse AI Foundations). No data written. Existing inventory: seven published courses, 90 lessons.
- Vite server for QA: `http://127.0.0.1:5174/` (5173 occupied; sandbox port binding required approved escalation). Root process session 62839. Do not stop another developer's 5173 server.

Local migration/import completed after all browser and code checks passed. No real authentication, assignment submission, enrollment or quiz attempt was performed against the student database. See exact results below.

Backup/pre/post verification helpers are prepared at `/tmp/first_course_backup.py` and `/tmp/verify_first_course_preservation.py`; both executed successfully after validation. The backup helper uses mode=ro, SQLite online backup, integrity_check and bidirectional SQL EXCEPT comparisons of every legacy table without returning personal records. Post-import verification compares every pre-existing column/row and disallows new student-related records; only expected new content and migration/permission metadata are allowed. Media checks use stat metadata rather than reading private submission files.


## Actual local import results — 19 October 2026

| Record | Created IDs / count |
| --- | --- |
| Course | **8**, Как выбрать нейросеть под свою задачу; approval enrollment; unpublished |
| Module | **31**, Модуль 1. Основы искусственного интеллекта и выбор ИИ-инструмента |
| Lessons | **91–96**, six lessons in source mapping order |
| Supplemental lesson content | six new records, only for lessons 91–96 |
| Structured assignment | **1**, attached to lesson **96** |
| Quiz | **3**, attached to lesson **96**; 70% threshold; unpublished |
| Quiz questions / choices | 15 / 60 new records |
| Import ownership | one new CourseImport; review_approved=False |
| Direction | reused existing ai-foundations; zero created or edited |
| Student-related records | zero created, edited or deleted |

The author was reused from the existing author reference of course 2. No account or role was created or changed.

- Lesson **91** (order 1): Что такое искусственный интеллект
- Lesson **92** (order 2): Как работают современные языковые модели
- Lesson **93** (order 3): Разница между ИИ-моделью и ИИ-сервисом
- Lesson **94** (order 4): Виды нейросетей и обзор популярных сервисов
- Lesson **95** (order 5): Методика выбора ИИ-инструмента
- Lesson **96** (order 6): Практическая работа: карта выбора ИИ

## Backup and preservation procedure

Private recovery directory: `.local-course-backups/first-course-20261019-102335`.

- SQLite backup: `db-before.sqlite3`, SHA-256 `4821248edfaea23d4aff8fb8dfe125978b942f4d989a6a9d80f9f4ad6b46a91d`.
- Procedure: opened source SQLite with URI `mode=ro` and `PRAGMA query_only=ON`; used the standard-library SQLite online backup API; checked backup integrity; compared all 27 existing tables in both directions with SQL EXCEPT before writes. Comparison returned counts only, never personal records.
- Backup directory permissions 0700; SQLite and verification manifest 0600. Directory and raw Word sources are ignored by Git. Nothing was staged.
- Media inventory: zero files under the private media root; no optional lesson-image-description metadata file existed, so no media metadata copy was necessary. No existing media was changed.
- Applied only `courses.0004_assignment_learning_activity_courseimport_and_more` and `progress.0004_structured_assignments`, with no seeds or data migrations.
- Compared every original column/row against the attached read-only backup after migration and again after import. **All pre-existing records across 27 tables were preserved.** Exact expected content deltas were checked; student-related table counts were unchanged.
- Reran `import_first_course --apply` with the same source, manifest, author and backup: successful no-op. The entire SQLite file was byte-for-byte unchanged during this rerun.
- Actual development-data anonymous GET checks passed: public catalog still contains seven published courses; draft slug returns 404; draft preview, lessons, practice and quiz require authentication (401). These GET checks did not change SQLite.
- Verification artifacts remain private beside the backup: `backup-verification.json` and `post-import-verification.json`. Raw source checksum is unchanged.

## API and model changes

- `GET /api/instructor/courses/<slug>/preview/`: private/no-store, authorized staff/superuser only, course outline without draft quiz answers. Existing Django Admin sessions and JWT are supported.
- Existing lesson API adds optional content_language and learning_content. Existing course list/detail adds content_language. Existing assignment representation adds learning_activity; legacy values remain blank.
- `GET /api/assignments/<id>/selection-map/`: own draft/status/feedback; GET creates no records.
- `PUT /api/assignments/<id>/selection-map/`: save partial bounded JSON using revision+payload; real enrollment required.
- `POST /api/assignments/<id>/selection-map/submit/`: complete ten-field validation, two or three distinct services, six shared comparison criteria and per-service test evidence; idempotent retry; pending/approved locked; rejected work editable with feedback history.
- Structured submissions use opt-in uniqueness and revision guards; legacy submission defaults and multiplicity are retained. No third-party AI execution, localStorage draft persistence or lesson-completion coupling.
- Course/quiz publication for this new import requires explicit CourseImport editorial acknowledgement. All new material remains unapproved and unpublished.

## Review and preview

1. Start Django normally (existing frontend API default: http://127.0.0.1:8000/api). Vite used for QA is running on http://127.0.0.1:5174/ because 5173 was already occupied. No other developer's server was stopped.
2. Sign into Django Admin with an existing authorized staff account. Open `/admin/courses/course/8/change/` and module 31. Inspect lessons 91–96 at `/admin/courses/lesson/<id>/change/`; body and optional structured teaching metadata are editable.
3. Review quiz 3 at `/admin/quizzes/quiz/3/change/` and its question change links. Every option/correct answer/explanation is also in `docs/courses/first-course-assessment-review.md`. Do not publish until this author review is complete.
4. Sign into the React application with an existing authorized staff account and open `http://127.0.0.1:5174/instructor/courses/kak-vybrat-neyroset-pod-svoyu-zadachu/preview`. Staff need both course and lesson view permissions, or superuser status. The display author role alone grants no preview permission.
5. Preview all six lessons. The practical form is read-only in staff preview, no enrollment/progress is created, and the draft quiz is not exposed as a student quiz. Its questions/keys are reviewed in Admin only.
6. Future student exercise: after human approval and deliberate publication/enrollment, an enrolled student can save a map draft, reload, resume and submit. In `/admin/progress/assignmentsubmission/`, authorized staff review pending work, enter feedback and approve/reject. Rejected students can edit and resubmit. No real student record was used for this test.
7. Publication is deliberately manual: review source facts, references and questions; acknowledge review in Course imports; then separately publish quiz 3 and course 8 when authorized. No publication action was taken by this task.

## Tests and independent reviews

- Full Django suite: 227 passed in a temporary test database; includes safe import/no-op/conflict/rollback/preservation, draft visibility, permissions, structured drafts/submit/review, quizzes and existing progress/media/enrollment regressions.
- Django check: no issues. Migration consistency: no changes detected.
- Frontend: all 16 test files passed after final changes; lint and production build passed. Added safe clickable original references, whitespace-name regression and source/table/language preservation coverage.
- Actual Firefox: 144 matrix cases (six lessons × four widths × three UI languages × two themes), plus 14 functional checks. All final clean cases passed; no persistent runtime/console errors, unexpected endpoints or real database mutations.
- Browser simulated writes stayed inside intercepted fixtures. Actual student login/Admin POST/quiz attempts were not exercised on development data; backend persistence/review tests use isolated fixtures.
- One initial 320px browser run hit the error boundary during a concurrent SourceParagraph import edit. It was fixed immediately; a fresh complete 320px rerun passed all 36 cases. Historical failure screenshot retained, not represented as a current defect.
- Native frontend_reviewer and security_reviewer completed independent read-only reviews. UI findings were fixed and reviewed again. Security found no blocker; its backup-freshness limitation is addressed by the verified online snapshot procedure above.
- Firefox was closed after QA. No dependencies installed; no commit or push.

## Actual screenshot evidence

All captures are under ignored `.playwright-mcp/`. Protected/student screens use fully intercepted source-backed fixtures, not real student accounts.

- `first-course-375-dark-overview.png`: six-lesson draft outline.
- `first-course-1440-light-lesson-4.png` and `first-course-interaction-lesson-4.png`: categories/service exploration and source table.
- `first-course-hierarchy-keyboard.png`, `first-course-interaction-lesson-2.png`, `first-course-interaction-lesson-5.png`: concept/LLM/framework interactions.
- `first-course-320-light-lesson-6.png`: narrow practical form.
- `first-course-assignment-pending.png`, `first-course-assignment-feedback.png`: submission and feedback states.
- `first-course-browser-functional-results.json`, `first-course-browser-320-results.json`: browser evidence. Historical `first-course-failure-320-ru-light.png` predates the clean rerun.

## Files added

- courses/management/commands/import_first_course.py
- courses/management/first_course_content.json
- courses/management/first_course_document.py
- courses/migrations/0004_assignment_learning_activity_courseimport_and_more.py
- courses/test_first_course_document.py
- courses/test_first_course_import.py
- progress/migrations/0004_structured_assignments.py
- progress/selection_maps.py
- progress/test_selection_maps.py
- frontend/src/components/learning/LearningContent.jsx
- frontend/src/components/learning/SelectionMap.jsx
- frontend/src/components/learning/learning.css
- frontend/src/pages/InstructorPreview.jsx
- frontend/src/utils/selectionMap.js
- frontend/tests/source-course.test.mjs
- docs/courses/first-course-assessment-review.md
- docs/courses/first-course-implementation.md

Existing models/serializers/views/Admin/URLs, relevant React routes/lesson/sidebar/course views and three locale dictionaries were extended. API authentication/session isolation, protected-image loading, quiz grading and existing course content were preserved. `.gitignore` retained its pre-existing archive rule and gained raw-source/backup exclusions.

## Remaining human decisions and limitations

- Publication and editorial approval are intentionally pending. Service features, plans/licensing, API cost assumptions, privacy policies, availability and reference URLs require author verification; original claims/links have not been silently updated. The original prompt-ingineering URL may contain a typo; it remains faithfully preserved and flagged for review.
- This is Chapter 1 only. The transition to an AI-agent lesson is preserved, but no future chapter was fabricated.
- Russian course content is not translated; EN/KK interfaces show an explicit Russian fallback notice.
- Structured teaching metadata uses the minimal existing Admin JSON editor; no separate course-builder dashboard or rich-text dependency was introduced.
- Actual OS screen-reader speech output was not independently measured; native semantics, language tags, keyboard operation and live regions were source/browser checked.

## Follow-up verification of reported missing-table error

The reported `no such table: courses_courseimport` error was not reproducible in the current checkout or live development server. Django settings use `/home/almas/Desktop/courses/Courses_projects/db.sqlite3`. Full `showmigrations` confirms all migrations applied, including both new 0004 migrations; `migrate --plan` reports no planned operations. Inspection confirms these migrations add metadata/structured-submission support without deleting educational records. No migrations were reapplied or database records changed during this follow-up.

- Revalidated the original pre-migration backup at `.local-course-backups/first-course-20261019-102335/db-before.sqlite3`: recorded SHA-256 matches and SQLite integrity check passes.
- Current SQLite integrity check passes with zero foreign-key violations. The original 27-table preservation comparison passes again; all original records and student-related counts remain unchanged. Eight courses exist, of which seven are published; new course 8 remains a draft with its six lessons and draft quiz.
- Actual read-only HTTP GET to `http://127.0.0.1:8000/api/courses/` returns **200**, seven public courses. A separate Django request-stack check with SQLite query-only enabled also returns 200 and verifies draft course 8 is absent; the SQLite file hash is unchanged by these checks.
- Reran the full Django suite: **227 passed**, using the temporary test database. Django check passes; migration consistency reports no changes.
- Reran all **16 frontend test files**, lint and production build: all passed. `git diff --check` passes.
- No additional implementation or schema change was necessary. If the error recurs in another server process, verify that process uses this checkout/settings/database; the earlier traceback alone does not establish its database path.
