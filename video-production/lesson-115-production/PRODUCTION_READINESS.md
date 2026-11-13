# Lesson 115 — Production Readiness

**Checked:** 2026-11-09. This is a read-only environment and asset audit. No media was rendered, recorded, generated, installed, moved or attached. No database or canonical lesson content was accessed or changed.

## Overall decision

**NOT READY for genuine CapCut screen recording.** The current VM has a usable Remotion/FFmpeg toolchain for explanatory graphics and post-production, but CapCut Desktop was not detected, and no actual F1 CapCut project or source video footage is present in the relevant project directories. The operator must supply a CapCut-capable recording environment and an authorized demonstration project before production can begin. Remotion-only graphics work could begin after the F1 assets and script are approved, but cannot substitute for the three required real application demonstrations.

The provisional audio decision is **voice narration plus only appropriate, approved effects; no continuous background soundtrack**. Do not loop or stretch the existing short music master.

## 1. Host and tool inventory

| Finding | Status | Evidence / production implication |
|---|---|---|
| OS | **CONFIRMED** | LMDE 7 (“gigi”), Debian 13 base, x86_64. |
| Compute | **CONFIRMED** | 8 virtual CPUs reported; Intel Core i5-12450H under KVM virtualization. No `/dev/dri` GPU device was present. Remotion can use the existing CPU toolchain, but GPU acceleration is not available through this VM. |
| Memory | **CONFIRMED** | 7.8 GiB total RAM, about 3.1 GiB available at inspection; 8.1 GiB swap with about 7.3 GiB free. For future renders, start with low/sequential concurrency and monitor memory. |
| Disk | **CONFIRMED** | Project filesystem: 41 GiB total, 21 GiB used, 19 GiB available at inspection. Raw capture/project sizes have not been estimated; check space again before recording. |
| Desktop session | **CONFIRMED** | `DISPLAY=:0`, X11 session. `gnome-screenshot` exists, but it is a still-image tool, not the requested video recorder. |
| CapCut Desktop | **UNKNOWN / NOT DETECTED** | No `capcut` executable, Debian package, Flatpak app, launcher entry, or match in checked common application locations was found. This bounded inspection cannot exclude a manually installed app in an unsearched custom location. The actual version/build and interface language are unknown. Treat actual CapCut capture as blocked until the operator verifies a usable installation. |
| OBS Studio | **UNKNOWN / NOT DETECTED** | No `obs`/`obs-studio` executable, Debian package, Flatpak app, or launcher was found. A different capture method has not been selected or validated. |
| FFmpeg / FFprobe | **CONFIRMED** | `/usr/bin/ffmpeg` and `/usr/bin/ffprobe`, version 7.1.5. Useful for media inspection, decoding, validation and later muxing; their presence does not provide CapCut footage. |
| Node.js / npm | **CONFIRMED, PATH SETUP NEEDED** | Existing NVM Node v24.21.0 and npm 11.19.0 are available at `/home/almas/.nvm/versions/node/v24.21.0/bin/`; neither `node` nor `npm` is on the current shell `PATH`. Use the existing NVM installation; do not install replacements. |
| Remotion | **CONFIRMED, GRAPHICS TOOLCHAIN PRESENT** | Existing projects pin Remotion 4.0.540. The Lesson 113 CLI runs when the existing NVM bin directory is temporarily added to `PATH`. Lesson 113 has its local dependencies (about 1.2 GiB); Lesson 114 links to them; the 12-second Module 5 style-test package also has local dependencies (about 713 MiB). The Lesson 115 folder is planning documents only and has no package, composition or render command. |
| Capture device / capture software | **UNKNOWN** | No screen-recording workflow was verified. Do not assume OBS or a specific recorder. |

**INFERRED:** Remotion graphics rendering may be feasible with this CPU toolchain, but the modest currently available RAM and absent GPU favor a low-concurrency preview-first workflow. Actual Lesson 115 render speed/stability and raw-recording storage needs have not been tested.

To use the existing Node/npm in a future shell without changing project files:

```sh
export PATH="/home/almas/.nvm/versions/node/v24.21.0/bin:$PATH"
node --version
npm --version
```

Existing Remotion commands (not run for this audit):

- Lesson 113: from `video-production/lesson-113-production/`, `npm run dev`, `npm run render:previews`, `npm run render:finals`, `npm run lint`, `npm run verify`.
- Lesson 114: from `video-production/lesson-114-production/`, `npm run studio -- --port=3118`, `npm run render:previews`, `npm run render:finals`, `npm run lint`.
- Style prototype only: from `video-production/module-5-style-test/`, `npm run render:preview` or `npm run render:full`.

