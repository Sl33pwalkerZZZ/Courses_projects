# Media Production and Integration

**Evidence date:** 2026-11-09. This guide summarizes the audited toolchain; it does not claim each output can be regenerated from tracked files.

## Runtime media flow

Course images, audio, subtitles and video are `LessonImage`/`LessonAttachment` records backed by protected files. Upload and import paths validate type/size/signature; delivery resolves paths within protected storage and checks lesson access. Video upload additionally inspects supported MP4 streams with system `ffprobe`. Native video obtains short-lived scoped playback authorization and streams byte ranges. See [`docs/protected-lesson-video.md`](../protected-lesson-video.md), `courses/media.py`, `courses/attachments.py`, `courses/video_validation.py`, `courses/video.py` and `courses/management/commands/import_lesson_media.py`.

Frontend placement uses stable lesson section anchors. `MediaLessonReading.jsx`, `frontend/src/utils/lessonAttachments.js` and `frontend/src/utils/lessonVideo.js` render image/audio/video/download content inline where metadata supplies an anchor, with fallbacks for unplaced media. Never replace this protected flow with public file URLs.

## Production tool map

| Tool | Confirmed use | Reproducibility boundary |
|---|---|---|
| Remotion | Isolated React-based projects under `video-production/`; source/composition packages and output files supported Lesson 113/114 production. | Production directory is untracked and mixed: source, package files, outputs, previews, logs, frame captures, QA and `node_modules`. Do not add the entire tree or rerender approved work without authorization. |
| FFmpeg / FFprobe | System tools detected; FFmpeg used for audio/video inspection and final audio mixing; FFprobe used by MP4 validation and media audits. | Versions/environment are not fully pinned by the app. Inspect project scripts and exact source inputs before reproducing. |
| Silero TTS | Local, offline Module 4 generation with MIT `v5_cis_base_nostress`, speaker `ru_roman`. | Model/runtime/checkpoint are not application dependencies; follow tracked provenance and license documents. Local candidates may be unapproved. |
| Conventional DSP | Procedural room-noise and filtering experiments for Module 4 Lesson 12. | Marked as DSP, not AI. Experiments are local/untracked and are not automatically production deliverables. |
| CapCut Desktop | Taught as an editing workflow in Course 10 Module 5. | Course content and storyboards are not proof the app was used to create integrated videos. |
| OBS Studio | No confirmed invocation/use in the audited source. | Actual screen recording provenance for Lesson 115 is not yet available. |

## Course asset state from the audit

- **Module 3:** six PNG illustrations, tracked source assets in `course_assets/module_3/`; imported and inline placement was confirmed in the audit. The JSON manifest's overall planning-only status was stale.
- **Module 4:** seven approved production assets: six protected attachment records (Lesson 10 narration; Lesson 11 speech, illustrative SRT and synchronized SRT; Lesson 12 before/after audio) plus the Lesson 12 workflow image. Approved Silero attribution/license and provenance are documented. Additional local untracked legacy/candidate audio exists and must not be mistaken for current production assets.
- **Lesson 113:** three integrated videos, with source/integration documents and commands in the local working tree. Output files and production package are not Git tracked according to the audit.
- **Lesson 114:** three integrated videos plus two VTT tracks. Matching DB/storage hashes were reported in the audit. Source/integration artifacts are untracked. Authenticated real-browser verification remained incomplete.
- **Lesson 115:** no video/VTT assets or attachment records in the audit. Planned items are `m5-l15-v1-export-check`, `m5-l15-v2-vertical-adaptation`, and `m5-l15-v3-final-review`; planned anchors follow sections 3, 5 and 7 respectively. Production, recording, narration, captions and integration remain work.

## Safe reproduction sequence

1. Read current status and the module's dated content/asset manifest; confirm current lesson mapping without relying on assumed numeric IDs.
2. Obtain/verify actual source media, permissions, narration transcripts and captions. Do not fabricate screens or treat plans as delivered files.
3. Produce in an isolated work area; preserve approved sources and record tool/model versions, licenses, command, duration, codec, sample rate, hashes and human approval.
4. Validate media with FFprobe and playback, and validate SRT/VTT timing against actual audio/video.
5. Back up SQLite and affected protected media; run importer dry-run and tests; only write after task-specific approval.
6. Verify attachment ownership, placement, access controls and the student-visible rendering. Keep Course 10 unpublished unless explicitly approved.

For asset counts, hashes, provenance and known orphan/duplicate caveats, use [the media audit](../project-audit/03-media-and-production-audit.md); it is more detailed and dated.
