# Module 4 — audio production: authored draft and media plan

No real import, migration, publication or media association applied by this task.

## Educational structure

Existing course is located by slug `ai-media-content`, never by a fixed database ID. It must remain an unpublished Russian draft with Modules 1–3 present. New module order 4: **Создание и обработка аудио с помощью ИИ**.

| Course lesson | Title | Local order | Objectives | Body characters |
| --- | --- | --- | --- | --- |
| 10 | Генерация речи и озвучка медиаматериалов | 1 | 3 | 9085 |
| 11 | Распознавание речи и создание субтитров | 2 | 3 | 8056 |
| 12 | Обработка звука и подготовка аудио для монтажа | 3 | 3 | 9494 |

Lesson 10: TTS versus human narration; text for listening; pauses, pronunciation, intonation and pace; a complete F1 workflow; source/consent checks; mistakes, takeaways and ungraded practice.

Lesson 11: STT versus translation; transcription review; a deliberately constructed negation error; timestamps and segmentation; a valid three-cue UTF-8 SRT; accessibility and sensitive interview handling; takeaways and ungraded practice.

Lesson 12: sample rate, channels, level and clipping; noise reduction and artifacts; intelligibility, music balance, format choices and export review; a complete F1 production sequence; takeaways and ungraded practice.

Full Russian authored draft: `courses/management/media_module_4.json`. Every lesson has three objectives, nine exact metadata headings, substantial explanations, definitions, concrete steps and corrections. The unchanged renderer recognizes these headings/tables and preserves SRT line breaks. No ID-specific presentation rules or React changes are introduced.

Ф1 is the same explicitly fictional paper-reuse project as Modules 2–3. No real participant, interview, TTS output, STT result, experimental outcome or product interface is claimed. Written sample errors are labelled illustrative. Platform/version-dependent features must be checked in the instructor's actual installation. Source-content review remains an educator task.

No quizzes, graded assignments, submissions, rubrics, thresholds or certificate rules. Graded work remains reserved for Module 6.

## Media manifest and real local examples

`docs/courses/media-module-4-assets.json` describes five teaching examples, with filenames/formats, lesson association, placement anchors, purpose, caption, alternative explanation and provenance/permissions.

| Example | State |
| --- | --- |
| Synthetic narration | Missing: needs a permitted standard voice and documented production |
| Speech with corrected transcript | Missing: needs a consented recording or clearly labelled synthetic source, then a real transcript check |
| SRT example | Created locally: `course_assets/module_4/m4-l2-f1-example.srt` |
| Original/processed comparison | Missing: requires the same authorized source, documented processing and level-matched review |
| Workflow diagram | Created locally: `course_assets/module_4/m4-l3-audio-workflow.png` |

The SRT contains three syntactically valid, sequential, nonoverlapping cues covering 0–10.5 seconds. **Its times are illustrative, not aligned to an existing recording.** It is a local file ready for manual use; there is currently no in-app lesson-file download endpoint. It must not be described as verified subtitles for a real clip.

The diagram is an original 1600×900 PNG drawn with Pillow and the existing system DejaVu Sans font. It is not a product screenshot or generated proof of audio quality. The full text equivalent is in lesson 12. No font files or external images are bundled. Retain the source script/provenance when distributing the diagram.

Reproduce these two assets without any database access:

```bash
.venv/bin/python scripts/prepare_media_module_4_assets.py
```

The script refuses different existing destination bytes instead of overwriting a teacher's change. It uses already installed Pillow, no new library or paid service. No local `espeak`, `espeak-ng`, `ffmpeg` or `sox` executable was found on PATH; no connected speech-generation tool was exposed. No voice was synthesized, cloned or imitated. No sine/noise placeholder is substituted for meaningful narration.

Both existing local examples are unassociated: no fake media/image rows are inserted. The diagram can later use the existing protected image upload and explicit section placement after approval. The manifest is an authoring plan, not a media registry.

## Existing media architecture and smallest follow-up

Current support:

