# AI Courses — Project Overview

**Knowledge-base verification date:** 2026-11-09
**Evidence basis:** repository source and the dated audits linked below. The database figures refer to the read-only snapshot recorded in the course audit, not a fresh query.

AI Courses is an existing educational platform for publishing courses, teaching lessons, tracking learning, and managing course delivery. Students browse published courses, request or begin enrollment according to course policy, study protected lessons and media, complete optional quizzes or assignments, and view progress or certificates when configured. Authors manage their own courses through Instructor Studio; administrators handle privileged publication, enrollment, role and certificate workflows.

The platform combines a Django REST Framework backend with a React/Vite browser application. SQLite is the configured local database. The application supports JWT sessions, role- and ownership-based authorization, enrollment approval, protected instructional content, lesson completion, quizzes, teacher-reviewed submissions, course reviews, certificates, RU/KK/EN localization, light/dark themes, and responsive interfaces. See [ARCHITECTURE.md](ARCHITECTURE.md) and [FEATURE_FILE_MAP.md](FEATURE_FILE_MAP.md) for implementation locations.

Course content is stored in Django records and, for authored/imported courses, has source documents or JSON/importer files. Course 10, `ai-media-content`, is the Russian-language media-production curriculum. The 2026-11-09 course audit recorded five modules and 15 lessons, with Course 10 unpublished. Keep it unpublished unless explicitly authorized. Lesson 115 media remains unfinished, and Module 6 scope has not been author-approved. See [COURSE_CONTENT_MAP.md](COURSE_CONTENT_MAP.md) and [ROADMAP.md](ROADMAP.md).

The platform itself is not verified to call a generative-AI inference provider. AI tools and methods described in lessons are educational subject matter. Silero TTS was used in a local course-media production workflow; that is not a learner-facing model integration. See [AI_INTEGRATIONS.md](AI_INTEGRATIONS.md).

## Operating principles

- Read [CURRENT_STATE.md](CURRENT_STATE.md) and check `git status` before any development.
- Preserve all modified and untracked work. Do not reset, clean, or discard it.
- Treat canonical course sources, database records, protected media and learner progress as separate assets with explicit ownership and approval boundaries.
- Use isolated test databases; never infer that a development database is disposable.
- Never expose secrets or personal learner information in reports.
- Keep generated media, local configuration, SQLite databases, backups and experimental candidates out of Git unless individually reviewed and explicitly intended for version control.
- Record durable architectural decisions in [DECISIONS.md](DECISIONS.md), and update [CURRENT_STATE.md](CURRENT_STATE.md) after a substantial development phase.

## Detailed evidence

- [Technical inventory](../project-audit/01-technical-inventory.md)
- [Course content and database audit](../project-audit/02-course-content-and-database-audit.md)
- [Media and production audit](../project-audit/03-media-and-production-audit.md)
- [Technical quality, security and reliability audit](../project-audit/04-technical-quality-and-bug-audit.md)

## Documentation map

There is no repository-root README in this checkout. `frontend/README.md` is the default Vite template; `quizzes/README.md` documents the quiz workflow. The `docs/` tree contains dated course plans, implementation reports, asset manifests, design-phase notes and audit reports. Several are historical snapshots and can conflict with later completion reports or current manifests. Prefer the current state page and dated completion records, then inspect the live source/manifest before relying on an old plan. Do not delete or rewrite historical records as part of routine development.

Known reconciliation points: root `AGENTS.md` still names the Neo-Academic look, while later approved frontend phases use the Amethyst Motion/Cinematic identity; the quizzes README says its migration is pending, while the 2026-11-09 course audit found quiz records; the Module 3 asset manifest still says planning-only despite attached images; Course 8 Lesson 92 database content differs from the base JSON; and older Module 4/5 documents describe earlier stages. These are dated/documentation conflicts, not authorization to change app state. Recheck runtime migration state and content sources before acting.
