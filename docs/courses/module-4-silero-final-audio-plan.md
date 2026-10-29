# Module 4: finalized Silero audio and editorial checkpoint

The author-approved seven protected materials are finalized. Course publication
status, Modules 1–3, other courses and student records are unchanged.

## Production assets

All files are in `course_assets/module_4/`:

| Lesson | File | Details |
| --- | --- | --- |
| 10 | m4-l10-silero-ru-roman-approved.wav | Approved Variant B, 19.2625 seconds |
| 11 | m4-l11-silero-ru-roman-approved.wav | Approved speech, 8.5625 seconds |
| 11 | m4-l2-f1-example.srt | Illustrative timing; not synchronized |
| 11 | m4-l11-silero-ru-roman-synchronized.srt | Actual speech-segment timing |
| 12 | m4-l12-silero-ru-roman-before.wav | Approved realistic synthetic room background, 8.5625 seconds |
| 12 | m4-l12-silero-ru-roman-after-dsp.wav | Approved strong V3 conventional DSP, 8.5625 seconds |
| 12 | m4-l3-audio-workflow.png | Original workflow diagram |

All WAVs are mono signed 16-bit PCM, 24000 Hz. They preserve the approved source
bytes exactly, without normalization, resampling or new filtering. SHA-256,
durations, original selection labels, cue offsets and processing parameters are
recorded in `module-4-final-provenance.json` and `media-module-4-assets.json`.
The latter contains no machine-specific attachment IDs or private storage paths.

Silero model: `v5_cis_base_nostress`, voice `ru_roman`. Official checkpoint:
https://models.silero.ai/models/tts/ru/v5_cis_base_nostress.pt

Checkpoint SHA-256:
`0405777e332906f0644e08a680f7cfdc2137ea864090079c1fdd30a43c1b8761`.
The CIS Base MIT exception is documented at
https://github.com/snakers4/silero-models#v5-cis-base-models
and https://github.com/snakers4/silero-models/blob/master/LICENSE_CIS .
The full notice is committed as `course_assets/module_4/LICENSE_CIS` and retained
in the attachment provenance. No ElevenLabs/eSpeak recordings, neural denoising
models, student data or third-party sound recordings are needed for this checkpoint.

## Editorial review

The eight exact wording corrections and two caption corrections are recorded in
`module-4-editorial-corrections.json`:

- Lesson 10 distinguishes the written F1 exercise from the separate attached
  university-media narration, without replacing either script.
- Lesson 11 no longer claims its audio is unavailable and clearly distinguishes
  the illustrative SRT from the synchronized download. The fabricated STT error
  remains explicitly illustrative, not a claim about a real service.
- Lesson 12 acknowledges the existing synthetic-noise demonstration and describes
  its processing as conventional DSP, not AI.
- Synchronized-SRT and filtered-audio captions omit obsolete eSpeak/version notes.

Section headings, order, objectives, learning interactions, IDs and attachment
bytes are preserved. The fresh-import content JSON includes the same corrected
wording. Existing installations can preview and apply the guarded update:

```sh
.venv/bin/python manage.py correct_module4_editorial --dry-run
.venv/bin/python manage.py correct_module4_editorial --apply
```

Apply takes a SQLite write reservation, rechecks exact before/after strings,
creates and verifies a SQLite backup, and updates only the three target lesson
text fields and two captions in one transaction. Unknown content fails closed;
repeated execution is a no-op. No schema migration is required.

The live corrections were applied after verified backup
`.local-course-backups/media-module-before-2b0e8af88806493e96261bcd2ca70a0e.sqlite3`.
Backups and local replacement baselines are never committed.

## Import and replacement

After the existing Module 4 curriculum import, an empty target can use the final
source assets directly:

```sh
.venv/bin/python manage.py import_lesson_media --dry-run
.venv/bin/python manage.py import_lesson_media --apply
```

The create-only command rejects replacement of existing Module 4 attachments.
For an already-finalized installation:

```sh
.venv/bin/python manage.py finalize_module4_media --dry-run
```

The current live result is **KEEP 7**, CREATE/REPLACE/SKIP 0. IDs, URLs and inline
section placements remain stable. The finalizer verifies actual protected bytes.

For a legacy installation, first review an exact private JSON baseline mapping
asset keys to previous row snapshots (`snapshot()` in the finalizer). Stop other
writers and media edits, then preview with an explicit local baseline:

```sh
.venv/bin/python manage.py finalize_module4_media --baseline /private/path/baseline.json --dry-run
```

Only after approval, use the same command with `--apply`. The baseline is specific
to that installation and must not be copied from another database or committed.
Unexpected old rows, duplicate/extra records, changed metadata or missing files
fail closed. The standalone SQLite transaction takes `BEGIN IMMEDIATE`, backs up
SQLite and all seven old media files with verified hashes, writes new private UUID
paths and updates existing attachment rows atomically. Old files remain intact;
repeated application is KEEP without extra files or backups.

Backup bundles under `.local-course-backups/module4-media-<uuid>/` contain verified
SQLite, media copies and a before/after journal with restrictive permissions.
Runtime failure rolls back rows and removes only newly created files. Post-commit
rollback must restore the coherent SQLite/media checkpoint during maintenance;
never restore a full snapshot over later student activity. With intervening writes,
a separately reviewed guarded row-level rollback is required.

## Validation and reproduction

```sh
.venv/bin/python manage.py check
.venv/bin/python manage.py test courses.test_module4_editorial courses.test_final_module4_assets courses.test_finalize_module4_media courses.test_lesson_media_import courses.test_media_module_4 courses.test_attachments courses.test_media_image_placements
.venv/bin/python scripts/reproduce_module4_audio.py
```

The last command is inspection-only by default: it checks the seven committed
assets and generates nothing. Tests use isolated databases and private storage;
no candidate audio, legacy recordings or evaluation metadata is required.
Coverage includes exact editorial/idempotent updates, backup failure, unknown
content rejection, media hashes/types, SRT sample boundaries, role-protected file
access, replacement idempotency, duplicate rejection and rollback.

Optional future exact regeneration is implemented in
`scripts/reproduce_module4_audio.py --reproduce --checkpoint <verified-checkpoint> --output-dir <new-directory>`.
It needs an isolated CPU PyTorch 2.15.0 environment, never Django's environment.
The model is not downloaded automatically. It reproduces the approved synthesis
sequence, seeded room noise and strong DSP parameters, refuses existing output,
and checks all golden hashes before writing. If runtime differences prevent
byte-identical reproduction, it stops; the committed approved recordings remain
the source of truth. Regeneration was not run for this Git checkpoint.

Protected-browser inspection had no authorized session. Rendered-source review
confirmed `MediaLessonReading` renders the corrected paragraphs and attachment
captions after the same section anchors. No frontend code or public course
visibility was changed.

Temporary candidates and historical experimental reports remain local only.
No deployment or course publication is part of this checkpoint.