These are prior-project commands, not a ready Lesson 115 renderer. The existing L13/L14 compositions are explanatory schematic content; neither creates a recording of CapCut. No render was attempted, and cached-browser readiness was not checked.

## 2. Existing relevant assets

File sizes below are the on-disk sizes at inspection. “Documented” describes what project records say; it is not a new rights determination or permission to reuse an item for Lesson 115.

| Exact path | Type / size | Stage and provenance | Potential Lesson 115 use / limitation |
|---|---:|---|---|
| `course_assets/module_5/m5-l13-v1-production/originals/f1-notepad-diagram.svg` | SVG, 790 B | Original code-drawn fictional F1 illustration. L13 README/provenance records its origin; author review/permission for distribution is still pending in its checklist. | Candidate for a clearly labeled Remotion diagram in V2; not footage and not a CapCut screenshot. Reuse only after approval. |
| `course_assets/module_5/m5-l13-v1-production/originals/f1-paper-diagram.svg` | SVG, 783 B | Same status: original code-drawn fictional illustration; review pending. | Candidate for V1/V2 explanatory graphics after approval; not source video. |
| `course_assets/module_5/m5-l13-v1-production/F1_video/notes/brief.md` | Markdown, 355 B | Fictional F1 brief. | Content reference only. It does not define an actual CapCut project or source footage. |
| `course_assets/module_5/m5-l13-v1-production/F1_video/notes/permission-checklist.csv` | CSV, 528 B | Documented as a blank review template, not an executed permission record. | Could support V3 as a visibly blank/checklist example. Never show it as proof that rights were cleared. |
| `course_assets/module_5/m5-l13-v1-production/narration-preview.wav` | WAV, 2,842,244 B (~59.2 s per its README) | Silero `v5_cis_base_nostress`, `ru_roman`, CPU/24 kHz/mono PCM16; exact model/license provenance is recorded. Explicitly an unapproved L13 draft, not final narration. | Voice-process reference only. It is not the L15 script and must not be reused as its narration. |
| `course_assets/module_5/m5-l13-v1-production/narration-script-ru.txt` | UTF-8 text, 1,585 B | L13 script; associated with the draft preview. | Not an L15 script. L15 drafts live separately in this production package and still need author approval. |
| `course_assets/module_5/m5-l13-v1-production/LICENSE_CIS` | Text, 1,076 B | Silero MIT notice retained for the L13 model workflow. | License reference only; any L15 voice use still needs script/voice approval and matching provenance. |
| `course_assets/module_4/voice_candidates/ru_roman_refined/ru-roman-variant-b-clear-pauses.wav` | WAV, 924,644 B | Author-selected/approved as the Lesson 10 candidate in the earlier audio task; Silero CIS Base MIT provenance is documented in the Module 4 records. | A possible voice/style reference, **not approved for Lesson 115**. Obtain approval for the new script and intended reuse before generation. |
| `video-production/lesson-114-production/public/f1-speech.wav` | WAV, 411,044 B | 8.56-second Silero `ru_roman` sample; transcript/model/checkpoint/license are recorded in `content/speech.json` and `LICENSE-SILERO.txt`. Used as a short illustrative speech sample for Lesson 114. | Not a full L15 narration. Do not present it as L15 speech. |
| `video-production/lesson-113-production/public/fonts/NotoSans-Regular.ttf` | TTF, 512,672 B | Local font copy with `public/fonts/NOTO-LICENSE.txt` (SIL OFL). | Available for Remotion graphics; copy with its license only in a later authorized production step. Also present in L14's local font directory. |
| `video-production/lesson-113-production/public/fonts/NotoSans-Bold.ttf` | TTF, 515,752 B | Same documented OFL font family. | Available for Remotion graphics, subject to preserving the notice. |
| `video-production/lesson-113-production/public/sfx/click.wav`, `whoosh.wav`, `pop.wav`, `drop.wav`, `complete.wav` | WAV, respectively 7,244; 40,364; 17,324; 13,484; 62,444 B | Original reproducible procedural PCM effects; method, checksums and no-third-party-sample origin are recorded in `content/sfx-provenance.json`. Used in L13 production. | Potential subtle effects for V1–V3 if each cue fits and the author approves reuse. They are not sounds recorded from CapCut. |
| `video-production/lesson-113-production/out/audio-preview/minimal-tech-ambient-v1-theme-64s.wav` | WAV, 18,432,102 B (~64 s by filename/production records) | Original procedural music master with provenance JSON. | **Do not use as a continuous bed**: too short for 115–120 s and no loop/stretch is authorized. Provisional plan is no continuous music. |
| `video-production/lesson-113-production/out/final-mixed/m5-l13-v1-source-organization.mp4`, `m5-l13-v2-project-import.mp4`, `m5-l13-v3-timeline-reopen.mp4` | H.264/AAC MP4 finals, respectively 2,939,164; 2,702,726; 3,480,665 B | Final L13 deliverables; provenance and validation records exist. L13 README explicitly describes them as text-led schematics without CapCut screen capture. | Visual/pacing references only. Not source footage or evidence of actual CapCut operations. |
| `video-production/lesson-114-production/out/final/m5-l14-v1-rough-cut-quality-v2.mp4`, `m5-l14-v2-narration-balance-quality-v2.mp4`, `m5-l14-v3-caption-review-quality-v2.mp4` | H.264/AAC MP4 finals, respectively 2,963,101; 3,405,390; 3,317,093 B | Final L14 Remotion-based instructional assets with audio/subtitle provenance and validation docs. | Production/style references only, not an L15 CapCut project or source video. |

