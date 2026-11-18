# Instructor Studio S6 — preview and publication readiness

Implemented from 5f370ee on feat/studio-course-authoring (2026-11-18). Existing local settings/untracked assets preserved. No server rules, endpoints, models or migration changes.

## Existing workflow and roles

Studio publication GET/POST /api/studio/courses/:id/publication/ is scoped to an active owning author or active admin-role/superuser. Staff alone does not grant authoring/moderation authority. POST creates a review request, never directly publishes; published courses and duplicate pending requests reject. Only literal boolean true acknowledges reviews.

Only a moderator (active admin-role/superuser) can list /api/studio/reviews/ or POST /api/studio/reviews/:id/decision/. Approval locks course/request, rechecks unchanged fingerprint and all gates, then atomically publishes the course and all its quizzes. Rejection needs a reason. Existing rules do not require a different person from the requester when the requester is an administrator.

The server currently checks exactly seven conditions (studio/services.py requirements):

1. Nonblank title.
2. Nonblank description.
3. At least one lesson, and every module contains lessons.
4. Every lesson has a nonblank title and main text_content.
5. At least one quiz; every quiz passes existing validate_quiz (threshold0–100, questions, nonblank choices, at least two choices, exactly one correct single answer or at least one correct multiple answer).
6. Source review: no CourseImport, explicit acknowledgement, or an already approved import.
7. Explicit assessment-review acknowledgement.

Assignments, objectives, media, subtitles, accessibility and certificates are not added as publication gates. The new preparation advice is explicitly labelled recommendations.

A draft can change while a request is pending. Approval then refuses a fingerprint mismatch. Moderator rejection with feedback and a new author request are necessary. Current status payload does not expose a dedicated stale flag, so UI explains this condition without pretending to detect it.

## Presentation changes

Publication now displays current published/pending/rejected/draft state, server checklist, localized next steps and links to course settings/curriculum/assessment. Missing review acknowledgements can focus their confirmation checkbox. Existing student preview URL /instructor/courses/:slug/preview is reused; moderators also see the review-queue link. Request remains disabled until loaded requirements and applicable confirmations are met, and while pending/published/busy. Server remains final authority. Existing request history/feedback is retained; timestamps follow current interface language. Refresh rechecks saved server state.

The preview API remains authenticated owner/admin-only, private/no-store and does not enroll a viewer. No preview API or student lesson rendering was changed.

## Read-only Course10 reference

Read through SQLite URI mode=ro and Django ORM with that read-only connection: Course10 remains unpublished,6modules/16lessons. Title/description/curriculum/lesson_content/assessment gates pass. With no supplied review acknowledgements, source_reviewed and assessment_reviewed are false. No request or publication was performed against this course.

## Files

- frontend/src/pages/instructor/Publication.jsx
- frontend/src/i18n/locales/ru.json
- frontend/src/i18n/locales/kk.json
- frontend/src/i18n/locales/en.json
- frontend/tests/studio-publication-readiness.test.mjs
- studio/test_publication_readiness.py
- docs/instructor-studio/s6-publication-readiness.md
- docs/project-memory/CURRENT_STATE.md

## Automated validation

- PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B /tmp/s6-tests.py:24 Django tests passed. Temporary runner overrides DATABASES to disposable SQLite/:memory: test DB and temporary media roots before django.setup; labels studio.test_publication_readiness and studio.tests. Synthetic fixture only; test DB destroyed.
- New backend rehearsal checks seven gates, missing-quiz and empty-text blockers, author correction, authorized preview with no enrollment, required acknowledgements, request creation without publication, duplicate request rejection, author approval denial, admin approval and published state. Existing Studio tests also cover stale fingerprints, reasoned rejection/resubmission, import guards and role isolation.
- From frontend: node --test tests/studio-publication-readiness.test.mjs tests/instructor-studio.test.mjs passed2/2 files; direct node tests/studio-publication-readiness.test.mjs passed4 cases after final assertion update.
- node --test tests/*.test.mjs:41/41 files passed,0failed. The final test-only assertion addition was then rerun successfully in the focused file.
- npm run lint; npm run build passed after application changes.
- PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B manage.py check: no issues.
- git diff --check passed.

## Actual browser evidence — isolated fixture

Existing Chromium with temporary Vite fixture /tmp/s6-browser mounted actual Publication, QuizEditor, InstructorPreview and PublicationReviews with MemoryRouter and an in-memory Axios adapter. Synthetic client identity was used only inside this adapter-backed fixture; no actual credentials or live API calls. Unexpected routes throw. Temporary diagnostic artifacts may expire.

Observed: blocked request → assessment link opens actual quiz editor → save removes quiz blocker → existing student preview shows synthetic course/module/lesson → acknowledgement enables request → request becomes pending without publication and duplicate submit disables → synthetic moderator role exposes review queue → review acknowledgement/approve updates published status → published request remains locked. One initial fixture attempt lacked the route's :slug parameter; corrected fixture then passed. This was not a production defect.

Real authenticated browser/backend end-to-end publication was not performed. Backend persistence, transactions and role checks were verified separately on isolated Django fixtures. No real account login, progress update or real course publication occurred. No mobile visual claim is made.

## Preservation

SQLite SHA-256 stayed02a8d41b53aad2be8898f3b0f8cf6b9ded912ef55486b1cc165f089372905b00; config/settings.py stayedea683b8b7bf47ca027890feaa09e4ca384a017b48670a87c73b452a923f39931. Course8/10, real media, assessments, certificates and publication state untouched. Index remains empty; no staging/commit/push or cleanup.

Native frontend_reviewer and security_reviewer completed independent read-only reviews. Frontend review found a disabled pending confirmation initially inconsistent with the server checklist; initialization was corrected and covered by checked-checkbox assertions. No blocking findings remain. Main agent performed the browser fixture checks.
