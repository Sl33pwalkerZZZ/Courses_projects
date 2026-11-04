# Post-redesign Git checkpoint readiness

> Historical audit and proposed lists. The authorized local finalization, resolved
> findings and **superseding exact four-commit lists** are recorded in
> [git-checkpoint-finalization.md](git-checkpoint-finalization.md). In particular,
> the unapproved Module 5 preview WAV below is excluded from the final commits.

Audit date: 2026-11-04. Branch: `design/amethyst-motion`. HEAD: `5cf26f9` (`feat: finalize module 4 audio lessons with Silero TTS`).

This is preparation only. Nothing has been staged, committed, pushed, deleted, restored or imported. The only project file created by this audit is this report. Existing source, settings, SQLite and protected assets were not edited. Tests use isolated databases and temporary media; build/cache outputs are ignored.

## Decision

The current frontend and relevant protected-video/import regressions pass together. A focused checkpoint is feasible with the exact lists below. Do not use `git add .` or `git add -A`. Separate code from local data and historical experiments. Review the noted documentation/reproducibility caveats before approving staging.

## Working tree

- Initial inventory: **36 modified tracked files**, **136 untracked files**; no staged changes or merge-conflict paths. This report adds one further untracked file.
- `git status -sb`: local branch tracks `origin/design/amethyst-motion`, without an ahead/behind marker at inspection; no fetch was performed, so this is not proof of remote freshness.
- `git diff --stat`: 36 files, 447 insertions, 89 deletions (tracked changes only; excludes new files).
- `git diff --check`: passed.
- Intentional `config/settings.py` changes are excluded from every proposed commit. No settings values or credentials are reproduced here.

## Validation performed in this audit

| Check | Result |
| --- | --- |
| Full frontend suite: `node --test --test-concurrency=2 tests/*.test.mjs` in `frontend/` | PASS: 34 test files, 0 failed/skipped |
| `npm run lint` | PASS (project uses Oxlint) |
| `npm run build` | PASS: 2,547 modules transformed |
| `.venv/bin/python -B manage.py check` | PASS: no issues |
| `.venv/bin/python -B manage.py makemigrations --check --dry-run` | PASS: no changes detected |
| `.venv/bin/python -B manage.py migrate --plan` | PASS: no planned operations; no migration applied |
| Relevant Django regression suite below | PASS: 62 tests, no reported skips |
| `scripts/validate_media_module_5_sources.py` | PASS: three lessons, three objectives/nine sections each; nine planned videos + nine planned VTTs, no claimed real video files |
| Module 5 `validate_package.py` | PASS: narration/checksum/PCM, six synthesis segments, five-scene storyboard, two original SVGs, license notice, no fake final MP4/VTT |
| Whitespace check | PASS |

Django suite:

```sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -B manage.py test \
  courses.test_video courses.test_video_upload courses.test_real_video \
  courses.test_media_module_5 courses.test_lesson_media_import \
  courses.test_final_module4_assets studio.test_role_security --noinput
```

The first sandboxed Django run stalled in asynchronous streaming verification and was interrupted. The complete 62-test run passed outside that sandbox restriction using isolated test DB/temp media. No development data was used as a mutation target. Actual ffprobe/FFmpeg local-sample regression is included; the local MP4 itself is deliberately excluded from Git. On clean checkouts the opt-in real-video test skips without the local sample/ffprobe; ordinary video tests remain available.

Coverage includes authorization, grants/revocation/expiry, Range/HEAD, real MP4 delivery/decoding, upload ownership, Module 5 conflict/idempotency/rollback, audio/SRT imports, final Module 4 source integrity and Studio role isolation. Frontend checks cover cinematic landing, Studio dashboard, student presentation, session isolation, enrollment, quiz and protected media. This is evidence of no detected regression in those checks, not proof of every authenticated user flow.

No fresh browser session was run in this Git audit. Existing local browser evidence is retained under `.playwright-mcp/cinematic/`, `studio-phase2/`, and `student-phase3/` (including `resume/`). Phase 3 documentation records 190 original checks and 56 targeted resume checks, public real-page verification plus protected presentation fixtures. Those are historical results, not new browser passes. Real authenticated student/teacher flows remain limited by unavailable authorized test sessions.

A native **security_reviewer** ran a read-only video/checkpoint review. No confirmed authorization bypass was found in the traced paths. It flagged the dependency and stale activation documentation below; it did not run tests or browser checks. No other review agent was run for this audit.

## Exact classification manifest

Every initially modified/untracked file appears exactly once below. `M` means tracked modification; `??` means untracked. Categories: **A** production code; **B** tests/documentation; **C** versionable source/content assets; **D** local configuration/secrets boundary; **E** generated/historical media (retain locally); **F** temporary QA/browser artifacts; **G** separate manual review. A category does not authorize deletion.

Category counts before this report: A: 46, B: 30, C: 18, D: 1, E: 25, F: 6, G: 46.

