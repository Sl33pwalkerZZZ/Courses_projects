# Module 5 — Project files / motion-design prototype

**Style test only. One composition, three connected scenes, exactly 12 seconds.**
No course integration, CapCut footage, voiceover, music, external images or database access.
The two MP4s are resolution variants of the same sample, not separate instructional videos.

## Open Studio

From the repository root:

```sh
export PATH="$HOME/.nvm/versions/node/v24.21.0/bin:$PATH"  # if Node is not already on PATH
cd video-production/module-5-style-test
npm run dev -- --port=3105
```

Open **http://localhost:3105/Module5StyleTest**. Space plays/pauses; click the
current timecode to enter an exact frame. Only `Module5StyleTest` is registered.
The project has its own `package.json`, lockfile and dependencies. For another
machine, run `npm ci` **in this directory**, never in the main frontend.
Remotion installs its own rendering browser on first render.

## Outputs

All paths below are relative to this directory:

- `out/module-5-style-preview-960x540.mp4` — playable low-resolution preview.
- `out/module-5-style-1920x1080.mp4` — full-resolution H.264/yuv420p MP4.
- `out/qa/preview-frame-01.png` … `preview-frame-07.png` — inspected preview frames.
- `out/qa/studio-frame-72.png`, `studio-frame-174.png`, `studio-frame-320.png` — Studio screenshots.
- `out/qa/studio-checks.json` — actual Chromium preview checks and DOM/font metrics.
- `out/verification.json` — ffprobe metadata, checksums and complete decode results.
- `out/qa/full-frame-01.png` … `full-frame-03.png` — inspected full-resolution scene frames.
- `out/qa/native-playback.json` — native Chromium MP4 playback check.
- `out/dependency-audit.json` — recorded npm dependency-audit findings.

Both encodes: 30 FPS, 360 frames, 12.000 seconds, deliberately no audio stream.
Generated outputs, caches and dependencies are ignored by this directory's `.gitignore`.

```sh
npm run lint            # official Remotion ESLint rules + TypeScript
npm run render:preview  # 960×540, CRF 20; inspect before rendering full resolution
npm run render:full     # 1920×1080, CRF 18
npm run verify          # installed system ffprobe/ffmpeg: metadata + full decode
```

Render concurrency is limited to one to respect the VM's memory budget. No
`--browser-executable` override is used for rendering; Remotion's bundled browser
renders both encodes. Existing Chromium is used separately for Studio QA only.

## Design and timing

| Time | Scene | Motion |
| --- | --- | --- |
| 0–3.4 s | От идеи к видеопроекту | Masked kinetic type and a spatial F1 project folder |
| 3.4–7.8 s | Организуем материалы | Four folders settle into a precise horizontal structure |
| 7.8–12 s | Готово к монтажу | The same folders unfold into four editing tracks and a playhead |

The F1 project and filenames are fictional teaching illustrations. The persistent
caption **«Иллюстрация интерфейса · не запись CapCut»** makes that explicit. The
waveform is an original schematic drawing, not an analysis of real narration.
There are no product screenshots, fabricated project results or downloaded stock assets.

## Editing the prototype

- **Colors and layout:** `src/tokens.ts` owns graphite, warm white, lavender,
  mint, blue, sand and the safe-area token. The layout uses 128px side margins.
- **Typography:** local Noto Sans Regular/Bold, loaded by `src/fonts.ts` using
  `@remotion/fonts`. Change local files, weights and `design.font` together.
  Headline sizes and tracking are editable inline on `RevealLine` instances.
- **Animation speed:** `timing.entrance` changes title entrance speed;
  `organizeStart/End` and `transformStart/End` tune the illustration. Scene
  boundaries are intentionally explicit on the three `Sequence` nodes in
  `Composition.tsx`. If changing those boundaries, coordinate title exit and
  ruler/playhead keyframes as well. There is no misleading single global speed knob.
  Keep `Root.tsx` at 360 frames unless intentionally creating a different duration.
- **Scene content:** edit `Opening`, `Organize`, `Ready` and the four authored
  `FolderToTrack` instances in `src/Composition.tsx`. Headings and filenames
  are not hardcoded to database lesson IDs.
- **Future narration/captions:** the illustration and text scenes have independent
  timing layers. Add a separately timed narration/caption track at the marked
  integration point after approving the audio; preserve its actual timing.
  This prototype includes neither a caption engine nor fabricated caption cues.
  Keep instructional captions concise and outside the persistent UI labels.

All animation derives from `useCurrentFrame()`, `useVideoConfig()` and clamped
`interpolate()` keyframes. No CSS animation, timers, random layout, hover or
network-dependent typography controls a rendered frame. The first preview
inspection led to earlier filename fading during the morph and a foreground
playhead so the final line remains continuous.

## Provenance and limitations

- Interface illustrations, typography choreography and diagrams: original code
  authored for this prototype; no CapCut assets or third-party recordings.
- Fonts: Noto Sans from the existing local system, **SIL OFL 1.1**. Full notice
  and distribution copyright are preserved in `public/fonts/NOTO-LICENSE.txt`.
- Remotion packages: pinned to **4.0.540** with a lockfile. Remotion's applicable
  software license is separate from the font license; confirm organizational
  licensing before adopting a production rendering service.
- The official scaffold installation reported **11 moderate dependency audit
  findings**. No automatic fixes or unrelated upgrades were applied. This is an
  isolated local preview toolchain, not a deployed server; review the findings
  before production automation.
- Playwright MCP Firefox was unavailable (missing browser executable). Studio
  was checked using the already installed Chromium QA environment instead.
- An independent native `frontend_reviewer` inspected source isolation/timing
  and found no confirmed blocker; final rendered-frame review was done by the
  main agent. No claim of review of the production student website is made.

Nothing is attached to lesson 113 or course 10. No application files, existing
media, course content, SQLite, migrations or local settings are changed. No
commit, push, deployment or publication is part of this style test.

## Verification record

- ESLint + TypeScript: PASS. Standalone Remotion bundle: PASS.
- Low-resolution preview was rendered and inspected before full-resolution output.
- Both MP4s: exactly 360 frames / 30 FPS / 12.000 seconds, H.264/yuv420p,
  no audio; complete FFmpeg decoding passed.
- Live Studio: seven selected frame positions, local-font loading, four animated
  folder elements, persistent illustration label and play/pause passed;
  no page errors, console errors or failed requests.
- Seven preview frames plus three full-resolution scene frames were inspected.
  Native `frontend_reviewer` also inspected title/folder/morph/timeline stills;
  no remaining clipping or legibility blocker was found.
- The full render log records all 360 frames encoded and the final output file.
  Its execution wrapper subsequently reported SIGTERM/143 rather than normal
  termination. The completed artifact was independently verified by metadata
  and full decode; no missing/corrupt frames were detected.
- Initial Node subprocess verification hit the sandbox's `EPERM` restriction;
  the same check passed when rerun outside that restriction. No verifier was
  weakened or dependency changed to hide that failure.
- Native MP4 startup/playback was checked separately. Optional seeking through
  the temporary Python output server was **not verified**: it returned 200 with
  no Content-Range for a Range request, and seeking reset/stalled in the harness.
  This is not a claim of a passing seek test. No protected-media server was changed.
- Existing tracked application files and SQLite matched their start-of-task
  SHA-256 hashes. Git HEAD and the index were unchanged.
