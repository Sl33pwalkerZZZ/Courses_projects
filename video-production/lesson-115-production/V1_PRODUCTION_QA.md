# Lesson 115 V1 — Production QA

**Status:** full-quality technical master rendered and validated; not attached to a lesson and not human-approved for publication.
**Checked:** 2026-11-09
**Video:** `m5-l15-v1-export-check`
**Course 10:** remains unpublished; database and canonical lesson content were not changed.

## Outputs

- Full-quality MP4: `out/final-sentence/m5-l15-v1-export-check.mp4`
- Pre-mux visual render: `out/final-sentence/m5-l15-v1-export-check-visual.mp4`
- Half-scale review preview: `out/previews-v3/m5-l15-v1-export-check-preview.mp4`
- Audio mix: `out/audio-sentence/m5-l15-v1-export-check-mix.wav`
- Russian WebVTT: `out/final-sentence/m5-l15-v1-export-check.vtt`
- Spoken-text transcript: `out/final-sentence/m5-l15-v1-export-check.ru.md`
- Full-render scene contact sheet: `out/qa/v1-final-scenes-contact.png`
- Source preview review contact sheet: `out/qa/v1-preview-layout-v3-frames-contact.png`
- Render logs and input hashes: `out/qa/m5-l15-v1-export-check-*` and `out/qa/frame-review.json`

The earlier incomplete layout-v2 log and previous preview attempts were preserved. No V2 or V3 final renders were started.

## Visual QA

Reviewed settled frames from all six scenes plus scene transitions in the half-scale preview, then extracted one full-resolution frame from each scene in the final MP4. The diagrams are visible and legible at the intended 1920×1080 composition size. Text, cards, scene headings and bottom captions remained within the frame in the inspected samples. The flow, file-name, container/codec, export, player-check and metadata diagrams all render. The repeated disclosure labels these as explanatory interface illustrations, not CapCut footage or measured program output.

No clipping, missing illustration, alignment defect or subtitle overlap was found in the inspected representative frames. The final scene contact sheet is a QA aid and is not an instructional deliverable.

## Audio QA

- Narration: 17 separately generated sentence cues using the documented local Silero CIS Base `ru_roman` workflow; provenance is recorded in `content/narration-sentence-cues-provenance.json` and `audio/LICENSE_CIS`.
- Mix: 48 kHz, stereo, PCM 16-bit WAV; procedural UI sound effects are retained; no continuous music is present, as required for this provisional Lesson 115 mix.
- WAV duration: 94.533333 s; mean sample level −29.9 dBFS; sample peak −6.3 dBFS.
- Final AAC: stereo, 48 kHz; integrated loudness −25.5 LUFS; true peak −6.3 dBFS. No clipping was detected.
- The streams begin at 0 and have matching 94.533 s duration. `ffmpeg -xerror` decoded the complete MP4 without errors.
- Silence detection finds pauses between spoken cues, the 0.56 s opening lead-in and the 1.10 s end pad. These are part of the sentence/scene layout; there is no music bed. They should still be heard in an author listening review.

Automated checks cannot approve voice naturalness. A person has not reviewed the generated narration in this QA pass, so no human listening approval is claimed.

## Subtitle QA

The UTF-8 WebVTT starts with `WEBVTT` and contains 17 ordered cues. Each cue's text and millisecond start/end match the corresponding generated sentence segment recorded in `content/audio-sentence-mix-provenance.json`; cues do not overlap. The last cue ends at 93.431 s, before the 94.533 s media end. This is sentence-segment synchronization, not phoneme-level forced alignment.

## Technical verification

| Check | Result |
|---|---|
| Preview render | PASS — 960×540 H.264, 30 fps, 2,836 frames, 94.533 s |
| Full render | PASS — 1920×1080, H.264/yuv420p, 30/1 fps, 2,836 frames |
| Audio stream | PASS — AAC stereo, 48 kHz, starts at 0, duration 94.533 s |
| Complete media decode | PASS — FFmpeg `-xerror` |
| Frame preservation | PASS — decoded `framemd5` sequence is identical before and after audio mux |
| Subtitle validation | PASS — all 17 cues match generated sentence boundaries and stay within duration |
| Content validation | PASS — `python3 -B scripts/test_content.py` |
| Lint/typecheck | PASS — `npm run lint` |
| Production bundle | PASS — Remotion bundle written to `/tmp/ai-courses-l115-v1-bundle-check` |

SHA-256:

```text
Final MP4:       9c9b6dadb755734a8e23f8d5579651e68b4b7dc6e3962659f877e756cd9f3653
Visual render:   afa63058e2058afd4d61ea06e027b7bb804e06020b32b5ba727d7bcd1fff209b
WebVTT:          f21a0c05a5de5b080b4abb53ae1358ae140ec640c4b9a1ae84bb5b242ea3a613
Mixed WAV:       f9898896d779d1983c2380ca811b36124725a6afb8d4d449cb9315e36712eb83
Decoded frames:  e53e6cfa40ccc115ae340ce5e31f12829f9ea4cae6c4c5527a78a56044e475ac (both pre-mux and final MP4)
```

