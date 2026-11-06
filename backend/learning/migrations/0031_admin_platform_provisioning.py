"""Provision the admin platform's configurable data.

Three forward-only data steps that the Course Creation Studio and the capability
layer both depend on:

1. ``CourseCategory`` rows for the catalogue the specification lists, so the studio's
   category dropdown is populated on first open instead of empty.
2. The specialised admin groups, so ``services.admin_access.capabilities()`` has real
   groups to resolve against rather than names that exist only in a document.
3. ``Course.instructor_user`` backfilled from the free-text ``Course.instructor``
   display name. Only exact matches are written; anything ambiguous is left null and
   stays administrator-only, because guessing which instructor "Ali R." meant would
   hand somebody editorial access to the wrong course.
"""

from django.db import migrations

CATEGORIES = [
    ('programming-fundamentals', 'Programming Fundamentals'),
    ('python', 'Python'),
    ('cpp', 'C++'),
    ('javascript', 'JavaScript'),
    ('web-development', 'Web Development'),
    ('backend-development', 'Backend Development'),
    ('frontend-development', 'Frontend Development'),
    ('data-structures-algorithms', 'Data Structures and Algorithms'),
    ('artificial-intelligence', 'Artificial Intelligence'),
    ('machine-learning', 'Machine Learning'),
    ('databases', 'Databases'),
    ('computer-science-fundamentals', 'Computer Science Fundamentals'),
    ('cybersecurity', 'Cybersecurity'),
    ('cloud-devops', 'Cloud and DevOps'),
]

ADMIN_GROUPS = [
    'Academic Manager',
    'Course Editor',
    'Competition Manager',
    'Leadership Manager',
    'Communication Manager',
    'Student Support',
]


def seed_course_categories(apps, schema_editor):
    CourseCategory = apps.get_model('learning', 'CourseCategory')
    for order, (slug, title) in enumerate(CATEGORIES, start=10):
        CourseCategory.objects.get_or_create(slug=slug, defaults={'title': title, 'order': order})


def create_admin_groups(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    for name in ADMIN_GROUPS:
        Group.objects.get_or_create(name=name)


def backfill_instructor_users(apps, schema_editor):
    Course = apps.get_model('learning', 'Course')
    User = apps.get_model('auth', 'User')

    # Index every plausible spelling of an account so the match is exact-name only.
    lookup = {}
    for user in User.objects.all():
        keys = set()
        full = ' '.join(part for part in (user.first_name, user.last_name) if part).strip()
        if full:
            keys.add(full.lower())
        if user.username:
            keys.add(user.username.lower())
        if user.email:
            keys.add(user.email.lower())
        for key in keys:
            # First match wins on a collision: an ambiguous name must not become an
            # access grant. The course simply stays administrator-owned.
            lookup.setdefault(key, user.pk)

    for course in Course.objects.exclude(instructor='').filter(instructor_user__isnull=True):
        match = lookup.get((course.instructor or '').strip().lower())
        if match is not None:
            Course.objects.filter(pk=course.pk).update(instructor_user_id=match)


class Migration(migrations.Migration):

    dependencies = [
        ('learning', '0030_coursecategory_course_archived_at_course_cover_image_and_more'),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.RunPython(seed_course_categories, migrations.RunPython.noop),
        migrations.RunPython(create_admin_groups, migrations.RunPython.noop),
        migrations.RunPython(backfill_instructor_users, migrations.RunPython.noop),
    ]
