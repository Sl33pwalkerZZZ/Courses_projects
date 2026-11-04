# Student experience — cinematic Phase 3

2026-11-03 · branch `design/amethyst-motion`

## Safety checkpoint

Verified before editing:
`.local-redesign-checkpoints/frontend-before-student-phase3-20261103-111802.tar.gz`.
Archive members were checked against the working frontend. Existing uncommitted
work retained; no Git restore/reset/clean, backend edits, migrations, course or
student record changes, commits, pushes or deployment. Unslop was not invoked.

## Audit and direction

Keep the cinematic product identity while putting educational text first.
Strong existing foundations retained: real course/module counts, accurate404 vs
retry states, server-derived enrollment status, collapsed/inert curriculum,
structured lesson rendering, inline protected media, native image enlargement,
transcripts, session isolation, progress and certificates.

Source-confirmed UX issues addressed:
- Dense1024px reader: sidebar+reader padding consumed excessive reading width.
- Long structured lessons lacked a contents navigator despite exact section metadata.
- Small Profile/lesson metadata and weak separation between controls and prose.
- Login/Register used the internal Studio eyebrow and a tall mobile introduction.
- Certificate verification lacked a clear document/status hierarchy.

No course cover field is supplied by the current API/models. The existing real
module journey is refined as the hero focal point; no cover image or learning
objective has been fabricated. Course description, modules, lessons, author and
reviews continue to use existing responses only.

## Independent increments

### CourseDetail

Editorial title/author hierarchy, framed actual module preview, readable synopsis,
section navigation and access panel. Real enrollment/application/continuation,
review counts, retry,404 and empty states unchanged. No API or state logic edits.

### Reading workspace

More room for prose, comfortable70ch target, 16–17px body text, larger interface
metadata and distinct objectives/completion/previous-next controls. At<=1024px,
the outline stacks above reading; between901–1024 it remains expanded in a bounded
scrolling region (existing compact disclosure logic still activates at900px).

`LessonSectionNavigation` derives a native disclosure and links solely from
`MediaLessonReading`'s existing sections. It shares generated IDs with the actual
h2 headings; targets are programmatically focusable. It is omitted for fewer than
two sections. No hardcoded lesson IDs, source text edits, stored metadata changes
or new educational claims. Legacy/custom readers keep their original renderer.

Native video/audio controls, WebVTT URLs, transcripts, image enlargement, download
handlers and authorization code remain unchanged. Attachments get a distinct
control surface and transcript separator; learning tables retain intentional
horizontal scrolling instead of compressing or deleting source columns.

### Profile

Account frame, readable progress metadata, course-card hierarchy and links to
existing learning/activity/certificates/applications targets. Existing analytics
and certificate APIs remain unchanged; no new statistics or account actions.
`EnrollmentCard` is exported for isolated visual testing without loading private
Profile APIs. Data-loading and session behavior remain intact.

### Login/Register and verification

Keep existing desktop companion/particle character and lightweight form entrance.
Compact mobile introduction, clear auth-specific eyebrow, strong form surface,
focus and error framing. Login/Register handlers and AuthField remain byte-identical.
Verification uses a document-like surface and actual valid/revoked status attributes;
minimal public fields, issuer, revocation and request behavior are unchanged.

## Motion

Retain existing course/profile/auth entrances, interactive title text and feedback.
No new animation around reading text or media. Section navigation is native HTML,
so no observer/animation completion is required to reveal content. No new loops,
WebGL, dependencies or global theme-token changes. Existing reduced-motion policy
continues to apply. Homepage and Studio styles/components are untouched.

## Exact changed files

Source:
- `frontend/src/pages/CourseDetail.css`
- `frontend/src/pages/LessonView.css`
- `frontend/src/pages/Profile.jsx`, `Profile.css`
- `frontend/src/pages/CertificateVerification.jsx`
- `frontend/src/components/AuthLayout.jsx`, `AuthLayout.css`
- `frontend/src/components/certificates/certificates.css`
- `frontend/src/components/learning/LearningContent.jsx` (objectives class only)
- `frontend/src/components/learning/MediaLessonReading.jsx`
- `frontend/src/components/learning/LessonSectionNavigation.jsx` (new)
- `frontend/src/components/learning/mediaLessonReading.css`
- `frontend/src/components/learning/lessonAttachments.css`
- `frontend/src/i18n/locales/{ru,kk,en}.json` (new studentVisual namespace only)

Tests/fixtures:
- `frontend/tests/student-experience.test.mjs` (new)
- `frontend/tests/inline-images.test.mjs`
- `frontend/tests/lesson-attachments.test.mjs`
- `frontend/tests/media-lesson.test.mjs`
- `frontend/tests/browser/student-workspace.html`, `student-workspace.jsx` (new)
- This report.

Existing placement tests were narrowed to actual body h2 positions after adding
contents links. External-reference counts explicitly count external links, not
new internal navigation links. Placement, source preservation and reference URL
assertions remain enforced, not removed.

## Browser verification approach

