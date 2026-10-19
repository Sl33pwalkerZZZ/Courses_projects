# Instructor Studio implementation

Status: implementation in progress. Existing uncommitted Word-based course work is preserved on `design/amethyst-motion`. No commits, publication or existing educational/student record changes are authorized by this task's verification flow.

## Existing functionality reused

- Course, Module, Lesson, Assignment, supplemental teaching metadata and CourseImport source provenance.
- Existing author role, JWT/session isolation, protected image API, owner-only student drafts and backend quiz grading/validation.
- CourseImport publication guard remains in force. Imported course 8 remains unapproved and unpublished.
- Existing instructor preview and Django Admin remain available; Studio adds author ownership authorization.

## Implementation plan and ownership

- Backend worker: additive Studio models, scoped REST endpoints, publication and submission review, quiz integrity, media upload, migrations and isolated tests.
- Frontend worker: Studio routes/editors/navigation/translations and frontend regression tests.
- Main agent: bounded generic DOCX parser, upload-safety tests, private database backup and preservation checks, integration, documentation and final verification.
- Independent native security_reviewer, frontend_reviewer and browser_qa: read-only reviews and isolated browser fixtures; no actual development-data form submissions.

## Schema review before application

Only a new `studio` application is planned: per-course settings, optional authored image alternatives, publication requests/audit events and owner-scoped import proposals. These additions do not rewrite existing course content, progress or quiz attempts. The precise migration will be inspected and dry-planned before applying after a verified SQLite backup.

## DOCX parsing

`studio/word.py` reads in-memory DOCX archives without extraction, network access, raw HTML rendering or executable content. Uploads are limited to 10 MB, expanded archives to 30 MB, individual XML files to 5 MB and proposed lessons to 100. Duplicate/path-traversing/encrypted archives, macros, XML entities and oversized documents are rejected. Original headings, paragraph text, table cells and safe HTTP(S) references are preserved. Unsupported media/formatting and tracked changes are warned about. The parser returns only a proposal; explicit confirmation is required by the import endpoint before course creation.

Six parser regression tests pass, including the actual local source's four tables; tests never modify the source or course database.

## Verification and limitations

To be filled after backend/frontend integration and independent reviews. Browser mutations must use fully intercepted fixtures or a separate temporary test environment. No real student submissions, enrollment or quiz attempts will be created for QA.
