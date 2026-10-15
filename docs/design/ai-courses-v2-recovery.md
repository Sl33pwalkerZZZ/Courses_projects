# AI Courses V2 — shutdown recovery report

Date: 2026-10-15. Branch: `design/ai-courses-v2`.
HEAD at recovery start: `5824973`.

## Outcome and preservation

The exact `http://localhost:5173/` homepage renders in Firefox at desktop,
tablet and mobile widths. Recovery did not rewrite any application component.
The unfinished Phase 1 implementation remains available for review.

Starting Git status contained nine modified frontend application files, two
modified Django files, and untracked Phase 1 components/styles/assets/tests plus
two earlier Django image-description files. All were preserved. A SHA-256
baseline of 213 existing source/document/database/media files confirms that only
the six test setup files listed below changed during recovery. Application
source, existing Django edits, SQLite and media remained unchanged.

No reset, restore, clean, stash, dependency installation, database migration,
course/student-data update, commit or push was performed.

## White-screen diagnosis and confidence

**Historical evidence:** the earlier design audit documented Firefox
`NS_ERROR_CORRUPTED_CONTENT` and empty/disallowed MIME types for optimized React,
Router, Motion and i18next imports. These prevent the React entry module from
running. See the evidence section of [the design plan](./ai-courses-v2-plan.md).

**Current observation:** a fresh browser already rendered correctly before any
recovery edits. All optimized module requests returned `200 text/javascript`.
The running server was in the correct frontend directory and had already been
started at 10:32 with `vite --force --strictPort`, before this recovery began.
The historical white screen was therefore not reproduced in this recovery.
No missing/incomplete import or React rendering exception was found.

**Confirmed cache interference:** six existing SSR test suites created Vite
servers with different optimizer settings but no separate `cacheDir`. They shared
`frontend/node_modules/.vite` with the development server and with one another.
During the first requested test run, existing development cache metadata
disappeared and was later regenerated. Installed Vite's
`loadCachedDepOptimizationMetadata()` deletes old optimized files when its
configuration hash changes. This establishes a real cache-invalidation hazard;
it does not prove the exact trigger of the earlier white screen or attribute it
to the shutdown. The browser continued rendering during this particular run.

**Minimal fix:** each SSR fixture now uses its own `mkdtemp` cache outside the
project and removes only that owned temporary directory when closed. The six
suites retain their existing modules, rendering assertions and API fixtures.
A regression test checks isolation, real JSX loading and cleanup.

Only the verified project Vite process was restarted, using the same command:

```sh
npm run dev -- --force --strictPort
```

