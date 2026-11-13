# Lesson 113 — Quality V2 integration proposal (Phase 5H)

Status: REVIEW ONLY. No uploads, database updates, course publication or schema changes authorized/executed by this phase. Course 10 (`ai-media-content`), module 39, lesson 113 remain unchanged.

## Deliverables and reproduction

Production root: `video-production/lesson-113-production/`.

- Approved, untouched Video 1: `out/quality-v2/m5-l13-v1-source-organization-quality-v2.mp4` (46 seconds; SHA-256 `e10e855ab2ad53816f5bbd245b0e5b2f0f3b0a019d9bfff75a7940b5f746aa7f`).
- New Video 2: `out/quality-v2/m5-l13-v2-project-import-quality-v2.mp4` (47 seconds).
- New Video 3: `out/quality-v2/m5-l13-v3-timeline-reopen-quality-v2.mp4` (54 seconds).

All are silent instructional diagrams with music/tonal feedback, not CapCut screen recordings. No narration or invented spoken subtitles. The 45-second F1 project in the lesson is a student exercise, not the tutorial running time.

New source: `src/quality-v2/SeriesWorkspace.tsx`, `lesson113-series.tsx`, `content/quality-v2/series.json`. The original Video 1 composition, files and all original exports were preserved. Video 2 demonstrates creating a project, the library/preview/timeline distinction, importing before placing, first-clip placement, aspect ratio and source/project/export distinctions. Video 3 continues that first clip, assembles five scenes, distinguishes video/audio tracks, adjusts 5 to 7 seconds without a gap, checks the boundary, reminds students to save before reopening and conditionally restores a missing source. Audio lane stays empty: no invented voice waveform or playback.

From the production directory, with existing Node on PATH:

```sh
npm run lint
node scripts/render_phase5h.mjs --preview
python3 -B scripts/extract_phase5h_frames.py
# Inspect frames/current-source Studio and record phase5h-frame-review.json first.
node scripts/render_phase5h.mjs --final
python3 -B scripts/phase5h_audio.py prepare
python3 -B scripts/phase5h_audio.py mix
python3 -B scripts/verify_phase5h.py
```

Scripts refuse to overwrite exports/stems; these are reproduction instructions for a clean output workspace, not commands to rerun over approved files. Rendering selects only Videos 2/3. New source hashes are checked before/after each render. The preview frame review gate precedes full export. Existing approved master/SFX checksums gate audio reuse. No model downloads, new synthesis or application dependencies.

## Exact attachment placement

Kind `video`, MIME `video/mp4`. Reuse these existing exact `after_section` values:

| Video | Existing stable section anchor | Follow-up practice |
|---|---|---|
| 1 | `3. Ф1: папки, имена и разрешения на материалы` | Start of section 4: organize copies, filenames and provenance before the detailed shot plan. |
| 2 | `5. Новый проект и импорт в CapCut Desktop` | Start of section 6: create/import/select/place first clip; independently check voice source and frame proportions. |
| 3 | `7. Таймлайн и повторное открытие проекта` | Start of section 8: save/reopen, verify order, durations, source links and boundaries. |

The reader places attachments after the complete anchored section, not immediately below its heading. Each proposed watch cue is the final paragraph of that section. No section is renamed; the ratio demonstration previews the next section without removing its explanation.

Accessible text equivalents and scene descriptions: three `.equivalent.ru.txt` and three `.transcript.ru.md` files in `content/quality-v2/`, named after the three final video basenames. These describe visible actions, not speech. Store the concise equivalent in the existing video `transcript` field. They explicitly identify the schematic interface; no fake timed VTT has been created. A future authored WebVTT description track requires actual matching timing and review. VTT is optional, not a prerequisite to uploading these music-only videos with visible text and text equivalents.

`content/quality-v2/lesson-113-video-integration.json` is a review manifest with actual final file checksums/metadata and upload metadata. It is NOT input for the current batch importer.

## Exact written-content proposal

`content/quality-v2/lesson-113-sync-proposal.json` contains the full before/after and ten exact paragraph replacements, not loose editorial instructions. Baseline lesson text SHA-256: `bba2bf3d971de54c96fbfcc877765ab8ce98bdb5946460e5d79cc0b54ab004ae`. Snapshot: `content/quality-v2/lesson-113-readonly-snapshot.json`.

Proposed edits only to `Lesson.text_content`:

