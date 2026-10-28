# Protected lesson audio and subtitle attachments

## Implemented

- One additive `LessonAttachment` model for authored MP3, PCM WAV and UTF-8 SRT; reuses the existing private FileField storage under `lessons/attachments/`. It does not reuse or change student submission records.
- Captions, descriptive labels, transcript/equivalent, provenance and `after_section` anchor are recorded on each attachment. No hardcoded lesson IDs, filenames or course logic exist in the renderer.
- Metadata is returned only in protected lesson/owner-scoped Studio responses. File delivery reuses existing `can_access_lesson` rules, JWT/session authentication, path confinement, private/no-store, Vary and nosniff. Owner/admin draft previews and enrolled students work; students without enrollment and unrelated authors are denied.
- Raw `/media/lessons/…` remains blocked. The legacy private filename route remains registered-image-only, so it cannot expose attachment files.
- Audio is fetched with the existing authenticated API client as a bounded blob, then played through native `<audio controls>` without autoplay. No JWT is put in a URL. Captions and visible transcripts accompany the player.
- SRT is fetched only on explicit download, uses the same authenticated loader, is delivered as an attachment, and is not misrepresented as a native browser subtitle track. SRT and WebVTT are different formats.
- Exact anchors place attachments after the relevant section, with subsequent text continuing. Unknown/absent anchors and unsupported layouts retain a separate materials-block fallback. Each attachment appears once. Existing inline images and image gallery fallback remain intact.
- Client requests abort and object URLs are revoked on replacement/unmount/session changes. Obsolete session responses cannot populate the new view. A prior SRT click is not automatically replayed for another account or attachment.
- Native controls inherit global light/dark colour scheme. New labels/forms support RU/KK/EN. Transcripts remain visible without playback; controls/captions are responsive and keyboard-accessible.
- Instructor Studio curriculum now provides an “Audio and materials” upload form with label, caption, transcript/equivalent, provenance and section selection. It retains existing draft locks and owner/admin boundaries. No deletion or replacement workflow was added.

## API

| Endpoint | Purpose |
| --- | --- |
| `GET /api/lessons/{id}/` | Existing authorized lesson response now includes `attachments` |
| `GET /api/studio/lessons/{id}/attachments/` | Owner/admin metadata list |
| `POST /api/studio/lessons/{id}/attachments/` | Owner/admin draft upload (`file`, `label`, `caption`, `transcript`, `provenance`, `after_section`) |
| `GET /api/lesson-attachments/{id}/` | Authorized audio bytes or forced SRT download |

MP3/WAV max 20 MB; SRT max 1 MB. File extensions alone are insufficient: WAV requires valid PCM structure and complete frames, MP3 requires complete supported Layer III frame boundaries, and SRT requires UTF-8, numbered cues, valid timestamps and ordered positive nonoverlapping intervals. Empty, unsupported, malformed and oversized files fail before storage. Structural MP3 validation is not a codec quality test or proof of intelligible/consented narration; free-format or otherwise unsupported MP3 variants are rejected safely.

Uploads require a label and provenance; audio also requires a transcript or meaningful textual equivalent. Anchors, when supplied, must uniquely match lesson headings. Exact repeated bytes/metadata return the existing asset; conflicting bytes/filenames/metadata are not overwritten. Same-lesson digest uniqueness also protects duplicate records. Failed transactions remove only newly written files. An identical upload does not invalidate previous editorial acknowledgement; actual additions invalidate the publication fingerprint/acknowledgement.

Publication fingerprints include attachment metadata/digests only where assets exist, preserving earlier fingerprints of empty-attachment lessons. No existing publication row or certificate policy is rewritten.

## Pending migration and compatibility

`courses/migrations/0005_lessonattachment.py` creates only the attachment table, lesson FK and uniqueness constraint. It contains no data update, delete or rewrite. It has been exercised in isolated test databases, **not applied to the development database**.

Before activation, existing lesson/Studio responses safely return `attachments: []` when the table is absent. New file/upload operations return an explicit 503. This is a deliberate temporary compatibility gate with no permanent schema cache, so applying the migration takes effect without stale readiness state. Unrelated public course browsing and existing images do not depend on the table.

