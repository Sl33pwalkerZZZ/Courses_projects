# Course 10, Module 6 — Final Assessment Specification

## Implementation update — 2026-11-11

The approved structure now has a source-pinned, create-only implementation at
`courses/management/commands/import_media_module_6.py` with its reviewed source
at `courses/management/media_module_6.json`. It defaults to `--dry-run`, rejects
unexpected Course 10 state or any conflicting Module 6 record, and creates no
records during preview. Its explicit `--apply` path creates one order-6 module,
one assessment lesson, one generic file-capable final assignment, a **draft**
15-question single-choice quiz at 70%, and a disabled Course 10 certificate
policy whose exact lesson scope is the existing 15 instructional lessons.

The importer has not been applied to the working SQLite database. Course 10
therefore still has five modules and 15 lessons and remains unpublished. The
new policy deliberately has no issuer identity or approval: a future authorized
administrator must configure those separately before issuance can be enabled.
The importer requires the pending `certificates.0005`, `progress.0005`, and
`users.0002` migrations to be applied first; they were rehearsed successfully
only on an isolated SQLite copy. Focused isolated tests cover dry run, exact
creation, quiz shape, policy scope, conflict rejection and replay no-op.

### Current database verification (2026-11-11)

The three prerequisite migrations are now applied in the working database, and
the importer has been run once. Course 10 has Module 6 ID 40 and assessment
Lesson 116, Assignment ID 2, draft Quiz ID 5 (15 single-choice questions, 60
choices, 70% threshold), and CourseCertificatePolicy ID 2. The policy is still
disabled and issuer approval is false. The importer was replayed in dry-run mode
and returned a no-op. Course 10 remains unpublished. The earlier paragraph above
describes the pre-apply state and is retained as implementation history.

The final-project review path now requires four optional-to-the-legacy-workflow,
server-validated scores (completeness, application, quality, documentation),
each from 0 to 25, for `final_media_project` assignments. Scores are stored in
the existing review-history JSON and exposed as a total to the student and
Instructor Studio. Course 8's `ai_selection_map` review remains unchanged.

**Official module title (owner-approved):** «Итоговая аттестация и получение сертификата»
**Purpose (owner-approved):** assess the skills taught in Course 10 Modules 1–5 through one integrated practical assignment and one final knowledge test, then apply the existing instructor-review and administrator-confirmed certificate workflow.
**Specification status:** owner-approved assessment structure and policies, technically reconciled against the current source and local database on 2026-11-10. This document is not authorization to create records, run a migration, issue certificates, or publish Course 10.

## Evidence labels

- **OWNER-APPROVED** means the project owner explicitly settled the policy or structure.
- **VERIFIED** means confirmed in the current source or with a read-only query of the local SQLite database on the verification date.
- **PROPOSED** means educational task copy or an implementation design derived from the approved policy; it still needs content-owner review before becoming canonical student content.
- **GAP / DEPENDENCY** means the current implementation cannot yet deliver the approved behavior or requires environment-specific verification.

## 1. Verified course state and learning outcomes

**VERIFIED:** Course 10 is ID `10`, slug `ai-media-content`, «ИИ для создания медиаконтента: от идеи до публикации». The database has five modules and 15 instructional lessons. It remains unpublished. Module 6, its lesson, assessment records and Course 10 certificate policy do not exist. No individual learner, submission, attempt, or certificate record was inspected for this document. The SQLite connection used `mode=ro` with `PRAGMA query_only=ON`; integrity check passed and foreign-key check returned no violations.

| Module order | Module ID | Existing title | Lessons in course order |
|---:|---:|---|---|
| 1 | 34 | Основы ИИ в медиапроизводстве | 100–102 |
| 2 | 35 | Тексты и сценарии с помощью ИИ | 103–105 |
| 3 | 36 | Создание изображений и графики с помощью ИИ | 106–108 |
| 4 | 37 | Создание и обработка аудио с помощью ИИ | 109–111 |
| 5 | 39 | Создание и монтаж видео в CapCut Desktop | 113–115 |
| 6 | No record | Итоговая аттестация и получение сертификата | No lesson yet |

The gap at lesson ID 112 is the removed technical QA fixture, not a curriculum lesson. When separately authorized, create Module 6 at order 6 and resolve all new primary keys by course/order relationships; never assume the future module or lesson IDs.

