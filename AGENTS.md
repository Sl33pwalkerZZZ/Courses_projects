# AI Courses project guidance

This is an existing Django REST/SQLite + React/Vite educational platform.
Preserve JWT, enrollment approval, protected lessons, independent lesson/quiz
completion, Profile activity, reviews, RU/KK/EN, and dark/light Neo-Academic UI.

## Delegation

- Delegate independent reviews when the user requests multi-agent work or a
  substantial change needs UI, security, or browser verification. Keep small
  single-file tasks local. The main agent owns scope, edits, and the final report.
- Use `frontend_reviewer` for React/UI/responsive/accessibility/theme/i18n reviews;
  `security_reviewer` for Django/JWT/enrollment/lesson/quiz authorization reviews;
  `browser_qa` for actual frontend checks with Playwright MCP when connected.
- Definitions are in `.codex/agents/*.toml`. Give each agent a bounded task,
  files/URLs to inspect, expected evidence, and the read-only audit constraint.
  Run independent reviews in parallel within the configured three-child limit.
  Reviewers must not spawn additional agents unless explicitly assigned.
- Collect the requested results and report which agents actually ran. If a
  session cannot select custom roles, say so; manually passing their instructions
  to a subagent is not proof that native TOML role selection worked.

## Audit boundaries

- Reviews are read-only: no application edits, DB mutations, migrations, seeds,
  resets, commits/pushes, dependency installations, or automatic external skills.
- Existing educational content and student progress belong to their maintainers.
  Do not change courses, modules, lessons, quizzes, enrollments, or attempts in
  an audit. Later implementation requires a task that explicitly authorizes it.
- Do not read or reveal student records, credentials, private quiz imports, or
  database backups. Database access, if necessary, must use read-only connections.
- Initial browser QA uses isolated public browsing; do not submit mutating flows
  or log in/register against the development DB. Mark protected flows untested
  unless an appropriate read-only test session/environment is supplied.
- A missing Playwright MCP is a reported setup limitation. Do not auto-install
  it or fabricate screenshots, console results, or passing browser checks.
- Return prioritized findings with file/line or browser evidence and distinguish
  observed failures, static risks, and checks that could not run. Report no
  findings when justified; do not invent issues to fill a review.

## Local setup

Use a trusted project and a fresh Codex session after changing agent definitions.
Model/reasoning settings inherit from the existing user configuration. Native
custom-agent discovery and available MCP tools must be verified in that client;
the files alone do not establish runtime availability. Preserve existing configs.
When needed, Django uses `.venv/bin/python`; frontend tooling is in `frontend/`.
If Node/npm are missing from PATH, use the existing NVM installation; do not install replacements.
