"""Publish-readiness checks for the Course Creation Studio (spec 3.6).

The old ``CourseAdminViewSet.publish`` flipped a boolean with no questions asked, so
a course with zero chapters could go live and appear in the learner catalogue as an
empty shell. This module answers one question honestly: *if this publishes, does a
student get a real course?*

The split between blocking issues and warnings is deliberate and matters more than
the checks themselves. The specification says to "block publication only when
genuinely required", so a problem only blocks when publishing would demonstrably
break the learner experience - no content at all, an unearnable certificate, a
coding exercise that cannot be graded. Anything that is merely thin, unpolished, or
a matter of editorial taste is a warning, and an administrator with a reason can
publish through it with an override that gets written to the audit log.
"""

from django.utils import timezone

#: Issue severity. Only ``blocking`` prevents publication.
BLOCKING = 'blocking'
WARNING = 'warning'


def _issue(code, message, *, severity, target=None):
    return {
        'code': code,
        'message': message,
        'severity': severity,
        'target': target or {},
    }


def blocking(code, message, *, target=None):
    return _issue(code, message, severity=BLOCKING, target=target)


def warning(code, message, *, target=None):
    return _issue(code, message, severity=WARNING, target=target)


def _target(kind, obj, label=None):
    return {
        'type': kind,
        'id': getattr(obj, 'pk', None),
        'slug': getattr(obj, 'slug', '') or '',
        'label': label or str(obj),
    }


def _has_learner_visible_content(lesson):
    """A lesson counts as non-empty if anything at all renders for a learner."""
    return bool(
        (lesson.content_body or '').strip()
        or (lesson.video_url or '').strip()
        or lesson.exercises.filter(is_active=True).exists()
    )


def _validate_prerequisite_chain(course):
    """Self-reference and cycle detection over ``prerequisite_courses``.

    A cycle here is not a style problem: enrolment eligibility walks this graph, so
    a loop makes the course permanently unenrollable.
    """
    issues = []
    if course.prerequisite_courses.filter(pk=course.pk).exists():
        issues.append(blocking(
            'prerequisite_self_reference',
            'This course lists itself as a prerequisite, which can never be satisfied.',
            target=_target('course', course),
        ))
        return issues

    seen = {course.pk}
    frontier = list(course.prerequisite_courses.values_list('pk', flat=True))
    while frontier:
        pk = frontier.pop()
        if pk in seen:
            issues.append(blocking(
                'prerequisite_cycle',
                'The prerequisite chain loops back on itself, making enrolment '
                'impossible for every learner.',
                target={'type': 'course', 'id': pk, 'slug': '', 'label': f'course #{pk}'},
            ))
            break
        seen.add(pk)
        frontier.extend(
            type(course).objects.filter(pk=pk)
            .values_list('prerequisite_courses__pk', flat=True)
        )
        frontier = [p for p in frontier if p is not None]
    return issues


def _check_exercise(exercise, issues):
    """Per-exercise configuration, mirroring what the runner actually needs."""
    label = exercise.title or f'exercise #{exercise.pk}'

    if not (exercise.instructions or '').strip():
        issues.append(blocking(
            'exercise_missing_instructions',
            f'"{label}" has no instructions, so the learner cannot tell what to do.',
            target=_target('exercise', exercise, label),
        ))

    if exercise.exercise_type == 'code':
        # Without tests or an expected output there is nothing to grade against, and
        # a code exercise that can never be marked correct silently blocks any
        # lesson or certification that depends on it.
        if not (exercise.test_cases or []) and not (exercise.hidden_tests or []):
            issues.append(blocking(
                'exercise_code_no_tests',
                f'"{label}" is a code exercise with no test cases configured.',
                target=_target('exercise', exercise, label),
            ))
        elif not (exercise.test_cases or []):
            issues.append(warning(
                'exercise_code_only_hidden_tests',
                f'"{label}" has only hidden tests, so a learner gets no feedback from '
                'the sample run.',
                target=_target('exercise', exercise, label),
            ))
    elif exercise.exercise_type in ('multiple_choice', 'multiple_select'):
        choices = exercise.choices or []
        correct = [c for c in choices if isinstance(c, dict) and c.get('is_correct')]
        if not choices:
            issues.append(blocking(
                'exercise_no_choices',
                f'"{label}" is a {exercise.get_exercise_type_display()} with no answer '
                'options.',
                target=_target('exercise', exercise, label),
            ))
        elif not correct:
            issues.append(blocking(
                'exercise_no_correct_answer',
                f'"{label}" has no answer marked correct, so it always scores zero.',
                target=_target('exercise', exercise, label),
            ))
        elif len(correct) == 1 and exercise.exercise_type == 'multiple_select':
            issues.append(warning(
                'exercise_select_single_answer',
                f'"{label}" allows multiple selections but marks only one answer '
                'correct.',
                target=_target('exercise', exercise, label),
            ))
        ids = [c.get('id') for c in choices if isinstance(c, dict)]
        if len([i for i in ids if i]) != len(set(i for i in ids if i)):
            issues.append(blocking(
                'exercise_duplicate_choice_ids',
                f'"{label}" has duplicate option identifiers, which breaks answer '
                'scoring.',
                target=_target('exercise', exercise, label),
            ))
    elif exercise.exercise_type == 'output_prediction':
        if not (exercise.expected_output or '').strip():
            issues.append(blocking(
                'exercise_output_no_expected',
                f'"{label}" predicts output but no expected output is recorded.',
                target=_target('exercise', exercise, label),
            ))

    if exercise.xp_reward and exercise.xp_reward > 1000:
        issues.append(warning(
            'exercise_xp_outlier',
            f'"{label}" awards {exercise.xp_reward} XP, far above the usual range.',
            target=_target('exercise', exercise, label),
        ))


