# Lesson 113 — Phase 5G final audio mixes

The author approved `out/audio-preview/m5-l13-v1-music-approval-v1.mp4` as the
music, sound-design and balance reference. This pass applies that configuration
to all three complete videos. It does not invoke Remotion, change its source,
regenerate music or overwrite an approved input.

## Files

| Video | Unmodified input | New mixed output | Duration / frames |
| --- | --- | --- | --- |
| 1 — Source organization | `out/final/m5-l13-v1-source-organization.mp4` | `out/final-mixed/m5-l13-v1-source-organization.mp4` | 46 s / 1380 |
| 2 — Project setup and import | `out/final/m5-l13-v2-project-import.mp4` | `out/final-mixed/m5-l13-v2-project-import.mp4` | 47 s / 1410 |
| 3 — Timeline and reopening | `out/final/m5-l13-v3-timeline-reopen.mp4` | `out/final-mixed/m5-l13-v3-timeline-reopen.mp4` | 54 s / 1620 |

All outputs retain 1920×1080, 30 FPS, H.264/yuv420p video with the **entire original
video bitstream copied**. Audio is 48 kHz stereo AAC, target 192 kbit/s. MP4 faststart
places `moov` before `mdat` for browser loading. Exact codec/bitrate, hashes and
stream durations are in `out/final-mixed/validation.json`.

## Approved audio configuration

- Source: `out/audio-preview/minimal-tech-ambient-v1-theme-64s.wav`, the exact
  approved 48 kHz stereo 24-bit master, verified against its provenance checksum.
- Music gain **−9 dB**; existing SFX fixed gain **+4 dB**.
- Existing cue-frame schedule controls the same **8 dB** musical dip, with
  60 ms attack, 30 ms hold after each cue, and 220 ms release.
- The master already contains the approved 1.2-second intro fade. The reused
  preview envelope adds the same 1.8-second outro fade at each complete video end.
- No compressor, limiter, automatic normalization, time stretching, synthesized
  replacement score or extra effects. The original click, whoosh, pop, drop and
  completion sounds remain in their original source tracks and at their original times.
- Each duration is shorter than the master's original fade (which starts at 62 s).
  The master is trimmed, so there is **no looping or loop seam**. The 35 existing
  cue events across the three files are preserved.

`mix_final_audio.py` imports `read_stereo`, `preview_stem` and `write_wav` from the
approved preview implementation. It does not replace or modify that implementation.
For Video 1, its music stem is sample-identical to the approved preview's first
18.1 seconds; only the excerpt's early outro is replaced by continuation of the
same approved master.

## Reproduce and verify

From `video-production/lesson-113-production/`:

```sh
python3 -B scripts/mix_final_audio.py --video all
python3 -B scripts/verify_final_audio.py --video all
```

Mixing refuses existing outputs; it never silently overwrites a prior mix. The
verification command may be rerun against existing outputs. Individual jobs use
`--video source-organization`, `--video project-import` or `--video timeline-reopen`.

For future Module 5 videos, add their source filename/id to `content/videos.json`
and corresponding frame cues to `content/sfx-cues.json`, place the original MP4 in
`out/final/`, and run:

```sh
python3 -B scripts/mix_final_audio.py --video VIDEO_ID
python3 -B scripts/verify_final_audio.py --video VIDEO_ID
```

The generic mixing path preserves input dimensions and frame count; the current
series verification assumes its established 30 FPS. A future video longer than
62 seconds is deliberately refused: first prepare an approved longer master or
musically seamless loop, rather than silently truncating/fading out the soundtrack.
No such extension is needed for these three videos.

The recorded per-video `*-mix.json` files contain the exact executed FFmpeg commands,
source/master/output SHA-256 values, cue schedules and approved gain settings.
The filter is the approved source gain plus music gain and unnormalized summation:

```text
[0:a:0]atrim=duration=SECONDS,asetpts=PTS-STARTPTS,volume=-0dB,volume=4dB[sfx];
[1:a:0]volume=-9dB[music];
[sfx][music]amix=inputs=2:duration=shortest:normalize=0[mix]
```

