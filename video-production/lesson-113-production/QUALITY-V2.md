# Lesson 113 — audio repair and instructional clarity, approval version 2

Scope: only Video 1 is revised/rendered. Existing compositions, all old MP4s,
original audio, main website, Django, SQLite and lesson content are preserved.
New render entry: `src/quality-v2/index.tsx`. All generated outputs are isolated
under `out/quality-v2/`. No commit, upload or publication.

## Audio diagnosis — findings versus uncertainty

The original generator explicitly mixes white noise into its 1400 Hz click,
filtered random noise into its drop/whoosh, and introduces the completion cue's
880 Hz second note without an independent slow attack. These are intentional
procedural transients/textures, not proof of corrupted decoding. The click has a
3 ms attack. High-pass RMS analysis above 4 kHz relative to total RMS measured:

| Original source | Above-4-kHz relative RMS | Maximum adjacent same-channel sample step |
| --- | ---: | ---: |
| click | −9.48 dB | 0.229710 |
| whoosh | −7.53 dB | 0.124188 |
| drop | −14.51 dB | 0.064328 |
| music master | −43.32 dB | 0.013676 |

The noisy effects are plausible contributors to the reported crackly/harsh sound.
The exact subjective glitch is **not conclusively localized** without the author's
listening comparison. No aliasing, sample-rate mismatch or clipping is established
as the root cause; native-rate delivery is 48 kHz. Music has far less high-frequency
energy than the affected effects. Absence of clipping is not used as a cleanliness
verdict. Measurements for original stems and all three SFX-only/final-mixed videos
are saved in `out/quality-v2/audio-diagnosis.json`.

Isolated 20-second listening samples: `original-sfx-listening-20s.wav`,
`original-music-listening-20s.wav`, `original-mix-listening-20s.wav` under that folder.
They retain their source levels; they are identification samples, not a falsely
loudness-matched preference test.

## Audio repairs

- Keep the exact approved original ambient master, its harmony/melody and tempo.
  Gently band-limit it with 70 Hz high-pass / 1800 Hz low-pass filters and a
  smooth 1.8-second ending fade. The existing intro fade is retained.
- Replace noisy click/drop/whoosh material with original warm, harmonically
  related sine tones. No random noise, inharmonic metallic partials or pitch sweep.
  New attacks are 12–35 ms with raised-cosine ramps and 70 ms tails.
- Remove the five repeated transition whooshes, decorative opening pop, and
  click on a static rights checklist. Eleven old cues become four purposeful
  cues: folder focus, copy naming, selected voice version and final next-step cue.
- Mix lossless music/SFX stems before one AAC encoding; do not recycle the old
  already-AAC effects track. This avoids an extra lossy effects generation.
- Music remains −9 dB. New effect samples have deliberately comfortable fixed
  source levels; SFX mix gain is independently adjustable, default 0 dB. Brief
  musical dips are 5 dB, with 60 ms attack / 220 ms release. No master volume
  reduction, compressor, limiter, neural processing or automatic normalization.
- Cleanliness/comfort still needs human listening approval; the report does not
  claim that metrics prove the subjective problem is completely solved.

## Editorial review of every existing scene

Native `frontend_reviewer` reviewed all 19 scenes against the lesson source and
storyboards. Initial findings are source-based; actual revised-frame review is
recorded separately. Unchanged Videos 2/3 are proposals only, not implemented.

