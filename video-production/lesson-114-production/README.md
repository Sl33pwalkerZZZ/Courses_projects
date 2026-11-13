# Lesson 114 — Quality V2 production (Phase5J)

Three original schematic instructional videos, using the approved Lesson113 QualityV2 design/audio system. No database, course, frontend, Django, existing source or lesson113 asset changes; no upload/publication/commit/push.

## Deliverables

- `out/final/m5-l14-v1-rough-cut-quality-v2.mp4` —54s.
- `out/final/m5-l14-v2-narration-balance-quality-v2.mp4` —60s.
- `out/final/m5-l14-v3-caption-review-quality-v2.mp4` —60s.

Matching lower-resolution playable previews: `out/previews/<same filenames>`.

Finals:1920×1080/30fps,H.264/yuv420p,AAC-LC stereo48kHz. Visual-only intermediates are internal mux inputs, not additional instructional deliverables. Interrupted preflight drafts are retained in named `out/qa/*draft/` directories and are not final previews.

## Reused architecture

No dependency installation. `node_modules` links to the existing pinned Lesson113 toolchain. `package.json` records the same versions for reproducibility. Shared tokens and font-loader are imported from Lesson113 source without modifying it; local fonts and their notices were copied to this isolated public directory. Repaired select/place/finish effects and the approved MinimalTechAmbient master are checksum-verified and read from Lesson113. The new shared `src/Workspace.tsx` implements only the added educational diagrams, not a new visual style or duplicate full project.

Studio: use existing Node (NVM if needed), then `npm run studio -- --port=3118 --no-open`; open http://localhost:3118/RoughCutQualityV2 (or NarrationBalanceQualityV2/CaptionReviewQualityV2). Studio's composition preview shows the visual layout; the final FFmpeg mix is the authoritative audio. No lesson113 composition is rendered by this entry.

## Production commands

```sh
python3 -B scripts/audio.py
npm run lint
npm run render:previews
python3 -B scripts/frames.py
# Inspect21 scene frames and transition sheets; record source-matching out/qa/frame-review.json.
npm run render:finals
python3 -B scripts/verify.py
python3 -B scripts/frames.py --final
python3 -B scripts/manifest.py
python3 -B scripts/test_production.py
```

Scripts refuse to overwrite exports/stems. Use a clean separate output directory or retain/archive your own drafts before reproducing; never overwrite an approved export. Preview scale0.5, CRF21; finals CRF18; bundled Remotion browser,4 workers, sequential video jobs. Final audio mux copies video unchanged, AAC320k/stereo48k,faststart.

## Audio design and fair comparisons

QualityV2 defaults: music-9dB, tonal effects0dB, approved70HzHP/1800HzLP,5dB brief SFX ducking,60ms attack/30ms hold/220ms release, original intro and1.8s raised-cosine outro. The composition/theme is unchanged; no new music, harsh old effects or neural model were generated/downloaded.

Video5 intentionally includes a voice-only pass (music muted), an over-loud background example A and lower background B. Both A/B use identical speech and identical music excerpt, with only music gain differing by14dB(+5 versus-9). The music excerpt has short crossfades outside the spoken phrase; the voice is never cut or renormalized between passes. These values are illustrative settings, not universal delivery standards. Voice clip gain is calculated once and peak-bounded; the exact gain is in the per-video audioJSON.

Video6 lowers the bed during the actual speech snippets to make word checking possible. Native course-reader voice playback, student progress and permissions are not involved here.

## Speech provenance

The8.5625s original approved Module4 synthetic speech is reused exactly, voice ru_roman, Silero `v5_cis_base_nostress`, MIT `LICENSE_CIS`. Source SHA256 `1229c8d93c90674780a25f41eb872cb45b7882fcd281005204d2392856b034dc`; exact script and120 real RMS-waveform bins in `content/speech.json`. Full model provenance and notice in `LICENSE-SILERO.txt`. No v5_ru/v5_cis_ext, ElevenLabs or eSpeak audio is used. Original source assets remain untouched.

## Instructional accuracy

Temporal recording trim/split/remove/close is clearly separate from still-image duration/reordering. The selected middle fragment has an explicit label plus contrasting styling. Closed gaps are manual in the schematic; no universal ripple-delete behavior or version-specific button location is claimed. Voice waveforms derive from actual PCM, not fabricated decorative bars. Subtitles use real sample timings and an explicitly constructed missing-negation error; no actual ASR run is claimed. SRT shows comma timestamps; WebVTT shows dots/header and actual `-->` separators. Renaming is not conversion.

`INTEGRATION-PLAN.md` and `content/lesson114-sync-proposal.json` provide exact proposed text edits and section3/5/7 anchors. Three visual equivalents are supplied. Two optional VTT files caption genuinely audible examples only; they do not invent spoken instruction.

## Verification evidence

`out/qa/validation.json`, lint/tests logs, source-freeze records, frame samples/contact sheets, browser reports and screenshots. Native read-only frontend_reviewer and browser_qa ran. Browser QA uses separately labelled existing Node Chromium because MCP Firefox is absent; no installation. It tests Studio diagrams and generated files, not authenticated LMS upload/playback. Objective AV metrics do not constitute author listening approval. Author review remains required before integration.

## Final verified results

| Video | Duration / frames | Integrated LUFS | True peak dBTP | Clipped samples |
|---|---|---|---|---|
| 4 | 54s / 1620 | -30.50 | -17.08 | 0 |
| 5 | 60s / 1800 | -20.23 | -1.20 | 0 |
| 6 | 60s / 1800 | -25.02 | -2.88 | 0 |

All final files pass full FFmpeg decode; compressed video packet/timestamp and every decoded frame match the corresponding visual source after audio mux. All intended tonal cues correlate with the mixed outputs at their exact action times. Identical voice samples and identical musical excerpts (apart from14dB gain) are verified across A/B. Six production regression tests and Remotion ESLint/TypeScript pass. Existing course validators accept all three real MP4s and both genuine VTT files without a database connection. Git/new-source whitespace checks pass. All943 baselined existing files, including SQLite/canonical source/settings/Lesson113 source+videos/protected media, remain unchanged.

The initial192kbps AAC version of the speech-heavy comparison exceeded the original absolute error threshold. The threshold was not relaxed: audio-only320kbps encoding improved its measured PCM-reference SNR from33.52to45.22dB and passed. All finals/previews now use320kbps; video streams and PCM mixes were unchanged. Old192kbps versions are retained in `out/qa/aac192-before-final-validation/`. Two caption-edit cues were aligned to actual visible changes at28/30.5s before delivery; their earlier unapproved audio is retained separately. This is objective technical evidence, not subjective author approval of the sound.

Final browser QA: all21 Studio scenes plus focused corrections passed geometry checks; three encoding-locked MP4s played and sought atbeginning/middle/end, expected1920×1080 and54/60/60s, readyState4/errornull, hashes unchanged. Actual Node Chromium fallback was used because MCP Firefox is absent. Only expected navigation-aborted media/event requests were recorded, no console/page/media errors. Muted automated playback is not full human listening or protected LMS integration. Screenshots/reports are under `out/qa/browser/`; all21 actual preview/final scene samples and transition sheets are under `out/qa/frames-*`.

The figures show selected exercise fragments, not a change to a saved45-second whole-course F1 edit. Author viewing/listening and explicit lesson-text/media integration approval remain the next steps. No database, lesson source, upload or publication change was performed.
