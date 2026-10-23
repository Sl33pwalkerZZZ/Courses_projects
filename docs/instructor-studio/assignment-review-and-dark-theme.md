# Assignment review and dark-theme refinement — 2026-10-23

Branch `design/amethyst-motion`, checkpoint `8c3cf2f`. Existing uncommitted
certificate-admin fixes were preserved. No migration, dependency installation,
real submission decision, certificate issuance, role change, commit or push.

## Why review was difficult to find

Instructor Studio already supported review through **My Courses → course →
Submissions**, implemented inside Publication.jsx. There was no top-level inbox
or dashboard shortcut, so this course-specific tab was easy to miss. Django
Admin exposed a different status editor; it lacked reviewer-ID audit evidence
required by certificate eligibility and was not a substitute for the teacher flow.

## Existing and completed functionality

Student SelectionMap already saves drafts, restores them through its GET endpoint,
submits pending work and shows status, teacher feedback and previous decisions.
Pending/approved work is locked; rejection permits revision/resubmission. This
student data/state implementation was retained.

Added `/instructor/submissions` with a visible **Работы студентов** navigation
entry and dashboard shortcut. It lists pending work by default, with approved,
rejected and all filters. Each card identifies student/course/lesson/date and
opens instructions and submitted text/structured answers/authorized attachment.
Known structured field labels, classifications and dates respect RU/KK/EN.
Approvals/rejections require confirmation; rejection requires feedback.
Parent-level success feedback persists after reload and receives keyboard focus.
Admin links with `?submission=<id>` open the selected record rather than hiding it
behind the pending filter. The course-specific submissions tab reuses this screen.

New `GET /api/studio/submissions/` reuses existing ownership filters and submission
models; drafts are excluded. Existing per-course GET, attachment GET and
`POST /api/studio/submissions/<id>/review/` remain in use.

One shared atomic `progress.services.review_assignment_submission` now controls
decisions. Active author/owner or authorized administrator is required. Self-review
is denied for every role, including superusers. Course and submission locks,
post-lock ownership recheck, pending-state validation and revision checks protect
the decision. Each review increments revision and records reviewer ID, status,
feedback and ISO timestamp in review_history, matching reviewed_at.

Django Admin submissions are now ownership-scoped read-only inspection with a
Studio link, no draft visibility and no add/change/delete forms. This prevents
unaudited direct status edits. It does not introduce another approval workflow.

## Certificate evidence and historical records

New approvals pass the existing `certificates.services.approved_submission` check:
current approved state plus authorized reviewer, timestamp and matching revision
in the latest audit entry. Certificate policies and issuance settings are untouched;
an approved assignment alone does not complete all certificate conditions.

Historical approved records without reliable evidence remain unchanged and are
explicitly labelled unverifiable/ineligible in the review UI. No automatic
conversion, backdated audit or inferred approval was performed. The ordinary
review workflow remains pending-only; remediation of already-approved unaudited
records needs a separately authorized explicit re-review path, not a raw status
edit or manufactured historical evidence.

## Manual use

1. Student opens lesson96 → selection map, fills anonymized data, saves draft.
2. Reopen lesson: saved draft restores. Submit when complete; status becomes pending.
3. Teacher/course owner or administrator opens Instructor Studio → **Работы
   студентов** → pending work → **Открыть работу студента**.
4. Review all submitted material, add feedback, approve or reject and confirm.
5. Student reopens the lesson to see status/feedback; rejected work can be revised
   and resubmitted. All real decisions remain manual; none were executed here.

## Central dark tokens

All changes live in `frontend/src/styles/v2-tokens.css`; existing index.css aliases
propagate them across public pages, lessons, profiles and Studio.

| Token group | Dark values |
| --- | --- |
| `--v2-canvas` | **#16181c** |
| `--v2-surface`, `--v2-surface-raised` | #1e2127 / #282c34 |
| `--v2-text`, `--v2-text-muted` | #F4F5F7 / #C4C7D0 |
| `--v2-border`, `--v2-control-border` | #414650 / #858C9B |
| hero canvas/raised/text/muted/border | corresponding neutral tokens above |
| overlay | rgb(22 24 28 / 78%) |
| activity0–3 | #282c34 / #8A68A8 / #A081C3 / #B594E5 |

Purple primary/link/focus/accent and activity4 remain unchanged. Light-theme
overrides are byte-for-byte unchanged. Images/external previews were not recolored.
Automated token contrast checks require normal text≥4.5:1, controls/focus≥3:1,
and active dark activity fills against empty cells≥3:1. This is targeted contrast
validation, not a claim of a full WCAG conformance audit.

## Validation and evidence

- Django full suite:313 tests,312 passed,1 expected dependency-absence skip.
- Frontend:27 test files passed, lint and production build passed.
- Django check and `makemigrations --check --dry-run`: passed, no schema changes.
- Isolated API fixtures cover draft save/reopen/submit, owner approval, rejection/
  resubmission, student/other-teacher/admin permissions, self-review denial,
  stale revisions, post-lock ownership change, private drafts, audit evidence and
  historical approval rejection. Prior Admin tests now assert read-only behavior.
- Native security reviewer found no blocking issue; suggested post-lock ownership
  hardening, implemented with a regression test.
- Native frontend reviewer identified lost confirmation/focus after reload;
  implemented persistent parent status and verified it in Firefox.
- Native browser QA:4 actual public homepage cases,24 teacher/student synthetic
  cases across desktop/mobile and dark/light,6 locale checks and keyboard details.
  Synthetic intercepted approve/reject tests confirm persistent focused success
  feedback, row removal and preserved rejection note, including320px.
- Charts and quiz choices checked with synthetic fixtures at1440/320px in both
  themes after theme transitions settled. No steady-state overflow/page errors.
- No authorized real student session was used. Protected screenshots are explicitly
  fixtures; all mutation requests were blocked except intercepted synthetic review
  responses. Full real-account navigation and persistence were not browser-tested.

Screenshots in `.playwright-mcp/`:

- `assignment-theme-home-{1440,375}-{dark,light}-firefox.png`
- `assignment-teacher-fixture-{1440,375}-{dark,light}-firefox.png`
- `assignment-student-fixture-{1440,375}-{dark,light}-firefox.png`
- `assignment-review-success-320-firefox.png`
- `assignment-theme-chart-quiz-fixture-{1440,320}-{dark,light}-firefox.png`
- `assignment-theme-quiz-settled-{1440,320}-{dark,light}-firefox.png`

Main agent visually inspected teacher/mobile and student/approved screenshots.
The teacher375dark screenshot was refreshed after translated answer labels.
Development SQLite SHA256 matches the pre-task baseline, preserving real users,
submissions, progress, enrollments, quiz attempts and certificate policies.

## Changed files

Backend: progress/admin.py, services.py and selection-map tests; studio/views.py,
urls.py, presentation.py and role-security tests; new studio/test_assignment_reviews.py.

Frontend: new pages/instructor/Submissions.jsx; InstructorStudio/CourseEditor/
Publication/App navigation; RU/KK/EN locales; styles/v2-tokens.css; new
assignment-review tests and updated contrast tests. No new migration files.
