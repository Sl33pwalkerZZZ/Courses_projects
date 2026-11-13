# AI Courses — Technical Inventory

**Audit date:** 2026-11-09
**Branch:** `design/amethyst-motion`
**Scope:** Read-only source, documentation, manifest and Git inspection. This report is a technical inventory, not a runtime penetration test or course-content audit.

Evidence labels used below:

- **CONFIRMED** — directly visible in source/configuration/documentation or Git metadata inspected for this report.
- **INFERRED** — strongly indicated by source design or project documentation, but not exercised in a live runtime during this audit.
- **UNKNOWN** — not verified or not present in the inspected evidence.

## A. Project overview and repository state

**CONFIRMED:** This is an existing Django REST Framework and React/Vite learning platform. The Django project is split across `courses`, `progress`, `quizzes`, `certificates`, `reviews`, `studio`, and `users`; `config` contains the Django project configuration. The browser application lives under `frontend/`. Separate Remotion projects and production outputs live under `video-production/`.

**CONFIRMED:** Git is on `design/amethyst-motion`, four commits ahead of `origin/design/amethyst-motion`; HEAD is `e1ae750` (`test: document and validate the post-redesign checkpoint`). The four commits not at the recorded origin are:

At the start of the audit, status showed four modified tracked files, 55 untracked entries, no staged changes, and the branch four commits ahead. After writing this report, status still shows the same four modified tracked files and now 56 untracked entries; the only additional entry is `docs/project-audit/01-technical-inventory.md`. No unrelated status entry changed.

| Commit | Scope |
|---|---|
| `28ff315` | Protected instructional video infrastructure, playback grants, range delivery, validation, tests and docs. |
| `ca684c3` | Module 5 source/import package, lesson authoring materials and validation. |
| `42455ca` | Cinematic frontend redesign phases 1–3, including public, Studio and student pages plus protected video frontend support. |
| `e1ae750` | Redesign/checkpoint documentation and an additional Module 5 package test. |

The origin commit at the inspected ref is `5cf26f9` (`feat: finalize module 4 audio lessons with Silero TTS`). This is a local Git ref comparison; no remote operation was run.

**CONFIRMED:** Before this report, the working tree had four modified tracked files:

- `config/settings.py` — intentional local settings change; values were not reproduced here.
- `courses/management/commands/import_media_module_5.py`
- `courses/management/media_module_5.json`
- `docs/courses/media-module-5-assets.json`

There were also numerous existing untracked files. Broad categories include copied `.agents/skills/` files; `.vite/` cache; `.local-video-test/` and `.local-cinematic-qa/` QA artifacts; untracked Module 4 candidate audio and production metadata; Lesson 113/114 integration commands, tests, JSON and completion documents; and large untracked `video-production/lesson-113-production/` and `lesson-114-production/` trees. There is also the unusual untracked text filename `e modules 2-4 and inline learning media\"`. It appears to be a captured diff/stat output artifact, not application source; it was not deleted or renamed.

The complete status is preserved in the terminal session. This report records the four modified paths and the significant untracked families rather than duplicating every generated file name. No existing file was changed during the audit.

**CONFIRMED:** `.gitignore` excludes `.venv/`, Python bytecode/cache, `db.sqlite3`, `media/`, `.local-redesign-checkpoints/`, `course_sources/`, and `.local-course-backups/`. Not every local QA/cache family is ignored. SQLite backups, private media, local environment files, and output folders must be reviewed explicitly before future staging. No file was staged.

## B. Technology stack and runtime configuration

### Backend

**CONFIRMED:** `requirements.txt` names Django, Django REST Framework, SimpleJWT, `django-cors-headers`, Pillow, and ReportLab. Actual imports/use inspected:

