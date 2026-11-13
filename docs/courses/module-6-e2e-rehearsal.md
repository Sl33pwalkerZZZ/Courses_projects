# Module 6 isolated assessment rehearsal — P1C

Date: 2026-11-12. Branch: `design/amethyst-motion`, HEAD `e1ae750` (four commits ahead of the local origin reference). This is API/service rehearsal plus static UI inspection, **not real-browser approval or publication readiness**.

## Isolation evidence

- The harness `/tmp/p1c_rehearsal.py` overrides `DATABASES` **before `django.setup()`**. Base and Django test SQLite paths are inside a fresh `TemporaryDirectory(prefix="ai-courses-p1c-")`; private/public media roots and importer backups also reside there. Migrations, synthetic accounts, submissions, quiz attempts and the single issued certificate existed only in this disposable environment. Django destroyed its test DB; the temporary directory was cleaned in `finally`.
- Working `db.sqlite3` SHA-256 before and after: `3c45b29b552d7b4ef5f9b78c672c8146317b42c6ab0257cc2c2ef4e105e4ecb3`. No live ORM mutations or live user-data inspection. Real Courses 8/10, publication, certificate policies and protected media were untouched.
- Synthetic Course ID 10 uses the existing slug with five synthetic instructional modules/15 lessons. The actual `import_media_module_6 --apply` command created Module 6 from `courses/management/media_module_6.json` in that temporary DB, using its real verified-backup path. No assessment content was invented. IDs other than the importer-required synthetic Course 10 are resolved through relations, not assumed to equal live IDs 116/2/5.
- Modules 1–5 in this harness are structural fixtures, not copies of their real educational content/media. This rehearsal does not revalidate the entire real course or its videos.
- Canonical importer creates a draft quiz. The harness published only that synthetic quiz via model validation/save to exercise the existing published-assessment contract. Global `CERTIFICATES_ENABLED=True` and a reserved synthetic verification origin were process-local overrides only.
- Initial harness runs failed because the fixture omitted open enrollment and because manually closing a streaming response ended the test transaction. These were corrected in the temporary harness; no application code or security assertion was changed. An initial invocation also required adding the project to `PYTHONPATH`.

## Full workflow results

| Stage | Observed result |
|---|---|
| Registration/login/restoration | Actual register, JWT login, refresh and authenticated identity APIs passed; no force-authentication for the learner. Staff API clients use isolated test authentication. |
| Enrollment | Unpublished-course enrollment API returned 404 as intended. Synthetic course temporarily published, open enrollment API returned 201, then course was unpublished again. Existing enrollment retained authorized draft access. This simulates the already-enrolled real learner without changing the real course. |
| Curriculum/lesson access | Draft CourseDetail returned six modules/16 lessons; final assessment lesson accessible to the enrolled learner. |
| Instructional progress | All 15 required instructional lessons completed using completion POST API; 15 real progress rows verified. Assessment-lesson completion was not required for certificate scope. |
| Initial practical submission | Multipart text + TXT file returned 201/pending; duplicate pending request returned 409. |
| Teacher review | Unrelated author denied (403/404); owning author rejected with feedback and four criterion scores. Fractional criterion input returned 400. |
| Revision and approval | Learner resubmission created a separate linked record. Owner approved it; history preserved rejected then approved versions. Further learner submission returned 409. |
| Protected submission file | Authorized download response 200; anonymous 401 and unauthorized author 403. Existing regression tests exercise file contents, ownership and safety. |
| Final quiz | Published API exposed 15 questions without pre-answer `is_correct`. Ten correct produced 66.67%, failed; eleven correct produced 73.33%, passed at threshold 70%. Both attempts persisted under the synthetic student. With 15 equal-weight questions, exactly 70% is not attainable. |
| Certificate identity | Student saved and explicitly confirmed `Әлия Синтетическая` through PUT/POST API. |
| Initial certificate block | Administrator issuance returned 400 with unpublished course/disabled policy. No certificate created. |
| Administrative policy setup | Only in the test DB: simulated publication; actual Django Admin policy change form enabled the policy, retained 15 required lessons, final quiz and assignment, and configured an approved synthetic issuer. Form returned 302; server eligibility became true. Publication was a fixture state simulation, not a test of the Studio publication-review workflow. |
| Issuance | Student/author issuance attempts returned 403. Administrator API returned 201; repeat returned 200 with exactly one certificate. Student/course/name/issuer and the exact lesson, assignment-revision and passed-attempt evidence were checked. |
| PDF/verification | Student download returned PDF (51,752 bytes); anonymous public verification returned valid status and initials without full learner name. No real certificate was issued. |

## Negative cases and regression coverage

