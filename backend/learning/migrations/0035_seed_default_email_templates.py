"""Seed the professionally written starter templates into the library.

Idempotent and keyed on ``name``: an existing template is left untouched so a
re-run (or a later deploy against an already-populated database) never
overwrites an administrator's edits or duplicates a row. The forward step
installs the defaults; the reverse step removes only the seeded names so a
rollback cleans up after itself without deleting admin-created templates.
"""

from django.db import migrations


def seed_templates(apps, schema_editor):
    EmailTemplate = apps.get_model('learning', 'EmailTemplate')
    from learning.default_email_templates import DEFAULT_EMAIL_TEMPLATES

    for spec in DEFAULT_EMAIL_TEMPLATES:
        if EmailTemplate.objects.filter(name=spec['name']).exists():
            continue
        EmailTemplate.objects.create(
            name=spec['name'],
            category=spec.get('category', 'Custom Templates'),
            description=spec.get('description', ''),
            subject=spec['subject'],
            heading=spec.get('heading', ''),
            preview_text=spec.get('preview_text', ''),
            body_html=spec.get('body_html', ''),
            plain_text=spec.get('plain_text', ''),
            cta_label=spec.get('cta_label', ''),
            cta_url=spec.get('cta_url', ''),
            footer_content=spec.get('footer_content', ''),
            is_favorite=spec.get('is_favorite', False),
            created_by=None,
        )


def unseed_templates(apps, schema_editor):
    EmailTemplate = apps.get_model('learning', 'EmailTemplate')
    from learning.default_email_templates import DEFAULT_EMAIL_TEMPLATES

    names = [spec['name'] for spec in DEFAULT_EMAIL_TEMPLATES]
    EmailTemplate.objects.filter(name__in=names).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('learning', '0034_emailtemplate'),
    ]

    operations = [
        migrations.RunPython(seed_templates, unseed_templates),
    ]