- LessonImage + LessonImageDescription: private PNG/JPEG/WebP upload, alt text, protected authenticated image delivery and explicit image_placement metadata with captions/enlargement.
- AssignmentSubmission.file: protected download for student work, not teacher-authored lesson assets. Reusing it for course audio would create the wrong ownership/assessment semantics.
- Course lesson serializers do not expose audio or general attachments. There is no reusable lesson audio player or lesson SRT download route.
- The image endpoint accepts only registered lesson images, while the upload endpoint validates image decoders. WAV/SRT must not be smuggled into ImageField or its endpoint.

Proposed separate task (not implemented and no migration generated here):

1. Add one narrow lesson-attachment model with lesson FK, private FileField, kind/MIME, stable opaque identifier, order, caption, transcript/alternative text, provenance and content hash. Reuse LessonImage for actual images rather than duplicating image records. Schema review and a verified backup would precede an explicitly approved migration.
2. Store non-image teaching files under a protected `lessons/attachments/` path in the existing private storage. Register every served file; expose no storage URL. Reuse `can_access_lesson`, path confinement, ownership checks and private/no-store responses. Keep raw legacy `/media/lessons/` blocked. Validate actual content, size and allowlisted MIME before storage.
3. Add an owner/admin upload/import operation and authenticated ID-based download endpoint. SRT is UTF-8 text delivered as an attachment with `nosniff`; its mere presence does not mark any lesson complete. Missing/unauthorized files remain inaccessible.
4. For short bounded clips, generalize the cancellable authenticated blob-loader pattern into a separate typed loader while retaining the existing image MIME checks. Native `<audio controls preload="metadata">` can consume the authorized object URL, with no autoplay, visible transcript/caption, loading/error/retry states and URL cleanup on unmount/account change. Do not use a raw protected URL as an ordinary audio src when JWT headers are required. Larger streaming media needs reviewed authenticated Range handling rather than unbounded memory downloads.
5. Add a bounded media-placement type, parallel to image_placement, resolving only assets from the authorized lesson payload. SRT download is not a native caption track: browser timed tracks generally require WebVTT; an audio transcript should remain visible even without track support. No automatic SRT-to-track claim is made.
6. Test owner/enrolled/anonymous/other-course permissions, direct legacy URLs, traversal, MIME, failed loads, cleanup/session changes, keyboard playback, transcripts and download behavior before release.

This is an architectural proposal, not a working player or migration. It avoids weakening existing image/student-submission security and avoids a substantial media-system change inside a content-preparation task.

## Import commands and safety

Preview (also default):

```bash
.venv/bin/python manage.py import_media_module_4 --dry-run
```

After review and explicit approval:

```bash
.venv/bin/python manage.py import_media_module_4 --apply
```

Expected creation: one Module, three Lesson and three LessonLearningContent rows; local lesson orders 1–3. No media rows, image files, course updates, assessments or publication changes.

Apply reuses the existing verified SQLite online-backup helper, then repeats draft/prerequisite/conflict checks in an atomic transaction. It rejects occupied order/title, misplaced target titles, edited target content, extra rows/images/assessments; an exact unchanged replay is a no-op before backup. Use a quiet maintenance window; SQLite writer contention may require a checked retry. Original import receipts and earlier module metadata/images remain unchanged. Future modules can be appended independently; the old create-only importers are not curriculum reset tools.

## Validation

Focused tests cover exact content/three objectives, creation counts, replay, conflicts, preservation of prior modules including image-placement metadata, no graded assessments, rollback after partial writes, backup failure, slug lookup with a fixture course ID different from 10, prerequisites, SRT syntax/timing/content, local PNG validity and asset-manifest honesty. All test mutations use isolated Django/temporary databases and files.

The real development dry-run proposed one module, three lessons and three learning-content rows; zero updates, quizzes, assignments or media records. SQLite checksum remained unchanged. Pure Node verification with the existing presentation utility reconstructed all three lesson bodies exactly. No frontend implementation changed in this task; therefore frontend tests/lint/build and browser audits were not rerun. No new authorization implementation or broad audit required subagents.

No real --apply, settings/certificate edits, migration, publication, deployment, commit or push. Existing uncommitted Module 2–3/frontend/settings work preserved.