| Category | State | Exact path | Disposition |
| --- | --- | --- | --- |
| G | ?? | `.agents/skills/unslop/SKILL.md` | HOLD: third-party tooling/accidental filename; separate manual review |
| G | ?? | `.agents/skills/unslop/agents/openai.yaml` | HOLD: third-party tooling/accidental filename; separate manual review |
| G | ?? | `.agents/skills/unslop/references/effects.md` | HOLD: third-party tooling/accidental filename; separate manual review |
| G | ?? | `.agents/skills/unslop/references/refs.md` | HOLD: third-party tooling/accidental filename; separate manual review |
| G | ?? | `.agents/skills/unslop/references/refs/beacon-engraving.webp` | HOLD: third-party tooling/accidental filename; separate manual review |
| G | ?? | `.agents/skills/unslop/references/refs/meadow-3d.webp` | HOLD: third-party tooling/accidental filename; separate manual review |
| G | ?? | `.agents/skills/unslop/references/refs/story-dashboard-frames.webp` | HOLD: third-party tooling/accidental filename; separate manual review |
| G | ?? | `.agents/skills/unslop/references/refs/unslop-dashboard-after.webp` | HOLD: third-party tooling/accidental filename; separate manual review |
| G | ?? | `.agents/skills/unslop/references/refs/unslop-hero-after.webp` | HOLD: third-party tooling/accidental filename; separate manual review |
| G | ?? | `.agents/skills/unslop/references/signs.md` | HOLD: third-party tooling/accidental filename; separate manual review |
| G | ?? | `.agents/skills/unslop/references/tokens.md` | HOLD: third-party tooling/accidental filename; separate manual review |
| G | ?? | `.agents/skills/unslop/references/visuals.md` | HOLD: third-party tooling/accidental filename; separate manual review |
| G | ?? | `.agents/skills/unslop/scripts/snapshot.mjs` | HOLD: third-party tooling/accidental filename; separate manual review |
| G | ?? | `.agents/skills/unslop/scripts/story.mjs` | HOLD: third-party tooling/accidental filename; separate manual review |
| F | ?? | `.local-cinematic-qa/.gitignore` | EXCLUDE: local QA scripts/receipts/sample; preserve, do not delete |
| F | ?? | `.local-video-test/cleanup-fixture.py` | EXCLUDE: local QA scripts/receipts/sample; preserve, do not delete |
| F | ?? | `.local-video-test/cleanup-result.json` | EXCLUDE: local QA scripts/receipts/sample; preserve, do not delete |
| F | ?? | `.local-video-test/prepare-fixture.py` | EXCLUDE: local QA scripts/receipts/sample; preserve, do not delete |
| F | ?? | `.local-video-test/prepared-fixture.json` | EXCLUDE: local QA scripts/receipts/sample; preserve, do not delete |
| F | ?? | `.local-video-test/sample.mp4` | EXCLUDE: local QA scripts/receipts/sample; preserve, do not delete |
| D | M | `config/settings.py` | EXCLUDE: intentional machine-local configuration; preserve unchanged |
| G | ?? | `course_assets/module_4/m4-audio-production.json` | EXCLUDE: historical Module 4 source/candidate; preserve provenance and rollback originals locally |
| E | ?? | `course_assets/module_4/m4-l1-f1-natural-narration.mp3` | EXCLUDE: historical Module 4 source/candidate; preserve provenance and rollback originals locally |
| E | ?? | `course_assets/module_4/m4-l1-f1-synthetic-narration.wav` | EXCLUDE: historical Module 4 source/candidate; preserve provenance and rollback originals locally |
| E | ?? | `course_assets/module_4/m4-l12-ru-roman-room-after-v2.wav` | EXCLUDE: historical Module 4 source/candidate; preserve provenance and rollback originals locally |
| E | ?? | `course_assets/module_4/m4-l12-ru-roman-room-before-v2.wav` | EXCLUDE: historical Module 4 source/candidate; preserve provenance and rollback originals locally |
| G | ?? | `course_assets/module_4/m4-l2-f1-corrected-transcript.txt` | EXCLUDE: historical Module 4 source/candidate; preserve provenance and rollback originals locally |
| E | ?? | `course_assets/module_4/m4-l2-f1-speech.wav` | EXCLUDE: historical Module 4 source/candidate; preserve provenance and rollback originals locally |
| E | ?? | `course_assets/module_4/m4-l2-f1-synchronized.srt` | EXCLUDE: historical Module 4 source/candidate; preserve provenance and rollback originals locally |
| E | ?? | `course_assets/module_4/m4-l3-f1-clean-reference.wav` | EXCLUDE: historical Module 4 source/candidate; preserve provenance and rollback originals locally |
| E | ?? | `course_assets/module_4/m4-l3-f1-original.wav` | EXCLUDE: historical Module 4 source/candidate; preserve provenance and rollback originals locally |
| E | ?? | `course_assets/module_4/m4-l3-f1-processed.wav` | EXCLUDE: historical Module 4 source/candidate; preserve provenance and rollback originals locally |
| G | ?? | `course_assets/module_4/m4-room-noise-v2.json` | EXCLUDE: historical Module 4 source/candidate; preserve provenance and rollback originals locally |
| C | ?? | `course_assets/module_4/voice_candidates/LICENSE_CIS` | C4 — optional draft-production source package; retain dependency pair |
| G | ?? | `course_assets/module_4/voice_candidates/README.md` | EXCLUDE: historical Module 4 source/candidate; preserve provenance and rollback originals locally |
| G | ?? | `course_assets/module_4/voice_candidates/evaluation.json` | EXCLUDE: historical Module 4 source/candidate; preserve provenance and rollback originals locally |
| G | ?? | `course_assets/module_4/voice_candidates/generate_candidates.py` | EXCLUDE: historical Module 4 source/candidate; preserve provenance and rollback originals locally |
| G | ?? | `course_assets/module_4/voice_candidates/lesson12-self-contained-dsp/README.md` | EXCLUDE: historical Module 4 source/candidate; preserve provenance and rollback originals locally |
| G | ?? | `course_assets/module_4/voice_candidates/lesson12-self-contained-dsp/demonstration.json` | EXCLUDE: historical Module 4 source/candidate; preserve provenance and rollback originals locally |
| E | ?? | `course_assets/module_4/voice_candidates/lesson12-self-contained-dsp/lesson12-room-after-dsp.wav` | EXCLUDE: historical Module 4 source/candidate; preserve provenance and rollback originals locally |
| E | ?? | `course_assets/module_4/voice_candidates/lesson12-self-contained-dsp/lesson12-room-before.wav` | EXCLUDE: historical Module 4 source/candidate; preserve provenance and rollback originals locally |
| G | ?? | `course_assets/module_4/voice_candidates/prepare_filter_v3.py` | EXCLUDE: historical Module 4 source/candidate; preserve provenance and rollback originals locally |
| C | ?? | `course_assets/module_4/voice_candidates/prepare_roman_module4.py` | C4 — optional draft-production source package; retain dependency pair |
| G | ?? | `course_assets/module_4/voice_candidates/prepare_room_noise_v2.py` | EXCLUDE: historical Module 4 source/candidate; preserve provenance and rollback originals locally |
| G | ?? | `course_assets/module_4/voice_candidates/prepare_self_contained_dsp.py` | EXCLUDE: historical Module 4 source/candidate; preserve provenance and rollback originals locally |
| G | ?? | `course_assets/module_4/voice_candidates/requirements-evaluation.txt` | EXCLUDE: historical Module 4 source/candidate; preserve provenance and rollback originals locally |
| G | ?? | `course_assets/module_4/voice_candidates/ru_roman_refined/README.md` | EXCLUDE: historical Module 4 source/candidate; preserve provenance and rollback originals locally |
| E | ?? | `course_assets/module_4/voice_candidates/ru_roman_refined/m4-l10-ru-roman-tts-candidate.wav` | EXCLUDE: historical Module 4 source/candidate; preserve provenance and rollback originals locally |
| E | ?? | `course_assets/module_4/voice_candidates/ru_roman_refined/m4-l11-ru-roman-speech-candidate.wav` | EXCLUDE: historical Module 4 source/candidate; preserve provenance and rollback originals locally |
| E | ?? | `course_assets/module_4/voice_candidates/ru_roman_refined/m4-l11-ru-roman-synchronized-candidate.srt` | EXCLUDE: historical Module 4 source/candidate; preserve provenance and rollback originals locally |
| G | ?? | `course_assets/module_4/voice_candidates/ru_roman_refined/m4-l11-ru-roman-transcript.txt` | EXCLUDE: historical Module 4 source/candidate; preserve provenance and rollback originals locally |
| E | ?? | `course_assets/module_4/voice_candidates/ru_roman_refined/m4-l12-filter-balanced-v3.wav` | EXCLUDE: historical Module 4 source/candidate; preserve provenance and rollback originals locally |
| E | ?? | `course_assets/module_4/voice_candidates/ru_roman_refined/m4-l12-filter-gentle-v3.wav` | EXCLUDE: historical Module 4 source/candidate; preserve provenance and rollback originals locally |
| E | ?? | `course_assets/module_4/voice_candidates/ru_roman_refined/m4-l12-filter-strong-v3.wav` | EXCLUDE: historical Module 4 source/candidate; preserve provenance and rollback originals locally |
| G | ?? | `course_assets/module_4/voice_candidates/ru_roman_refined/m4-l12-filter-v3-notes.md` | EXCLUDE: historical Module 4 source/candidate; preserve provenance and rollback originals locally |
| G | ?? | `course_assets/module_4/voice_candidates/ru_roman_refined/m4-l12-filter-v3-report.json` | EXCLUDE: historical Module 4 source/candidate; preserve provenance and rollback originals locally |
| E | ?? | `course_assets/module_4/voice_candidates/ru_roman_refined/m4-l12-ru-roman-clean-candidate.wav` | EXCLUDE: historical Module 4 source/candidate; preserve provenance and rollback originals locally |
| E | ?? | `course_assets/module_4/voice_candidates/ru_roman_refined/m4-l12-ru-roman-filtered-candidate.wav` | EXCLUDE: historical Module 4 source/candidate; preserve provenance and rollback originals locally |
| E | ?? | `course_assets/module_4/voice_candidates/ru_roman_refined/m4-l12-ru-roman-noisy-candidate.wav` | EXCLUDE: historical Module 4 source/candidate; preserve provenance and rollback originals locally |
| G | ?? | `course_assets/module_4/voice_candidates/ru_roman_refined/production-candidates.json` | EXCLUDE: historical Module 4 source/candidate; preserve provenance and rollback originals locally |
| E | ?? | `course_assets/module_4/voice_candidates/ru_roman_refined/ru-roman-variant-a-neutral.wav` | EXCLUDE: historical Module 4 source/candidate; preserve provenance and rollback originals locally |
| E | ?? | `course_assets/module_4/voice_candidates/ru_roman_refined/ru-roman-variant-b-clear-pauses.wav` | EXCLUDE: historical Module 4 source/candidate; preserve provenance and rollback originals locally |
| G | ?? | `course_assets/module_4/voice_candidates/test_candidates.py` | EXCLUDE: historical Module 4 source/candidate; preserve provenance and rollback originals locally |
| G | ?? | `course_assets/module_4/voice_candidates/test_filter_v3.py` | EXCLUDE: historical Module 4 source/candidate; preserve provenance and rollback originals locally |
| G | ?? | `course_assets/module_4/voice_candidates/test_roman_module4.py` | EXCLUDE: historical Module 4 source/candidate; preserve provenance and rollback originals locally |
| G | ?? | `course_assets/module_4/voice_candidates/test_room_noise_v2.py` | EXCLUDE: historical Module 4 source/candidate; preserve provenance and rollback originals locally |
| G | ?? | `course_assets/module_4/voice_candidates/test_self_contained_dsp.py` | EXCLUDE: historical Module 4 source/candidate; preserve provenance and rollback originals locally |
| E | ?? | `course_assets/module_4/voice_candidates/v5_cis_base_nostress-ru_marat.wav` | EXCLUDE: historical Module 4 source/candidate; preserve provenance and rollback originals locally |
| E | ?? | `course_assets/module_4/voice_candidates/v5_cis_base_nostress-ru_roman.wav` | EXCLUDE: historical Module 4 source/candidate; preserve provenance and rollback originals locally |
| E | ?? | `course_assets/module_4/voice_candidates/v5_cis_base_nostress-ru_zhadyra.wav` | EXCLUDE: historical Module 4 source/candidate; preserve provenance and rollback originals locally |
| C | ?? | `course_assets/module_5/m5-l13-v1-production/F1_video/notes/brief.md` | C4 — optional draft-production source package; retain dependency pair |
| C | ?? | `course_assets/module_5/m5-l13-v1-production/F1_video/notes/permission-checklist.csv` | C4 — optional draft-production source package; retain dependency pair |
| C | ?? | `course_assets/module_5/m5-l13-v1-production/LICENSE_CIS` | C4 — optional draft-production source package; retain dependency pair |
| C | ?? | `course_assets/module_5/m5-l13-v1-production/README.md` | C4 — optional draft-production source package; retain dependency pair |
| C | ?? | `course_assets/module_5/m5-l13-v1-production/five-scene-storyboard.md` | C4 — optional draft-production source package; retain dependency pair |
| C | ?? | `course_assets/module_5/m5-l13-v1-production/generate_preview.py` | C4 — optional draft-production source package; retain dependency pair |
| C | ?? | `course_assets/module_5/m5-l13-v1-production/narration-preview.wav` | C4 — optional draft-production source package; retain dependency pair |
| C | ?? | `course_assets/module_5/m5-l13-v1-production/narration-provenance.json` | C4 — optional draft-production source package; retain dependency pair |
| C | ?? | `course_assets/module_5/m5-l13-v1-production/narration-script-ru.txt` | C4 — optional draft-production source package; retain dependency pair |
| C | ?? | `course_assets/module_5/m5-l13-v1-production/originals/f1-notepad-diagram.svg` | C4 — optional draft-production source package; retain dependency pair |
| C | ?? | `course_assets/module_5/m5-l13-v1-production/originals/f1-paper-diagram.svg` | C4 — optional draft-production source package; retain dependency pair |
| C | ?? | `course_assets/module_5/m5-l13-v1-production/permission-review-template.md` | C4 — optional draft-production source package; retain dependency pair |
| C | ?? | `course_assets/module_5/m5-l13-v1-production/recording-checklist.md` | C4 — optional draft-production source package; retain dependency pair |
| C | ?? | `course_assets/module_5/m5-l13-v1-production/storyboard-source.json` | C4 — optional draft-production source package; retain dependency pair |
| C | ?? | `course_assets/module_5/m5-l13-v1-production/validate_package.py` | C4 — optional draft-production source package; retain dependency pair |
| A | M | `courses/attachments.py` | C1 — propose versioning |
| A | ?? | `courses/management/commands/import_media_module_5.py` | C2 — propose versioning |
| C | ?? | `courses/management/media_module_5.json` | C2 — propose versioning |
| A | ?? | `courses/migrations/0006_lessonattachment_video_vtt.py` | C1 — propose versioning |
| A | ?? | `courses/migrations/0007_lessonplaybackgrant.py` | C1 — propose versioning |
| A | M | `courses/models.py` | C1 — propose versioning |
| A | M | `courses/serializers.py` | C1 — propose versioning |
| B | ?? | `courses/test_media_module_5.py` | C2 — propose versioning |
| G | ?? | `courses/test_module4_audio.py` | HOLD: historical experiment/test/audit; not required for final feature checkpoint |
| B | ?? | `courses/test_real_video.py` | C1 — propose versioning |
| B | ?? | `courses/test_video.py` | C1 — propose versioning |
| B | ?? | `courses/test_video_upload.py` | C1 — propose versioning |
| A | M | `courses/urls.py` | C1 — propose versioning |
| A | ?? | `courses/video.py` | C1 — propose versioning |
| A | ?? | `courses/video_validation.py` | C1 — propose versioning |
| B | ?? | `docs/cinematic-landing-phase-1.md` | C3 — propose versioning |
| B | ?? | `docs/cinematic-student-phase-3.md` | C3 — propose versioning |
| B | ?? | `docs/cinematic-studio-phase-2.md` | C3 — propose versioning |
| G | ?? | `docs/courses/media-module-4-legacy-assets.json` | HOLD: historical experiment/test/audit; not required for final feature checkpoint |
| B | ?? | `docs/courses/media-module-5-assets.json` | C2 — propose versioning |
| B | ?? | `docs/courses/media-module-5-content-review.md` | C2 — propose versioning |
| B | ?? | `docs/courses/media-module-5-import-readiness.md` | C2 — propose versioning |
| B | ?? | `docs/courses/media-module-5-plan.md` | C2 — propose versioning |
| B | ?? | `docs/courses/media-module-5-storyboards.json` | C2 — propose versioning |
| B | ?? | `docs/courses/media-module-5-validation.md` | C2 — propose versioning |
| G | ?? | `docs/courses/module-4-audio-demonstrations.md` | HOLD: historical experiment/test/audit; not required for final feature checkpoint |
| G | ?? | `docs/courses/module-4-cleanup-inventory.json` | HOLD: historical experiment/test/audit; not required for final feature checkpoint |
| G | ?? | `docs/courses/module-4-elevenlabs-provenance.json` | HOLD: historical experiment/test/audit; not required for final feature checkpoint |
| G | ?? | `docs/courses/module-4-rnnoise-COPYING.txt` | HOLD: historical experiment/test/audit; not required for final feature checkpoint |
| G | ?? | `docs/courses/module-4-rnnoise-license-audit.json` | HOLD: historical experiment/test/audit; not required for final feature checkpoint |
| G | ?? | `docs/frontend-unslop-audit.md` | HOLD: historical experiment/test/audit; not required for final feature checkpoint |
| B | ?? | `docs/protected-lesson-video.md` | C1 — propose versioning |
| B | ?? | `docs/protected-video-verification.md` | C1 — propose versioning |
| G | ?? | `e modules 2-4 and inline learning media"` | HOLD: third-party tooling/accidental filename; separate manual review |
| A | M | `frontend/src/api.js` | C3 — propose versioning |
| A | M | `frontend/src/components/AuthLayout.css` | C3 — propose versioning |
| A | M | `frontend/src/components/AuthLayout.jsx` | C3 — propose versioning |
| A | M | `frontend/src/components/HomeHero.jsx` | C3 — propose versioning |
| A | M | `frontend/src/components/certificates/certificates.css` | C3 — propose versioning |
| A | M | `frontend/src/components/instructor/LessonAttachmentManager.jsx` | C3 — propose versioning |
| A | ?? | `frontend/src/components/instructor/StudioCourseCollection.jsx` | C3 — propose versioning |
| A | ?? | `frontend/src/components/instructor/StudioDashboard.jsx` | C3 — propose versioning |
| A | ?? | `frontend/src/components/instructor/StudioNavigation.jsx` | C3 — propose versioning |
| A | ?? | `frontend/src/components/landing/ClosingInvitation.jsx` | C3 — propose versioning |
| A | ?? | `frontend/src/components/landing/DepthSurface.jsx` | C3 — propose versioning |
| A | ?? | `frontend/src/components/landing/LandingCoursePreview.jsx` | C3 — propose versioning |
| A | ?? | `frontend/src/components/landing/LearningShowcase.jsx` | C3 — propose versioning |
| A | M | `frontend/src/components/learning/LearningContent.jsx` | C3 — propose versioning |
| A | M | `frontend/src/components/learning/LessonAttachment.jsx` | C3 — propose versioning |
| A | ?? | `frontend/src/components/learning/LessonSectionNavigation.jsx` | C3 — propose versioning |
| A | ?? | `frontend/src/components/learning/LessonVideo.jsx` | C3 — propose versioning |
| A | M | `frontend/src/components/learning/MediaLessonReading.jsx` | C3 — propose versioning |
| A | M | `frontend/src/components/learning/lessonAttachments.css` | C3 — propose versioning |
| A | M | `frontend/src/components/learning/mediaLessonReading.css` | C3 — propose versioning |
| A | M | `frontend/src/i18n/locales/en.json` | C3 — propose versioning |
| A | M | `frontend/src/i18n/locales/kk.json` | C3 — propose versioning |
| A | M | `frontend/src/i18n/locales/ru.json` | C3 — propose versioning |
| A | M | `frontend/src/pages/CertificateVerification.jsx` | C3 — propose versioning |
| A | M | `frontend/src/pages/CourseCatalog.jsx` | C3 — propose versioning |
| A | M | `frontend/src/pages/CourseDetail.css` | C3 — propose versioning |
| A | M | `frontend/src/pages/LessonView.css` | C3 — propose versioning |
| A | M | `frontend/src/pages/Profile.css` | C3 — propose versioning |
| A | M | `frontend/src/pages/Profile.jsx` | C3 — propose versioning |
| A | M | `frontend/src/pages/instructor/CourseEditor.jsx` | C3 — propose versioning |
| A | M | `frontend/src/pages/instructor/InstructorStudio.jsx` | C3 — propose versioning |
| A | ?? | `frontend/src/pages/instructor/studio-command.css` | C3 — propose versioning |
| A | ?? | `frontend/src/styles/cinematic-landing.css` | C3 — propose versioning |
| A | M | `frontend/src/utils/lessonAttachments.js` | C3 — propose versioning |
| A | ?? | `frontend/src/utils/lessonVideo.js` | C3 — propose versioning |
| B | ?? | `frontend/tests/browser/student-workspace.html` | C3 — propose versioning |
| B | ?? | `frontend/tests/browser/student-workspace.jsx` | C3 — propose versioning |
| B | ?? | `frontend/tests/browser/studio-workspace.html` | C3 — propose versioning |
| B | ?? | `frontend/tests/browser/studio-workspace.jsx` | C3 — propose versioning |
| B | ?? | `frontend/tests/cinematic-landing.test.mjs` | C3 — propose versioning |
| B | M | `frontend/tests/design-foundations.test.mjs` | C3 — propose versioning |
| B | M | `frontend/tests/enrollment-requests.test.mjs` | C3 — propose versioning |
| B | M | `frontend/tests/inline-images.test.mjs` | C3 — propose versioning |
| B | M | `frontend/tests/lesson-attachments.test.mjs` | C3 — propose versioning |
| B | ?? | `frontend/tests/lesson-video.test.mjs` | C3 — propose versioning |
| B | M | `frontend/tests/media-lesson.test.mjs` | C3 — propose versioning |
| B | M | `frontend/tests/session-isolation.test.mjs` | C3 — propose versioning |
| B | ?? | `frontend/tests/student-experience.test.mjs` | C3 — propose versioning |
| B | ?? | `frontend/tests/studio-dashboard-design.test.mjs` | C3 — propose versioning |
| A | M | `frontend/vite.config.js` | C3 — propose versioning |
| G | ?? | `scripts/generate_module_4_audio.py` | HOLD: historical experiment/test/audit; not required for final feature checkpoint |
| B | ?? | `scripts/validate_media_module_5_sources.py` | C2 — propose versioning |
| A | M | `studio/views.py` | C1 — propose versioning |
| B | ?? | `docs/git-checkpoint-readiness.md` | C3 — include audit report after approval |

