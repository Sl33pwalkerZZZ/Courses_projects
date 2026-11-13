# Remotion Graphics Specification

## Reuse boundary

Use the existing Lesson 113/114 Quality V2 Remotion style and isolated package conventions, not a new design system:

- Source references: `video-production/lesson-113-production/src/tokens.ts`, `fonts.ts`, `primitives.tsx`, and `video-production/lesson-114-production/src/Workspace.tsx` where it is present and relevant.
- Existing visual identity: Noto Sans; graphite/warm-white surfaces; restrained lavender, mint, blue and sand; restrained opacity/focus transitions; original F1 editorial diagrams. Fonts are locally loaded and have OFL notices in the existing package.
- Use frame-driven, deterministic timing. Keep motion calm and text on screen long enough to read. No decorative loops, heavy camera movement, fake cursor gestures, flashing, or animation over small UI text.
- Do not change the application frontend or reuse course-reader code as a substitute for a Remotion composition.

## Safe graphics by video

| Video | Appropriate original Remotion graphics | Must remain genuine recording |
|---|---|---|
| V1 — export check | Opening/end title; separate diagram “MP4 container / H.264 video codec / dimensions / frame rate”; measured-file checklist with fields populated only from actual `ffprobe` output | CapCut sequence, export panel/settings, progress/completion, output in player, terminal metadata capture |
| V2 — vertical adaptation | Original F1 artwork in labeled 16:9 and 9:16 frames; illustrative crop/margin guide; comparison of preserved/cropped composition | Actual project copy, actual ratio selection, reframe/scale/text edits and final export shown in the installed CapCut build |
| V3 — final review | Three-stage editorial checklist; clearly fictional unsupported-claim card; handoff checklist with no fabricated approvals | Actual export playback, real subtitle/caption check, actual source record and version handoff evidence |

## Separation and labeling

- Real application capture is never recreated, painted over, or presented inside a Remotion imitation of CapCut. Do not build a fake app window, fake export progress, fake context menu or fake settings.
- Put diagrams in clean interstitials or use an unobtrusive labeled overlay outside important app controls. Use labels such as `Схема · не интерфейс CapCut` and `Учебный пример · не результат проекта` where a graphic might be mistaken for evidence.
- Do not use Remotion to fill missing evidence. A measured export field must come from the real file; permission state must come from a verified record; an unavailable UI control must remain unavailable in the lesson.
- No graphics are created in this preparation package.
