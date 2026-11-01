"""
Class XII — Computer Science (Advanced Python), Sindh Board.

Infrastructure only, and it will stay that way until the textbook arrives. The
brief is explicit: "If the Class XI or XII source textbooks are not available
in the repository, do not invent their curriculum."

What the owner has told us: Class XII is the advanced continuation of Class XI —
lists, dictionaries and similar data structures — and the book will be supplied
later. That is a *description*, not a syllabus, so nothing is recorded as an
official topic and no lessons exist.

When the PDF lands, verify it unit by unit exactly the way Class X was
(textbooks/CLASS-X-SOURCE-VERIFICATION.md documents the method), then replace
this shell with a real curriculum module.
"""

from .common import TRACK  # noqa: F401  (re-exported for the seed command)

COURSE_SLUG = 'sindh-board-class-xii-python'

COURSES = [
    {
        'slug': COURSE_SLUG,
        'title': 'Class XII — Computer Science (Advanced Python)',
        'subtitle': 'Sindh Board, English Medium',
        'description': (
            'Advanced Python for Class XII, following the Sindh Board Computer '
            'Science textbook.\n\n'
            'Awaiting the textbook. Class XII builds on Class XI (lists, '
            'dictionaries and further data structures), but the printed book '
            'has not been supplied or verified yet, so there are no lessons. '
            'Nothing is published as board syllabus until it has been read off '
            'the page.'
        ),
        'difficulty': 'advanced',
        'language': 'python',
        'instructor': '',
        'prerequisites': 'Class XI — Computer Science (Python).',
        'learning_objectives': [],
        'is_free': True,
        'is_published': False,   # draft until the textbook is provided and verified
        'order': 3,
        'chapters': [],          # deliberately empty — nothing invented
    },
]
