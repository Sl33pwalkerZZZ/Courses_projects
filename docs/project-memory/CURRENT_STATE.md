# Current Project State

## Latest implementation — Instructor Studio S4.1 attachment moves (2026-11-16)

- From `1a6894a` on `feat/studio-course-authoring`: existing attachment manager shows saved placement/unresolved anchors and each video's unique linked WebVTT. Eligible video/audio/SRT can move to saved student-renderable sections; video+VTT move atomically, direct VTT moves and ambiguous groups/destinations reject.
- New owned unpublished lesson attachment placement PATCH checks saved ordered headings, expected source and subtitle ID. Only after_section changes; IDs/files remain. S2.1/S3 retained; moves block pending title renames/lesson saves, media refresh preserves unsaved text. No migrations or live data changes.
-41 isolated Django tests,38/38 frontend test files, lint/build/check/whitespace passed. Actual isolated Chromium observed pair move/reopen/student preview+same track, dirty preservation, pending rename guard and localized errors at EN1440dark/RU390light/KK320dark without overflow. Mock API only; real authenticated flow remains manual. Native frontend/security reviewers ran read-only.
- SQLite/settings hashes unchanged, Course10 unpublished, Course8/live media preserved, index empty; no stage/commit/push. Exact files/API/limitations: `docs/instructor-studio/s4-1-attachment-placement.md`.


## Latest implementation — Instructor Studio S3 section inventory/rename (2026-11-16)

- On `feat/studio-course-authoring`, starting at `2050986`: existing lesson sections now show ordered media including video/VTT and unresolved anchors; plain-text lessons retain fallback. Only existing heading renaming is added, no add/delete/reorder.
- Exact title anchors remain the model contract. Explicit rename intents are validated and applied through the existing atomic lesson PATCH, updating body/source sections/image placements/all matching attachment anchors together, preserving media IDs/files. Stale/ambiguous/colliding references reject; owner/published locks retained. No migrations.
- S2.1 drafts/dirty confirmation/save races preserved, including raw invalid title input and newer renames while saving. Display-only stale-prop aliases are attachment-ID scoped; reused headings cannot redirect another asset.
-32 isolated Django tests,37/37 frontend test files, lint/build/system/whitespace checks passed. Actual isolated Chromium observed rename/refresh/stay/failed save/pending save/reopen/student video+VTT placement/plain fallback; EN1440dark/RU390light/KK320dark without page overflow. Mock API only; no real authenticated Studio verification. Native frontend/security read-only reviews ran.
- Working SQLite/settings checksums unchanged, Course10 unpublished, Course8/live media/data untouched. No stage/commit/push. Details/files/manual checks: `docs/instructor-studio/s3-section-renaming.md`.


## Latest implementation — Instructor Studio S2.1 (2026-11-16)

- Current branch `feat/studio-course-authoring` was created during S1 from local checkpoint e669aaa (five P1O commits complete). Existing local settings/untracked assets preserved. S1 discovery is in chat; no source changes were made during that audit.
- S2.1 retains same-course/path/session workspace data during background refresh, preserving keyed lesson drafts while outline/media props update; refresh errors offer retry. Initial load/permission/session boundaries retained.
- Lesson saves acknowledge submitted baseline only: failed saves retain edits; newer typing during PATCH stays dirty. Localized close/switch/router leave confirmation and beforeunload added. Early inert POP dispatcher in main.jsx is required before BrowserRouter; see DECISIONS and `docs/instructor-studio/s2-1-draft-stability.md`.
-36/36 frontend test files, lint(no warnings), build and whitespace checks passed. Actual isolated Chromium fixture reproduced before loss and passed after flows (refresh/upload/reorder/stay/discard/save races/Back; EN1440,RU390,KK390). Mocked API only; real authenticated Studio/backend flow and native prompt appearance remain manual. MCPFirefox unavailable. No backend/DB/settings/course/media/assessment changes, staging, commit or push.


## Latest checkpoint update — P1M whitespace safety (2026-11-13)

