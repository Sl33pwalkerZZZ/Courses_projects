# Instructor Studio S5.1 — final practical assignment authoring

Completed on `feat/studio-course-authoring`, starting at `f2c4b87`, resumed 2026-11-18. Existing unfinished implementation was retained and completed, without resetting or replacing unrelated work.

## Confirmed gap and existing contract

Assignment has only description, type and learning_activity; there is no separate title field. Studio now explicitly labels description as the assignment name and instructions, with guidance that both are saved together. No artificial title parsing/storage or schema migration was added. Line breaks remain visible in the shared student/Studio instruction rendering.

The final_media_project activity already existed in Lesson116 and in the server review service, but the Studio activity selector omitted it and AssignmentWriteSerializer rejected it. The existing selector and serializer now support it. Lesson116 was read only: assignment2, type text, activity final_media_project; no educational content or records were changed.

Submission options reflect actual existing validation:

- text: meaningful text, permitted files, or both; at least one component.
- file: at least one permitted file, explanatory text optional.
- ai_selection_map: existing specialized text-only interaction remains unchanged.
- final_media_project: supports text/file types, rejects quiz placeholders.

No new submission option enums or upload settings were introduced. Existing upload-limit copy is reused. Existing legacy quiz placeholders are preserved until their activity is explicitly changed; selecting a final project normalizes an incompatible quiz type to text. Quiz-editor logic and certificate configuration remain untouched.

## Rubric and preservation

The existing review rubric has four fixed criteria: completeness, application, quality, documentation, each integer0–25, total100. Studio and the student instruction view display these values read-only, reusing the review labels/criterion list. No scoring inputs, passing threshold, approval behavior or review service rules were changed.

The assignment list retains its data during same-path refreshes. Existing forms remain keyed by assignment ID; failed saves retain entered fields. Successful edits show the saved response; successful creates reset only the submitted create form. The existing backend refuses changes to assignments with submissions and retains published-course/ownership locks. Existing submissions, feedback, revisions and scores are not rewritten.

## Exact changed files

- studio/serializers.py
- studio/test_assignment_authoring.py (new)
- frontend/src/pages/instructor/Assessment.jsx
- frontend/src/components/learning/AssignmentSubmission.jsx
- frontend/src/components/learning/AssignmentInstructions.jsx (new)
- frontend/src/components/learning/assignmentInstructions.css (new)
- frontend/src/i18n/locales/en.json
- frontend/src/i18n/locales/ru.json
- frontend/src/i18n/locales/kk.json
- frontend/tests/studio-assignment-authoring.test.mjs (new)
- docs/instructor-studio/s5-1-assignment-authoring.md (this report, new)
- docs/project-memory/CURRENT_STATE.md
- docs/project-memory/DECISIONS.md

config/settings.py was already locally modified and is not a task change.

## Automated checks actually run

- `PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B /tmp/s51-run-django.py`:42 passed. The temporary runner explicitly uses a disposable SQLite test database and temporary MEDIA_ROOT/PUBLIC_MEDIA_ROOT. Labels: studio.test_assignment_authoring, studio.test_assignment_reviews, progress.test_assignment_submissions, progress.test_selection_maps.
- New backend tests cover create/edit/reopen, exact student lesson-response description, final text/file acceptance, invalid activity/empty description/final-quiz rejection, standard/map compatibility, student/other-author/anonymous denial, published lock, and unchanged historical submission/feedback/rubric records after rejected edits.
- `cd frontend && node tests/studio-assignment-authoring.test.mjs`:5 passed.
- `cd frontend && node --test tests/*.test.mjs`:39/39 test files passed.
- `npm run lint`:passed. `npm run build`:passed.
- `.venv/bin/python -B manage.py check`:passed.
- `git diff --check`:passed.

The existing review and selection-map regression suites passed; this is isolated regression evidence, not a mutation or live end-to-end test of Course8. No quiz or certificate implementation changes were made.

## Actual browser observations

The main agent used existing Chromium with a temporary Vite fixture mounting actual AssignmentManager/AssignmentForm and actual student AssignmentSubmission preview. Every API request was handled by an in-memory adapter; unexpected requests failed closed. No real authentication, Django requests, persistent draft course, submissions or media writes were used. These results are fixture-browser evidence, not real-account verification.

Observed:

- Whitespace-only instructions rejected locally with aria-invalid and no mutation request.
- Final project creation, saved activity and exact description preserved after reopening.
- Four read-only rubric entries visible, no score inputs.
- Edit text and select file-required mode; simulated backend validation error retained the draft and old stored text; retry/save/reopen retained the new type and exact text.
- Saved student preview showed exactly the stored description, including newlines, and four criteria; preview had no submission controls.
- Creating a normal assignment left the final project unchanged.
- EN1440dark, RU390light, KK320dark showed no horizontal page overflow. No uncaught page errors reported. Screenshots were visually inspected.

Temporary evidence: /tmp/s51-browser/report.json, editor-en-1440.png, editor-ru-390.png, editor-kk-320.png, student-preview.png; scripts fixture.jsx/run.mjs. Logs: /tmp/s51-django.log, /tmp/s51-final-frontend.log, /tmp/s51-final-lint.log, /tmp/s51-final-build.log. These may expire and are not staged.

Native security_reviewer completed the initial read-only contract review; native frontend_reviewer completed the resumed UI review. The latter identified incompatible legacy-quiz type preservation when switching to final project; this was fixed. No native browser_qa run is claimed.

## Remaining manual checks and safety

For a real authorized test environment, create an unpublished isolated lesson, choose Итоговый медиапроект, enter multiline description, save/reopen, change supported submission mode, then open saved student preview. Confirm submitted assignments remain locked by the existing server and review scores/history remain unchanged. Do not use real Course8/10 records for mutating checks.

SQLite/settings SHA-256 match the resume baseline. Course10 remains unpublished; Course8, Lesson116, live submissions/reviews, media and certificate settings are untouched. No migration, staging, commit or push. Navigation confirmation for assignment forms is not a new feature in this slice; lesson-editor S2.1/S3/S4.1 behavior is preserved by regression tests.