The following map summarizes the **saved learning objectives** of Modules 1–5. It is a coverage guide, not additional course content.

| Module | Verified learning outcomes relevant to the final assessment |
|---|---|
| 1 — Foundations | Distinguish ordinary automation from generative AI; decide where human review is required; prepare a media brief and prompt; verify facts, rights and disclosure. |
| 2 — Text and scripts | Select an idea using audience, goal and verifiable sources; prepare a brief, prompt, short script and storyboard; adapt a message to a platform without changing its facts. |
| 3 — Images and graphics | Specify and evaluate a visual prompt; create readable hierarchy and consistent visual style; distinguish illustrations from documentary evidence and avoid fabricated data. |
| 4 — Audio | Prepare and review synthetic narration; distinguish recognition, transcription and translation; correct and synchronize subtitles; assess signal quality, export and provenance. |
| 5 — Video | Organize a reopenable CapCut project; edit image, voice and captions coherently; verify intelligent-tool output; adapt aspect ratio and check export, rights and accessibility. |

## 2. Owner-approved one-lesson structure

**OWNER-APPROVED:** Module 6 contains exactly one final-assessment lesson. The lesson provides one entry point with three stages:

1. **Comprehensive practical assignment** — one integrated media-production project applying the outcomes in Modules 1–5.
2. **Final knowledge test** — 15 single-correct-answer questions.
3. **Completion and certificate information** — explain instructional completion, assessment results, instructor review, eligibility and administrator-confirmed issuance as distinct states.

The assignment and quiz are platform assessment entities attached to this one lesson; do not create duplicate assessment lessons. A working lesson title is «Итоговая аттестация по курсу» (**PROPOSED**, for author review). The exact lesson title, Russian instructions and section headings are not yet approved. Lesson completion remains independent of assignment approval and quiz results; those are separate evidence records.

## 3. Comprehensive practical assignment

### Objective and proposed task outline

**OWNER-APPROVED:** require one integrated project based on actual Course 10 content and assess application across Modules 1–5. Do not reuse the Course 8 AI selection map or its question bank. Do not invent real-world results, audience metrics, permissions, or factual sources.

**PROPOSED, derived from the verified outcomes:** plan and prepare a short media publication from brief to export. The learner identifies an audience, purpose, message and platform; documents source checking, rights and AI use; prepares or edits a script and storyboard; produces a consistent visual and audio package; assembles an organized CapCut project; creates a main export and an adaptation; and completes a factual, rights, accessibility and technical quality check. The content owner must approve the scenario and mandatory deliverables before this becomes student-facing assignment text.

### Proposed evidence package

The following deliverables jointly demonstrate the five modules; their precise required/optional status remains **PROPOSED**:

- Media brief with audience, purpose, core message, platform, duration and target format.
- Source/fact-check and rights/provenance notes, including where AI was used.
- Final edited script and storyboard linking narration to visuals.
- Visual assets and concise style guide, with generated or illustrative material identified.
- Reviewed narration or speech, corrected transcript and synchronized captions, with voice/asset provenance.
- Reopenable, organized CapCut project or approved project package, primary export and any required adaptation.
- Final checklist for factual accuracy, rights, sound, captions, readability, aspect ratio and playback.

The author must still decide the exact scenario, duration, required source files, export aspect ratios, whether adaptation is mandatory, and whether editable CapCut project files are required. These are content decisions; do not infer them from a lesson objective.

### Owner-approved instructor rubric

**OWNER-APPROVED:** use this 100-point guideline for instructor evaluation.

| Criterion | Guideline points |
|---|---:|
| Completeness and fulfillment of requirements | 25 |
| Correct application of concepts and tools from Modules 1–5 | 25 |
| Quality and usefulness of the resulting work | 25 |
| Explanation, documentation and reproducibility | 25 |
| **Total** | **100** |

**VERIFIED:** the current review model stores approve/reject, reviewer, timestamp, feedback, revision and decision history; it does not persist criterion scores or a 100-point total. The rubric is guidance, not a stored grade. Approval remains the authoritative completion/certificate signal. No numeric cutoff for translating points to approval has been specified. Persisting rubric scores is an optional, separately designed enhancement, not a prerequisite to this specification.

### Submission and review workflow

**OWNER-APPROVED:** learners may submit text, files, or both; see status and instructor feedback; and resubmit after rejection/feedback. Only an approved submission satisfies certificate eligibility. Preserve previous submissions and review decisions. An approved submission is locked unless an authorized instructor explicitly reopens it.