- P1L staged272 approved files but final cached whitespace check found25 findings in13 files. P1M removes only whitespace from11 unpinned source/docs/transcript/storyboard files; preserves2 Lesson114 VTT byte-for-byte because integration/production manifests and protected attachments pin their hashes.
- New root `.gitattributes` uses2 exact root-anchored paths with only `whitespace=-blank-at-eof`. No global whitespace disable, hash rewrites, media changes or approval rewrites. Existing render gates remain authoritative.
- Planned index now273 paths in5 groups31/21/18/176/27. Small verified pre-change archive stored privately outside repo. No commits/push/publication/DB/settings changes. Cached whitespace check passes;9MP4/5VTT source and14 protected-file hashes unchanged;27 isolated integration tests and115 verifier passed. Additional114 production suite:5pass/1pre-existing obsolete snapshot assertion failure (before snapshot compared against approved after canonical). Do not alter historical snapshot or approved content to satisfy it; review test separately before commits.


## Latest implementation update — P1K reproducibility (2026-11-13)

- Lesson115 now has an offline-generated npm lockfile preserving the exact existing Remotion4.0.540 graph; no installation/upgrades or shared node_modules changes. Restored read-only `npm run verify` plus5 verifier regressions; source-only mode explicitly excludes final-media QA. Existing content checks,4 mixer tests,5 verifier tests,6 pinned MP4/VTT assets and ESLint/TypeScript passed.4 isolated Django Lesson115 integration tests passed; system check clean.
- Checkpoint plan retains5 groups,272 unique explicit paths (31/21/18/175/27), including P1I PDF source/tests/report and115 lock/verifier. No stage/commit/push. P1J recovery archive predates these P1K sources; preserve an incremental source snapshot or separately authorize checkpoint commits.
- Approved videos and hashes unchanged. Adding scripts changes the render gate input set: historical approvals preserved; future rendering requires a new matched owner approval. No rerender needed for existing finals. External music/narration/model environment remains an archive dependency.
- Owner reports real Firefox certificate viewing/downloading successful after P1I; not a new automated browser check. Public verification/origin configuration still separate and disabled. DB/settings/course/publication/policies unchanged. Details: `docs/courses/checkpoint-readiness-p1k.md`.


## Latest implementation update — P1I optional verification for private PDFs (2026-11-13)

- Owner PDF delivery no longer depends on public verification configuration. Existing download route accepts `?preview=1` for inline, defaults to attachment; authentication/ownership, revoked/evidence guards and private/no-store retained. No URL is derived from Host. QR/link is omitted unless verification is enabled and an explicit valid origin is configured. Stored certificate name/course/issuer/date and all records unchanged; issuance stays disabled.
- Profile now provides JWT-backed in-page PDF preview/close and download, scoped to session generation with Blob URL cleanup; hides unavailable public verification links using backend availability metadata. RU/KK/EN preserved. Native PDF viewer content in real Firefox remains unverified; headless iframe was blank, while actual generated PDF was parsed/rasterized successfully and browser download bytes matched.
-62 isolated Django tests:61pass/1expected skip;10 focused certificate tests;35 frontend files; lint/build/system/whitespace passed.6 browser fixture locale/width combinations checked controls, bytes, errors, logout and stale response rejection; no real API/accounts. Security reviewer found no confirmed defect. Live DB hash unchanged f8a79ad1a69953e3725cc58d43a85cc7459d13b0ce6aa3714a4db573e78c3c2e. Details/manual instructions: `docs/courses/certificate-pdf-p1i.md`. No settings/DB/media/course/policy modifications, issuance, staging/commit/push. P1G's earlier “origin blocks PDF” limitation is superseded; public verification/global gates remain.

## Latest implementation update — P1G private issued-certificate reads (2026-11-13)

- Authenticated own-list and existing guarded PDF download now use an ungated private read base, independent of issuance. Public verification, eligibility/status and API mutations remain feature-gated. Disabled-mode Admin policy writes/issuance/revocation are blocked; issuance and revocation services both enforce the flag. Existing certificate-name workflow and eligibility rules unchanged; no new routes/schema/frontend changes.
- Course8's existing owner can retrieve its stored card without reissuance. Real browser not tested. Local PDF remains blocked by missing trusted CERTIFICATE_PUBLIC_ORIGIN; tests use an explicitly synthetic trusted origin. Public verify/QR route remains unavailable in disabled mode by design. See `docs/courses/certificates-read-only-p1g.md` for the API matrix and manual checks.
- P1F backup reverified. Live database hash f8a79ad1a69953e3725cc58d43a85cc7459d13b0ce6aa3714a4db573e78c3c2e unchanged.57 isolated Django tests:56 passed/1 expected skip;2 frontend certificate/session files passed; system/whitespace checks passed. Native security reviewer found no confirmed defects. No settings/DB/media/course/policy mutations, issuance/revocation, publication, staging, commit or push.

