# Final local Git checkpoint — 2026-11-04

Branch: `design/amethyst-motion`. Previous checkpoint: `5cf26f9`.
This supersedes the proposed grouping in `git-checkpoint-readiness.md` while
preserving that original audit as historical evidence. Local commits are
authorized; **no push, deployment, publication, import or migration is performed**.

## Findings resolved

1. `docs/protected-lesson-video.md` now states that courses migrations 0006/0007
   are already applied locally, distinguishing fresh-deployment instructions.
   `manage.py migrate --plan` reports no operations. No migration file was edited
   or newly generated during finalization.
2. The Module 5 preview generator depends on the Module 4 helper **only during
   offline synthesis**, not Django/React runtime. The helper and MIT notice are
   versioned with the authoring sources. Source validation verifies its pinned
   hash. The unapproved `narration-preview.wav` remains local and is not committed.
   Stored provenance is retained for licensing and reproducibility. The generator
   now requires an explicit fresh `--output-dir`; it never overwrites existing
   audio/metadata. No synthesis or dependency installation was performed.
3. Source-only validation succeeds without preview audio and explicitly reports
   skipped playback validation. `--require-preview` validates the existing local
   WAV or fails if absent. Three regression tests cover source-only checkout,
   required-audio failure and model-free generator help. Staged source export
   was validated in a clean temporary directory without local WAV dependencies.
4. Staged whitespace checking found an extra blank EOF line in
   `five-scene-storyboard.md`; only that trailing blank was removed. No storyboard
   wording or lesson content was changed.

## Verified backups

Fresh backup directory: `.local-course-backups/git-checkpoint-20261104T051842Z/`.

- Live SQLite: `PRAGMA integrity_check = ok`; `PRAGMA foreign_key_check` returned zero violations, rechecked after tests. No data rows were printed.
- Existing backup reopened read-only and passed both checks: `.local-course-backups/media-module-before-294cf29f8d3a4547b6393654f6ebf6eb.sqlite3`.
- A fresh SQLite online backup was created as `db.sqlite3` inside the new directory, then reopened read-only and passed both checks. Previous backups were not overwritten.
- New database-backup SHA-256: `8300b0a34eb5e36f0cd4d8bde976ec056b07aa6779b6041b2ede35777bb484c0`.
- Separate `protected-media-and-instructional-sources.tar.gz`: **98 files**, **16,452,909 bytes**, covering all existing `media/`, `course_assets/` and `course_sources/` files at checkpoint start. This includes important untracked candidate audio and Module 5 sources, not just files selected for Git.
- Archive SHA-256: `8bee248d2de6da881a991fe02998a2b3dbd462231abb1ff6f8146f7eb61ee21f`. Every archived file was read back and its SHA-256 compared with its source; exact file coverage and all hashes matched. No archive was extracted over project files.
- Private `verification.json` in the backup directory records the per-file inventory and baseline hashes. Backup and inventory remain ignored/local. The archive captures pre-finalization authoring scripts; the four intentional source-text adjustments are retained in Git. Audio, DOCX and protected-media bytes are unchanged.
- This is a verified local recovery set. No off-machine copy or full application restore exercise is claimed. Keep this private archive outside public storage and arrange an external copy independently.

## Validation

| Check | Result |
| --- | --- |
| Relevant Django suite (listed below) | **65 passed**, no reported skips |
| Full frontend `node --test --test-concurrency=2 tests/*.test.mjs` | **34 test files passed**, zero failed/skipped |
| `npm run lint` | PASS |
| `npm run build` | PASS |
| Django system check | PASS, no issues |
| `makemigrations --check --dry-run` | No changes detected |
| `migrate --plan` | No pending operations |
| Module 5 source consistency validator | PASS |
| Local package `--require-preview` | PASS; existing WAV checksum/PCM checked without regeneration |
| Export of exact staged source package without WAV | PASS, explicit audio SKIP |
| Staged checks per commit | Explicit allowlist, name/status, diff review, bounded secret-pattern scan, no unexpected binary or file over 1 MiB, whitespace check |

```sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B manage.py test \
  courses.test_video courses.test_video_upload courses.test_real_video \
  courses.test_media_module_5 courses.test_media_module_5_package \
  courses.test_lesson_media_import courses.test_final_module4_assets \
  studio.test_role_security --noinput
```

Tests use disposable DB/temp storage; streaming tests were run outside the
sandbox restriction already identified in the original audit. The source-only
package test uses copied sources and does not require PyTorch or checkpoints.
No fresh browser verification or additional agent review was needed for these
checkpoint/documentation/source-tool changes. Existing visual QA limitations
remain as recorded in the three phase documents. Secret-pattern scanning is
bounded; it is not a guarantee against every possible sensitive string.