**VERIFIED in current worktree source:** the reusable generic workflow uses `AssignmentSubmission`; it does not replace the Course 8 structured `ai_selection_map` flow. Student routes are:

- `GET /api/assignments/<assignment_id>/submissions/` — assignment metadata and that learner’s history.
- `POST /api/assignments/<assignment_id>/submissions/` — submit text, files, or both.
- `GET /api/assignments/<assignment_id>/submissions/<submission_id>/files/<attachment_id>/` and the legacy-file route — authenticated, scoped downloads.
- Assignment descriptions are supplied in the existing lesson response. No separate assignment catalogue is introduced.

The Student LessonView embeds `frontend/src/components/learning/AssignmentSubmission.jsx`. Instructor review remains in Instructor Studio at `frontend/src/pages/instructor/Submissions.jsx`, backed by `GET /api/studio/courses/<course_id>/submissions/`, `POST /api/studio/submissions/<id>/review/`, `POST /api/studio/submissions/<id>/reopen/`, and scoped file-download routes. The existing `progress.services.review_assignment_submission` service remains authoritative. Review is limited to the course owner or authorized administrator/moderator; self-review is denied.

Generic revisions are immutable linked `AssignmentSubmission` records. Rejection permits a new revision; reopening an approved submission creates a new draft linked to the approved record. Prior file attachments remain on their original revision. Only the current approved tip with verifiable reviewer/time/history can satisfy the certificate evidence check. A pending generic submission is unique per learner and assignment. The Course 8 structured map retains its separate single-record draft/resubmission behavior and is not converted to the generic history chain.

The current student component displays each revision’s content, status, attachments and feedback in chronological order. It does not yet display each revision’s submitted/reviewed timestamps or the complete event-level review log, although the API/model retain relevant timestamps and decision history. Include those details in the release-quality UI review. The generic student form submits directly as pending; it does not provide a learner-saved draft. A draft record is created only by the instructor’s explicit reopen action.

**GAP / DEPENDENCY:** these API and model changes are present in the uncommitted worktree, but `progress.0005_assignmentsubmissionattachment_and_more` is not applied to the current SQLite database. The live schema therefore does not yet contain the attachment table, revision link or generic-pending uniqueness constraint. Do not treat the student upload flow as live/usable until the migration is reviewed, backed up, applied under explicit authorization, and verified. No Module 6 records are part of that migration.

### Initial assignment upload contract

The current implementation defines this server-validated allowlist and size policy:

- **Documents:** PDF, DOCX, PPTX, XLSX, CSV, TXT — maximum 10 MiB each.
- **Images:** PNG, JPG, JPEG, WEBP — maximum 10 MiB each.
- **Video:** MP4 — maximum 50 MiB each.
- At most 5 files and 100 MiB combined per submission.
- ZIP/archives, executables, scripts, macro-enabled Office files, HTML, SVG and all unlisted extensions are rejected.

The application validates the extension and file contents rather than trusting client MIME: PDF signature/EOF, expected OOXML package members/content types with macro rejection, decoded image format, UTF-8 text checks, and ISO-BMFF MP4 box structure. It uses randomized private `submissions/` storage paths, sanitized display filenames, hashes, transactional record creation and file cleanup on failed writes. Download handlers check learner enrollment and submission ownership; instructor downloads check course ownership/authority. The lesson-media endpoint is restricted to registered lesson files, and public media handling rejects `submissions/` paths.

**Operational limitations:** MP4 validation confirms a structurally complete container, not H.264/AAC codec compatibility or that the video decodes. Upload checks happen after the framework parses the multipart request; temporary-disk/request-body protection must also be configured and verified at the deployment proxy/server. The actual production request cap and storage quota are unknown. Do not expose the workflow in production until these limits are confirmed. These application defaults are the initial owner-requested policy, not a claim that the deployment can accept every maximum-size request.

## 4. Final knowledge test

### Owner-approved configuration

- Exactly **15** questions, each with one correct answer (`single`).
- **1 point per question**, 15 points maximum; the current engine represents this as `correct_count` out of `question_count` plus a percentage, rather than a separate points field.
- **70%** passing threshold. With equal weighting, the minimum is **11/15** (73.33%); 10/15 (66.67%) fails.
- Approximately three questions for each of Modules 1–5.
- Mix basic, intermediate and challenging application; remove ambiguous wording and duplicate concepts.
- Author all question text, distractors, keys and explanations for Course 10. Never copy Course 8 questions or answers.

