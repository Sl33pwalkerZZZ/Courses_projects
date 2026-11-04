# Phase 5A: real MP4 verification

## QA cleanup completed after author-confirmed Firefox playback

The author confirmed that the protected MP4 plays successfully in Firefox. On
2026-11-02, explicit cleanup approval was executed: course 11, module 38, lesson
112, attachment rows 7/8, the fixture's learning-content/settings rows and six
associated playback grants were removed transactionally. Only their two exact
protected media files were removed afterward. IDs/sequences were not reset.

Fresh SQLite and both media backups were verified before deletion at:
`.local-course-backups/video-qa-cleanup-20261102T062248Z-9a9e5d6d/`.
Database SHA-256:
`750eae8de1f7931958f0fa1f7973b3d8ea8f90041b770658c4fd5b37e934d270`.
Integrity/foreign-key checks passed; both media backup hashes matched. Courses
8/10 fingerprints, 18 other lesson-media files, local settings, the original
sample and unrelated table counts were verified unchanged. Local cleanup receipt:
`.local-video-test/cleanup-result.json`.

The former fixture URLs below are historical and must no longer be used. The
video implementation, migrations, tests and documentation remain. Development
continues only inside course 10; see `docs/courses/media-module-5-plan.md`.

## Historical manual fixture (now removed)

The following unpublished fixture was prepared for the author's normal Firefox
and has since been removed as recorded above:

- Course **11**: `[VIDEO QA] Protected Playback Test`, owner `almas`.
- Module **38**, lesson **112**.
- MP4 attachment **7**, WebVTT attachment **8**, both after `Проверка видео`.
- Start here: `http://localhost:5173/instructor/courses/video-qa-protected-playback-test/preview`.
- Click the lesson there to open `http://localhost:5173/lessons/112` with preview
  navigation state. Opening that lesson URL directly can lose the draft outline
  context, so the preview entry is preferred.
- Editing view: `http://localhost:5173/instructor/courses/11/curriculum`.

Use your existing `almas` login. Preparation used local Studio API-view calls with
the account's existing superuser authority, without reading credentials, creating
tokens/sessions, or changing roles. No browser playback result is claimed.

Before DB writes, a SQLite online backup was created at:
`.local-course-backups/video-qa-20261102T054726Z-0142bb2a/db.sqlite3`.
Integrity and foreign-key checks passed; SHA-256:
`8c4c4669928a7cb3354e12bb7b7da587fbfc520a50353c8750949dc64575f742`.
The transaction added one course/settings/module/lesson/learning-content row and
two attachments. Existing courses 8/10 fingerprints, all 18 existing lesson-media
file hashes, unrelated table counts and local settings were checked unchanged.
The local receipt is `.local-video-test/prepared-fixture.json`.

### Test the prepared fixture

1. Log in as `almas`, open the preview entry above, then click its only lesson.
   Do not create another course or repeat the setup instructions below.
2. Confirm video occurs between `Проверка видео` and `После видео`, with a visible
   caption/text equivalent. Play/pause and seek to second 8.
3. Enable subtitles in native controls: expect `Тестовый видеоряд: 0–6 секунд.`
   followed by `Тестовый видеоряд: 6–12 секунд.` These are test timing labels,
   not a speech transcript. Check narrow/mobile width and both themes.
4. For revocation, open DevTools on the lesson and execute:

   ```js
   const qaVideoPath = document.querySelector('.lesson-video video').getAttribute('src')
   if (qaVideoPath !== '/api/lesson-attachments/7/playback/') throw new Error('Unexpected fixture')
   await fetch(qaVideoPath, { headers: { Range: 'bytes=0-0' }, cache: 'no-store' }).then(r => r.status)
   ```

   Expect **206**. Navigate away using an application link (keep DevTools open),
   then repeat the fetch after the cleanup DELETE completes: expect **403**.
   Reopen through preview to get fresh authorization. Already buffered playback
   is not proof of authorization. Do not export cookies or grant response bodies.
