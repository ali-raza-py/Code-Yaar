"""
Class XI — Computer Science (Python), Sindh Board, English Medium.

Scope is the textbook's programming unit only:

    Unit 3  Programming Fundamentals (Python)   (printed pp. 91-138)

Units 1, 2 and 4-6 (Computer Systems, Computational Thinking, Data and
Analysis, Applications and Impacts, Digital Literacy) are general CS theory,
not programming lessons — matching how Class X covers only its programming
units.

Everything here was read off the scanned textbook page by page and recorded
in textbooks/CLASS-XI-SOURCE-VERIFICATION.md before it was written. Nothing
in this course is invented: each chapter, lesson and exercise carries the
unit, printed topic name and page numbers it came from, and anything that
goes beyond the book is labelled supplementary or additional.

Sandbox honesty: random/datetime material (the Report Card activity, the
guess-the-number game as printed) is taught as samples and reasoning items
and is never auto-graded by output comparison; where a book activity is
graded, the secret values are pinned down deterministically.
"""

from .common import TRACK  # noqa: F401  (re-exported for the seed command)
from . import (
    class_xi_intro,
    class_xi_io_operators,
    class_xi_control_structures,
    class_xi_libraries_debugging,
)

COURSE_SLUG = 'sindh-board-class-xi-python'

COURSES = [
    {
        'slug': COURSE_SLUG,
        'title': 'Class XI — Computer Science (Python)',
        'subtitle': 'Sindh Board, English Medium · Unit 3',
        'description': (
            'Learn Python the way the Sindh Board teaches it, from the first '
            '`print()` to a working ATM simulation.\n\n'
            'This course covers Unit 3 — Programming Fundamentals — of the '
            'Class XI Computer Science textbook (English Medium): what '
            'programming and IDEs are, variables and data types, input and '
            'output, all six operator families, control structures, '
            'libraries and debugging. Every lesson names the exact textbook '
            'topic and page it comes from, and every code sample runs for '
            'real in the sandbox — nothing here pretends to have executed.'
        ),
        'difficulty': 'intermediate',
        'language': 'python',
        'instructor': '',
        'prerequisites': (
            'Class X Computer Science (C++) or equivalent programming '
            'basics. The first lessons review general programming ideas, so '
            'a confident self-taught beginner can also start here.'
        ),
        'learning_objectives': [
            'Explain what a program, a programming language and an IDE are',
            'Name Python data types and create variables following the board\'s naming rules',
            'Read input with input() and convert strings to int and float correctly',
            'Use arithmetic, assignment, relational, logical, membership and bitwise operators',
            'Control program flow with if, if-else, if-elif-else, nested if, for, while, break and continue',
            'Import libraries in the five textbook ways and use math, random and datetime',
            'Install third-party libraries with pip and name Numpy, Pandas and Matplotlib',
            'Tell syntax, runtime and logical errors apart and read a traceback',
            'Build complete programs: a calculator, a number-guessing game and an ATM simulation',
        ],
        'is_free': True,
        'is_published': True,   # Unit 3 verified page-by-page; all solutions sandbox-tested
        'order': 2,
        'chapters': [
            class_xi_intro.CHAPTER_INTRO,
            class_xi_intro.CHAPTER_IDE,
            class_xi_io_operators.CHAPTER_IO_OPS,
            class_xi_control_structures.CHAPTER_CONTROL,
            class_xi_libraries_debugging.CHAPTER_LIBS_DEBUG,
        ],
    },
]
