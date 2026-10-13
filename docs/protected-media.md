# Protected lesson media

`MEDIA_ROOT` remains the existing `media/` directory. It is **private storage**
for lesson images and student submissions. No files or database paths were moved.

- React loads `GET /api/lesson-images/<image-id>/` through the existing JWT API
  client, then displays a temporary blob URL. The lesson API exposes this endpoint,
  never a public storage URL.
- The file endpoint uses the same Enrollment / authorized staff-preview rule as
  lesson content. Pending or rejected requests alone do not grant access.
- `MEDIA_URL` is `/api/private-media/`. Existing Django FileField/Admin links use
  this authenticated endpoint. Only registered lesson images are served; unrelated
  files and student submissions are denied. Admin previews can use their existing
  session; React uses JWT. Responses are private and must not be cached.
- `/media/` serves only `PUBLIC_MEDIA_ROOT` (`public-media/`) in development.
  Lesson/submission namespaces, traversal, escaping symlinks, and overlapping
  public/private roots are rejected. Current course artwork is bundled frontend
  content, not a Course cover upload field. Future intentionally public covers can
  be placed in the separate public directory.

## Production deployment requirements

Do **not** configure Nginx, Apache, a CDN, or any other service to serve `MEDIA_ROOT`
or the repository root directly. Remove any old `/media/` alias to `media/`, deny
access to lesson/submission directories, and invalidate cached private files if
previously exposed. Proxy `/api/lesson-images/` and `/api/private-media/` to Django
with Authorization headers intact and caching disabled.

If public images are served by the web server, map `/media/` exclusively to
`PUBLIC_MEDIA_ROOT`, keeping it separate from private uploads. Do not put private
files or links to them there.

The current protected endpoint reads local files from `MEDIA_ROOT`. Do not replace
the default upload storage with a public S3/CDN backend or a public storage URL.
A future remote storage integration requires a private bucket and an authenticated
delivery implementation before enabling it. No production web-server or remote
storage configuration currently exists in this repository.

Uploaded files must be preserved outside the publicly served frontend/static build.
An infrastructure administrator must verify these rules on the actual deployment;
Django cannot prevent a separately configured public file server from bypassing it.
