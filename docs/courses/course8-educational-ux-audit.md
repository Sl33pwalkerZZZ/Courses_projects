# Course 8: educational UX and presentation audit

Date: 2026-10-21. Branch: `design/amethyst-motion`.

## Scope and evidence

Authoritative source: `course_sources/Глава_1_Выбор_ИИ_модели_и_сервиса.docx`. Read the original Word XML and its four tables, the published course's six lesson bodies and learning-content JSON, Assignment 1's instructions, and the published student-facing quiz question/choice fields. No correct-answer flags or private student work were exported.

The imported lesson bodies preserve **all 88 nonempty source paragraphs verbatim**, plus all four tables as pipe-text fallbacks. There are no added non-table prose paragraphs in the stored lesson bodies. The source has **zero embedded media files/drawings**, and lessons 91–96 have no LessonImage records. Missing source image files therefore do not explain lesson 92.

The raw source is faithful to the DOCX. The added layer consists of lesson objectives, interaction titles and data, an editable digital practice map, and interface copy. The main educational problem is presentation/repetition in that added layer, not evidence that the source bodies were fabricated. Factual currency of externally referenced products was not independently certified; source qualifications were preserved.

Read-only calls through the actual Django lesson API returned HTTP 200 and the expected interactions for all six lessons, using an in-memory administrator preview identity under SQLite `query_only`. No account/session/token was created. This verifies actual serializer output, not authenticated student browser access.

Firefox could browse the actual public course at `http://localhost:5173/courses/kak-vybrat-neyroset-pod-svoyu-zadachu/`. It started without an authorized student session. No credentials were requested, read, logged or minted, and no real login was attempted. Protected rendering/persistence checks used the real educational payload with isolated, fail-closed simulated authentication, enrollment, progress and mutation responses. They must not be described as actual saved student work.

## Findings by lesson

| Lesson | Confirmed issues | Applied presentation improvement | Content decision still requiring approval |
| --- | --- | --- | --- |
| **91 — Что такое искусственный интеллект** | DOCX chapter cover, date and course-wide outcomes precede the lesson. Lesson outcomes follow the prose in the old UI. Full definitions repeat in the added hierarchy. | Lesson objectives now precede reading; source section headings have semantic hierarchy; unnecessary generic implementation preface removed. All source definitions and cover paragraphs remain available. | Relocate source cover/course-wide outcomes to a teacher-approved overview/reference location. The proposed lesson-body change is conditional on retaining that material elsewhere. |
| **92 — Как работают современные языковые модели** | Five valid steps exist, but each has the identical generic disclaimer instead of a stage-specific explanation. The old selector/detail design provided little visual sequence and repeated the same text when selecting stages. A fully blank panel was not reproduced with an authorized real student session. | Persistent semantic five-stage process cards, visible independently of an opacity animation. Shared explanation appears once; distinct supplied explanations remain supported. Source limitations are unchanged. | Teacher approval for distinct source-grounded step descriptions. Do not claim the current frontend invented richer explanations. |
| **93 — Разница между ИИ-моделью и ИИ-сервисом** | Stored content includes a pipe-text table plus the same native comparison table. This is duplicate storage, **not proof of two visible tables**: existing exact-table fallback suppression already prevents that. | Retained accessible native table, source paragraphs and the important many-models/many-services qualification; improved source heading hierarchy. | No factual rewrite needed. Optional editorial shortening should be reviewed separately. |
| **94 — Виды нейросетей и обзор популярных сервисов** | Service prose repeats in cards; category information is available in both choice details and its full table. Added heading literally says the information requires checking “before publication”, although the course is published. | Exact editorial heading is displayed using the DOCX heading “Обзор популярных ИИ-сервисов”. Table/link behavior and all source caveats remain. | Persisting the corrected heading requires approval. Do not remove the qualifications about changing features, accounts/licenses, independent verification or no universally best service. |
| **95 — Методика выбора ИИ-инструмента** | Step 2 really has `text: ""`; its task/function table was placed outside the active detail. Step 3 repeats criteria also listed below. Five source steps are restated in the digital selector. | Selecting the verified second step places its actual source task/function table inside the detail, with no second copy below. Association is tightly guarded by the exact type, title and headers; no explanation is invented. | Future editorial consolidation of repeated steps/criteria needs teacher review. Empty step 2 does not justify adding unsourced factual text. |
| **96 — Практическая работа: карта выбора ИИ** | Prose instructions, a blank source map and the structured form compete with example, conclusions, seven resources and the quiz. Raw pipe-text map is already suppressed when its exact native equivalent exists; the visible redundancy was principally native blank map versus editable form. Assignment description contains digital-implementation provenance. | One clearly labelled practice entry; original map/instructions retained in a closed source-reference disclosure. The form opens explicitly. Timing, six instructions, worked example and safety guidance remain. Conclusions follow practice; resources stay accessible in a separate disclosure; the existing quiz has a distinct panel. Exact implementation provenance is removed from display, not storage. | Optional storage cleanup and assignment-description cleanup are proposed only. Do not delete the source template or original instructions. |

