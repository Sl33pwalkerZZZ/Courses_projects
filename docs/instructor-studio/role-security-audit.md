# Instructor Studio role-security audit

Recovery verification: 2026-10-20, branch `design/amethyst-motion`, HEAD `3e66255`.
The interrupted working tree was preserved, including the earlier Studio completion work. No reset, restore, clean, dependency installation, migration, commit or push was performed during this recovery.

## Root cause and explicit policy

A read-only query of the specifically requested account confirmed:

| Account | Stored role | is_staff | is_superuser | is_active |
| --- | --- | --- | --- | --- |
| almas | student | true | true | true |

The observed access was actual backend administrative authority through an existing Django superuser override, not merely a visible link or an obsolete JWT role claim. The old identity display did not explain that effective authority. No real account or privilege was changed. An active superuser intentionally retains administrator authority even when the stored role says student; the frontend now explicitly labels that override.

Studio authorization now has one policy: active `author` users can manage their own courses; active trusted `admin` users and active Django superusers can administer Studio. `is_staff` or Django course model permissions alone do not grant Studio access. Ordinary registration still forces the student role. Changing this policy does not remove existing Django superuser privileges.

| Capability | Student | Staff/student, not superuser | Author | Admin role | Active superuser/student |
| --- | --- | --- | --- | --- | --- |
| Public catalog and normal enrolled learning | Yes | Yes | Yes | Yes | Yes |
| Studio dashboards and management APIs | No | No | Yes | Yes | Yes |
| Private course management/preview | No | No | Own courses | All courses | All courses |
| Publication request | No | No | Own courses | Yes | Yes |
| Publication approval/rejection | No | No | No | Yes | Yes |
| Grant/revoke ordinary instructor role | No | No | No | Yes | Yes |

Inactive users have no Studio authority. Course publication locks, source/assessment approval guards, validation and enrollment requirements for learner progress remain applicable; administrator preview does not manufacture personal enrollment or progress.

## Backend implementation

- `studio/permissions.py`: central active-user, instructor and moderator predicates plus explicit effective capabilities. Identity includes the unchanged stored role, effective role, staff/superuser flags and authority source.
- `studio/services.py`: deny-by-default owner-scoped course queryset; only administrators receive the all-course queryset. Existing nested-resource ownership and transactional publication checks are retained.
- `studio/views.py`: all management endpoints require instructor authorization; moderation and role management additionally require administrator authority. Role writes accept exactly the `role` field, only allow student/author transitions and refuse privileged targets. They cannot grant admin, staff or superuser status.
- `users/serializers.py`: the authenticated user's own identity response exposes the same effective capabilities. Registration and existing JWT endpoints remain unchanged.
- `courses/permissions.py`: legacy preview, lesson and protected-image rules use the same administrator/owning-author policy; staff/student model permissions no longer bypass it. Normal enrollment remains an independent valid lesson-access path.

`GET /api/studio/me/` is intentionally a safe authenticated capability-discovery endpoint available to students too. It returns their own identity and denied capabilities, not courses or teacher data. Unsupported mutation methods return 405. Other Studio endpoints deny ordinary students. Existing `/api/auth/me/` remains read-only.

SimpleJWT resolves the current database user on each authenticated request. Stored role changes therefore affect the next API authorization check, including requests using an older token; arbitrary JWT role claims are not authority.

## React implementation

- `frontend/src/utils/instructorIdentity.js` and `hooks/useInstructor.js`: shared capability cache keyed by authentication-session generation, concurrent identity-request deduplication and rejection of obsolete responses.
- `frontend/src/App.jsx`, `pages/instructor/InstructorStudio.jsx`, `components/Header.jsx`: every `/instructor/*` route, including legacy preview and unknown instructor paths, is gated by explicit backend `can_access_studio`. Administrator routes are gated before page components mount. Denied users receive translated accessible 403 states; anonymous users retain login redirects.
- `pages/instructor/CourseEditor.jsx`, `Publication.jsx`: authors see My Courses; moderators see All Courses. Administrator controls use server capabilities. The Studio heading displays the effective role and explicit superuser override.
- `components/instructor/useStudio.js`: existing abort/session isolation is preserved; 403 responses trigger capability revalidation. Capability changes remount private Studio state.
- `i18n/locales/{ru,kk,en}.json`: matching effective-role, override, denied-access and administrative labels. Theme and learner UI behavior remain intact.

