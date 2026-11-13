# Phase 5H — Lesson 113 Quality V2

This phase completes only Videos 2 and 3 and prepares review-only lesson synchronization/integration artifacts. Approved Video 1 has not been rendered or modified. No database, application, lesson-source JSON, original composition or old export was changed. No upload, publication, migration, commit or push.

## Design and instructional changes

Both new videos reuse the approved typography, palette, quiet pacing, stable schematic framing and repaired Quality V2 sound. The shared workspace persists across scenes. Movement demonstrates selection, placement, timing, a boundary crossing, reopening and restoring a source; there are no decorative arrows or floating transitions. Every scene says it is a diagram, not recorded CapCut operation. File names remain consistent with Video 1.

- Video 2, 47s: project creation; library/preview/timeline; import without premature timeline placement; select/preview; place first five-second clip; choose 16:9 without stretching; distinguish source, editable project and future export.
- Video 3, 54s: continue the same first clip; arrange five scenes; separate video/audio tracks; adjust first still from five to seven seconds while explicitly shifting neighbors; inspect the scene boundary; save reminder before reopening; check restored clip order/durations; conditional source recovery; editable-project versus exported-file check. The empty audio lane accurately shows that narration has not been placed. No waveform or voice playback is fabricated.

Small defects caught in actual previews: a source-library row conflicted with the ruler, and the final ruler tick wrapped. Library spacing/type and ruler label geometry were corrected and retested in Chromium. The missing-source text equivalent clarifies that a cached timeline thumbnail is not proof the source is available.

## Audio

Exact saved approved Minimal Tech Ambient master and tonal select/place/finish WAVs were checksum-verified and reused. Music gain -9dB, SFX 0dB (the approved Quality V2 mix, not the older +4dB mix). Ducking 5dB, 60ms attack, 30ms hold, 220ms release; original intro and 1.8s raised-cosine outro. Music HP70Hz/LP1800Hz matches the approved first-video chain. No new sound synthesis, white-noise effects, harsh prior SFX or narration. Video is stream-copied during muxing.

Numeric results and hashes are recorded in `out/quality-v2/phase5h-validation.json`. Objective clipping/decoding/continuity/correlation checks are not subjective human listening approval.

## Source and tools added

- `src/quality-v2/SeriesWorkspace.tsx`, `lesson113-series.tsx`
- `content/quality-v2/series.json`
- `scripts/render_phase5h.mjs`, `phase5h_audio.py`, `extract_phase5h_frames.py`, `verify_phase5h.py`
- `scripts/prepare_phase5h_plan.py`, `prepare_phase5h_integration.py`, `test_phase5h.py`
- `content/quality-v2/lesson-113-readonly-snapshot.json`
- `content/quality-v2/lesson-113-sync-proposal.json`
- `content/quality-v2/lesson-113-video-integration.json`
- Three `*.transcript.ru.md` and three `*.equivalent.ru.txt` text alternatives
- Root project doc `docs/courses/lesson-113-quality-v2-integration-plan.md`

Generated previews, final MP4s, stems, frame PNGs, source-freeze/hash records and QA evidence stay under `out/quality-v2/`. Old previews from before this phase's library-layout correction remain in `phase5h-prelayout-fix/`; none are production deliverables.

## Reviews and browser evidence

Native `frontend_reviewer`, `security_reviewer` and `browser_qa` ran read-only. Frontend review inspected all 13 actual new scene frames and both transition sheets with no blockers. Security review inspected the existing upload/metadata/storage/grant rules and identified the batch-import gap described below. Browser QA used actual Node Chromium because Firefox MCP was not connected; no browser/dependency installation.

Studio checks verified import-before-placement, boundary identity at seven seconds, project-list/reopen sequence, missing-source recovery, library/ruler clearance, nonwrapping ticks, no workspace overflow or failed images. No console/page/HTTP failures; Studio event-stream abort on navigation is recorded separately. Evidence: `out/quality-v2/phase5h-browser/` including `report.json`, `ratio-report.json`, `focused-report.json`, `ruler-report.json`, screenshots. Actual rendered frames and before/after cut sheets: `phase5h-frames-preview/` and `phase5h-frames-final/`.

Browser sampling and muted media playback do not establish listening quality or real CapCut behavior. No authenticated protected-player/upload test was performed; no course or student record was changed for QA.

## Text and integration proposal

See the exact root integration doc and machine-readable proposal. Ten paragraph-level changes clarify the silent/schematic demonstrations, add watch cues at the ends of sections 3/5/7, place follow-up practice in 4/6/8, explain save-before-reopen and conditional source recovery, and shorten repeated definitions. Full before/after is provided. All three objectives, all nine headings/order, core definitions, rights information, fictional F1 case and optional/ungraded practice remain.

The existing create-only Module 5 importer is not a content updater. Its source checksum and existing-record guards must not be bypassed. Current `import_lesson_media` rejects video/VTT. Existing authorized Studio upload accepts the validated videos, but three uploads are not one atomic DB/filesystem operation. The next approved integration task needs a narrowly scoped idempotent orchestrator or explicitly reviewed staged uploads, fresh verified DB/media backups, conflict checks and targeted rollback. No schema migration is needed. Video transcripts use concise visual equivalents; no false spoken VTT is created.

Stop here for author review of new exports and explicit approval of the text/update/upload plan.

## Local playback

```sh
ffplay -autoexit out/quality-v2/m5-l13-v1-source-organization-quality-v2.mp4
ffplay -autoexit out/quality-v2/m5-l13-v2-project-import-quality-v2.mp4
ffplay -autoexit out/quality-v2/m5-l13-v3-timeline-reopen-quality-v2.mp4
```

## Final measured results

| Video | Duration / frames | Integrated LUFS | True peak dBTP | Clipped samples |
|---|---|---|---|---|
| 1 | 46s / 1380 | -30.63 | -17.13 | 0 |
| 2 | 47s / 1410 | -30.69 | -17.30 | 0 |
| 3 | 54s / 1620 | -30.58 | -17.62 | 0 |

All three: 1920×1080, 30fps, H.264/yuv420p, AAC-LC stereo 48kHz. Complete FFmpeg decode passed. Compressed video packet/timing and every decoded video-frame hash match each corresponding visual source. SFX residual correlations exceed 0.9999 at exact frame cues. Music remains continuous outside intended fades. First 44.2s of each new filtered music stem exactly match the approved first-video filtered stem. This is preservation/correctness evidence, not new subjective listening approval.

Validation completed: isolated ESLint/TypeScript `npm run lint`; five Python source/proposal regression tests; all three real backend MP4 profile validations (without Django setup or a database connection); new source/doc whitespace and `git diff --check`. Preservation baseline verifies all 641 existing files unchanged. Separate read-only recheck matches the entire SQLite file hash and exact Lesson 113 snapshot, zero attachments, three objectives, nine sections and unpublished course state. Evidence: `phase5h-database-preservation.json`, `phase5h-source-tests.log`, `phase5h-video-validator.json`, `phase5h-lint-final.log`. No full application test rerun was necessary for this isolated production-only change.

Final Chromium file playback: all three report their expected dimensions/duration; muted playback advances and beginning/middle/end seeks decode (readyState 4, error null). Nine final screenshots and `phase5h-browser/final-playback-report.json` retained. Two native file requests aborted on page navigation, with no console/page/media errors. An initial event-based seek timeout was replaced by decoded-ready polling and all samples then passed. No authenticated protected-player test or subjective listening is claimed.