DOCX trace: chapter cover/outcomes P1–7; AI explanation P8–24; LLM sequence/limitations P25–34; model/service P35–38 and table 1; categories/services P39–53 and table 2; selection method P54–69 and table 3; practice P70–80 and table 4; conclusions P81–84; resources P85–92. These labels follow source body-element positions, including tables; there are 88 nonempty prose paragraphs.

## Lesson 92: what is known about the blank report

There is no missing `steps` array, schema mismatch or missing DOCX diagram. All five titles and texts are present in SQLite and delivered through the actual serializer. The old component already read `interaction.steps`, so blaming an unrecognized JSON field would be incorrect.

The confirmed defect was an ineffective selector/detail presentation: every stage showed the same generic text and there was no persistent visual process. The old detail also used an initial opacity animation. That animation dependency was removed for robustness, but it was **not established as the cause** of the reported fully blank real-session experience. Protected baseline browser access was unavailable, so the exact original runtime disappearance remains unconfirmed. The new sequence is visibly rendered and regression-tested at every requested width.

## Navigation and duplication

- Lesson rendering has one H1, one responsive outline disclosure and one course-progress element. Mobile closes that same disclosure instead of rendering a second navigation tree. Closed contents can still appear in copied `textContent`, but are not visible or exposed as open navigation.
- Public CourseDetail uses one semantic screen-reader title plus an `aria-hidden` animated visual title. Firefox confirms one accessible title and no doubled visual title. This correct accessibility structure was retained.
- Sidebar contents and previous/next navigation were two different landmarks with the same accessible label. The sidebar now uses the existing outline label; this distinguishes their purpose without deleting navigation.
- Course/module context and the current lesson title serve different purposes. They were not removed merely because copied text contains both.

## Frontend-only changes

- `components/learning/LearningContent.jsx`, `learning.css`: persistent process visualization, repeated shared explanation once, omission of empty interaction shells, removal of `learning.authoredActivity` technical preface, contextual source table for lesson 95 and Amethyst-compatible process styling.
- `utils/lessonPresentation.js`: pure, non-mutating presentation helpers; exact source-template identification, exact editorial title/provenance handling and conservative final-lesson sectioning.
- `pages/LessonView.jsx`, `LessonView.css`: objectives first, semantic source headings, one structured practice disclosure, preserved source reference, conclusions/resources hierarchy and separate existing quiz panel. Authentication, completion and quiz logic were not rewritten.
- `components/LessonCourseSidebar.jsx`: distinct contents landmark name.
- RU/KK/EN locales: translated practice controls. Browser QA also found the pre-existing literal `common.cancel` in practice confirmation; it now has translations in all three languages.
- Regression tests: new `learning-presentation.test.mjs`, new `lesson-presentation.test.mjs`, and additions to `lesson-workspace.test.mjs`.

