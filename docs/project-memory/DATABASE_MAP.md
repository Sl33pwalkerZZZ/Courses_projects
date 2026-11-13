# Database Map

**Evidence date:** 2026-11-09. This is a schema/relationship guide plus explicitly dated aggregate inventory, not current operational state. No learner-specific records are documented here.

## Main curriculum graph

```text
users.User (author)
  └─ courses.Course
       ├─ courses.Module (ordered)
       │    └─ courses.Lesson (ordered; text_content)
       │         ├─ courses.LessonLearningContent (optional JSON objectives/sections/interactions)
       │         ├─ courses.LessonImage (protected instructional image)
       │         ├─ courses.LessonAttachment (audio/SRT/VTT/video)
       │         │    └─ courses.LessonPlaybackGrant (scoped/revocable playback)
       │         ├─ courses.Assignment
       │         └─ quizzes.Quiz (one-to-one, optional)
       ├─ progress.Enrollment / EnrollmentRequest
       ├─ reviews.CourseReview
       └─ certificates.CourseCertificatePolicy / Certificate
```

## Ownership and behavior

- `Course` belongs to an author and has ordered modules. `Module` has ordered lessons. Lesson text is stored on `Lesson`; structured teaching metadata is optional `LessonLearningContent` JSON. There are no separate module/lesson description fields in the audited schema.
- `EnrollmentRequest` is the pending/approved/rejected application lifecycle. A uniqueness rule prevents multiple pending applications for a student/course. Approval is atomic and creates or reuses one `Enrollment`; rejection history remains.
- `LessonProgress` is attached to enrollment and lesson, unique for that pair. Lesson completion is separate from quiz pass/fail and assignment review.
- `AssignmentSubmission` belongs to assignment/student and stores draft/submission/review status, reviewer/feedback/timestamps and review history. Do not treat historical submissions as approved without attributable evidence.
- `QuizAttempt` and `QuizAnswer` store server-calculated scores plus snapshots for stable later feedback. Correct-answer data is backend-side; the public quiz serializer does not send correct flags before submission.
- `CourseCertificatePolicy` configures requirements. `Certificate` stores an opaque verification identifier and issue-time snapshots; eligibility/issue/revoke services are the authoritative boundary. The audit found a policy for Course 8 and none for Course 10.
- `CourseImport`, Studio publication records/settings and image-description records support import and editorial workflows.

## App ownership

| App | Primary records |
|---|---|
| `users` | Custom user and role fields |
| `courses` | Course/curriculum/content, media metadata and import receipts |
| `progress` | Enrollment, requests, lesson progress and assignment submissions/reviews |
| `quizzes` | Quiz structure, attempts and answer snapshots |
| `certificates` | Policy, issued certificates, revocation/verification data |
| `reviews` | Course reviews and moderation state |
| `studio` | Course settings, import previews, publication requests/events and studio-only support data |

## Database safety

SQLite is the configured local database. The audits intentionally did not include credentials, learner rows, quiz answers, attempts or certificate-holder details in this map. Do not open/copy/reset the local database for routine documentation. For authorized data work, use read-only connections for inspection, verify backups before writes, use isolated test databases, and keep learner information out of output.

The aggregate snapshot in [the course audit](../project-audit/02-course-content-and-database-audit.md) recorded 10 courses, 38 modules, 114 lessons; it also records quiz/assignment counts without answer or learner data. It is a dated local development snapshot, not a production assertion.