## Four non-overlapping commit boundaries

Tests necessary for each feature remain with that feature. Phase documentation,
checkpoint records and the new source-only regression tests form the fourth
commit. This preserves the original allowlisted production paths while moving
the former optional authoring package into Module 5 **without generated audio**.

### 1. `feat: add protected instructional video infrastructure`

Commit: `28ff315`. 14 explicit paths:

```text
courses/attachments.py
courses/migrations/0006_lessonattachment_video_vtt.py
courses/migrations/0007_lessonplaybackgrant.py
courses/models.py
courses/serializers.py
courses/test_real_video.py
courses/test_video.py
courses/test_video_upload.py
courses/urls.py
courses/video.py
courses/video_validation.py
docs/protected-lesson-video.md
docs/protected-video-verification.md
studio/views.py
```

### 2. `feat: add module 5 content importer and authoring sources`

Commit: `ca684c3`. 26 explicit paths:

```text
course_assets/module_4/voice_candidates/LICENSE_CIS
course_assets/module_4/voice_candidates/prepare_roman_module4.py
course_assets/module_5/m5-l13-v1-production/F1_video/notes/brief.md
course_assets/module_5/m5-l13-v1-production/F1_video/notes/permission-checklist.csv
course_assets/module_5/m5-l13-v1-production/LICENSE_CIS
course_assets/module_5/m5-l13-v1-production/README.md
course_assets/module_5/m5-l13-v1-production/five-scene-storyboard.md
course_assets/module_5/m5-l13-v1-production/generate_preview.py
course_assets/module_5/m5-l13-v1-production/narration-provenance.json
course_assets/module_5/m5-l13-v1-production/narration-script-ru.txt
course_assets/module_5/m5-l13-v1-production/originals/f1-notepad-diagram.svg
course_assets/module_5/m5-l13-v1-production/originals/f1-paper-diagram.svg
course_assets/module_5/m5-l13-v1-production/permission-review-template.md
course_assets/module_5/m5-l13-v1-production/recording-checklist.md
course_assets/module_5/m5-l13-v1-production/storyboard-source.json
course_assets/module_5/m5-l13-v1-production/validate_package.py
courses/management/commands/import_media_module_5.py
courses/management/media_module_5.json
courses/test_media_module_5.py
docs/courses/media-module-5-assets.json
docs/courses/media-module-5-content-review.md
docs/courses/media-module-5-import-readiness.md
docs/courses/media-module-5-plan.md
docs/courses/media-module-5-storyboards.json
docs/courses/media-module-5-validation.md
scripts/validate_media_module_5_sources.py
```

### 3. `feat: complete cinematic frontend redesign phases 1 to 3`

Commit: `42455ca`. 50 explicit paths:

```text
frontend/src/api.js
frontend/src/components/AuthLayout.css
frontend/src/components/AuthLayout.jsx
frontend/src/components/HomeHero.jsx
frontend/src/components/certificates/certificates.css
frontend/src/components/instructor/LessonAttachmentManager.jsx
frontend/src/components/instructor/StudioCourseCollection.jsx
frontend/src/components/instructor/StudioDashboard.jsx
frontend/src/components/instructor/StudioNavigation.jsx
frontend/src/components/landing/ClosingInvitation.jsx
frontend/src/components/landing/DepthSurface.jsx
frontend/src/components/landing/LandingCoursePreview.jsx
frontend/src/components/landing/LearningShowcase.jsx
frontend/src/components/learning/LearningContent.jsx
frontend/src/components/learning/LessonAttachment.jsx
frontend/src/components/learning/LessonSectionNavigation.jsx
frontend/src/components/learning/LessonVideo.jsx
frontend/src/components/learning/MediaLessonReading.jsx
frontend/src/components/learning/lessonAttachments.css
frontend/src/components/learning/mediaLessonReading.css
frontend/src/i18n/locales/en.json
frontend/src/i18n/locales/kk.json
frontend/src/i18n/locales/ru.json
frontend/src/pages/CertificateVerification.jsx
frontend/src/pages/CourseCatalog.jsx
frontend/src/pages/CourseDetail.css
frontend/src/pages/LessonView.css
frontend/src/pages/Profile.css
frontend/src/pages/Profile.jsx
frontend/src/pages/instructor/CourseEditor.jsx
frontend/src/pages/instructor/InstructorStudio.jsx
frontend/src/pages/instructor/studio-command.css
frontend/src/styles/cinematic-landing.css
frontend/src/utils/lessonAttachments.js
frontend/src/utils/lessonVideo.js
frontend/tests/browser/student-workspace.html
frontend/tests/browser/student-workspace.jsx
frontend/tests/browser/studio-workspace.html
frontend/tests/browser/studio-workspace.jsx
frontend/tests/cinematic-landing.test.mjs
frontend/tests/design-foundations.test.mjs
frontend/tests/enrollment-requests.test.mjs
frontend/tests/inline-images.test.mjs
frontend/tests/lesson-attachments.test.mjs
frontend/tests/lesson-video.test.mjs
frontend/tests/media-lesson.test.mjs
frontend/tests/session-isolation.test.mjs
frontend/tests/student-experience.test.mjs
frontend/tests/studio-dashboard-design.test.mjs
frontend/vite.config.js
```

