# Audio and Subtitle Workflow

No audio or subtitle files are generated during production preparation. All cue timing is pending real recording/edit/export.

## Narration

1. Obtain author approval of the three Russian scripts in `narration/`.
2. Choose an authorized speaker. The existing Lesson 114 package documents Silero `v5_cis_base_nostress`, `ru_roman` and an MIT notice; reuse only after verifying the checkpoint, runtime and distribution scope. Do not use ElevenLabs Free, eSpeak or an unverified voice source as production narration.
3. Generate/record each script to a separate lossless WAV source, preserving the exact script, speaker/model/tool, license/permission, sample rate, duration and checksum. Do not force the 115–120 second storyboard timing by time-stretching; edit pauses or revise the cut after review.
4. Capture CapCut system audio only if an authentic operation sound is educationally useful and rights/privacy are clear. Otherwise keep it muted and use the approved voice/effects as separately controlled tracks.

## Music and effects

- Use no continuous music by default for these longer cuts until the 64-second approved theme has an approved long-form extension or seam. The Lesson 113 mixer refuses videos over 62 seconds. Do not loop, stretch, or hide the loop point.
- If an extended theme is later approved, preserve speech intelligibility, disclose the source, use the same review/mixing convention as Lessons 113/114, and independently verify loudness/true peak/clipping. Do not assume the earlier −9 dB bed gain is correct for every new narration.
- Existing procedural tonal cues may be used sparingly if their original source and timing are preserved. Never label a Remotion sound as captured from CapCut.

## WebVTT and accessible equivalent

1. Lock the narration and final edit first. Export the actual candidate MP4 and final audio/mix.
2. Create the `.vtt` from the audible final speech and align cue starts/ends by listening to that exact export. Storyboard timestamps are not subtitle timestamps. Do not create a placeholder VTT or copy timings from an earlier video.
3. Validate WebVTT header/UTF-8, monotonic cue order, no unintended overlaps, all cues within the video duration, accurate wording/punctuation and synchronization at the beginning/middle/end. Include meaningful spoken words; identify non-speech sound only when it matters.
4. Keep cues concise and readable (normally no more than two lines), avoid covering key interface evidence, use sufficient display time, and preserve essential negation/fictional-example disclaimers. The VTT is a sidecar course attachment, not a fake burned-in UI panel.
5. Maintain an approved full transcript/readable text equivalent beside the video. If the final clip is edited after VTT timing, retime and retest the VTT.
6. Verify both voice-on and muted playback, subtitle activation, keyboard-operable playback where tested, and that the essential demonstration remains understandable without relying on color or sound alone.

## Later integration

Only after author approval and final asset validation should a separately authorized task update the module asset manifest or create protected `LessonAttachment` records. Preserve stable section anchors 3/5/7, use the existing protected delivery system, perform a verified database/media backup, dry-run, test permissions and confirm the course remains unpublished.
