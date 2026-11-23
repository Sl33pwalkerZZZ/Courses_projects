# Protected instructional video (Phase 5A)

This extends `LessonAttachment`; it does not create or publish a course/module.
Existing audio, SRT, image IDs and storage paths remain unchanged.

## Activation boundary

Two additive migrations are included and **already applied to the local
SQLite database** (reconfirmed on 2026-11-04):

- `courses.0006_lessonattachment_video_vtt`: adds video/VTT choices.
- `courses.0007_lessonplaybackgrant`: creates short-lived revocable grant rows.

`manage.py migrate --plan` reports no pending operations locally. Do not reapply
or modify these migrations. For a fresh deployment only, obtain approval and
create an integrity-verified SQLite backup before reviewing the migration plan
and applying the outstanding migrations. Playback endpoints return 503 if the
grant table has not been created; ordinary lessons/audio/SRT remain usable.

MP4 upload requires a trusted system `ffprobe`. Nothing is installed by this
feature. Missing ffprobe rejects uploads clearly; do not disable validation.
Optional settings (defaults live in the feature, not local settings.py):

| Setting | Default | Meaning |
| --- | --- | --- |
| `LESSON_VIDEO_MAX_BYTES` | 262144000 (250 MiB) | MP4 upload bound |
| `LESSON_VIDEO_GRANT_SECONDS` | 300 | Grant TTL, clamped to 30–900 seconds and no later than the issuing JWT's expiry |
| `LESSON_FFPROBE` | executable found on PATH | Trusted ffprobe executable path |

Accepted MP4: ISO MP4 signature, one H.264/yuv420p video stream, Baseline /
Constrained Baseline / Main / High profile, level <= 5.1, <= 60 fps, dimensions
up to 3840×2160, positive finite duration; optional one AAC-LC mono/stereo stream
at 44.1/48 kHz. Other streams/codecs are rejected. ffprobe runs without a shell,
with a 20-second timeout and only the file protocol. This checks container and
metadata, **not complete bitstream decoding or malware scanning**. Keep ffprobe
patched and run uploads under a restricted OS account. Configure reverse-proxy
upload limits/timeouts consistently with the application limit; upload validation
currently reads at most the configured limit plus one byte into memory.

WebVTT is bounded to 1 MiB, UTF-8 plain text, with ordered non-overlapping
HH:MM:SS.mmm cues and no embedded markup. SRT remains a separate download format.

## Authentication and delivery

1. The existing JWT client POSTs to the **same-origin** endpoint
   `/api/lesson-attachments/{id}/playback-grant/`.
2. Django checks existing lesson/enrollment/author/admin preview permissions.
   It creates an unpredictable nonce, stores only its hash with user, attachment,
   expiry and revocation state, and sends a signed, per-grant HttpOnly
   SameSite=Strict cookie. The cookie is Secure on HTTPS. Its name includes the
   attachment and grant IDs; Path is the exact returned playback path.
3. The JSON response contains a plain playback path, expiry and a separately
   signed **revocation-only** capability. The path is
   `/api/lesson-attachments/{attachment_id}/playback/{grant_id}/`. The grant ID
   is a non-secret selector, not an access capability. No JWT/nonce/proof is in a URL.
4. Native `<video>` GET/HEAD requests send the scoped cookie automatically. Every
   request checks signature, nonce record, expiry, revocation, attachment/hash,
   active account, password auth hash and current lesson access again. The signed
   grant ID must match both the route selector and the server-side grant row.
5. Unmount/logout/account changes revoke exact grants by DELETE to the grant
   endpoint with `{ "revoke_token": "..." }`. Revocation needs this proof, not a
   JWT from a possibly different account. A stale grant response is revoked in
   the API interceptor and remains canceled. Revoking A cannot revoke B's newer
   grant. DELETE expires only that grant's cookie name and Path, even when repeated.
   A delayed response for A cannot overwrite B's cookie slot.

The Vite dev proxy routes `/api` to Django on 127.0.0.1:8000. Restart Vite after
the config change. Production **must** serve frontend and `/api` on the same HTTPS
origin and configure trusted proxy HTTPS headers correctly. The video code does
not fall back to cross-origin cookies or JWT query strings.

Full GET returns 200; a valid single range returns 206 with Content-Range and
bounded Content-Length; unsupported/malformed/multiple or unsatisfiable ranges
return 416 with `Content-Range: bytes */size`. HEAD ignores Range and returns full
representation headers without a body. Responses use private/no-store, nosniff,
Accept-Ranges, and Cookie variation. The standard video player never buffers a
full video Blob. Private files must not be served by nginx/CDN/public MEDIA_URL.

## Authoring and inline placement