| Dependency | Evidence and feature |
|---|---|
| Django | Models, URL routing, admin, settings and application services throughout the backend. |
| Django REST Framework | API views, serializers, permissions, validation and API tests across the apps. |
| SimpleJWT | `users/urls.py` exposes token obtain/refresh endpoints; `frontend/src/api.js` uses them. |
| `django-cors-headers` | Listed in settings and middleware for API cross-origin handling. |
| Pillow | Image validation/import paths (`studio/views.py`, `courses/management/commands/import_lesson_media.py`, Module 3 image importer) and image fields. |
| ReportLab | Lazy-loaded by `certificates/pdf.py` to render downloadable certificates; PDF tests check its availability. |

**CONFIRMED:** React 19, React DOM, Vite, `@vitejs/plugin-react`, Axios, Motion, Lucide React, i18next/react-i18next, React Router, and Oxlint appear in `frontend/package.json`. The tracked `frontend/package-lock.json` records npm resolution. `frontend/package.json` scripts are `dev`, `build`, `lint`, and `preview`; there is no npm `test` script. The repository’s frontend unit tests are `.mjs` files under `frontend/tests/` and use Node’s test runner by convention.

**CONFIRMED:** Additional `video-production/*/package.json` files define isolated Remotion projects and scripts for Studio, preview/final rendering, lint/build and package verification. Their dependencies include Remotion packages, React and development tools. These are not dependencies of the learner-facing frontend.

**CONFIRMED:** `config/settings.py` configures the custom `users.User`, SQLite, DRF/JWT settings, static/media behavior and certificate-related feature settings. Django’s `MEDIA_URL` is `/api/private-media/`; in `DEBUG`, `config/urls.py` also adds a distinct `/media/<path>` handler. Secret values and environment-variable contents were not read or included.

**UNKNOWN:** No Dockerfile/Compose, Procfile, deployment manifest, Celery task module, or task queue configuration was found in the bounded project-file search. The checked-in `run.sh` starts Django’s development server and Vite and terminates child jobs on exit; it is a local development launcher, not a production deployment definition. Production hosting, HTTPS termination, static asset serving, database provisioning and secrets management are not documented by the inspected files.

### Database and migrations

**CONFIRMED:** Django settings select SQLite at `BASE_DIR / 'db.sqlite3'`. Migrations are present in every domain app. The source migration files include courses through `0007_lessonplaybackgrant`, progress through `0004_structured_assignments`, reviews through `0003_review_rating_range`, certificates through `0004`, studio through `0002`, and initial migrations for users/quizzes.

**UNKNOWN:** This audit did not query the local SQLite database or migration table. Therefore it does not claim that every listed migration is applied, that the database is healthy, or that any particular course/lesson/attachment row currently exists. Test configuration/runtime database behavior was not exercised.

## C. Backend architecture

### Apps and responsibilities

| App | Responsibility confirmed from models, views and URLs |
|---|---|
| `courses` | Course/catalog/curriculum records, structured lesson content, images, assignments, uploaded lesson attachments, protected media delivery and import commands. |
| `progress` | Enrollment and enrollment requests, lesson completion, student activity, structured assignment drafts/submissions and teacher review. |
| `quizzes` | Published lesson quizzes, questions/choices, immutable attempt summaries and answer snapshots. |
| `certificates` | Course-level certificate policy, eligibility, issuance/revocation, PDF generation, download and public verification. |
| `reviews` | Course reviews, rating validation, moderation-related data and course/own-review APIs. |
| `studio` | Author/admin course editing, curriculum and assessment management, media upload, DOCX preview/import, publication requests, enrollment decisions, assignment review and instructor roles. |
| `users` | Custom user/role model, registration, current-user endpoint and JWT endpoints. |

### Main data relationships

**CONFIRMED:** `Course` references a protected `Direction` and an author; it owns ordered `Module` rows. Modules own ordered `Lesson` rows. A lesson stores source text and may have one `LessonLearningContent` row with JSON objectives, source sections and interactions. It can own lesson images, assignments and lesson attachments; a quiz is OneToOne with a lesson. Lesson content is rendered from the stored text/structured sections by the React lesson reader.

