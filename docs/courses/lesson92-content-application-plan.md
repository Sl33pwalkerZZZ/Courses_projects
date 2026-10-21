# Lesson 92: approval-gated content application plan

**Applied with explicit teacher approval on 2026-10-21.** Only lesson 92’s five step descriptions and source note were updated. See [the application report](lesson92-approved-content-update.md). The guarded procedure below records the approved plan.

Target: course 8 → lesson 92 → existing `LessonLearningContent` record 2 → **only `interactions`**. The exact before/after values are in [lesson92-content-edit-proposal.json](lesson92-content-edit-proposal.json), extracted from the existing five-change course proposal. The current read-only database value matches its `before` value.

The proposed five stage descriptions were reviewed against DOCX P26–28: user request; tokenization/context; model processing using learned patterns; sequential token generation; a result that requires verification. They add no claims about hidden reasoning, a particular architecture, guaranteed correctness or external tool usage. The source's non-guarantee caveat is retained once as a note. These are proposed teaching words, not content already published by the renderer fix.

## Preconditions after explicit teacher approval

1. Confirm approval names **lesson 92 only** and the proposed after checksum. Do not apply the broader course proposal.
2. Verify course 8, lesson 92's membership and record 2 still exist, the interaction is `llm_steps`, and there are exactly five stages in the same order. Verify the original DOCX checksum.
3. Create a fresh consistent SQLite backup using the online backup API and verify its integrity. Do not replace/reset the live database. Keep backups private and outside version control.
4. Record count/hash baselines without exporting student records. Preserve all courses, IDs, bodies, quiz 3/questions/keys, enrollments, progress, attempts and submissions.

## Idempotent decision and transaction

- Compare parsed JSON structurally using canonical UTF-8 JSON (sorted keys, separators `(',', ':')`, `ensure_ascii=False`), with checksums from the narrow proposal.
- If the current `interactions` already equals the proposed `after`, return **already applied / no writes**.
- If current content differs from both `before` and `after`, **abort without writes**. Never overwrite a teacher's intervening edit or append a duplicate interaction.
- Otherwise re-read and check inside a short database transaction, with course/lesson identity guards and concurrency protection appropriate to SQLite. `select_for_update` alone is not a SQLite write lock; a competing writer or changed content must abort/retry from a fresh guarded read, not be overwritten.
- Update exactly the existing record's `interactions` field. Preserve the interaction type/title, five stage titles/order, all other model fields and all other records. Do not call an importer, recreate records, publish/unpublish anything or apply changes for lessons 91, 94 or 96.
- Validate the written value and unchanged protected baselines before treating the operation as successful. If any invariant fails, roll back the transaction.

## Verification and rollback

Read the actual lesson API and verify five unchanged titles, the five approved descriptions and one source caveat. Check desktop/mobile visible headings/paragraphs, normal/reduced motion and authenticated student access when an authorized session is available. Verify a second application is a no-op and an unexpected edited input is refused in isolated tests first.

If a later rollback is required, restore **only this field** from the recorded `before` value, in a transaction guarded by an exact match to the expected applied `after`. Never restore an entire old SQLite file over newer student progress, submissions or attempts.

The current frontend fix displays each **currently saved** stage description, even when the descriptions are identical. It does not inject this proposal into the published page. The five distinct teaching descriptions have now been explicitly approved and applied; all other course proposals remain unapproved.
