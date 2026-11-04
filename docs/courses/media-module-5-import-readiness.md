# Module 5 — Phase 5C import readiness (2026-11-03)

## Restart verification

Branch `design/amethyst-motion`, checkpoint `5cf26f9`. Existing unpublished course
10 (`ai-media-content`) contains modules 34–37, orders 1–4, with lessons 100–111
(three per module). Module 5 and temporary QA course 11 are absent.
Read-only inventory confirmed nonempty lesson bodies and retained learning metadata.
No source, database, media, publication or account changes were made in Phase 5C.

## Create-only importer

`courses/management/commands/import_media_module_5.py` pins the Phase 5B source
SHA-256 `8e1003838194901cd780bd1ef61d0cd25ef2840a6e0845115d301c73734f3670`.
It requires exact course ID, slug/title, unpublished state, Russian settings,
existing authorized author and intact preceding curriculum. Pending publication
review, partial modules and changed content are rejected rather than overwritten.
It preserves all three objectives and nine ordered section anchors per lesson.
Matching repeated imports are no-ops, including after later media attachment.
An explicit apply uses the existing verified SQLite online-backup helper before
atomic creation and rechecks the target inside the transaction. No schema change.

## Actual dry-run

Run: `.venv/bin/python -B manage.py import_media_module_5 --dry-run`

| Curriculum position (not database ID) | Local order | Body characters | Objectives | Sections |
|---|---:|---:|---:|---:|
| 13 — Подготовка видеопроекта и организация материалов | 1 | 12813 | 3 | 9 |
| 14 — Монтаж, озвучка и интеллектуальные инструменты | 2 | 12652 | 3 | 9 |
| 15 — Экспорт, адаптация и подготовка видео к публикации | 3 | 12931 | 3 | 9 |

Would create **7 rows**: one module (order 5), three lessons and three learning-content
records. Zero course creation, updates, deletions, assessments, images, attachments
or publication requests. The course remains unpublished. Actual dry-run created
no backups and wrote no database or media files. New database IDs are allocated
only during a future explicitly authorized apply.

## Media and review boundaries

Nine MP4s and nine WebVTT tracks remain planned, not recorded/imported. Text can
be imported independently using stable source-section anchors. Existing protected
video delivery and authorized Studio upload already support MP4/WebVTT. The batch
`import_lesson_media` command still accepts image/audio/SRT only, with a 20 MiB
batch limit: extend its type validation and per-kind limits before using it for
recorded Module 5 videos. It is deliberately unchanged in this text-only phase.
Do not run the planned-assets manifest as an import or create placeholder rows.
Human CapCut version/OS, factual, narration, accessibility and rights review from
`media-module-5-content-review.md` remains pending. Source validation is structural,
not editorial approval or proof that videos exist.

## Git classification

Preserve existing uncommitted Phase 5A implementation (attachment models,
serializers, video delivery/validation, migrations 0006/0007, Studio upload,
React player, locales, tests and video documentation) and Phase 5B source,
storyboards, manifest, validator and review documentation. These are implementation
checkpoint candidates, not evidence of production deployment approval.

Keep intentional `config/settings.py` local edits out of any future checkpoint.
Also exclude SQLite/protected storage/backups, `.local-video-test`, Module 4
legacy ElevenLabs/eSpeak/RNNoise experiments and temporary candidate audio,
legacy generator/test artifacts and the stray filename beginning `e modules 2-4`.
No existing file was deleted, staged or committed during this phase.

## Next action

Review the text and pending human-review checklist first. After explicit approval:

```bash
.venv/bin/python -B manage.py import_media_module_5 --apply
```

The command creates and verifies a fresh SQLite backup under
`.local-course-backups/` before writing. Do not publish automatically. Record and
review the nine real demonstrations, then attach through Studio or a separately
tested batch importer extension. No apply or migration was executed in Phase 5C.