**CONFIRMED:** `Enrollment` joins a student to a course and enforces one enrollment per student/course. `EnrollmentRequest` is a separate application lifecycle with pending/approved/rejected state, reviewer and timestamps; the model constrains duplicate pending applications. `LessonProgress` associates an enrollment with a lesson and is unique per pair. `AssignmentSubmission` links an assignment and student, supports draft/review state, feedback, revision/history and structured payloads.

**CONFIRMED:** `QuizAttempt` stores a score, correctness counts, passing threshold snapshot, pass/fail state and idempotency identifiers. `QuizAnswer` stores answer snapshots so past feedback can remain meaningful if question content changes. Choice correctness is persisted server-side; quiz submission is handled through `quizzes.services.submit_attempt`.

**CONFIRMED:** `CourseCertificatePolicy` configures course eligibility; `Certificate` stores opaque verification code, learner/course/issuer snapshots, evidence, issuer and revocation fields. `certificates.services.eligibility`, `issue_certificate`, and `revoke_certificate` are the service boundary. Reviews link a student and course. Studio adds publication requests/events, per-course settings, image descriptions and DOCX import-preview records.

### Request path and APIs

**CONFIRMED:** `config/urls.py` includes Studio, user authentication, course, progress, quiz, certificate routes and a private-media route. A typical browser request flows through the frontend Axios client (`frontend/src/api.js`) to a DRF view; the view applies authentication/permissions and delegates persistence/business rules to serializers or service functions; the serializer returns public or user-scoped data to the page/component.

Important endpoint families (route definitions are in the named `urls.py` files):

| Endpoint family | Responsibility and frontend consumer |
|---|---|
| `/api/auth/token/`, `/api/auth/token/refresh/`, `/api/auth/register/`, `/api/auth/me/` | JWT login/refresh, registration and identity; `api.js`, `Login`, `Register`, `Profile`. |
| `/api/courses/`, `/api/courses/<slug>/`, `/api/lessons/<id>/` | Public catalog/course descriptions and permission-checked lessons; `CourseCatalog`, `CourseDetail`, `LessonView`. |
| `/api/my/enrollments/`, `/api/my/enrollment-requests/`, `/api/my/activity/`, `/api/lessons/<id>/complete/` | Student learning access, applications, activity and lesson completion; enrollment/profile/lesson utilities. |
| `/api/courses/<slug>/enroll/`, `/api/courses/<slug>/enrollment-requests/` | Open enrollment or application workflow according to course policy. |
| `/api/lessons/<id>/quiz/`, `/attempts/`, `/api/quiz-attempts/<id>/` | Enrolled learner quiz retrieval, grading and own attempt history. |
| `/api/studio/...` | Author/admin dashboard, course/curriculum/assessment edits, attachment/image upload, publication, submission review, enrollment decisions, roles and import workflow. |
| `/api/lesson-images/<id>/`, `/api/lesson-attachments/<id>/` | Protected image/attachment delivery and metadata. |
| `/api/lesson-attachments/<id>/playback-grant/` and `/playback/` | Native video grant and private byte-range stream. |
| `/api/courses/<slug>/reviews/`, `/api/reviews/<id>/` | Course review collection and owner review operations. |
| `/api/courses/<id>/certificate-status/`, `/api/my/certificates/`, `/api/certificates/verify/<code>/`, `/download/`, `/api/certificates/admin/...` | Learner certificate status/list, minimal public verification, downloads, and admin issue/revoke. |

**CONFIRMED:** Backend APIs use standard Django/DRF URL/view classes rather than a generated schema or router registration. No OpenAPI/Swagger config was identified in the inspected project files.

### Authentication and authorization

**CONFIRMED:** `users.User` adds `student`, `author`, and `admin` roles to Django’s user. SimpleJWT token obtain/refresh views are in `users/urls.py`. `studio.permissions.moderator` recognizes an active superuser or admin-role account; `instructor` additionally recognizes active authors. `studio.services.course_for`/`owned_courses` are ownership helpers, while `courses.permissions.can_access_lesson` grants access to permitted moderators, the owning author, or enrolled learners.

