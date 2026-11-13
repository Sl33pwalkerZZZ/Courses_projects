# Root AGENTS.md Integration Proposal

**Status:** Review proposal only. The repository root `AGENTS.md` already exists and was left unchanged, as required by the Phase 5 safeguards.

## Existing guidance

The current root file already covers platform invariants, delegation policy, read-only audit boundaries and local setup. It does not currently direct a new session to the project-memory knowledge base or require regular memory updates.

## Safe additive integration

After explicit approval, append a short section (do not replace existing text):

```markdown
## Project memory

- Before development, read `docs/project-memory/CURRENT_STATE.md` and check `git status`.
- Read the relevant `docs/project-memory/` pages and linked audit reports; treat dated database/runtime facts as snapshots.
- Preserve all uncommitted and untracked work. Never reset, clean or discard it without explicit permission.
- Keep Course 10 unpublished unless explicitly authorized; follow canonical source and isolated-database rules.
- After a substantial phase, update `CURRENT_STATE.md` and record durable decisions in `DECISIONS.md`.
- Never include secrets, credentials, learner data or backup contents in project memory.
```

This is a proposal; no existing instruction text was changed. Reconcile it with the current file rather than appending duplicate wording if approved.

Before applying the proposal, also resolve the existing visual-language wording: the root file says “Neo-Academic UI,” while the approved Phase 1–3 redesign documentation identifies the current interface as Amethyst Motion/Cinematic. Update that phrase only after confirming the intended maintained visual identity; do not preserve a stale description by silently replacing a different one.
