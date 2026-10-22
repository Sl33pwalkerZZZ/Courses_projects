# Final lesson UX and verified certificates — implementation review

Branch: `design/amethyst-motion`. Existing uncommitted work preserved.
No development SQLite migrations, content writes, issuance, role changes, commits
or pushes were performed. The feature is intentionally disabled by default.

## Lesson fixes completed

- Lesson95: each connector now extends from one numbered circle centre to the
  next across the complete variable-height step. Opaque circle backgrounds mask
  the line. Desktop/mobile sizes account for half the 2px stroke width.
- Lesson96: all seven original URLs were present in SQLite and the old DOM.
  Isolated Firefox reproduced a closed-by-default disclosure and weak link
  affordance, but **did not reproduce a blank opened disclosure**. Replaced it
  with an always-visible semantic resource list, original URLs and descriptive
  link labels; minimum44px targets and visible keyboard focus.
- Compared optional activity prompts with the15 final question texts without
  reading or changing answer keys. Removed lesson94 activity, which repeated
  quiz question9. Lessons93/95 now use contextual formative scenarios rather than
  copying final questions. Feedback is immediate and local only, with no grading,
  persistence or progress effects. Topic overlap is purposeful reinforcement.
- Assessment wrapper copy in RU/KK/EN now distinguishes lesson completion,
  assessment results and separate certificate requirements. Authored quiz3,
  its instructions, questions, answer keys, attempts and70% threshold are intact.

## Certificate architecture implemented

Reuses `certificates.Certificate`, `Enrollment`, `LessonProgress`, `QuizAttempt`
and `AssignmentSubmission`; no parallel completion or grading records.

`CourseCertificatePolicy` configures all-lessons requirement, optional final quiz,
required approved assignments and an explicitly approved issuer identity per
course. Defaults are disabled. Existing lesson/course completion semantics do
not change. Issued certificates capture immutable name/course/issuer/evidence
snapshots, administrator, opaque UUID4 hex code and revocation metadata.

Eligibility is server-side: published/enrolled course, enabled policy and approved
issuer, plus configured learning requirements. Quiz evidence must be a recorded
passed attempt for the selected published course quiz, meeting its current
threshold. Assignment evidence must have approved status, reviewed timestamp and
matching latest review-history status/revision/timestamp from an authorized
educator. Legacy unaudited approvals do **not** establish certificate eligibility;
they require an authorized educator to review through the existing workflow.
No completion evidence is invented or student records altered.

Issuance is administrator-only, transactional, with course/policy locking and a
unique student/course constraint. Repeat issuance returns the existing record.
Revoked certificates stay revoked rather than creating replacements. Names must
be Unicode-letter display names with at least two parts, match the learner's
existing profile name and be confirmed by the administrator. This is display-name
review, not a claim of legal identity verification or academic accreditation.

Administrators can configure policies, confirm issuance and revoke in Django
Admin. Active admin role/superuser is required; staff student or ordinary author
cannot issue/revoke. PDF download is owner/admin only and generated in memory,
never a public media file. Public verification discloses initials, course, issuer,
dates and validity/revocation status, not account details, grades or submissions.
Responses disable caching to avoid stale private/revocation data.

## APIs and frontend

- `GET /api/courses/<id>/certificate-status/`
- `GET /api/my/certificates/`
- `GET /api/certificates/<code>/download/` (authenticated owner/admin)
- `GET /api/certificates/verify/<code>/` (minimal public verification)
- `POST /api/certificates/admin/issue/` (administrator only)
- `POST /api/certificates/admin/<code>/revoke/` (administrator only)

Profile has **Мои сертификаты**; authenticated CourseDetail has eligibility/status.
Public frontend route: `/certificates/verify/<code>`.
Private reads/downloads use current-session guards. Public verification state is
keyed by code/retry so a delayed result cannot appear under another code. Missing
disabled endpoints degrade safely; temporary503 failures show error and Retry.
Students have no issuance controls.

After approval/setup, Django Admin path:
`/admin/certificates/certificate/` → **Validate and issue certificate**.
No raw certificate add/edit form bypasses the eligibility service.

## Migration and issuance plan — AWAITING APPROVAL

Pending file:
`certificates/migrations/0004_coursecertificatepolicy_certificate_course_title_and_more.py`.
It adds policy tables, snapshot/audit/revocation fields, UUID default and unique
student/course constraint. Existing codes/rows are preserved. A preflight refuses
duplicate existing student/course certificates without deleting records. Current
read-only inspection found zero existing certificates. Migration consistency
passes; only0004 is in the real database's migration plan. It has **not** run.

Proposed activation sequence, not executed:

