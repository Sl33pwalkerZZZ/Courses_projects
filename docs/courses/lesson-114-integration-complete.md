# Lesson 114 — Phase 5K integration complete

Completed locally on 2026-11-06 on `design/amethyst-motion`. Course 10 (`ai-media-content`) remains unpublished. Existing module39 / lesson114 reused; no course, module or lesson created. No video re-encoding, remixing, rendering or source-file modification. No commit/push.

## Protected attachments

| ID | Type / filename | Placement | Duration / cues | SHA-256 |
|---|---|---|---|---|
| 12 | video: `m5-l14-v1-rough-cut-quality-v2.mp4` | 3. Черновая сборка и ритм кадров | 54 | `398bccbc15ee19f4fdb1158809aafedcd1d73fc1354b8f3383633eda54a56bb1` |
| 13 | video: `m5-l14-v2-narration-balance-quality-v2.mp4` | 5. Озвучка, паузы и баланс звука | 60 | `0d4171604271e3c62a122e41590be221a9cdec6b84184e8006a811dca513b8df` |
| 14 | video: `m5-l14-v3-caption-review-quality-v2.mp4` | 7. Субтитры и ответственное использование ИИ | 60 | `266c7770ac8fe56fa73061a055548e2ba7a0dc7e838e53eec3763560a0342ad2` |
| 15 | vtt: `m5-l14-v2-narration-balance-quality-v2.vtt` | 5. Озвучка, паузы и баланс звука | 9 cues | `0f23a05e719d13ae7b4715d8cb78730f772545789fb5117ee0395dd485eb1620` |
| 16 | vtt: `m5-l14-v3-caption-review-quality-v2.vtt` | 7. Субтитры и ответственное использование ИИ | 6 cues | `52f8083248c0739db35e7cb2af6c399d385983429da73659185aaf01f49e3ac2` |

Source MP4s remain under `video-production/lesson-114-production/out/final/`; source tracks under its `content/`. Protected copies use the existing attachment storage and `/api/lesson-attachments/{id}/` metadata/file and playback-grant endpoints. No public permanent MP4 URL. All videos: H.264/yuv420p,1920×1080,30fps; AAC-LC stereo48kHz.

The two native tracks contain only actual short Silero spoken examples, not full instructional narration. Video2 has9 cues and video3 has6; timestamps match approved spoken-segment offsets and stay within60s. Captions and text equivalents prominently disclose this limited scope. Video1 has no speech/VTT. Full visual instructions remain accessible in the lesson and attachment text equivalents. No fictional ASR result is presented as a real measurement.

## Eight approved paragraph edits

1. Честно обозначить схематическую адаптацию исходных планов реальной записи и наличие настоящих звуковых примеров.
2. Видео1 после целого раздела3, а не вместо письменной инструкции.
3. После видео1 следует различающая запись и картинку практика; определение кадрирования сохранено.
4. Видео2 после раздела5; точное описание реального A/B, а не ненаблюдаемой обработки.
5. После видео2 — понятная необязательная практика; исходное различие ИИ/ручных операций сохранено.
6. Единственная терминологическая замена: пример соответствует настоящей разрешённой записи, а не отсутствующей новой фразе.
7. Видео3 после раздела7; никаких вымышленных результатов распознавания или готовых речевых дорожек к беззвучной инструкции.
8. Практика после видео3; все прежние предупреждения и итоги остаются.

Exact before/after paragraphs and hashes are pinned in `courses/management/lesson114_quality_v2.json`; only Lesson114.text_content changed. Three objectives, nine original sections/anchors, ordering, original theory and learning metadata preserved. Canonical `media_module_5.json` second lesson synchronized and importer source checksum updated. Manifest updates restricted to lesson14 entries plus overall status/notes; lessons13/15 asset entries preserved.

## Backups and verification

- Mandatory pre-edit snapshot: `.local-course-backups/lesson114-phase5k-preflight-20261106-105325-0c227f16/`.
- Fresh pre-write snapshot: `.local-course-backups/lesson114-phase5k-20261106-060040-944506b1/`. Timestamps use the respective running environment timezone; both distinct snapshots retained.
- Each contains a SQLite backup, verified `protected-media-and-approved-sources.tar`, and private `before-state.json`. SQLite integrity/FK checks pass; tar inventory and every archived SHA-256 verified. No previous backup overwritten.
- Post-write read-only SQLite comparison across39tables confirms only Lesson114.text_content, attachment rows12–16 and the attachment sequence differ. All other rows, schema, courses8/10 properties, lessons113/115, enrollments, progress, quizzes, submissions and certificates unchanged. Integrity `ok`, zero FK violations.
- Existing protected-media hashes, all approved113/114 MP4/VTT source hashes, and `config/settings.py` match preflight. No media deleted/overwritten.
- Repeated dry-run: `KEEP 5 (3 videos + 2 VTT); approved text unchanged; no-op, no backup or writes.`

