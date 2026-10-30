import secrets

from django.db import migrations, models


def _public_id():
    return secrets.token_urlsafe(20)


def backfill_badge_credentials(apps, schema_editor):
    UserAchievement = apps.get_model('learning', 'UserAchievement')
    User = apps.get_model('auth', 'User')
    used = set(
        UserAchievement.objects.exclude(credential_id='').values_list('credential_id', flat=True)
    )
    used_public = set(
        UserAchievement.objects.exclude(public_id='').values_list('public_id', flat=True)
    )
    for row in UserAchievement.objects.select_related('user').all():
        changed = False
        if not row.public_id:
            pid = _public_id()
            while pid in used_public:
                pid = _public_id()
            row.public_id = pid
            used_public.add(pid)
            changed = True
        if not row.credential_id:
            year = row.earned_at.year if row.earned_at else 2026
            while True:
                candidate = f'CY-BDG-{year}-{secrets.token_hex(3).upper()}'
                if candidate not in used:
                    row.credential_id = candidate
                    used.add(candidate)
                    break
            changed = True
        if not row.recipient_name:
            user = row.user
            name = f'{user.first_name} {user.last_name}'.strip() or user.username
            row.recipient_name = name
            changed = True
        if changed:
            row.save(update_fields=['public_id', 'credential_id', 'recipient_name'])


class Migration(migrations.Migration):

    dependencies = [
        ('learning', '0007_remove_xptransaction_unique_xp_award_per_user_action_reference_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='achievement',
            name='category',
            field=models.CharField(
                choices=[
                    ('course', 'Course Completion'),
                    ('chapter', 'Chapter Completion'),
                    ('streak', 'Streak'),
                    ('exercise', 'Exercise Mastery'),
                    ('skill', 'Skill'),
                    ('special', 'Special'),
                    ('excellence', 'Excellence Award'),
                    ('project', 'Project Builder'),
                ],
                default='special',
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name='userachievement',
            name='public_id',
            field=models.CharField(blank=True, default='', max_length=40),
        ),
        migrations.AddField(
            model_name='userachievement',
            name='credential_id',
            field=models.CharField(blank=True, default='', max_length=32),
        ),
        migrations.AddField(
            model_name='userachievement',
            name='recipient_name',
            field=models.CharField(blank=True, default='', max_length=250),
        ),
        migrations.AddField(
            model_name='userachievement',
            name='status',
            field=models.CharField(
                choices=[('active', 'Active'), ('revoked', 'Revoked')],
                default='active',
                max_length=12,
            ),
        ),
        migrations.RunPython(backfill_badge_credentials, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='userachievement',
            name='public_id',
            field=models.CharField(editable=False, max_length=40, unique=True),
        ),
        migrations.AlterField(
            model_name='userachievement',
            name='credential_id',
            field=models.CharField(editable=False, max_length=32, unique=True),
        ),
    ]
