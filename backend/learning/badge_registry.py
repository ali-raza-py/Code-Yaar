"""Centralized badge registry: the single source of truth for achievements.

Every badge definition lives here — ID/slug, name, description, icon,
category, difficulty, XP bonus, unlock condition, and the learner-facing
"how to earn" guidance. ``manage.py seed_badges`` materializes this list as
``Achievement`` rows idempotently; nothing else may create badges, and no
badge is ever displayed as completed without the server verifying the
underlying activity rows (see ``services/achievements.py``).

Condition vocabulary (handled by the award engine):
- ``lesson_complete``         completed lessons >= value
- ``chapter_complete``        all lessons of any one chapter completed
- ``course_complete``         completed enrollments >= value (0 = any)
- ``exercise_correct_count``  distinct exercises passed >= value
- ``challenge_count``         distinct challenges solved >= value
- ``challenge_topic_count``   distinct challenges solved in topic >= value
- ``streak_n`` / ``streak_7`` current streak days >= n (streak_7 kept for
                              rows seeded before the generalised mode)
- ``first_activity``          any verified learning activity at all
- ``account``               registered on the platform
- ``project_course_complete`` completed courses in tracks that offer projects
"""

# Difficulty taxonomy shared with courses, tracks, challenges and exercises:
# beginner = green, intermediate = orange, advanced = red (frontend tokens).
BEGINNER = 'beginner'
INTERMEDIATE = 'intermediate'
ADVANCED = 'advanced'