The connected journey independently toggled isolated state and verified both ineligibility and issuance refusal for: incomplete required lesson; pending assignment; rejected assignment; no passed quiz; unconfirmed name; disabled policy; unapproved issuer; unpublished course; loss of current learner enrollment. Temporary state was restored between checks. These predicate-isolation changes were deliberate test fixture mutations, not supported user actions or evidence fabrication.

Additional synthetic unenrolled learner denied; duplicate pending submissions, unauthorized review and issuance, approved lock, history retention, student association and duplicate certificate issuance passed. Existing suites additionally cover reopen/new revision invalidating old assignment evidence, invalid/stale reviewer evidence, scoped/foreign lessons, quiz authorization/idempotency, revoked certificates, owner-only downloads and global issuance disablement. Course 8's specialized `ai_selection_map` regression suite passed without changing live Course 8.

## PDF checks

`certificates.test_pdf` exercised Unicode Cyrillic/Kazakh text extraction with `pdftotext`, raster rendering with `pdftoppm`, verification URI, real ReportLab QR payload construction, missing-font failure, and revoked/unsafe-URL guards. ReportLab is installed, so its missing-dependency branch was the single skipped test. A phone/camera scan of the rendered QR and human visual PDF approval remain NOT TESTED. No production issuer identity or production verification origin was approved by this rehearsal.

## Commands and results

Temporary rehearsal and existing regressions:

```bash
PYTHONPATH="$PWD:/tmp" PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B /tmp/p1c_rehearsal.py
```

This calls Django test with:

```text
p1c_rehearsal.Rehearsal
progress.test_assignment_submissions
progress.test_selection_maps
studio.test_assignment_reviews
quizzes.tests
certificates.tests
certificates.test_admin
certificates.test_pdf
courses.test_module6_import
```

**134 discovered: 133 passed, 1 skipped, 0 failed** on the final run (8.776 seconds). Includes one connected API journey with multiple checkpoints; checkpoints are not counted as separate tests. System checks passed. Isolated SQLite `integrity_check=ok`, zero foreign-key violations. Full log: `/tmp/p1c-test-results.log`. The temporary harness/log are local diagnostic artifacts, not durable repository tests.

Frontend, from `frontend/` after sourcing existing NVM:

```bash
node --test --test-concurrency=2 --test-timeout=30000 tests/assignment-submission.test.mjs tests/assignment-review.test.mjs tests/quizzes.test.mjs tests/certificates.test.mjs
```

**4 test files passed, 0 failed.** This runner reports file counts. No frontend code changed; lint/build were not rerun in this diagnostic phase. `git diff --check` passed.

## Frontend inspection and ranked follow-ups

Native `frontend_reviewer` ran a read-only source contract review, with no DB/browser actions. Assignment fields/history/download routes, quiz payload/results, certificate-name save/confirmation and teacher review/reopen contracts match the backend. Draft/global-disabled certificate unavailability is deliberately handled as unavailable in the UI.

- **P0:** No confirmed blocker found in the rehearsed assessment/issuance chain. This is not proof that every security path is covered.
- **P2 confirmed UI mismatch:** `frontend/src/pages/instructor/Submissions.jsx:62` converts rubric input using `Number()` and permits fractions; button submission does not invoke native form validation. Backend `studio/serializers.py` requires integer scores. The rehearsal confirmed 12.5 returns 400. Minimal proposed fix: validate whole numbers 0–25 before posting and show localized inline feedback; preserve strict backend checks. No fix applied during this audit.
- **P1 release gate:** Real authenticated browser journey remains NOT TESTED. Playwright MCP was attempted and could not launch its configured Firefox executable. No installation, credential extraction or persistent login/account creation was attempted.
- **P1 release gate:** Human issuer approval, real deployment origin/global switch, publication/source approval and PDF sign-off remain separate owner decisions. Passing this rehearsal does not authorize them.
- **P2 coverage:** Keep the connected journey as a durable isolated regression test in a separately approved implementation task; today it is a temporary diagnostic harness. Existing tests cover reopening, but the connected final-project journey stops after issuance and does not reopen its approved revision.

## Remaining human/browser checks

In an authorized disposable environment, verify full lesson navigation, six-module mobile sidebar, file selection/errors/download, rejected feedback and resubmission history, teacher rubric/review queue, failing/passing quiz results, name confirmation, certificate status refresh/list/download and QR scanning. Do not run assessment submissions, completion actions or issuance against real learner records merely to repeat this rehearsal. Existing production videos/subtitles, responsive interaction, cross-tab behavior in a real account and visual PDF approval were not browser-tested here.

## Working-tree preservation

Pre-audit Git status saved at `/tmp/p1c-status-before.txt`; status before writing this report matched it byte-for-byte. Only this new report is added by P1C inside the repository. Existing tracked/untracked work, including intentional settings changes, is preserved. No application/source/migration/manifest modifications, staging, commits, pushes, publication or production media changes. Project memory was not changed because this phase is diagnostic and the report is the requested output; implementation history remains intact.
