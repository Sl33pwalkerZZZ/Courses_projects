# AI Signal Studio — Phase 2 authentication

Branch: `design/ai-courses-v2`. Status: implemented and validated; not committed.

## Changes

Login and Register now use the existing V2 sans-serif font stack, ink/white
surfaces, blue actions, teal accents and shared Button. AuthLayout replaces the
gold/orbit illustration with the existing local signal-map layers. The form panel
enters by 12px over 240ms; field focus has a 160ms decorative signal line alongside
an immediate native focus outline. Error alerts remain visible while settling
4px over 160ms. All new Motion effects become immediate under reduced motion.

The existing Header is reused unchanged. App enables the existing StudioFooter
and blue scroll progress on authentication routes; deferred pages retain their
existing presentation. Mobile stacks the intro and form and omits decorative art
at widths at or below 900px. Fields remain 16px, hints 14px, visibility controls
44px and inputs/submit controls at least 52px high.

Login and Register submit handlers are byte-for-byte identical to the saved
checkpoint. Existing JWT login, register-then-login sequence, redirects, session
isolation, error handling, required/email/minimum-length validation, autocomplete,
optional email and password visibility remain intact. No auth utility was edited.

## Integration finding

The homepage footer originally contained local fragment links. Reusing those on
auth pages would point at missing sections. Auth footer links now use the homepage
paths `/#course-library` and `/#learning-workflow`.

Firefox also confirmed that asynchronous catalog cards could push the workflow
offscreen after cross-page navigation. A focused Footer observer waits for the
existing catalog `aria-busy` state to finish before landing once on the workflow.
It disconnects after landing, on hash mismatch or cleanup. The homepage component
itself was not changed. Delayed success and error responses are covered by the
fully intercepted browser regression fixture.

## Files

Updated:

- `frontend/src/components/AuthLayout.jsx`
- `frontend/src/components/AuthLayout.css`
- `frontend/src/components/AuthField.jsx`
- `frontend/src/pages/Login.jsx`
- `frontend/src/pages/Register.jsx`
- `frontend/src/App.jsx` — auth-only shared shell selection
- `frontend/src/components/Footer.jsx` — reused footer navigation integration

Added:

- `frontend/src/components/AuthError.jsx`
- `frontend/tests/auth-design.test.mjs`
- `frontend/tests/browser/auth-design.mjs`
- This report; Firefox captures in `.playwright-mcp/auth-v2-*.png`.

## Verification

- `node --test tests/*.test.mjs`: all **13 test files passed**.
- Direct auth suite: **12 checks passed**, covering actual rendered components in
  RU/KK/EN, native constraints, labels/hints, visibility semantics, disabled fields,
  escaped alerts, decorative local assets and correct reused-footer links.
- `npm run lint`: passed without warnings using the repository's Oxlint.
- `npm run build`: passed, 2,465 modules transformed.
- `git diff --check`: passed.

Native `frontend_reviewer` independently reviewed the implementation and focused
footer fix, finding no blocking source issues. Native `browser_qa` independently
used Firefox against exact `http://localhost:5173/`.

Browser coverage:

- Both pages at **1440/768/375/320px × RU/KK/EN × light/dark**: 48 renders;
  no horizontal overflow, page errors or failed requests.
- Normal-motion keyboard navigation: username, password, visibility, submit and
  account-switch link; visible focus and show/hide behavior confirmed.
- Every API request intercepted in isolated contexts for functional tests:
  required fields, optional/invalid email, minimum password length, keyboard
  submit, 401 login error, 400 registration error, network failure, disabled/busy
  state, duplicate guard, stale-error clearing and successful redirects.
- Registration success exercised the real frontend register-then-login sequence
  using synthetic responses. Session markers were checked without printing tokens.
- Delayed catalog success/error both retain correct workflow anchor landing.
- No real authentication request or database write was performed.

## Screenshots

These are actual Firefox captures of the implementation, not Figma renders.

| Page | Desktop, EN light | Mobile 375px, EN dark | Narrow mobile 320px, EN light |
|---|---|---|---|
| Login | [View](../../.playwright-mcp/auth-v2-final-login-1440-light-en.png) | [View](../../.playwright-mcp/auth-v2-final-login-375-dark-en.png) | [View](../../.playwright-mcp/auth-v2-final-login-320-light-en.png) |
| Register | [View](../../.playwright-mcp/auth-v2-final-register-1440-light-en.png) | [View](../../.playwright-mcp/auth-v2-final-register-375-dark-en.png) | [View](../../.playwright-mcp/auth-v2-final-register-320-light-en.png) |

State captures use synthetic fixture values:
[login loading](../../.playwright-mcp/auth-v2-login-loading.png),
[login error](../../.playwright-mcp/auth-v2-login-error.png),
[registration loading](../../.playwright-mcp/auth-v2-register-loading.png),
[registration error](../../.playwright-mcp/auth-v2-register-error.png).

## Preservation and limitations

A starting hash baseline of 220 existing source/document/database/media files
confirmed changes only in the seven authorized frontend integration files listed
above. Backend code, SQLite/media, course content, private page sources, auth
utilities, locales and package manifests were unchanged. No dependencies,
migrations, commits or pushes were introduced.

Noto Sans uses the project's existing local/system fallback stack; this phase did
not add webfont downloads. Real login/registration against the development database
was intentionally not tested. The supplied Figma node is a homepage concept;
authentication adapts its established palette, typography, surfaces and local
signal artwork rather than claiming an authentication-specific Figma frame exists.