### Reusable Remotion source

| Exact path | Type / size | Stage and provenance | L15 use |
|---|---:|---|---|
| `video-production/lesson-113-production/src/Root.tsx` | TSX, 1,147 B | Local composition registration; documented in the L13 package README. | Reference for registering future explanatory compositions for V1–V3. |
| `video-production/lesson-113-production/src/Tutorial.tsx` | TSX, 3,880 B | Local scene sequencing/timing and audio cue integration. | Reference for restrained, frame-driven explanatory inserts in V1–V3; not app capture. |
| `video-production/lesson-113-production/src/primitives.tsx` | TSX, 8,479 B | Local reusable Remotion typography/panel/step primitives, documented in README. | Candidate shared primitives for all three. |
| `video-production/lesson-113-production/src/visuals.tsx` | TSX, 22,684 B | Local original F1 folder/workspace/timeline diagrams, documented in README/provenance. | Candidate original graphics for V1–V3 after checking the particular graphic's factual relevance; never mimic CapCut UI. |
| `video-production/lesson-113-production/src/tokens.ts` and `src/fonts.ts` | TS, 495 B and 356 B | Local visual tokens and font loading; README records the series style. | Shared style/font setup for V1–V3. Preserve the font license notice listed above. |
| `video-production/lesson-114-production/src/Workspace.tsx` and `src/index.tsx` | TSX, 21,597 B and 790 B | Local original diagrams/composition registration. L14 README documents its relationship to L13 components and audio pipeline. | Additional diagram reference for V1–V3 only where conceptually appropriate; not a substitute for real app footage. |
| `video-production/module-5-style-test/src/Composition.tsx` | TSX, 17,251 B | Original 12-second style-test source, package/readme documents the test purpose. | Style reference only; not a Lesson 115 composition or screen recording. |

Six existing Module 3 PNGs are present under `course_assets/module_3/`: `m3-l1-prompt-anatomy.png` (56,617 B), `m3-l1-prompt-comparison.png` (51,663 B), `m3-l2-layout-hierarchy.png` (59,805 B), `m3-l2-process-infographic.png` (48,131 B), `m3-l3-export-check.png` (43,082 B), and `m3-l3-style-guide.png` (49,008 B). The asset manifest describes them as original instructor-created diagrams, but also says creator/date/font/permission evidence is required before distribution; its top-level “planning only” status conflicts with the files already being present. **No Module 3 image is assigned to an L15 video.** Do not treat them as cleared L15 assets without resolving provenance and confirming relevance.

### Sources that are not available

- **CONFIRMED within inspected project paths:** `course_assets/module_5/` contains no MP4/MOV/WebM source footage and no video asset beyond the separate Lesson 113/114 Remotion output directories. Its Lesson 13 F1 package contains the diagrams, documentation and narration preview above, not a CapCut timeline or recorded footage.
- **CONFIRMED within inspected production paths:** no CapCut-native project file or raw screen recording was found for Lesson 115. The Lesson 113 and 114 MP4s are prior Remotion deliverables; they must not be repurposed as genuine CapCut footage.
- **UNKNOWN:** whether the author has an approved CapCut project or footage outside these project directories. This audit intentionally did not search unrelated personal folders.
- **CONFIRMED:** no Lesson 115 narration audio or WebVTT exists in the Lesson 115 package. Only draft scripts/storyboards exist.

## 3. Per-video readiness

Planned master/attachment locations follow `ASSET_REQUIREMENTS.md`: masters should be reviewed under `video-production/lesson-115-production/out/final/`; approved course assets are later named under `course_assets/module_5/`. Do not create either output yet. All storyboard durations are targets, not measured durations.

