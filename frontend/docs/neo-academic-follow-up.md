# Neo-Academic frontend follow-up

Work remains on `frontend/neo-academic-ui`. No Django source, migrations, routes, or database records were changed. The catalog layout, navy/cream base colors, typography, filters, and existing course/lesson API paths remain in place.

## Frontend changes

- Course cards now use gold and neutral accents, including direction badges and all three art variants. One semantic React Router link covers the whole card and points to `/courses/:slug`. Decorative card art ignores pointer events.
- Login and Register share a responsive academic layout, serif headings, gold actions, visible labels, autocomplete, password visibility controls, accessible request errors, and pending states. Motion entrance animations respect reduced-motion preferences. Email remains optional; registration reflects the existing eight-character minimum.
- Route changes reset scroll to the top and focus the main content without a page-sized focus outline. This prevents catalog scroll position from hiding the start of CourseDetail.
- A shared footer appears on every page, with branding, educational description, catalog and auth-dependent account links, a synchronized RU/KZ/EN switcher, university educational-project copy, copyright, and a restrained CSS orbit animation. The previous catalog-only footer was removed.
- As approved during this task, `/profile` provides a basic account destination: username, optional email, and enrolled courses using existing endpoints. Anonymous visitors go to Login. Loading, empty, request-error, retry, and expired-session sign-in states are supported. Progress, completed-course status, and certificates are not fabricated.
- Header navigation also exposes the working Profile destination for signed-in users. Shared legacy links/buttons and course badges use the site's gold palette; detail and lesson layouts are preserved.

New UI strings are supplied in `en.json`, `ru.json`, and `kk.json`. Detailed registration validation messages are preserved as supplied by Django; the surrounding interface and frontend-auth errors use the selected language. KZ is the visible language label; the existing standard language code `kk` is retained.

## Course navigation diagnosis

`CourseCard.jsx` already used `Link` with `/courses/${course.slug}`, and `App.jsx` already declared `/courses/:slug`. Django's detail lookup uses the course slug and remains unchanged. There were no nested anchors, blocking event handlers, or full-card overlays. `AmbientBackground` was already non-interactive (`pointer-events: none`, behind an isolated catalog), and `ScrollProgress` was also non-interactive. Header stacking did not cover the catalog.

Native Firefox clicks from a scrolled catalog successfully opened the current test course in both the original and updated branch. The existing failed-click symptom was not reproduced with the available single-course data, so an overlay or route bug is not asserted as a confirmed cause. The frontend lacked explicit route scroll handling; the updated app resets scroll and focus on pathname changes to keep the new page visible regardless of its eventual height, with fragment-only catalog navigation preserved. Slugs are encoded in link URLs, and card decorations explicitly ignore pointer events. Real read-only catalog/detail APIs are used for navigation verification; auth/profile submissions are mocked to avoid altering Django data.

## Profile: existing backend and required additions