The form still explains that it stores work in AI Courses without calling external AI services. This is relevant data-handling guidance, not the removed implementation provenance. Confidentiality, anonymization and source-verification warnings remain.

## Proposed published-content edits — approval required

See [`course8-content-edit-proposal.json`](course8-content-edit-proposal.json) for **exact current/proposed values**, source checksum, existing record targets and preservation conditions. It is not an executable importer or authorized database update.

1. Conditional relocation of lesson 91's chapter introduction and course-wide outcomes; retain them in an approved overview/reference destination before changing the lesson body.
2. Five distinct lesson 92 stage descriptions derived only from source P26–28, with the non-guarantee caveat once.
3. Persist lesson 94's neutral DOCX-based service heading.
4. Optional removal of lesson 96's duplicate pipe-text map only; retain the existing JSON source map, reference access and DOCX.
5. Persist assignment-description cleanup while retaining the task and confidentiality warning.

One source URL contains `prompt-ingineering-best-practices-for-chatgpt`; its correctness requires verification and teacher approval before correction. It was not silently rewritten.

No restructuring into six modules is justified. Keep the existing one-module/six-lesson progression. None of these proposed database edits has been executed; explicit approval is required first.

## Validation and boundaries

- Full Django suite: **271 tests passed**, using temporary databases. Includes access, enrollment, practical drafts/submission validation, independent completion/progress, quiz grading/attempts and protected media.
- Frontend: **21 test files passed**, including renderer, exact presentation deduplication, source preservation, translated controls, draft validation, progress/error and session regressions. Lint is clean and production build passed (2,512 modules).
- Django system check passed. No migrations, dependency installations or database writes were required.
- Native frontend review found the initial practice translations in the wrong nested namespace; fixed, with root-key and rendered-material regressions. Final recheck found no blockers. Independent educational-content review found no lost source explanations or unsupported factual additions.
- Actual public Firefox checks: 24 width/language/theme cases (1440, 768, 375, 320 × RU/KK/EN × light/dark), without horizontal overflow or JavaScript errors.
- Protected Firefox checks: real educational payloads with isolated API fixtures. Lesson 92's process and lesson 96's practice/navigation/quiz layout passed 48 validated cases with the actual document language/theme asserted. An earlier fixture matrix reset preferences on every load and was excluded from these totals.
- Fixture draft-save failure preserves entered work; success/reload restores it. Completion failure does not show a completed badge; successful completion and reload restore one. Lesson 95's second-step table appears inside the active detail and not twice. Original saved student work was never edited to perform these checks.
- Fixture practice submission confirms and persists as pending/read-only after reload; cancellation sends no POST and uses translated copy. The fixture quiz accepts 15 answers through the actual review/submission UI, displays a simulated saved result and restores its attempt history after reload. These intercepted responses test frontend behavior, not correctness against real answer keys. Keyboard process selection, mobile disclosure activation and one current-lesson indicator also passed.

Current screenshots are under `.playwright-mcp/`: `course8-public-before-1440-firefox.png`, `course8-public-before-320-firefox.png`, and `course8-<92|96>-<1440|768|375|320>-<light|dark>-after-firefox.png`. The file named `course8-96-audit-initial-firefox.png` was overwritten during fixture setup and must not be presented as a protected before screenshot.

Consolidated browser evidence: `.playwright-mcp/course8-browser-audit-results.json`.

There was no authorized real student browser session. Actual student save/submit/quiz/progress end-to-end persistence was therefore not certified by browser QA; isolated backend tests and browser fixtures are separate evidence. Correct-answer keys and real grading content were not put into frontend fixtures.

All earlier uncommitted Instructor Studio/enrollment work was preserved. No courses, lesson bodies, assignments, questions, answer keys, enrollments, progress, submissions, attempts, users or media were modified. SQLite's final byte hash is compared to the pre-audit hash; integrity and foreign-key checks are included in final verification. No commit or push.