5. For expiry, reopen the lesson, store the path again under a fresh variable,
   wait beyond the grant response's `expires_in` without retry/reloading, then
   perform a fresh no-store Range fetch: expect 403. Retry requests a fresh grant.
   An anonymous/private-window GET to the playback path must also fail.

This test procedure is retained as historical evidence; the fixture is removed.

## Executed, without using the development DB

Input: `.local-video-test/sample.mp4` (not committed or modified).

- SHA-256: `b2e2dedff0852c073275f4db3775759a925ae2db226e6a0edc016ae35a9a24dc`
- 1,342,475 bytes, 12 seconds.
- H.264 Main, level 3.1, yuv420p, 640×360, 30 fps.
- AAC-LC, mono, 48 kHz.

`courses/test_real_video.py` uses this input with **real ffprobe, real JWT
authentication, the real Studio multipart upload endpoint and real file delivery**.
It creates an instructor-owned fixture course/lesson in Django's disposable test
database and writes only to a TemporaryDirectory-owned MEDIA_ROOT. No codec
metadata or file validation is mocked in that test module.

Verified automatically: idempotent upload, byte-identical complete delivery,
single-byte/middle/suffix/open-ended ranges, HEAD, 416, authorized preview,
anonymous/other-author/student denial, isolated enrollment removal, protected VTT,
expired server grant, exact revocation, replacement-grant isolation and inactive
account denial. FFmpeg decoded the delivered file and sought to second 8 without
errors. **This is API/decoder verification, not browser playback or browser seeking.**

Run from the project root:

```sh
.venv/bin/python manage.py test courses.test_real_video
```

Optional input override: `AI_COURSES_TEST_VIDEO=/absolute/path/to/sample.mp4`.
The supplied sample should be at least 9 seconds and over 1 MB for this specific
verification scenario. Tests skip explicitly when the input/ffprobe is absent;
the decode test additionally needs ffmpeg. They never migrate the development DB.
Fixture cleanup removes only test-owned temporary storage; Django destroys its
test database. The source sample and all existing assets are retained.

## Actual browser status

Playwright MCP launch failed because its configured Firefox executable is absent:
`/home/almas/.cache/ms-playwright/firefox-1569/firefox/firefox`.
No browser login, UI upload, rendered playback, visible subtitle, screenshot or
browser seek result is claimed. No browser/dependency was installed automatically.

## Manual UI check (not executed)

Use an authorized instructor session. Never open/edit courses 8 or 10 for this
check. A new draft with a unique `[VIDEO QA]` prefix is an explicitly disposable
fixture, not Module 5 content. Keep a note of its course, module, lesson and
attachment IDs. Do not publish it or enroll real students.

1. Open `http://localhost:5173/instructor/courses/new`. Create a draft named
   `[VIDEO QA] <your unique timestamp>`, with a test description and an existing
   category. In Curriculum, add one module and one lesson. Record the new IDs.
2. Edit the lesson body to the following and save:

   ```text
   Тест видео

   Изолированная проверка видео.

   После видео

   Продолжение текста.
   ```

