# Optional lesson quizzes

Quizzes use separate records and do not complete lessons, change enrollments,
or contribute to Profile learning activity. The existing lesson completion
button remains independent of quiz scores.

## Migration awaiting review

`quizzes.0001_initial` creates `Quiz`, `QuizQuestion`, `QuizChoice`,
`QuizAttempt`, and `QuizAnswer` tables. It adds seven constraints covering
passing percentages, question types, score/count ranges, unique submissions,
and one submitted answer per question. The one-to-one lesson relation allows
at most one quiz per lesson. No curriculum data is created or updated, and
there are no data migrations or changes to existing tables.

This migration has **not** been applied to the development database.
Review it and back up that database before applying
`python manage.py migrate quizzes`. Tests apply it only to Django's temporary test database. The quiz
API/Admin require the new tables before they can be used in development.

## Authoring in Django Admin

1. Add a Quiz, select an existing lesson, enter a title/instructions and a
   passing percentage from 0 to 100. Save it as a draft.
2. Add questions through Quiz questions (or the draft quiz's question inline).
   On each question's edit page, set its type, order, optional explanation,
   and at least two ordered choices. Mark exactly one correct choice for a
   single-choice question, or at least one for a multiple-select question.
3. Return to the Quiz and check `is_published`. Incomplete or invalid questions
   prevent publication. Published quiz content is also checked by the API.
4. Unpublish before editing/deleting questions or choices, then republish.
   Existing attempts retain their question, choice, explanation and threshold
   snapshots. A quiz with attempts cannot be moved to another lesson or deleted
   through Admin. Attempts and their submitted answers are read-only in Admin.

Administrators use existing Django model permissions; there are no new roles.
The lesson selector links to existing lessons without editing their content.

## Student APIs

All endpoints require JWT authentication and an actual Enrollment for the
lesson's course. Staff privileges or display roles do not bypass this quiz
requirement. Existing staff lesson-preview permissions are unchanged.

- `GET /api/lessons/<lesson_id>/quiz/`: `{quiz: null}` when there is no
  published quiz. Otherwise returns title, instructions, passing percentage,
  ordered questions and choices, with no correct flags or explanations.
- `POST /api/lessons/<lesson_id>/quiz/attempts/`: accepts the JSON below,
  and returns a server-calculated score, pass/fail result, timestamp, and
  per-question feedback with selected/correct choices and explanations.
- `GET /api/lessons/<lesson_id>/quiz/attempts/?page=1`: student-owned history
  in pages of 10, with `count`, `next`, `previous`, `results`, `latest` and `best`.
- `GET /api/quiz-attempts/<attempt_id>/`: this student's saved feedback only.
  Other students' IDs return 404; no update/delete API is provided.

```json
{
  "submission_id": "a-client-generated-UUID",
  "answers": [
    {"question_id": 123, "choice_ids": [456]}
  ]
}
```

Every question must have a nonempty answer. Single-choice answers contain
exactly one choice. All IDs must belong to the correct quiz/question;
duplicate IDs, unknown fields and malformed values are rejected. Each question
has equal weight. Multiple-select answers receive credit only for the exact
correct set. Scores display two decimal places; passing uses the exact ratio
against the configured percentage, including the valid boundaries 0 and 100.

Use a new submission UUID for an intentional new attempt. Repeating the same
UUID and answers returns the saved attempt (200 instead of 201), without
changing its timestamp. Changed answers with the same UUID return 409.
Submission and answer storage are atomic, with a database uniqueness guard.
The frontend blocks double-clicks and retains the UUID after a failed response.

## Manual check after migration approval

- Create and publish a quiz on an existing lesson using Admin, without editing
  the lesson or course. Include both question types.
- Sign in as an enrolled student. The knowledge check appears after lesson
  material. Answer questions, navigate backward/forward, review, then confirm.
- Check correct/incorrect feedback, score and pass status. Retry to create a
  second attempt; reload and check latest/best scores and previous feedback.
- Use a pending/rejected applicant and an anonymous session to confirm that
  protected lesson/quiz content remains inaccessible.
- Mark a lesson complete independently and check Profile activity. Quiz
  attempts alone must not add activity or completed lessons.
- Check RU/KK/EN, both themes, keyboard radio/checkbox/navigation controls,
  phone layouts and reduced motion. Authored question text is not translated.
- Simulate a failed quiz/history/submission request in browser tools and use
  the focused retry. The lesson material and completion button remain usable.

## Validation commands

```sh
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
cd frontend
npm run lint
node --test tests/*.test.mjs
npm run build
```