## Latest diagnostic/fix update — P1F existing certificate visibility (2026-11-13)

- Course8 issued snapshot remains present, unrevoked, owned by user2 (the intended `student` account); current browser identity is unverified. Global `CERTIFICATES_ENABLED=False` closes certificate APIs with404. Profile incorrectly mapped that to an empty list; it now shows localized certificate-section unavailability, preserving the global gate and all issuance/authorization rules. Older snapshots do not require reissuance or new name confirmation merely to be listed when reads are available.
- Fresh consistent SQLite backup and read-only historical comparisons are documented in `docs/courses/missing-certificate-p1f.md`. Live hash f8a79ad1a69953e3725cc58d43a85cc7459d13b0ce6aa3714a4db573e78c3c2e remained unchanged throughout P1F; integrity/FK checks and backup counts passed. Name/confirmation fields differ from an available November11 backup, consistent with the owner's action; exact explanation of every historical file-byte change is not proven.
-44 isolated Django tests,8 focused certificate-render tests,57 session tests,35 frontend test files, lint/build, system/whitespace checks passed. Playwright MCP Firefox remains unavailable; actual authenticated Profile not tested. No config, backend runtime, model/schema, policy, course/content/media or real record changes, certificate issuance/revocation, staging, commits or pushes. Global gate/read-only existing certificate policy remains an owner decision for a separate task.

## Latest implementation update — P1D rubric UI validation (2026-11-12)

- Final-project review now validates four whole-number scores0–25 before confirmation/POST. Raw invalid input remains editable without rounding/clamping; empty input is not replaced by zero. Localized RU/KK/EN errors are associated with invalid fields, and attempted decisions focus the first invalid field. Existing backend validation, scoring rules, feedback, statuses and action error handling remain unchanged.
- Verification:8 focused assignment-review tests;35/35 frontend files; lint/build;16 isolated Django review/submission tests; system and whitespace checks passed. Existing Chromium fixture passed12 locale/theme/desktop-mobile combinations including blocked invalid requests, focus, approved/rejected payloads and simulated backend errors; zero real API calls or page exceptions. Vite QA WebSocket diagnostics occurred; this is not real-account verification. Native frontend reviewer reported no confirmed defects.
- Read-only real-account checklist and exact changed files: `docs/courses/module-6-ui-readiness.md`. Real authorized student/instructor browser checks remain outstanding. Working SQLite checksum unchanged; no backend, migrations, course/content/media/policy/publication changes, staging, commit or push. Previous P0–P1C and all unrelated working-tree changes preserved.

## Latest implementation update — P1B CourseDetail cache boundary (2026-11-12)