3. **Current Studio limitation:** the editor does not expose `source_sections`
   for a newly created lesson. Without these, media uses its supported materials
   fallback. For the inline test only, configure headings on your new fixture
   using the existing authorized API, from browser DevTools on the Vite site:

   ```js
   const { default: fixtureApi } = await import('/src/api.js')
   const fixtureCourseId = Number(prompt('New [VIDEO QA] course ID'))
   const fixtureLessonId = Number(prompt('New fixture lesson ID'))
   if (!Number.isSafeInteger(fixtureCourseId) || fixtureCourseId <= 0 ||
       [8, 10].includes(fixtureCourseId) || !Number.isSafeInteger(fixtureLessonId)) {
     throw new Error('Invalid fixture IDs')
   }
   const { data: fixtureCourse } = await fixtureApi.get(`/studio/courses/${fixtureCourseId}/`)
   const fixtureLesson = fixtureCourse.modules.flatMap(m => m.lessons).find(l => l.id === fixtureLessonId)
   if (!fixtureCourse.title.startsWith('[VIDEO QA]') || fixtureCourse.is_published ||
       !fixtureLesson || fixtureLesson.text_content.split('\n\n').filter(p => p === 'Тест видео').length !== 1) {
     throw new Error('Not the expected owned draft fixture')
   }
   await fixtureApi.patch(`/studio/lessons/${fixtureLessonId}/`, {
     learning_content: {
       content_language: 'ru', source_sections: ['Тест видео', 'После видео'],
       objectives: [], interactions: [],
     },
   })
   ```

   This reuses normal authentication/refresh without printing tokens. It performs
   a persistent edit **only when you run it**, guarded to the new draft fixture.
   Refresh Curriculum afterward. Skip this step if you are testing fallback only.

4. In that lesson's attachment form select `.local-video-test/sample.mp4`.
   Enter a test label/caption, honest source provenance and a text equivalent.
   Select `Тест видео` as placement and Upload. Expect 201; a repeat with identical
   metadata should return 200 and the same attachment ID.
5. Create a local `sample.vtt` containing the following **test time labels, not a
   speech transcript**, and upload it with the same `Тест видео` placement:

   ```vtt
   WEBVTT

   00:00:00.000 --> 00:00:06.000
   Тестовый видеоряд: 0–6 секунд.

   00:00:06.000 --> 00:00:12.000
   Тестовый видеоряд: 6–12 секунд.
   ```

6. Use Preview saved lesson (`/lessons/<new lesson ID>` with the Studio preview
   navigation state). Confirm the player occurs after the first section, before
   `После видео`. Enable subtitles in native controls; confirm the visible label
   changes at second 6. Check play, pause, keyboard control and seeking to second
   8. Check 1440/768/375/320 px, light/dark and RU/KK/EN. Do not mark the lesson
   complete. A 1.3 MB clip may buffer completely, so seeking need not cause a new
   HTTP request; distinguish buffered seeking from a verified Range request.
7. In Network, confirm same-origin grant POST, HttpOnly scoped cookie and native
   video URL without JWT/query secrets. Verify 200/206 requests as applicable.
   Do not screenshot/export cookies, Authorization or grant/revocation bodies.
8. On the preview, use DevTools to verify a fresh authenticated byte-range request:

   ```js
   const fixturePlaybackPath = document.querySelector('.lesson-video video').getAttribute('src')
   if (!/^\/api\/lesson-attachments\/\d+\/playback\/$/.test(fixturePlaybackPath)) throw new Error('Unexpected URL')
   await fetch(fixturePlaybackPath, {
     headers: { Range: 'bytes=0-0' }, cache: 'no-store',
   }).then(r => ({ status: r.status, range: r.headers.get('Content-Range') }))
   ```

   Expect 206. Navigate away normally, then repeat the fetch on the same SPA
   origin: expect 403 after the cleanup DELETE. For expiry, obtain a fresh grant,
   wait past its `expires_in` (normally up to 300 seconds), then repeat without
   renewing: expect 403. Already buffered playback is not proof of valid access.
   Retry should obtain new authorization. In an anonymous/private window, the
   same playback path must return 403. Use the isolated automated suite for
   enrollment mutation and account-deactivation scenarios, not real accounts.

## Cleanup boundary

The automated verification created no persistent fixture. Subsequent manual
preparation created course 11, and later explicit approval authorized its exact
cleanup, now completed above. `.local-video-test/sample.mp4`, backups, receipts
and unrelated media remain. Do not repeat cleanup or create another QA course.
Before any later cleanup, verify its exact `[VIDEO QA]` title, creator, IDs,
unpublished state, no enrollments/assessments, and the exact files created by its
uploads. No broad directory deletion or course-ID-only deletion is authorized.
