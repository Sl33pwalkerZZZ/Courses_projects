# Lessons 91–92 checkpoint validation — 2026-10-22

Started with a clean working tree on `design/amethyst-motion`, HEAD `8da8148`.
The requested renderer work was already saved in that checkpoint; it was preserved.

## Lesson 92

`LearningContent.jsx` and `learning.css` render an ordered, connected vertical
timeline at every width. All five headings and descriptions are ordinary visible
text, without hover, selection, scroll observer or animation dependencies.
Read-only SQLite verification found five distinct descriptions and exact equality
with the approved lesson92 proposal's `after` interactions. No content was reapplied.

## Lesson 91: presentation and pending content proposal

Existing presentation code hides only the exact verified seven-paragraph opening
for lesson91 in the expected course. Any changed prefix or section heading falls
back to the complete source. Examples retain their exact wording in a semantic
list, and the concept hierarchy uses nested lists.

New regression tests cover exact-prefix matching, other lesson/course fallback,
teacher edits, input immutability and lossless example grouping.

`scripts/lesson91_title_page_cleanup.py --dry-run` reported `ready — NO WRITE`.
The proposal is **not applied or approved**. Its exact diff is
`docs/courses/lesson91-content-edit.diff` and full before/after values are in
`docs/courses/lesson91-content-edit-proposal.json`.

It removes seven opening paragraphs: chapter marker, document title, course
attribution, date, objective/outcomes heading, objective paragraph and outcomes
paragraph. This includes course-level introductory educational objectives, not
only cover metadata. Approval must cover that full scope; alternatively narrow
the proposal before approval. Every paragraph from section 1.1 onward remains
byte-for-byte unchanged. The original DOCX remains intact.

Before any future approved application: create a fresh verified SQLite backup,
verify source checksum and exact before text/course membership, then use the
transactional script's explicit approval and backup checksums. Unexpected source
or database changes reject the update; an already-applied exact result is a no-op.
Only lesson91.text_content is permitted to change. No apply command was executed.

## Validation

- Django system check: passed.
- Django courses tests: 61 passed in isolated test database.
- Cleanup-script tests: 5 passed using isolated fixtures, including refusal,
  rollback and idempotency cases.
- Frontend suite: passed; lint and production build passed.
- Independent native `frontend_reviewer`: no blocking source findings; identified
  missing presentation guard tests, now added.
- Read-only SQLite integrity: ok; foreign-key violations: zero.
- Course8 remains published, with lessons91–96. Development SQLite file SHA-256
  unchanged during validation, preserving quizzes, progress and other records.

## Fresh Firefox verification

Native `browser_qa` used Playwright MCP Firefox with an isolated context at the
live Vite server, mounting the current `LessonMaterial` renderer with saved real
educational data. No authorized student session was available: this verifies
rendering, not the complete authenticated student flow.

At 1440, 768, 375 and 320px, both themes, all five distinct lesson92 explanations
were visible with opacity1, visible visibility and positive bounding boxes.
Stages had the same horizontal position, increasing vertical positions and
2px connectors. No horizontal overflow; reduced motion was tested.
Screenshots: `.playwright-mcp/lesson92-checkpoint-{width}-{light,dark}-firefox.png`.
The main agent also visually inspected the 375px dark screenshot.

Final browser matrix: 96 cases (both lessons, four widths, two themes, three
languages and both motion preferences), zero failures, page errors or failed
requests during the matrix. Lesson91 cover metadata was hidden and seven examples
were visible. Its screenshots use `lesson91-checkpoint-{width}-{theme}-firefox.png`.

A final working-tree check also found a new `.codex/config.toml` MCP tool approval
setting. The main agent did not edit that configuration and preserved it.

No migrations, installations, commits or pushes.