**CONFIRMED:** `frontend/src/api.js` attaches access tokens to private API calls, uses a shared refresh flight, tracks session generation and rejects responses after an account change. Public course reads can remain anonymous; stale credentials are not used for public browse. Login/register/logout update the session store and local storage. The source includes cross-tab session storage listeners under `frontend/src/utils/authSession.js`.

**INFERRED:** The design aims to isolate private page state across account changes by keying private routes to the auth-session generation and canceling stale responses. This was source-inspected, not browser-tested here.

### Import and background work

**CONFIRMED:** `courses/management/commands/` contains import/finalization tools for course source modules 1–5, lesson media, Module 3 images, Module 4 media, and Lesson 113/114 video integrations, alongside demo seed commands. `studio/word.py` parses DOCX content; Studio import is split into preview and confirm endpoints. No Celery/RQ/async task implementation was found; media validations and imports are request/management-command work, with `ffprobe` invoked synchronously for MP4 validation.

**UNKNOWN:** The actual current database contents, applied migration state, enabled course records, and effective production environment settings were intentionally not verified in this phase.

## D. Frontend architecture

### Entry points, routes and state

**CONFIRMED:** `frontend/index.html` mounts `frontend/src/main.jsx`; `main.jsx` installs i18n, theme provider, global CSS/tokens, Motion’s reduced-motion configuration and React Router. `App.jsx` maps routes to catalog, login/register, certificate verification, profile, course detail, instructor preview/Studio and lesson view. Studio routes nest dashboard, course list/editor, curriculum, assessment, submissions, publication and import screens.

**CONFIRMED:** Key page components include `CourseCatalog.jsx`, `CourseDetail.jsx`, `LessonView.jsx`, `Profile.jsx`, `Login.jsx`, `Register.jsx`, `CertificateVerification.jsx`, and `pages/instructor/*`. Shared components cover navigation/footer, catalog filters/cards, enrollment and review UI, learning content, quizzes, progress/calendar, protected media, Studio navigation and reusable UI primitives.

### Lesson and media rendering

**CONFIRMED:** `LessonView.jsx` fetches `/api/lessons/<id>/`, resolves lesson presentation, objectives, structured sections, images, attachments, assignment UI, quizzes and completion controls. `MediaLessonReading.jsx` renders ordered structured sections and places images/audio/video attachments after configured section anchors, falling back to gallery/attachment placement where no anchor exists. `LearningContent.jsx` handles reusable structured text blocks; `Course8Reading.jsx` and `course8Reading.js` provide specialized course 8 reading/presentation behavior.

**CONFIRMED:** `ProtectedLessonImage.jsx` and the lesson attachment utilities use authenticated API loading. `LessonAttachment.jsx` renders audio and downloadable SRT; `LessonVideo.jsx` uses native video with controls, captions and transcript. Native media cannot set arbitrary JWT headers, so `utils/lessonVideo.js` first requests a grant and then loads the same-origin playback path with scoped cookies. It does not place a permanent JWT in the media URL or use full-file Blob buffering for video.

### Design system, localization and responsiveness

**CONFIRMED:** Styling combines global `index.css`, `styles/v2-tokens.css`, Amethyst Motion/Cinematic styles and per-component/page CSS. `ThemeProvider` applies a light/dark theme; i18next locale files exist for Russian, Kazakh and English under `frontend/src/i18n/locales/`. Motion is used in selected UI components and global `MotionConfig reducedMotion="user"` respects the user preference. Responsive behavior is implemented in component/page CSS media queries.

**UNKNOWN:** This audit did not launch a browser or evaluate actual layout/accessibility at target widths. No screenshots or live console/network evidence were created for this inventory.

## E. AI and intelligent feature inventory

**CONFIRMED:** A bounded source scan of application Python/React code (`config`, Django apps and `frontend/src`) found no OpenAI, Gemini, Anthropic/Claude, Groq, LangChain/LangGraph, vector database, embedding, RAG or local-LLM client integration. The production frontend/backend therefore has no verified generative-AI inference API in this inventory.

