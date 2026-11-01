"""
Sindh Board textbook curricula.

Each module describes one textbook unit as plain data: chapters, lessons,
exercises and hints, together with the printed page reference the content was
taken from. Nothing here is executed — `seed_sindh_board` turns it into the
existing Course/Chapter/Lesson/Exercise models, so the admin remains the place
where content is edited after seeding.

Rule that keeps the curriculum honest:

* `source_type='official'` content must be `verification_status='verified'`,
  which `SourceReference.clean()` enforces. Un-reviewed material physically
  cannot be seeded as board syllabus.
* Anything that goes beyond the printed book is labelled `supplementary` or
  `additional` and is shown to learners as such.
"""

from . import class_x  # noqa: F401
from . import class_xi  # noqa: F401
from . import class_xii  # noqa: F401

# Registry consumed by the seed command, in navigation order.
CURRICULA = [class_x, class_xi, class_xii]
