# Student progress tracking

## Data model

Existing enrollment, lesson progress, exercise attempts, and practical progress
remain the authoritative completion records. `LearningActivity` is the
cross-content ledger for meaningful events:

- `course_started`
- `lesson_completed`
- `practical_completed`
- `quiz_attempted`
- `course_completed`
- `bookmark_created`

Each activity belongs to the authenticated user and has a unique daily
deduplication key. It is indexed by user/date and user/type/time. No client
percentage or user ID is accepted by the progress API.

## API

`GET /api/progress/` requires authentication and returns:

- `overview`: course, lesson, practical, assessment, learning-time, and streak
  totals.
- `courses`: enrolled-course lesson progress and last access timestamps.
- `subjects` and `classes`: published practical completion percentages.
- `weekly_activity`: meaningful activity counts for the last seven local days.
- `quiz_performance`: final-assessment attempt scores (100 for a passed attempt,
  0 otherwise).
- `contribution_data`: 365 local-calendar dates with lesson, practical, quiz,
  total activity counts, and a 0-4 intensity level. Missing dates are returned
  with zeroes so clients can render a complete GitHub-style grid without
  fetching individual activity records.
- `total_learning_activities` and `active_learning_days`: totals for the same
  365-day contribution window.
- `activities`: recent activity history.
- `active_dates`: dates used by the streak calendar.
- `insights`: server-calculated learner guidance.

Activity history accepts optional `type`, `from`, and `to` query parameters.
All records are scoped to `request.user`.

## Calculation rules

Course progress is completed active lessons divided by active lessons in the
enrolled course. A course is completed only by the existing server-side course
completion service. Assessment metrics use exercises marked
`is_final_assessment`; opening an assessment does not create an attempt.

Contribution totals and streaks include only lesson completions, practical
completions, quiz attempts, and course completions. Course starts and
bookmarks remain available in the ledger but do not represent learning
activity. Dates use Django's configured timezone, and multiple events on one
date count as one learning day for streaks. The current streak can end today
or yesterday, so a learner does not lose a streak before the current day is
over.

## Frontend

The authenticated `/progress` route is linked from the dashboard and sidebar.
It renders real API data for overview cards, green course/practical bars,
weekly activity, quiz performance, a responsive 12-month contribution graph,
insights, and filtered activity history. Empty, loading, and API error states
are included. Contribution cells are keyboard focusable and expose their full
date and category counts through accessible labels.

## Tests

Run focused progress tests:

```powershell
cd backend
python manage.py test learning.tests.ProgressDashboardAPITest
```

Run backend checks:

```powershell
python manage.py check
python manage.py makemigrations --check
```