## Suggested commits and exact file lists

These lists are proposals, not staged files. C1 → C2 → C3 form the recommended application checkpoint. Keeping the frontend integration and all three redesign phases together avoids splitting shared locale, media CSS and session-test files into fragile partial hunks. C4 is a separate optional authoring-package checkpoint; it is draft source material, not completed video production or permission to attach/publish it.

### C1: `feat: add protected instructional video backend`

Include both additive migrations with their model and delivery implementation. Existing tracked dependencies are already in HEAD. Backend-only checkpoint; full UI integration arrives in C3. Activation text in the documentation must be understood as the original Phase 5A boundary, not current DB state.

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

### C2: `feat: add safe module 5 content import and storyboards`

Text import only into existing draft course 10. No real MP4/VTT assets are claimed or created. No import executed in this audit.

```text
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

### C3: `feat: complete cinematic public studio and student experience`

Includes reusable video UI alongside Phases 1–3 because locales and shared readers span these features. Include isolated browser fixture source; exclude screenshot bundles and local harness environments.

```text
docs/cinematic-landing-phase-1.md
docs/cinematic-student-phase-3.md
docs/cinematic-studio-phase-2.md
docs/git-checkpoint-readiness.md
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

### C4: `chore: preserve first module 5 video authoring package`

Retain **both** Module 4 helper and its license notice listed below: `generate_preview.py` dynamically imports that helper, and `validate_package.py` compares that license. Excluding either would make the package incomplete. The 59.2125-second WAV is an explicitly labeled draft, not an approved 110-second final demonstration. Requires external isolated PyTorch environment and the pinned MIT checkpoint; do not commit environments/model weights or infer publication approval. Current generator is create-only and intentionally refuses to overwrite its existing output.