**CONFIRMED:** AI terminology, prompts and workflow explanations appear in course content and seed/import data (for example `courses/management/demo_course_data.py`, `courses/management/seed_comfyui_course.py`, and media-module JSON). These files author educational material; they are not evidence of the platform calling a model provider.

**CONFIRMED:** The local Module 4 audio-generation source `course_assets/module_4/voice_candidates/prepare_roman_module4.py` identifies Silero `v5_cis_base_nostress`, `ru_roman`, a checkpoint source/checksum and the local model API. The Module 5 draft preview script imports PyTorch at runtime and loads that checkpoint from a separate local `.local-silero-eval` environment. These scripts create course-production audio; they are not part of the Django learner request path. The local Silero checkpoint/venv is not tracked as an application dependency.

**UNKNOWN:** No complete license or model-cache audit was performed beyond reading the checked-in `LICENSE_CIS` notices and provenance files. No model was downloaded, loaded or executed during this task.

## F. Media/video architecture and production workflow

### Protected storage and delivery

**CONFIRMED:** `LessonAttachment` stores lesson, kind (`audio`, `srt`, `video`, `vtt`), file name, MIME type, hash, label/caption/transcript/provenance, section anchor and order. `LessonPlaybackGrant` stores a user, attachment, token hash, expiry and revocation timestamp—not a raw JWT. Private files use the `lessons/attachments/` namespace.

**CONFIRMED:** `courses/media.py` confines resolved paths to the configured storage root and rejects traversal/symlink escapes. The legacy development public-media view blocks `lessons/` and `submissions/`, and uses a separate public root. Protected attachment/image views apply lesson authorization. `courses/attachments.py` validates extension/signature/size and SRT/VTT/audio formats; `courses/video_validation.py` checks MP4 signature and invokes trusted system `ffprobe` to validate stream/codec/dimensions/rate. Upload is available through the authorized Studio lesson-attachment endpoint and React `LessonAttachmentManager`.

**CONFIRMED:** `courses/video.py` creates short-lived, scoped, revocable playback grants, sets a path-scoped HttpOnly/SameSite cookie, rechecks user/session/access on media reads, and serves full/HEAD/range responses (`200`, `206`, `416`) without exposing a public file path. `docs/protected-lesson-video.md` documents the HTTPS/same-origin routing implications. This architecture depends on production routing `/api` to Django on the frontend origin for native cookie-authenticated playback.

### Assets and tools

**CONFIRMED:** Module 3 has six tracked PNG teaching illustrations. Module 4’s tracked final package includes the Silero license notice, approved audio for lessons 10–12, synchronized lesson 11 SRT, illustrative SRT and workflow PNG, plus the final manifest/provenance. The working tree also contains untracked Module 4 experimental/candidate audio and local generation scripts; these are not all production assets and should not be staged as a group without the manifest/license/provenance review.

**CONFIRMED:** Module 5’s imported lesson source lives in `courses/management/media_module_5.json`, with a dry-run/apply importer and source/asset/storyboard documentation. Lesson 113/114 integration completion docs report protected attachments and source manifests. The untracked production directories contain final/preview/QA MP4s, audio stems, frame captures, render logs, scripts, and `node_modules`; treat these as mixed production source and generated/local artifacts, not a single deployable asset bundle. The completion reports document that lessons 113 and 114 were integrated, with course 10 remaining unpublished. This state was not re-read from SQLite during this audit.

**CONFIRMED:** System `ffmpeg` and `ffprobe` executables were found on PATH. Node and npm were not found on PATH (a bounded home-directory search found no `bin/node` executable). The static frontend test/build/lint commands could therefore not be run in this environment. No external tools or packages were installed.

**INFERRED:** Remotion was used to author/render the Lesson 113/114 videos, based on checked-in per-production `package.json` scripts, source folders, output files and completion docs. The actual render process was not executed in this audit.