## Remaining review and V2/V3 readiness

- V1 is technically rendered and verified. Human listening and author approval remain outstanding. Do not treat this report as permission to attach or publish the video.
- V2 and V3 have six-scene compositions, scripts, sentence audio, timings and WebVTT source files in the shared project. The corrected layout and renderer are reusable, so both are ready to begin isolated preview renders. They have not been visually reviewed and must not proceed directly to full-quality render or integration.
- No V2/V3 final renders were started. No course database, attachment, manifest, canonical lesson text, Course 8 data, Course 10 publication state or unrelated production output was changed.

Playback for human review:

```bash
ffplay -autoexit video-production/lesson-115-production/out/final-sentence/m5-l15-v1-export-check.mp4
```

## Background-music candidate — technical QA addendum

**Checked:** 2026-11-09. This is a new local listening candidate; the original no-music V1 master above is unchanged. No candidate has human listening approval, course attachment, or publication approval.

### Music source and rights

- Track: **Minimal Tech Ambient — original AI Courses theme**. Creator: AI Courses project, procedurally synthesized. There is no external source URL because no third-party recording, sample, pretrained model, or music API was used.
- Reproducible source: `video-production/lesson-113-production/scripts/prepare_music_preview.py`. The approved 64-second source was copied byte-for-byte to `audio/music/minimal-tech-ambient-v1-theme-64s.wav`; both SHA-256 values are `bb3a3d45fc3820a18a087c2791de0139c7cc3459456749071a3ed4ac7ebbb489`.
- The existing score and synthesis method were continued at native tempo for the full video durations. No looping, time-stretching, compression, or limiting was used. Rights note and full provenance are in `content/audio-bgm-provenance.json`; prior owner approval covers the AI Courses video series, while broader sublicensing is not asserted.

### Mixing and outputs

- New candidate: `out/final-sentence/m5-l15-v1-bgm-candidate.mp4` (SHA-256 `22a00b5d27549f993ef9c1c2d8205fbdf6ba28cbbe76e68ad547dcf0f4ae059f`). The original `out/final-sentence/m5-l15-v1-export-check.mp4` remains unchanged.
- Reproducible mixer: `scripts/mix_background_music.py`; focused regression tests: `scripts/test_background_music.py` (4 passed). The music reference is 22 dB below median active narration before ducking, with a smooth 6 dB maximum duck, 200 ms attack and 1 s release. Music was synthesized with 1.2 s in and 2 s out raised-cosine fades.
- Music gain was set separately per video to preserve the same measured narration/music relationship: V1 −29.18 dB, V2 −29.15 dB, V3 −28.62 dB. Median music-to-voice level during speech after ducking: V1 −27.76 dB, V2 −27.78 dB, V3 −27.74 dB. The per-20 ms extremes include quiet cue edges and duck-envelope transitions; automated measurements do not establish subjective intelligibility.
- Original narration and all synchronized UI effects are the unchanged foreground WAV input. Subtracting each PCM24 music bed from its PCM24 mix reproduces that foreground within `0.000000119` full-scale (quantization error). SFX event timing is therefore unchanged.
- Full-duration PCM24 stereo/48 kHz BGM and mix stems are prepared for V1, V2 and V3 under `out/audio-bgm/`. No V2/V3 MP4 was rendered or muxed.
- Candidate FFprobe: H.264/yuv420p, 1920×1080, 30 fps, 2,836 frames, 94.533333 s; AAC stereo 48 kHz, 94.533000 s. Full `ffmpeg -xerror` decode passed. EBU R128 measured integrated loudness −25.5 LUFS and true peak −6.3 dBTP (below the requested −1 dBTP ceiling). The original no-music mix measured −25.5 LUFS / −6.3 dBTP, so adding this subtle bed did not raise the measured programme loudness or peak.
- All 2,836 decoded video-frame MD5 hashes match the original V1 master exactly. The unchanged original MP4 SHA-256 is `9c9b6dadb755734a8e23f8d5579651e68b4b7dc6e3962659f877e756cd9f3653`. The unchanged V1 WebVTT SHA-256 is `f21a0c05a5de5b080b4abb53ae1358ae140ec640c4b9a1ae84bb5b242ea3a613`; its timing was not edited.

### Listening and next review

```bash
ffplay -autoexit video-production/lesson-115-production/out/final-sentence/m5-l15-v1-bgm-candidate.mp4
```

For the music bed alone:

```bash
ffplay -autoexit video-production/lesson-115-production/out/audio-bgm/m5-l15-v1-export-check-music.wav
```

Technical checks pass. The remaining gate is human listening and author approval of narration clarity, music level, and transitions. Do not attach this candidate or publish Course 10 on the basis of automated QA.
