# AI Courses — Media and Production Audit

**Audit date:** 2026-11-09
**Branch:** `design/amethyst-motion`, four commits ahead of `origin/design/amethyst-motion`
**Scope:** Media files, production sources/scripts/manifests, Module 3–5 integration metadata, read-only media metadata and current course attachment references. This report complements `01-technical-inventory.md` and `02-course-content-and-database-audit.md`; it does not repeat the course inventory.

Evidence labels: **CONFIRMED** means directly inspected from a file, the read-only local database, a command’s metadata output, or recorded integration evidence. **INFERRED** means strongly supported by source/documentation but not independently executed end-to-end. **UNKNOWN** means unverified or absent from inspected evidence.

## A. Media inventory and classification

A repository-wide extension scan (excluding `.git`, `node_modules`, virtual environments and Python caches) found **51 MP4, 99 WAV, 3 MP3, 9 SRT, 5 VTT, 911 PNG, 87 SVG, 5 WebP, 2 DOCX and 1 PDF**. These are filesystem counts, not counts of distinct approved course deliverables. They include render outputs, duplicate versions, hidden local backups, screen captures and QA images. The 911 PNGs include 618 `.playwright-mcp/` screenshots and hundreds of production frames/QA images; they must not be mistaken for course illustrations. `.local-course-backups/`, `.local-video-test/`, `.local-cinematic-qa/`, `.playwright-mcp/`, `.agents/`, `frontend/dist/`, and Remotion `build/` contain backup, test, screenshot, skill or build material rather than canonical learner media.

| Asset family | Current learner/course role | Canonical/source locations | Production/output locations and status |
|---|---|---|---|
| Course 10, Module 3 (lessons 106–108) | Six original educational PNG diagrams, two per lesson; protected image records and section-placement metadata exist. | `course_assets/module_3/*.png`; `docs/courses/media-module-3-assets.json`; `courses/management/media_module_3.json`; `courses/management/commands/import_media_module_3_images.py`; `place_media_module_3_images.py`. | Protected copies in `media/lessons/ai-media-content/module-3/`; DB associations and decoded pixel comparisons were verified in Phase 2. Source PNGs are Git tracked. Manifest status still says `awaiting_creation` although files and DB attachments exist: stale. |
| Course 10, Module 4 (lessons 109–111) | Seven approved materials: L10 WAV; L11 WAV + illustrative SRT + synchronized SRT; L12 before/after WAV + workflow PNG. | `course_assets/module_4/` (approved seven); `docs/courses/media-module-4-assets.json`; `docs/courses/module-4-final-provenance.json`; `docs/courses/module-4-silero-final-audio-plan.md`; `course_assets/module_4/LICENSE_CIS`. | Protected copies under `media/lessons/attachments/` and `media/lessons/ai-media-content/module-4/`. Current DB rows’ hashes match protected file bytes and manifest. Canonical seven are tracked. Additional eSpeak/ElevenLabs and experiments are retained locally and are not the current attachment set. |
| Course 10, Module 5 (lessons 113–115) | L13: 3 videos; L14: 3 videos + 2 VTT tracks; L15: no media attached. | `docs/courses/media-module-5-assets.json`; `courses/management/media_module_5.json`; `docs/courses/media-module-5-storyboards.json`; `docs/courses/media-module-5-content-review.md`. | L13 Remotion project: `video-production/lesson-113-production/`; L14 project: `video-production/lesson-114-production/`. Protected live files under ignored `media/lessons/attachments/`. The projects, generated MP4 outputs and integration source files are untracked. L15 files are planned only; no expected MP4/VTT was found. |
| Lesson 113 production source materials | Fictional F1 paper/notepad SVGs, typography, tokens, scene data, transcripts/text equivalents, SFX cues and procedural SFX source. | `video-production/lesson-113-production/src/`, `content/`, `public/`, `scripts/`, `transcripts/`; original diagrams also in `course_assets/module_5/m5-l13-v1-production/originals/`. | `out/final/` contains earlier sound-effects-only base exports; `out/final-mixed/` contains a previous music mix; `out/quality-v2/` contains the three versions actually attached. Previews, visual-only mux inputs, audio stems, extracted frames and validation JSON are retained in `out/`. All `video-production/` files are untracked. |
| Lesson 114 production source materials | Reuses L13 tokens, local font files/license notice, music/SFX; adds a schematic workspace, short spoken examples, text equivalents and two narrow VTT tracks. | `video-production/lesson-114-production/src/`, `content/`, `scripts/`, `public/`, `README.md`. | `out/final/` contains the three attached 54/60/60-second MP4s; `out/previews/`, `out/qa/`, audio stems and visual-only exports are working outputs. All untracked. |
| Prototype | One 12-second Remotion style test, not a course lesson. | `video-production/module-5-style-test/src/`, package files and `README.md`. | `out/module-5-style-preview-960x540.mp4` and `out/module-5-style-1920x1080.mp4`, plus QA frames. Not attached. Untracked. |
| Course source docs and raw source media | Two DOCX sources for Course 8 and Course 10 Module 1. | `course_sources/`. | Source directory is Git-ignored/local; it is not a video-edit project. |
| Frontend and other graphics | SVG iconography, Amethyst/Cinematic illustration assets, site favicon/icons. | `frontend/src/assets/`, `frontend/public/`. | `frontend/dist/` is a generated build copy and should not be treated as a second canonical source. |

