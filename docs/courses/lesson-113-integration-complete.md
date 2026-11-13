# Phase 5I — Lesson 113 integration complete

Local integration authorized and completed on 2026-11-06, branch `design/amethyst-motion`. Course 10 (`ai-media-content`) remains **unpublished**. No new course, module, lesson, assessment, enrollment, progress, certificate, migration or publication record was created. No commit/push/deployment. Main React frontend and `config/settings.py` were not changed.

## Attachments and exact approved sources

Production directory: `video-production/lesson-113-production/out/quality-v2/`.

| Attachment ID / order | Filename | Duration | Exact `after_section` |
|---|---|---:|---|
| 9 / 1 | `m5-l13-v1-source-organization-quality-v2.mp4` | 46s | `3. Ф1: папки, имена и разрешения на материалы` |
| 10 / 2 | `m5-l13-v2-project-import-quality-v2.mp4` | 47s | `5. Новый проект и импорт в CapCut Desktop` |
| 11 / 3 | `m5-l13-v3-timeline-reopen-quality-v2.mp4` | 54s | `7. Таймлайн и повторное открытие проекта` |

Verified SHA-256:

```text
9  e10e855ab2ad53816f5bbd245b0e5b2f0f3b0a019d9bfff75a7940b5f746aa7f
10 d17bd4577c2d3a86fcde4338af2bc9f4b4437b80a88ad977dc8ea97916cd638e
11 a11da7005d5b47781545fa634d603f7b3380c60e50ec4d039936bc103c018084
```

All source MP4 bytes are unchanged. Existing validators accepted actual signatures/ffprobe metadata: H.264/yuv420p, 1920×1080, 30fps, AAC-LC stereo 48kHz. Storage uses the existing private `lessons/attachments/<random>/...` mechanism. Actual serialized metadata exposes only `/api/lesson-attachments/{id}/` and `/api/lesson-attachments/{id}/playback-grant/`, no public storage path. Native video uses the existing scoped grants and Range delivery; no permanent JWT URLs or Blob-buffering change.

Each video has a visible caption identifying a schematic interface rather than an actual CapCut recording, plus the approved concise text equivalent of the visible actions. There is no narration; no false spoken VTT was created. Original background music and tonal effects remain unmodified.

## Actual lesson-text update

Only `courses_lesson.id=113.text_content` changed, applying all ten exact paragraph edits from the Phase 5H proposal. The complete before/after and paragraph hunks are retained in `courses/management/lesson113_quality_v2.json`; review history remains in `video-production/lesson-113-production/content/quality-v2/lesson-113-sync-proposal.json`.

1. Added the silent/schematic notice and distinguished tutorial lengths from the 45-second F1 exercise.
2. Shortened repeated naming explanations while retaining independent definitions of source, project and export.
3. Added the Video 1 watch cue after the original rights discussion.
4. Added folder/copy/provenance practice at the start of section 4.
5. Clarified first-clip placement versus later assembly and added the Video 2 watch cue.
6. Added post-video project/import/first-clip practice before the detailed ratio explanation.
7. Clarified saving through the installed version's supported workflow before reopening.
8. Added conditional missing-source recovery and the Video 3 watch cue; students must not manufacture an error by moving/deleting files.
9. Added optional, ungraded reopen/boundary self-check after Video 3.
10. Shortened the repeated summary, preserving editable-project/MP4 and publication cautions.

The reader places each video after the complete anchored section; practice follows in sections 4/6/8. The lesson remains independently readable. Three original objectives, all nine original headings/order, the structured learning metadata, definitions, fictional F1 case, rights explanation and ungraded practice boundaries are preserved. `LessonLearningContent.id=20` was not changed. Module 39 still contains lessons 113/114/115 in the same order. Course 10 still has five modules/fifteen lessons. Modules 1–4 and lessons 114/115 remain identical.

## Canonical source and reproducibility

Changed:

- `courses/management/media_module_5.json`: only first lesson's text; all other fields and lessons unchanged.
- `courses/management/commands/import_media_module_5.py`: only reviewed source checksum pin.
- `docs/courses/media-module-5-assets.json`: three actual approved/integrated video records, hashes/captions/text equivalents/IDs and truthful no-narration VTT status; lessons 14/15 remain planned.

Added:

- `courses/management/commands/integrate_lesson113_videos.py`
- `courses/management/lesson113_quality_v2.json`
- `courses/test_lesson113_integration.py`
- This report.

Canonical source SHA-256: `82814d69536adda49b684e83cf174945bd3c00e932c9be0dbef7a2add85c1149`.
Pinned integration plan SHA-256: `054b65629f4a41ec33684f57dce47c32c7035591014dfce530a82b276352911a`.

```sh
.venv/bin/python -B manage.py integrate_lesson113_videos --dry-run
.venv/bin/python -B manage.py integrate_lesson113_videos --apply
```

Default is dry-run. The completed-state rerun reports `KEEP 3; approved text unchanged; no-op, no backup or writes.` Do not use the generic batch attachment importer (it rejects videos), or the create-only module importer as a lesson updater.