BADGES = [
    # ── Learning achievements ────────────────────────────────────────────
    {
        'slug': 'first-lesson', 'title': 'First Steps',
        'description': 'Complete your first lesson.',
        'icon': 'trophy', 'category': 'course', 'difficulty': BEGINNER,
        'xp_bonus': 50,
        'condition_type': 'lesson_complete', 'condition_value': '1',
        'how_to_earn': 'Open any course and finish one lesson.',
    },
    {
        'slug': 'quick-learner', 'title': 'Quick Learner',
        'description': 'Complete five lessons.',
        'icon': 'star', 'category': 'course', 'difficulty': BEGINNER,
        'xp_bonus': 100,
        'condition_type': 'lesson_complete', 'condition_value': '5',
        'how_to_earn': 'Finish five lessons in any course.',
    },
    {
        'slug': 'knowledge-seeker', 'title': 'Knowledge Seeker',
        'description': 'Complete 25 lessons.',
        'icon': 'book', 'category': 'course', 'difficulty': INTERMEDIATE,
        'xp_bonus': 300,
        'condition_type': 'lesson_complete', 'condition_value': '25',
        'how_to_earn': 'Finish twenty-five lessons across the academy.',
    },
    {
        'slug': 'dedicated-learner', 'title': 'Dedicated Learner',
        'description': 'Complete 50 lessons.',
        'icon': 'graduation', 'category': 'course', 'difficulty': ADVANCED,
        'xp_bonus': 600,
        'condition_type': 'lesson_complete', 'condition_value': '50',
        'how_to_earn': 'Finish fifty lessons across the academy.',
    },
    {
        'slug': 'chapter-master', 'title': 'Chapter Master',
        'description': 'Complete every lesson in a chapter.',
        'icon': 'star', 'category': 'chapter', 'difficulty': BEGINNER,
        'xp_bonus': 200,
        'condition_type': 'chapter_complete', 'condition_value': '',
        'how_to_earn': 'Finish all lessons inside one chapter.',
    },

    # ── Coding achievements ──────────────────────────────────────────────
    {
        'slug': 'first-commit', 'title': 'First Commit',
        'description': 'Solve your first coding exercise.',
        'icon': 'braces', 'category': 'exercise', 'difficulty': BEGINNER,
        'xp_bonus': 50,
        'condition_type': 'exercise_correct_count', 'condition_value': '1',
        'how_to_earn': 'Submit a correct answer to any course exercise.',
    },
    {
        'slug': 'problem-solver', 'title': 'Problem Solver',
        'description': 'Solve 10 coding exercises.',
        'icon': 'braces', 'category': 'exercise', 'difficulty': INTERMEDIATE,
        'xp_bonus': 250,
        'condition_type': 'exercise_correct_count', 'condition_value': '10',
        'how_to_earn': 'Pass ten distinct exercises in any course.',
    },
    {
        'slug': 'code-master', 'title': 'Code Master',
        'description': 'Solve 50 coding exercises.',
        'icon': 'braces', 'category': 'exercise', 'difficulty': ADVANCED,
        'xp_bonus': 700,
        'condition_type': 'exercise_correct_count', 'condition_value': '50',
        'how_to_earn': 'Pass fifty distinct exercises in any course.',
    },
    {
        'slug': 'challenge-initiate', 'title': 'Challenge Initiate',
        'description': 'Solve your first coding challenge.',
        'icon': 'bolt', 'category': 'exercise', 'difficulty': BEGINNER,
        'xp_bonus': 75,
        'condition_type': 'challenge_count', 'condition_value': '1',
        'how_to_earn': 'Submit a correct solution to any practice challenge.',
    },
    {
        'slug': 'dsa-explorer', 'title': 'DSA Explorer',
        'description': 'Complete 10 data-structures-and-algorithms challenges.',
        'icon': 'bolt', 'category': 'skill', 'difficulty': ADVANCED,
        'xp_bonus': 500,
        'condition_type': 'challenge_topic_count', 'condition_value': 'dsa:10',
        'how_to_earn': 'Solve ten challenges in the Data Structures & Algorithms topic.',
    },

    # ── Consistency achievements ─────────────────────────────────────────
    {
        'slug': 'first-activity', 'title': 'First Move',
        'description': 'Complete your first learning activity.',
        'icon': 'sparkle', 'category': 'special', 'difficulty': BEGINNER,
        'xp_bonus': 25,
        'condition_type': 'first_activity', 'condition_value': '',
        'how_to_earn': 'Finish a lesson, exercise, or challenge.',
    },
    {
        'slug': 'streak-3', 'title': 'Three-Day Spark',
        'description': 'Learn for three consecutive days.',
        'icon': 'fire', 'category': 'streak', 'difficulty': BEGINNER,
        'xp_bonus': 100,
        'condition_type': 'streak_n', 'condition_value': '3',
        'how_to_earn': 'Do something every day for three days in a row.',
    },
    {
        # Pre-existing row kept at its original slug; the registry now pins
        # it onto the generalised ``streak_n`` mode.
        'slug': 'streak-7', 'title': 'Week Warrior',
        'description': 'Maintain a 7-day learning streak.',
        'icon': 'fire', 'category': 'streak', 'difficulty': INTERMEDIATE,
        'xp_bonus': 300,
        'condition_type': 'streak_n', 'condition_value': '7',
        'how_to_earn': 'Learn every day for seven days in a row.',
    },
    {
        'slug': 'streak-30', 'title': 'Monthly Marathon',
        'description': 'Maintain a 30-day learning streak.',
        'icon': 'fire', 'category': 'streak', 'difficulty': ADVANCED,
        'xp_bonus': 800,
        'condition_type': 'streak_n', 'condition_value': '30',
        'how_to_earn': 'Learn every day for thirty days in a row.',
    },

    # ── Community & project achievements ─────────────────────────────────
    {
        'slug': 'community-member', 'title': 'Community Member',
        'description': 'Join the Code Yaar community.',
        'icon': 'users', 'category': 'special', 'difficulty': BEGINNER,
        'xp_bonus': 0,
        'condition_type': 'account', 'condition_value': '',
        'how_to_earn': 'Create a Code Yaar account — you already have one.',
    },
    {
        'slug': 'project-builder', 'title': 'Project Builder',
        'description': 'Finish a full course in a track that ships projects.',
        'icon': 'layers', 'category': 'project', 'difficulty': INTERMEDIATE,
        'xp_bonus': 400,
        'condition_type': 'project_course_complete', 'condition_value': '1',
        'how_to_earn': 'Complete a course whose career track offers hands-on projects.',
    },

    # ── Course- and excellence awards (pre-existing rows, patched in place) ──
    {
        'slug': 'python-foundations-complete', 'title': 'Python Graduate',
        'description': 'Complete the Python Foundations course.',
        'icon': 'graduation', 'category': 'course', 'difficulty': INTERMEDIATE,
        'xp_bonus': 500,
        'condition_type': 'course_complete',
        'condition_value': 'python-foundations',
        'how_to_earn': 'Finish every lesson and the final assessment of Python Foundations.',
    },
    {
        'slug': 'git-foundations-complete', 'title': 'Version Control Ready',
        'description': 'Complete the Git & GitHub Foundations course.',
        'icon': 'graduation', 'category': 'course', 'difficulty': BEGINNER,
        'xp_bonus': 300,
        'condition_type': 'course_complete',
        'condition_value': 'git-github-foundations',
        'how_to_earn': 'Finish every lesson and the final assessment of Git & GitHub Foundations.',
    },
    {
        'slug': 'excellence-award', 'title': 'Excellence Award',
        'description': 'Maintain a seven-day streak while completing coursework.',
        'icon': 'award', 'category': 'excellence', 'difficulty': ADVANCED,
        'xp_bonus': 500,
        'condition_type': 'streak_n', 'condition_value': '7',
        'how_to_earn': 'Keep a seven-day streak and complete a course.',
    },
]


def badge_by_slug(slug: str) -> dict | None:
    for badge in BADGES:
        if badge['slug'] == slug:
            return badge
    return None