**CONFIRMED:** No `.aep`, `.prproj`, `.drp`, `.blend`, `.kdenlive` or CapCut native project files were found in the inspected production folders. The editable Remotion compositions are the actual project sources for L13/L14, not CapCut projects. No actual CapCut screen recordings were found in those deliverables.

## B. Video production infrastructure and tool usage

| Tool | Evidence of actual use | Scope / reproducibility |
|---|---|---|
| Remotion + React/TypeScript | **CONFIRMED:** `package.json`, lockfiles, `remotion.config.ts`, source compositions and generated outputs exist in each of the L13, L14 and style-test packages. L13 `src/Root.tsx` registers `SourceOrganization`, `ProjectImport`, `TimelineReopen`; L14 registers its three quality-v2 compositions. Completion docs identify them as Remotion renders. | Reproducible in principle from untracked sources, pinned package manifests/lockfiles, local fonts, original SVGs and SFX source. Package output/frame gates and dependencies require the isolated package toolchain and Chromium/Remotion browser. All three project trees and outputs are currently untracked. |
| FFmpeg | **CONFIRMED:** L13 scripts call FFmpeg for audio extraction/mixing/mux and full decode checks (`scripts/mix_final_audio.py`, `verify_final_audio.py`, `phase5h_audio.py`, `quality_v2_audio.py`). L14 `scripts/audio.py`/`verify.py` create stems and mux while copying the visual stream. Scripts and docs preserve audio/video separation and use `-c:v copy` for mix passes. | Executable `/usr/bin/ffmpeg` is available. Some scripts generate or overwrite files and were not run in this audit. No transcode/render was performed here. |
| FFprobe | **CONFIRMED:** Used by media validation scripts and by this audit to inspect the six live L13/L14 MP4s and local audio assets. Backend upload validation also invokes ffprobe for profile checks. | `/usr/bin/ffprobe` is available. Read-only metadata inspection only. |
| OBS Studio | **UNKNOWN / no use evidence:** No OBS project, scene profile, recording output or production command was found. `obs` is not on the current shell PATH. | No OBS recording is needed to reproduce the existing schematic Remotion videos. |
| CapCut Desktop | **CONFIRMED not used to create L13/L14 videos:** Videos persistently identify the interface as schematic and not CapCut footage. The curriculum teaches CapCut workflows, but the production compositions simulate generic workflows. No CapCut executable was found on PATH and no native project/screen recording was found. | Real CapCut recording is an outstanding dependency for L15 and any future screen-accurate demonstration. PATH absence alone does not prove the application is absent from the machine. |
| Other editors / renderers | **UNKNOWN:** No evidence of Premiere, DaVinci Resolve, Kdenlive or another native editor project in the inspected production package. | No claim of use. |
| Browser/Chromium | **CONFIRMED by production docs:** Remotion uses its bundled browser for rendering. Existing integration docs report Chromium fixture checks; those are not a substitute for a current live learner session. | No browser process was started for this audit. `node`/`npm` are not available on this shell PATH. |

**CONFIRMED:** The actual L13/L14 composition exports are not filmed CapCut screens. They use original, explicitly labeled schematic UI and written equivalents. This is an intentional provenance distinction, not a missing decoder or attachment fault.

