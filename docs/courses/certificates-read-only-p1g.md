# P1G — private reads of existing issued certificates

2026-11-13, Asia/Almaty. Scope: read existing snapshots without enabling issuance. Real SQLite, policies, users, courses and media were not changed.

## Exact read/write separation

| Endpoint / workflow | With CERTIFICATES_ENABLED=False | Boundary |
|---|---|---|
| GET/HEAD `/api/my/certificates/` | Available | Authenticated, own records only; issued/revoked snapshots retain their stored status; no eligibility recalculation or name reconfirmation required. Empty owner list returns200 `[]`. |
| GET/HEAD `/api/certificates/<code>/download/` | Available subject to existing guards | Owner or already-authorized moderator only; other user404; revoked/unverified403; trusted origin and PDF runtime/font guards unchanged. PDF generated in memory; no issuance or record save. |
| Existing certificate details | Supplied by the own-list schema | No separate detail route exists; none added. |
| `/api/courses/<id>/certificate-status/` |404 | Eligibility/status remains gated; unpublished-course restrictions unchanged. |
| `/api/certificates/verify/<code>/` |404 | Public behavior intentionally NOT broadened. |
| POST `/api/certificates/admin/issue/` and `/revoke/` |404 after authentication | Existing feature-gated API base retained. Both service functions reject disabled mode independently. |
| Django Admin certificate list/detail and policy list/detail | Authorized read-only view | Staff moderator permissions remain; issued snapshot fields immutable. |
| Admin issuance form; policy add/change; revoke action | Denied/hidden while disabled | Issue GET/POST403; policy add/change denied, view retained; revoke action hidden and service rejects direct calls. |
| `/api/my/certificate-name/` | Existing behavior unchanged | Student-owned GET/PUT/POST confirmation is deliberately separate from issuance; no change in this task. |

Only MyCertificates and DownloadCertificate inherit the new ungated authenticated `PrivateCertificateReadView`. The gated `CertificateView` still controls all other existing certificate API routes. All private read responses, including errors, retain `Cache-Control: private, no-store`. No user/course IDs are hardcoded. Unsupported write methods on the two read routes return405.

Admin policy preconfiguration and Admin revocation previously remained possible with the flag false. To satisfy P1G's read-only requirement, these paths are now explicitly locked in disabled mode, while flag-on authorized configuration/revocation tests remain. No real policy or certificate was changed. Backend ownership, evidence, certificate uniqueness and eligibility requirements were not loosened.

## Frontend

No frontend code changed in P1G. P1F's existing Profile renderer already distinguishes200 issued snapshots,200 empty list,404 unavailable section, loading and401/403/network/server errors with Retry. Existing RU/KK/EN and session isolation remain. Certificate-name confirmation workflow is untouched.

## Live readiness and intentional restrictions

Course8's existing snapshot can now be returned to its authenticated owner through MyCertificates even though issuance remains disabled. This conclusion follows from the verified P1F live record plus isolated API regression, **not a real-account browser journey**. No browser identity or JWT was read or manufactured for a live account.

A current local setting check found **no configured trusted `CERTIFICATE_PUBLIC_ORIGIN`**. Therefore a real PDF download still correctly returns403 until an independently approved trusted origin is configured. No setting was changed or default origin fabricated. With a trusted synthetic origin in isolated tests, real ReportLab PDF download returns200 without altering any Certificate field. PDF rendering does not require a migration, issuance or DB mutation.

The existing PDF contains a verification link/QR. Public verification remains404 while the global flag is false. Thus even a locally downloaded PDF must not be presented as currently publicly verifiable in this mode. Opening public verification is a separate owner decision, not implemented implicitly. The Profile verification link similarly remains subject to that gate.

## SQLite safety

Before tests, reverified `.local-course-backups/p1f-20261113T040236040248Z/db.sqlite3` through a read-only SQLite connection: integrity ok, zero FK violations, existing certificate count1. No restoration or live backup overwrite.

Working SQLite SHA-256 before/after: `f8a79ad1a69953e3725cc58d43a85cc7459d13b0ce6aa3714a4db573e78c3c2e`. Global flag remains false. Tests configured in-memory SQLite and temporary private/public media before Django setup, so fixture users/records and schema migrations remained isolated. No persistent certificate or enrollment mutations.

## Tests actually executed

Backend, through isolated runner:

```text
.venv/bin/python -B [in-memory DATABASES + temporary media wrapper]
  test certificates.test_profile_visibility certificates.tests certificates.test_admin certificates.test_pdf
  check
```

**57 discovered:56 passed,1 skipped,0 failed**. The skip is the missing-ReportLab branch because ReportLab is already installed. Includes disabled-mode owner list/PDF; other-account404; revoked display/download denial; no certificates; missing/expired/valid JWT; unsupported write405; API/service issuance and revocation blocks; disabled policy invariants; Admin policy-write denial and hidden issue/revoke controls; enabled-mode legacy tests; PDF Unicode/QR construction and origin/font guards. Legacy test expectations were updated only where P1G explicitly changes the disabled-mode contract; they still assert security boundaries.

Frontend from `frontend/` using existing NVM:

```bash
node --test --test-concurrency=2 --test-timeout=30000 tests/certificates.test.mjs tests/session-isolation.test.mjs
```

**2 files passed,0 failed** (existing8 certificate rendering tests and57 session cases). No frontend changes, so full frontend suite/lint/build were not repeated in P1G. Django system checks and `git diff --check` passed.

Native `security_reviewer` independently inspected the read/write split, ownership/PDF guards and admin/service guards read-only; no confirmed security defect. Reviewer did not access DB records, run tests or verify a browser. Real authenticated browser Profile/PDF remains NOT TESTED; the last MCP check in P1F could not launch the absent configured Firefox. No browser was installed in P1G.

## Exact P1G modified paths

- `certificates/views.py`
- `certificates/services.py`
- `certificates/admin.py`
- `certificates/templates/admin/certificates/change_list.html`
- `certificates/tests.py`
- `certificates/test_admin.py`
- `certificates/test_profile_visibility.py`
- `docs/project-memory/CURRENT_STATE.md`
- `docs/project-memory/DECISIONS.md`
- This report.

Existing dirty files include earlier P0–P1F work; it was preserved. No schema/API route addition, frontend redesign, settings edit, global enablement, real issuance/revocation, course publication, staging, commits or pushes.

## Remaining manual checks

1. In the owner's existing session reload Profile; check `/api/my/certificates/` is200 and the old Course8 card appears. A different account must see only its own records. Do not share tokens or full certificate IDs in reports.
2. Do not reissue the certificate to fix display. Until a trusted origin is separately configured, verify that download gives its existing explanatory failure. After any approved origin setup, test PDF retrieval and confirm it creates no new record.
3. Treat verify-link404 as intentionally disabled, not proof that the issued snapshot was revoked. Do not enable public verification/global issuance without separate authorization.
4. Course10 remains unpublished with its disabled policy. Stop before the Git checkpoint; earlier allowlists must be reviewed for these new changes.
