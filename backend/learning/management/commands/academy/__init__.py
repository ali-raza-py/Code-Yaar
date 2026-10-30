"""Academy content package.

Course curricula are stored as structured data here and materialised into
Django models by the ``seed_academy`` management command. Keeping content as
data (rather than duplicated across frontend pages) lets a single reusable
system drive every course, module, lesson, exercise and assessment.

Each course module exports a ``COURSE`` dict following this schema:

    {
      'slug', 'title', 'subtitle', 'description',
      'difficulty', 'language', 'prerequisites',
      'track': {'slug', 'title', 'description'},
      'objectives': [str, ...],
      'certification': {'passing_score': int, ...},   # optional overrides
      'modules': [
        {
          'title', 'slug', 'description',
          'lessons': [
            {
              'title', 'slug', 'objective', 'body', 'duration',
              'exercises': [ {..Exercise fields..}, ... ]   # optional
            }
          ]
        }
      ],
      'assessment': [ {..Exercise with is_final_assessment implied..}, ... ]
    }

Exercise dicts use keys matching learning.models.Exercise (choices, test_cases,
expected_output, starter_code, solution_code, exercise_type, xp_reward).
"""