- `CourseDetailView.finalize_response` now sets `Cache-Control: private, no-store` on authenticated responses and all errors, including rejected credentials and access denials. Every CourseDetail variant also varies on `Authorization` and `Cookie`, including anonymous successes. Anonymous published content retains its existing cache policy; the catalog is unchanged. The enrolled-draft queryset, schemas and existing private/no-store instructor preview and lesson responses are preserved. No Django cache middleware is configured in the inspected middleware list. This prevents future compliant cache storage; previously stored responses are not retroactively removed by a new header.
- Added eight isolated cache-boundary tests: anonymous public response, authenticated public response, enrolled draft, owning author preview, unauthorized draft/preview, account switch/logout, invalid JWT and HEAD. Together with progress/enrollment/preview authorization regressions, 52 Django tests passed on an in-memory database with temporary media roots; system checks passed. Relevant frontend session-isolation, lesson-workspace and stability tests passed (3 files). Native `security_reviewer` performed an independent read-only source review and found no confirmed defect; it did not run tests or inspect database records. No frontend files changed, so lint/build were not rerun in this backend-only phase. Whitespace checks passed.
- Real authenticated browser verification remains unavailable: Playwright MCP cannot launch its configured Firefox because the executable is absent, and no authorized test session was supplied. No browser installation, login, credential extraction or mutating student action was attempted. P1A's fixture coverage is not evidence of a real-account journey.
- Manual read-only verification: in the student's existing normal browser session open `/lessons/100`; reload to exercise session restoration; check six modules and sixteen lesson links, expand Module 6 and navigate to `/lessons/116`; compare progress with the existing account history without completing anything. Inspect videos/subtitle controls on `/lessons/113`, `/lessons/114`, `/lessons/115`; do not submit assignments/quizzes or mark lessons completed. At 320/390px expand the curriculum and confirm it does not overlay the article. In Network verify authorized CourseDetail is 200 with private/no-store and Vary Authorization/Cookie; do not copy token headers. Check for unexpected 401/403/404 and console errors. Login itself and media/subtitle activation remain unverified here.
- Working SQLite SHA-256 before/after is unchanged (`3c45b29b552d7b4ef5f9b78c672c8146317b42c6ab0257cc2c2ef4e105e4ecb3`). No database, settings, migrations, content, media, publication or certificate-policy changes, staging, commits or pushes. Module 6 end-to-end testing can proceed after an authorized session is available; certificate issuance/publication is not enabled by this patch.

## Latest implementation update — P1A independent curriculum and progress (2026-11-12)

- LessonView now loads curriculum and enrollment progress independently. Each resource has its own loading/error state and retry; simultaneous retries are coalesced. A progress failure no longer hides the curriculum, and an outline failure no longer discards confirmed progress. Network failures retain and label the last confirmed progress; 401/403 remove stale access data and remain explicit errors. Missing progress never becomes 0% or an incomplete lesson marker.
- The workspace is keyed by lesson, session generation, and preview mode. Disposed/canceled requests cannot update replacement state. Instructor preview only requests its authorized curriculum and does not request learner progress. Existing P0 API/session code and backend authorization remain unchanged.
- Read-only working SQLite verification confirms Course 10 is unpublished with modules 34–37, 39–40 and 16 lessons (100–111, 113–116). No curriculum filtering depends on progress availability or publication assumptions in React.
- A real isolated Chromium fixture exposed an existing mobile CSS conflict: the 340px curriculum height limit combined with visible overflow let links overlap lesson material. The narrow fix restores natural-height compact disclosures below 900px and bounded scrolling at the intermediate layout. Final fixture QA passed 24 width/locale/theme combinations (1440/768/390/320; RU/KK/EN; light/dark), including all 16 links, progress-only keyboard retry, last-link focus, overflow, and sidebar/article geometry. No page exceptions or real API requests occurred. Screenshots and the temporary harness are under `/tmp/ai-courses-p1a-*` and `/tmp/ai_courses_p1a_qa.cjs`; this was not real-account testing. Playwright MCP itself could not launch its configured Firefox; the existing cached Chromium/Playwright-core was used without installing dependencies.
- Verification: 42 focused lesson-workspace tests passed; the complete 35-file frontend suite, lint and production build passed; 44 Django progress/enrollment/preview authorization tests passed on an isolated in-memory database, including six-module enrolled-draft visibility and denial to another student. Whitespace checks passed. The working SQLite checksum is unchanged; no content, publication, media, certificate-policy, configuration or migration changes, staging, commits or pushes occurred.

## Latest implementation update — frontend P0 session and refresh fixes (2026-11-12)

- `frontend/src/api.js` now validates the originating session for authenticated course-detail responses, including enrolled draft courses. The catalog remains anonymous; genuinely anonymous public responses remain usable across account changes. Same-account token rotation preserves the existing session generation.
- Refresh-only requests recover access before sending an authenticated request. Recovery shares the existing generation-scoped refresh flight; queued requests and delayed refresh results cannot adopt another account. Failed refresh clears the failed session and permits one anonymous fallback only for the explicit public GET/HEAD allowlist. Protected requests never fall back anonymously, and retries remain bounded.
- Regression tests reproduced failures before the patch. Completed verification: 56 session-isolation tests and 17 API stability tests passed; all 35 frontend test files passed; lint and production build passed; 33 Django enrollment/preview authorization tests passed using an isolated in-memory database; `git diff --check` passed. No real-account browser verification was performed.
- Remaining backend follow-up: enrolled draft `CourseDetailView` responses should explicitly use private/no-store caching. This P0 patch makes no backend, database, migration, course-content, media, or publication changes. The working SQLite checksum is unchanged from the audit. Existing unrelated working-tree changes remain preserved; no staging, commit, or push occurred.

