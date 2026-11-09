from django.db import migrations


def seed_themes_and_automations(apps, schema_editor):
    EmailTheme = apps.get_model('learning', 'EmailTheme')
    EmailAutomationRule = apps.get_model('learning', 'EmailAutomationRule')
    from learning.default_email_themes import DEFAULT_EMAIL_THEMES
    from learning.default_email_automations import DEFAULT_EMAIL_AUTOMATIONS

    for spec in DEFAULT_EMAIL_THEMES:
        EmailTheme.objects.get_or_create(
            slug=spec['slug'],
            defaults={
                'name': spec['name'],
                'description': spec.get('description', ''),
                'best_for': spec.get('best_for', ''),
                'primary_color': spec.get('primary_color', '#073D32'),
                'accent_color': spec.get('accent_color', '#087F68'),
                'highlight_color': spec.get('highlight_color', '#A9EDCC'),
                'background_color': spec.get('background_color', '#FFFFFF'),
                'is_default': spec.get('is_default', False),
            },
        )

    for spec in DEFAULT_EMAIL_AUTOMATIONS:
        EmailAutomationRule.objects.get_or_create(
            trigger=spec['trigger'],
            defaults={
                'name': spec['name'],
                'description': spec.get('description', ''),
                'enabled': spec.get('enabled', True),
                'theme': spec.get('theme', 'emerald-signature'),
                'recipient_group': spec.get('recipient_group', 'trigger_recipient'),
            },
        )


def unseed(apps, schema_editor):
    EmailTheme = apps.get_model('learning', 'EmailTheme')
    EmailAutomationRule = apps.get_model('learning', 'EmailAutomationRule')
    from learning.default_email_themes import DEFAULT_EMAIL_THEMES
    from learning.default_email_automations import DEFAULT_EMAIL_AUTOMATIONS
    EmailTheme.objects.filter(slug__in=[s['slug'] for s in DEFAULT_EMAIL_THEMES]).delete()
    EmailAutomationRule.objects.filter(trigger__in=[s['trigger'] for s in DEFAULT_EMAIL_AUTOMATIONS]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('learning', '0036_emailtheme_emailtemplate_theme_emailautomationrule'),
    ]

    operations = [
        migrations.RunPython(seed_themes_and_automations, unseed),
    ]