# Instructor Studio S4.1 — attachment placement and linked WebVTT

Implemented on `feat/studio-course-authoring` from `1a6894a`, 2026-11-16. Pre-existing settings and untracked materials preserved. No staging, commits, push, migrations or development database/media writes.

## Existing contract

Placement uses exact title strings in `LessonAttachment.after_section`. Student `attachmentLayout` links a video to WebVTT only if its anchor is nonempty and exactly one video and one VTT share it. Empty anchors are intentional gallery fallback, not caption pairing. Audio and SRT are independent; WebVTT is not separately rendered. The title-based model and protected delivery/grant APIs remain unchanged.

## Implemented behavior

The existing attachment manager displays saved placement, unresolved nonempty anchors, and each video's linked WebVTT label/filename (or missing/ambiguous status). Eligible audio/SRT/video rows have a selector in saved section order and an explicit move action. The target list uses the actual student section resolver, so text-only, legacy or incompatible structured lessons retain their current behavior rather than promising unsupported inline placement. Stable attachment row IDs avoid remounting rows after a move.

New route: `PATCH /api/studio/lessons/{lesson_id}/attachments/{attachment_id}/placement/`.

Payload fields:

- `after_section`: desired valid saved heading.
- `expected_after_section`: current persisted source anchor.
- `expected_sections`: exact ordered saved-heading snapshot.
- `expected_subtitle_id`: uniquely linked VTT ID, or null.

The endpoint uses existing active instructor/admin authorization, owner-scoped lesson lookup, course lock and atomic transaction. The attachment must belong to that same lesson. Saved headings must match the snapshot, occur uniquely/in order in the body and support the student renderer. Source/pairing changes, unsupported fields, invalid targets and published courses reject without changes. Video and its unique VTT move together; destination sections containing another video or VTT reject to prevent lost, ambiguous or newly invented caption associations. Ambiguous source groups cannot move. Direct WebVTT movement is intentionally deferred: move its uniquely linked video instead. Legacy source anchors can be explicitly resolved by moving an eligible asset/pair to a valid section; unrelated legacy records/SRT are unchanged. Blank source anchors never imply a pair.

Only after_section changes; attachment IDs, bytes, storage paths, filenames, hashes, captions, provenance and order are retained. The response is the authorized current attachment list. Successful authoring follows the existing source-review invalidation pattern; no-op and failed moves do not change it. Studio responses remain private/no-store. Explicit persistent video-to-track relations are deferred.

## Draft/save behavior

Pending section-title changes (including invalid raw input) and an active lesson save disable moves. During a move, section renaming and lesson saving are disabled; body typing remains available. Requests always use saved headings, never remap targets through a local pending rename. Existing S2.1 retained workspace data and S3 draft/acknowledgment behavior remain in use.

A successful move updates local media props immediately, clears only display-only old aliases, and refreshes the workspace. Raw lesson fields and dirty state remain intact. Failed moves retain placement and edits. Error/status copy uses RU/KK/EN. No media IDs/files are regenerated and no full lesson content is sent by the move action.

## Exact changed files

- `studio/attachment_placement.py` (new)
- `studio/test_attachment_placement.py` (new)
- `studio/views.py`
- `studio/urls.py`
- `frontend/src/utils/studioAttachmentPlacement.js` (new)
- `frontend/tests/studio-attachment-placement.test.mjs` (new)
- `frontend/src/components/instructor/LessonAttachmentManager.jsx`
- `frontend/src/components/instructor/LessonSections.jsx`
- `frontend/src/pages/instructor/Curriculum.jsx`
- `frontend/src/pages/instructor/instructor.css`
- `frontend/src/utils/instructorStudio.js`
- `frontend/src/i18n/locales/en.json`
- `frontend/src/i18n/locales/ru.json`
- `frontend/src/i18n/locales/kk.json`
- This report (new)
- `docs/project-memory/CURRENT_STATE.md`
- `docs/project-memory/DECISIONS.md`

## Automated verification executed

- `.venv/bin/python -B manage.py test studio.test_attachment_placement studio.test_section_renames studio.tests --noinput`: **41 passed**, disposable Django test database. New move tests use synthetic attachment file paths without storage writes; existing image test uses temporary media.
- `.venv/bin/python -B manage.py check`: passed.
- From `frontend/`: `node --test tests/*.test.mjs`: **38/38 test files passed**.
- New frontend placement file: six cases covering ordered targets/student pairing, reload layout, ambiguous/blank anchors, pending rename versus dirty text, legacy/fallback eligibility, and RU/KK/EN rendering/errors.
- `npm run lint`, `npm run build`, `git diff --check`: passed.
- Backend coverage: pair move/reload/student lesson response; exact metadata preservation; stale heading/source/track; invalid/ambiguous destination; duplicate source tracks; direct VTT denial; standalone SRT/audio; legacy/blank sources; reader fallback; anonymous/student/other-author/cross-lesson denial; published lock; no-op; rollback after the paired update actually executed (failure injected after updating both rows).

Initial test-fixture username duplication and temporary browser-adapter ID parsing errors were corrected; the final checks above passed. No application assertion was weakened to satisfy them.

## Actual browser observations (isolated fixture)

Existing Chromium and temporary Vite mounted actual CourseWorkspace/Curriculum and student MediaLessonReading, with an in-memory Axios adapter and synthetic local test video/VTT. No real authentication, Django requests, persistent fixture course, database or protected storage writes were used. Therefore this is not real-account/backend browser verification.

Observed:

- Linked VTT label/filename shown for video.
- Video and same VTT move from first to second section; orphan SRT stays unchanged.
- Unsaved body survives workspace reload after movement.
- Pending title rename disables movement; undo restores eligibility.
- Rejected move preserves placement and body; localized errors render at EN1440 dark, RU390 light, KK320 dark, without horizontal page overflow.
- Dirty navigation supports stay then discard; saved student renderer shows exactly one video under second heading and its original VTT ID902.
- Reopening editor retains saved movement; discarded body edits are not persisted.
- No uncaught page errors reported. Screenshot inspection confirmed linked media text and student placement. Artifacts: `/tmp/s41-browser/{report.json,placement-en-1440.png,placement-ru-390.png,placement-kk-320.png,student-preview.png}`; temporary and not staged.

Native security_reviewer and frontend_reviewer ran independent read-only reviews. Their fixes/test recommendations were addressed; no remaining confirmed implementation blocker reported. No native browser_qa run or real-account verification is claimed.

## Manual follow-up and limitations

On an isolated unpublished fixture: type unsaved prose, select another section on a captioned video, move and reopen; preview saved lesson and enable its subtitle track. Attempt a destination already containing video/VTT and verify rejection. Rename a heading without saving and verify movement is disabled. Exercise standalone SRT/audio and legacy anchors. Do not mutate Course 8/10 for verification.

No new schema or migration is required. No explicit track selection, detaching, section creation/deletion/reordering, or gallery relocation action was added. SQLite ignores select_for_update; the project retains its existing multiwriter lock-error limitation. These tests verify stale checks and transaction rollback, not concurrent-write serialization.

Working SQLite/settings hashes match the pre-task snapshot; Course10 remains unpublished, Course8/live records/media unchanged. Git index remains empty. Existing untracked materials remain preserved.
