# Lesson 115 Asset Requirements

All video/VTT records below are **planned, not created**. Names and anchors match `docs/courses/media-module-5-assets.json`; that manifest is not modified in this planning phase.

## Required capture and delivery files

| Key | Genuine capture required | Final course asset | Anchor | Status |
|---|---|---|---|---|
| `m5-l15-v1` | CapCut end-of-sequence/export operation, actual export completion, actual output in player; actual `ffprobe` result may be included | `course_assets/module_5/m5-l15-v1-export-check.mp4`; sidecar `m5-l15-v1-export-check.vtt` | section 3 | Not recorded/not synchronized |
| `m5-l15-v2` | Actual supported project-copy and 9:16 composition workflow, manual reframing, text placement and actual output | `course_assets/module_5/m5-l15-v2-vertical-adaptation.mp4`; sidecar `m5-l15-v2-vertical-adaptation.vtt` | section 5 | Not recorded/not synchronized |
| `m5-l15-v3` | Actual file/player checks and actual source/handoff records; Remotion counterexample separated from export | `course_assets/module_5/m5-l15-v3-final-review.mp4`; sidecar `m5-l15-v3-final-review.vtt` | section 7 | Not recorded/not synchronized |

Recommended isolated production layout (create only at recording/render stage):

```text
video-production/lesson-115-production/
  recordings/raw/                 original screen captures; preserve unchanged
  project-files/<actual-project>/ actual CapCut project directory and dependencies
  narration/raw/                  approved original voice takes/model outputs
  assets/                         copied/created F1 media with provenance
  src/                            optional Remotion explanatory graphics only
  out/previews/                   review exports; never replace finals
  out/final/                      reproducible editorial masters
```

Do not assume CapCut's native project extension or that its project file is self-contained. Keep the native project exactly as the installed build saves it and include every linked media file needed to reopen it.

## Human-supplied production inputs

- A real machine with CapCut Desktop, operator confirmation of exact version/build, OS and interface language. These were not verified by this audit and must be recorded, not guessed.
- A clean isolated F1 example timeline and source files. Keep the F1 case fictional and avoid names, accounts, notices, private paths, real institutional claims and real savings figures.
- Original/permission-cleared visuals. Potential re-use: original F1 notepad SVGs in `course_assets/module_5/m5-l13-v1-production/originals/` and/or the approved Module 3 illustrations. Inspect their accompanying provenance and confirm the content fits before copying; never treat filenames or a checklist template as proof of permission.
- Narration for each locked script. Preferred continuity option is the documented Silero `v5_cis_base_nostress` / `ru_roman` workflow with the retained MIT notice, after confirming the local checkpoint/environment and intended distribution scope. An instructor recording is an alternative only with voice-use permission. No Lesson 115 narration has been generated or approved.
- The approved Noto Sans files and OFL notice from the existing Lesson 113/114 production package if Remotion graphics are produced. Verify the actual files/license when copying; do not depend on a machine-installed font.
- One actual final MP4 per video plus one Russian WebVTT file timed to that final spoken audio. Keep transcript and source/provenance records.

## Audio assets and constraint

- Keep speech in a separate clean source track before mixing; no copyrighted music or third-party SFX.
- Existing approved Minimal Tech Ambient master: `video-production/lesson-113-production/out/audio-preview/minimal-tech-ambient-v1-theme-64s.wav`. Existing mixer deliberately refuses inputs over 62 seconds. These target videos are 115–120 seconds. Do not stretch or loop it. Either deliver voice-first without a continuous music bed, or obtain approval for a sufficiently long original master and seam/fade design before mixing.
- Existing approved UI/tonal effects may be reused only where their provenance and timing fit; do not imply they were captured from CapCut.

## Information to capture in provenance

For each output record source capture hashes; editor/app version, OS and interface language; project/input asset inventory and rights evidence; narration script/voice and license; fonts/license; Remotion package/commit/commands if used; edit/mix commands; actual duration, dimensions, FPS, video/audio codec, sample rate/channels, SHA-256; VTT hash and timing-validation result; reviewers and approval state.

No asset generation, copy or manifest/database update is part of this preparation stage.
