# Final Quality and Approval Checklist

Use this only after real recording/rendering. It is a plan, not a claim that media exists or passed.

## Editorial and evidence

- [ ] Correct video key, title and section anchor: V1/3, V2/5, V3/7.
- [ ] All CapCut views are actual recordings of the identified version/build, OS and interface language.
- [ ] Narration matches the approved script and describes what is visibly happening; no invented controls, settings, performance, project outcomes or app capabilities.
- [ ] F1 is labeled fictional. No fabricated savings, institutional result, permission record, metric, grade or public-posting event.
- [ ] Remotion diagrams are original, clearly labeled, and never mistaken for CapCut UI or evidence.
- [ ] Source/voice/music/fonts permissions and provenance are documented; no personal/student data or secrets appear.
- [ ] Course 10 remains unpublished and no video is uploaded/attached by this production task.

## Container and media integrity

Preferred course-player delivery profile (from the Module 5 asset conventions and current server validator):

- MP4 container, one H.264 video stream, `yuv420p`.
- Landscape screen-capture delivery preferred at 1920×1080 / 30 fps to match Lessons 113/114; the video content in V2 demonstrates a separate 9:16 canvas. Do not change delivery orientation without owner approval.
- Optional one AAC-LC mono/stereo audio stream; preferred 48 kHz stereo for narration/mix. The validator allows 44.1 or 48 kHz and one/two channels.
- The server validator accepts dimensions up to 3840×2160 and frame rate up to 60, but the series target remains 1920×1080/30. These are compatibility bounds, not a quality guarantee.
- Use browser-friendly MP4 faststart where the final mux workflow supports it. Do not modify real screen content to meet codec settings; re-encode only from a preserved source and verify the result.

Checks:

- [ ] `ffprobe` records codec/profile, pixel format, width/height, frame rate, duration, audio codec/rate/channels and stream count for every final.
- [ ] Full FFmpeg decode succeeds; no truncation, corruption, black/silent unexpected sections or clipping.
- [ ] Audio/video starts and durations align. Voice is intelligible, natural and not covered by music/SFX; no loudness jumps.
- [ ] At beginning, middle, end and all critical operations: inspect visible UI, disclosure labels, text safe margins and audio/captions.
- [ ] VTT cue format/UTF-8/order/bounds/text are checked against the exact final MP4. Every VTT was generated from actual timing.
- [ ] A human watches and listens to each full final, including V2 crop legibility and V3 fictional labels. Record named role/review date in local approval log (no personal data in public captions).
- [ ] A clean copy of each CapCut project reopens with its dependencies; source captures remain unchanged and hashed.

## Approval gates

1. Script and storyboard approval.
2. Actual CapCut/version/OS and source/rights verification.
3. Short capture/preview review before full edit.
4. Narration/music/subtitle review after actual timing.
5. Full export QC and author approval of each exact file/hash.
6. Separate explicit authorization for a protected-media import, backup, dry-run and browser access test.

This phase only prepares planning files; none of these gates has been completed.