## Implementation files

- `courses/management/commands/integrate_lesson114_videos.py`: narrowly scoped exact-state command; default dry-run; pinned8edits/5assets; backup before transaction; conflict refusal and rollback file cleanup.
- `courses/management/lesson114_quality_v2.json`: approved payload and hashes.
- `courses/test_lesson114_integration.py`:13 isolated tests including real approved MP4 delivery.
- `courses/management/commands/integrate_lesson113_videos.py`: reusable backup prefix argument only; default113 behavior preserved.
- `courses/management/media_module_5.json`: only lesson114 text synchronized.
- `courses/management/commands/import_media_module_5.py`: reviewed source checksum/comment updated; generic importer not rerun.
- `docs/courses/media-module-5-assets.json`: actual lesson114 sources, metadata, hashes, attachmentIDs and scoped tracks.
- This report.

## Tests and independent reviews

Passed:

```text
.venv/bin/python -B manage.py test courses.test_lesson114_integration courses.test_lesson113_integration courses.test_media_module_5 courses.test_video courses.test_video_upload courses.test_attachments --noinput
69 tests — OK (including13 new Lesson114 tests)
node --test tests/*.test.mjs —34 test files passed,0 failures/skips
npm run lint — passed
npm run build — passed
manage.py check — no issues
manage.py makemigrations --check --dry-run — no changes
git diff --check — passed
```

Django tests used isolated test database/temp media, including actual approved MP4 checksums/fullGET/HEAD/206 single ranges/416 and expired/revoked grants. Pending/rejected/anonymous users denied; owner preview allowed; VTT permissions and exact cue pairing verified. Async streaming tests were run outside the restricted sandbox with a180s timeout because sandbox thread wakeups can stall; no development database used by tests. Expected denial/injected-rollback logs are covered test cases.

Native `security_reviewer` independently reviewed the exact-state command, approved source hashes, scoped VTTs, backup and rollback: no blocking findings. Native `browser_qa` ran read-only isolated presentation checks. Neither reviewer mutated data or spawned additional agents.

## Browser evidence and limitations

Firefox MCP could not launch because its executable is missing; no installation attempted. Used existing Node Chromium with intercepted fixture grants/files and exact approved media bytes. This is not a live authenticated student/instructor verification.

-18 combinations: RU/KK/EN × light/dark ×1440/390/320px; no overflow.
-3inline videos after3/5/7;9sections,3objectives; visible spoken-only subtitle scope.
-All3actual MP4s played muted and sought to20s; native VTT parsed9/6cues.
-Loading/403 denial and retry UI, reduced-motion setting, video focusability checked. No runtime errors; expected simulated403console messages and navigation cancellations retained.
-Fixture shape errors (missing nullable poster field and missing actual workspace wrapper) were corrected in the harness, not application code. No confirmed frontend bug required a source edit.

Evidence: `.local-cinematic-qa/phase5k/BROWSER-QA.md`, `report.json`, `scope-report.json`,19screenshots. Representative: [dark mobile video2](../../.local-cinematic-qa/phase5k/dark-320-video-2.png), [light desktop video3](../../.local-cinematic-qa/phase5k/light-1440-video-3.png). Local QA evidence remains untracked.

## Manual local inspection

Open **http://localhost:5173/lessons/114** with the existing authorized owner/administrator session (or use existing Instructor Studio preview). Course is unpublished; do not publish to test. Check inline videos after sections3/5/7, seeking, captions on2/3, readable equivalents, and following practice paragraphs. Live cookie issuance/revocation and real-account navigation remain manual checks because no authorized test session was supplied. Backend enforcement was verified only in isolated tests.

Idempotent review command:

```bash
.venv/bin/python -B manage.py integrate_lesson114_videos --dry-run
```

Local approved apply already completed; do not rerun unrelated importers or restore the full backup casually. Rollback would require a separate reviewed targeted procedure preserving subsequent changes; snapshots retained for recovery. No migration, frontend redesign, publication, commit or push performed. All pre-existing unrelated working-tree changes retained.