```text
course_assets/module_4/voice_candidates/LICENSE_CIS
course_assets/module_4/voice_candidates/prepare_roman_module4.py
course_assets/module_5/m5-l13-v1-production/F1_video/notes/brief.md
course_assets/module_5/m5-l13-v1-production/F1_video/notes/permission-checklist.csv
course_assets/module_5/m5-l13-v1-production/LICENSE_CIS
course_assets/module_5/m5-l13-v1-production/README.md
course_assets/module_5/m5-l13-v1-production/five-scene-storyboard.md
course_assets/module_5/m5-l13-v1-production/generate_preview.py
course_assets/module_5/m5-l13-v1-production/narration-preview.wav
course_assets/module_5/m5-l13-v1-production/narration-provenance.json
course_assets/module_5/m5-l13-v1-production/narration-script-ru.txt
course_assets/module_5/m5-l13-v1-production/originals/f1-notepad-diagram.svg
course_assets/module_5/m5-l13-v1-production/originals/f1-paper-diagram.svg
course_assets/module_5/m5-l13-v1-production/permission-review-template.md
course_assets/module_5/m5-l13-v1-production/recording-checklist.md
course_assets/module_5/m5-l13-v1-production/storyboard-source.json
course_assets/module_5/m5-l13-v1-production/validate_package.py
```