## Latest implementation update — Module 6 foundation and certificate-name confirmation (2026-11-11)

- Added a student-owned certificate-name confirmation workflow in the current worktree. `users.0002_user_certificate_name_and_more` adds the normalized display-name field and server-side confirmation timestamp; `/api/my/certificate-name/` only addresses the authenticated student, and issuance snapshots only an explicitly confirmed value. The Profile UI and RU/KK/EN translations are present. This migration is **not applied** to the working SQLite database.
- Added `courses/management/commands/import_media_module_6.py` and `courses/management/media_module_6.json`. The default dry run proposes exactly one final-assessment module/lesson, one generic assignment, one draft 15-question/60-choice single-answer quiz at 70%, and one disabled scoped certificate policy. It has **not** been applied; Course 10 still has five modules and 15 lessons and remains unpublished.
- Rehearsed the three pending migrations — `certificates.0005_coursecertificatepolicy_required_lessons`, `progress.0005_assignmentsubmissionattachment_and_more`, and `users.0002_user_certificate_name_and_more` — against a fresh SQLite backup in `/tmp`, not the working database. The rehearsal passed integrity and foreign-key checks before/after, preserved reference counts, and made `/api/courses/` return HTTP 200 when pointed to the migrated copy.
- Focused isolated Django suite: 126 tests passed. Frontend certificate and assignment-submission tests passed; lint, production build, Django check, migration consistency, and whitespace check passed. No authenticated browser journey was run.
- The working `db.sqlite3` still lacks the three migrations, so its `/api/courses/` runtime error remains expected until the owner approves applying those reviewed migrations. Preserve the existing `backups/pre-migrations/db-before-migrations-20261111-091224.sqlite3` backup.

## Module 6 verification update — live records and rubric review (2026-11-11)

- The working database now reports the three migrations applied and contains Course 10 Module 6 ID 40 with one assessment lesson ID 116, one assignment, draft Quiz ID 5 with 15 single-choice questions and 60 choices, and a disabled Course 10 policy selecting exactly the 15 lessons in Modules 1–5. Course 10 remains unpublished; no Module 5 or Course 8 records were changed by this verification.
- The approved source and repository history define one Module 6 lesson; no canonical multi-lesson Module 6 plan was found. The lesson combines practical submission, final quiz, and completion/certificate guidance as separate platform entities.
- Final-project instructor review now accepts and stores four server-validated rubric scores (0–25 each) in the existing review-history JSON, returns the rubric total to instructor/student views, and still uses the existing attributable approve/reject/reopen workflow. No schema migration was needed for rubric scores.
- Focused verification after this change: 49 Django Studio/submission/certificate/import tests passed; frontend assignment-review, assignment-submission and certificate tests passed; lint, build, system check, migration consistency and whitespace checks passed. No authenticated browser session was available.

## Latest implementation update — certificate lesson scope (2026-11-10)

- `CourseCertificatePolicy` now has an explicit `required_lessons` selection. A nonempty selection is the exact lesson completion scope; when it is empty, `require_all_lessons=True` retains the legacy all-course-lessons behavior. The policy admin form rejects lessons from other courses, and server eligibility fails closed if an invalid cross-course relation is present.
- Added migration `certificates.0005_coursecertificatepolicy_required_lessons`. It was exercised by Django's disposable in-memory test database only and was **not applied** to the working SQLite database. `progress.0005` remains untouched and unapplied to the working database.
- No Course 10 policy or Module 6 records were created; Course 10 remains unpublished. Course 8 policy/data were not changed; the legacy fallback remains covered by isolated tests.
- Focused certificate/admin tests: 31 passed. Frontend certificate test file, lint, production build, Django system check, migration consistency check, and `git diff --check` passed. The frontend labels the scoped requirement in RU/KK/EN.
- No files were staged, committed, or pushed. Existing unrelated WIP remains preserved.

