# AI Courses — release deployment handoff

## Release status (2026-11-26)

Branch: **release/ai-courses-v1**. Existing commits: `1cd2f7f` (D5), `9faa556` (AI Guide); the following security/handoff commit completes this release. Its exact hash is returned in the delivery report; obtain it with `git rev-parse origin/release/ai-courses-v1` after fetch. [Release history](https://github.com/Sl33pwalkerZZZ/Courses_projects/commits/release/ai-courses-v1).

Owner authorizes one branch push and **production-only Course10 beta publication after deployment and smoke tests**, not local database writes. Deployment and publication have **not** been performed. Course8 must remain unchanged. Certificate issuance stays disabled. The ASCII/theme inconsistency is a known nonblocking visual issue; D6–D8/RAG are out of scope.

Real Groq smoke with the rotated root `.env` key returned **HTTP200**, using synthetic non-sensitive lesson text. No stale process-key override was present; the service sent Bearer authorization to the fixed Groq HTTPS endpoint. Only answer length was recorded, never a key or private course content. Previous401 was superseded by this successful test.

## Backend configuration — implemented, not hypothetical

Use **DJANGO_SETTINGS_MODULE=config.production**, not development `config.settings`. Required process environment:

```text
DJANGO_SETTINGS_MODULE=config.production
DJANGO_ENV=production
DJANGO_DEBUG=false
DJANGO_SECRET_KEY=<new private random key, at least 50 characters>
DJANGO_ALLOWED_HOSTS=<exact API hostname, comma separated if needed>
SQLITE_PATH=<absolute persistent path to restored database>
DJANGO_MEDIA_ROOT=<absolute private attachment/media directory>
DJANGO_PUBLIC_MEDIA_ROOT=<separate absolute public cover/image directory>
DJANGO_STATIC_ROOT=<absolute collected-static directory>
GROQ_API_KEY=<private rotated provider key>
GROQ_MODEL=openai/gpt-oss-20b
DJANGO_CSRF_TRUSTED_ORIGINS=<exact HTTPS frontend origin>
DJANGO_CORS_ALLOWED_ORIGINS=<exact HTTPS frontend origin, only if needed>
DJANGO_EMAIL_HOST=<production SMTP server>
DJANGO_EMAIL_PORT=587
DJANGO_EMAIL_HOST_USER=<SMTP username>
DJANGO_EMAIL_HOST_PASSWORD=<private SMTP credential>
DJANGO_DEFAULT_FROM_EMAIL=<authorized sender>
```

Generate the new signing key inside the hosting secret manager; never copy the historic public key. `config.security` rejects missing/weak/public-development keys in production and rejects DEBUG=true. `SECRET_KEY_FALLBACKS=[]`: old signed sessions/JWTs must be invalidated; users sign in again. The historic revoked key remains in already-public history by explicit owner decision; no history rewrite or force push.

For local development only, an absent process key generates a stable mode600 `.local-django-secret`, atomically and outside version control. **Do not deploy that file.** DJANGO_SECRET_KEY is read from process environment, not implicitly from root `.env`. The Groq client separately reads only GROQ_API_KEY/GROQ_MODEL from root `.env` when no process variable exists; production should use secret-manager environment. Restart workers after rotating either credential. Never log Authorization, prompts, learner responses or `.env`.

Production settings force HTTPS redirect, secure cookies, DEBUG=false and certificate issuance=false. Only behind a trusted ingress which strips client-supplied forwarded headers, set `DJANGO_TRUST_PROXY_HTTPS=true`. HSTS is one year for this host. `check --deploy` intentionally retains W005/W021 until the domain owner explicitly approves all-subdomain HTTPS/preload; do not enable preload blindly. SMTP configuration is required operationally; no email delivery was tested.

Use persistent writable SQLite with one application instance/worker initially. Requirements install Django/DRF; install a production WSGI server such as gunicorn in the deployment environment (not bundled in current requirements). Current LocMem throttle is per-process, not a global spending quota: multiple workers/instances require a shared cache via a reviewed deployment override and provider budget limits.

```bash
# Environment variables above must already be set securely.
.venv/bin/python manage.py check --deploy
.venv/bin/python manage.py showmigrations
.venv/bin/python manage.py migrate --plan
# Only against the backed-up deployment DB after isolated rehearsal:
.venv/bin/python manage.py migrate --noinput
.venv/bin/python manage.py collectstatic --noinput
.venv/bin/gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 1 --timeout 60
```

Never point these deployment commands at the working local SQLite. Do not expose Django's dev server publicly.

## Frontend, reverse proxy and protected media

Build `frontend/` with `npm ci && npm run build`, `VITE_API_URL=/api`. On Vercel or equivalent, configure a **same-origin `/api` reverse proxy** to the HTTPS Django backend; a cross-origin base URL alone is insufficient for protected playback cookies. Preserve Authorization, Set-Cookie, Cookie, Range/If-Range, Content-Range,206 and streaming. Never cache personalized/private API/media responses or add CDN public caching to them. Serve collected static files and the separate public-media directory through the ingress; never serve the private media root as a public directory. Test actual proxy cookie behavior before launch.

No secrets belong in VITE_* variables, build artifacts or Git. Groq endpoint is `POST /api/ai-guide/`, authenticated, with `{lesson_id, question, language}`. Lesson authorization is checked server-side; only lesson title/text enters the provider request, not quiz keys, student submissions or private attachments. Stateless calls,25s timeout,12/min/user, no-store. This is not RAG or automatic grading; answers can be wrong.

## Authorized data/media transfer

Git is **not** a database/media backup. Transfer a consistent private SQLite backup (SQLite backup API) plus all referenced protected media from the verified owner recovery archives over a private channel. Record SHA256, restore outside the repository, verify SQLite integrity/FK and every referenced file before starting the backend. Preserve attachment IDs, paths, question/choice IDs, quiz attempts and student records. Do not copy arbitrary previews instead of the approved nine Module5 final MP4 and corresponding VTT. Public images and private attachments have distinct roots.

Prefer restoring the current verified database/media, not recreating courses or blindly reapplying create-only importers. Canonical module JSON/importers are source/recovery evidence, not a complete export of learner state; Module1 additionally needs the private source document. Module6 importer conflicts with an already-published Quiz5 by design. C1/C2 are already applied to the local source database. On the restored **still-unpublished Course10**, verify without changes:

```bash
.venv/bin/python manage.py correct_course10_editorial --dry-run
.venv/bin/python manage.py reorder_course10_quiz5 --dry-run
```

Expect no C1 text changes and C2 already-applied/no changes. Stop on conflicts; do not rerun apply without a separate reviewed plan. Confirm Course10 six modules/16lessons, Course8 unchanged, Quiz5 published/15questions/70%, assignment rubric unchanged, certificate policy disabled.

## Course10 beta publication — exact production-only Studio workflow

After production HTTPS, DB/media restoration and access/playback smoke succeed:

1. Author or authorized administrator opens `/instructor/courses/10/publication`; preview `/instructor/courses/ai-media-content/preview`.
2. Manually review both acknowledgements: «Я проверил источник, факты, ссылки и материалы уроков» and «Я проверил каждый вопрос, правильный ответ и пояснение». Do not auto-check them. Existing nonblocking editorial note: verify the course description represents the whole course rather than only Module1.
3. If desired, the owner may use the existing course editor to add a truthful localized beta notice after reviewing translations. No automatic beta flag or content edit was introduced in this release.
4. «Отправить на проверку» and confirm. Existing API: POST `/api/studio/courses/10/publication/`, source_reviewed=true, assessment_reviewed=true.
5. An active **admin role or superuser** opens `/instructor/reviews` (`is_staff` alone is insufficient), reviews course/source/test, checks «Я проверил источник, уроки, тест и требования публикации», then «Одобрить и опубликовать». Existing decision API: POST `/api/studio/reviews/{request_id}/decision/`, decision=approve.
6. Confirm actual production Course10 becomes visible publicly and lessons remain enrollment-protected. Certificate issuance/policy must remain off. No such action has been taken locally.

Existing server gates: title/description, lessons and no empty modules, each lesson title/content, at least one valid quiz, both acknowledgements; quiz pass score0–100, nonempty questions, at least two nonempty choices and valid correct-answer cardinality. Duplicate pending requests are rejected. Approval rechecks the content fingerprint atomically; changed content requires rejection/new submission. Approval publishes the course/quizzes and records source review, not certificate activation.

## Minimal deployment smoke / verification evidence

- Anonymous catalog and published-course detail; draft requests denied. Synthetic enrolled student sees all six modules/16lessons; unrelated account cannot read lessons/files/submissions.
- All nine videos: play, Range seek, reopen, concurrent grants and113→114→113; correct captions can be enabled; audio and permitted downloads work. Check proxy preserves per-grant cookie paths and revocation.
- Login/refresh/logout/account switch; lesson progress restoration, quiz/assignment and Studio preview. Use synthetic rehearsal data; do not mutate real learner progress.
- Groq one non-sensitive authorized request returns200, no key in browser; unauthorized lesson access is denied. Check error and quota handling without flooding provider.
- Existing certificate owner preview/download remains authenticated; no new issuance. Public verification stays unavailable until separately configured/authorized.
- Verify SMTP delivery and persistent backup/restore operationally; neither is proven by a source push.

This release verification:29 isolated Django tests (security6 + AI/authorization23), system check and whitespace checks. Production deployment check has zero errors and the two intentional HSTS warnings above. Earlier AI commit evidence remains backend23, frontend475,lint/build, isolated Chromium UI/API; those browser tests used a synthetic provider. The new real Groq200 is a separate server-client smoke, not production browser/deployment approval. Native security_reviewer reviewed the security implementation; final staged review excludes unrelated local settings, databases, credentials, backups and generated media.
