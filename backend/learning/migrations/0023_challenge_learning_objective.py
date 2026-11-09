from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('learning', '0022_notificationemaillog_usernotification_category_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='challenge',
            name='learning_objective',
            field=models.TextField(
                blank=True,
                default='',
                help_text='What the learner practices by completing this challenge',
            ),
        ),
    ]
