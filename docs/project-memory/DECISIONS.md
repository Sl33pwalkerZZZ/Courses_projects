# Architectural and Project Decisions

## 2026-11-26 — owner-authorized release rotation and production-only beta

- Supersedes the earlier active-key push blocker: remove the exposed signing key from current source, require a private production environment secret and never accept the historic key as fallback. Leave already-public history unchanged. Local development uses a stable private ignored mode600 key; preserve unrelated local settings changes outside the commit. Production entrypoint is config.production, fails closed, disables DEBUG/issuance, isolates private media and uses SMTP.
- One release-branch push is authorized after security review. A revoked key in existing public history alone is not a release blocker. No all-ref/mirror/force push.
- Course10 beta publication is authorized only after actual deployment, private database/media restoration and smoke tests, using existing manual Studio acknowledgements and admin approval. No local SQLite publication and no certificate activation. See deployment handoff for exact gates and known operational limitations.

## 2026-11-26 — bounded Groq guide and release safety gate

- Owner prioritizes the minimal AI Guide and release over D6–D8. Reuse lesson authorization and a database title/text allowlist; never accept client lesson content or query quiz keys/submissions. Each question is a stateless Groq call; chat stays in React state. This is not RAG. Keep RU/KK/EN, omit reasoning, sanitize provider errors and prohibit response caching. The basic 12/min cache throttle is not a distributed cost quota; deployment needs shared cache and provider budget controls.
- `/api/ai-guide/` avoids reserving a valid course slug. The guide needs no sibling lesson key because LessonWorkspace already resets by lesson/session. Identical Guide/Quiz keys caused real duplicate DOM and were fixed before committing.
- Release push authorization depends on whole-history safety. The active tracked Django signing key is already origin-exposed: do not push, rewrite history or change settings silently. Production externalization/rotation needs a separate owner decision, and Groq needs valid backend credentials. Preserve private env files and backups outside Git.

## D5 — discovery and course information hierarchy (2026-11-25)

- Owner approved preserving the landing hero/ASCII while replacing the catalog grid with horizontal discovery cards, an open course title, a separate access panel and a continuous curriculum. Preserve Obsidian/Frost/Aqua, D3.3 materials and D4 behavior; no new dependencies or theme implementation.
- The current public course API has no cover image or distinct learning-outcome fields. Use original, decorative SVG geometry and actual direction/title/description/counts, never invented thumbnails, progress, ratings or publication badges. Keep protected lesson links dependent on confirmed enrollment; instructor drafts still use Studio preview.
- D4 was explicitly accepted and committed as88a9b85. D5 stays uncommitted for owner visual acceptance; D6 and publication/certificate changes require separate tasks. See docs/design/D5_CATALOG_COURSE_REDESIGN.md for exact evidence and limits.

## D4 — state-preserving theme reveal and snapshot lifecycle (2026-11-25)

- Owner authorized D4 separately; preserve D3.3 materials/palette and all application state. ThemeProvider changes context/dataset only; no subtree cloning/remount/routes. Native reveal is runtime-enhancement, not a permission or session change.
- Original48-point contour originates at actual toggle;720msdesktop/560mobile. Unsupported/rejected native snapshot or pseudo-animation uses420ms CSS color fallback +smallripple. Reduced/hidden immediate. Generations invalidate late callbacks; rapid parity retained via requestedTheme ref.
- Explicitly cancel filled WAAPI effect and skip/release native snapshots on completion; finished cleanup is scoped to its own active transition. Preserve focus and live media. Pause liquid physics duringreveal; short blend duringfallback.
- ClosedSQLite test error reproduced only with file-backed TestCase after response.close; request_finished closes atomic connection. AffectedtestalonePASS and standard isolatedmemory36PASS. No production code/settings change to suppress it.
- Native motion reviewer unavailable: nativefrontend reviewer substituted; combined contour/boundary evidence accepted within1000x760login only, not a generalFPS guarantee. Owner hardwarebrowser visual acceptance remains separate.

## D3.3 — selective optics and explicit fallback (2026-11-25)