def _check_resource(resource, issues):
    """Validate one course resource link (``Resource`` belongs to a course, not a lesson)."""
    url = (resource.file_url or '').strip()
    if not url:
        issues.append(warning(
            'resource_missing_link',
            f'Resource "{resource.title}" has no file or URL attached.',
            target=_target('resource', resource),
        ))
    elif not url.startswith(('http://', 'https://', '/')):
        issues.append(warning(
            'resource_broken_link',
            f'Resource "{resource.title}" has a URL that is neither absolute nor '
            'site-relative.',
            target=_target('resource', resource),
        ))


def run_publish_check(course, *, for_publish=True):
    """Return the publish-readiness report for ``course``.

    ``for_publish`` is kept for future callers that want a plain health report
    without publication-specific blockers; today every blocker is a content blocker,
    so both modes run the same checks.
    """
    issues = []

    if not (course.description or '').strip():
        issues.append(blocking(
            'course_missing_description',
            'The course has no description, so its page would read as empty.',
        ))
    if not (course.thumbnail or '').strip() and not course.cover_image:
        issues.append(blocking(
            'course_missing_thumbnail',
            'No thumbnail or cover image is set, so the course card renders blank in '
            'the catalogue.',
        ))
    if len((course.title or '').strip()) < 3:
        issues.append(blocking(
            'course_missing_title',
            'The course needs a title of at least three characters.',
        ))
    if not course.track_id:
        issues.append(blocking(
            'course_missing_track',
            'The course is not attached to a learning track.',
        ))

    if not (course.learning_objectives or []):
        issues.append(warning(
            'course_missing_objectives',
            'No learning objectives are defined; the specification asks students to '
            'see what they will be able to do.',
        ))
    if not (course.subtitle or '').strip():
        issues.append(warning(
            'course_missing_subtitle',
            'No short description is set, so list views fall back to the full '
            'description.',
        ))

    issues.extend(_validate_prerequisite_chain(course))

    chapters = list(course.chapters.all().prefetch_related('lessons__exercises'))
    if not chapters:
        issues.append(blocking(
            'course_no_chapters',
            'The course has no chapters; there is nothing for a learner to open.',
        ))

    published_lessons = 0
    order_gaps = []
    for chapter in chapters:
        lessons = list(chapter.lessons.all())
        if not lessons:
            issues.append(blocking(
                'chapter_empty',
                f'Chapter "{chapter.title}" contains no lessons.',
                target=_target('chapter', chapter),
            ))
            continue

        live_here = [l for l in lessons if l.is_active]
        published_lessons += len(live_here)
        if not live_here:
            issues.append(warning(
                'chapter_all_draft',
                f'Every lesson in chapter "{chapter.title}" is a draft, so the '
                'chapter is invisible to learners.',
                target=_target('chapter', chapter),
            ))

        if chapter.xp_reward and chapter.xp_reward > 5000:
            issues.append(warning(
                'chapter_xp_outlier',
                f'Chapter "{chapter.title}" awards {chapter.xp_reward} XP.',
                target=_target('chapter', chapter),
            ))

        previous_order = None
        for lesson in sorted(lessons, key=lambda l: (l.order, l.pk)):
            if previous_order is not None and lesson.order > previous_order + 1:
                order_gaps.append((chapter, previous_order, lesson.order))
            previous_order = lesson.order

            if not (lesson.title or '').strip():
                issues.append(blocking(
                    'lesson_missing_title',
                    f'A lesson in chapter "{chapter.title}" has no title.',
                    target=_target('lesson', lesson),
                ))
            if lesson.is_active and not _has_learner_visible_content(lesson):
                issues.append(blocking(
                    'lesson_empty',
                    f'Lesson "{lesson.title}" is published but renders no content.',
                    target=_target('lesson', lesson),
                ))
            if lesson.is_active and not (lesson.learning_objective or '').strip():
                issues.append(warning(
                    'lesson_missing_objective',
                    f'Lesson "{lesson.title}" states no learning objective.',
                    target=_target('lesson', lesson),
                ))
            if lesson.prerequisite_id == lesson.pk:
                issues.append(blocking(
                    'lesson_prerequisite_self_reference',
                    f'Lesson "{lesson.title}" requires itself.',
                    target=_target('lesson', lesson),
                ))
            elif lesson.prerequisite_id and lesson.prerequisite.chapter_id != lesson.chapter_id:
                issues.append(warning(
                    'lesson_prerequisite_cross_chapter',
                    f'Lesson "{lesson.title}" requires a lesson from another chapter; '
                    'sequential unlocking is evaluated per chapter.',
                    target=_target('lesson', lesson),
                ))
            if lesson.is_active and (lesson.duration_minutes or 0) == 0:
                issues.append(warning(
                    'lesson_missing_duration',
                    f'Lesson "{lesson.title}" has no duration, so the course total '
                    'time estimate will read low.',
                    target=_target('lesson', lesson),
                ))

            for exercise in lesson.exercises.filter(is_active=True):
                _check_exercise(exercise, issues)

        for lesson in lessons:
            if lesson.source_type == 'official' and lesson.verification_status != 'verified':
                issues.append(blocking(
                    'lesson_unverified_official_source',
                    f'Lesson "{lesson.title}" claims official board-textbook sourcing '
                    'but has not been verified against the textbook.',
                    target=_target('lesson', lesson),
                ))

    if published_lessons == 0 and chapters:
        issues.append(blocking(
            'course_no_published_lessons',
            'Not one lesson in this course is published.',
        ))

    for chapter, previous_order, order in order_gaps:
        issues.append(warning(
            'lesson_order_gap',
            f'Chapter "{chapter.title}" jumps from lesson order {previous_order} to '
            f'{order}; the sequence has a gap.',
            target=_target('chapter', chapter),
        ))

    if course.require_final_assessment:
        # Certification depends on at least one assessable activity. Publishing a
        # certificate-enabled course with none means every finisher is silently
        # ineligible, which is a learner-facing defect rather than unfinished polish.
        flagged = any(e.is_final_assessment for e in _all_active_exercises(course))
        if not flagged:
            issues.append(blocking(
                'final_assessment_missing',
                'This course requires a final assessment for certification, but no '
                'published exercise is flagged as the final assessment - nobody could '
                'ever earn the certificate.',
            ))

    for resource in course.resources.filter(is_active=True):
        _check_resource(resource, issues)

    if course.xp_completion_reward and course.xp_completion_reward > 10000:
        issues.append(warning(
            'course_xp_outlier',
            f'The course completion bonus is {course.xp_completion_reward} XP, well '
            'above the usual range.',
        ))

    blocking_issues = [i for i in issues if i['severity'] == BLOCKING]
    warning_issues = [i for i in issues if i['severity'] == WARNING]
    return {
        'ok': not blocking_issues,
        'blocking': blocking_issues,
        'warnings': warning_issues,
        'checked_at': timezone.now().isoformat(),
        'counts': {
            'chapters': len(chapters),
            'lessons': sum(len(c.lessons.all()) for c in chapters),
            'published_lessons': published_lessons,
        },
    }


def _all_active_exercises(course):
    """Active exercises of published lessons, as model instances.

    Kept as a single flat query because the publish check runs over the whole course
    and this is the only place that needs cross-chapter exercise reach.
    """
    from ..models import Exercise

    return Exercise.objects.filter(
        lesson__chapter__course=course,
        is_active=True,
        lesson__is_active=True,
    )
