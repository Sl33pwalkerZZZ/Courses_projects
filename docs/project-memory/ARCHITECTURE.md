# Architecture

**Verified:** 2026-11-09 from source inspection and project audits. Production deployment topology and current database state are not established by this document.

## System shape

```text
Browser (React 19 / Vite)
  ├─ React Router pages and shared components
  ├─ i18next RU / KK / EN, theme provider, Motion
  └─ Axios API client + auth-session utilities
       └─ Django REST Framework API (JWT)
            ├─ courses — catalog, curriculum, lesson content and protected media
            ├─ progress — enrollment, lesson progress and assignment submissions
            ├─ quizzes — quiz authoring, attempts and server-side grading
            ├─ certificates — policies, eligibility, issuance, PDF and verification
            ├─ reviews — course ratings and moderation data
            ├─ studio — instructor/admin authoring and review workflows
            └─ users — custom user, roles, registration and JWT endpoints
                 └─ SQLite configured for local development
```

## Backend

- `config/` contains Django settings and root URL routing. `config/settings.py` has intentional local uncommitted changes; do not overwrite or expose its values.
- The Django apps are separated by domain as shown above. Models express ownership and relationships; serializers validate API input/output; views and permission classes enforce request access; service modules hold multi-record business rules where present.
- `courses` owns `Course → Module → Lesson`, optional `LessonLearningContent`, lesson images/attachments and playback grants. Import commands live under `courses/management/commands/` and canonical course JSON under `courses/management/`.
- `progress` owns enrollment requests/enrollments, lesson completion and assignment drafts/review. `quizzes.services.submit_attempt` is the server grading boundary. `certificates.services` computes eligibility and issues/revokes certificates.
- `studio` exposes authoring and review APIs. Author access is scoped to owned courses; administrator operations use existing staff/admin authorization. DOCX import has preview and confirmation steps.
- `users` supplies a custom user model with application roles, alongside Django staff/superuser flags. Do not assume those flags and the application role are interchangeable.
- Local settings configure SQLite at the project database path. No production deployment topology, CI release flow, task queue, or separate production settings module was confirmed in the audits.

## Browser application

- Entry: `frontend/index.html` → `frontend/src/main.jsx` → `frontend/src/App.jsx`.
- `main.jsx` installs router, i18n, theme, global styling and Motion reduced-motion policy. `App.jsx` routes public catalog/course pages, auth, certificates, profile, lessons, instructor preview and Instructor Studio.
- `frontend/src/api.js` handles API requests and JWT access/refresh. `frontend/src/utils/authSession.js` tracks session changes, including cross-tab changes. The API implementation is designed to reject stale-session responses and use one shared refresh request.
- Course and lesson views call Django APIs. `MediaLessonReading.jsx` composes structured lesson sections and places media at configured anchors; unplaced media falls back to the existing attachment/gallery behavior.
- Public UI styling is spread across global CSS, design tokens, Amethyst/Cinematic styles and component/page styles. Translation resources are under `frontend/src/i18n/locales/`.

## Protected media and browser playback

- Lesson images/audio/downloads use authenticated API delivery. Lesson video uses a scoped, short-lived playback grant and same-origin, path-scoped HttpOnly/SameSite cookie because native `<video>` cannot attach the app's Authorization header.
- `courses/video.py` validates the grant and current lesson access while serving complete, HEAD and byte-range responses. Storage paths are confined; protected files must not be placed behind a public `MEDIA_URL`.
- Vite development proxies `/api` to Django. Production must route frontend and API same-origin over HTTPS for the native playback cookie design to work. Production proxy/TLS settings remain unverified.
- Details: [`docs/protected-lesson-video.md`](../protected-lesson-video.md) and the media audit.

## Local development and verification

- Backend uses `.venv/bin/python` when that environment exists; frontend tools live in `frontend/`.
- `run.sh` is a local development launcher for Django and Vite, not a production deployment definition.
- Backend tests use `python manage.py test`; frontend tests use Node's test runner over `frontend/tests/*.test.mjs`; lint/build scripts are in `frontend/package.json`.
- See [TESTING_QA.md](TESTING_QA.md) for bounded commands and known limitations.

## Evidence limits

This is a source architecture map, not proof that current services are running. Current migrations, database records, secrets, production hosts, browser flows and deployed media routing require separately authorized checks. Do not read learner records or credentials just to refresh this overview.
