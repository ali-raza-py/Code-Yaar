"""Shared helpers for describing board-textbook curricula as data."""

BOARD = 'Sindh Board'

# One learning track groups every board class: LEARN > Tracks > Sindh Board
# Computer Science > Class X / XI / XII.
TRACK = {
    'slug': 'sindh-board',
    'title': 'Sindh Board Computer Science',
    'category': 'school_board',
    'is_published': True,
    'description': (
        'Programming courses built directly from the Sindh Board Computer '
        'Science textbooks (English Medium) for Class X, XI and XII. Every '
        'lesson cites the chapter and page it comes from.'
    ),
    'difficulty': 'beginner',
    'estimated_hours': 0,
    'order': 0,
}


def ref(unit, topic, pages, textbook_class, source_type='official',
        verification='verified'):
    """
    Build the source-reference dict stored on a chapter, lesson or exercise.

    `pages` is the *printed* page number in the textbook, so a learner can open
    the physical book to the same place. `verification` defaults to 'verified'
    because curriculum modules may only ship content that has been read off the
    page; the model's clean() rejects 'official' content that claims otherwise.
    """
    return {
        'source_type': source_type,
        'verification_status': verification,
        'textbook_board': BOARD,
        'textbook_class': textbook_class,
        'textbook_unit': unit,
        'textbook_topic': topic,
        'textbook_pages': pages,
    }
