# Lesson 92: visible process rendering follow-up

Branch `design/amethyst-motion`, 2026-10-21. This follows the broader course audit and supersedes its selectable-process/shared-description presentation.

## Confirmed cause versus unresolved observation

**Confirmed rendering defect:** the previous `LearningContent.jsx` computed `sharedProcessText` when all step descriptions were equal, suppressed the description in every card, and showed just one generic paragraph. The real saved lesson 92 has five identical descriptions, so that branch definitely ran. Its selectable buttons merely changed a border; they supplied no additional teaching content.

**The reported invisible titles are not explained by verified evidence.** Current saved JSON contains five populated `title`/`text` pairs, and the actual Django serializer returns the same five steps. The previous source rendered all five titles in ordinary button spans. An independent CSS review found no applicable opacity, clipping, color, responsive, IntersectionObserver or Motion rule that hid those title spans. The exact original authenticated DOM could not be inspected: no authorized student session was available, and Playwright MCP's persistent Firefox profile was locked. No pre-fix screenshot of the reported numbers-only symptom was captured. A stale served implementation or a browser-specific state remains a hypothesis, not a confirmed root cause.

The original audit's screenshots/fixture successes must not be used as proof that the real student's title disappearance was solved.

## Renderer fix completed

- `llm_steps` now renders a semantic ordered list. Every stage has a persistent visible number, native `h4` heading and native paragraph for its currently saved description.
- No hover, pressed/selected state, button styling, reveal transition, IntersectionObserver callback or animation completion controls process text.
- Stage descriptions are no longer suppressed or merged, even when equal. **The current generic description consequently remains visible in each of the five cards.** Approved distinct teaching descriptions have not been injected into the frontend.
- Scoped grid layout, minimum-width handling, wrapping and explicit theme text colors keep heading/description content readable at mobile/desktop widths.
- Other learning selectors keep their existing native keyboard buttons; no unrelated quiz, practice, progress or authentication logic was changed.

Changed renderer files: `frontend/src/components/learning/LearningContent.jsx` and `learning.css`. Regression changes: `frontend/tests/learning-presentation.test.mjs` and `source-course.test.mjs`. Existing earlier uncommitted work is preserved.

## Real-data verification

- SQLite was read through a read-only connection. Course 8's existing learning-content record 2 for lesson 92 contains five valid stages. No account, credential, student submission or answer key was read for this diagnosis.
- A read-only call through the actual Django `/api/lessons/92/` serializer returned HTTP 200 and exactly the saved interaction JSON. This used an in-memory administrator preview identity with `PRAGMA query_only`, not an actual student login/session.
- Existing installed Playwright library launched Firefox in a fresh temporary context after MCP's persistent-profile lock prevented MCP execution. No dependency installation, profile deletion, process termination or authentication-token reuse was performed.
- The actual live Vite component and global CSS rendered the actual saved interaction—not invented step data. All API calls were blocked in the isolated component harness. This is a real-data renderer test, **not an authenticated full-LessonView test**.
- **16 cases passed:** 1440/768/375/320px × light/dark × normal/reduced motion. IntersectionObserver was inert before application import in all cases. Each case had five headings and five descriptions with positive bounding boxes, visible display/visibility, opacity 1, nontransparent theme text and no clipping. No horizontal overflow or page JavaScript errors. Mobile screenshots were visually inspected.

Evidence: `.playwright-mcp/lesson92-after-computed.json`.

Screenshots include:

- `.playwright-mcp/lesson92-after-1440-light-no-preference-firefox.png`
- `.playwright-mcp/lesson92-after-375-light-reduce-firefox.png`
- `.playwright-mcp/lesson92-after-320-dark-reduce-firefox.png`

Remaining matrix screenshots use the same width/theme/motion naming. Accessible text presence alone was not accepted as a passing visibility check; native headings/paragraphs, computed styles, layout boxes and actual screenshots were inspected.

## Content remains approval-gated

The existing course-wide proposal was read, and **only** its lesson-92 `interactions` edit was extracted into [lesson92-content-edit-proposal.json](lesson92-content-edit-proposal.json). It includes exact before/after values, the source checksum and canonical JSON checksums. Current saved content matches `before`.

[lesson92-content-application-plan.md](lesson92-content-application-plan.md) specifies backup verification, course/lesson guards, transactional/idempotent behavior, refusal of unexpected intervening edits and field-only rollback. No executable importer or database-write command was added or run. No proposal for lesson 91, 94 or 96 is authorized by this plan.

Teacher approval is required before replacing the current generic descriptions with the five distinct source-grounded descriptions. The renderer already supports both datasets; tests exercise both without applying either to the database.

## Checks and remaining acceptance

Relevant Django suite (`courses progress quizzes`): **184 tests passed**; Django system check passed. All **21 frontend test files passed**; lint is clean and production build passed. A prior test that required the old process buttons was updated to assert permanent headings/paragraphs, while a separate regression preserves keyboard buttons for other selectors.

SQLite's final byte hash matches the pre-task hash; integrity is `ok` and foreign-key violations are zero. No database content, account, lesson ID/order, quiz question/key, enrollment, progress, submission or attempt is modified. No migrations, commits or pushes.

**Still outstanding:** recheck `/lessons/92` in the affected student's actual authenticated session. The current renderer has been verified against the real saved data; the exact earlier title-hiding runtime cause and that student's end-to-end outcome must not be called confirmed without that check.
