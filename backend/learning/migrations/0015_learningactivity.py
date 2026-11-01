from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('learning', '0014_practicalclass_is_published'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='LearningActivity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('activity_type', models.CharField(choices=[
                    ('course_started', 'Course started'),
                    ('lesson_completed', 'Lesson completed'),
                    ('practical_completed', 'Practical completed'),
                    ('quiz_attempted', 'Quiz attempted'),
                    ('course_completed', 'Course completed'),
                    ('bookmark_created', 'Bookmark created'),
                ], max_length=30)),
                ('title', models.CharField(max_length=250)),
                ('status', models.CharField(default='completed', max_length=30)),
                ('dedupe_key', models.CharField(max_length=180, unique=True)),
                ('activity_date', models.DateField()),
                ('occurred_at', models.DateTimeField(auto_now_add=True)),
                ('course', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='learning_activities', to='learning.course')),
                ('exercise', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='learning_activities', to='learning.exercise')),
                ('lesson', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='learning_activities', to='learning.lesson')),
                ('practical', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='learning_activities', to='learning.practical')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='learning_activities', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-occurred_at'],
                'indexes': [
                    models.Index(fields=['user', 'activity_date'], name='learning_le_user_id_b90ac8_idx'),
                    models.Index(fields=['user', 'activity_type', '-occurred_at'], name='learning_le_user_id_ecde49_idx'),
                ],
            },
        ),
    ]