The server was left running on port 5173. No Vite config or runtime application
changes were necessary. Vite documents dependency caching and forced regeneration
in its [official dependency pre-bundling guide](https://vite.dev/guide/dep-pre-bundling#caching).
If this happens again, stop the development server with Ctrl+C, use the command
above, and reload the browser with cache bypass. Do not reset project files or data.

## Files changed during recovery

New helper and focused regression:

- `frontend/tests/helpers/vite.mjs`
- `frontend/tests/vite-cache-isolation.test.mjs`

Only SSR setup/imports changed in:

- `frontend/tests/activity.test.mjs`
- `frontend/tests/course-detail.test.mjs`
- `frontend/tests/course-errors.test.mjs`
- `frontend/tests/design-foundations.test.mjs` (existing unfinished file retained)
- `frontend/tests/lesson-workspace.test.mjs`
- `frontend/tests/quizzes.test.mjs`

Other new artifacts are this report and `.playwright-mcp/recovery-*.png`.
The existing uncommitted Header/hero/palette/locale changes belong to the
interrupted Phase 1 implementation, not this recovery diff.

## Validation

| Check | Result |
|---|---|
| `node --test tests/*.test.mjs` | All 11 test files passed, including the new cache-isolation regression. |
| `npm run lint` | Passed without warnings. The repository uses Oxlint; ESLint is not installed. No replacement was installed. |
| `npm run build` | Passed; all 2,461 modules transformed. |
| `.venv/bin/python manage.py check` | No issues, zero silenced. |
| Dev cache stability after fix | All 25 regenerated development-cache files had identical hashes before/after a full test run while Vite was running. |
| `git diff --check` | Passed. |

Native `browser_qa` independently used Firefox on exact port 5173. The initial
matrix covered **1440/768/375/320px × RU/KK/EN × light/dark**: 24 combinations,
seven real public course cards each, no page overflow or console/page/network
failures. Fresh checks after the restart passed at all four widths, plus public
course navigation and return to catalog.

The existing browser regression fixture was run with only its base URL changed
in memory from 5175 to 5173. All API responses in that fixture are synthetic.
Search, direction/level/reset without refetch, no-results, repeated/cross-page
catalog anchors, mobile keyboard menu focus/Escape/restoration, language switching,
error/Retry and empty responses passed. Real authenticated flows were not tested.
Reduced motion showed no running animations; the normal desktop signal trace
settled correctly. No forms or mutating real API requests were submitted.

Native `frontend_reviewer` independently reviewed source and the recovery diff:
no supported React rendering blocker and no blocker to the cache-isolation fix.
Its historical-cause qualification is reflected above.

## Interrupted Phase 1 status

| Area | Status | Existing implementation / remaining work |
|---|---|---|
| Core light/dark palettes | DONE | `frontend/src/styles/v2-tokens.css` imported from `main.jsx`; opt-in homepage scope preserves legacy pages. |
| Complete design-token adoption | PARTIAL | Core colors, spacing and radii exist; full typography/layout/motion token adoption remains. |
| Shared primitives | PARTIAL | Button, Badge and native Dialog implemented in `components/ui/`; extended field/surface/feedback inventory remains for later work. |
| Application Header | DONE | Compact responsive Header, translated menu, theme/language preferences, focus containment/return and catalog navigation. |
| Homepage hero | DONE | `HomeHero.jsx/.css`, `SignalMap.jsx/.css`, three local SVG layers and optional one-shot Motion trace; no remote asset URLs. |
| Responsive homepage | DONE | Four widths verified; stacked actions and compact mobile menu. Illustration intentionally hidden at widths ≤900px. |
| Catalog behavior preservation | DONE | Existing API, query, direction/level filtering, reset, Retry and navigation retained and browser-tested. Long pinned homepage intro is no longer rendered. |
| Font delivery | PARTIAL | CSS names Noto Sans with system fallbacks; no self-hosted font has been bundled. |
| Optional direction chooser / short workflow | NOT STARTED | Existing catalog direction filter still works. These optional design-plan sections were not added in recovery. |
| CourseDetail / LessonView / Profile redesign | NOT STARTED | Intentionally deferred; existing pages preserved. |

Phase 1's core homepage implementation is functional. Remaining work is design
completion/polish and review, not a need to recreate the completed components.

## Working browser screenshots

These are actual Firefox screenshots of `http://localhost:5173/`, not the earlier
alternate-port preview and not Figma renders.

| View | Screenshot |
|---|---|
| Desktop 1440px, EN, light | [View](../../.playwright-mcp/recovery-final-1440-light-en.png) |
| Tablet 768px, RU, dark | [View](../../.playwright-mcp/recovery-final-768-dark-ru.png) |
| Mobile 375px, KK, light | [View](../../.playwright-mcp/recovery-final-375-light-kk.png) |
| Narrow mobile 320px, EN, dark | [View](../../.playwright-mcp/recovery-final-320-dark-en.png) |
| Before recovery edits — already rendering | [View](../../.playwright-mcp/recovery-before-desktop.png) |
| After original tests, before cache isolation | [View](../../.playwright-mcp/recovery-after-tests-before-fix.png) |

Protected pages, real accounts and student records were not browser-tested.
No further redesign was performed during recovery.