| Video | Ready dependencies | Missing dependencies / human action | Real capture and Remotion needs | Audio / target outputs | Readiness |
|---|---|---|---|---|---|
| **V1 — `m5-l15-v1-export-check`** (after Lesson 115 section 3; 120 s target) | Russian script/storyboard; FFmpeg/FFprobe for later inspection; existing Remotion 4.0.540 sources/fonts for a separate container-vs-codec explainer. | CapCut Desktop plus confirmed version/OS/UI language; an isolated, reopenable horizontal F1 CapCut project and permission-cleared input media; author approval of narration and actual voice method. No export can be shown until a genuine export is made in that app. | Screen-record the actual timeline, real export settings/completion, resulting file in a player and real `ffprobe` output. Remotion can create an opening/title and a separate measured/neutral codec diagram; it cannot fake the export panel or progress. | No music bed. Approved narration and optionally approved existing procedural SFX. Target master `video-production/lesson-115-production/out/final/m5-l15-v1-export-check.mp4`; later asset `course_assets/module_5/m5-l15-v1-export-check.mp4` plus VTT timed to final narration. | **BLOCKED for capture; graphics tooling available.** |
| **V2 — `m5-l15-v2-vertical-adaptation`** (after section 5; 115 s target) | Script/storyboard; original F1 SVG illustrations as possible graphics after rights review; Noto Sans/OFL and Remotion packages. | CapCut Desktop/version confirmation; actual saved 16:9 project and cleared visual source assets; verify the installed build supports the demonstrated project-copy and 9:16 workflow; approve script/voice. Do not narrate or depict a control before it is observed. | Record the real copy, aspect-ratio, manual reframing, text placement and actual output. Remotion can show a separately labeled 16:9/9:16 crop guide using cleared original artwork; never recreate CapCut UI. | No music bed. Approved voice/SFX only. Target master `video-production/lesson-115-production/out/final/m5-l15-v2-vertical-adaptation.mp4`; later asset with matching `.vtt` at `course_assets/module_5/`. | **BLOCKED for capture; required feature availability UNKNOWN.** |
| **V3 — `m5-l15-v3-final-review`** (after section 7; 115 s target) | Script/storyboard; Remotion can make the clearly fictional unsupported-claim teaching card; FFprobe is available for actual metadata checks; a blank rights-checklist template exists. | CapCut Desktop/project and an actual candidate export; documented rights/provenance for each input; real review results (not prefilled checkmarks); approve script/voice. Blank template is not evidence that media is cleared. | Record actual output playback and checks, actual source/rights records with private data removed, and real subtitle/hand-off steps. Remotion may show the fictional counterexample and a neutral checklist, clearly separated from evidence. | No music bed. Approved voice/SFX only. Target master `video-production/lesson-115-production/out/final/m5-l15-v3-final-review.mp4`; later asset with matching `.vtt` at `course_assets/module_5/`. | **BLOCKED for capture and rights evidence; explanatory graphics tooling available.** |

## 4. Exact blockers and recommended sequence

1. **Provide a real CapCut recording environment.** Confirm that CapCut Desktop is installed on the machine to be recorded, and record its exact version/build, OS and UI language. This VM did not expose a detected CapCut installation. Also select and test an approved video capture tool; OBS is not detected here. Do not stage the real capture on a different UI and present it as this VM's interface.
2. **Prepare the isolated F1 project.** Supply or build a separate project in the real application, with original/permission-cleared media, a saved horizontal edit for V1/V2, and a candidate export for V3. Preserve source files and the native project plus linked media. Do not use an empty rights template as clearance.
3. **Review the L15 scripts and voice.** Get author approval for all three scripts and choose either an authorized human voice or an explicitly approved Silero reuse/new generation. The existing Lesson 10 voice candidate is not automatically approved for L15. Record transcript, voice/model, license and attribution. Do not use the L13 preview as L15 narration.
4. **Keep audio voice-first.** Apply the requested no-continuous-music default. Select only appropriate effects from the documented original procedural SFX after review; do not capture or claim they are CapCut sounds. The 64-second music master is not suitable for these longer clips without a separately approved new plan.
5. **Make graphics only after asset review.** Reuse the L13 Remotion conventions and Noto Sans/OFL notice. Confirm rights/relevance for F1 SVGs and any Module 3 images. Graphics must remain visibly separate from authentic interface evidence.
6. **Record short previews before full videos.** Capture genuine operations, redact private paths/account data without hiding relevant warnings, preserve raw captures, then approve a cut. Generate WebVTT only from final spoken audio and final video timing. Validate MP4 profile, decode, audio/video duration, subtitle bounds, hashes and human playback before any later import task.

**Conclusion:** the repository is ready for planning and limited Remotion asset work, but **not ready to start actual Lesson 115 CapCut recording**. CapCut installation/version, authentic demo project/source visuals, capture method, script/voice approval and rights evidence are the gating inputs. Course 10 and its lesson/media records were not inspected or modified in this readiness audit; no publication action occurred.