1. Add one schematic/silent-video notice and distinguish tutorial versus exercise durations.
2. Shorten a repeated explanation of project/source naming while retaining the independent definitions and link warnings.
3. Add the Video 1 watch cue after the original rights discussion.
4. Put folder/provenance practice after Video 1, before the preserved shot-plan explanation.
5. Clarify that Video 2 places the first clip; full assembly follows in section 7. Add its watch cue.
6. Put import/first-clip practice before the preserved aspect-ratio/pixel explanation.
7. Explicitly save with the installed version's supported mechanism before leaving/reopening; no fictional guaranteed save button/cloud behavior.
8. Add a conditional missing-source check and Video 3 watch cue. Never ask students to delete/move files to manufacture an error.
9. Put an optional, ungraded reopen/boundary self-check after Video 3.
10. Shorten the repeated final definitions, preserving MP4-versus-editable-project and publication warnings.

All three existing objectives, nine existing section headings/order, definitions, F1 fictional status, licensing/rights, structured schema, Russian language, ungraded practice and assessment boundaries remain. Nothing proposes new graded assessments. The written lesson still independently teaches the topic.

Do not apply this proposal automatically. Re-read the live lesson and reject any unexpected current title, IDs, module, text, objectives, sections or attachments. If already at the exact reviewed after-state, no-op; if at exact before-state, update only the approved field in a transaction. Reject mixed/unknown states. Preserve `LessonLearningContent` metadata as-is.

The existing Module 5 importer is create-only and source-hash-pinned: do not use it as an update command. After approval, update only the matching lesson text in `courses/management/media_module_5.json` as the reproducible source mirror, with a reviewed checksum/test update. This phase leaves that source untouched.

## Existing protected-upload contract and remaining implementation gap

Authorized multipart endpoint: `POST /api/studio/lessons/113/attachments/`. Owner or explicit moderator/admin only; published courses cannot be edited through this path. Authorize against the course, not merely `is_staff`.

The metadata object accepts exactly five strings: `label` (1–255), `caption` (up to 2000), `transcript` (nonempty, up to 20000), `provenance` (nonempty, up to 4000), `after_section` (up to 255, exact section heading). There is no video `alt_text` field. Caller cannot set attachment order; the API appends. Use the reviewed manifest, validate all assets first and upload in Video 1/2/3 order only after approval.

Actual validator: MP4, one H.264 yuv420p video stream (supported Baseline/Main/High profiles, level <=5.1), <=60fps, <=3840×2160, positive finite duration; optional one AAC-LC mono/stereo 44.1/48k audio stream. Default size limit 250MiB (`LESSON_VIDEO_MAX_BYTES`). No unrelated streams. ffprobe required. Existing SRT/audio behavior unchanged.

**Do not pass this manifest to `import_lesson_media`: that command currently rejects video/VTT and has a 20MiB batch limit.** The existing upload endpoint validates/stores/deduplicates videos but its three separate uploads are not a single atomic group. The next approved integration task should implement a narrow reviewed idempotent orchestration command (or explicitly accept staged uploads), using existing validators/storage services. It must reject conflicting bytes/filenames/metadata, validate all inputs before writes, lock the target course and combine the guarded text update plus three attachment rows in a transaction. File writes require explicit rollback cleanup; a DB transaction alone cannot roll back storage. Do not invent a second media system. No migration is needed.

## Playback and safety

The protected player requests a short-lived authenticated playback grant; native media uses a signed HttpOnly SameSite=Strict path-scoped cookie. No permanent JWT in URLs or full-file Blob playback. Each request checks grant expiry/revocation, active user/session, attachment hash and current lesson access. Default grant lifetime 300s, capped by JWT expiry. Owner/admin preview works for the draft; ordinary public users must not receive draft metadata/files. Existing enrollment/access semantics must remain unchanged. Confirm authorized preview, unauthorized/pending/rejected access, seek/range responses and logout/revocation in the future integration task.

Before any approved writes: fresh SQLite online backup into a new private destination; verify integrity and foreign-key checks. Separately inventory and back up protected media and three source MP4s with checksums. Snapshot only targeted lesson fields and any existing attachments. No resets, whole-DB restores over later student activity, content reimports or course publication.

Rollback: record newly created attachment IDs and stored paths. Delete only new rows/files whose ownership/hash still match, revoke only their grants, restore only the targeted text field if it still equals the exact proposed after-state. Never delete pre-existing/deduplicated assets or unrelated records. Preserve all old production exports for rollback.

## Verification and limitations

Evidence and final measurements are in `out/quality-v2/phase5h-validation.json`, `phase5h-video-validator.json`, `phase5h-frame-review.json`, `phase5h-frames-{preview,final}/` and `phase5h-browser/`. Final production report: `PHASE-5H.md`.

Native `frontend_reviewer`, `security_reviewer` and `browser_qa` ran read-only reviews. Chromium fallback was used; Firefox MCP was unavailable. Studio/frame/file-playback evidence is not authenticated protected-player testing. No student session, live upload or live permission mutation was performed. Objective decode/peak/cue tests do not establish human listening approval of the new full videos. Author review and explicit lesson-content/upload approval remain required.
