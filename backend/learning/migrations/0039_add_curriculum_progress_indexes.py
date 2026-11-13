# Adds composite indexes on the hot curriculum/progress filter columns so the
# course, chapter, lesson and progress lookups served over the hosted Postgres
# link can use index scans instead of table scans. Additive only: no columns,
# tables, or data are removed or altered.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('learning', '0038_userprofile_first_login_at'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='chapter',
            index=models.Index(
                fields=['course', 'is_active', 'order'],
                name='chap_course_active_order',
            ),
        ),
        migrations.AddIndex(
            model_name='lesson',
            index=models.Index(
                fields=['chapter', 'is_active', 'order'],
                name='lesson_chapter_active_order',
            ),
        ),
        migrations.AddIndex(
            model_name='exercise',
            index=models.Index(
                fields=['lesson', 'is_active'],
                name='exercise_lesson_active',
            ),
        ),
        migrations.AddIndex(
            model_name='lessonprogress',
            index=models.Index(
                fields=['user', 'status'],
                name='lesson_progress_user_status',
            ),
        ),
        migrations.AddIndex(
            model_name='exerciseattempt',
            index=models.Index(
                fields=['user', 'exercise', 'status'],
                name='exercise_attempt_user_status',
            ),
        ),
        migrations.AddIndex(
            model_name='enrollment',
            index=models.Index(
                fields=['user', 'course', 'status'],
                name='enroll_user_course_status',
            ),
        ),
    ]
