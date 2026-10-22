# Course 8 educational presentation refinement — 2026-10-22

Scope: frontend presentation only, branch `design/amethyst-motion`, starting at
`8da8148`. Existing uncommitted work was preserved. No SQLite content update,
migration, account changes, course import, dependency installation, commit or push.

## Per-lesson result

| Lesson | Student experience and source preservation |
| --- | --- |
| 91 | Existing exact cover-prefix filtering, seven semantic examples and nested AI/ML/DL/LLM hierarchy retained. Learning objectives and full definitions remain. Known section heading loses Word numbering only in presentation. |
| 92 | Five approved descriptions and verification warning unchanged; connected vertical timeline retained. Original explanation and limitations remain. |
| 93 | Full definitions, one comparison table and non-one-to-one relationship retained. Source GPT/ChatGPT example highlighted separately. Optional ungraded model/service self-check. |
| 94 | One five-row category table, multimodal caveat, five service cards with each description and official link once, final comparison advice retained. Requested capability-change notice added. Optional category self-check. |
| 95 | One always-visible five-step sequence. Eight-row task/capability table under Step 2; six criteria once under Step 3; full explanations under Steps 1, 4 and 5. Weekly-report scenario stays in Step 1. Optional comparison-method self-check. |
| 96 | Six exact instructions become an ordered list. Duration, task, weekly-report example and permission/anonymization warning remain. Redundant empty template/reference omitted only when verified structured assignment is present. Confidentiality guidance visible before form disclosure. Conclusions and references remain separate; existing quiz section stays outside practice, unchanged. |

Student progression is foundations → limitations → model/service distinction →
categories/services → selection method → applied comparison. Existing objectives
(explain, distinguish, select, justify) align with the final practical assignment.
Optional practice gives feedback after selection without saving, grading or
changing completion. Radio controls provide native keyboard interaction.
Educational material stays Russian with the existing fallback notice; all new UI
labels are localized RU/KK/EN.

## Safe duplicate handling

Known lesson IDs, course slug and fingerprints of complete source body and
interactions must match before curated rendering. Lesson96 additionally verifies
the structured assignment description. Unexpected teacher edits fall back to the
complete ordinary renderer. No global repeated-word suppression is used.

Production guards store only length/FNV-1a64 fingerprints, not protected lesson
prose. These detect accidental editorial drift and are **not** authorization or
cryptographic integrity checks. Rendering still consumes authorized API data.
Full educational snapshots are test fixtures only, not imported into production.
Original numbered source references remain unchanged; only eight exact known
headings lose `1.1.`–`1.8.` in student presentation. Lists and meaningful numbers
are unaffected.

No assignment submission, quiz grading, JWT, media or enrollment APIs were changed.
Existing save/submit controls and independent completion behavior were preserved.

## Remaining teacher review

- Lesson91 seven-paragraph database cleanup remains **unapproved/unapplied**.
  Existing exact before/after proposal includes course-level objective/outcomes,
  not merely cover metadata; review that scope before any future write.
- Service capabilities, plans, integrations and product examples are source
  snapshots; review factual updates separately rather than silently editing them.
- Lesson96 source reference includes `prompt-ingineering` in a URL. It is preserved
  pending source/link review.
- No other stored-text edits are proposed or applied. The new capability-change
  notice and practice prompts are requested presentation guidance, not verbatim
  DOCX quotations.

## Changed frontend files

- `pages/LessonView.jsx`, `pages/LessonView.css`: integration, visible heading
  normalization, ordered practice instructions and separation of source/form.
- `components/learning/Course8Reading.jsx`, `course8-reading.css`: verified source
  readings, cards, tables and selection timeline.
- `components/learning/PracticeCheck.jsx`, `learning.css`: optional local practice.
- `utils/course8Reading.js`, `course8Source.json`, `sourceFingerprint.js`,
  `sourceHeadings.js`, `lessonPresentation.js`: guarded normalization/deduplication.
- `i18n/locales/{ru,kk,en}.json`: practice interface labels.
- Regression tests: course8-reading, source-headings, practice-check,
  lesson-presentation, lesson-workspace; educational-only fixture in
  `tests/fixtures/course8Source.json`.

Paths above are relative to `frontend/src` except tests, relative to `frontend`.
Pre-existing `.codex/config.toml` and lesson91–92 validation work were preserved.

## Validation and reviewers

- Django check passed; 189 courses/progress/quizzes tests passed in isolated DB.
- Frontend regression suite, lint and production build passed; source drift,
  preserved objectives, one-table/link rendering, practice isolation and numbering
  distinctions are covered.
- Native frontend reviewer and independent educational-content reviewer used.
- Original DOCX SHA256 remains
  `940238198fb563ff9d1d857886f852dcfdf4cbb4b04d5ca2e3c7e8c431721cff`.
- Development SQLite file SHA256 matches the pre-task baseline. All existing
  educational records, enrollments, progress, submissions and attempts are intact.

## Firefox evidence

Native `browser_qa` ran Playwright MCP Firefox against the current live
`LessonMaterial` with real educational-only saved content in an isolated context.
32 layout cases passed (lessons93–96, widths1440/768/375/320, both themes), plus
12 RU/KK/EN checks. Normal/reduced motion and native radio Space/arrow navigation
were checked. Feedback appeared after interaction only. No horizontal overflow,
blank cards, empty tables, page errors or failed requests in the authoritative run.
Lesson96 had all six instructions. Main agent visually inspected93mobileDark,
95desktopLight and96mobileDark screenshots.

Screenshots:
`.playwright-mcp/course8-refinement-{93,94,95,96}-{1440,768,375,320}-{light,dark}-firefox.png`

Evidence: `.playwright-mcp/course8-refinement-browser-results.json`.
An initial larger QA loop stopped on an incorrect lesson96 test selector;
the corrected authoritative run above passed. This was not an application bug.

No authorized student session was available. Full authenticated workspace,
assignment persistence and real quiz submission were not browser-tested. Their
existing logic was preserved and relevant isolated regression tests passed.
