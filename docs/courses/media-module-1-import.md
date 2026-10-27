# Media course Module 1 — import review

Prepared 2026-10-27. Not applied to development SQLite.

## Commands

Preview (also the default when neither mode is specified):

```bash
.venv/bin/python manage.py import_media_module --author-username almas --dry-run
```

After reviewing and approving the preview:

```bash
.venv/bin/python manage.py import_media_module --author-username almas --apply
```

The apply command creates a uniquely named, mode-0600 SQLite backup in the existing ignored `.local-course-backups/` directory and checks SQLite integrity and foreign keys before creating anything. It prints the backup location. No backup is created during preview. A failed import rolls back all new rows. Re-running an unchanged import is a no-op; changed source or curriculum is rejected, never overwritten. Use a quiet maintenance window for the backup/import.

## Exact proposal

- Course: ИИ для создания медиаконтента: от идеи до публикации
- Slug: `ai-media-content`
- Existing owner: `almas`, ID 1 (authorized through superuser status; account unchanged)
- Existing category: AI Foundations (`ai-foundations`)
- Russian, beginner, open enrollment, unpublished draft
- Module 1: Основы ИИ в медиапроизводстве
- Ordered lessons:
  1. Как генеративный ИИ помогает создавать медиаконтент — 3384 body characters
  2. Бриф, промпт и выбор ИИ-инструмента — 3765 body characters
  3. Проверка фактов, права и прозрачность использования ИИ — 5480 body characters
- Each lesson has three source objectives.
- Creates 1 Course, 1 Module, 3 Lesson, 3 LessonLearningContent, 1 CourseSettings and 1 CourseImport. Zero updates.
- No Assignment, Quiz, publication, certificate or student records created/changed.

## Source mapping and presentation

Source: `course_sources/media_module_1.docx`
SHA-256: `2c263201dabc9975c044761ff762247350e726c616bbae1c03407841f6a69e81`.

The bounded existing Studio DOCX parser preserves real text and hyperlink targets. Exact lesson headings define the three boundaries; no factual prose is generated. Objectives go in LessonLearningContent; remaining prose goes in Lesson.text_content. Four tables are expanded into labelled row paragraphs at their original positions because the current SourceParagraph renderer handles text/URLs, not Markdown tables. Every table heading/cell, example, practical instruction and rubric entry is preserved. No React changes needed.

Module outcome and timing become the course description. Cover title/language/level and draft-status metadata are represented by the course configuration instead of repeated in lesson prose. All three original reference URLs are retained; no replacement or fabricated sources. External claims/links have not been independently fact-checked, so source review remains unapproved.

The source's mini-task, prompt practice and media-project passport are instructional content only. The suggested 7/10 rubric is preserved as text; no new grading system or automatic completion evidence is implied. The source distinguishes this practice from a future final course assessment. No final quiz is supplied or invented. Existing Studio publication validation will still require an assessment and explicit review before publishing. Detailed future CapCut instruction is outside this module.

## Validation

Nine focused importer/backup tests cover creation and all source paragraphs/cells, dry-run, unchanged replay, conflicts, existing-content protection, unauthorized author, source mismatch, rollback and backup failure/private backup integrity. Tests use isolated Django and temporary SQLite databases; backup call is mocked only in in-memory importer tests, with a separate real temporary-file backup test.

Native `security_reviewer` completed a read-only review: no blocking findings. No real student session or browser rendering was tested; compatibility is based on the existing text/link renderer and source-content preservation checks.

No migration, real import, account change, publication or issuance was performed. The pre-existing `config/settings.py` modification was preserved.