## Exact activation sequence — user approval required

Do not execute these automatically. From the repository root:

```bash
# Create and verify a separate private SQLite backup; prints its exact path.
.venv/bin/python manage.py shell -c 'from django.conf import settings; from courses.management.commands.import_media_module import create_backup; print(create_backup(settings.DATABASES["default"]["NAME"], settings.BASE_DIR / ".local-course-backups"))'

# Review the plan: only courses.0005 is currently pending.
.venv/bin/python manage.py migrate --plan

# Apply the reviewed additive migration only after approval.
.venv/bin/python manage.py migrate courses 0005_lessonattachment

# Preview the existing local Module 4 materials.
.venv/bin/python manage.py import_lesson_media --dry-run

# Import only after approval; this also makes a fresh verified backup.
.venv/bin/python manage.py import_lesson_media --apply
```

Use a quiet maintenance window for backup/import. SQLite concurrent writes can cause a lock error; retry only after checking state. The importer checks conflicts before backup and repeats them inside an atomic transaction, tracking files for rollback cleanup.

No settings changes or new packages are needed. Reload/restart existing development processes if they do not pick up the code. In Studio, open the existing course curriculum and the corresponding lesson, then use “Audio and materials”; preview via the existing lesson preview link without publishing the course.

## Module 4 manifest import

`docs/courses/media-module-4-assets.json` gains only `kind` and `label_ru` per entry, plus a corrected setup note. Existing anchors/captions/alternatives/provenance are reused. The generic importer accepts `--manifest`, `--assets-dir` and `--backup-dir` for future courses. Add one ready/approved manifest entry per actual file. Unapproved/pending entries are skipped, not turned into placeholder records; missing ready files are errors.

Current plan:

| Local file | Existing lesson discovered by slug/module/order | Result after approved import |
| --- | --- | --- |
| `m4-l2-f1-example.srt` | 110, section “5. SRT: простой текстовый формат” | Protected inline-labelled download; illustrative timing warning retained |
| `m4-l3-audio-workflow.png` | 111, section “6. Полный рабочий процесс Ф1” | Existing protected-image record + captioned `image_placement` metadata |

The import does not change theory, learning objectives, earlier images, student progress, quizzes, assignments, certificates or publication status. Exact repeats are no-ops. New image placement uses the existing JSON contract; audio/SRT placement is stored on the attachment. No dummy audio is created. Synthetic narration, speech/transcript and before/after processing files still need genuine authorized production/review. Once approved files exist, instructors may upload MP3/WAV through the same generic Studio form and assign a section.

The old Module 4 content importer is create-only, not a reset mechanism: it may intentionally report a conflict after later image/metadata additions. Do not use it to overwrite the curriculum.

## Tests, review and limitations

- Focused attachment/API tests: permissions for anonymous/pending/rejected/enrolled/owner/admin/other author; metadata/file secrecy; legacy and traversal protection; MP3/WAV/SRT validation; upload duplicates/conflicts/cleanup; pre-migration behavior; publication fingerprint changes.
- Manifest tests: dry-run, real isolated import of SRT+PNG, idempotency, conflicts, anchor rejection, atomic rollback/file cleanup and migration gate.
- Frontend tests: native audio semantics/transcript/caption, SRT download behavior, typed blob loading/cancellation/revocation, stale responses, errors, inline placement and fallback; full existing rendering regressions.
- Native security reviewer ran read-only and found no remaining blocking issue. Its repeat-upload editorial-flag finding was fixed and tested.
- Native browser reviewer attempted Playwright Firefox, but the MCP tool disconnected before execution. No Firefox session, screenshots, console/network observations or actual playback/seek/keyboard/download/layout claims can be made. Automated markup/loader checks passed; real desktop/mobile verification remains pending a connected browser.
- There is no real Module 4 audio yet. Test WAV/MP3 fixtures are structural test data, not course narration. Actual audio quality and permissions require human review.
- Short clips are fully downloaded before native playback; seeking uses local blob data. Authenticated HTTP Range streaming for large media is outside this bounded implementation.

No real migration/import, publication, deployment, commit or push. Existing settings and earlier uncommitted work were preserved.
