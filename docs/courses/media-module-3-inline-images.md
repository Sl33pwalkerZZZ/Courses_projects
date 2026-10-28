# Inline protected illustrations — Module 3

## Metadata contract

No migration or new storage system. The existing `LessonLearningContent.interactions` list can contain:

```json
{
  "type": "image_placement",
  "image_id": 123,
  "after_section": "Exact heading from source_sections",
  "caption": "Readable authored caption"
}
```

This is placement metadata, not an interactive teaching card. The image must already belong to the lesson. Studio validates bounded fields, unique image references and existing exact anchors. The metadata survives normal Studio saves; the teaching-section editor does not present it as a blank teaching card.

`MediaLessonReading` renders a figure after the anchored section's prose/table blocks. It uses only image IDs already included in that authorized lesson response. No filename, lesson ID, course ID, arbitrary URL or copied educational text is hardcoded in React. Valid placed images are excluded from the bottom gallery. Missing anchors/images, unsupported reading layouts and absent metadata retain the gallery fallback rather than hiding images.

Captions are visible figcaptions, separate from alt text. Informative alt text continues to come from the protected lesson image serializer. Enlargement uses the same authenticated blob in a native modal dialog: click/keyboard button, Escape, close button, focus restoration, and theme-aware responsive styling. No second image request or public URL is needed. No animation is required.

## Association plan

The asset manifest now has a `placement.after_section` for each file:

| Lesson order | Asset | After section |
| --- | --- | --- |
| 1 | prompt anatomy | 3. Пять опор визуального запроса |
| 1 | prompt comparison | 4. Слабый и улучшенный запрос |
| 2 | layout hierarchy | 3. Иерархия, композиция и типографика |
| 2 | process infographic | 6. Пошаговая информационная схема без выдуманных данных |
| 3 | style guide | 5. Краткое руководство по стилю |
| 3 | export check | 6. Подготовка файлов для CapCut Desktop |

Preview:

```bash
.venv/bin/python manage.py place_media_module_3_images --dry-run
```

After approval, to associate the existing records:

```bash
.venv/bin/python manage.py place_media_module_3_images --apply
```

The command discovers the course by slug and lessons by module/lesson order/title; resolves already-registered filenames from the manifest; validates ownership/anchors using the Studio serializer; rejects conflicting placements. It adds only the six metadata entries and preserves other teaching interactions. No lesson body, objectives, image file, image record, alt text, assessment, certificate or publication record is changed.

Default preview is read-only. Apply first creates and verifies a private SQLite backup using the existing helper, then repeats checks under an atomic transaction. Only `interactions` is saved on three existing learning-content rows. Repeating exact associations is a no-op. Use a quiet maintenance window; SQLite write contention can require retry. No real apply was performed during implementation. The existing create-only Module 3 content importer intentionally treats later metadata edits as a conflict; do not use it to reset the curriculum.

## Checks

Focused Django tests cover foreign-image rejection, duplicate references, missing anchors, preservation, conflict rejection, idempotency and rollback. Frontend tests cover explicit placement, captions between theory sections, deduplication and fallback. Existing media/session protections are reused unchanged.

Browser checks use isolated saved-content fixtures and mocked authenticated image responses when no safe real session is supplied. They must not be represented as an authenticated live-account test. Actual database association remains pending the explicit apply above.

Implementation files: `studio/serializers.py`; new `courses/management/commands/place_media_module_3_images.py` and `courses/test_media_image_placements.py`; `frontend/src/utils/lessonImagePlacements.js`, `mediaLessonPresentation.js`, `lessonPresentation.js`; `LessonView.jsx`; `MediaLessonReading.jsx` and `mediaLessonReading.css`; `ProtectedLessonImage.jsx`; `LearningContent.jsx`; the Studio `EducationalSections.jsx` metadata-preservation guard; RU/KK/EN enlargement labels; asset-manifest anchors; `frontend/tests/inline-images.test.mjs`.

Validation completed: 59 relevant Django tests, 29 frontend test files, lint, production build and Django system check passed. A real placement dry-run resolved the six registered images and proposed three JSON-field updates, with the SQLite checksum unchanged. No real metadata association was applied.

Native `frontend_reviewer` ran a read-only review; its indistinguishable enlargement-control label finding was fixed by including the image alt description. Native `browser_qa` completed 18 Firefox cases (three lessons, 1440/375/320px, both themes, reduced motion). Two loaded figures and captions per lesson, correct anchors and continued text, no bottom duplicates/overflow, and keyboard enlargement/Escape/focus return passed. No page errors or failed requests were observed. Checks used actual saved educational text/local PNGs with simulated placement metadata and intercepted image responses, not a real authorized session. Screenshots: `.playwright-mcp/inline-module3-{106,107,108}-{1440,375}-{dark,light}.png`.
