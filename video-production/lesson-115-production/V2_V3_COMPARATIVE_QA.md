# Lesson 115 — V2/V3 Preview and Comparative QA

**Checked:** 2026-11-09
**Scope:** 960×540 Remotion review renders with the already-approved V1 Minimal Tech Ambient mix settings. These are previews only; V2/V3 have not received human listening approval and are not final exports.

## Outputs

- V2 preview: `out/previews-bgm-v1/m5-l15-v2-vertical-adaptation-preview.mp4`
- V3 preview: `out/previews-bgm-v1/m5-l15-v3-final-review-preview.mp4`
- V2 pre-mux visual render: `out/previews-bgm-v1/m5-l15-v2-vertical-adaptation-visual.mp4`
- V3 pre-mux visual render: `out/previews-bgm-v1/m5-l15-v3-final-review-visual.mp4`
- Comparative contact sheet (six representative scenes per version): `out/qa/comparative-bgm-preview-frames/three-version-scene-comparison.jpg`
- Individual V2 contact sheet: `out/qa/comparative-bgm-preview-frames/v2-contact.jpg`
- Individual V3 contact sheet: `out/qa/comparative-bgm-preview-frames/v3-contact.jpg`

The frame samples cover the midpoint of every scene, including opening and final scenes. One frame per scene is retained in `out/qa/comparative-bgm-preview-frames/` for closer inspection.

## Render and stream validation

Both preview compositions used Remotion 4.0.540, two workers, half-scale 960×540 output, H.264/yuv420p, 30 fps and CRF 21. The prepared matching audio stems were muxed with FFmpeg using video stream copy (`-c:v copy`) and AAC stereo at 48 kHz / 320 kbps. No full-quality final renders were made.

| Version | Duration | Video | Audio | Size | SHA-256 |
|---|---:|---|---|---:|---|
| V2 — vertical adaptation | 80.733333 s; 2,422 frames | H.264, 960×540, 30 fps | AAC-LC, stereo, 48 kHz; 80.733000 s | 3,455,105 bytes | `54bb85cdfeff14199ff79bda5837e442d56923127493259662488a8420ff256d` |
| V3 — final review | 79.166667 s; 2,375 frames | H.264, 960×540, 30 fps | AAC-LC, stereo, 48 kHz; 79.166000 s | 3,373,387 bytes | `74e5b056cd9d33ed3e529ca13ea32caaa6f9c924c3efa86de69adfc94198398c` |

The muxed audio begins at the media start and differs from video duration only by normal AAC packet rounding (under one millisecond). Full FFmpeg `-xerror` decode passed for both outputs. SHA-256 hashes of the encoded video streams match their respective pre-mux visual renders exactly:

- V2: `SHA256=6683da211e58781de7fb97721a7a88a67731d12c282c0f34fafc2b04dc5d3f43`
- V3: `SHA256=19969c4717d9e89174bee0c7f88e8d526a086fa30469ddf09e37a008e95d93bc`

This confirms that audio muxing did not re-encode or alter the rendered frames. V1 was not modified. Its approved music candidate remains `out/final-sentence/m5-l15-v1-bgm-candidate.mp4`.

## Approved music and mix configuration

All three audio mixes use the existing approved settings: narration-relative music target gap 22 dB, maximum duck 6 dB, 0.2 s attack and 1.0 s release. The provenance also records the existing speech-activity threshold (-48 dBFS), 1.2 s fade-in and 2.0 s fade-out. Music gain is set per track to retain the same measured speech/music relationship; this does not change the approved composition or ducking settings.

The original project-created Minimal Tech Ambient source is 48 kHz stereo PCM24 and has SHA-256 `bb3a3d45fc3820a18a087c2791de0139c7cc3459456749071a3ed4ac7ebbb489`, matching `content/audio-bgm-provenance.json`. It is the same track source used by the owner-reviewed V1 candidate. V2 and V3 use their already prepared full-duration PCM24 mix stems:

- V2 stem `out/audio-bgm/m5-l15-v2-vertical-adaptation-bgm-mix.wav`: SHA-256 `3c632eceef447e33547ebf6b767891cc76a94d6b4bb0559320c43af415cd4699`.
- V3 stem `out/audio-bgm/m5-l15-v3-final-review-bgm-mix.wav`: SHA-256 `766d9695ea7bd087a6d57c88a4b5d052224b01c113196232a4a80727767b0697`.

The provenance identifies the foreground input as the existing narration-plus-UI-SFX mix, used unchanged by the music mixer; music ducking follows the voice-control stem. No sound-effect or narration timing was rewritten. V2/V3 mixing parameters are consistent with V1. This automated evidence cannot establish subjective speech intelligibility; no human listening approval is claimed for V2/V3.

## Audio QA

EBU R128 analysis of the AAC preview streams:

| Version | Integrated loudness | Loudness range | True peak | Result |
|---|---:|---:|---:|---|
| V1 approved reference | −25.5 LUFS | — | −6.3 dBTP | Owner approved soundtrack/mix configuration; original reference left unchanged |
| V2 preview | −25.4 LUFS | 4.9 LU | −5.6 dBTP | No clipping detected |
| V3 preview | −24.7 LUFS | 4.1 LU | −5.1 dBTP | No clipping detected |

The peaks remain below 0 dBTP. Integrated loudness is close across the three versions, while minor differences reflect their distinct voice/SFX content. Automated values do not substitute for listening. Narration/SFX timing is inherited from the exact pre-mixed foreground stems; both audio tracks start at zero and decode through the full video duration.

## Subtitle QA

The original WebVTT files were not changed. Both begin with `WEBVTT`, contain ordered, non-overlapping cues and end before the video duration:

- V2: `out/final-sentence/m5-l15-v2-vertical-adaptation.vtt`, 13 cues; last cue ends at 00:01:19.615 within 80.733 s.
- V3: `out/final-sentence/m5-l15-v3-final-review.vtt`, 15 cues; last cue ends at 00:01:18.060 within 79.167 s.

The Remotion compositions also place their sentence captions from the existing sentence timing data. These checks establish cue ordering and bounds, not phoneme-level alignment. The WebVTT files are sidecar assets and are not embedded as a subtitle stream in these MP4 previews.

## Comparative visual QA

Six scene-midpoint frames were reviewed per version, plus individual 960×540 samples from V2 scene 3 and V3 scene 5. Across inspected samples:

- Main headings, explanatory panels and educational diagrams stay within the frame; no clipping or overlap was observed.
- Spoken captions remain distinct from the instructional illustration and footer. At preview scale the 960×540 text is readable in the inspected frames; final-resolution legibility still needs review after a future full render.
- The visual treatment is consistent across V1–V3: dark editorial canvas, restrained lavender/sand accents, matching title/header/footer, and the same disclosure hierarchy.
- The software-like panels carry “ПОЯСНИТЕЛЬНАЯ ИЛЛЮСТРАЦИЯ” and “НЕ ФАКТИЧЕСКИЙ ВЫВОД ПРОГРАММЫ” disclosures; the footer also identifies them as schemes and directs learners to verify actions in their own editor version. They are not represented as actual CapCut recordings.
- No confirmed visual defect requiring a source edit was found. V1 and the V2/V3 source compositions were not changed during QA.

The videos have different instructional purposes, so their diagrams are not interchangeable. V1 is strongest as a technical export-check walkthrough; V2 makes the horizontal-to-vertical adaptation and composition comparison clearest; V3 has the strongest editorial handoff/checklist structure. There is no defensible single overall visual winner from these samples. The owner should review both previews and choose independently; no final version is selected here.

## Tests and limits

