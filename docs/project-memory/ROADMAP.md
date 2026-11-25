# Roadmap

## Актуальный план D3.2–F7 (решение владельца,2026-11-25)

Цель — публичный AI Courses v1.0 с двумя завершёнными курсами и встроенным AI Tutor. Новые курсы отложены до первого запуска. Это план, не разрешение автоматически выполнять последующие стадии. Course10 остаётся черновиком до отдельного решения владельца.

| Этап | Содержание / граница |
|---|---|
| D3.2 | Завершить текущую UX/UI и motion реализацию и проверку; личная визуальная приёмка владельца |
| D3.3 | Реализованы A/B/C/D материалы, выборочная оригинальная edge refraction Chromium и Firefox frost fallback; browser/tests завершены. Ожидается личная визуальная приёмка владельца; см. D33_LIQUID_GLASS_MATERIALS.md |
| D4 | Анимированные light/dark transitions |
| D5 | Каталог и страницы курсов |
| D6 | Учебное пространство и профиль |
| D7 | Оставшиеся Studio-specific уточнения и итоговая проверка; общая оболочка уже внедрена D3.2 |
| D8 | Полная проверка дизайна, accessibility, performance и regressions |
| F1 | Финализировать представление, описание и метаданные Course10 |
| F2 | Настроить и проверить выдачу сертификатов по отдельному решению владельца |
| F3 | Подготовить финальную Git-версию и план интеграции |
| F4 | Явное одобрение владельца и публикация Course10 |
| F5 | Встроенный AI Tutor: RAG + LLM API, объяснения в контексте курса, learning guidance, source-grounded ответы и formative feedback; не раскрывает ключи оценивания и не заменяет официальную проверку преподавателя |
| F6 | Production infrastructure: persistent DB, protected media storage, security, backups, environment variables и deployment configuration |
| F7 | Deploy и публичный запуск с HTTPS |

Для F6 сначала оценить подходящие free tiers: лимиты, условия институционального использования, стоимость хранения/трафика, безопасность и надёжность. Провайдеры пока не выбраны. D3.2 не реализует D3.3/D4 или F1–F7; никаких публикаций и включения сертификатов в этом этапе.

## Design roadmap — D3.1 complete, owner visual review required (2026-11-25)

- D3 was implemented but not visually approved. D3.1 refines it to owner-directed Obsidian/Frost/Aqua with Liquid Glass, continuous ASCII, independent restrained parallax, auth/footer and Studio overview improvements.
- Evidence: docs/design/D31_LIQUID_GLASS_REFINEMENT.md. Next action is owner review at isolated preview5199, then separate D4 authorization. Preserve D0–D8; no automatic publication or certificate activation.

## Design roadmap — D3 complete, owner review next (2026-11-25)

- D3 changes composition, not just palette: open asymmetric hero, one original scroll-linked ASCII sculpture, unboxed learning sequence, preserved real catalog and clear close. D3_LANDING_REDESIGN.md contains before/after monochrome evidence, Chromium matrix and limitations.
- Await owner visual review of D3. D4 theme transitions remain separate; D5–D8 not started. No course publication or certificate activation authorized.

## Design roadmap — D2 complete (2026-11-24)

- D2 shared Graphite/Lime semantic tokens, accessible states, local multilingual font delivery, specimen and DESIGN.md completed. Evidence: docs/design/D2_DESIGN_SYSTEM.md. Existing page composition/feature behavior preserved.
- Next separately authorized D3: homepage and one original ASCII Scroll. D4 theme transitions, D5 catalog/course, D6 learning/Profile, D7 Studio, D8 final isolated regression remain pending. Old D1/D0 notes below are historical. No automatic publication/certificate activation.

## Design roadmap — D1 complete (2026-11-24)

- D0 checkpoint888317e on design/graphite-lime; D1 actual-browser visual audit complete with no UI edits. Current redesign sequence D0–D8 lives in docs/design/REDESIGN_ROADMAP.md; evidence and limits in D1_VISUAL_AUDIT.md.
- Next separate task D2: semantic Graphite/Lime system, multi-script font delivery, component states, both themes. D3: one original ASCII Scroll; D4: safe theme transitions; D5catalog/course; D6learning/profile; D7Studio; D8isolatedfinalverification.
- Existing auth/access/media/assessment/business rules remain fixed. Content/publication/certificate decisions from C5 are independent; no automatic publication or issuance in redesign.

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