### Question blueprint — coverage, not question text

| Source module | Three-item coverage target |
|---|---|
| 1 | Generative AI vs ordinary automation and human accountability; brief/prompt/tool choice; fact checking, rights or transparent disclosure. |
| 2 | Audience/purpose to brief and bounded prompt; edit a script/storyboard; adapt a platform message without distorting facts. |
| 3 | Visual prompt and generation limits; readable graphics with verified text/data; consistent style and provenance. |
| 4 | TTS preparation and voice provenance; correct/synchronize transcript/subtitles; assess audio/export and distinguish conventional DSP from AI. |
| 5 | Organize a reopenable CapCut project; edit narration/captions and verify tool output; select/adapt export and perform publication QA. |

Final questions must be reviewed against the canonical lesson materials before draft quiz creation. The blueprint does not authorize quiz records or publication.

### Verified quiz engine behavior

`QuizQuestion.Type.SINGLE` supports the approved format. `quizzes.services.submit_attempt` validates the published quiz, grades equally by question, uses the exact integer ratio for pass/fail, and snapshots question/choice/key/explanation state into each answer. A client UUID makes retries of the same request idempotent; a distinct UUID creates a separate attempt. Attempts have no cap/cooldown, and earlier attempts remain. The current student attempt endpoints require authentication and enrollment and scope attempts to their owner. Correct choices and explanations are withheld from the pre-submit quiz response and included in the learner’s own submitted-attempt feedback.

The current `QuizAttempt` stores correct count, question count, percentage, threshold snapshot and pass result. It does not persist a separate point total; for the approved equally weighted quiz, points can be represented by correct count. Question/choice randomization is not supported and is not required by the approved policy.

## 5. Completion and certificate rules

### Owner-approved eligibility

Certificate eligibility requires all of the following:

1. Completion of all required instructional lessons in Modules 1–5 (the 15 existing lessons, excluding the Module 6 assessment lesson).
2. Instructor/authorized administrator approval of the Module 6 practical assignment.
3. A passing attempt on the configured final quiz at 70% or higher (at least 11/15).
4. The learner has provided and confirmed their full name.

Assessment evidence and lesson completion stay independent. Do not make quiz pass or assignment approval a prerequisite for marking the final assessment lesson read/complete. Eligibility is computed server-side; issuance remains a separate authorized administrator workflow, and learners cannot self-issue.

### Verified Course 8 certificate architecture and Course 10 gap

**VERIFIED:** `CourseCertificatePolicy`, `Certificate`, `certificates.services.eligibility`, `issue_certificate`, and `revoke_certificate` are the reusable server architecture. The current Course 8 policy is enabled, requires all course lessons, points to its existing final quiz and required assignment, and uses the approved issuer identity `AI Courses` with issuer approval. Course 10 currently has no policy. The Course 8 certificate PDF uses learner name, course title, issue date, issuer, opaque verification code and QR/link. The public verification endpoint returns initials, course title, issuer, issue date and valid/revoked state without account identifiers. Revocation records are retained; revoked certificates are not deleted, PDF download is denied, and verification continues to show the revoked state. A unique database constraint prevents duplicate certificates per student/course; a revoked certificate is not automatically reissued.

**GAP:** current `require_all_lessons=True` checks every lesson in the course. It cannot express the approved Course 10 requirement of exactly the 15 instructional lessons while excluding the single Module 6 assessment lesson. Before configuring Course 10, add a narrowly scoped required-lesson selection to the certificate policy and server-side eligibility logic; preserve the existing `require_all_lessons` semantics for Course 8. This requires an additive migration and isolated tests. No such migration or Course 10 policy is included here.

The current course-progress API also counts every course lesson. If Module 6 adds an assessment lesson, the progress display may report completion differently from certificate eligibility, which intentionally scopes Modules 1–5. The user-facing copy must explain that distinction. Changing progress semantics to exclude the assessment lesson is a separate decision and must not be done implicitly.

**GAP:** issuance currently requires a moderator/administrator, certificate feature flag, published course, enrollment, enabled/approved policy, approved quiz/assignment evidence and a valid full name matching the learner’s profile. The Admin issuance form lets an administrator enter and confirm the profile-matching name; there is no certificate-specific learner confirmation step. Add an explicit learner-provided/confirmed name workflow, or obtain a separately approved determination that the existing learner profile workflow satisfies this requirement. Do not imply the existing administrator field is learner confirmation.

