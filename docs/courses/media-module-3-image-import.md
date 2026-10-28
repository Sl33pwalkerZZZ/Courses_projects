# Module 3 protected-image attachment

Prepared command, not applied to development SQLite.

```bash
# Default also previews only:
.venv/bin/python manage.py import_media_module_3_images --dry-run

# Run only after approval:
.venv/bin/python manage.py import_media_module_3_images --apply
```

Defaults: `course_assets/module_3/` and `docs/courses/media-module-3-assets.json`. Optional `--assets-dir`, `--manifest`, `--backup-dir` accept explicit local paths. The old planning status in the manifest is descriptive; actual PNG files are validated, not assumed from that status.

Lookup is by course slug `ai-media-content`, module order 3 and lesson orders 1–3. Module/lesson titles are cross-checked against the manifest; lesson IDs are never hardcoded. The course must be unpublished with no pending publication request.

| Lesson order | Title | Gallery files, in order |
| --- | --- | --- |
| 1 | Генерация изображений с помощью ИИ | `m3-l1-prompt-anatomy.png`, `m3-l1-prompt-comparison.png` |
| 2 | Создание обложек, карточек и инфографики | `m3-l2-layout-hierarchy.png`, `m3-l2-process-infographic.png` |
| 3 | Единый визуальный стиль медиапроекта | `m3-l3-style-guide.png`, `m3-l3-export-check.png` |

Each source must be a real single-frame PNG, up to 5 MB and 16 million pixels. Unsafe paths, escaping symlinks, duplicate filenames and invalid informative alt text are rejected. Files are fully decoded and re-encoded like the existing Studio upload path; original source PNGs remain unchanged.

The command uses the existing LessonImage FileField storage under `lessons/ai-media-content/module-3/`, preserving basenames. It creates six LessonImage and six LessonImageDescription records on a fresh apply, with `decorative=False` and exact manifest alt text. Existing authentication, enrollment/preview permission checks and protected blob loading remain unchanged. No public static image URLs or new storage mechanism are introduced.

**Captions/placement limitation:** neither LessonImage nor LessonImageDescription has a caption or inline-placement field. The existing gallery shows images after lesson material. The command retains Russian captions as PNG `Description` iTXt metadata and in the manifest/preview; it does not claim these are visible captions, alter lesson text or overload alt text. Visible captions/inline figures would require a separately scoped frontend/API/schema solution.

Apply creates/verifies a private SQLite backup before mutations, using the existing helper. It then repeats conflict checks and creates rows transactionally. Failed imports remove only the new storage files created by that attempt; sources and pre-existing attachments remain intact. Exact existing paths, bytes, lesson association, order and descriptions produce a no-op. Conflicting or unregistered destination files, other gallery images or duplicate records stop execution. Partial matching attachments are preserved, and only missing ones are added. Run during a quiet maintenance window; concurrent SQLite writers can fail with a lock error and should retry only after checking state.

No lessons, learning content, previous modules, accounts, student records, quizzes, certificates or publication state are updated. There are no migrations or frontend changes.

Validation: 12 isolated attachment tests; system check passed. Development dry-run validated all six local 1600×900 PNGs and proposed six attachments to discovered lessons 106–108. SQLite checksum stayed unchanged. No actual attachment/apply, commit, push or deployment occurred. The pre-existing Module 3 content importer intentionally rejects post-import gallery edits rather than removing these attachments; use this dedicated image command for safe replay.