## G. Testing and infrastructure

**CONFIRMED:** The source tree contains Django test modules across all domain apps, including dedicated attachment/video upload/range tests, media import tests, Module 5 and Lesson 113/114 integration tests, enrollment/permission/assignment-review tests, quiz/user/review/certificate tests. Frontend contains 34 `.test.mjs` files under `frontend/tests/`, covering authentication/session, course, learning/media/video, Studio, localization/design and other utility behaviors.

**CONFIRMED:** `frontend/vite.config.js` proxies `/api` to `http://127.0.0.1:8000` in Vite development to keep protected media same-origin. `frontend/package.json` has `npm run lint` (Oxlint) and `npm run build` (Vite); test files are not exposed by a package script in the inspected manifest. Django tests are managed through `manage.py test`.

**NOT RUN:** No Django, frontend, security, browser or production-render tests were executed. The project instructions warn that database access/test setup can mutate local state; this audit avoided tests and SQLite queries. The shell also lacks Node/npm. Prior project documentation contains test reports, but they are historical records and were not treated as newly reproduced results.

**UNKNOWN:** CI workflow files, production release automation and deployment environments were not found in the bounded search. No GitHub Actions, Docker configuration or production web-server configuration was identified.

## H. Important risks, limitations and follow-up inventory

1. **Working tree contains substantial local and reproducible work. CONFIRMED.** Four tracked files are modified and numerous production/test/documentation/experimental files are untracked. No cleanup or staging should happen without reviewing the exact files individually.
2. **Local configuration differs from HEAD. CONFIRMED.** `config/settings.py` is modified. Its contents are intentionally not reproduced here; keep it out of any future broad staging operation.
3. **Production video work is incompletely represented in Git. CONFIRMED.** The Lesson 113/114 completion docs and integration scripts/tests are in the untracked set, as are output MP4s and extensive QA/node_modules artifacts. Separate durable source and required deliverables from caches, stems and screenshots before deciding what belongs in version control.
4. **Runtime state is not established by source. UNKNOWN.** Current database migration status, exact course/lesson/attachment rows, active media files, server settings and course publication state require a separately authorized read-only/runtime verification.
5. **No AI inference integration found. CONFIRMED within scanned application source.** Course content about AI should not be mistaken for a platform model integration. Silero is a local media-production workflow with an isolated PyTorch dependency.
6. **Deployment contract needs environment-specific verification. INFERRED.** Protected native playback relies on same-origin HTTPS cookies and correct `/api` proxying in production; source documentation explains the requirement, but no production deployment config was found.
7. **Frontend checks unavailable here. CONFIRMED.** Node/npm were absent. Existing `node_modules` directories do not prove that the current runtime or build is available.

## I. Areas not verified

- Current SQLite data, migration application state, and course/module/lesson counts.
- Actual authenticated browser flows, visual appearance, accessibility tree, network/console errors and responsive behavior.
- Test execution against an isolated test database.
- Production environment variables/secrets, production database/storage layout, HTTPS/cookie settings and deployment pipeline.
- Whether every ignored or local source/media file has a verified backup.
- Full legal/license review of every model, generated media file or embedded font.
- Runtime behavior of the current uncommitted Module 5 importer/manifest edits beyond source inspection.

## Inspection trail and safety

Inspected project instructions (`AGENTS.md`), `.gitignore`, Git status/log/diff summaries, Django model/view/serializer/permission/service/URL inventories, migration filenames, settings structure with values omitted, management commands, frontend routes/API/auth/theme/i18n/lesson media components, package manifests/lockfiles, test inventory, media documentation/manifests and selected production workflow source. A full file read of student records, credentials, `.aws`, `.env`, SQLite backup files or private course source documents was not performed.

No application code, configuration, course content, database, dependency, existing documentation, generated asset, or Git index was modified. No tests, migrations, imports, Git staging/commit/push, browser login, or database query was run. The only file created for this task is this report.
