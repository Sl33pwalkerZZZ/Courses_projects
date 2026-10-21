# Lesson 92: approved descriptions applied

Applied on 2026-10-21, branch `design/amethyst-motion`, following the user's explicit approval. No commit or push.

## Exact scope

Existing course **8**, lesson **92**, `LessonLearningContent` record **2**, JSON field `interactions[0]` only:

| Unchanged stage title | Approved `steps[].text` now stored |
| --- | --- |
| Запрос пользователя | Последовательность начинается с запроса пользователя. |
| Разбиение на токены и обработка контекста | Запрос разбивается на токены — части слов, слова и другие текстовые элементы; обрабатывается контекст запроса. |
| Вычисления языковой модели | Языковая модель обрабатывает контекст, используя закономерности, обнаруженные при обучении. |
| Генерация ответа | Ответ генерируется последовательно, с выбором токенов. |
| Результат для пользователя | Пользователь получает ответ, достоверность которого необходимо проверить. |

Added the approved interaction `note`: **Сама языковая модель не гарантирует достоверность информации и не всегда имеет доступ к текущим событиям.** This is supported inside the existing JSON field, serialized by the existing API and displayed by the existing renderer. No migration was needed.

The previous generic description was identical in all five stages. The applied strings are exactly those in the lesson-92 change from `course8-content-edit-proposal.json`. Before applying, a structural guard reconstructed the proposed result using only these five text replacements and the note, then rejected any other proposed difference.

## Backup before writing

Private, Git-ignored SQLite online backup:

`.local-course-backups/lesson92-approved-20261021T063559747489Z/db-before.sqlite3`

SHA-256: `6f6ecdbbd0c7c46c94c834f20bdee4efa12b95d7496a59f415f753b2ad148bc6`.

Integrity: `ok`; foreign-key violations: **0**. The verified backup matched the live database across all **35 tables**, including counts, row hashes and schema. Verification metadata is alongside the backup in `verification.json`; no personal row contents were printed or included in this report.

## Transaction, guards and preservation

Verified course membership, published status, existing learning-content ID, all five old texts and the original DOCX checksum before writing. Used SQLite `BEGIN IMMEDIATE`, rechecked the exact pre-update state and backup baseline under the write lock, and updated only the existing record's `interactions` column. The transaction checked the approved result, all protected data and database integrity before commit.

Every other field and row, every table count and the schema match the verified pre-update backup. This includes all other lessons, lesson IDs/titles/order/bodies, objectives/source metadata, source DOCX, course publication flags, quiz 3/questions/answer keys, assignments, users, enrollments, progress, attempts and submissions. No import or record recreation ran. Other proposed changes for lessons 91, 94 and 96 were not applied.

Repeated the guarded application after commit: it returned **already applied / no write**, and SQLite's byte hash remained unchanged. Guard self-tests rejected unexpected intervening text/title values and verified rollback and unrelated-field preservation using an in-memory fixture database.

## API and renderer verification

- Actual Django `/api/lessons/92/` endpoint against the real database returned HTTP 200 and the exact approved JSON, with five different descriptions and the note. This read-only endpoint check used an in-memory administrator preview identity, not a real account mutation or issued credential.
- Browser data was refreshed from that response, not from the proposal or a stale generic fixture.
- Connected Playwright MCP Firefox rendered the current live Vite component and global styles with the updated saved API data in **16 cases**: 1440/768/375/320px × light/dark × normal/reduced motion. IntersectionObserver was disabled. Five headings and five exact distinct descriptions were visibly readable with nonzero bounding boxes, opacity 1, visible display, no clipping and no horizontal overflow. No JavaScript/console errors or failed requests. Mobile screenshot was also visually inspected.
- Screenshots: `.playwright-mcp/lesson92-approved-1440-light-no-preference-firefox.png`, `.playwright-mcp/lesson92-approved-375-light-reduce-firefox.png`, and the remaining width/theme/motion combinations.
- Full computed browser evidence: `.playwright-mcp/lesson92-approved-results.json`.

A full authenticated student's browser session was not available; browser checks exercised the real updated educational data in the actual renderer. An already open `/lessons/92` page should be refreshed to fetch the newly saved text.

## Tests

- Relevant Django suite (`courses progress quizzes`): **184 passed**, isolated test database.
- Django system check: no issues.
- Frontend renderer/source/workspace regression files: **3 passed**.
- Frontend lint: clean; production build passed.
- Post-test verification compares all protected rows/fields and the post-update byte hash again; no test changed the live database.

All prior uncommitted application changes were preserved. This task added no application-source or schema changes.