## Existing Module 4 final assets: already versioned

The seven canonical assets below are already tracked at HEAD. They need no duplicate staging and no legacy candidate substitutions. `courses.test_final_module4_assets` passed actual SHA-256, WAV integrity, approved manifest/licensing and synchronized-subtitle checks.

```text
course_assets/module_4/m4-l10-silero-ru-roman-approved.wav
course_assets/module_4/m4-l11-silero-ru-roman-approved.wav
course_assets/module_4/m4-l11-silero-ru-roman-synchronized.srt
course_assets/module_4/m4-l12-silero-ru-roman-after-dsp.wav
course_assets/module_4/m4-l12-silero-ru-roman-before.wav
course_assets/module_4/m4-l2-f1-example.srt
course_assets/module_4/m4-l3-audio-workflow.png
```

The tracked `course_assets/module_4/LICENSE_CIS`, `docs/courses/media-module-4-assets.json`, `module-4-final-provenance.json`, `module-4-editorial-corrections.json` and existing import/finalization commands retain the final MIT attribution, production plan and reproducible editorial corrections. Historical ElevenLabs Free, eSpeak, RNNoise and DSP experiments in the classification table are **not** production dependencies. Preserve the approved original candidate files for rollback; this audit does not delete them.

## Explicit exclusions beyond the Git-visible manifest