- Owner confirmed transparent shells/cards/navigation and dense reading/assessment/forms; preserve composition. A workspace38%, B panels48%, C small floating backplate28%, D reading96%. Nested Studio B panels tint one shared A backdrop rather than repeating filters.
- Original deterministic edge-normal PNG + SVG displacement on header pseudo-element only; foreground is outside filter. Chromium desktop enhancement is conditional; Firefox/mobile/reduced use64/68% frosted fallback. No third-party code or dependencies.
- Treat computed CSS as insufficient visual evidence. Chromium production-map pixel A/B confirmed refraction. Native Firefox143 headless SWGL does not demonstrate ordinary blur; document readable tint/edge fallback and require owner hardware-browser review. No sustainedFPS claim from computation microbenchmark.
- Materials report and screenshots are review evidence, not owner approval. D4 starts only after separate owner approval.

## D3.2 — shared authoring shell and bounded visual motion (2026-11-25)

- Keep approved Obsidian/Frost/Aqua. Replace rigid SVG ribbons with original low-resolution Canvas light-field deformation. Continuous effects have hidden/reduced cleanup and explicit lower mobile budget; targetFPS is not measured performance guarantee.
- OpticalCompanion uses pointer geometry only, never typed data. All Studio routes share a wide persistent shell with stable Outlet; no route remount keys added, no editor/API/permission rules changed. Main shell is brought forward from D7; D7 now means remaining refinement/finalverification.
- Distinguish68/72% frosted layering from genuine optical refraction. Owner explicitly plans D3.3 for transparency, edge distortion/specular/material layering with Firefox/performance fallback. Referencefreefrontend fetch403 means no license/code reuse assumed.
- Owner roadmap: D3.2,D3.3,D4–D8,F1metadata,F2certificates,F3Git/integration,F4ownerpublication,F5RAG+LLMtutor,F6production,F7HTTPSlaunch. Tutor may explain/source-ground/formatively guide, never expose assessment keys or replace instructor grades. Additional courses wait until v1.0 launch; infrastructure choices require limits/institutional-use/cost/security/reliability review. These are future stages, not executed decisions/configuration.

## D3.1 owner-directed material and motion (2026-11-25)

- Owner explicitly supersedes Graphite/Lime with Obsidian/Frost/Aqua and controlled Liquid Glass. Existing product truth, all access rules and course state remain fixed. Preserve semantic success/error colors; reader/form controls stay legible and predominantly opaque.
- Original continuously rotating ASCII torus is anchored to hero; one separate bounded passive parallax supplies scroll continuity. SVG currents use transform animation, pause hidden, static reduced-motion fallback; no WebGL/new dependency or borrowed ASCII code.
- Studio overview demonstrates sidebar/metrics hierarchy; deeper authoring and complete D7 redesign remain out of scope. Theme persistence unchanged; D4 transitions require separate approval.

## D3 original ASCII and scoped composition (2026-11-25)

- Reuse D2 typography/palette while replacing the landing topology; preserve separate catalog/card/business contracts for D5. Primary destination is available courses, confirmed by owner; no fabricated platform statistics/reviews or built-in AI generation claims.
- Original seeded glyph geometry, event-driven Canvas, natural passive scrolling, static pre fallback for mobile/reduced-motion/no-canvas. No external ASCII art/code/WebGL packages; React Bits/ascii libraries used as references only after license inspection.
- Normalize IBM Plex Mono OFL text line endings only, preserving wording and upstream license hash alongside normalized local hash; never alter font binaries to resolve whitespace.

## D2 semantic foundation and local typography (2026-11-24)

- Owner-directed Graphite & Lime replaces the mandatory future Amethyst visual direction. Preserve existing --v2-* token compatibility and index aliases while introducing --color-* semantic roles; no wholesale page/layout migration in D2.
- Use self-hosted OFL Noto Sans400–800 plus IBM Plex Mono400. Exact evaluated Manrope file lacks required Kazakh characters; do not rely on per-character system fallback. Keep licenses, source URLs, exact hashes and cmap regression coverage with fonts.
- Lime fill always has dark ink; light links/focus/progress use deep green. Separate decorative and meaningful control borders. No new dependencies, public demo route, business-state changes or new motion loops. Future ASCII/theme transitions remain D3/D4.

## 2026-11-24 — D1 redesign audit and proposed motion scope