**Last verified:** 2026-11-10 (Lesson 115 V1–V3 Full HD final MP4s and WebVTT sidecars verified and integrated into Lesson 15; Course 10 remains unpublished). See the final record in [`V2_V3_COMPARATIVE_QA.md`](../../video-production/lesson-115-production/V2_V3_COMPARATIVE_QA.md).
**Branch:** `design/amethyst-motion`
**HEAD:** `e1ae750` — `test: document and validate the post-redesign checkpoint`
**Ahead of origin:** 4 commits. No staged changes were shown at the snapshot.

## Recent commits ahead of origin

| Commit | Scope |
|---|---|
| `28ff315` | Protected instructional video infrastructure, grants/range delivery, tests/docs |
| `ca684c3` | Course 10 Module 5 source/import package |
| `42455ca` | Cinematic frontend redesign Phases 1–3 |
| `e1ae750` | Post-redesign checkpoint validation/documentation |

Origin ref in the audit was `5cf26f9`, finalizing Module 4 Silero audio. No fetch/push was performed for this memory task.

## Working tree — preserve as-is

Tracked modifications:

- `AGENTS.md` — project-memory integration guidance; preserve.
- `config/settings.py` — intentional local change. Do not read into reports, overwrite, stage or commit.
- `courses/management/commands/import_media_module_5.py`
- `courses/management/media_module_5.json`
- `docs/courses/media-module-5-assets.json`

`git diff --stat` at the pre-Lesson-115 planning snapshot: 5 tracked files modified; inspect current diff before any later staging. No staged files were reported.

Untracked top-level status entries included:

- `.agents/` (large copied Remotion skill material; preserve and do not assume it is application source)
- `.local-cinematic-qa/`, `.local-video-test/`, `.vite/`
- `course_assets/module_4/` experimental audio, provenance/evaluation data, scripts and candidate directories; do not treat all candidates as approved deliverables
- `course_assets/module_5/m5-l13-v1-production/narration-preview.wav`
- Lesson 113/114 integration commands, JSON snapshots, tests and completion/planning docs under `courses/` and `docs/courses/`
- Module 4 audio scripts, legacy/provenance/license audit files and tests
- `docs/project-audit/` (four audit reports at this checkpoint)
- `docs/frontend-unslop-audit.md`, `skills-lock.json`, `video-production/`
- `video-production/lesson-115-production/` — new planning-only package with three Russian narration drafts, three timecoded storyboards, asset/Remotion/recording/audio-subtitle/QA guidance. No recording, narration audio, render, MP4, VTT, database attachment or import was created.
- `video-production/lesson-115-production/PRODUCTION_READINESS.md` — read-only host/tool and asset readiness audit. Actual CapCut Desktop and OBS were not detected in checked locations; authentic L15 source project/footage and approved L15 narration are missing from inspected project directories. Remotion/FFmpeg are locally available with the existing NVM PATH setup.
- Unusual file named `e modules 2-4 and inline learning media"` — suspicious/captured output-looking name; its purpose was not established. Preserve for owner review.

Before this memory work, the status had 60 entries using compact `git status --porcelain`. After creating this documentation, it has 61 entries; the only additional status path is the new `docs/project-memory/` directory. Recursively expanding untracked directories includes many more files. The untracked production tree is mixed source/output/cache/QA and must be reviewed path-by-path. Do not use broad add/clean/reset operations.

Exact compact untracked paths at the post-documentation snapshot:

```text
.agents/
.local-cinematic-qa/
.local-video-test/
.vite/
course_assets/module_4/m4-audio-production.json
course_assets/module_4/m4-l1-f1-natural-narration.mp3
course_assets/module_4/m4-l1-f1-synthetic-narration.wav
course_assets/module_4/m4-l12-ru-roman-room-after-v2.wav
course_assets/module_4/m4-l12-ru-roman-room-before-v2.wav
course_assets/module_4/m4-l2-f1-corrected-transcript.txt
course_assets/module_4/m4-l2-f1-speech.wav
course_assets/module_4/m4-l2-f1-synchronized.srt
course_assets/module_4/m4-l3-f1-clean-reference.wav
course_assets/module_4/m4-l3-f1-original.wav
course_assets/module_4/m4-l3-f1-processed.wav
course_assets/module_4/m4-room-noise-v2.json
course_assets/module_4/voice_candidates/README.md
course_assets/module_4/voice_candidates/evaluation.json
course_assets/module_4/voice_candidates/generate_candidates.py
course_assets/module_4/voice_candidates/lesson12-self-contained-dsp/
course_assets/module_4/voice_candidates/prepare_filter_v3.py
course_assets/module_4/voice_candidates/prepare_room_noise_v2.py
course_assets/module_4/voice_candidates/prepare_self_contained_dsp.py
course_assets/module_4/voice_candidates/requirements-evaluation.txt
course_assets/module_4/voice_candidates/ru_roman_refined/
course_assets/module_4/voice_candidates/test_candidates.py
course_assets/module_4/voice_candidates/test_filter_v3.py
course_assets/module_4/voice_candidates/test_roman_module4.py
course_assets/module_4/voice_candidates/test_room_noise_v2.py
course_assets/module_4/voice_candidates/test_self_contained_dsp.py
course_assets/module_4/voice_candidates/v5_cis_base_nostress-ru_marat.wav
course_assets/module_4/voice_candidates/v5_cis_base_nostress-ru_roman.wav
course_assets/module_4/voice_candidates/v5_cis_base_nostress-ru_zhadyra.wav
course_assets/module_5/m5-l13-v1-production/narration-preview.wav
courses/management/commands/integrate_lesson113_videos.py
courses/management/commands/integrate_lesson114_videos.py
courses/management/lesson113_quality_v2.json
courses/management/lesson114_quality_v2.json
courses/test_lesson113_integration.py
courses/test_lesson114_integration.py
courses/test_module4_audio.py
docs/courses/lesson-113-integration-complete.md
docs/courses/lesson-113-quality-v2-integration-plan.md
docs/courses/lesson-114-integration-complete.md
docs/courses/media-module-4-legacy-assets.json
docs/courses/module-4-audio-demonstrations.md
docs/courses/module-4-cleanup-inventory.json
docs/courses/module-4-elevenlabs-provenance.json
docs/courses/module-4-rnnoise-COPYING.txt
docs/courses/module-4-rnnoise-license-audit.json
docs/frontend-unslop-audit.md
docs/project-audit/
docs/project-memory/
e modules 2-4 and inline learning media"
scripts/generate_module_4_audio.py
skills-lock.json
video-production/
```

## Latest verified update — Lesson 115 final production and integration (2026-11-10)

- Course 10 / Module 5 / Lesson 115 now has exactly six protected attachments: three MP4s and three corresponding WebVTTs. Pair placements are after section 3 (attachment IDs 17–18), section 5 (19–20), and section 7 (21–22). The nine section anchors and lesson text hash were verified unchanged.
- Final files are in `video-production/lesson-115-production/out/final-bgm/`. V1 was preserved byte-for-byte from the owner-approved BGM candidate. V2 and V3 were rendered Full HD at 30 FPS, then muxed with the approved Minimal Tech Ambient configuration; their decoded video frames match their full-quality pre-mux renders.
- Final MP4 SHA-256 values: V1 `22a00b5d27549f993ef9c1c2d8205fbdf6ba28cbbe76e68ad547dcf0f4ae059f`; V2 `704519231eaf4dbc9733f1b4aa2c3fd57630ab63d4ce6601bd056885c031a2ae`; V3 `f8a08dc12683c102036e38e9627b14689b69e27567117315c2229a273ce298f3`. The VTT files are unchanged from their prepared subtitle sources.
- Verified pre-write backup: `.local-course-backups/lesson115-final-integration-20261109-211343-ef8297e3`. SQLite integrity is `ok`, foreign-key check has zero violations, and the snapshot records zero Lesson 115 attachments before integration. It includes protected-media and source-input archives. Earlier incomplete backup attempts remain preserved and were not used.
- The importer now reports `KEEP 6` with no changes. Focused integration and video playback tests, Django checks, frontend lint/build, SQLite integrity/FK checks, and an actual-data attachment-layout utility check pass.
- Real authenticated Firefox playback/subtitle activation was not verified in this session: no authorized browser session or Playwright MCP tool was available. Course 10 remains unpublished; no commit or push was made.