| Feature | Already available | Backend work needed for full profile |
| --- | --- | --- |
| Username/account | `GET /api/auth/me/` returns `id`, `username`, `email`, `role` ([users/views.py](../../users/views.py), [users/serializers.py](../../users/serializers.py)) | None for display. Editing account details is outside this task. |
| Enrolled courses | `GET /api/my/enrollments/` returns enrollment `id`, nested course details including slug, and `granted_at`. The endpoint filters by the current user ([progress/views.py](../../progress/views.py), [progress/serializers.py](../../progress/serializers.py)). | None for the basic account page. |
| Curriculum/order | Public `GET /api/courses/:slug/` returns ordered modules and lesson IDs/titles/orders ([courses/serializers.py](../../courses/serializers.py), [courses/models.py](../../courses/models.py)). | None to open the curriculum. |
| Lesson completion | `LessonProgress` stores an enrollment, lesson, and nullable `completed_at`; `POST /api/lessons/:id/complete/` writes completion for enrolled users. A progress serializer exists but is not exposed by a GET endpoint ([progress/models.py](../../progress/models.py), [progress/views.py](../../progress/views.py)). | Add an authenticated read endpoint, such as `GET /api/my/enrollments/:id/progress/`, or extend the enrollment response with progress summaries. |
| Course progress | All lesson and completion records exist. | Return `total_lessons`, `completed_lessons`, and a progress percentage. Filter completions to the course's current lessons; define zero-lesson behavior and what happens when the curriculum changes. Aggregate on the backend rather than making one request per course/lesson. |
| Completed courses | Completion can be derived from lesson completion records; there is no course-completion flag, timestamp, or completion API. Assignment submissions also exist with approval status. | Define whether completion means all lessons or also approved assignments. Return `is_completed`/`completed_at` using that rule. A durable historical completion timestamp may require a new field/model; a basic all-lessons status can be computed without a new table. |
| Certificates | `Certificate` stores student, course, unique verification code, and issuance date; admin can manage records. Views are placeholders and no API URLs are registered ([certificates/models.py](../../certificates/models.py), [certificates/views.py](../../certificates/views.py), [config/urls.py](../../config/urls.py)). | Add an authenticated `GET /api/my/certificates/` returning course identity, code, and issuance date. Automated issuance, code generation, duplicate-per-course prevention, public verification, and downloadable documents need additional implementation if required. |
| Continue learning | Profile can already open an enrolled course's curriculum; ordered lesson IDs and completion records exist. | Include a `next_lesson_id` (first incomplete lesson in curriculum order) and preferably a lesson title in progress summaries. A true “resume last viewed lesson” feature additionally requires recording the last viewed lesson; the current completion endpoint does not track viewing. |

Only username, enrolled courses, and links back to the curriculum can be built completely from the current read APIs. Full progress/completed-course/certificate/resume functionality needs the additions above. User-scoped reads must only return the requesting student's records.

## CAPTCHA: backend work required, not implemented

There is no CAPTCHA integration in the current user serializers, JWT views, or dependencies. Once a provider is selected, registration and login need to accept a challenge token and verify it on the server before creating a user or issuing JWTs. Registration can extend `RegisterSerializer`; login needs a custom SimpleJWT serializer/view in place of the unmodified `TokenObtainPairView`. Provider credentials belong in environment configuration, with explicit invalid/expired/verification-failure responses. Frontend widget integration and localized feedback follow that API contract. No CAPTCHA model is inherently required, and no placeholder CAPTCHA was added.

## Reviews: model support exists, API work required

| Requirement | Current support |
| --- | --- |
| Text review | `Review.text` is a `TextField`. |
| Rating | A `PositiveSmallIntegerField` exists, but it does **not** enforce 1–5. There are no range validators or database constraints. |
| Average course rating | No aggregation, serializer field, or endpoint exists. |
| Author | `Review.student` references the user; it can supply a public username. It is not serialized by any existing API. |
| Date | `Review.created_at` stores the date; it is not exposed by an API. |
| Moderation | Statuses are pending/approved/rejected; default is pending. Admin can moderate records. |
| One review per student/course | Enforced by the existing uniqueness rule. |

Sources: [reviews/models.py](../../reviews/models.py), [reviews/admin.py](../../reviews/admin.py), [reviews/views.py](../../reviews/views.py), and [config/urls.py](../../config/urls.py). The reviews views are placeholders, there is no review serializer/URL module, and reviews are not included in the root API routes. The frontend therefore cannot consume an existing review API.

Required backend work:

1. Add rating validation for 1–5 and a database check constraint, auditing existing values before the migration.
2. Add a review serializer exposing `id`, `text`, `rating`, public author username/ID as needed, and `created_at`. Assign the author from `request.user`, not the submitted payload.
3. Add a public paginated course-review list, such as `GET /api/courses/:slug/reviews/`, limited to approved reviews of published courses. Define whether authenticated enrollment is required to submit a review, and enforce the chosen rule server-side.
4. Add authenticated review creation (and owner-only editing if desired), preserve the existing uniqueness rule, and define how edits interact with moderation.
5. Expose `average_rating` and `review_count` on course list/detail responses or in the review response, computed from approved reviews only. Use `null` average and count zero when there are no approved reviews.

