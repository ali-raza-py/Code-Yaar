"""Reorganize language-oriented tracks into learner-facing tracks.

Turns the former per-language tracks (Python, C++, CS Fundamentals, duplicate
Developer Tools) into a small set of discovery tracks that group courses by
what a learner is pursuing:

    Sindh Board Computer Science  (school_board)  Class X / XI / XII courses
    Programming Fundamentals      (programming)   Python, C++, DSA
    Web Development               (web)           HTML/CSS/JavaScript
    Developer Tools               (other)         Git & GitHub
    Artificial Intelligence       (ai)            created unpublished — the
                                                  admin adds courses before
                                                  publishing it

Courses are MOVED between tracks (never deleted, never duplicated), so every
enrollment, lesson-progress row, attempt and certificate keeps its FK chain.
Vacated tracks are removed only when they hold no courses. Idempotent: safe to
re-run, and a no-op on a fresh database where the old slugs never existed.
"""

from django.db import migrations

# Old track slug -> where its courses land after the reorganization.
COURSE_MOVES = {
    'python': 'core-programming',
    'cpp': 'core-programming',
    'fundamentals': 'core-programming',
    'tools': 'developer-tools',
}

# Recommended sequence within the merged programming track (by course slug);
# anything else is appended after these by title.
PROGRAMMING_ORDER = {
    'python-foundations': 1,
    'cpp-fundamentals': 2,
    'problem-solving-dsa': 3,
}

# Track copy mirroring the content that actually exists in the catalogue.
TRACKS = {
    'sindh-board': {
        'title': 'Sindh Board Computer Science',
        'category': 'school_board',
        'difficulty': 'beginner',
        'order': 0,
        'is_published': True,
        'description': (
            'Programming courses built directly from the Sindh Board Computer '
            'Science textbooks (English Medium) for Class X, XI and XII. Every '
            'lesson cites the chapter and page it comes from, so what you '
            'practice on screen always matches what you read in class.'
        ),
        'learning_objectives': [
            'Follow the board syllabus class by class: C++ in Class X, Python in Classes XI and XII.',
            'Write, compile and run exam-relevant programs with confidence.',
            'Revise with textbook-cited lessons, exercises and lab activities.',
            'Earn verifiable Code Yaar certificates for each completed class course.',
        ],
    },
    'core-programming': {
        'title': 'Programming Fundamentals',
        'category': 'programming',
        'difficulty': 'beginner',
        'order': 1,
        'is_published': True,
        'description': (
            'Start with Python, continue with C++, then sharpen the problem-'
            'solving and data-structure skills every language builds on. '
            'Languages are lessons inside this track, not separate destinations.'
        ),
        'learning_objectives': [
            'Write, run and debug programs in Python and C++.',
            'Use variables, control flow, functions, strings and lists fluently.',
            'Apply core data structures and algorithms to unfamiliar problems.',
            'Reason about Big-O and compare two working solutions.',
        ],
    },
    'web': {
        'title': 'Web Development',
        'category': 'web',
        'difficulty': 'beginner',
        'order': 2,
        'is_published': True,
        'description': (
            'Build modern websites from structure to interactivity — HTML, '
            'CSS and JavaScript taught as one continuous path.'
        ),
        'learning_objectives': [
            'Structure pages with valid, semantic HTML.',
            'Style layouts with CSS selectors, the box model and flexbox.',
            'Make pages interactive with JavaScript and the DOM.',
            'Assemble a multi-section portfolio page from scratch.',
        ],
    },
    'developer-tools': {
        'title': 'Developer Tools',
        'category': 'other',
        'difficulty': 'beginner',
        'order': 3,
        'is_published': True,
        'description': (
            'The everyday tools of real software work: version control, '
            'collaboration and shipping code with a team.'
        ),
        'learning_objectives': [
            'Track, stage and commit changes with Git.',
            'Collaborate on GitHub with branches, forks and pull requests.',
            'Inspect and rewrite history safely with log, diff and revert.',
        ],
    },
    # Deliberately unpublished until real courses exist — an empty shelf is
    # never shown to learners (the Tracks page hides tracks without courses).
    'artificial-intelligence': {
        'title': 'Artificial Intelligence',
        'category': 'ai',
        'difficulty': 'intermediate',
        'order': 4,
        'is_published': False,
        'description': (
            'A structured path into AI — from Python for AI to machine '
            'learning and generative AI. Courses appear here as they are '
            'built and published.'
        ),
        'learning_objectives': [],
    },
}

# Board-course class labels so track pages can group by CLASS X / XI / XII.
ACADEMIC_CLASSES = {
    'sindh-board-class-x-cpp': 'Class X',
    'sindh-board-class-xi-python': 'Class XI',
    'sindh-board-class-xii-python': 'Class XII',
}


def reorganize(apps, schema_editor):
    CareerTrack = apps.get_model('learning', 'CareerTrack')
    Course = apps.get_model('learning', 'Course')
    Project = apps.get_model('learning', 'Project')
    Certification = apps.get_model('learning', 'Certification')

    for slug, spec in TRACKS.items():
        track = CareerTrack.objects.filter(slug=slug).first()
        if track is None:
            track = CareerTrack.objects.create(slug=slug, **spec)
            continue
        for field, value in spec.items():
            setattr(track, field, value)
        track.save()

    # Move every course out of the vacated language tracks into its new home.
    for old_slug, new_slug in COURSE_MOVES.items():
        old = CareerTrack.objects.filter(slug=old_slug).first()
        if old is None:
            continue
        new = CareerTrack.objects.get(slug=new_slug)
        for course in old.courses.all():
            course.track = new
            course.save(update_fields=['track'])
        # Re-point anything else that referenced the old track.
        Project.objects.filter(track=old).update(track=new)
        Certification.objects.filter(track=old).update(track=new)
        if not old.courses.exists():
            old.delete()

    # Sequence the merged programming track: Python -> C++ -> DSA.
    programming = CareerTrack.objects.filter(slug='core-programming').first()
    if programming is not None:
        remaining = 10
        for course in programming.courses.order_by(
            'order', 'title'
        ):  # stable base order
            target = PROGRAMMING_ORDER.get(course.slug)
            if target is not None:
                remaining = max(remaining, target + 1)
                course.order = target
            else:
                course.order = remaining
                remaining += 1
            course.save(update_fields=['order'])

    # Label the board courses with their academic class.
    for course_slug, label in ACADEMIC_CLASSES.items():
        Course.objects.filter(slug=course_slug).update(academic_class=label)

    # Give every remaining track a sensible category/publish state so the new
    # learner-facing listing never shows a half-configured track.
    for track in CareerTrack.objects.all():
        changed = False
        if not track.category:
            track.category = 'other'
            changed = True
        if track.slug not in TRACKS:
            published = track.courses.filter(
                is_active=True, is_published=True
            ).exists()
            if track.is_published != published:
                track.is_published = published
                changed = True
        if changed:
            track.save()


def noop(apps, schema_editor):
    """Reversing this restructure would duplicate track history; leave data."""


class Migration(migrations.Migration):

    dependencies = [
        ('learning', '0013_careertrack_category_careertrack_cover_image_and_more'),
    ]

    operations = [
        migrations.RunPython(reorganize, noop),
    ]