### 4. `test: document and validate the post-redesign checkpoint`

This document is included in this fourth commit; obtain its hash with `git log -4 --oneline` (a document cannot embed its own commit hash). 6 explicit paths:

```text
courses/test_media_module_5_package.py
docs/cinematic-landing-phase-1.md
docs/cinematic-student-phase-3.md
docs/cinematic-studio-phase-2.md
docs/git-checkpoint-finalization.md
docs/git-checkpoint-readiness.md
```

## Deliberate exclusions and remaining local changes

`config/settings.py` is the only intended tracked modification left outside the
checkpoint. Its exact initial SHA-256 is unchanged. It is not staged or committed.
All seven canonical Module 4 media assets and their final license/provenance
remain already tracked from `5cf26f9`; no duplicate legacy audio was added.

The following Git-visible untracked paths are deliberately retained locally
(after the fourth group's six paths are committed). They are not disposable:
local QA scripts/receipts and sample MP4; the installed Unslop skill; historical
Module 4 experiments, references and tests; the unapproved Module 5 preview WAV;
and the suspicious terminal-output file. The latter was inspected as ASCII text
with terminal escape sequences (4,463 bytes), has no identified application role,
and remains untouched for manual owner review. Its content is not copied here.

Remaining untracked file count: **78**.

```text
.agents/skills/unslop/SKILL.md
.agents/skills/unslop/agents/openai.yaml
.agents/skills/unslop/references/effects.md
.agents/skills/unslop/references/refs.md
.agents/skills/unslop/references/refs/beacon-engraving.webp
.agents/skills/unslop/references/refs/meadow-3d.webp
.agents/skills/unslop/references/refs/story-dashboard-frames.webp
.agents/skills/unslop/references/refs/unslop-dashboard-after.webp
.agents/skills/unslop/references/refs/unslop-hero-after.webp
.agents/skills/unslop/references/signs.md
.agents/skills/unslop/references/tokens.md
.agents/skills/unslop/references/visuals.md
.agents/skills/unslop/scripts/snapshot.mjs
.agents/skills/unslop/scripts/story.mjs
.local-cinematic-qa/.gitignore
.local-video-test/cleanup-fixture.py
.local-video-test/cleanup-result.json
.local-video-test/prepare-fixture.py
.local-video-test/prepared-fixture.json
.local-video-test/sample.mp4
course_assets/module_4/m4-audio-production.json
course_assets/module_4/m4-l1-f1-natural-narration.mp3
course_assets/module_4/m4-l1-f1-synthetic-narration.wav
course_assets/module_4/m4-l12-ru-roman-room-after-v2.wav
course_assets/module_4/m4-l12-ru-roman-room-before-v2.wav
course_assets/module_4/m4-l2-f1-corrected-transcript.txt
course_assets/module_4/m4-l2-f1-speech.wav
course_assets/module_4/m4-l2-f1-synchronized.srt
course_assets/module_4/m4-l3-f1-clean-reference.wav
course_assets/module_4/m4-l3-f1-original.wav
course_assets/module_4/m4-l3-f1-processed.wav
course_assets/module_4/m4-room-noise-v2.json
course_assets/module_4/voice_candidates/README.md
course_assets/module_4/voice_candidates/evaluation.json
course_assets/module_4/voice_candidates/generate_candidates.py
course_assets/module_4/voice_candidates/lesson12-self-contained-dsp/README.md
course_assets/module_4/voice_candidates/lesson12-self-contained-dsp/demonstration.json
course_assets/module_4/voice_candidates/lesson12-self-contained-dsp/lesson12-room-after-dsp.wav
course_assets/module_4/voice_candidates/lesson12-self-contained-dsp/lesson12-room-before.wav
course_assets/module_4/voice_candidates/prepare_filter_v3.py
course_assets/module_4/voice_candidates/prepare_room_noise_v2.py
course_assets/module_4/voice_candidates/prepare_self_contained_dsp.py
course_assets/module_4/voice_candidates/requirements-evaluation.txt
course_assets/module_4/voice_candidates/ru_roman_refined/README.md
course_assets/module_4/voice_candidates/ru_roman_refined/m4-l10-ru-roman-tts-candidate.wav
course_assets/module_4/voice_candidates/ru_roman_refined/m4-l11-ru-roman-speech-candidate.wav
course_assets/module_4/voice_candidates/ru_roman_refined/m4-l11-ru-roman-synchronized-candidate.srt
course_assets/module_4/voice_candidates/ru_roman_refined/m4-l11-ru-roman-transcript.txt
course_assets/module_4/voice_candidates/ru_roman_refined/m4-l12-filter-balanced-v3.wav
course_assets/module_4/voice_candidates/ru_roman_refined/m4-l12-filter-gentle-v3.wav
course_assets/module_4/voice_candidates/ru_roman_refined/m4-l12-filter-strong-v3.wav
course_assets/module_4/voice_candidates/ru_roman_refined/m4-l12-filter-v3-notes.md
course_assets/module_4/voice_candidates/ru_roman_refined/m4-l12-filter-v3-report.json
course_assets/module_4/voice_candidates/ru_roman_refined/m4-l12-ru-roman-clean-candidate.wav
course_assets/module_4/voice_candidates/ru_roman_refined/m4-l12-ru-roman-filtered-candidate.wav
course_assets/module_4/voice_candidates/ru_roman_refined/m4-l12-ru-roman-noisy-candidate.wav
course_assets/module_4/voice_candidates/ru_roman_refined/production-candidates.json
course_assets/module_4/voice_candidates/ru_roman_refined/ru-roman-variant-a-neutral.wav
course_assets/module_4/voice_candidates/ru_roman_refined/ru-roman-variant-b-clear-pauses.wav
course_assets/module_4/voice_candidates/test_candidates.py
course_assets/module_4/voice_candidates/test_filter_v3.py
course_assets/module_4/voice_candidates/test_roman_module4.py
course_assets/module_4/voice_candidates/test_room_noise_v2.py
course_assets/module_4/voice_candidates/test_self_contained_dsp.py
course_assets/module_4/voice_candidates/v5_cis_base_nostress-ru_marat.wav
course_assets/module_4/voice_candidates/v5_cis_base_nostress-ru_roman.wav
course_assets/module_4/voice_candidates/v5_cis_base_nostress-ru_zhadyra.wav
course_assets/module_5/m5-l13-v1-production/narration-preview.wav
courses/test_module4_audio.py
docs/courses/media-module-4-legacy-assets.json
docs/courses/module-4-audio-demonstrations.md
docs/courses/module-4-cleanup-inventory.json
docs/courses/module-4-elevenlabs-provenance.json
docs/courses/module-4-rnnoise-COPYING.txt
docs/courses/module-4-rnnoise-license-audit.json
docs/frontend-unslop-audit.md
e modules 2-4 and inline learning media"
scripts/generate_module_4_audio.py
```

Ignored exclusions remain in place: all SQLite databases/sidecars, protected
`media/`, `.local-course-backups/`, `.local-redesign-checkpoints/`,
`.playwright-mcp/`, `.local-silero-eval/`, `.venv/`, private `course_sources/`,
frontend dependencies/build output and temporary browser environments. None was
staged. No credential/environment file, auth token/cookie, model weights or
unapproved generated audio/video was selected. No local file was deleted.

## Preservation and push readiness

- Live SQLite SHA-256 matches the start-of-task baseline, proving stored course
  content and all student/certificate data bytes are unchanged during this task.
- All pre-existing protected media, original DOCX and audio/image bytes match
  baseline hashes. Only the four documented Module 5 authoring text files changed.
- No real import, account mutation, certificate issuance, migration, publication
  or deployment occurred. All intended allowlisted production source and required
  helper/license dependencies are included; generated preview audio is excluded.
- These four commits are ready for a separately authorized **eventual push**
  after checking remote freshness/conflicts. No fetch or push is performed here;
  local tracking status is not proof of the remote's current state.
- Remaining limitations: source-only narration reproducibility requires the
  documented isolated CPU PyTorch environment and pinned licensed model (not
  installed or redistributed here); narration still needs author approval and
  Module 5 final recordings/VTT do not yet exist. Deployment still requires
  same-origin HTTPS `/api`, private storage, maintained ffprobe and grant cleanup.
- Final status/log and intended-file coverage must be checked after the fourth
  commit. The index should be empty; local exclusions should remain unchanged.