- User-approved Graphite & Lime replaces the old mandatory visual direction for future redesign, while product/functionality remains. D1 is analysis/screenshots/documentation only, not implementation of a new visual system.
- D1 recommends one original educational ASCII Scroll scene for homepage, native scroll and static/reduced-motion/mobile fallback; no mandatory3D/slider/demo stack or newdependency. Final tokens/fonts and scene implementation are D2/D3 decisions.
- Detector findings are stylistic candidates, not accessibility or release failures. Source/browser evidence and exact scope are recorded in docs/design/D1_VISUAL_AUDIT.md. No real course publication, Studio attestations, student state or certificate changes.

## 2026-11-24 — Draft-course review unavailability and publication separation

- Reviews API stays published-only. Its404 within a loaded course overview is a neutral unavailable state, never a fabricated empty review list or authority to post.401 and other failures retain login/retry; success clears stale error. No backend access expansion.
- Publication's two content-review acknowledgements remain human decisions, even after automated C1–C5 checks. Certificate activation/issuer/public-origin decisions are independent from publication; preserve disabled issuance and truthful116notice until separately authorized.
- Evidence: docs/courses/course10-publication-c5.md; targeted isolated browser and publication/review/certificate regressions.

## 2026-11-23 — Per-grant protected playback cookie slots

- Native playback uses /lesson-attachments/<attachment>/playback/<grant_pk>/ with a distinct HttpOnly cookie name and exact Path per grant. Numeric PK is a selector, not a capability; signed gid plus server PK/nonce/user/file/access/TTL checks remain mandatory. DELETE clears only its nonce's slot. This prevents obsolete responses overwriting an active grant, including same-attachment tabs.
- Legacy /playback/ remains bounded read-only compatibility for signed payloads withoutgid; no new shared cookies. New/legacy namespaces cannot cross-authorize. New frontend accepts both; an old cached bundle needs refresh when backend/frontend are upgraded together. No schema changes or permission weakening; manual expiry Retry remains.
- Evidence: docs/courses/video-playback-c31.md (41Django/64frontend tests and real isolated Chromium). Working DB/media/settings untouched.

## 2026-11-23 — C2 pinned published-quiz order exception

- Owner-authorized Quiz5 order correction is an explicit operator-only management command, not an expansion of Studio edit permissions. Normal PUT deletes/recreates choices, so it must not be used for ID-preserving reorder.
- Only existing QuizChoice.order may change, with exact pinned IDs/text/keys/links/metadata and a fully before/after permutation. Any attempts before transition require renewed review; later attempts do not prevent a no-write KEEP. No unpublishing, regrading or historical snapshot rewrites. SQLite IMMEDIATE + verified backup + atomic updates preserve scope. Source JSON carries the same future-import ordering.
- Verified only on isolated databases; working apply still requires separate approval. See docs/courses/course10-quiz-order-c2.md.

## 2026-11-16 — Studio drafts and BrowserRouter leave guards

- Workspace resource retention is opt-in, scoped to API path plus auth generation. It must preserve editor subtree during refresh but clear private data on permission/session change. No draft persistence in localStorage.
- A successful save advances only the submitted baseline; newer edits remain dirty. Keep form controls editable during pending saves and preserve keyed lesson identity.
- BrowserRouter requires an early, otherwise inert POP dispatcher before its listener, plus an active Studio editor guard. Late listeners failed in actual Chromium. The implementation uses UNSAFE_NavigationContext/numeric history idx; upgrades require route/Back/reload regression checks. Existing native localized confirm pattern retained; no router migration or API change.


**Evidence review date:** 2026-11-09. This records decisions supported by project instructions, source and audit reports. It is not a reconstruction of undocumented conversations; unknown rationale is labeled.

## D-01 — Preserve Course 10 as the single media-course curriculum; do not publish by default

- **Decision:** Add Modules 1–5 inside existing Course 10 (`ai-media-content`); keep it unpublished until the owner explicitly approves publication.
- **Context:** The database audit mapped five modules and 15 lessons, with Lessons 113–115 in Module 5.
- **Reason:** Course 10 is the existing canonical course; separate QA courses are technical fixtures, not curriculum.
- **Consequences:** No duplicate Course 10 or Module 5 course should be created. Lesson 115 and Module 6 remain open work.
- **Evidence:** `docs/project-audit/02-course-content-and-database-audit.md`; `AGENTS.md` audit boundaries.

