# Module 5 plan — course 10 only

Status: **Phase 5B source artifacts prepared for author review; no module, lessons
or media imported**.

Canonical lesson content: `courses/management/media_module_5.json`.
Full reading copy: `docs/courses/media-module-5-content-review.md`.
Nine final planned video slots (three per lesson), their exact anchors and scripts:
`docs/courses/media-module-5-storyboards.json` and
`docs/courses/media-module-5-assets.json`. These supersede the initial illustrative
video names below. All recordings remain uncreated/unapproved. See
`docs/courses/media-module-5-validation.md` for checks and human-review gates.

Target: existing course **10**, slug `ai-media-content`, title
`ИИ для создания медиаконтента: от идеи до публикации`.
Module order **5**: `Создание и монтаж видео в CapCut Desktop`.
Modules 1–4 (IDs 34–37, lessons 100–111) remain unchanged. Do not create another
course or reuse deleted QA record IDs. Course-wide lesson numbers are 13–15;
their local `Lesson.order` values will be 1–3, with new DB-assigned primary keys.

## Educational approach

Continue the existing fictional Ф1 notebook media project. Propose a short
30–60-second informational video assembled from author-approved assets from
earlier modules. This is an illustrative project, not evidence of a real event.
Keep explanations and practical instructions in Russian, with three objectives,
definitions, a worked sequence, common mistakes/corrections, key takeaways and
one optional ungraded exercise per lesson. Include text equivalents for videos.

No graded Assignment/Quiz records, submissions, attempts, certificates or passing
requirements. Optional practice is reading/checklist content only. All graded
work remains reserved for Module 6; no completion/grading semantics change.

### 13. Подготовка видеопроекта и организация материалов

Objectives:

1. Turn the existing brief/script into a simple ordered shot plan.
2. Organize source images, narration and subtitles with traceable provenance.
3. Create and reopen a CapCut Desktop project with suitable framing.

Planned sections:

- What the final video should communicate, audience and intended viewing format.
- Difference between a project, source media and an exported video.
- Shot list/storyboard: scene, duration estimate, visual, narration, on-screen text.
- Ф1 source inventory: approved images/audio, permissions and factual checks.
- Folder organization and understandable filenames; preserve original files.
- Importing materials and identifying the relevant editor panels in the recorded version.
- Initial canvas/aspect-ratio choices; preview and timeline basics.
- Common mistakes: missing sources, unclear filenames, mismatched framing.
- Optional exercise: organize a local project and make a five-shot draft plan.

Planned visuals: original folder/storyboard diagram and an actual instructor
screen recording of project creation/import. No fabricated application screenshots.

### 14. Монтаж, озвучка и интеллектуальные инструменты

Objectives:

1. Assemble a clear sequence using cuts, trimming and timing against a script.
2. Combine narration, titles and subtitles without obscuring the message.
3. Evaluate AI-assisted output and correct it manually when needed.

Planned sections:

- Rough cut before decoration: arrange the Ф1 sequence.
- Trimming, splitting and adjusting scene duration.
- Framing images and restrained transitions; maintain readable text.
- Importing narration and checking voice/music balance by listening.
- Subtitle workflow: import approved SRT or demonstrate auto captions if available.
- Review every generated caption for spelling, timing and factual accuracy.
- Separate conventional editing from AI-assisted operations; no automatic quality guarantees.
- Common mistakes: excessive effects, competing audio, unreadable titles, unreviewed captions.
- Optional exercise: assemble a rough cut and correct a short subtitle passage.

Planned visuals: actual timeline/narration demonstration, subtitle correction
recording and an original review checklist. Provide a manual fallback if an
AI feature is unavailable or requires a subscription.

### 15. Экспорт, адаптация и подготовка видео к публикации

Objectives:

1. Select and explain export settings suitable for a specified delivery target.
2. Adapt framing and text for another aspect ratio without misleading cropping.
3. Perform a final factual, accessibility, rights and technical review.

Planned sections:

- Export versus saving a project; retain an editable original.
- Dimensions, aspect ratio, frame rate, codec and bitrate as different choices.
- Course-player delivery profile: MP4/H.264 yuv420p with optional AAC-LC audio.
- Export walkthrough using the actual recorded desktop version.
- Horizontal/vertical adaptation: reframe and recheck each title/subtitle.
- Open and watch the exported file from start to finish; check audio and text.
- Readable subtitles, factual accuracy, source permissions and AI-use transparency.
- Common mistakes: wrong canvas, clipped text, missing audio, unverified export.
- Optional exercise: export one version, adapt a second and complete a personal checklist.

Planned visuals: real export-settings recording, original framing comparison and
an actual final-preview example. Preparing a file is not automatic publication.

## Initial asset ideas (video names superseded by Phase 5B manifest)

Prepare a manifest only after the author reviews this outline. Suggested names
are plans, not existing or approved files:

| Lesson | Planned file | Purpose / proposed anchor |
| --- | --- | --- |
| 13 | `m5-l13-project-setup.mp4` + `.vtt` | Real setup/import demonstration after the project-import section |
| 13 | `m5-l13-source-organization.png` | Source folders and storyboard after the organization section |
| 14 | `m5-l14-timeline-narration.mp4` + `.vtt` | Trimming, timing and narration after the rough-cut walkthrough |
| 14 | `m5-l14-caption-review.mp4` + `.vtt` | Real caption correction after the subtitle section |
| 15 | `m5-l15-export-review.mp4` + `.vtt` | Export and playback check after the export walkthrough |
| 15 | `m5-l15-format-adaptation.png` | Framing comparison after the adaptation section |

Use distinct section anchors for separate videos/tracks; the reader pairs exactly
one video and one VTT per nonempty matching `after_section`. Do not use QA sample
footage as completed educational material. No assets are generated by this plan.

Manifest fields: filename, lesson order/title, exact anchor, kind, Russian label,
caption, text equivalent, actual duration/format/codec metadata, SHA-256, creator,
source permissions/license notices, recorded app version/OS/date, human review
status, verified transcript and caption timings. Status remains unapproved until
the real files are available and reviewed. Preserve Silero MIT attribution if
approved Silero narration is reused; exclude ElevenLabs Free/eSpeak candidates.

## Implementation/import proposal

1. Review this outline, then author source content in a reviewed JSON/document
   manifest. No Module 5 source DOCX was found in `course_sources/` during this
   inspection. Do not invent a source document or import provenance.
2. Proposed files (not yet implemented):
   - `courses/management/media_module_5.json` — reviewed Russian lesson content.
   - `courses/management/commands/import_media_module_5.py` — create-only importer.
   - `courses/test_media_module_5.py` — isolated regression tests.
   - `docs/courses/media-module-5-assets.json` — reviewed asset manifest.
3. Reuse Module 4's import pattern, but explicitly verify **both course ID 10 and
   slug**, draft status, author authority, expected Modules 1–4, Russian settings,
   and absence of a pending publication request. Never invoke a course-creation
   or seed command. Refuse existing title/order conflicts or misplaced lessons.
4. Default to `--dry-run`; explicit `--apply` only after review and a verified
   fresh SQLite backup. Lock the course in an atomic transaction. Create exactly
   one Module and three Lesson/LessonLearningContent pairs; no existing updates.
   An identical repeat is a no-op. Later media must not break content idempotency.
5. Match `source_sections` to unique ordered body headings, beginning at the first
   paragraph. Keep interactions empty apart from valid image placements so the
   existing media reader remains active. No lesson-ID/filename rules in React.
6. Reuse `LessonAttachment`, its ffprobe validation, protected storage, grants,
   range delivery and Studio upload. No new video model/storage/migration needed.
7. **Existing batch-import gap:** `import_lesson_media.load_assets()` currently
   accepts image/audio/SRT only and imposes a blanket 20 MiB limit. Before using
   it for Module 5, narrowly add video/VTT kinds, reuse the configured video limit
   and existing signature/metadata validators, and add tests. Do not bypass its
   approval/conflict protections or build another importer/storage mechanism.
   Studio MP4/VTT uploads already work through the existing authorized endpoint.
8. Back up media where a proposed operation could affect existing files. In this
   module's create-only flow, use new unique storage paths and reject conflicts;
   never overwrite Module 3/4 materials. Resolve lessons by course/module/lesson
   order and exact title, not guessed database IDs.
9. Test creation, repeated no-op, conflicting records, transaction rollback,
   unchanged Modules 1–4/course 8/student/certificate data, zero assessments,
   section placement, authorized preview, video/VTT validation and access.
10. Present the content/media dry-run and reviewed asset list before a separate
    approval to write. No command in this plan is currently available to execute.

## Recording prerequisites and factual review

Record original CapCut Desktop demonstrations on a documented supported authoring
machine/version. Official documentation describes Windows/macOS desktop workflows;
do not assume the LMS's Linux VM provides the desktop recording environment.
Verify app version, region, language and subscription before promising exact UI
labels or AI availability. Never require a paid feature without an approved
alternative. CapCut's official guidance describes caption recognition, manual
correction and SRT/TXT import; availability of advanced tools varies. Keep CapCut
editing subtitle files (SRT) separate from the LMS's browser tracks (WebVTT).

Authoritative references checked for planning (2026-11-02):

- https://www.capcut.com/resource/capcut-desktop-download
- https://www.capcut.com/help/how-to-recognise-subtitles
- https://www.capcut.com/help/how-to-import-subtitles

## Approval boundary

No Module 5 records, educational assets or assessments have been created. The next
approval is for this content/import approach. Content authorship, asset creation,
implementation, dry-run and eventual application remain separate review steps.
