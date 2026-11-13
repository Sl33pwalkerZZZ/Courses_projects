# P1I — authenticated PDF preview/download without public verification

2026-11-13, Asia/Almaty. No issuance, policy, legal identity or stored certificate-content changes.

## Exact failure

P1G opened private reads, but `DownloadCertificate.get` still returned403 before rendering when `CERTIFICATE_PUBLIC_ORIGIN` was empty. `render_certificate` also required a verification URL for its QR/link. Those were verification dependencies, not requirements for reading an issued snapshot. The document renderer performs no database writes and does not call issuance.

## Narrow implementation

- Same existing authenticated `/api/certificates/<code>/download/` route: default disposition is `attachment`; `?preview=1` is `inline`. No new endpoint.
- Same owner-or-existing-authorized-moderator boundary, evidence and revocation restrictions. Anonymous401, other owner404, revoked/unverified403. Private/no-store remains on success/errors; successful PDF adds nosniff.
- Optional QR/link only when public verification is already enabled AND a valid explicitly configured origin exists. Scheme/hostname/credentials/path/query/fragment/port are checked; no request Host fallback and no invented address. Missing/invalid origin omits this optional block instead of preventing the owner's PDF.
- Renderer accepts `verification_url=None`, leaves stored learner/course/issuer/date and existing educational/non-accreditation text unchanged, and adds only the neutral footer “Публичная ссылка проверки не добавлена.” instead of a misleading QR. No record or issuer identity is rewritten. ReportLab invariant output makes preview/download from the same snapshot byte-identical, with no persistent caching.
- Own-list metadata adds `verification_available` based on the existing feature gate and snapshot validity. Profile uses it to hide the dead public link and explain unavailability. Existing verification URL schema remains for enabled operation.
- Profile adds localized View PDF and Close preview; obtains PDF with the existing JWT client, uses a session-generation-scoped Blob URL in a titled inline iframe, revokes it on close/replacement/unmount/account change, and rejects stale pending responses. No tokens in URLs/new-window preview and no unprotected media endpoint. Existing download and error/retry behavior retained. CSS only sizes the preview container using existing tokens.

## Tests actually run

Backend (isolated in-memory SQLite and temporary private/public media roots, overridden before Django setup):

```text
test certificates.test_profile_visibility certificates.tests certificates.test_admin certificates.test_pdf
check
```

**62 discovered:61 passed,1 expected skip,0 failures.** ReportLab is installed, so the missing-dependency branch is skipped. Tests cover owner preview/download; identical bytes and inline/attachment/private/no-store/nosniff; anonymous/other-owner/revoked restrictions; disabled feature with and without an origin; no QR even with configured origin when public verification is disabled; invalid origin omission; metadata/policy row equality; valid JWT and expired/missing JWT; service/API/admin issuance blocks. The historical tests demanding origin403 were updated to the explicitly approved optional-verification contract, not removed.

PDFs were actually parsed via `pdftotext` and rasterized with `pdftoppm`, including Cyrillic/Kazakh text and issuer/course/name preservation. QR factory is checked not called in no-verification mode and PDF has no URI annotations. This is more than HTTP200 validation.

Frontend:

```bash
node --test-timeout=30000 tests/certificates.test.mjs
node --test --test-concurrency=2 --test-timeout=30000 tests/*.test.mjs
npm run lint
npm run build
```

**10 focused certificate tests and35/35 frontend files passed**; lint/build passed. Existing P0 session isolation/refresh tests remain in the full suite. `git diff --check` and Django system checks passed.

Existing cached Chromium/Playwright-core ran `/tmp/p1i-browser.cjs` against an isolated Vite fixture: **6 combinations** (RU/KK/EN ×1440/320px), preview request/iframe creation, close+revoke, downloaded file bytes, error handling, logout hiding/revoking preview, and delayed-response-after-logout producing no Blob URL. Zero real API requests and zero page exceptions; synthetic client state only, not a live account or authentication bypass against the backend. Temporary server stopped. No packages/browsers installed.

**Browser limitation:** the headless-shell screenshot shows an empty native PDF iframe even though its Blob URL is attached. Native viewer content rendering is NOT verified by this fixture; the real generated PDF is confirmed readable by Poppler and the saved browser download matches it. Real Firefox built-in viewer remains a manual check, not a claimed pass.

Native security reviewer independently reviewed the renderer/view/React boundary read-only and found no confirmed security defects. It did not run tests or access DB/browser records.

## Diagnostic artifacts (synthetic only)

- `/tmp/p1i-sample.pdf`: sample renderer output, no real certificate/account data.
- `/tmp/p1i-sample.png`: inspected Poppler raster of that PDF; no QR/link and preserved typography/layout.
- `/tmp/p1i-profile-320.png`, `/tmp/p1i-profile-1440.png`: fixture controls; not proof of native PDF rendering.
- `/tmp/p1i-frontend-tests.log`, `/tmp/p1i-build.log`.

## Safety and changed paths

Working SQLite hash before/after: `f8a79ad1a69953e3725cc58d43a85cc7459d13b0ce6aa3714a4db573e78c3c2e`. No live DB mutations, models/migrations, settings, certificates/policies, Course8/10 content/publication or protected-media changes. P1F verified backup remains untouched. No staging, commit or push. Existing WIP preserved.

P1I changes only:

- `certificates/views.py`, `certificates/pdf.py`
- `certificates/tests.py`, `certificates/test_profile_visibility.py`, `certificates/test_pdf.py`
- `frontend/src/components/certificates/Certificates.jsx`, `certificates.css`
- `frontend/src/i18n/locales/ru.json`, `kk.json`, `en.json`
- `frontend/tests/certificates.test.mjs`
- This report, `docs/project-memory/CURRENT_STATE.md`, `docs/project-memory/DECISIONS.md`.

## Real Firefox manual check

1. Reload Profile in the existing certificate-owner session. The old issued Course8 card should remain; no new certificate needs to be issued.
2. Click “Посмотреть PDF”. Check authenticated GET to the existing download route with `?preview=1` returns200 application/pdf, inline and private/no-store. Do not copy Authorization/token headers into reports.
3. Confirm the embedded document is readable in Firefox's built-in PDF viewer; name/course/issuer/issue date match the existing certificate. If Firefox is configured to download PDFs instead of displaying them, its viewer configuration may affect inline display; do not treat the headless fixture as proof either way.
4. Close preview, click “Скачать PDF”, open the saved PDF, compare the same fields. Download response uses attachment. No QR/public link should appear under the current disabled verification configuration.
5. Switch/logout and confirm preview disappears; do not issue/revoke/modify anything. Different accounts must not gain access.

Global issuance remains false. Public verification remains gated404 and Profile explains that limitation. Neither origin configuration nor publication/global enablement is needed for these private PDFs. P1H staging plan is now a historical allowlist and must be refreshed separately before any Git checkpoint; this task stops here.