## D-02 — Graded assessment is reserved for Module 6, whose specification is not yet defined

- **Decision:** Modules 1–5 learning activities remain optional/ungraded; do not invent Module 6 structure, grading or certificate requirements.
- **Context:** Module 5 lesson sources reserve graded assessment for Module 6, but the audited project contains no Module 6 content or rubric.
- **Reason:** Assessment structure and learning outcomes are author decisions.
- **Consequences:** Obtain approved lesson count/topics, learning objectives, quiz/assignment criteria, review/retake policy and completion evidence before authoring.
- **Evidence:** Course audit section “Module 6 — UNKNOWN”; Course 10 JSON and asset sources listed there.

## D-03 — Course material has canonical sources; importers must not silently overwrite conflicts

- **Decision:** Use course-specific source documents/JSON plus explicit approved update records; retain conflict/fingerprint checks. Do not bulk-reimport a course to apply an editorial correction.
- **Context:** Audit found approved Lesson 92 data differing from the base Course 8 JSON and multiple historical manifests with stale status.
- **Reason:** Preserve reviewed material, IDs, student progress and media associations.
- **Consequences:** Make narrow idempotent updates only with explicit approval; mark historical/planning/completed manifests and reconcile source snapshots deliberately.
- **Evidence:** `docs/project-audit/02-course-content-and-database-audit.md`, source-of-truth section.

## D-04 — Protected lesson media remains behind authenticated access

- **Decision:** Lesson images/audio/downloads/video use private protected storage and server-side lesson authorization. Native video uses scoped short-lived grants/cookies and range delivery rather than permanent JWT query strings or public URLs.
- **Context:** Browser media elements cannot attach the application's Authorization header.
- **Reason:** Preserve enrollment, instructor-preview and revocation checks for media bytes.
- **Consequences:** Production must provide same-origin HTTPS/proxy routing for the playback cookie. Do not move lesson files into a public static/media handler.
- **Evidence:** `docs/protected-lesson-video.md`, `courses/video.py`, `courses/media.py`, Technical Audit 01 and 04.

## D-05 — Lesson, quiz and assignment evidence are separate

- **Decision:** Lesson completion, quiz attempts and assignment review remain separate records and semantics. Certificate eligibility is calculated server-side from configured evidence.
- **Context:** Platform supports independent progress and assessments; assignment approval must be attributable.
- **Reason:** A quiz attempt or lesson check-off alone must not falsely imply all course requirements were satisfied.
- **Consequences:** Do not merge these APIs or award certificates from client-submitted claims.
- **Evidence:** Course audit assessment/completion section; `quizzes/README.md`; certificate eligibility service mapping.

## D-06 — Keep inference-provider claims separate from educational subject matter

- **Decision:** Do not claim that the learner platform uses a model provider unless a runtime integration exists in source. Silero TTS is course-asset production, not app inference.
- **Context:** Bounded application scan found no hosted/local model client; AI tools appear in lesson data.
- **Reason:** Avoid overstating product capabilities and confusing content with application behavior.
- **Consequences:** Document future provider integrations and data boundaries if introduced.
- **Evidence:** Technical Audit 01, AI section; [AI_INTEGRATIONS.md](AI_INTEGRATIONS.md).

## D-07 — Treat Git worktree and local media as user-owned state

- **Decision:** Preserve uncommitted/untracked work; do not stage broad directories, clean files, or assume local media is disposable. Keep local config/database/backups out of Git.
- **Context:** The worktree has intentional `config/settings.py` changes, many untracked production assets, local QA outputs and imported skill material.
- **Reason:** Some files are production source or rollback assets; others are local-only, and their status cannot be inferred safely from being untracked.
- **Consequences:** Review explicit paths and staged diff before any commit; maintain separate verified backups for database and media.
- **Evidence:** current `git status` at 2026-11-09; `docs/project-audit/03-media-and-production-audit.md`; `docs/git-checkpoint-readiness.md` if present.