| Boundary | Treatment |
| --- | --- |
| `config/settings.py` | Intentional local edits; never stage wholesale |
| `db.sqlite3`, other `*.sqlite3`/SQLite sidecars | Local persistent data; exclude even if a filename is not covered by ignore rules |
| `media/` | Protected uploaded copies; never expose/version as public assets |
| `.local-course-backups/` | Private SQLite/media backups; keep separately |
| `.local-redesign-checkpoints/` | Recovery archives/manifests; local-only |
| `.playwright-mcp/` | Screenshots, browser logs/reports and automation artifacts; local evidence, excluded |
| `.local-cinematic-qa/`, `.local-video-test/` | QA runtime, local test media and fixture receipts/scripts; exclude |
| `.local-silero-eval/`, `.venv/`, `frontend/node_modules/` | Local environments and weights; exclude |
| `frontend/dist/`, Vite caches, `__pycache__/`, `*.pyc` | Generated outputs; exclude |
| `course_sources/` | Private DOCX/source ownership boundary; exclude |
| Credentials, `.env*`, tokens, private keys, account/session dumps | Never stage; none intentionally included |

Repository `.gitignore` explicitly excludes `.venv`, Python caches, `db.sqlite3`, `media`, `.idea`, redesign checkpoints, `course_sources` and course backups. Additional effective ignore rules cover browser artifacts, cinematic QA, Silero environment, frontend dependencies and build output. **`.local-video-test/` is Git-visible**: an explicit file allowlist remains essential. No ignore files were modified.

