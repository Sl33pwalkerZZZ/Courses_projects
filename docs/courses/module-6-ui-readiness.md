# P1D — rubric validation and manual student UI readiness

2026-11-12. Scope: frontend-only rubric validation. No backend, migrations, real database, content, assessment-rule, media, certificate-policy or publication changes.

## Defect and correction

The existing rubric has exactly four criteria (`completeness`, `application`, `quality`, `documentation`), each an integer 0–25. Backend validation in `studio/serializers.py::ReviewWriteSerializer` and `progress/services.py::review_assignment_submission` remains authoritative and unchanged.

Previously the input handler silently clamped out-of-range scores, replaced empty input with zero, and retained fractional numbers. Buttons outside native form validation could send fractions to a backend that rejects them.

The input now retains raw values. `validateRubricScores` checks all four required criteria, rejects empty/non-numeric/fractional/negative/>25 values and converts valid values to numeric integers for the existing payload. No rounding/clamping is performed. Inputs have required/min/max/step constraints plus localized associated errors (`aria-invalid`, `aria-describedby`). Invalid approve/reject attempts focus the first invalid field and return before confirmation or POST. Total is shown only when all scores are valid. Existing initial zero defaults, statuses, feedback, backend errors, scoring rules and workflows are preserved.

## Verification actually run

- Focused: `node --test-timeout=30000 tests/assignment-review.test.mjs`: **8 passed, 0 failed**. Covers valid boundaries, invalid fraction/range/empty/non-number input, no mutation, rendered constraints/ARIA/errors in RU/KK/EN and server rubric-error formatting. Existing self-review/readonly/reopen checks remain.
- Full frontend: `node --test --test-concurrency=2 --test-timeout=30000 tests/*.test.mjs`: **35 files passed, 0 failed**. Log `/tmp/p1d-frontend-tests.log`.
- `npm run lint` and `npm run build`: passed.
- Django `test studio.test_assignment_reviews progress.test_assignment_submissions`: **16 passed** with `DATABASES` overridden before setup to in-memory SQLite and temporary private/public media roots. Django system checks passed. No development DB migrations.
- `git diff --check`: passed.
- Native `frontend_reviewer` independently reviewed the narrow patch read-only and found no confirmed defect; it did not run tests or inspect the database.
- Existing cached Chromium/Playwright-core (no installation) ran `/tmp/p1d-browser.cjs`: **12 combinations** (RU/KK/EN × light/dark × 1440/320 px). Invalid 12.5, -1, 26 and empty inputs preserved; both decisions blocked without confirmation/POST and focused the invalid input. Valid integer keyboard approval and rejection sent correct numeric payloads. Simulated backend400 remained visible without losing entered scores. Zero real API requests (API blocked and component client mocked); zero page exceptions; no horizontal overflow. Screenshots `/tmp/p1d-rubric-1440.png`, `/tmp/p1d-rubric-320.png`.
- QA setup initially encountered outdated optimized dependency URLs; corrected only the temporary harness to use each dependency's actual Vite version. Vite client WebSocket/HMR diagnostics persisted because local network connections were blocked; do not interpret this as a clean-console real application test. Temporary Vite server was stopped. No authorized real-account session was used.
- Working `db.sqlite3` SHA-256 before/after: `3c45b29b552d7b4ef5f9b78c672c8146317b42c6ab0257cc2c2ef4e105e4ecb3` (unchanged).

## Short manual checklist — existing local sessions only

Use `http://localhost:5173` with the already enrolled student, owning author or authorized administrator. Do not grant roles, create enrollment, submit/review work, complete lessons or issue certificates to enable this check. These account capabilities are verified by source/tests, not by inspecting real account credentials/records in P1D.

### Student (read-only)

1. Open `/courses/ai-media-content` from the existing enrolled session; reload. Confirm authorized draft visibility and six modules/16 lessons. An un-enrolled visitor must not gain draft access; do not publish to work around a denial.
2. Open `/lessons/100`, expand the full curriculum, then open Module6 `/lessons/116`. At 320/390px check sidebar layout and keyboard navigation. Do not click lesson completion.
3. Open `/lessons/113`, `/lessons/114`, `/lessons/115`; check each video's presence, playback/seek and available subtitle controls. Do not modify attachments.
4. On Lesson116 inspect assignment description/history/feedback and file controls; do not submit. Inspect quiz question/results UI without submitting an attempt.
5. Open `/profile` and inspect certificate-name controls without saving/confirming a different name. Disabled certificates/draft status must not imply eligibility or issuance.
6. Check Network/Console for unexpected failures; never copy Authorization headers, cookies or tokens into reports.

### Instructor / administrator (read-only)

1. Open `/instructor/courses/10/curriculum`, use its existing lesson-preview links; or `/instructor/courses/ai-media-content/preview`. Confirm draft preview without enrollment mutation.
2. Open `/instructor/courses/10/submissions`. If there is no existing pending final-project submission, an empty list is legitimate; **do not create a real submission** just for QA.
3. Where a pending review already exists, changing rubric fields is local form state: inspect integer0–25 validation and associated messages, then leave without a decision. Use the isolated fixture, not real pending work, to exercise approve/reject requests or simulated backend errors. A non-owner must remain denied.
4. Open `/instructor/courses/10/assessment` and inspect existing questions/threshold without saving or changing publication. For an authorized admin, inspect `/admin/certificates/coursecertificatepolicy/` without changing policy/issuer or issuing a certificate. Course10 must remain unpublished and its policy disabled.

## Checkpoint readiness

No failing automated check remains for this patch. Real-account/browser sign-off remains outstanding and is not replaced by fixture testing. The broad dirty tree predates P1D: any Git checkpoint requires an explicit file-by-file staging review; intentional `config/settings.py`, SQLite, backups, protected media, temporary QA assets and unrelated experiments must stay excluded. No staging/commit/push was performed.

Modified P1D paths: `frontend/src/pages/instructor/Submissions.jsx`, `frontend/src/utils/instructorStudio.js`, `frontend/src/i18n/locales/{ru,kk,en}.json`, `frontend/tests/assignment-review.test.mjs`, this report, and `docs/project-memory/CURRENT_STATE.md`.
