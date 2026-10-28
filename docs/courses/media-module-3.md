# Module 3 — Russian teaching draft and visual production plan

Course: existing unpublished course 10 / `ai-media-content`.
Module order 3: **Создание изображений и графики с помощью ИИ**.
No development database changes applied by this task.

## Lesson structure

| Course sequence | Title | Local order | Objectives | Body characters |
| --- | --- | --- | --- | --- |
| 7 | Генерация изображений с помощью ИИ | 1 | 3 | 9024 |
| 8 | Создание обложек, карточек и инфографики | 2 | 3 | 7919 |
| 9 | Единый визуальный стиль медиапроекта | 3 | 3 | 9238 |

Lesson 7: image-generation concepts and limits, object/composition/light/style/aspect-ratio parameters, weak versus improved prompts, a second adaptation prompt, evaluation and responsible use.

Lesson 8: cover/card/infographic purposes, hierarchy, typography, contrast, separate prompts for image foundations and accurate written layouts, process diagrams without invented data, readability checks.

Lesson 9: colour and type roles, grids, a style-guide example, two prompts for consistent production and checking descriptions, file versions/provenance, preparation and inspection of graphics for CapCut Desktop.

Each lesson contains substantial explanations, definitions, a sequential working method, examples, mistakes and corrections, takeaways and one explicitly optional ungraded exercise. Full editable Russian content is in `courses/management/media_module_3.json`. No external source document or factual authority is claimed for this newly authored draft.

All lessons use the explicitly fictional Ф1 paper-reuse project from Module 2. Sample descriptions/outputs are teaching examples, not actual generated image files or real research findings. No fabricated citations, statistics or product screenshots are included. Tool features and import formats are to be checked in the instructor's installed version; no unsupported UI walkthrough is presented.

No quiz, graded assignment, submission requirement, rubric, passing threshold or certificate change is created. Graded assessment remains reserved for Module 6. Existing Modules 1–2 are not edited.

## Visual manifest — not finished assets

Detailed machine-readable briefs are in `docs/courses/media-module-3-assets.json`. **All six PNG assets await creation and instructor approval.** No remote URL, stock placeholder or manifest entry is treated as a finished asset.

| Lesson | Suggested file | Learning function |
| --- | --- | --- |
| 7 | `m3-l1-prompt-anatomy.png` | Connect five prompt parameters with composition decisions |
| 7 | `m3-l1-prompt-comparison.png` | Compare unclear and brief-driven original layouts |
| 8 | `m3-l2-layout-hierarchy.png` | Compare information hierarchy while keeping facts identical |
| 8 | `m3-l2-process-infographic.png` | Show a process without inventing numeric evidence |
| 9 | `m3-l3-style-guide.png` | Demonstrate reusable colour/type/layout roles |
| 9 | `m3-l3-export-check.png` | Show reframing and export checks without faking product UI |

Each brief includes lesson title/local order, purpose, exact depiction, recommended 1600×900 PNG format, Russian caption, informative alt text, creation status, provenance and licence requirements. These are original instructor-diagram briefs; no third-party artwork needs to be downloaded. If a creator introduces external materials or fonts, record rights and permitted course use first. Original project files, creator, date and approval should accompany final exports.

The content is readable without missing diagrams: it never claims a planned asset is already on screen. The module's visual-learning production is not complete until these assets are created, checked for readability at mobile size and approved.

## Existing image architecture and later upload

- `LessonImage` uses private `lessons/` storage; `LessonImageDescription` supplies language-specific alt text and decorative status.
- Instructor Studio `POST /api/studio/lessons/{lesson_id}/images/` checks owning-author/admin permission and draft editability. It accepts validated PNG/JPEG/WebP up to 5 MB and 16 million pixels, re-encodes to PNG and requires alt text for informative images.
- Lesson serializers return protected API URLs, not storage URLs. `LessonImageView` uses the same lesson-access rule as lesson content, with private/no-store responses. Public legacy `/media/lessons/` access is blocked.
- React `ProtectedLessonImage` fetches with the authenticated API client and renders object URLs with alt text, retry and cleanup. No public static paths are needed.
- Images currently appear in the lesson image area after the main material; this task adds no inline-asset framework. There is no dedicated caption field or visible figure caption in the existing image component. Captions in this manifest are authoring briefs, not silently stored as alt text or falsely claimed to be visible. Caption/placement integration can be reviewed when the real assets are supplied.

After the module import is separately approved, find the actual new lesson IDs through Instructor Studio; map by module and local lesson order, not guessed IDs. Once diagrams and rights are approved, use the existing Studio upload form with Russian descriptions and `decorative=false`. No automatic image import is enabled in this command because no approved files are supplied. Do not place them in public static assets or alter protected-media security.

## Safe command

Preview (also the default):

```bash
.venv/bin/python manage.py import_media_module_3 --dry-run
```

Only after explicit approval:

```bash
.venv/bin/python manage.py import_media_module_3 --apply
```

Expected creation: 1 Module, 3 Lesson and 3 LessonLearningContent rows. Local lesson orders are 1–3; IDs are assigned only when applied. Zero existing-record updates, quizzes, assignments or images.

The command reuses the existing SQLite online-backup helper: unique private backup in ignored `.local-course-backups/`, integrity and foreign-key checks before any insert, exact backup path printed. Default preview creates neither backups nor rows. All inserts are atomic, with target/conflict checks repeated inside the transaction. Use a quiet maintenance window; concurrent SQLite writers can cause a lock error, in which case the transaction must be retried after checking state.

Existing course 10 must retain its slug, Russian settings, unpublished status and Modules 1–2. Pending publication blocks extension. Conflicting module order/title, target lessons elsewhere, altered lesson bodies/metadata, extra lessons, images or assessments stop the command instead of overwriting. An unchanged replay is a no-op before backup. After educators add images or edit the new material, a replay intentionally reports a conflict and does not undo their work.

No course, user, certificate, policy, student record, import receipt or publication record is saved. The original Module 1 whole-course fingerprint is not rewritten; its old create-only importer is not an update mechanism for the extended course. Future modules may be appended without changing this command's exact Module 3 checks.

## Validation and boundaries

- 32 relevant Django tests passed (Module 3, Module 2 and Module 1 import suites).
- Tests cover exact creation/content/objectives, no-op replay, protection of prior modules/other courses, conflicting content, partial-write rollback, backup failure, draft prerequisite recheck, no graded assessments or images, and complete manifest coverage. Existing backup tests use temporary SQLite files; all import mutations use isolated Django test databases.
- `manage.py check`: passed.
- Real SQLite dry-run: planned 1 module / 3 lessons / 3 learning-content rows, zero updates. File checksum unchanged across preview.
- Existing presentation utility: all three bodies reconstruct exactly, with nine metadata headings each. No frontend implementation changes were required, so no frontend test/build or browser review was run.
- No new permissions or media-serving code was introduced; no additional review agent was invoked.
- Text and visual briefs still require instructor/editorial review. All six visual assets remain uncreated and unapproved.

No real `--apply`, migrations, publication, deployment, commit or push performed. Existing settings and Module 2 working-tree files preserved.