Use the existing Instructor Studio lesson attachment form to upload `.mp4` and
`.vtt`, including label, caption, provenance and the video's transcript/text
equivalent. Choose an existing section heading. Published-course locks and owner
checks remain in effect.

One video and one VTT sharing a nonempty `after_section` are paired automatically;
ambiguous groups are not guessed. Use distinct sections for multiple videos with
different tracks. A unique existing same-section `image_placement` image supplies
an optional protected poster. IDs are validated against that lesson. Poster
images use the existing small-image Blob loader, not the video delivery path.
Unplaced videos use the existing materials fallback. No course IDs or filenames
are hardcoded in React. The same reader/player works in authorized draft previews.

## Limitations and operations

- Native playback errors/expiry provide Retry to request fresh authorization;
  there is no infinite renewal loop or silent public fallback.
- Failed network cleanup or abrupt browser termination can leave a grant usable
  until its short expiry. Enrollment removal, account deactivation and password
  changes deny subsequent requests regardless of cleanup. Already buffered bytes
  and an already authorized response cannot be recalled.
- Grant records are ephemeral authorization state. Schedule retention cleanup of
  expired rows in production (for example, remove expired rows after one day).
  Never delete enrollments, learner records or certificate evidence as part of it.
- Avoid logging Authorization, Cookie, Set-Cookie and grant response/revocation
  bodies. Ordinary URL access logs contain no user token.
- Same-attachment players/tabs use independent grant cookie slots. Revoking or
  expiring one does not invalidate another. Native errors still use manual Retry.
- Legacy `/playback/` remains read-only for previously signed cookies without a
  grant-ID field, bounded by original expiry and all current access checks. New
  grants never issue legacy cookies. Legacy/scoped cookies cannot cross namespaces.
- Ship backend and frontend assets together: the new frontend accepts both URL
  versions, but a cached pre-C3.1 bundle rejects new numeric paths in its strict
  URL validator. Refresh that bundle; do not add an anonymous/public fallback.
  Already-open legacy playback remains protected and works until its original TTL.

## Manual verification after approval/setup

Use an isolated test course/database and a real short H.264/AAC MP4, not course 10
or a real student's records:

1. Owner uploads a video, transcript, optional VTT and optional positioned image
   through Studio; another author/student cannot upload to that lesson.
2. Open the unpublished preview as its author/admin. Confirm captions, poster,
   transcript, controls and keyboard access at 1440, 768, 375 and 320 px in both
   themes and RU/KK/EN. Enable captions in native controls.
3. In Network inspect same-origin POST then native GET/Range 206. Seek through the
   video. Confirm no JWT/query secret and no full video Blob request.
4. In an anonymous tab the plain playback URL fails; pending/rejected students
   cannot obtain grants. Enrolled students can play. Remove only an isolated
   fixture enrollment and confirm the next range fails.
5. Log out or switch fixture accounts with playback open: playback clears and an
   exact-grant DELETE occurs. Check expired/revoked grants fail, and Retry creates
   a fresh grant only for an authorized account.
6. Confirm existing audio/SRT/image inline placement and downloads still work.

Automated tests use temporary storage and isolated Django test databases. Initial
implementation tests used synthetic transport bytes and mocked probe metadata
because ffprobe/ffmpeg were absent then. With those tools now installed,
`courses.test_real_video` additionally verifies the local MP4, actual upload and
FFmpeg decoding/seeking without mocking codec validation. See
`docs/protected-video-verification.md`. Playwright Firefox is still missing; no
actual browser playback result or screenshot is claimed.

HTTP range semantics reference: https://www.rfc-editor.org/rfc/rfc9110.html#name-range
Cookie behavior reference: https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Set-Cookie

## Implementation file inventory

Backend:

```
courses/models.py
courses/attachments.py
courses/serializers.py
courses/urls.py
courses/video.py
courses/video_validation.py
courses/migrations/0006_lessonattachment_video_vtt.py
courses/migrations/0007_lessonplaybackgrant.py
courses/test_video.py
courses/test_video_upload.py
studio/views.py
```

Frontend:

```
frontend/vite.config.js
frontend/src/api.js
frontend/src/utils/lessonAttachments.js
frontend/src/utils/lessonVideo.js
frontend/src/components/learning/LessonAttachment.jsx
frontend/src/components/learning/LessonVideo.jsx
frontend/src/components/learning/lessonAttachments.css
frontend/src/components/instructor/LessonAttachmentManager.jsx
frontend/src/i18n/locales/ru.json
frontend/src/i18n/locales/kk.json
frontend/src/i18n/locales/en.json
frontend/tests/lesson-video.test.mjs
frontend/tests/session-isolation.test.mjs
```

Documentation: `docs/protected-lesson-video.md` (this file).
The pre-existing local `config/settings.py` modification is not part of this work.