| Video / scene | Learner must understand | Main object/action | Necessary explanation | Remove/simplify |
| --- | --- | --- | --- | --- |
| 1 brief | Prepare selected fictional-example materials | One F1 working folder | Fictional case, no measured savings | Tiny repeated provenance labels and changing decorative cards |
| 1 folders | Each material has a home | Same five-folder workspace | Structure is an example, not a CapCut requirement | Floating folders and background geometry |
| 1 copies | Preserve originals and name working copies | Original pair plus named copies in sources | Inspect contents, not only extensions | Mere sideways entrance with no original/copy distinction |
| 1 rights | Unknown conditions mean exclusion | Same named file plus provenance template | Author, source, distribution terms | Disconnected checklist and click on static text |
| 1 approved | Select the correct voice and captions | Named voice version versus experiment | Retain transcript/provenance/rights, check SRT | Generic rows replacing the important object |
| 1 ready | Verify preparation before importing | Same root/workspace and notes checklist | Brief/plan/rights in notes; exclude unconfirmed sources | Premature reopening claim and material→project→export slogan |
| 2 create | Create an identifiable ordinary project | Named project card | Actual controls vary by version | Oversized F1 and repeated project name |
| 2 workspace | Distinguish three functions | Library, preview, timeline | Select / inspect / set time | Already-populated timeline in a supposedly new project |
| 2 import | Import is not assembly | Prepared file into library | Wait and inspect before editing | Preview appearing before deliberate selection |
| 2 ratio | Select the intended canvas | Same sheet in 16:9 | 9:16 separately; ratio ≠ pixels | Competing pixel examples |
| 2 entities | Source/project/export differ | Three persistent concrete objects | MP4 cannot replace editable project | Generic text-only metaphor cards |
| 2 place | Library/clip/preview must correspond | Same sheet in all three | Playhead inside first clip | Blank clip that cannot prove material identity |
| 3 arrange | Follow the five-scene plan | Five identifiable ordered clips | Picture/audio/text can have separate tracks | Dominant fictitious waveform and duplicate number/legend |
| 3 trim | Clip edge controls duration | First clip edge 5→7s | Seven seconds is exercise guidance | Unexplained temporary gap and unrelated waveform |
| 3 cut | Check the actual picture at a boundary | Playhead with corresponding preview | Check gaps/overlap/blank output | Timeline-only proof of image continuity |
| 3 zoom | Scale is not speed | Same clips and ruler zoom together | Duration stays unchanged | Simultaneously moving playhead |
| 3 reopen | Verify editable project after reopening | Same named project and sequence | Normal workflow in installed version | Checklist replacing the actual reopen demonstration |
| 3 links | Recover a missing source | Same file and clip; visible break/recovery | Locate correct source, verify picture | Unbroken line merely changing color |
| 3 finish | Verify continued editability | Reopened sequence and accessible files | MP4 ≠ project; retain originals/backup | Reused preparation checklist/slogan |

## Revised Video 1

The six scenes remain **46 seconds**. Stable workspace coordinates, folder names,
file identities and typography replace the changing abstract panels. A persistent
schematic/fictional label prevents any claim of genuine CapCut recording.

- No arrows, connector lines, camera drift, decorative grid/circle/diagonals,
  cursor trails/rings, floating cards or sliding text. Borders only delineate the UI.
- Titles make a short opacity change rather than traveling. Folder focus and
  selected files change emphasis only when relevant to the explanation.
- Originals stay explicitly separate from working copies. The same paper filename
  remains visible in the rights check. Filename “approved” is explicitly not proof
  of permission. The provenance panel is a template, not a fabricated license.
- Voice version selection introduces a named audio object; caption timing and
  rights checks are retained. Example filenames are labeled as examples.
- The final checklist stops at **before import**; it no longer claims saved or
  reopened project availability. No checked boxes imply real permission approval.
- Instructions remain fully understandable with audio muted. No graded assessment,
  source DOCX/content rewrite or database change is involved.

## Reproduction

From `video-production/lesson-113-production/` (existing toolchain only):

```sh
python3 -B scripts/quality_v2_audio.py diagnose
python3 -B scripts/quality_v2_audio.py prepare
npm run lint
node_modules/.bin/remotion studio src/quality-v2/index.tsx --port=3115
node_modules/.bin/remotion render src/quality-v2/index.tsx SourceOrganizationQualityV2 out/quality-v2/video-1-visual-preview.mp4 --codec=h264 --scale=0.5 --crf=21 --concurrency=4
# Inspect all six scenes and transitions before the full-resolution approval export.
node_modules/.bin/remotion render src/quality-v2/index.tsx SourceOrganizationQualityV2 out/quality-v2/video-1-visual-1080p.mp4 --codec=h264 --crf=18 --concurrency=4
python3 -B scripts/quality_v2_audio.py mix
```

Outputs refuse overwrite in the audio helper. Independent gains are available as
`mix --music-db -9 --sfx-db 0`. Keep any future revision in another versioned
folder rather than replacing previous approval assets. Video 2/3 renders must
wait for author approval of this single revised Video 1.

## Final technical results

- Approval video: `out/quality-v2/m5-l13-v1-source-organization-quality-v2.mp4`.
- Audio-only comparison: `out/quality-v2/m5-l13-v1-quality-v2-audio.wav`.
- H.264/yuv420p, 1920×1080, 30 FPS, 1,380 frames, 46 seconds.
- AAC stereo, 48 kHz; A/V starts and durations match. Full decode passed.
- Loudness: -30.63 LUFS; true peak -17.13 dBTP; clipped samples: 0.
- All four intended cues match their new frame schedule; minimum residual
  correlation 0.99993.