A bounded scan of the proposed lists checked private-key headers, common GitHub/AWS token formats and literal JWT patterns without printing values. This is not an exhaustive secret/PII audit; a staged diff review is still required after separate staging approval. Local settings, DBs, backup contents and account receipts were not opened for scanning. Template permission checklists are not signed permissions; narration provenance is draft-only.

## Backups and recovery boundaries

Backup availability was checked by filesystem metadata only. No backup contents or student records were read; this audit does **not** claim a new integrity/FK verification. Existing task reports recorded verified backups at their creation time.

Found 40 files under `.local-course-backups/`. Recent SQLite backup examples:

- `.local-course-backups/media-module-before-294cf29f8d3a4547b6393654f6ebf6eb.sqlite3` — 1,163,264 bytes.
- `.local-course-backups/media-module-before-4fd82db44287433182c7b99538100a52.sqlite3` — 1,163,264 bytes.
- `.local-course-backups/video-qa-cleanup-20261102T062248Z-9a9e5d6d/db.sqlite3` — 1,163,264 bytes.
- `.local-course-backups/video-qa-20261102T054726Z-0142bb2a/db.sqlite3` — 1,159,168 bytes.
- `.local-course-backups/before-video-migrations-20261102-101640.sqlite3` — 1,150,976 bytes.