## C. Audio, TTS and subtitle production

### Approved Module 4 deliverables

| Lesson | File | Read-only technical result | Provenance / role |
|---|---|---|---|
| 10 | `course_assets/module_4/m4-l10-silero-ru-roman-approved.wav` | WAV PCM s16le, mono, 24 kHz, 19.2625 s. | Approved `ru-roman-variant-b-clear-pauses.wav` copy; checkpoint `v5_cis_base_nostress`, speaker `ru_roman`. |
| 11 | `m4-l11-silero-ru-roman-approved.wav` | WAV PCM s16le, mono, 24 kHz, 8.5625 s. | Approved Silero speech example; not an interview or actual ASR result. |
| 11 | `m4-l2-f1-example.srt` | Three SRT-shaped cues; intentionally illustrative and not synchronized to the recording. Its final cue exceeds the attached speech duration by design. | Kept to explain SRT syntax; must not be used as the timed caption track. |
| 11 | `m4-l11-silero-ru-roman-synchronized.srt` | Three cues; ordered/non-overlapping; final cue ends at 8.312 s within the 8.5625 s recording. | Synchronized from the approved audio’s generated segment sample boundaries, not old eSpeak timings or ASR. |
| 12 | `m4-l12-silero-ru-roman-before.wav` | WAV PCM s16le, mono, 24 kHz, 8.5625 s. | Same approved speech with reproducible procedurally generated broadband room/ventilation noise; seed and provenance are documented. Not a field recording. |
| 12 | `m4-l12-silero-ru-roman-after-dsp.wav` | WAV PCM s16le, mono, 24 kHz, 8.5625 s. | Author-selected strong V3 conventional spectral DSP filtering; not neural/AI denoising. Uses same aligned speech source. |
| 12 | `m4-l3-audio-workflow.png` | PNG 1600×900. | Original diagram; inline after section 6. |

The exact approved hashes, script/transcript, processing method and MIT notice are recorded in `docs/courses/module-4-final-provenance.json` and `docs/courses/media-module-4-assets.json`; the full notice is `course_assets/module_4/LICENSE_CIS`. Silero official family/model registry links and checkpoint checksum are in `course_assets/module_4/voice_candidates/README.md` and provenance docs. **CONFIRMED:** current course attachments reference the four canonical WAV/SRT assets, not the old ElevenLabs/eSpeak files.

### Production history and candidates

- **CONFIRMED:** Earlier work retained an eSpeak-generated WAV and candidate speech/SRT material for comparison. These are not the production Lesson 10–12 attachments. This runtime has neither `espeak` nor `espeak-ng` on PATH; previous generation scripts/candidate documentation are retained locally.
- **CONFIRMED:** An ElevenLabs Free-plan Lesson 10 MP3 was supplied by the author and its transcript/provenance were documented. Commercial use was explicitly not authorized. It was replaced by the MIT-licensed Silero selection for production; the local source MP3 and an old protected-storage copy remain. They are not referenced by current Lesson 10 attachment rows and should not be redistributed as production audio.
- **CONFIRMED:** Three CIS Base voices were evaluated. `ru_roman` was selected; the exact model was `v5_cis_base_nostress`, under the repository’s `LICENSE_CIS` MIT notice. Refined variants include neutral and clearer-pause delivery; the author-approved Lesson 10 Variant B and Lesson 11 sample were copied into the canonical filenames. Stress marks (`+`) and sentence segmentation are part of reproducible Russian synthesis scripts.
- **CONFIRMED:** Conventional DSP experiments include spectral-profile subtraction/filter variants and an RNNoise investigation. RNNoise/neural denoising was rejected for the final teaching example. The selected final uses procedural synthetic room noise and conventional DSP. The author later requested another self-contained before/after pair under `voice_candidates/lesson12-self-contained-dsp/`; that later pair is a candidate/proposal and is not in the current production manifest or DB. Do not label it approved or substitute it without review.
- **CONFIRMED:** The canonical module 4 manifest excludes eSpeak and ElevenLabs as production selections and records the selected Silero/DSP provenance. Candidate recordings and experiments remain as untracked local files; their presence does not mean approved.