Video mapping uses `-map 0:v:0 -c:v copy`; only `[mix]` is encoded with
`-c:a aac -b:a 192k -ar 48000 -ac 2`. There is no global `-t`, `-shortest` or frame
cap that could drop/reorder the final copied video packets. The 16–19 ms source
AAC padding is trimmed to the actual picture duration; no intended SFX are removed.

## Playback

```sh
ffplay -autoexit out/final-mixed/m5-l13-v1-source-organization.mp4
ffplay -autoexit out/final-mixed/m5-l13-v2-project-import.mp4
ffplay -autoexit out/final-mixed/m5-l13-v3-timeline-reopen.mp4
```

## Validation and limits

The validator compares every compressed video packet including presentation/decode
timestamps, and every decoded video frame against its corresponding complete input.
It fully decodes each MP4, verifies frame count/FPS and aligned A/V starts/durations,
checks music continuity and fade endpoints, measures beginning/middle/end regions,
and subtracts the known music stem to correlate every original SFX cue at its
exact scheduled time. LUFS/true-peak measurements are analysis only; saved mixes
are not loudness-normalized. Zero clipping and absence of abrupt musical sample
steps are checked independently of mean volume.

Numeric checks establish preservation and synchronization; they do not claim that
the author has listened to every full-length mix. The approved interface remains
schematic, not actual CapCut footage. These files are not attached to Lesson 113;
a later authorized upload/integration check in the protected course player is separate.

No Django, SQLite, local settings, course content, enrollments, certificates,
frontend application, original MP4s or approved reference assets are changed.
No dependency installation, commit, push, publication or deployment.

## Final measured results

| Video | Integrated LUFS | True peak dBTP | Mean dBFS | Clipped samples | Identical decoded frames | Minimum SFX correlation |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| source-organization | -30.44 | -13.67 | -32.67 | 0 | 1380 | 0.99219 |
| project-import | -30.66 | -13.19 | -32.86 | 0 | 1410 | 0.97128 |
| timeline-reopen | -30.59 | -13.73 | -32.85 | 0 | 1620 | 0.99527 |

All three have exact matching A/V stream durations and starts. All compressed
video packet hashes/timestamps and all 4,410 decoded pictures are identical.
Music is present through each intended body, with smooth measured fade endpoints.
All 35 cue-window checks pass; SFX exceed musical RMS in those windows by at least
2.66 dB. Residual correlations reflect lossy AAC audio encoding, not video changes.
Beginning/middle/end regional measurements and sample-step checks passed.

## Actual browser verification

Native `browser_qa` ran independently. Playwright MCP connected, but its Firefox
executable was missing; no browser was installed. Actual tests used the existing
Chromium 157.0.8103.15 through Node Playwright, directly opening the mixed MP4s.
Each file decoded at 1920×1080, advanced during playback, sought to beginning,
middle and end, resumed after seeking, and reached `ended=true` at 46/47/54 s.
No console, page, request or media errors were observed.

Evidence: `out/final-mixed/browser-qa/playback-results.json` and nine screenshots.
The tests were muted and sampled, not continuous human viewing/listening.
Headless dropped-frame counters were 33/32/28 during sampled playback/seeking;
full FFmpeg decoding and exact picture comparisons passed. These VM/browser
performance observations are not evidence of corrupted output. Firefox playback
and the application protected-player upload flow remain untested in this pass.

## Preservation and changed files

New source files only: `scripts/mix_final_audio.py`, `scripts/verify_final_audio.py`,
and this document. Generated files are isolated under `out/final-mixed/`, with
one generation log at `out/final-audio-mix.log`. No approved preview file was edited.

514 baseline files were rehashed: application/SQLite, approved reference assets,
Remotion source and the three original finals are unchanged. Source syntax,
existing-output overwrite refusal and `git diff --check` passed. Git staging is
empty. See `out/final-mixed/preservation.json`.

No technical blocker was found for these three local files. Full-length author
listening and a later explicitly authorized protected-player upload are separate
next steps. No media has been attached, published or deployed.
