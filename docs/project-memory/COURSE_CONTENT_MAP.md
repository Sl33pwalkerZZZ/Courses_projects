# Course Content Map

**Database snapshot:** read-only audit dated 2026-11-09. Do not treat counts as live/current without a separately authorized read-only check. Full lesson summaries and educational content are in [the detailed audit](../project-audit/02-course-content-and-database-audit.md).

## Snapshot inventory

The audit recorded **10 courses, 38 modules, 114 lessons**. Course 8 was the sole published course. Course 10 remained unpublished. Counts and publication status can change; do not mutate the database as part of a documentation refresh.

| Course ID | Slug / title | Modules / lessons | State and source note |
|---:|---|---:|---|
| 1 | `test_course` — Test_Course | 0 / 0 | Unpublished; canonical source/owner unknown. |
| 2 | `ai-fundamentals-work-study` — AI Fundamentals for Work & Study | 5 / 15 | Unpublished; seeded from `courses/management/demo_course_data.py`; published 15-question quiz on lesson 15 in audited snapshot. |
| 3 | `prompt-engineering-llms` — Prompt Engineering for LLMs | 5 / 15 | Unpublished; seeded demo curriculum. |
| 4 | `ai-research-knowledge-systems` — AI Research & Knowledge Systems | 5 / 15 | Unpublished; seeded demo curriculum. |
| 5 | `ai-automation-n8n` — AI Automation with n8n | 5 / 15 | Unpublished; seeded demo curriculum. |
| 6 | `ai-documents-office-work` — AI for Documents & Office Work | 5 / 15 | Unpublished; seeded demo curriculum. |
| 7 | `local-llms-private-ai` — Local LLMs & Private AI | 5 / 15 | Unpublished; seeded demo curriculum; one published quiz in audited snapshot. |
| 8 | `kak-vybrat-neyroset-pod-svoyu-zadachu` — Как выбрать нейросеть под свою задачу | 1 / 6 | Published; source DOCX, JSON importer, lesson 92 approved interaction data discrepancy documented in audit. Preserve content and progress. |
| 9 | `123` — 123 | 2 / 3 | Unpublished; placeholder-looking empty lesson content, ownership/intent unknown; preserve pending owner decision. |
| 10 | `ai-media-content` — ИИ для создания медиаконтента: от идеи до публикации | 5 / 15 | Unpublished/open enrollment in audit snapshot; primary active authoring focus. |

## Course 10 modules and lessons

The content audit mapped Course 10 as follows. Lesson IDs have a gap at 112; do not infer a missing Course 10 lesson from numeric IDs alone. A temporary technical QA fixture used an ID in that range and was reported removed; the audit snapshot has 15 Course 10 lessons.

| Module order / ID | Title | Ordered lesson IDs and titles |
|---|---|---|
| 1 / 34 | Основы ИИ в медиапроизводстве | 100 Как генеративный ИИ помогает создавать медиаконтент; 101 Бриф, промпт и выбор ИИ-инструмента; 102 Проверка фактов, права и прозрачность использования ИИ |
| 2 / 35 | Тексты и сценарии с помощью ИИ | 103 Поиск идей и подготовка медиабрифа; 104 Создание сценариев с помощью ИИ; 105 Адаптация медиаконтента для разных площадок |
| 3 / 36 | Создание изображений и графики с помощью ИИ | 106 Генерация изображений с помощью ИИ; 107 Создание обложек, карточек и инфографики; 108 Единый визуальный стиль медиапроекта |
| 4 / 37 | Создание и обработка аудио с помощью ИИ | 109 Генерация речи и озвучка медиаматериалов; 110 Распознавание речи и создание субтитров; 111 Обработка звука и подготовка аудио для монтажа |
| 5 / 39 | Создание и монтаж видео в CapCut Desktop | 113 Подготовка видеопроекта и организация материалов; 114 Монтаж, озвучка и интеллектуальные инструменты; 115 Экспорт, адаптация и подготовка видео к публикации |

Each Course 10 lesson had three objectives and nine structured sections in the audit snapshot. Module 3 lessons 106–108 had six inline images total; Module 4 had seven production media records; lessons 113 and 114 had video integrations; lesson 115 had no media. Course 10 had no quiz, assignment or certificate policy in that snapshot. Graded assessment was intended for Module 6, but Module 6 is not yet defined.

## Canonical source-of-truth map

- Course 8: `courses/management/first_course_content.json`, `course_sources/Глава_1_Выбор_ИИ_модели_и_сервиса.docx`, `courses/management/commands/import_first_course.py`, plus narrowly approved update proposals where documented. Its Lesson 92 database interaction differs from the base JSON; do not reimport the course to reconcile it.
- Course 10 Module 1: `course_sources/media_module_1.docx`, `courses/management/commands/import_media_module.py` and the import receipt.
- Course 10 Modules 2–5: `courses/management/media_module_2.json` through `media_module_5.json`, matching module import commands. Lesson 113/114 canonical text had been synchronized according to the audit.
- Module 3 assets: `docs/courses/media-module-3-assets.json`, six files under `course_assets/module_3/`, and `import_media_module_3_images.py` / `place_media_module_3_images.py`. The manifest status was stale in the audit and needs an approved metadata correction.
- Module 4 assets: `docs/courses/media-module-4-assets.json`, `courses/management/media_module_4.json`, provenance/license documents and import/finalization commands. See media audit; old planning docs are historical.
- Module 5 video: `docs/courses/media-module-5-assets.json`, storyboards and dated integration reports. The working-tree manifest and code are modified; inspect `git diff` before treating them as committed truth.
- Courses 1 and 9: source/owner intent unknown. Do not delete or rewrite based on test-looking names.

## Content rules

Treat source DOCX/approved JSON plus explicit update records as canonical according to each course's import workflow. Importers are not general-purpose overwrite tools; inspect their conflict/fingerprint checks. Keep Course 10 unpublished unless the owner explicitly authorizes publication. Do not add graded assessments to Modules 1–5; Module 6 requirements are still an author decision.