**Deployment dependencies:** certificate issuance is feature-flagged. PDF download requires ReportLab, configured Cyrillic/Kazakh-capable regular/bold fonts and a trusted public verification origin. These settings/assets must be verified in the eventual deployment environment. The approved issuer must remain `AI Courses` unless the issuing entity changes through an authorized decision. No university accreditation or signature claim may be added.

## 6. Course 8 reference — verified behavior

Read-only database verification on 2026-11-10 found Course 8 (`Как выбрать нейросеть под свою задачу`) published with Module ID 31, order 1, and Lessons 91–96. Its lesson 96 has Assignment ID 1 (`ai_selection_map`) and published Quiz ID 3 with 15 questions: 10 single-choice, 5 multiple-choice, 60 choices total, and a 70% threshold. The current policy selects that quiz and assignment and has issuer name `AI Courses`. Course 10 remains a separate unpublished course; none of Course 8 content is to be copied.

| Capability | Existing implementation |
|---|---|
| Course and structured lesson content | `courses/models.py`: `Course`, `Module`, `Lesson`, `Assignment`, `LessonLearningContent` |
| Course 8 structured map | `progress/selection_maps.py`, `progress/views.py::SelectionMapView`, `frontend/src/components/learning/SelectionMap.jsx`; dedicated `ai_selection_map` behavior remains unchanged. |
| Generic submission source in current worktree | `progress/models.py`, `progress/assignment_views.py`, `progress/submission_files.py`, `progress/services.py`; migration `progress/migrations/0005_assignmentsubmissionattachment_and_more.py` is pending on the real local database. |
| Student and instructor UI source | `frontend/src/components/learning/AssignmentSubmission.jsx`, `frontend/src/pages/LessonView.jsx`, `frontend/src/pages/instructor/Submissions.jsx` |
| Quiz authoring and student testing | `studio/views.py`, `quizzes/models.py`, `quizzes/validation.py`, `quizzes/services.py`, `quizzes/views.py`, `frontend/src/components/LessonQuiz.jsx` and related quiz components. |
| Assignment review | `progress.services.review_assignment_submission`; `studio/views.py` review/reopen endpoints and Instructor Studio submissions UI. |
| Certificate eligibility and issue/revoke | `certificates/models.py`, `certificates/services.py`, `certificates/admin.py`, `certificates/views.py`, `certificates/pdf.py`. |

Course 8’s structured assignment workflow is intentionally not the universal file/text workflow: it stores a structured JSON map and preserves its established review semantics. The generic API excludes `ai_selection_map` and quiz assignments. Existing Course 8 content, quiz, learner data, progress and certificate records are outside this specification.

## 7. Ordered implementation roadmap and dependencies

1. **Finish and activate the universal submission workflow.** The uncommitted implementation and focused tests are present. Review its security and UI changes, resolve the request-body/proxy-size limitation, verify test isolation and migration consistency, then create/verify a fresh SQLite and protected-media backup before any separately authorized real migration. The real database currently has `progress` migrations only through `0004`; `0005` is unapplied. Do not create Module 6 yet.
2. **Add certificate lesson scoping.** Design a reusable required-lesson selection, additive migration and eligibility tests proving Course 10 checks the 15 instructional lessons but not the assessment lesson. Preserve Course 8 all-lesson behavior. Use an isolated database first; real migration requires a verified backup and separate authorization.
3. **Add learner name confirmation.** Implement an explicit learner-side confirmation or verify/approve an existing profile UX with evidence; keep administrator issuance and server-side profile matching.
4. **Approve final assignment content.** Decide scenario, exact instructions, required/optional deliverables, project-package format, source/provenance requirements and how the four rubric criteria guide the approve/reject decision. Do not add numerical grade storage/cutoff without a separate decision.
5. **Author and review the 15-question bank.** Create Course 10-specific single-answer questions, distractors and explanations from the blueprint and canonical Modules 1–5 sources. Keep draft until reviewed and publication is explicitly authorized.
6. **Prepare a conflict-safe Module 6 importer.** Target Course 10 ID 10 and module order 6; resolve record IDs from relationships. Dry-run by default, reject conflicts, back up before a real import, and never modify Modules 1–5 or publish the course.
7. **Configure Course 10 assessment and certificate policy.** Attach one practical assignment and one 15-question quiz to the single lesson; set 70%, configure the exact required-lesson set and approved issuer through authorized workflows only.
8. **Complete student/instructor UI and certificate experience.** Reuse LessonView, Instructor Studio, course progress, certificate status/list, PDF and public verification. Explain instructional completion versus eligibility/issuance. Preserve all existing semantics and access checks.
9. **Validate in isolated test databases/storage.** Cover submission formats/limits, ownership, file authorization, review/reopen/resubmission, Course 8 regression, 15-question scoring/retakes/history, scoped lesson eligibility, name confirmation, idempotent issue/revoke, PDF/Unicode and verification privacy. Then conduct authorized browser QA. Publishing Course 10, applying live migrations, importing Module 6, or issuing real certificates each requires explicit authorization and backups appropriate to the change.

