# Media course Module 2 — authored draft and safe import

Prepared 2026-10-28. Development SQLite has **not** been changed by this task.

## Educational structure

Existing course 10 / `ai-media-content`, unpublished draft. New module order 2: **Тексты и сценарии с помощью ИИ**.

| Course sequence | Lesson title | Local order | Objectives | Body characters |
| --- | --- | --- | --- | --- |
| 4 | Поиск идей и подготовка медиабрифа | 1 | 3 | 8453 |
| 5 | Создание сценариев с помощью ИИ | 2 | 3 | 9216 |
| 6 | Адаптация медиаконтента для разных площадок | 3 | 3 | 9887 |

The LMS orders lessons within their module, so local orders are 1–3, following Module 1. Database IDs are allocated only if the command is explicitly applied.

Lesson 4 develops audience, purpose, idea selection, factual boundaries and the working brief. Includes weak/strong brief comparisons, a complete reusable prompt, an illustrative response, mistakes and an optional exercise.

Lesson 5 explains script structure, 60–90-second planning, iterative revision, narration and storyboarding. Includes an initial and improved prompt, a worked 75-second outline, a follow-up editing prompt, factual/attribution checks and an optional exercise. Timings are planning intervals, not guaranteed spoken durations.

Lesson 6 compares long/short/video/text contexts, audience, hooks, pacing and tone. Includes three versions of one story for YouTube, Reels and TikTok, packaging examples, a full adaptation prompt and a sample response, mistakes and an optional exercise. Chosen durations are educational editorial choices, not platform limits or promises of distribution.

All examples share **Ф1**, an explicitly fictional student paper-reuse project. No real research outcomes, numbers, quotes, organizations or references are invented. These are newly authored teaching drafts; no Module 2 source DOCX or external authority is claimed. Teacher/editorial review is still needed before publication.

## Storage and presentation

`courses/management/media_module_2.json` contains the full Russian text and objectives for review. The command writes only Module, Lesson and LessonLearningContent records. Heading metadata exactly matches the body paragraphs; the existing renderer restores labelled-row tables in place and styles definitions, prompts and warnings. No React changes, ID-specific presentation rules or duplicate content are added.

No quizzes, graded assignments, submission forms, rubrics, thresholds or certificate policy changes are created. Optional exercises explicitly require no submission or assessment. The course plan places all graded assessments in Module 6. Existing Module 1 content (including its historical explanatory rubric) is intentionally untouched; reconciling that text with the revised course plan would require a separately approved content edit.

## Preview and approved execution

Default is dry-run:

```bash
.venv/bin/python manage.py import_media_module_2 --dry-run
```

After explicit approval, from the repository root:

```bash
.venv/bin/python manage.py import_media_module_2 --apply
```

Before creation the existing SQLite backup helper creates a private unique copy under the ignored `.local-course-backups/` directory and validates integrity and foreign keys. A backup failure stops the import. The command prints its exact location. Use a quiet maintenance window when applying.

Creation is transactional, with target/conflict checks both before backup and inside the transaction. SQLite serializes writes; simultaneous contending writers may receive a lock error and should rerun after checking state. No partially created module is committed on failure.

The target must remain course 10 with the correct slug, Russian settings, existing Module 1 and unpublished status. A pending publication request prevents extension until resolved. Existing modules occupying order 2, mismatched target content, additional target lessons, assessments/images or target lesson titles elsewhere are conflicts. They are never overwritten. Exact unchanged replays are no-ops and create neither new rows nor backups.

The command never updates the course or its original Module 1 CourseImport receipt. The original Module 1 command checks the full original curriculum fingerprint and is expected to reject the extended course after Module 2 exists; do not use it to update or reimport this course. The dedicated Module 2 command checks only its own target content.

## Validation

- 19 Django tests passed: Module 2 creation/content/order, idempotency, no assessments, existing-course preservation, partial-write rollback, backup failure, course/target conflicts, teacher edits, transaction recheck; existing Module 1 tests include the real temporary-file verified-backup test.
- `manage.py check`: passed.
- Real SQLite dry-run: creates 1 module, 3 lessons, 3 learning-content rows; 0 updates. Database checksum unchanged.
- Pure Node check using the existing presentation utility: exact reconstruction of all three lesson bodies; semantic sections and labelled-row tables recognized without React changes.
- No frontend files changed, so frontend test/lint/build and browser agents were not run for this task. No browser or authenticated preview claim is made.
- No subagents were needed: no new authorization paths or frontend implementation were introduced. The requested primary-model switch cannot be selected within this runtime.

No migrations, real import, publication, assessment, certificate issuance, commit or push performed. Existing `config/settings.py` changes preserved.
