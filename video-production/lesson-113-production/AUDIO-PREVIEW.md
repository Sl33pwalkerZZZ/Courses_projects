# Lesson 113 — Minimal Tech Ambient approval preview

This pass adds audio only. The three approved final videos and Remotion animation
source are unchanged. No website, Django, database or course attachment changes.

## Listen

The **single approval preview** is the first **19.9 seconds / 597 frames** of Video 1:

`out/audio-preview/m5-l13-v1-music-approval-v1.mp4`

```sh
ffplay -autoexit out/audio-preview/m5-l13-v1-music-approval-v1.mp4
```

Run from `video-production/lesson-113-production/`, or open the MP4 in a desktop
player. The excerpt contains the opening, folder organization and source-copy
illustrations, including five original SFX cues.

Standalone original theme:
`out/audio-preview/minimal-tech-ambient-v1-theme-64s.wav`

Prepared excerpt stem (faded and ducked, **before** the -9 dB mix gain):
`out/audio-preview/minimal-tech-ambient-v1-preview-music-stem.wav`

## Composition and provenance

Original offline Python standard-library synthesis; no downloads, recordings,
paid API, pretrained audio model, music sample pack, vocal or borrowed melody.
48 kHz stereo, 24-bit PCM master, deterministic seed 1132026.

72 BPM; sparse Dmaj9 → Bm7 → Gmaj9 → Aadd9 harmony, two bars per chord.
Soft sine pads have gentle attacks/releases, light detuning and slow amplitude
movement. Short sine bells use a sparse original four-note motif per chord.
Rounded low-mid pulses and very quiet independently filtered noise provide
movement and stereo texture without drums or intrusive sub-bass.

The reusable `compose(seconds)` function extends the score at native tempo;
it does not time-stretch recordings. This 64-second master is an approval theme,
not an instruction to remix the other videos. Future integration remains pending.

## Mix

- Existing stereo AAC effects decoded and preserved with a fixed **+4 dB gain**.
- Music at **-9 dB** relative to the generated stem.
- Music briefly dips by up to 8 dB around the existing cue frames: 60 ms attack,
  30 ms post-cue hold, 220 ms release. SFX timing is unchanged.
- 1.2-second musical fade-in; 1.8-second musical fade-out. No compressor or limiter.
- `amix normalize=0` avoids automatic gain scaling. Only audio is AAC encoded;
  the existing H.264 video stream is copied.
- The initial ordinary `-t 20` copy included a reordered end picture. The final
  597-frame boundary avoids that tail discrepancy; validation compares every
  compressed packet/timestamp and every decoded picture against the original.

## Adjusting balance after listening approval

Implementation: `scripts/prepare_music_preview.py`. Defaults: `--music-db -9`
and `--sfx-db 4`. More negative music values lower the bed; positive SFX values
raise the existing effects. Global music mute is `--music-db -60` (practically
inaudible); no changes to Remotion props are required for this audio-only pass.

Example for a **later requested** quieter alternative, not generated in this task:

```sh
python3 -B scripts/prepare_music_preview.py --music-db -12 --sfx-db 4 --tag quieter
python3 -B scripts/verify_music_preview.py quieter
```

Every tag creates separate outputs and refuses overwrite. Never point this tool
at the approved final filenames. The excerpt is derived from the saved 24-bit master for reproducibility. Music fades, cue ducking and synthesis parameters
are explicit in the source and machine-readable provenance.

## Evidence

- `out/audio-preview/minimal-tech-ambient-v1-provenance.json`: score, seed,
  source/output SHA-256, gains, fades and actual FFmpeg command.
- `out/audio-preview/validation-v1.json`: decode, visual identity, audio measurements,
  SFX residual correlation, fades and continuity checks.
- `out/audio-original-verification.log`: existing three-video SFX verification.

Checks establish file integrity and synchronization, **not human listening
approval**. Listen on ordinary speakers/headphones to judge musical balance,
repetition and distraction. No remix of Videos 2 or 3 has been created.

## Measured approval-preview results

| Check | Result |
| --- | --- |
| Duration / picture count | 19.9 seconds / 597 |
| Visual identity | All 597 packet hashes/timestamps and decoded pictures match the original prefix |
| Mix mean / sample peak | -32.9 dBFS / -14.0 dBFS |
| Integrated loudness / true peak | -30.67 LUFS / -14.01 dBTP |
| Clipped decoded samples | 0 |
| Preserved cue count | 5 |
| Minimum SFX residual correlation | 0.9983 |
| Minimum SFX-over-music RMS within cue windows | 2.65 dB |
| A/V starts and duration | Aligned; both streams 19.9 seconds |

All four saved audio/video assets fully decode. Music continuity and fade endpoints
pass analysis; no unexpected silent gap was detected. The original three finals
were independently checked for existing SFX frame alignment (minimum source-cue
correlation above 0.984). Their SHA-256 values remain unchanged.

Local regression checks passed: deterministic synthesis, stereo, expected sample
count, bounded sample peak, silent starting sample, syntax and overwrite refusal.
No dependencies were installed. Human listening approval is still pending.