Account changes immediately hide old identity state, and late account-A responses cannot publish into account B's cache. Same-account authority is revalidated on focus/visibility, navigation subject to a 15-second cache, foreground 60-second polling and explicit permission-change/403 events. Failed identity refresh removes cached authority and offers retry.

## Regression and validation results

Fresh recovery runs completed successfully:

- `.venv/bin/python manage.py test --verbosity 1`: **265 tests passed** in an isolated temporary test database. Includes existing enrollment, quizzes, protected media, imports and publication workflow regressions.
- `.venv/bin/python manage.py check`: no issues.
- `.venv/bin/python manage.py makemigrations --check --dry-run`: no changes detected.
- `.venv/bin/python manage.py migrate --plan`: no planned operations. No migrations were applied.
- Frontend `node --test tests/*.test.mjs`: **18 test files passed**, no failures/skips.
- Frontend `npm run lint`: passed.
- Frontend `npm run build`: passed, 2,510 modules transformed.
- `git diff --check`: passed.

New `studio/test_role_security.py` has nine focused tests with temporary users for anonymous, student, staff/student with course model permissions, author A/B, nonstaff admin, superuser/student and inactive authority. It checks all five HTTP verbs against 24 management paths for unauthorized identities (480 denied-request assertions), foreign nested IDs, owner-only listing, read-only identity discovery, role mass assignment, privileged targets, stale/forged JWT role claims, refresh after role revocation and normal learner enrollment/access. The existing staff-preview regressions were updated to assert the intentional stricter Studio-role policy in `courses/test_media.py`, `courses/test_first_course_import.py` and `progress/test_enrollment_requests.py`; administrator authority tests in `studio/tests.py` reflect the trusted admin role.

New `frontend/tests/instructor-permissions.test.mjs` covers explicit capability checks, concurrent requests, account switching, late responses, logout, same-account permission revocation, failed refresh and retry. Existing session-isolation tests also pass.

## Independent reviews and Firefox limitation

Native `security_reviewer`, `frontend_reviewer` and `browser_qa` agents actually ran again during recovery. Security and frontend reviewers found no blocking issues in the changed authorization/session paths. Their reviews were read-only; the main agent ran the full checks above.

Current Firefox validation **could not run**: `.codex/config.toml` configures Playwright with Firefox, but no connected Playwright MCP/browser tools are exposed in this resumed session. Browser QA verified that limitation and installed nothing. Reconnect the configured MCP server in a trusted session before claiming browser acceptance.

Prior interrupted-run artifacts exist, but are not a completed or current passing browser report:

- `.playwright-mcp/role-student-1440-light.png`
- `.playwright-mcp/role-student-320-dark.png`
- `.playwright-mcp/role-author-1440-light.png`

Saved `role-fixture-setup.mjs`, `role-browser-matrix.mjs` and `role-browser-functional.mjs` describe synthetic permission/account-switch checks and a planned 72-case viewport/language/theme matrix. No completed result artifact exists. Current Firefox layout, keyboard, console/network, account-switch and deep-route checks remain unverified. Use isolated synthetic intercepted APIs, not real account mutations, when resuming them.

## Data safety and remaining boundaries

Read-only SQLite verification reports integrity `ok`, zero foreign-key violations and nine existing courses. Course 8 remains unpublished with six lessons, draft quiz 3 containing 15 questions and unapproved import provenance. No existing user, educational content, progress, quiz attempt, enrollment, media file or publication state was changed. A read-only aggregate count/hash snapshot of all tables was used to verify no changes during final recovery verification; no personal row contents or credentials were exported. The supplied external recovery archive was left untouched.

Django Admin remains a separate staff/model-permission control plane. A staff/student deliberately granted Django model permissions can retain corresponding Django Admin access. Existing enrollment-request Admin approval also retains its staff-plus-model-permission policy. This fix restricts Studio and shared protected lesson/preview APIs; it does not silently revoke existing Django Admin grants.

Same-account server-side role changes can leave old navigation visible until capability revalidation; backend access is denied immediately on the next request. Browser acceptance remains pending for the connection reason above. No real account was downgraded to make the observed superuser behave like an ordinary student.
