# Instructor Studio S3 — existing sections and safe title renaming

Implementation on `feat/studio-course-authoring`, starting at `2050986` (2026-11-16). No staging/commits/push, migrations or development database writes.

## Data contract and scope

The section identifier in this schema is its exact title string: `LessonLearningContent.source_sections`, standalone paragraphs in `Lesson.text_content`, `image_placement.after_section`, and `LessonAttachment.after_section`. Video/VTT association is derived from the shared anchor, not filename. No new section IDs or schema were introduced.

The editor now shows sections in source order with image/audio/SRT/video/VTT inventory. Missing/ambiguous anchors are explicitly unresolved. Legacy identifiers which do not correspond to unique body headings are read-only; plain lessons retain the existing text editor. No section creation/deletion/reordering or media pairing UI was added.

Renaming edits the local body heading, source section and image placements, and accumulates explicit `section_renames: [{from_title, to_title}]` for the existing lesson PATCH. Server validation rejects stale/duplicate/missing headings, body/section order mismatches, target collisions (including orphan media), missing image references and conflicting operations. On the existing atomic transaction, all matching lesson-owned attachment anchors move together; IDs/files/checksums/captions/provenance/order remain intact. Ownership and published-course locks are unchanged. The lesson is refreshed after acquiring the course lock before expected-old validation.

Existing unresolved image placements may be preserved unchanged, but new/changed placements still require valid lesson-owned images and anchors. They are never silently repaired. No public media paths or permission contracts changed.

## S2.1 preservation

Raw heading input belongs to the existing draft (including invalid/empty input), participates in dirty confirmation, and blocks saving if invalid. Labels/errors use RU/KK/EN with aria-invalid and associated feedback. Background workspace refresh cannot reset the form. Failed PATCH retains edits. Successful PATCH acknowledges only submitted edits; newer rename intents are rebased to the saved heading. Display-only aliases are scoped by attachment ID and expected previous anchor, so delayed/failed workspace reload cannot temporarily detach media or confuse reused titles. They are not sent to the API and do not create a false dirty state.

## Reference inspection (read-only)

Course 10 remains unpublished with six modules/sixteen lessons. All stored source headings correspond uniquely to body paragraphs. Lesson 113 has nine sections and three videos anchored after sections 3/5/7. Existing video/VTT anchors in lessons 114/115 resolve. No reference content, manifests or records were edited.

## Files

- `studio/section_renames.py`, `studio/serializers.py`, `studio/views.py`, `studio/test_section_renames.py`
- `frontend/src/utils/studioSections.js`, `frontend/src/utils/studioDraft.js`
- `frontend/src/components/instructor/LessonSections.jsx`, `frontend/src/components/instructor/useLessonDraft.js`
- `frontend/src/pages/instructor/Curriculum.jsx`, `frontend/src/pages/instructor/instructor.css`
- `frontend/src/i18n/locales/{ru,kk,en}.json`
- `frontend/tests/studio-sections.test.mjs`, `frontend/tests/studio-draft.test.mjs`
- This report and appended project-memory updates. Pre-existing memory/settings/untracked work preserved.

The S2.1 test snapshot now uses the actual raw submitted form (as the handler does), rather than a serialized API payload which intentionally excludes editor-only fields; existing assertions remain.

## Automated verification

- `.venv/bin/python -B manage.py test studio.test_section_renames studio.tests --noinput`: **32 passed**, disposable test database. Synthetic file paths only in new tests; existing image-upload test uses temporary media.
- `.venv/bin/python -B manage.py check`: passed.
- From frontend: `node --test tests/*.test.mjs`: **37/37 test files passed**.
- New section utility regressions: ordered inventory, image/video/VTT mapping, save/reload student resolver, ambiguous/body/orphan collisions, save-race rebasing, stale-prop inventory, freed-heading reuse, conflicting batch and plain/legacy fallback. S2.1 draft/navigation tests remain passing.
- `npm run lint`, `npm run build`, `git diff --check`: passed.
- Backend tests also cover transaction rollback, stale replay, orphan preservation, image-reference preservation, student/other-author denial and published-course lock.

## Browser evidence and limitations

Actual existing Chromium ran the real CourseWorkspace/Curriculum/editor and student MediaLessonReading with an isolated in-memory Axios adapter. This is not an authenticated real-account test. No Django calls, account creation or persistent fixture data were used.

Observed: linked video/VTT inventory and unresolved SRT; rename survives module refresh; stay preserves draft; duplicate title blocks saving with aria-invalid; failed save retains title; newer rename during held PATCH survives/rebases; second save/reopen retains the heading; student renderer places video beneath the new heading with the correct VTT track. EN1440 dark, RU390 light and KK320 dark showed no horizontal page overflow. Browser output/screen captures are temporary under `/tmp/s3-browser/`; no screenshots were added to Git. Native frontend/security reviewers ran read-only; frontend reviewer caught and verified the attachment-alias collision fix. No native browser_qa review or human listening/playback approval is claimed.

Manual follow-up on an isolated draft: open a lesson, rename a unique section with video/VTT, trigger attachment/module refresh, try stay/discard, simulate failed save, save/reopen and open saved student preview. Verify text, placement and subtitle toggle. For a plain lesson check text editing; for ambiguous/orphan references verify warnings rather than guessed reassignment. Do not use real Course 10 to mutate test content.

## Safety

Working SQLite and local settings SHA-256 match their pre-task values. Course 10 remains unpublished; Course 8, live lessons/media/student data and certificate configuration unchanged. No migration or real import is needed. Section editing beyond rename and reader redesign remain deferred.
