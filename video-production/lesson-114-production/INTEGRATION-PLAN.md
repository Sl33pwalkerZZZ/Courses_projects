# Lesson 114 — proposed integration, not applied

Target existing course10 `ai-media-content`, module39, lesson114. Course stays unpublished. This production phase does not edit SQLite, the canonical Module5 JSON, lessons113/115, existing media or application code.

## Placement using existing anchors

| Video | Existing exact `after_section` | Practice afterward |
|---|---|---|
| `m5-l14-v1-rough-cut-quality-v2.mp4` | `3. Черновая сборка и ритм кадров` | Start of section4: select the correct object, distinguish temporal footage from stills, check the gap and preserve words/conditions. |
| `m5-l14-v2-narration-balance-quality-v2.mp4` | `5. Озвучка, паузы и баланс звука` | Start of section6: align image/voice, listen solo, lower competing background, check words and fades. |
| `m5-l14-v3-caption-review-quality-v2.mp4` | `7. Субтитры и ответственное использование ИИ` | Start of section8: verify actual words, punctuation and cue boundaries, then check without sound. |

The reader inserts media after the full anchored section. Pre-video instructions belong at that section's end; post-video practice follows in the next section. The illustrative workspace is never described as real CapCut footage or a verified button layout.

## Exact written-content proposal

`content/lesson114-sync-proposal.json` contains complete before/after, hashes and eight guarded paragraph replacements. It is review-only. `content/lesson114-readonly.json` captures the original lesson and structured metadata from a query-only SQLite connection. The canonical source's second lesson matches this snapshot.

1. Append one explanation of schematic illustrations and genuine synthetic speech samples to the existing copied-project paragraph.
2. Append a watch/expected-result cue for roughcut after section3's gap warning.
3. Prepend optional practice distinguishing recording/still-duration changes in section4, preserving the original definition.
4. Append a watch cue for the genuine voice-solo/A/B comparison after section5's original DSP warning.
5. Prepend voice/image/music follow-up practice in section6, preserving the original distinction between manual editing and AI.
6. Replace only the incompatible constructed caption example «Мы не приводим расчёт экономии»/«Мы приводим расчёт экономии» with the genuine recording's «а не измерение экономии»/constructed «а измерение экономии». Preserve the explanation that this is deliberately modelled, not real ASR output.
7. Append a watch cue for caption/word/punctuation/timing checking at the end of section7, explaining SRT versus WebVTT accurately.
8. Prepend optional caption verification practice in section8, retaining every original error warning and summary.

All three objectives, nine ordered heading paragraphs, definitions, F1 fictional status, rights/privacy/AI limitations, original educational explanations and module6-only grading boundary are preserved. The written lesson remains independently usable. Nothing creates assessment conditions.

## Text equivalents and genuine optional caption files

Each video has `content/<basename>.equivalent.ru.txt` plus a scene-by-scene `.transcript.ru.md`. These describe visible instructional actions, not a fictitious instructor narration. They identify schematic graphics, fictional file names and constructed ASR errors.

Roughcut has no speech and no spoken VTT. Audio balance and caption review contain the existing authorized Silero F1 speech, not a new lesson voiceover. Their optional `.vtt` files caption only those genuinely audible phrases:

- Video5: source starts12.5s/23s/41s; exact same8.5625s speech each pass.
- Video6: source starts8s/51s.
- Original source cue times:0.200–2.950,3.250–6.125,6.425–8.312s. Global cue positions are calculated by adding the actual sample starts, not estimated from reading speed.

These VTT files do not pretend the on-screen instructions were spoken. The text equivalent remains necessary for the visual instruction. Future protected-player attachment pairing must use exactly one video+one VTT on each applicable anchor. Do not create a VTT for a silent video merely to satisfy the old planning manifest.

## Changes from the original storyboard plans

Original plans called for110/120/120-second real CapCut recordings and new instructor narration. The approved QualityV2 direction explicitly replaces that representation with concise54/60/60-second diagrams. No real CapCutcapture or real ASR execution is claimed. The separate technical clip is a conceptual temporal diagram (12→10s, two splits at3/5s, removal and manual close to8s), not documentary footage of F1. Stills are then handled separately.

The source recording reused from Module4 says: «Команда использует чистую сторону листа. Это пример повторного использования бумаги, а не измерение экономии». The original storyboard's «Мы не приводим…» is not in that recording; no new unapproved recording was synthesized. This mismatch is resolved in the proposed narrow text edit only, not silently in the saved lesson.

## Later integration safeguards

After author video/text review and separate explicit integration approval:

1. Reverify target IDs/slug/draft state, lesson text and metadata against the snapshot; reject unexpected changes.
2. Verify final MP4 hashes/profile and optional VTT syntax, actual audible cue timing and unique anchors.
3. Create a new verified SQLite online backup and protected-media/source inventory backup; preserve all current attachments and learner records.
4. Reuse the existing protected attachment validation/storage/grant system. Use kind `video`, MIME `video/mp4`; genuine VTT uses kind `vtt`, MIME `text/vtt`.
5. Use exactly the five supported metadata strings: label, caption, transcript (concise visual equivalent), provenance and after_section. Keep model/source MIT notice and original graphic/music provenance. No public storage URLs or JWT query strings.
6. Use a narrow reviewed idempotent operation, rejecting mixed states/conflicts, to apply only the approved text paragraph edits and new attachments transactionally. Track only newly written files and clean them on exceptions. Do not rerun the create-only module importer to patch text.
7. Mirror the reviewed text into only the canonical second lesson and intentionally update its pinned source checksum. Do not change other lessons or existing objectives/headings.
8. Verify authenticated draft preview, enrollment permissions, Range/HEAD, grant expiry/revocation, inline placement and responsive layout in an authorized context. This phase performs no upload or application permission change.

No migration is required by this plan. Rollback must target only new IDs/files and the exact approved after-text, never restore a whole old database over newer student activity.
