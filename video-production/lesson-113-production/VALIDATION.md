# Lesson 113 video package — validation

## Scope and teaching content

Three separate Russian text-led tutorials for course 10 / module 39 / lesson 113.
The 12-second approved reference is preserved; this package is isolated from the
website, Django and stored lessons. No voiceover, music or speech-caption files.

| Video | Scenes | Nominal duration | Frames at 30 FPS |
| --- | ---: | ---: | ---: |
| Source organization | 6 | 46 seconds | 1380 |
| Project setup and import | 6 | 47 seconds | 1410 |
| Timeline and reopening | 7 | 54 seconds | 1620 |

Concise Russian statements have 6–9 seconds per scene. Automated reading-time
checks allow for the entrance and report maxima below three words per second.
The three Markdown transcripts add descriptive equivalents for the illustrations.
These are reading alternatives, not invented speech or synchronized subtitles.

## Visual and browser review

- All 19 scene frames extracted from the actual low-resolution MP4s and inspected.
- Native `frontend_reviewer` independently reviewed all 19 preview frames and the
  lesson/storyboard source. A clipped right-edge timeline tick was corrected; the
  third preview was rerendered and its corrected frame reviewed by both agents.
- Chromium Studio checks visited all 19 representative scenes: local font loaded,
  instructional text visible, no detected text/panel overflow, zero JavaScript or
  console errors. Evidence: `out/qa/studio-checks.json`.
- Two Studio `/events` SSE connections were canceled during composition navigation;
  retained in the evidence as expected navigation aborts, not hidden as clean network.
- The first QA helper selected the duration field instead of the playback timecode.
  This changed task-local composition metadata. It was detected and corrected;
  the affected render was stopped and rerendered. The corrected helper uses the
  playback field and verifies unchanged source. `calculateMetadata` now derives
  frame count from scene data. Only verified, correctly timed outputs are delivered.

## Technical evidence

See `out/technical-validation.json` for final per-file codec, dimensions, frame
count, duration, byte size, SHA-256, audio peak/RMS and SFX correlation results.
The verifier runs complete FFmpeg decoding, checks H.264/yuv420p/AAC, and compares
every decoded SFX against its source at the scheduled animation frame. Minor AAC
container padding does not add video frames. No audio carries required teaching
information. Numerical measurements do not replace the author's listening review.

## Honest demonstration limits

Every scene labels its interface as an illustration, not a CapCut recording.
There are no fabricated real application actions, save confirmations, exact
version-specific button locations or cloud-sync promises. Reopening, relinking
and installed-version behavior still require the learner's own application.
The fictional F1 project claims no measured environmental or university outcome.

No browser playback through the AI Courses protected player is claimed: nothing
has been attached. Final student-player integration requires a later authorized
upload. Full decoding and composition QA are separate from that integration test.

## Preservation

A start-of-task SHA-256 inventory covers 538 existing project, SQLite and approved
prototype files. Final preservation verification is recorded below. No main app
files, course manifests, lesson text, authentication, media permissions or prior
assets are part of this package. No commit, push, publication or deployment.

## Reproduction

See [README.md](README.md) for Studio URLs, render commands, SFX mute/volume,
component structure, licenses and known limits. All render/cache/evidence files
live under ignored `out/`; source and documentation remain separate.
