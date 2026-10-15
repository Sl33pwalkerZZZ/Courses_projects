# Accessible lesson images without a database migration

The protected lesson API now includes `images[].alt_text`, a mapping of authored
alternatives by language (`en`, `ru`, `kk`). The existing image-ID endpoint, JWT
loading, enrollment checks, and temporary blob URLs are unchanged.

Descriptions can be supplied in the optional UTF-8 JSON file configured by
`LESSON_IMAGE_DESCRIPTIONS_FILE`, defaulting to the private
`media/lesson-image-descriptions.json`. No metadata file or content entries are
created by this change. The course-content maintainer can later author entries:

```json
{
  "123": {
    "en": "An author-written description of the informative image.",
    "ru": "Авторское описание информативного изображения.",
    "kk": "Ақпараттық суреттің автор жазған сипаттамасы."
  },
  "124": {}
}
```

Keys are real LessonImage IDs, not lesson IDs or file paths. An empty object marks
a decorative image. Missing/blank entries preserve the previous `alt=""` behavior;
informative images require a maintained description. Descriptions are never
generated from filenames or copied from lesson titles. Provide concise alternatives
that convey the image's relevant information; describe complex diagrams in lesson
content as appropriate.

React uses the current language and falls back to an available authored alternative
(English first), setting `lang` for correct screen-reader pronunciation. Switching
languages does not reload the protected image. Keep this metadata out of public
assets; it is exposed only through authorized lesson responses.

The file is read once per lesson response, so updates need no application restart.
A missing file is optional. Invalid/unreadable JSON produces a generic server
warning and empty alternatives rather than breaking lesson access. Invalid entries
and unsupported languages are ignored. Keep the JSON valid when deploying updates.

This is a file-based authoring option, not a Django Admin editor. A future Admin
description field would require a deliberate schema change. Existing courses,
lessons, records and image files are not rewritten.