## D-08 — Do not rerun demo seeding as a harmless refresh

- **Decision:** Inspect the effects before running `seed_demo_courses`.
- **Context:** Audit found it uses `update_or_create` and forces `is_published=True`, while the audited demo courses were unpublished.
- **Reason:** A rerun can change visibility, not merely insert missing content.
- **Consequences:** Add protections only in a separately scoped implementation task; do not run against persistent data casually.
- **Evidence:** Course audit source-of-truth section.

## D-09 — Separate fast checks from local-media-heavy tests

- **Decision:** Consider isolating source-backed large media/integration tests from the default Django suite, without weakening coverage.
- **Context:** The full Django suite did not finish in Audit 04; optional Lesson 113/114 tests may read large local assets.
- **Reason:** Make CI/test feedback bounded and reproducible.
- **Consequences:** Any test reorganization must preserve a documented integration-media verification path.
- **Evidence:** Technical Audit 04 testing and remediation sections. This is a recommendation, not an implemented decision.

## D-10 — Lesson 115 production may use Remotion explanatory illustrations

- **Decision:** Continue the existing Remotion/FFmpeg pipeline for Lesson 115 instructional motion graphics and narration; a CapCut/OBS recording setup is not required to produce these explanatory demonstrations. Any editor-like schematic must be technically accurate and clearly labeled as an illustration, never represented as genuine CapCut footage. Keep generated media local and unattached until separately reviewed and integrated.
- **Context:** The owner explicitly directed continuation of the existing Remotion workflow, identified CapCut as lesson subject matter rather than a production dependency, and required truthful disclosure of software-interface illustrations.
- **Reason:** Produce the lesson with the established reproducible toolchain without fabricating screen recordings or blocking on unavailable capture tools.
- **Consequences:** V1's technical master remains pending human listening and author approval. V2/V3 require independent preview and QA. Course 10 remains unpublished; no database or attachment update follows automatically.
- **Evidence:** `video-production/lesson-115-production/V1_PRODUCTION_QA.md`; current Lesson 115 production task instructions.

## D-11 — Certificate lesson completion can use an explicit policy scope

- **Decision:** A nonempty `CourseCertificatePolicy.required_lessons` relation is the exact set used for certificate lesson-completion eligibility. If the relation is empty, `require_all_lessons=True` preserves the legacy all-course-lessons behavior. A nonempty scope takes precedence over that fallback flag.
- **Context:** The approved Course 10 certificate requirements cover the 15 instructional lessons in Modules 1–5 and exclude the Module 6 assessment lesson, while Course 8 must continue requiring every course lesson.
- **Reason:** Reuse the existing policy and server-side eligibility service while making the lesson scope explicit and testable.
- **Consequences:** The policy form validates selected lessons against its course; eligibility fails closed for invalid cross-course scope data. Migration `certificates.0005_coursecertificatepolicy_required_lessons` is additive and remains unapplied to the working database pending the separately approved migration workflow. This decision does not create or configure a Course 10 policy or authorize Module 6 records.
- **Evidence:** `certificates/models.py`, `certificates/services.py`, migration `certificates/migrations/0005_coursecertificatepolicy_required_lessons.py`, and isolated eligibility tests.

## D-12 — Certificate names require learner confirmation separate from profile data

- **Decision:** A certificate snapshot can use only the learner-owned, NFC-normalized `certificate_name` when a server-side confirmation timestamp applies to that exact value. Saving and confirming are separate actions; changing the name clears confirmation.
- **Context:** Course 10 requires an explicit learner-controlled certificate display name while administrative issuance must not override it.
- **Consequences:** Eligibility includes the confirmation requirement, issuance locks and rereads the student row, and certificate snapshots remain immutable after later name changes. The endpoint has no student identifier and is limited to the authenticated `student` role. Migration `users.0002_user_certificate_name_and_more` remains pending on the working SQLite database.
- **Evidence:** `users/models.py`, `certificates/services.py`, `certificates/views.py`, `certificates/admin.py`, and isolated certificate tests.

## P1G — Existing issued snapshots remain privately readable when issuance is disabled (2026-11-13)