The local TTS scripts (`course_assets/module_4/voice_candidates/prepare_roman_module4.py`, `generate_candidates.py`) require an external checkpoint file and isolated PyTorch runtime. The checkpoint is not stored in Git; local evaluation setup is separate from Django `.venv`. Exact byte reproduction may depend on Python/PyTorch/runtime versions, although checked-in reports document SHA-256 and refuse overwriting existing candidate outputs. The project does not call ElevenLabs or Silero from the student-facing web application; TTS is an offline authoring workflow.

### Lesson 114 spoken samples and VTT

**CONFIRMED:** L14 video 1 is sound-effects-only and has no VTT. Videos 2 and 3 contain short Silero spoken samples, not full lesson narration. Their separately attached WebVTT files contain 9 and 6 cues, respectively, scoped to the speech only; visual instructions remain in the lesson text equivalent. The L14 recording models a deliberately illustrative recognition error; ASR was not executed. Source VTTs are under `video-production/lesson-114-production/content/`; protected copies are attached after sections 5 and 7. The video MP4s do not embed subtitle streams.

## D. Production workflow and reproducibility

**CONFIRMED:** L13 source includes `content/videos.json`, `content/sfx-cues.json`, `content/sfx-provenance.json`, `src/{Root,Tutorial,primitives,visuals,tokens,fonts,types}.tsx`, original F1 SVGs, Noto Sans local font files/license notice, Remotion configuration and scripts. `scripts/prepare_package.py` creates deterministic original SFX and accessible text equivalents. Music is synthesized locally and mixed under existing effects; `mix_final_audio.py` uses FFmpeg. L14 reuses L13’s licensed font/token/music/SFX assets, has its own workspace compositions, speech/audio scripts and subtitle/text-equivalent material.

**CONFIRMED:** Package manifests and `package-lock.json` pin the Remotion toolchain, but all production source trees are untracked; package `node_modules` are local installs/links and are not source. Reproduction requires Node/npm, `npm ci` in the isolated package, the pinned Remotion/React packages and bundled browser, Python for project scripts, and system FFmpeg/FFprobe. These commands were read from documentation only; none were executed. The current shell can run FFmpeg/FFprobe but has no `node`, `npm`, `obs`, `capcut`, or eSpeak command on PATH.

**CONFIRMED:** No raw CapCut project, raw camera footage, or real desktop capture is required to reproduce the present schematic L13/L14 Remotion deliverables. To create genuinely screen-recorded lessons, an author must separately record a real CapCut Desktop version/OS/language, use approved local educational source files, capture narration under recorded permissions, and re-time transcripts/VTT against the final edited audio/video.

## E. Module 3–5 media and manifest consistency

### Module 3 images

| Lesson | Image | Placement |
|---|---|---|
| 106 — image generation | `m3-l1-prompt-anatomy.png`; `m3-l1-prompt-comparison.png` | After sections 3 and 4. |
| 107 — covers/cards/infographics | `m3-l2-layout-hierarchy.png`; `m3-l2-process-infographic.png` | After sections 3 and 6. |
| 108 — consistent visual style | `m3-l3-style-guide.png`; `m3-l3-export-check.png` | After sections 5 and 6. |

**CONFIRMED:** All six files exist; database image associations and placements exist, and Phase 2 verified copied pixels. **CONFIRMED discrepancy:** `docs/courses/media-module-3-assets.json` still marks assets `awaiting_creation` although present and attached. Update only with separate authorization; no manifest was changed in this audit.

### Module 4 media placement

- L109 audio after `4. Учебная демонстрация Ф1: подготовка озвучки`.
- L110 approved speech after section 3; illustrative and synchronized SRT downloads after section 5.
- L111 before/after audio comparison after section 3; original workflow image after section 6.

The seven current Module 4 asset hashes match the live DB media bytes and final manifest. The review confirmed current captions identify Silero `ru_roman`, synthetic noise and conventional DSP accurately. No media was opened/listened to subjectively.

### Lessons 113–115

**Lesson 113 — integrated media:**

| Attachment | Duration | DB/manifest SHA-256 | Inline section |
|---|---:|---|---|
| `m5-l13-v1-source-organization-quality-v2.mp4` | 46 s | `e10e855ab2ad53816f5bbd245b0e5b2f0f3b0a019d9bfff75a7940b5f746aa7f` | 3. Ф1: папки, имена и разрешения на материалы |
| `m5-l13-v2-project-import-quality-v2.mp4` | 47 s | `d17bd4577c2d3a86fcde4338af2bc9f4b4437b80a88ad977dc8ea97916cd638e` | 5. Новый проект и импорт в CapCut Desktop |
| `m5-l13-v3-timeline-reopen-quality-v2.mp4` | 54 s | `a11da7005d5b47781545fa634d603f7b3380c60e50ec4d039936bc103c018084` | 7. Таймлайн и повторное открытие проекта |

