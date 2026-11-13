# Lesson 115 — Production Package

**Historical package state (2026-11-09; superseded by P1K status below):** production planning prepared; no screen recordings, narration audio, Remotion renders, MP4s, WebVTT files or CapCut project files have been created here.
**Course:** 10, `ai-media-content` (keep unpublished)
**Lesson:** 115, `Экспорт, адаптация и подготовка видео к публикации`
**Source verification:** 2026-11-09.

## Current reproducibility status — P1K, 2026-11-13

The planning snapshot above and recording prerequisites below are historical. Production subsequently used explicitly labeled Remotion illustrations, not CapCut recordings. Three approved Full HD music-mixed videos and WebVTT pairs exist in `out/final-bgm/`; exact bytes are pinned by `courses/management/lesson115_final_video_integration.json`. Restore them from the private recovery media archive; Git intentionally excludes generated output and narration masters.

- `package-lock.json` pins the existing Remotion 4.0.540 dependency graph. It was generated offline from the identical Lesson 113 package graph, with npm updating only root package metadata; no packages were installed or upgraded. Install from this lock in a **separate checkout/environment**, not through the local shared `node_modules` symlink.
- `npm run verify` executes existing content/music tests, verifier regression tests, lock consistency, six exact asset hashes, ffprobe video/audio profiles and subtitle timing/placement checks. Requires Python 3.11+ and ffprobe. It never renders, imports, writes media or accesses Django/SQLite.
- `npm run verify -- --source-only` runs source checks without requiring archived finals. This is explicitly **not** final-media QA. `npm run lint` checks ESLint/TypeScript.
- Verification does not replace human listening, visual review or protected browser playback. The pinned final hashes preserve the already-approved deliverables.
- `render.mjs` hashes `scripts/` for the final-render gate. New verification source changes that input set; historical approval records remain untouched. A future render needs a new owner-approved, hash-matched record. Existing approved finals need no rerender for this tooling repair. The default renderer is not the final BGM integration path: follow the documented approved mixing workflow.
- Keep Lesson 113 shared primitives, composer source, font/SFX licenses, Silero CIS MIT provenance, and private music/narration masters available. A lockfile alone does not guarantee bit-identical TTS/rendering across platforms.

## Deliverables planned

| Key | Demonstration | Planned output | Inline placement | Target duration |
|---|---|---|---|---:|
| `m5-l15-v1` | Локальный экспорт и проверка настоящего файла | `m5-l15-v1-export-check.mp4` + `.vtt` | After section 3, `Экспорт проверочной версии в CapCut Desktop` | 120 s |
| `m5-l15-v2` | Вертикальная версия без потери смысла | `m5-l15-v2-vertical-adaptation.mp4` + `.vtt` | After section 5, `Адаптация 16:9 в 9:16` | 115 s |
| `m5-l15-v3` | Проверка файла перед передачей редактору | `m5-l15-v3-final-review.mp4` + `.vtt` | After section 7, `Редакторская проверка перед публикацией` | 115 s |

The IDs, target names, anchors and planned durations match the existing storyboard and asset manifest. Timings are editorial targets, not measured recording or caption cue times. The manifest remains untouched.

## Package map

- `narration/` — Russian voice scripts for recording/TTS after approval.
- `storyboards/` — timecoded plans separating real screen capture from labeled Remotion graphics.
- `ASSET_REQUIREMENTS.md` — inputs, files and outstanding approvals.
- `REMOTION_GRAPHICS.md` — reuse boundary and graphics that are safe to make schematically.
- `RECORDING_CHECKLIST.md` — capture procedure for actual CapCut operations.
- `AUDIO_SUBTITLE_WORKFLOW.md` — voice, mix and WebVTT timing workflow.
- `FINAL_QA.md` — technical, editorial, accessibility and approval gates.

## Source references

- Canonical lesson authoring snapshot: `courses/management/media_module_5.json` (working-tree modified; review current diff before later production).
- Existing detailed plans: `docs/courses/media-module-5-storyboards.json` and `docs/courses/media-module-5-assets.json`.
- Course audit/anchor evidence: `docs/project-audit/02-course-content-and-database-audit.md` and `docs/project-audit/03-media-and-production-audit.md`.
- Approved visual/audio pipeline: `video-production/lesson-113-production/` and `video-production/lesson-114-production/`. These directories are untracked and mixed with generated outputs/cache; consult source/docs only and do not copy or rerender wholesale.

## Production flow

1. Content owner approves the scripts and confirms fictional-example labels.
2. The recording operator supplies the actual CapCut Desktop version, operating system, interface language, capture method and an authorized test project. None is assumed by this package.
3. Prepare a separate F1 test project using original/permission-cleared assets. Keep originals and project files.
4. Record genuine CapCut actions. Do not reconstruct application chrome in Remotion. If a required control is absent in the installed build, stop and revise the demonstration plan with the owner.
5. Add Remotion titles/diagrams only as clearly labeled explanatory material, separate from the true app view.
6. Record/generate voice only after script approval and voice/distribution confirmation. Do not stretch the existing 64-second music master to cover these 115–120 second targets.
7. Edit from real recordings, then time WebVTT against final narration and final export. Produce previews before finals.
8. Run `FINAL_QA.md`, obtain human author review, then follow a separate explicit task for protected-media import. No import or course publication is authorized here.

## Human inputs required before recording

- Machine with CapCut Desktop installed and the exact build/OS/interface locale to be shown.
- A separate, clean project and approved F1 teaching assets/permission records. The F1 story is fictional; no real outcome or measured saving may be asserted.
- Approval of these narration drafts and the voice method. The existing Module 4 Silero voice/model is an available documented production method, but no new L15 voice file was generated or approved in this phase.
- Audio bed decision: the approved Minimal Tech Ambient master is about 64 seconds, while the existing mixer refuses videos over 62 seconds. Either use narration with no continuous music, or obtain a separately approved longer master/crossfade plan. Never loop or stretch without a reviewed seam.

No database, canonical course text, manifest, existing media or attachment record was changed.