Owner-authorized separation: the authenticated own certificate list and previously authorized PDF download do not depend on CERTIFICATES_ENABLED. They read stored snapshots without recalculating eligibility, changing name confirmation or issuing records. Ownership, revocation/evidence, trusted PDF origin and private/no-store remain required. No separate certificate detail route is introduced.

Public verification and course eligibility/status retain the global gate. Issuance/revocation services and disabled-mode Admin policy writes/issue/revoke remain blocked; Admin reads remain visible to authorized staff. Certificate-name confirmation stays independently student-owned as before. A downloaded PDF's verification link is intentionally unavailable while public verification is gated. Any future public-read expansion or trusted-origin/global enablement requires its own authorization. Evidence: `docs/courses/certificates-read-only-p1g.md` and isolated certificate regression tests. This supersedes historical documentation permitting Admin policy preconfiguration/revocation while the global feature is disabled.

## P1I — Optional public verification does not block authenticated PDF reads (2026-11-13)

Owner-approved: an issued valid snapshot can render as an authenticated private PDF without CERTIFICATE_PUBLIC_ORIGIN. The renderer omits QR/link if public verification is disabled or explicit origin is absent/invalid; it never uses request Host. Existing public verification route and issuance gate remain unchanged. Same API supports inline preview and attachment download, with identical snapshot metadata and no record mutation. Profile hides unavailable public verification and keeps preview Blob URLs session-scoped. This supersedes only P1G's origin-as-download-prerequisite; it does not authorize public verification or issuance. Evidence: `docs/courses/certificate-pdf-p1i.md`.


## 2026-11-16 — Studio section renaming preserves title anchors atomically

Existing source_sections are title strings, not synthetic immutable IDs. S3 uses explicit expected-old/new intents on the existing owned unpublished lesson PATCH. Validate unique body headings/ordered source titles and reject collisions; save text, image-placement references and all matching attachment anchors in one transaction. Move video/VTT together by their existing shared anchor, retaining IDs/files; never infer pairing from filenames or repair existing orphan anchors. Refresh lesson state after obtaining the course lock. Editor-only invalid inputs remain dirty; save acknowledgements rebase newer intents. Any stale-prop display alias must be scoped to attachment ID and expected old anchor, never historical title alone (freed titles can be reused). See `docs/instructor-studio/s3-section-renaming.md`. No schema change, public-media change or live-data update.


## 2026-11-16 — Studio S4.1 moves preserve implicit video/WebVTT groups

Keep the existing title-anchor pairing contract until an explicit video/track relation is separately designed. The owned unpublished lesson placement PATCH accepts expected saved headings/source/subtitle ID, moves a uniquely linked video/VTT together atomically and rejects conflicting destination video/VTT. Direct VTT moves are deferred; audio/SRT stay independent. Only expose inline targets accepted by the student section resolver. Pending local title renames and active lesson saves block movement; media refresh must retain dirty lesson fields. Attachment IDs/files/order and private delivery remain unchanged. See `docs/instructor-studio/s4-1-attachment-placement.md`.


## 2026-11-18 — Studio final assignments reuse the existing contract

S5.1 supports existing final_media_project in the Studio selector and assignment serializer, with text/file submission types. The model has no title field: use description for the full assignment name+instructions without inventing a new persisted title or rewriting content. A shared safe-text component preserves line breaks in Studio/student instruction previews. Existing four review criteria remain fixed at integer0–25 and are displayed read-only; rubric configuration, quiz editing and certificate rules are separate work. Existing-submission and published-content locks remain authoritative. See docs/instructor-studio/s5-1-assignment-authoring.md.


## Studio section creation uses existing title anchors (2026-11-18)

Creation appends source_sections and exact standalone heading paragraphs in text_content through the existing lesson PATCH, without another section model or API field. First-section creation explicitly places a chosen heading before existing plain text, preserving that text inside the section to satisfy the current renderer's first-heading rule. Legacy teaching-block/identifier lessons retain their existing editor until an explicit conversion workflow exists. New anchor validation protects orphan media from accidental reassociation; unchanged legacy metadata is not normalized retroactively. Pending creation fields are local dirty state only, never persisted as competing content. See docs/instructor-studio/section-creation-101848f.md.
