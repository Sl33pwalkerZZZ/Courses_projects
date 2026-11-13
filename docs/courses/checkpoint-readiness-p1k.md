# P1K — Lesson115 reproducibility and checkpoint readiness

2026-11-13. Scope: production tooling and documentation only; no rendering, installs, database writes, staging, commit or push.

## Repairs

- Generated Lesson115 npm lockfile offline in an isolated temporary directory. Existing Lesson113 root dependency/devDependency/engine specifications match115 exactly; every non-root lock package entry remained identical. npm `--package-lock-only --ignore-scripts --offline --no-audit --no-fund` performed no installation. Shared node_modules and sibling locks preserved; package.json unchanged.
- Restored the declared `npm run verify` entrypoint as read-only standard-library Python. Reuses `test_content.py` and four background-music tests; adds five focused verifier tests. Default verifies six pinned approved assets, H.264 Full HD/30, AAC stereo48k, exact frame counts, audio/video durations, subtitle pairing/placement and VTT bounds/order. No Django imports or mutations. `--source-only` explicitly does not certify final media.
- Verifier tests cover missing/corrupt files, malformed/overlapping/out-of-bounds subtitles and wrong video profile/frame count/FPS. Hash checks preserve the already-approved media; they do not substitute for new perceptual approval.
- README115 now distinguishes historical planning from completed production and documents verification, archive dependencies and render gate implications.

## Checks actually executed

- `npm run verify` in Lesson115: existing content checks passed;4 music tests passed;5 verifier tests passed;6 approved asset hashes/profiles/timing checks passed. VTT counts17/13/15.
- `npm run lint` in Lesson115: ESLint and TypeScript passed.
- `.venv/bin/python -B manage.py test courses.test_lesson115_video_integration --noinput`:4 passed using isolated test DB, destroyed afterwards; Django system check clean.
- `.venv/bin/python -B manage.py check`: no issues. `git diff --check`: passed. Index empty. Branch `design/amethyst-motion`, HEAD `e1ae750`, ahead4; every initial Git status entry retained.
- No video rerender, audio generation, media import or real-account browser testing in P1K. Owner reports successful real Firefox certificate preview/download after P1I; this is not a new agent browser result.

## Checkpoint and remaining limitations

Five-group explicit staging commands are maintained in `docs/git-p1e-checkpoint-plan.md`. Includes P1I pdf.py/test_pdf.py/report and new115 lock/verifier/tests. Existing migrations and shared113 production dependencies remain included. No staging performed.

P1J private recovery backup is outside Git and covers original DB/media/finals/production history; new P1K source changes postdate that archive. Keep a supplementary source snapshot or complete the separately approved local commits. Same-disk, unencrypted private recovery backup is not disaster recovery; copy privately to separate storage before removing any originals.

`render.mjs` hashes scripts: adding verifier sources changes that input set. Historical approvals remain untouched. Existing pinned finals need no rerender; any future final render must obtain a current hash-matched owner approval. Do not bypass the gate. Shared113 primitives, original music masters, approved narration stems and the documented MIT Silero environment remain required; no guarantee of cross-platform bit-identical synthesis/rendering.

`CERTIFICATE_PUBLIC_ORIGIN` remains unconfigured; public verification remains disabled. It no longer blocks private owner PDF preview/download. No certificate or issuer policy enabled.

## Safety and allowlist verification

Allowlist:272 unique paths in groups31/21/18/175/27; no duplicates, missing files, symlinks/node_modules, SQLite/protected storage/MP4 outputs, files over5MiB or checked private-key/token/JWT patterns. All selected Python files parse. This bounded pattern scan is not a guarantee of absence of every possible secret; staged diff review remains mandatory before each future commit. Existing three new migrations and required runtime modules are explicit in the plan; package/frontend locks and other unchanged dependencies are already tracked.

Only tracked modification outside the allowlist is intentional `config/settings.py`. SQLite SHA-256 remains `f8a79ad1a69953e3725cc58d43a85cc7459d13b0ce6aa3714a4db573e78c3c2e`; settings,115 package.json and113/114 locks match pre-task hashes. Six final asset checksums match the unchanged integration manifest. No media, DB, account, certificate or publication mutation.

P1K changes only: `video-production/lesson-115-production/package-lock.json`, `scripts/verify.py`, `scripts/test_verify.py`, `README.md`; `docs/git-p1e-checkpoint-plan.md`, this report, and `docs/project-memory/CURRENT_STATE.md`. Full working tree remains dirty from earlier authorized work. Prior local-only files are preserved.

Ready for separately owner-approved local commits, subject to staged review at execution. No functional blocker found for the source checkpoint. Full production rebuild still requires archived media/model environment and refreshed render approval; public origin remains a separate configuration issue.