The narrow command accepts only the exact original text with zero attachments, or the exact completed text with the three expected matching bytes/metadata/order. It refuses mixed/conflicting states. Before writing it validates all three files and anchors, creates/verifies the backup, then locks the course and updates text plus attachments in one transaction. New storage files are tracked and removed on exceptions; pre-existing files are never deleted. Tests inject failure after storing file 2 to verify both SQL rollback and file cleanup.

## Verified backup and preservation

Fresh backup directory:

```text
/home/almas/Desktop/courses/Courses_projects/.local-course-backups/lesson113-phase5i-20261106-044424-7f2e801f/
```

Files:

- `media-module-before-14025eb0869f451ba073520e1e7f2cfa.sqlite3` — online SQLite backup from a read-only source; integrity `ok`, zero foreign-key violations.
- `protected-media-and-approved-sources.tar` — all existing protected media plus the three approved source MP4s; every archived byte stream verified against its SHA-256 inventory.
- `before-state.json` — original Lesson 113 text/metadata, empty attachment inventory, source/media checksums and backup reference.

Private directory/file permissions are used. Disk space was verified. Existing backups were not overwritten.

Post-apply read-only, in-engine SQL comparisons checked all 39 tables against the backup without retrieving private learner/account records. The only differences are Lesson 113 text, new attachment rows 9/10/11 and their SQLite sequence. Schema and all other records are identical. Every pre-existing protected media checksum is unchanged; local settings and approved source MP4 hashes are unchanged. Live SQLite integrity/FK checks still pass.

Rollback, if later explicitly authorized: use the before-state and recorded IDs/hashes; remove only these new attachment rows/grants/files and restore only Lesson 113 text if it still matches the exact approved after-state. Never restore an old whole database over newer learner activity. Abrupt process termination/power loss can leave a new filesystem object before SQL commits; reconcile only new paths/hashes against the retained inventory. The supervised apply completed successfully with no orphan files or partial state observed.

## Validation results

- **56 Django tests passed**: command dry-run/idempotency, exact edits/guards, source/module import, backup verification, conflicts/missing/corrupt files, rollback/orphan cleanup, protected metadata/files, grant expiry/revocation, GET/HEAD/Range/416 and upload validation.
- One test copies **all three real approved MP4s** into temporary media in an isolated test database, runs real ffprobe validation, imports them, verifies full GET hashes, HEAD lengths, prefix/suffix 206 ranges, unsatisfiable 416, expired grants and revoked grants. No grant, account or test-course record was created in the development database.
- **34 frontend test files passed**, zero failures.
- Frontend lint and production build passed; Django system check passed; `makemigrations --check --dry-run`: no changes detected; Git whitespace check passed.
- Final dry-run: `KEEP 3`, no writes.

The first new fixture omitted the review timestamp for a rejected request and was corrected to satisfy the existing model constraint. Sandboxed Python event-loop thread wakeups stalled an existing async-stream test; a minimal `asyncio.to_thread` check reproduced that environment restriction. The final complete suite ran outside that restriction with an explicit timeout and passed; no application async/auth code was changed.

Evidence: `.local-cinematic-qa/phase5i/` (`apply.log`, `live-verification.json`, `idempotency.log`, `actual-attachment-serializer.json`, `django-verified-final.log`, frontend/check/build logs).

## Browser QA and limitations

Native `security_reviewer` and `browser_qa` ran read-only reviews. Security review found no blocking defect.

Playwright MCP Firefox could not launch because its executable is missing; nothing was installed. The existing separate Node Chromium fallback ran an isolated presentation fixture with the approved real lesson AFTER text, nine-section metadata and three video text equivalents. All API requests were intercepted; this was not a real logged-in account.

**22 browser checks passed:** 1440/390/320px, RU/KK/EN, light/dark, correct sections 3/5/7 and ordering, accessible labels/transcripts, native controls, keyboard focus, reduced motion, loading and error/retry states. Mocked playback/seeking reached 20s; no JavaScript rendering errors. Expected mocked 403 feedback and media-request cancellations on navigation are recorded separately. At 320px the schematic interface is small; fullscreen and readable text equivalents are available.

Screenshots: `.local-cinematic-qa/phase5i/dark-320-video-2.png`, `light-1440-video-3.png`, other matrix screenshots. Full browser notes: `.local-cinematic-qa/phase5i/QA-NOTES.md` and `report.json`.

No real authenticated browser session was available. Actual account login, live protected grant playback and seeking in the normal Firefox session remain a manual check; backend behavior with real MP4 bytes was verified in isolation. No passwords/tokens were requested or exposed.

## Where to inspect

With existing Django/Vite running via `./run.sh`, sign in normally as the owning instructor or an authorized administrator:

- Exact lesson: **http://localhost:5173/lessons/113**
- Authorized course preview: http://localhost:5173/instructor/courses/ai-media-content/preview
- Curriculum: http://localhost:5173/instructor/courses/10/curriculum

Open lesson 113; verify videos follow sections 3, 5 and 7, captions/text equivalents are readable, and play/seek/fullscreen work. The unpublished course must stay unpublished; no learner enrollment or publication change is needed for authorized instructor preview.