The exact current source exports are `video-production/lesson-113-production/out/quality-v2/` (each MP4 hash equals its live attachment and the Module 5 manifest). Each is H.264 1920×1080, 30/1 fps, AAC stereo 48 kHz. FFprobe reports video + audio only; no embedded subtitles. These demonstrate original schematic workflows, not actual CapCut UI. The three files under `out/final/` and three under `out/final-mixed/` are earlier stages/alternate mixes, not current DB copies; preserve them as history until maintainers classify them. `out/previews/`, `out/qa/`, visual-only outputs, stems, frames and logs are intermediate/QA, not attachments.

**Lesson 114 — integrated media:**

| Attachment | Duration | DB/manifest SHA-256 | Inline section |
|---|---:|---|---|
| `m5-l14-v1-rough-cut-quality-v2.mp4` | 54 s | `398bccbc15ee19f4fdb1158809aafedcd1d73fc1354b8f3383633eda54a56bb1` | 3. Черновая сборка и ритм кадров |
| `m5-l14-v2-narration-balance-quality-v2.mp4` | 60 s | `0d4171604271e3c62a122e41590be221a9cdec6b84184e8006a811dca513b8df` | 5. Озвучка, паузы и баланс звука |
| `m5-l14-v2-narration-balance-quality-v2.vtt` | 9 cues | `0f23a05e719d13ae7b4715d8cb78730f772545789fb5117ee0395dd485eb1620` | 5. Озвучка, паузы и баланс звука |
| `m5-l14-v3-caption-review-quality-v2.mp4` | 60 s | `266c7770ac8fe56fa73061a055548e2ba7a0dc7e838e53eec3763560a0342ad2` | 7. Субтитры и ответственное использование ИИ |
| `m5-l14-v3-caption-review-quality-v2.vtt` | 6 cues | `52f8083248c0739db35e7cb2af6c399d385983429da73685aaf01f49e3ac2` | 7. Субтитры и ответственное использование ИИ |

All three live MP4 bytes equal `video-production/lesson-114-production/out/final/` files and manifest/DB hashes. FFprobe reports H.264 1920×1080 at 30 fps plus AAC stereo 48 kHz; the VTT tracks are sidecars, not embedded subtitle streams. A further visual-only version exists for each video and must not be confused with the final audio-bearing attachment. Package documentation reports final decode/sync checks and browser fixture tests; this audit did not rerun those production scripts.

**Lesson 115 — not produced:**

| Planned file pair | Storyboard / section placement | Current status and production dependencies |
|---|---|---|
| `m5-l15-v1-export-check.mp4` + `.vtt` | 120 s planned; after section 3 `Экспорт проверочной версии в CapCut Desktop`. Show local export controls, actual settings, completed exported file, and ffprobe inspection. | **CONFIRMED:** manifest/storyboard `planned_not_created`; zero DB attachments; no matching MP4/VTT in `video-production/lesson-115-production/` or `course_assets/module_5/`. Requires a real horizontal F1 project/export, actual CapCut build and available fields, local ffprobe report, instructor narration with distribution permission, final transcript and time-aligned VTT. |
| `m5-l15-v2-vertical-adaptation.mp4` + `.vtt` | 115 s planned; after section 5 `Адаптация 16:9 в 9:16`. Show preserving horizontal version, separate vertical edit, repositioning and text checks. | Requires the real editable horizontal project and approved source graphics; verify version-supported project duplication/aspect controls, actual vertical re-layout/export, narration permission and VTT retiming. No source project/export currently recorded. |
| `m5-l15-v3-final-review.mp4` + `.vtt` | 115 s planned; after section 7 `Редакторская проверка перед публикацией`. Show technical, factual and rights checks without publishing/upload. | Requires a real final export, source/rights checklist with truthful evidence, safe fictional examples, no personal data, authorized narration, final transcript and timed VTT. No fabricated permission or performance record. |

