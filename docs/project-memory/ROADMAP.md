# Roadmap

## Current priorities — C5 (2026-11-24)

- C1–C4 and Lesson115/Module6 implementation are complete; older production priorities below are historical snapshots, not current blockers. C4 full isolated student workflow passed; C5 fixed neutral reviews404 and checked publication readiness.
- Next: owner reviews sources/assessment and course-wide description, then separately authorizes Studio acknowledgement/request and administrator decision. Course10 remains unpublished; no requests submitted. See docs/courses/course10-publication-c5.md.
- Certificates remain disabled: obtain issuer/global/policy/public-verification decisions, rehearse issuance on a fresh isolated copy, then separately authorize configuration and precise116notice update. Publishing course does not require enabling certificates.

**Status snapshot:** 2026-11-09 (updated after Lesson 115 V1 technical QA). Derived from the latest audit reports, current git state and user-approved roadmap. Recheck before starting work.

## Completed or present

- Cinematic frontend redesign Phases 1–3 are in commits `42455ca` and `e1ae750`; preserve these changes.
- Protected instructional video infrastructure is in commit `28ff315`.
- Course 10 Module 5 text curriculum/import work exists in commit `ca684c3` and has uncommitted manifest/importer edits. The database audit snapshot recorded Course 10 modules 1–5 and lessons 100–111, 113–115; course remained unpublished.
- Lessons 113 and 114 had three integrated videos each; Lesson 114 also had two VTT files. The audit found matching stored attachment hashes. Browser verification of authenticated Lesson 114 remains unverified.
- Modules 1–4 content/asset state is documented in the audits. Do not change it as part of remaining Lesson 115 work.
- Lesson 115 V1 has a full-quality local technical master, aligned VTT and QA report. It is not author-approved or attached. V2/V3 have not been preview-rendered; see `video-production/lesson-115-production/V1_PRODUCTION_QA.md`.
- Project audit phases 1–4 have reports under `docs/project-audit/`.

## Active priorities

1. **Finish Lesson 115 production and review.** First obtain human listening and author review of the V1 technical candidate. If approved, render V2 and V3 previews with the same Remotion pipeline and no continuous music, inspect each, then render full-quality versions only after their QA passes. The compositions are explanatory illustrations, not CapCut screen recordings; keep that distinction visible. Use a separately authorized media integration task after review. No Lesson 115 attachment records were found in the dated audit snapshot, which must be refreshed before any import. Keep Course 10 unpublished.
2. **Define Module 6 with the content owner.** No database module, JSON, source, number of lessons, objectives, rubric, quiz/assignment configuration, retake policy or certificate evidence was found. The audit says graded assessments belong in Module 6 but does not specify them. Obtain decisions; do not invent content or thresholds.
3. **Run course-wide remediation after author/content approval.** Candidate items from the audits: update Course 10 description before publication; correct stale Module 3 asset-manifest status; reconcile Course 8 Lesson 92 canonical JSON with approved database content; preserve unknown Course 1/9 data pending owner confirmation; add safeguards around demo seeding; label historical docs.
4. **Authenticated Lesson 114 browser verification.** Prior reports lack an authorized read-only test session. Arrange an isolated test session/environment without changing real accounts or learner data; verify video playback, seeking, captions, permissions and responsive UI.

## Technical remediation queue

- **Before any deployment:** verify actual production settings/topology. The local `check --deploy` failure/warnings in Audit 04 are conditional and do not prove production settings are the same.
- **Performance:** measure query counts for Studio course/dashboard/submission views; Audit 04 found source-level query growth, not measured production slowdown.
- **Maintenance:** define retention for expired/revoked `LessonPlaybackGrant` records, then implement a bounded cleanup only after data-retention approval.
- **Test reliability:** finish/run the full Django suite with a known isolated DB; optionally split local large-media integration tests while retaining explicit verification.
- **Release QA:** browser-test public and authorized role flows, locales/themes, responsive layouts, reduced motion and protected media on the actual deployment topology.

## Release gates

- Keep Course 10 unpublished until explicitly approved.
- Do not create/issue Course 10 certificates without approved policy and evidence criteria.
- Do not attach planned video records before real files, captions and provenance pass validation.
- Preserve Course 8 and all learner progress; don't run broad seed/import commands without reviewing their effects.
- No publication, migration, import, commit or push is authorized by this roadmap.

Evidence: `docs/project-audit/02-course-content-and-database-audit.md`, `03-media-and-production-audit.md`, `04-technical-quality-and-bug-audit.md`.