## 8. Required acceptance criteria

- Exactly one order-6 Module 6 and one final-assessment lesson in Course 10; no new course; Modules 1–5 and Lessons 113–115 remain unchanged.
- Student can submit text, files or both; see immutable revision history, status and feedback; resubmit after rejection; and is locked after approval unless an authorized instructor reopens the work. Unauthorized users cannot submit or download another learner’s files.
- Only the course owner or authorized administrator can review/reopen; decision, reviewer, time and feedback are attributable. Only a verifiably approved current revision counts for certificate eligibility.
- The final quiz contains 15 Course 10-authored single-answer questions, yields 0–15 correct, passes at 11 or more, retains attempts and has unlimited retakes without cooldown.
- Certificate eligibility checks the 15 required instructional lessons, assignment approval, passed quiz, enrollment, published course, approved issuer and confirmed learner name. It does not require assessment lesson completion.
- Issuance is server-side, administrator-authorized and idempotent. PDF fields and QR/link are accurate; public verification discloses minimal identity; revocation remains visible and does not delete the certificate.
- Tests use isolated database and temporary storage. Real Course 10 remains unpublished. No real records are changed until a separate approved import/migration task with verified backups.

## 9. Decisions still genuinely open

The following details remain open; they do not reopen the approved module/lesson count, rubric, quiz settings, retake policy, resubmission rule, issuer identity or certificate requirements.

- Exact Russian title, section headings and student-facing instructions for the single assessment lesson.
- Capstone scenario and which proposed deliverables are mandatory; duration, adaptation formats, source requirements, and whether/how the editable CapCut project is packaged.
- Whether the 100-point rubric remains instructor guidance only (current schema) or is later stored numerically; if stored, define a score threshold and approval mapping.
- Explicit learner-side full-name confirmation design (or a separately approved determination that an existing profile workflow is sufficient).
- Production request-body/proxy limits and temporary-storage quota for the implemented 100 MiB submission policy; MP4 codec/decode policy if playable upload rather than download-only evidence is desired.
- Whether overall progress display should distinguish instructional completion from the Module 6 assessment lesson; do not change the current all-course-lesson progress calculation without a separate decision.
- Deployment readiness for the certificate feature flag, Unicode fonts and trusted public verification origin.

## 10. First implementation task

**Recommended first task:** complete the universal assignment workflow already present in the uncommitted worktree, with special attention to bounded multipart request handling, owner/instructor authorization, private download coverage, regression tests for the Course 8 structured map, and migration readiness. Its dependency is verification of application and deployment upload limits; the local database currently has not applied `progress.0005_assignmentsubmissionattachment_and_more`. Use isolated tests, then stop for owner review before any real migration or Module 6 records.

**VERIFICATION LIMIT:** this documentation task made no application-code or database changes and did not rerun browser tests. The current protected student/instructor flows have no authorized real-account test session in the recorded project state; do not claim authenticated browser verification until one is provided. The latest recorded focused implementation results are 67 Django tests passed with 1 skipped, frontend suite 35 tests passed, lint/build passed; these were not rerun during this documentation-only verification.

## Boundaries

This is the finalized owner-approved specification, not implementation or publication authorization. The current worktree includes uncommitted workflow code and a pending migration; this document does not apply or approve that migration. No Module 6 database records, course content, migration state, publication status, certificate policy or real learner data was modified. Course 10 remains unpublished. Preserve all other uncommitted and untracked files; nothing was staged, committed or pushed.
