# Enrollment request management

Implemented on `design/amethyst-motion`, 2026-10-21.

## Root cause

Applications already used `progress.EnrollmentRequest`, and Django Admin already registered a working review list, individual approve/reject buttons and bulk actions. React's student application form and history existed, but Instructor Studio had no enrollment-review page, navigation entry or REST review endpoints. Publication Reviews reviews course publication, not student enrollment. This was a missing administrative integration, not a missing request or enrollment model.

## Where to click

1. Sign into React as the existing authorized administrator `almas`.
2. Open **Instructor Studio → Заявки на обучение** (English: Enrollment requests; Kazakh: localized equivalent).
3. Direct route: `/instructor/enrollment-requests` on the normal frontend host.
4. The default filter is pending. Identify the intended student's username and course title, review the application, optionally enter an explanation, then select Approve or Reject and confirm.
5. A successful approval grants course access immediately in the backend. Refresh the student's course or Profile page to restore the approved enrollment and lesson links. The published quiz is available through its lesson; approval does not complete lessons or attempts.
6. Use Approved, Rejected or All filters to inspect decision history. Rejected students may reapply through the existing student form; earlier requests remain intact.

Existing Django Admin alternative: `/admin/progress/enrollmentrequest/`. Its approve/reject controls use the same service. No real request was decided during implementation or QA.

## Backend

- `GET /api/studio/enrollment-requests/?status=pending|approved|rejected|all` lists applicant username, course, application message, status, submission/review dates and explanation. Default: pending. Invalid filters return 400.
- `POST /api/studio/enrollment-requests/<id>/decision/` accepts exactly `decision: approve|reject` and optional `note` (up to 10,000 characters), returning the actual request state and `changed` flag.
- Both operations require active Studio administrator authority (`role=admin` or explicit Django superuser override). Students, ordinary authors, staff-only students and inactive users cannot list or decide applications.
- Decisions reuse `progress.services.review_enrollment_request`: one transaction, consistent course/application lock order, pending-only transitions, reviewer/timestamp recording and `Enrollment.get_or_create` under the existing unique student/course constraint. Repeated or conflicting later decisions preserve the first decision and return `changed=false`.
- The existing service now recognizes trusted active Studio administrators as well as its existing Django Admin staff-plus-explicit-model-permission authority. That separate Django Admin authority was intentionally retained; no accounts or roles were changed.
- No new models, migrations, enrollment system or competing decision service were added. The existing student APIs, course/lesson permissions, assignment access and published-quiz enrollment checks remain in use.

## React

The moderator-only route and navigation use existing Studio guards, themes, components and RU/KK/EN translations. The page includes pending/history filters, loading, retry, empty states, labelled note controls, confirmation and accessible success/error announcements. Decisions are never sent on page load or cancellation. The UI reports the actual stored status when another administrator has already decided a request, rather than claiming a stale approval succeeded. Existing request cancellation and authentication-session isolation remain shared with Studio.

Files: `frontend/src/pages/instructor/EnrollmentRequests.jsx`, `App.jsx`, `pages/instructor/InstructorStudio.jsx`, three locale dictionaries; backend `studio/views.py`, `urls.py`, `serializers.py` and `progress/services.py`. Focused regression files: `studio/test_enrollment_management.py`, `studio/test_role_security.py`, `progress/test_enrollment_requests.py` and `frontend/tests/enrollment-requests.test.mjs`.

## Verification and safety

- Full Django suite: **271 tests passed**, isolated temporary database only. Covers roles, private lists, unknown IDs, filter/payload validation, duplicate approval, stale conflicting decisions, rejection/reapplication, existing enrollment reuse and rollback after a failed save. A student is denied protected lessons, the practical assignment and a published 15-question quiz before approval and can retrieve all three afterward. Answer keys remain absent from student quiz responses.
- Frontend: **19 test files passed**; lint and production build passed.
- Django system check passed; migration consistency reports no changes; migration plan has no operations. No migrations were applied.
- Independent native security and frontend reviewers found no blocking issues. Native browser QA ran Firefox using intercepted synthetic applications and sessions, never the actual student's request. Pending details, cancellation with no POST, approval/rejection and history/reload, explanations, stale decisions, loading/empty/error/retry states, student/author denial, superuser override, keyboard focus and reduced motion passed. At 1440px EN/light, 768px RU/light, 375px RU/dark and 320px KK/light there was no horizontal overflow, unlabelled input, JavaScript error or unexpected API request. Screenshots: `.playwright-mcp/enrollment-<width>-<language>-<theme>-firefox.png`. Browser QA caught reused assignment wording on decision buttons; page-specific enrollment labels were added in all three languages. Actual protected student lesson/quiz access was verified by the isolated backend lifecycle test, not by logging into a real student browser session.
- Read-only verification confirmed course 8 is published with approval enrollment, lessons 91–96 remain present and quiz 3 remains published with 15 questions. Only aggregate request counts were inspected; private real application messages were not read. SQLite's byte hash is checked against the pre-implementation baseline. No course, request, account, enrollment, progress, quiz attempt or media records were changed.

SQLite does not implement row-level `select_for_update`; concurrent writers may receive database-lock errors, which the UI displays for retry. Existing uniqueness and transactions protect against duplicate enrollments and partial approvals. This work verifies repeated approvals and rollback; it does not claim a concurrent-writer stress test.