The storyboard’s durations and times are planned edit timelines, not measured recordings/caption cues. It explicitly requires a real CapCut Desktop screen recording and warns against simulated interfaces. Current production is ready in **educational script/storyboard/placement design**, but not ready to record: a real supported CapCut Desktop environment, exact version/OS/language, source project/materials, author voice/recording permission, capture policy and post-production/review timing remain dependencies. MP4/VTT names in the manifest are placeholders for future assets; no broken attachment rows exist.

## F. Git tracking, duplicates and orphan candidates

**CONFIRMED:** `git ls-files` shows the six Module 3 source PNGs, the seven canonical Module 4 deliverables and applicable license/source files are tracked. The 3 integrated Lesson 113 and 3 Lesson 114 MP4 files are **not Git tracked**; their production project trees and final output paths are untracked. The protected `media/` directory is excluded by `.gitignore`; DB attachments are persistent local media, not reproducible from Git alone. `video-production/` currently contains 643 non-`node_modules` files, all untracked (including source, lockfiles, renders, previews, frame captures, logs and QA). Do not stage the directory wholesale.

**CONFIRMED:** The local filesystem has five files under protected attachment storage without a current reference in either `LessonAttachment.file` or `LessonImage.image`:

- `media/lessons/attachments/30e6525960a84251bf06c522f20a3712/m4-l1-f1-natural-narration.mp3` (old ElevenLabs copy)
- `media/lessons/attachments/b51afacfaebf439b983ab74192bf0f79/m4-l2-f1-speech.wav`
- `media/lessons/attachments/142593a98ee8449a8d14abf0a22d8347/m4-l2-f1-synchronized.srt`
- `media/lessons/attachments/8378478882904b8bb6ce13f3936d3972/m4-l3-f1-original.wav`
- `media/lessons/attachments/7df8fdaac4334942a899100bf64e1fa8/m4-l3-f1-processed.wav`

These may be retained rollback/legacy/candidate copies. Their current lack of a DB reference does not establish that deletion is safe. No deletion or cleanup is recommended without checking backups, provenance and owner intent.

**CONFIRMED:** Module 3/4 canonical source files and approved assets are tracked; Module 4 candidate/evaluation directories contain many untracked alternatives, including the ElevenLabs MP3, old eSpeak recordings, voice samples and DSP experiments. They are not all approved deliverables. Module 5 Lesson 113/114 production sources and outputs are untracked and therefore absent from the four commits ahead of origin unless separately included in the working-tree checkpoint. `course_assets/module_5/m5-l13-v1-production/narration-preview.wav` is explicitly an unapproved local Silero draft (59.2125 s against a planned 110 s video), not part of the integrated L13 videos or production import set. The exact package source and the corresponding current DB attachment hashes do exist locally, but remote reproducibility is not established.

## G. Provenance and licensing

- **Silero:** The final Module 4 voice is CIS Base `v5_cis_base_nostress`, speaker `ru_roman`. The model family exception is MIT under `LICENSE_CIS`; preserve copyright/permission notice and official checkpoint provenance. The checkpoint itself is not in Git and must be obtained from the documented official source/checksum into an isolated environment. The exact spoken scripts are documented in provenance records.
- **ElevenLabs Free:** Author-generated MP3 has confirmed provenance and non-commercial educational approval with attribution, but commercial use is not authorized. It is excluded from current production and must remain excluded from commercial distribution unless independently licensed/replaced.
- **eSpeak:** Historical sample only; not selected for current course audio. Exact version/command and redistribution terms for every local historical recording are not fully documented in the final deliverable set (**UNKNOWN**); do not re-use as approved voice-over without review.
- **DSP and room noise:** Procedurally generated synthetic noise, recorded seed/method and conventional spectral DSP are documented. Captions explicitly say this is not AI denoising. No commercial sound library or third-party field recording is required for the approved pair.
- **Remotion/fonts/SFX:** Original vector diagrams and procedural SFX have source/provenance records. Noto fonts include their OFL notice in production `public/fonts/`. Remotion licensing is a separate consideration from generated course content; the package readme asks maintainers to review it for their intended organizational/commercial production use. This audit is not legal advice or a fresh third-party license review.
- **Lesson 114 narration:** Reuses the already approved Silero speech and MIT attribution. Captions/text equivalents clearly limit what is spoken and label the simulated ASR example.
- **Course source illustrations:** Module 3 PNGs have manifest captions/alt descriptions and source/provenance metadata; original Module 5 diagrams are hand-authored SVG. No arbitrary stock imagery was identified in these specific deliverables.

