"""
Class X — Computer Science (C++), Sindh Board, English Medium.

Scope is the textbook's four programming units only:

    Unit 2  Basics of Programming in C++      (printed pp. 20-47)
    Unit 3  Input/Output Handling in C++      (printed pp. 48-69)
    Unit 4  Control Structure                 (printed pp. 70-92)
    Unit 5  Functions                         (printed pp. 93-106)

Unit 1 (Problem Solving and Algorithm Designing), Unit 6 (Digital Logic) and
Unit 7 (Introduction to Scratch) are part of the same exam paper but are not
programming lessons, so they are deliberately not turned into a C++ course.

Everything here was read off the scanned textbook page by page and recorded in
textbooks/CLASS-X-SOURCE-VERIFICATION.md before it was written. Nothing in this
course is invented: each chapter, lesson and exercise carries the unit, printed
topic name and page numbers it came from, and anything that goes beyond the
book is labelled supplementary or additional.
"""

from .common import TRACK  # noqa: F401  (re-exported for the seed command)
from . import class_x_unit2, class_x_unit3, class_x_unit4, class_x_unit5

COURSE_SLUG = 'sindh-board-class-x-cpp'

COURSES = [
    {
        'slug': COURSE_SLUG,
        'title': 'Class X — Computer Science (C++)',
        'subtitle': 'Sindh Board, English Medium · Units 2-5',
        'description': (
            'Learn C++ the way the Sindh Board teaches it, from the first '
            '`cout` to writing your own functions.\n\n' 'This course covers the four programming units of the Class X Computer '
            'Science textbook (English Medium): Basics of Programming in C++, '
            'Input/Output Handling, Control Structure and Functions. Every '
            'lesson names the exact textbook topic and page it comes from, and '
            'every code sample is compiled and run for real by the sandbox — '
            'nothing here pretends to have executed.'
        ),
        'difficulty': 'beginner',
        'language': 'cpp',
        'instructor': '',
        'prerequisites': (
            'No programming experience needed. Unit 2 starts with what a '
            'computer program is. Basic school algebra helps for the formula '
            'practicals.'
        ),
        'learning_objectives': [
            'Explain how a C++ program is written, translated and run',
            'Declare variables and constants using the correct C++ data types',
            'Write programs that read input with cin and print output with cout',
            'Use arithmetic, relational, logical and assignment operators correctly',
            'Control program flow with if, else-if, switch, for, while and do-while',
            'Write, declare and call your own functions with and without return values',
            'Tell syntax, run-time and logic errors apart and fix them',
        ],
        'is_free': True,
        'is_published': True,
        'order': 1,
        'chapters': [
            class_x_unit2.CHAPTER,
            class_x_unit3.CHAPTER,
            class_x_unit4.CHAPTER,
            class_x_unit5.CHAPTER,
        ],
    },
]
