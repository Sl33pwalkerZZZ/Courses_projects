# Instructor Studio S5.2 — final quiz authoring

Completed on feat/studio-course-authoring from S5.1 checkpoint 9a4386b. Existing local settings and untracked production work were preserved.

## Confirmed gaps and narrow correction

The existing editor/API already round-trips quiz title, instructions, passing_percentage, ordered question text/type/explanation, choices and correctness. No new endpoint, model or assessment rule was needed.

- Client validation previously accepted blank passing_percentage through Number('') = 0 and accepted fractions that the server rejects. It now requires an integer 0–100, with native step=1 and localized fallback feedback. No silent rounding.
- Quiz resource reload after PUT previously replaced the editor with loading UI. Same-scope refresh now retains the existing editor; initial loading/errors/retry and permission/session boundaries remain provided by useStudioResource. A different lesson still has a distinct keyed editor.
- Existing server limits (100 questions, 20 choices per question) are reflected in client validation/add controls; minimum two choices remains unchanged.
- Radio groups now have a per-editor useId prefix. Multiple mounted editors cannot share selection groups.
- RU/KK/EN guidance distinguishes single/exactly-one and multiple/exact-set grading and explains the current answer disclosure policy.

## Existing safety and student policy, unchanged

Studio GET/PUT /api/studio/lessons/:id/quiz/ remains owner/admin scoped. Published course, published quiz or any existing quiz attempt prevents rewriting. Unassessed unpublished draft PUT atomically replaces questions/choices. Existing attempts must not be cleared to enable editing.

Student quiz GET excludes is_correct, explanation and correct IDs. After a valid submission, only the enrolled owner can inspect their attempt's answer snapshot, correct choices and explanations. This immediate post-submission feedback is the existing policy, not a new disclosure rule. Scoring and pass decisions remain server-side; multiple answers require exact-set equality.

Lesson116 was inspected only through read-only SQLite metadata: existing quiz5, published, threshold70, 15 questions/60 choices. No answer keys or learner data were copied into fixtures. Courses8/10 and all real attempts remain untouched.

## Changed files

- frontend/src/pages/instructor/Assessment.jsx
- frontend/src/utils/instructorStudio.js
- frontend/src/i18n/locales/ru.json
- frontend/src/i18n/locales/kk.json
- frontend/src/i18n/locales/en.json
- frontend/tests/studio-quiz-authoring.test.mjs
- studio/test_quiz_authoring.py
- docs/instructor-studio/s5-2-quiz-authoring.md
- docs/project-memory/CURRENT_STATE.md

## Automated evidence

- Temporary isolated Django runner: PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B /tmp/s52-tests.py. It overrides DATABASES to a temporary SQLite path/TEST.NAME=:memory: and media roots to a temporary directory before django.setup. Labels: studio.test_quiz_authoring, studio.tests, quizzes.tests. Final run: **72 passed**, no failures; isolated database destroyed.
- New backend regression creates a synthetic draft course/quiz, edits question/correct choice/threshold, reopens exact API output, rejects fractional threshold without mutation, checks student key privacy, scores wrong/right attempts, and verifies attempts/answer snapshots remain identical after a rejected rewrite of an assessed quiz.
- From frontend: node --test tests/studio-quiz-authoring.test.mjs tests/instructor-studio.test.mjs: **2/2 files passed**. New file contains three threshold/cardinality/SSR-locale regression cases.
- node --test tests/*.test.mjs: **40/40 files passed**, zero failed.
- npm run lint; npm run build: passed.
- PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B manage.py check: no issues.
- git diff --check: passed.

## Actual browser evidence and limits

Existing local Chromium was driven against a temporary Vite fixture under /tmp/s52-browser, mounting the actual LessonAssessments/QuizEditor. All API traffic was replaced by an in-memory adapter; unexpected routes throw. No login, persistent account, live API or database writes were involved.

Observed successful flow: open existing fixture quiz → edit question/instructions/threshold and select second correct option → synthetic400 save error retains fields → retry succeeds → delayed resource refresh retains editor fields → remount/reopen retains question, correct answer and threshold85. Native fractional step validation was verified. Initial fixture setup had Vite/driver errors, corrected before the final successful run; those attempts are not passing application checks.

This is an actual rendered component interaction, not a real authenticated end-to-end browser session. Backend persistence, scoring and disclosure were verified separately by isolated Django tests. No human-authenticated Course10 edit or real student attempt was performed. Temporary fixture files are diagnostic artifacts and may expire.

## Manual authorized follow-up

On an isolated unpublished course only: open Assessment, choose a lesson with an unassessed draft quiz, edit question/options/key and integer threshold, save, switch away and reopen. Check exact stored text and key. Exercise a rejected save and verify input remains. Publish only the isolated test quiz through authorized test controls, submit synthetic answers as its enrolled test learner, and inspect own feedback/history. Confirm assessed quizzes are locked. Do not do this against live Course8/10 or real learner progress.

## Preservation

No backend application code, API contract, models, migrations, certificate settings or live content changed. SQLite SHA-256 remained 02a8d41b53aad2be8898f3b0f8cf6b9ded912ef55486b1cc165f089372905b00; existing local config/settings.py remained ea683b8b7bf47ca027890feaa09e4ca384a017b48670a87c73b452a923f39931. No staging, commits, push, publication or cleanup. Native frontend_reviewer and security_reviewer ran read-only and found no scoped blocking defect; browser interactions above were performed by the main agent.