## H. Validation performed and limitations

- Opened `db.sqlite3` with SQLite URI `mode=ro`, `PRAGMA query_only=ON`; integrity was `ok`, foreign-key check returned no rows. Read only Course 10 attachment/image metadata, not learners, enrollments, attempts, submissions, answers or certificates.
- Ran FFprobe on all six current protected L13/L14 MP4s and canonical Module 4 audio. MP4 metadata is consistent with documented dimensions, rates and codecs; the 6 MP4 file SHA-256 values match current DB records and manifest. Sidecar SRT/VTT files exist; the synchronized Module 4 SRT’s 3 cues end within its audio. No embedded subtitle streams appeared in probed videos.
- Compared known source/output hashes; Module 3 pixel equivalence and Module 4 attachment hashes are also recorded in Phase 2. No complete video decode, transcode, render, audio listening review, visual frame review or browser playback was performed in this audit. Prior package reports are cited as historical evidence, not re-executed results.
- Did not execute any production scripts, install packages, invoke APIs, write DB records, or alter assets. `ffprobe` reads only. No secrets or personal learner information were inspected.
- `node`, `npm`, `obs`, `capcut`, `CapCut`, `espeak` and `espeak-ng` were not available on the current shell PATH; `/usr/bin/ffmpeg` and `/usr/bin/ffprobe` are available. This is a PATH observation, not a definitive whole-machine application inventory.

## I. Recommended improvements

1. **P0 — preserve source reproducibility:** Add a deliberate versioning/archive policy for the source and minimal final deliverables for L13/L14. At present the DB references valid local bytes, but the production project and source outputs are untracked; a fresh clone cannot reproduce them. Keep large QA outputs and protected copies out of Git; use an approved artifact store with checksums and durable backup.
2. **P1 — reconcile manifests:** Update Module 3 asset status from `awaiting_creation` only in an approved metadata task; add canonical/source SHA-256 and attachment state. Keep module-relative lesson order distinct from DB primary keys.
3. **P1 — finish L15 capture dependencies:** Confirm author-approved voice and distribution terms, CapCut Desktop version/OS/language, project/source graphics, capture workflow and actual export test before recording. Capture all three storyboard workflows using genuine screen recordings. Generate VTT only after final edit/voice is locked, then verify cues against the actual media.
4. **P1 — segregate and label outputs:** Adopt clear `source/`, `review-preview/`, `approved-master/`, `superseded/` and `qa/` conventions, with one manifest state per file and checksum. Record whether each version is a visual-only render, audio mix, integrated protected copy or mere preview.
5. **P1 — media integrity automation:** Add a read-only audit command that compares manifest assets, database metadata, file existence, hashes, inline anchors, VTT pairings and Git/local storage state. It should report unreferenced files without deleting them.
6. **P2 — reproducible offline TTS:** Document a clean isolated environment setup, exact checkpoint hash/source, package lock, seed, synthesis text/transcript and output hashes. Preserve the MIT notice. Keep authoring TTS separate from web runtime.
7. **P2 — archive candidates carefully:** Record approved/rejected/needs-listening status and provenance at file level. Do not infer approval from a filename such as `final`, `candidate`, or a directory name; retain rollback copies until explicitly retired.
8. **P2 — include instructional text alternatives:** Preserve transcripts/text equivalents for silent schematic videos and scope spoken-sample VTTs precisely. Continue to label simulated interfaces and simulated ASR examples.

## J. Git status before and after

**Before report creation:** `design/amethyst-motion` was four commits ahead. Four tracked files were modified: `config/settings.py`, `courses/management/commands/import_media_module_5.py`, `courses/management/media_module_5.json`, and `docs/courses/media-module-5-assets.json`. Numerous untracked files were already present; `git status --porcelain=v1 --untracked-files=all` returned 602 entries. There were no staged changes. Existing local settings values are intentionally not disclosed.

**After report creation:** same branch and pre-existing changes remain. The only new file is this report; the `--untracked-files=all` count increases by one to 603. No application, manifest, media, source, database or other working-tree file was modified. Nothing was staged, committed or pushed.
