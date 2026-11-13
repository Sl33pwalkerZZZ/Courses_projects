# Testing and QA

**Commands verified in project docs/audit:** 2026-11-09. Commands below are guidance; run only after checking current project state and isolation.

## Typical checks

```sh
# From repository root; use the existing environment
.venv/bin/python -B manage.py check
.venv/bin/python -B manage.py makemigrations --check --dry-run
.venv/bin/python -B manage.py test

cd frontend
npm run lint
node --test tests/*.test.mjs
npm run build
```

No frontend `npm test` script was identified in the audited package manifest; Node's built-in test runner is the established command. Use a temporary output directory for builds if an existing `frontend/dist` must be preserved.

## Isolation and data safety

- Django's test runner creates a test database. The audit's completed targeted backend suites used an in-memory SQLite URI. Do not point test commands at the persistent database with a custom override.
- Import commands and management scripts can write production-like database/media state. Prefer tests and `--dry-run`; only execute `--apply` when a task expressly authorizes it and required backups/preconditions are satisfied.
- For media import/replacement, back up both SQLite and affected protected files, verify the backup, check attachment references and hashes, then use an atomic/idempotent command with explicit conflict behavior.
- Do not run seed commands casually. The audit found `seed_demo_courses` can force publication on rerun.
- Avoid reporting learner records, credentials, tokens, private quiz data or backup contents.

## Results recorded by Technical Audit 04

Completed on the audit snapshot:

- `manage.py check` passed.
- `makemigrations --check --dry-run` passed.
- `progress.test_enrollment_requests`: 28 passed.
- `quizzes.tests`: 48 passed.
- `studio.test_role_security`: 9 passed.
- Frontend Node tests: 34 test files passed; lint and production build passed.
- `git diff --check` passed.

Limitations: the full Django suite was interrupted without a final summary and is not a pass. Browser/authenticated flows were not verified because local servers were unavailable and no authorized read-only test session was provided. `check --deploy` failed for the active local configuration and produced deployment warnings; this does not establish production settings. No current checks were run while preparing this documentation.

## Browser and media QA checklist

- Record whether pages were actually opened in a browser, fixture or authorized user session; distinguish source review from live observation.
- Check desktop/tablet/mobile, RU/KK/EN, light/dark and reduced motion where relevant.
- Check console/network errors, loading/empty/error states, focus/keyboard access, overflow and accessible names.
- For lesson media, test authorized and denied accounts, direct endpoints, expiry/revocation, seeking/range requests, captions/transcripts, section placement and fallback behavior.
- Do not authenticate against real users or mutate real data for QA. Use isolated fixtures.

## Known test gaps

The audit flagged full-suite runtime/optional large media tests, missing live browser verification, no production scale/query measurements, no deployment topology verification, and incomplete final Lesson 115 production. See [Audit 04](../project-audit/04-technical-quality-and-bug-audit.md) for exact historical evidence.