## Feature state from latest audits

- Course 10 (`ai-media-content`) had five modules and 15 lessons in the 2026-11-09 read-only snapshot. It was unpublished; do not publish without explicit approval.
- Lessons 113 and 114 video attachments were integrated in the audited database snapshot. Lesson 114 also had two VTT tracks. Their authenticated browser experience was not verified.
- Lesson 115 (lesson ID 115) has three structured objectives and nine sections. V1 (`m5-l15-v1-export-check`) has its original full-quality no-music master plus a separate, technically verified BGM listening candidate at `video-production/lesson-115-production/out/final-sentence/m5-l15-v1-bgm-candidate.mp4`; the source master and VTT are unchanged. Candidate QA is in `video-production/lesson-115-production/V1_PRODUCTION_QA.md`. Human listening/author approval remains pending; it is not attached. V2/V3 compositions, narration, timings, subtitles and BGM audio stems are present, but neither video has been rendered or visually reviewed. The 2026-11-09 database audit snapshot found no Lesson 115 media attachments; verify before any later import. Course 10 remains unpublished.
- Module 6 has no existing content or approved assessment design. Obtain author decisions before implementation.
- Course 8 is an independently published course with its own progress/quiz/assignment/certificate state. Preserve it.
- Project audit reports 01–04 are complete and linked from [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md).

## Known issues and limitations

- Full Django test run was interrupted before a final result; it is not a passing result.
- Completed targeted tests in Audit 04: 28 enrollment, 48 quiz, 9 Studio-role tests; 34 frontend test files; lint/build/system/migration consistency checks passed at that time.
- Browser/authenticated flows were not verified in Audit 04 because servers were unavailable and no authorized test session was supplied.
- Local `check --deploy` reported a development email-backend error and seven deployment warnings. Production settings/topology are unknown; do not blindly change local settings.
- Audit 04 found Studio query growth and no identified cleanup for expired/revoked playback-grant rows. Impact/current row counts were not measured.
- Current settings/importer/manifest modifications were not re-reviewed in this memory task beyond status and diff summary.
- Host snapshot for the readiness audit: LMDE 7 / Debian 13 x86_64 VM, 8 vCPUs, 7.8 GiB RAM (3.1 GiB available then), 19 GiB filesystem space available then; Node 24.21/npm 11.19 in NVM but not on default PATH; Remotion 4.0.540 and FFmpeg/FFprobe 7.1.5 available. CapCut/OBS availability is not established outside the searched locations.

## Immediate next action

The owner has approved the V1 Minimal Tech Ambient music candidate and mix. V2 and V3 preview-only renders now exist at `video-production/lesson-115-production/out/previews-bgm-v1/`; comparative technical and representative-frame QA is recorded in `video-production/lesson-115-production/V2_V3_COMPARATIVE_QA.md`. V2/V3 still need owner visual/listening review. Do not render full-quality finals or attach any Lesson 115 media until separately approved. Arrange authenticated Lesson 114 verification separately. Before Module 6, request an author-approved structure and grading policy. Keep Course 10 unpublished throughout unless the owner explicitly changes that boundary.

## Context restoration links

- Stable overview: [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)
- Architecture and source locations: [ARCHITECTURE.md](ARCHITECTURE.md), [FEATURE_FILE_MAP.md](FEATURE_FILE_MAP.md)
- Content, database and media: [COURSE_CONTENT_MAP.md](COURSE_CONTENT_MAP.md), [DATABASE_MAP.md](DATABASE_MAP.md), [MEDIA_PIPELINE.md](MEDIA_PIPELINE.md)
- Verification and decisions: [TESTING_QA.md](TESTING_QA.md), [DECISIONS.md](DECISIONS.md)
- Prioritized work: [ROADMAP.md](ROADMAP.md)
- Root AGENTS integration proposal: [AGENTS_INTEGRATION_PROPOSAL.md](AGENTS_INTEGRATION_PROPOSAL.md)