- `python3 -B scripts/test_content.py`: PASS (three targets, six storyboard scenes each, narration/synthesis text identity, stress metadata and illustration disclosure).
- `python3 -B scripts/test_background_music.py`: PASS (4 tests).
- FFmpeg full-file decode with `-xerror`: PASS for V2 and V3.
- FFprobe stream, duration, frame-count and codec checks: PASS.
- VTT syntax/order/non-overlap/duration-bound checks: PASS.
- Encoded video stream hash comparison before/after mux: PASS for both previews.
- Human listening review: NOT DONE for V2/V3. These are previews awaiting owner review, not approved finals.

## Playback

```bash
ffplay -autoexit video-production/lesson-115-production/out/previews-bgm-v1/m5-l15-v2-vertical-adaptation-preview.mp4
ffplay -autoexit video-production/lesson-115-production/out/previews-bgm-v1/m5-l15-v3-final-review-preview.mp4
```

Course 10 remains unpublished. No video was attached to the course; database, canonical lesson content, media manifests, V1, Lesson 113 and Lesson 114 were not changed.

## Final Full HD production and Lesson 15 integration — 2026-11-10

The prior preview-only status above describes the comparison checkpoint and is superseded by this final production record. The owner approved the V2/V3 preview visuals directly; approval was recorded against the current source hash map before rendering. The renderer's source-hash approval gate passed. No V2/V3 visual design files were changed. V1's approved Full HD BGM candidate was preserved byte-for-byte.

Final protected deliverables are under `out/final-bgm/`:

| Version | MP4 | WebVTT | Duration / frames | Audio | MP4 SHA-256 |
|---|---|---|---|---|---|
| V1 | `m5-l15-v1-export-check.mp4` | `m5-l15-v1-export-check.vtt` | 94.533 s / 2836 | H.264 1920×1080 30 FPS; AAC-LC stereo 48 kHz | `22a00b5d27549f993ef9c1c2d8205fbdf6ba28cbbe76e68ad547dcf0f4ae059f` |
| V2 | `m5-l15-v2-vertical-adaptation.mp4` | `m5-l15-v2-vertical-adaptation.vtt` | 80.733 s / 2422 | H.264 1920×1080 30 FPS; AAC-LC stereo 48 kHz | `704519231eaf4dbc9733f1b4aa2c3fd57630ab63d4ce6601bd056885c031a2ae` |
| V3 | `m5-l15-v3-final-review.mp4` | `m5-l15-v3-final-review.vtt` | 79.167 s / 2375 | H.264 1920×1080 30 FPS; AAC-LC stereo 48 kHz | `f8a08dc12683c102036e38e9627b14689b69e27567117315c2229a273ce298f3` |

Final audio EBU R128: V1 −25.5 LUFS / 4.5 LU LRA / −6.3 dBTP; V2 −25.4 LUFS / 4.9 LU LRA / −5.6 dBTP; V3 −24.7 LUFS / 4.1 LU LRA / −5.1 dBTP. All complete MP4s decoded successfully. Every V2/V3 decoded video frame matched its corresponding pre-mux full-quality render. VTT cue counts are 17, 13 and 15 respectively; all cues are ordered, non-overlapping, within the paired video duration, and text-matched to the narration transcript. This verifies file-level timing bounds, not human listening quality.

The six attachments are present on Course 10 / Module 5 / Lesson 115 only: IDs 17–18 after section 3, IDs 19–20 after section 5, and IDs 21–22 after section 7. React's existing `attachmentLayout` utility was checked using actual Lesson 115 data and grouped the three video/VTT pairs under those anchors with no fallback items. Lesson text and its nine anchors are unchanged. A repeat importer dry-run returned `KEEP 6` and made no changes.

The verified pre-write backup is `.local-course-backups/lesson115-final-integration-20261109-211343-ef8297e3`; its SQLite copy passed integrity and foreign-key checks, its before-state records zero Lesson 15 attachments, and protected-media/source-input archives were hash-verified. Course 10 remains unpublished. Django checks and focused Lesson 115 integration/video tests passed; frontend lint and production build passed. Real authenticated Firefox playback and subtitle-toggle interaction remain unverified because this session had neither an authorized browser session nor an available Playwright MCP tool. Human listening approval of the complete final V2/V3 renders is also not claimed.