Likes are not included in this plan or implementation.

## Scroll-reactive background plan (proposal only)

Extend the existing `AmbientBackground` rather than adding a new rendering engine. Keep all decoration inside the catalog's existing isolated layer, `aria-hidden`, behind content, and `pointer-events: none`.

- **Top / hero:** fine CSS academic grid plus the existing orbital geometry. Use muted gold and neutral lines against the current navy/cream surfaces; retain the catalog composition.
- **Middle / platform introduction:** fade in a small SVG of knowledge-network connections and a handful of nodes. Use low line opacity and no pulsing foreground graphics.
- **Lower / course library:** fade the network out into quiet CSS archive/shelf rectangles and horizontal rules. Reduce density and opacity to protect card readability.

Use Motion's already-installed `useScroll` with catalog/section refs and `useTransform` for broad, overlapping opacity bands. Derive transitions from actual section positions so desktop and mobile catalog heights do not require fixed pixel thresholds. Limit any vertical drift to approximately 8–12px, and animate opacity/transforms instead of layout. Keep the geometry to a few SVG paths/CSS elements, and avoid React state updates on every scroll event.

For `prefers-reduced-motion`, disable scroll-driven movement and continuous drift, and show static, low-opacity section decoration. The current `MotionConfig`, `Reveal`, and global CSS reduced-motion rules provide the foundation. No WebGL/Three.js or background scroll system was added in this task; the footer's CSS orbit is the only new continuous decorative animation.

## Changed files

- `src/App.jsx`: shared footer, account route/guard, auth page shell, and route scroll/focus handling.
- `src/index.css`: gold badge/button/link/selection tokens, shared page sizing, and removal of the old auth-form styles.
- `src/components/CourseCard.jsx` and `CourseCard.css`: encoded course URLs, explicit accessible course names, gold/neutral art, and decorative pointer handling.
- `src/components/AuthLayout.jsx`, `AuthLayout.css`, and `AuthField.jsx`: shared auth layout, academic illustration, responsive styling, visible field labels, and password controls.
- `src/pages/Login.jsx` and `Register.jsx`: redesigned forms and pending/error behavior.
- `src/components/Footer.jsx` and `Footer.css`: shared translated footer and reduced-motion-compatible orbit.
- `src/components/Header.jsx`: signed-in Profile navigation.
- `src/pages/CourseCatalog.jsx` and `CourseCatalog.css`: removal of the previous small catalog-only footer.
- `src/pages/Profile.jsx` and `Profile.css`: basic account and enrollment page using existing APIs.
- `src/i18n/locales/en.json`, `ru.json`, and `kk.json`: auth, footer, and profile copy.
- `docs/neo-academic-follow-up.md`: backend inventory, required API work, navigation evidence, and scroll-background proposal.

## Validation

- `npm run build` passes.
- `npm run lint` passes.
- `git diff --check` passes; every source change is confined to `frontend/`.
- Native Firefox clicks using the real read-only catalog/detail API open `/courses/test_course`; the updated route starts at scroll offset zero. The original failed-click symptom was not reproduced with the available course data.
- Login and Register pass the layout/label/translation checks in RU, KZ, and EN, in light and dark themes, at 320, 390, 768, and 1440px widths (48 combinations). Desktop and mobile screenshots were also visually inspected.
- Visible password controls and anonymous Profile redirection were checked in Firefox. Auth and account-state scenarios use mocked responses; no test users or enrollment records are created.
- Translation dictionaries have matching UI keys, and changed card/auth styles contain no purple/violet references. Existing catalog hero/orbit styling was preserved.
- Mocked browser checks passed for login pending/credential-error/success, the authenticated footer link, profile loaded/empty/API-error states, logout, registration minimum length/server validation/pending/success, and post-registration sign-in. Native keyboard input verified the registration minimum length.
- Enabling reduced motion in Firefox stops the footer orbit and hides the scroll-progress strip. A CSS fallback also handles a preference change after page load.