1. Obtain explicit approval for this migration/configuration plan and the exact
   issuer identity. Keep `CERTIFICATES_ENABLED=False` throughout migration.
2. Create a fresh SQLite online backup under
   `.local-course-backups/certificates-<timestamp>/db-before.sqlite3`; verify SHA256,
   `PRAGMA integrity_check`, foreign keys and table counts/content digests against
   a consistent source snapshot. Recheck migration plan; abort on unexpected work.
3. Apply only reviewed certificates0004. Verify integrity and that every existing
   record, course8 content and student-data digest is unchanged.
4. Provision declared `reportlab>=4.3.1,<5` in the project runtime, Unicode fonts,
   and an approved HTTPS `CERTIFICATE_PUBLIC_ORIGIN`. Test PDF/QR deployment.
5. Configure course8 policy: all six lessons91–96, published final quiz3 at its
   existing70%, required practical assignment1 in lesson96, approved issuer.
   No policy has been created or enabled in the real database.
6. Review eligibility and missing learner names using authorized administration.
   Do not alter student evidence just to qualify them. Enable the feature only
   after deployment readiness and approval.
7. Real issuance remains a separate explicit, confirmed administrator action
   after the user's issuance-plan approval. No automatic/bulk issuance is enabled.

No real backup was needed or read for this implementation because no real schema
or data write was performed. A **fresh verified backup is mandatory before step3**.

## PDF preview and prerequisites

Preview: `.playwright-mcp/certificate-preview.pdf` — prominently SAMPLE, with a
fictional Kazakh display name, demonstration issuer and example.invalid QR/link.
No Certificate record was created for it. Amethyst palette, embedded DejaVu fonts,
course/date/issuer and clickable verification link are included. No university
identity, signature or accreditation is claimed.

Project venv lacks ReportLab; an existing system ReportLab4.3.1 was used through
`PYTHONPATH=/usr/lib/python3/dist-packages` for isolated rendering tests. Nothing
was installed. Missing runtime dependencies/fonts produce an explicit unavailable
response, rather than exposing a traceback. Issuance stays disabled pending setup.
PDF supports Cyrillic/Kazakh text; interface is RU/KK/EN, PDF template is RU/EN.

## Validation and limits

- Full Django suite:300 tests, passed with3 PDF-rendering skips in ordinary venv.
- Certificates focused suite:24 tests, passed with those same3 dependency skips.
- Existing system ReportLab run:6 PDF checks,5 passed; missing-dependency branch
  skipped because dependency was present. Real PDF rasterization and Cyrillic/
  Kazakh text extraction passed; exact QR target and PDF URI annotation checked.
  Independent camera/decoder scanning was unavailable and is not claimed.
- Frontend:26 test files passed; lint and production build passed. One existing
  quiz-copy assertion was updated to the new completion wording.
- Django check and `makemigrations --check --dry-run` passed. Public courses API
  returns200 using a read-only connection; disabled verification returns404
  without querying new schema. No real migration was applied.
- Firefox:32 lesson cases (95/96 × four widths × two themes × two motion modes),
  all7 links visible, no overflow/page errors. Final stroke-centre precision
  rechecked at1440 and375px. Certificate disabled UI24 width/theme/language cases,
  actual unknown-code404 and synthetic503/retry/valid→delayed-unknown checks passed.
- Native security/frontend reviewers ran. Addressed verification component
  request-key isolation, temporary503 handling and migration database-alias use.
  Security reviewer found no backend authorization blocker. Parallel issuance
  load testing was not performed; transactional/unique guards were inspected.
- No authorized student session was available: lesson checks used actual saved
  educational JSON/live components; certificate success cases were synthetic.
  No real issuance, authenticated download or student submission was browser-tested.

Screenshots:
`.playwright-mcp/final-lesson-{95,96}-{1440,768,375,320}-{light,dark}-firefox.png`,
`.playwright-mcp/certificate-verification-503-375-firefox.png`,
`.playwright-mcp/certificate-disabled-375-dark-firefox.png`.

Development SQLite SHA256 equals its pre-task baseline. Original DOCX remains
unchanged. All enrollments, progress, assignments, attempts, quiz results, user
roles and course content are intact.

## Main changed files

Backend: `certificates/{models,services,views,urls,admin,pdf,tests,test_pdf}.py`,
certificate Admin templates, migration0004, `config/{settings,urls}.py`,
`requirements.txt`.

Frontend: certificate components/CSS and verification page, App/Profile/CourseDetail
integration, LessonResources, LessonView/styles, lesson95 reading CSS, PracticeCheck,
LessonQuiz copy, RU/KK/EN locales and focused regression tests. Prior uncommitted
course-refinement/configuration work was preserved.