Affected QA media backup availability: `.local-course-backups/video-qa-cleanup-20261102T062248Z-9a9e5d6d/media/` contains the saved QA MP4/VTT; Module 4 replacement media backup directory `module4-media-110d2c76257642adabb0977a467466c0/media/` is also present. These are historical scoped backups, not a verified complete current protected-media snapshot.

Frontend recovery files available (metadata only):

- `.local-redesign-checkpoints/amethyst-before-20261016-101103.tar.gz` — 194,867 bytes.
- `.local-redesign-checkpoints/amethyst-before-20261016-101103.tar.json` — 13,859 bytes.
- `.local-redesign-checkpoints/frontend-20261015-112926.json` — 12,415 bytes.
- `.local-redesign-checkpoints/frontend-20261015-112926.tar.gz` — 177,229 bytes.
- `.local-redesign-checkpoints/frontend-before-cinematic-20261103-103631.tar.gz` — 281,919 bytes.
- `.local-redesign-checkpoints/frontend-before-student-phase3-20261103-111802.tar.gz` — 293,710 bytes.
- `.local-redesign-checkpoints/frontend-before-studio-phase2-20261103-110050.tar.gz` — 287,258 bytes.
- `.local-redesign-checkpoints/frontend-before-unslop-20261103-100120.tar.gz` — 281,935 bytes.
- `.local-redesign-checkpoints/frontend-before-unslop-rollback-20261103-101706.tar.gz` — 282,845 bytes.
- `.local-redesign-checkpoints/student-phase3-resume-baseline.json` — 1,642 bytes.
- `.local-redesign-checkpoints/unslop-restoration-manifest-20261103-101706.json` — 8,733 bytes.
- `.local-redesign-checkpoints/unslop-retained-additions-20261103-101706/` — retained-additions directory (not an archive).

**Remaining backup gap:** no newly verified post-Module-5-import full SQLite + protected-media recovery set was established by this read-only audit. An off-machine copy and a successful restore test were not verified. Before future database/media writes, create and verify a fresh paired backup and record its restore procedure. A Git commit covers tracked source/assets only; it does not back up SQLite, protected uploads, untracked source audio, ignored archives or local environments.

## Risks and approval checklist

1. Preserve the exact allowlists. Many untracked files are valuable historical sources, not disposable. No bulk staging/cleaning.
2. `docs/protected-lesson-video.md` describes migrations 0006/0007 as not yet applied (original Phase 5A instructions). Today's migration plan has no pending operations. Reconcile its activation wording in a separately authorized documentation edit, or explicitly retain it as historical. This audit did not edit it.
3. C4 must include its two Module 4 helper/license dependencies. Its audio remains pending listening/author approval; planned MP4/VTT do not exist, and storyboard timings are not caption timings.
4. Keep public/private media boundaries: production needs same-origin HTTPS `/api`, trusted maintained ffprobe, private media storage, sensible proxy upload bounds and expired-grant retention. Existing feature defaults do not depend on staging the local settings file. An authorized stream/buffer cannot be retroactively recalled; grants recheck access on subsequent requests.
5. Local-only historical `courses/test_module4_audio.py` requires legacy generated files/scripts. It is intentionally not in the recommended checkpoint or focused suite; do not mistake it for a missing production test dependency. The seven final assets have their own tracked regression tests.
6. The odd Git-visible filename beginning `e modules 2-4` and `.agents/skills/unslop/` need separate manual ownership/licensing/intention review. They are excluded, preserved and were not invoked. No new Unslop changes were made.
7. Tests/build are fresh; browser evidence is historical and protected flows use presentation fixtures. Do not represent this checkpoint audit as a new authenticated end-to-end approval.
8. After approval to stage, inspect `git diff --cached --name-status`, `git diff --cached --check`, full staged diff and staged binary sizes, compare with these lists, and verify no source dependencies were omitted. Then seek the separately requested commit/push authorization; neither is performed now.

Stop point: audit and proposed checkpoint only. No Module 5 video production, Module 6 work, publication, deployment, staging, commit or push.

Bounded secret-pattern scan: no matches in proposed files. This does not certify absence of every possible secret or personal datum.