- Full new visual packet/timestamp identity is verified after audio muxing; old
  visual identity is intentionally different in this single revised Video 1.
- Quiet endpoints, continuous musical body and same-channel sample-step checks
  passed. Primary instruction/title/note reading rates are 1.76–2.44 words/s;
  contextual panel labels are static, not flashing text.
- New select/place/finish above-4-kHz relative RMS: −35.73 / −46.79 / −38.27 dB.
  New maximum waveform steps: 0.00698 / 0.00480 / 0.00555, versus original
  click/drop/whoosh 0.22971 / 0.06433 / 0.12419. Source levels differ; relative
  spectral measures establish a texture change independently of master gain.
- A validation failure caught the default linear outro curve. Only the new
  audio was remixed with the original smoother raised-cosine/`hsin` curve;
  no second visual render was needed for that correction. The unapproved
  intermediate is retained in `out/quality-v2/intermediate-linear-fade/`.

## Before / after

| Before | Revised approval version |
| --- | --- |
| Noisy click/drop/whoosh, 11 cue events | Warm tonal cues with slower ramps, 4 relevant events |
| Changing scene-specific panels and connectors | One fixed five-folder workspace |
| Cards enter without clear copy/original distinction | Working copies and separately retained originals are labeled |
| Rights checklist loses important object identity | Same named paper file and explicit provenance template |
| Ready panel claims reopening before import | Unchecked preparation list; project not yet created |
| Text slides, moving backdrop/cursor rings | Static readable text and limited focus changes |

All six actual low-resolution scene frames and transition pairs were inspected
before the full render. Final 1080p frames verify the header spacing, opaque
copy labels and clarified experiment wording. The initial low-resolution preview
is intermediate evidence, not the final approval file. See `final-frames/`.

## Repaired audio listening

```sh
ffplay -autoexit out/quality-v2/m5-l13-v1-source-organization-quality-v2.mp4
ffplay -autoexit out/quality-v2/m5-l13-v1-quality-v2-audio.wav
# To isolate the originally reported texture:
ffplay -autoexit out/quality-v2/original-sfx-listening-20s.wav
ffplay -autoexit out/quality-v2/original-music-listening-20s.wav
```

## Verification and preservation notes

Remotion ESLint/TypeScript, deterministic synthesis, bounded peaks/smooth sample
ends and `git diff --check` passed. `scripts/verify_quality_v2.py` reproduces the
file/audio/safety checks; detailed evidence is `out/quality-v2/validation.json`.

The executor restarted during rendering and its temporary `/tmp` baseline was
unavailable. A persistent recovery checkpoint is stored with this version.
All original video/audio assets independently match their existing approval/mix
manifest hashes, and 562 protected files match the persistent checkpoint.
Only the named new files were authored; no original production source was edited.
Videos 2/3, the main app, SQLite and intentional local settings are untouched.

Subjective sound quality still requires the author's approval. This version is
an instructional diagram, not a real CapCut screen recording. Do not propagate
the style/audio changes to other videos before review.

## Independent review and actual browser result

Native `frontend_reviewer` reviewed all 19 original scenes against source material,
then all six revised preview frames and transitions. The final header spacing,
opaque copy labels and unambiguous experiment caption address its final comments.
Native `browser_qa` ran explicit **Node Chromium** checks. MCP tools were exposed
but configured Firefox was absent; no browser or other dependency was installed.

Final Studio samples at 15/19/34 seconds passed source-hash guards and visible
text bounds checks. Zero-area style metadata in raw readings is not visible overflow.
The final MP4 played and sought at beginning/middle/end (about 1.08/23.48/44.96s),
decoding at 1920×1080 with duration 46s. No console, page or media errors occurred.
One seek-canceled request and one headless dropped frame were recorded; playback
continued. The file hash stayed unchanged. Evidence: `browser-qa/mp4-report.json`
and three screenshots. Automation was muted and sampled, not human full-length
listening or a protected-course-player test.

New source files: `src/quality-v2/index.tsx`, `src/quality-v2/QualityVideo.tsx`,
`content/quality-v2/video-1.json`, `scripts/quality_v2_audio.py`,
`scripts/verify_quality_v2.py`, and `QUALITY-V2.md`. Existing original composition
registrations, visuals, audio generators and final mixes are not modified.