Uses existing cached project-local Chromium/Playwright-core, not an installed new
library and not a claimed MCP browser run. Current frontend served at5176 with
`VITE_API_URL=/api` in the QA process environment only; existing Vite proxy reaches
the actual Django public API. **No browser CORS adaptation or settings edits.**
Only GET API requests are allowed by the test context.

Before screenshots use the verified snapshot at5182. Current public CourseDetail,
Login/Register are checked against the real local app. No forms submitted.
Protected lesson/profile and valid verification presentation use clearly labeled
synthetic fixtures at `/tests/browser/student-workspace.html`, without JWT or
private endpoint access. Fixture video/audio show native loading presentation and
transcripts, not fake imported playable media. No records or media are attached.
The user previously confirmed no authorized test session exists.

Screenshots/results are local only under `.playwright-mcp/student-phase3/`:
- `before-{course,login,register}-{1440,320}.png`
- `after-{course,login,register}-{1440,320}.png`
- `fixture-{lesson,profile,certificate}-{1440,320}.png`
- `results.json`

Initial capture showed reviews before scroll reveal; corrected captures scroll
through the page explicitly. First long pass ended when its temporary server
stopped; only the completed rerun is used as final test evidence.

## Independent review

Native frontend_reviewer audited and reviewed final source; no blocking finding.
Native browser_qa independently inspected actual screenshots, correctly separating
public captures from fixtures and flagging reveal timing/table scroll checks.
No reviewer edited code, database records or account state.

## Verification results

Final frontend validation on 2026-11-04: **34 test files passed**, with
`node --test --test-concurrency=2 tests/*.test.mjs`; `npm run lint` and
`npm run build` passed. `git diff --check` passed. No dependencies installed. Existing tests cover
session isolation, enrollments, progress, quiz behavior, inline images/audio/video,
certificates, Studio and Phase1 landing. New tests validate derived navigation
anchors, focusable headings, source preservation and translated labels.

## Remaining limitations

Real authenticated enrollment, lesson completion, assignment/quiz submission,
private media playback/seeking/subtitles, profile refresh and certificate download
remain unverified in a browser; no safe account session was supplied. Their code
is unchanged and existing frontend regression tests still run. Valid/revoked
certificate presentation fixtures are not evidence of issuance or real identity.

No claim that every course, external image, table or hardware performance profile
has been exhaustively audited. Long tables intentionally scroll locally. Student
visual review with real authorized data is the next useful check; no Module6 or
video production was started.


## Resume and final verification — 2026-11-04

Recovered the current Git working tree, source diff, verified original archive,
all18 initial screenshots and the completed original `results.json`. That saved
run contains190 successful checks:180 layout combinations (six surfaces × three
languages × two themes × five widths, including1024), section navigation, native
registration validation, password visibility, reduced-motion auth and unknown
public certificate handling. Its status is `complete`; it is not treated as a
still-running or assumed successful process.

No redesign was repeated. No additional application-source fix was justified by
the two remaining concerns:

- Reviews are intentionally revealed on intersection. After real scrolling and
  waiting for the existing entrance to finish, the public reviews heading,
  empty-state explanation and sign-in link are visibly rendered. The earlier
  blank screenshots were captured before reveal, not missing backend content.
- Tables deliberately retain readable columns inside a named `overflow:auto`
  region with `tabIndex=0`. At320px, the tested region has246px visible width and
  321px content width; ArrowRight moves its scrollLeft from5 to75 while the page
  remains within the viewport. The second column is locally scrollable rather
  than lost or made unreadably small.

Fresh evidence is isolated under `.playwright-mcp/student-phase3/resume/`:
`results.json`, `reviews-{light,dark}-{1440,320}.png`,
`table-{light,dark}-{1440,320}.png`. The raw first harness run is retained as
`initial-run-raw-events.json`. The initial reporter rejected intentional aborted
course GETs from the development StrictMode effect cleanup. Final reporting keeps
raw events and separately classifies only canceled GETs for the exact course URL
whose replacement completed with200. All other failed requests still fail QA;
these events were not erased or used to mask network/server failures.

The targeted run finished with **status `complete`: 56 checks passed**, zero page
errors, zero console errors and zero mutating API requests. Seven intentional
course-GET cancellations are retained and classified separately; there were no
unexpected request failures. It verifies24 real-public review combinations and24 isolated lesson
table combinations across1440/768/390/320, RU/KK/EN and both themes; section-link
focus is checked for each language/theme, plus reduced-motion review visibility
and auth transforms. It does not pretend to be an authenticated student session.
Normal same-origin `/api` proxying is used; no CORS adapter, tokens or mutating
requests. A temporary preview lifetime interruption was handled by running the
QA server and checks together, without changing the application's server setup.

The independent read-only source review confirmed the existing region/anchor
semantics and protected-renderer preservation. An independent screenshot reviewer
confirmed visible reviews and readable table content; page containment and actual
keyboard scrolling are established by the recorded browser metrics, not by a
cropped screenshot alone.

Resume changes are confined to verification scripts/artifacts and this report.
The successful Phase3 implementation remains intact. Hash checks preserve the
cinematic homepage, Instructor Studio, auth handlers, lesson state, video/attachment
code, SQLite and `config/settings.py`. No real content or student data changed.
