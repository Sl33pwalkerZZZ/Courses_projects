# Architectural and Project Decisions

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
