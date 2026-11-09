"""Course Creation Studio API (spec section 3).

The existing ``CourseAdminViewSet`` is a flat CRUD table: it cannot express what the
studio actually needs, which is *"give me this course with its whole curriculum in one
call, let me autosave a section of it, and tell me whether it is publishable"*. This
module adds that surface without disturbing the table endpoints the older admin pages
still use.

Three design decisions are load-bearing:

*Conflict detection on autosave.* The studio saves continuously, so two tabs - or a
half-finished request from a laptop that slept - can silently overwrite newer work.
Every write therefore carries ``expected_updated_at``; a mismatch returns ``409`` and
the client reloads rather than guessing. ``Course.updated_at`` is ``auto_now``, so it
moves on every save and is a genuine version token here.

*Derived counts, never stored counts.* Chapter publication state and lesson totals are
computed from the rows themselves. A stored "is this chapter published" flag would be a
second truth that drifts the moment somebody toggles a lesson.

*Scoped instructor access.* Administrators reach every course. An instructor reaches
only the courses where ``Course.instructor_user`` is their own account, which is what
makes "instructors cannot modify unassigned courses" a server-side fact instead of a
sidebar arrangement.
"""

from django.db import transaction
from django.db.models import Count, Prefetch, Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.text import slugify
from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import (
    Chapter, Course, CourseCategory, Exercise, Lesson, Resource, record_admin_action,
)
from .permissions import HasAdminCapability, ScopedCourseAccess
from .services import publishing
from .services.admin_access import (
    ALL as ALL_CAPABILITIES, COURSE_ARCHIVE, COURSE_PUBLISH, COURSE_STUDIO_EDIT,
    COURSE_STUDIO_VIEW, has_capability,
)


# ─── Helpers ──────────────────────────────────────────────────────────────────

def unique_slug(model, base, *, exclude_pk=None, **scope):
    """Return ``base`` or ``base-2``, ``base-3``... until it is free within ``scope``.

    The previous ``duplicate()`` hard-coded ``f"{slug}-copy"``, so duplicating a course
    twice raised IntegrityError on the unique constraint - a crash any administrator
    would hit during ordinary work.
    """
    base = slugify(base or 'item') or 'item'
    candidate = base
    suffix = 2
    while True:
        qs = model.objects.filter(slug=candidate, **scope)
        if exclude_pk is not None:
            qs = qs.exclude(pk=exclude_pk)
        if not qs.exists():
            return candidate
        candidate = f'{base}-{suffix}'
        suffix += 1


def _parse_dt(raw):
    if not raw:
        return None
    from django.utils.dateparse import parse_datetime

    dt = parse_datetime(str(raw))
    if dt and timezone.is_naive(dt):
        dt = timezone.make_aware(dt, timezone.get_current_timezone())
    return dt


def _coerce_int_list(payload, key):
    """Validate a caller-supplied id list into clean ints, or raise ValueError."""
    raw = payload.get(key) or []
    if not isinstance(raw, list):
        raise ValueError(f'"{key}" must be a list.')
    ids = []
    for entry in raw:
        try:
            ids.append(int(entry if not isinstance(entry, dict) else entry.get('id')))
        except (TypeError, ValueError):
            raise ValueError(f'"{key}" contains a non-numeric id.')
    return ids


class CapabilityActionsMixin:
    """Map each studio action to the capability it requires.

    ``HasAdminCapability`` reads ``required_admin_capability`` off the view; resolving
    it per action keeps one viewset from having to be split into six just to express
    "reading is cheaper than publishing".
    """

    capability_map = {}

    def get_required_capability(self):
        return self.capability_map.get(self.action, COURSE_STUDIO_VIEW)

    def get_permissions(self):
        self.required_admin_capability = self.get_required_capability()
        return [HasAdminCapability(), ScopedCourseAccess()]


# ─── Serializers ──────────────────────────────────────────────────────────────

class CourseStudioSerializer(serializers.ModelSerializer):
    """The fields the studio's identity / objectives / requirements / XP steps write."""

    prerequisite_courses = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Course.objects.all(), required=False
    )

    class Meta:
        model = Course
        fields = [
            'title', 'subtitle', 'description', 'thumbnail', 'cover_image',
            'category', 'track', 'academic_class', 'difficulty', 'language',
            'instructor', 'instructor_user', 'prerequisites', 'learning_objectives',
            'tags', 'is_free', 'order', 'certification_enabled',
            'certification_passing_score', 'require_all_lessons',
            'require_final_assessment', 'prerequisite_courses',
            'sequential_learning', 'xp_completion_reward', 'manual_estimated_hours',
        ]

    def validate_learning_objectives(self, value):
        if value and not isinstance(value, list):
            raise serializers.ValidationError('Learning objectives must be a list.')
        return value or []

    def validate_tags(self, value):
        if value and not isinstance(value, list):
            raise serializers.ValidationError('Tags must be a list.')
        return value or []

    def validate_prerequisite_courses(self, value):
        course = self.instance
        if course is not None:
            if any(c.pk == course.pk for c in value):
                raise serializers.ValidationError(
                    'A course cannot require itself before enrolment.'
                )
            # Reject a two-step loop (A requires B, B already requires A) at the API
            # edge so the studio gets a field error instead of a publish-time mystery.
            nested = {
                pk
                for c in value
                for pk in c.prerequisite_courses.values_list('pk', flat=True)
            }
            if course.pk in nested:
                raise serializers.ValidationError(
                    'That prerequisite chain loops back to this course.'
                )
        return value

    def validate_instructor_user(self, value):
        request = self.context.get('request')
        # Reassigning who owns a course is a staffing decision, not editorial work,
        # so a Course Editor cannot hand a course to somebody else.
        if value is not None and request is not None:
            user = request.user
            if not has_capability(user, ALL_CAPABILITIES):
                if getattr(value, 'pk', None) != getattr(user, 'pk', None):
                    raise serializers.ValidationError(
                        'Only a platform administrator can reassign a course.'
                    )
        return value


class ChapterStudioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chapter
        fields = ['title', 'slug', 'description', 'order', 'xp_reward', 'is_active']
        extra_kwargs = {'slug': {'required': False}}

    def validate_title(self, value):
        if not (value or '').strip():
            raise serializers.ValidationError('Chapter title is required.')
        return value.strip()


class LessonStudioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = [
            'title', 'slug', 'content_type', 'learning_objective', 'content_body',
            'video_url', 'video_duration_seconds', 'order', 'duration_minutes',
            'xp_reward', 'is_free_preview', 'is_active', 'is_required',
            'prerequisite', 'estimated_reading_minutes', 'completion_condition',
            'instructor_notes',
        ]
        extra_kwargs = {'slug': {'required': False}}

    def validate_title(self, value):
        if not (value or '').strip():
            raise serializers.ValidationError('Lesson title is required.')
        return value.strip()

    def validate_completion_condition(self, value):
        if value and not isinstance(value, dict):
            raise serializers.ValidationError('Completion condition must be an object.')
        return value or {}

    def validate(self, attrs):
        prerequisite = attrs.get('prerequisite', getattr(self.instance, 'prerequisite', None))
        chapter = attrs.get('chapter') or getattr(self.instance, 'chapter_id', None)
        chapter_id = getattr(chapter, 'pk', chapter)
        if prerequisite is not None and chapter_id is not None:
            if self.instance is not None and prerequisite.pk == self.instance.pk:
                raise serializers.ValidationError({'prerequisite': 'A lesson cannot require itself.'})
            if getattr(prerequisite, 'chapter_id', None) != chapter_id:
                raise serializers.ValidationError({
                    'prerequisite': 'A lesson prerequisite must live in the same chapter.'
                })
        return attrs

    def validate_prerequisite(self, value):
        # Same-chapter enforcement needs the chapter, so it runs in validate(); this
        # hook only blocks the obvious self-reference before the object exists.
        if self.instance is not None and value is not None and value.pk == self.instance.pk:
            raise serializers.ValidationError('A lesson cannot require itself.')
        return value


class ExerciseStudioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exercise
        fields = [
            'title', 'slug', 'exercise_type', 'instructions', 'context',
            'constraints', 'expected_behavior', 'explain', 'difficulty',
            'language', 'starter_code', 'solution_code', 'expected_output',
            'choices', 'test_cases', 'hidden_tests', 'xp_reward', 'max_attempts',
            'is_final_assessment', 'order', 'is_active',
        ]
        extra_kwargs = {'slug': {'required': False}}

    def validate_title(self, value):
        if not (value or '').strip():
            raise serializers.ValidationError('Exercise title is required.')
        return value.strip()

    def validate(self, attrs):
        exercise_type = attrs.get('exercise_type', getattr(self.instance, 'exercise_type', None))
        choices = attrs.get('choices', getattr(self.instance, 'choices', None) or [])
        if exercise_type in ('multiple_choice', 'multiple_select'):
            correct = [c for c in choices if isinstance(c, dict) and c.get('is_correct')]
            if not correct:
                raise serializers.ValidationError({
                    'choices': f'Mark at least one answer correct for this {exercise_type.replace("_", " ")}.',
                })
        return attrs


# ─── Studio viewset ───────────────────────────────────────────────────────────

class CourseStudioViewSet(CapabilityActionsMixin, viewsets.GenericViewSet):
    """Course Creation Studio workspace endpoints, mounted at /api/admin/course-studio/."""

    queryset = Course.objects.select_related('track', 'category', 'instructor_user')
    serializer_class = CourseStudioSerializer
    # Replaced per-action by CapabilityActionsMixin.get_permissions().
    permission_classes = [HasAdminCapability, ScopedCourseAccess]

    capability_map = {
        'list': COURSE_STUDIO_VIEW,
        'bundle': COURSE_STUDIO_VIEW,
        'partial_update': COURSE_STUDIO_EDIT,
        'update': COURSE_STUDIO_EDIT,
        'create': COURSE_STUDIO_EDIT,
        'create_chapter': COURSE_STUDIO_EDIT,
        'update_chapter': COURSE_STUDIO_EDIT,
        'destroy_chapter': COURSE_STUDIO_EDIT,
        'duplicate_chapter': COURSE_STUDIO_EDIT,
        'reorder_chapters': COURSE_STUDIO_EDIT,
        'create_lesson': COURSE_STUDIO_EDIT,
        'update_lesson': COURSE_STUDIO_EDIT,
        'destroy_lesson': COURSE_STUDIO_EDIT,
        'duplicate_lesson': COURSE_STUDIO_EDIT,
        'move_lesson': COURSE_STUDIO_EDIT,
        'reorder_lessons': COURSE_STUDIO_EDIT,
        'bulk_publish_lessons': COURSE_PUBLISH,
        'create_exercise': COURSE_STUDIO_EDIT,
        'update_exercise': COURSE_STUDIO_EDIT,
        'destroy_exercise': COURSE_STUDIO_EDIT,
        'checklist': COURSE_STUDIO_VIEW,
        'publish': COURSE_PUBLISH,
        'unpublish': COURSE_PUBLISH,
        'schedule': COURSE_PUBLISH,
        'unschedule': COURSE_PUBLISH,
        'archive': COURSE_ARCHIVE,
        'unarchive': COURSE_ARCHIVE,
    }

    def get_object(self):
        course = super().get_object()
        self.check_object_permissions(self.request, course)
        return course

    def list(self, request):
        """The studio's course picker, with curriculum counts in one query.

        An instructor only ever sees their own courses here (``ScopedCourseAccess`` is
        enforced on the queryset, not per row) so the list doubles as the assignment
        screen the specification describes.
        """
        qs = self.get_queryset()
        if not has_capability(request.user, ALL_CAPABILITIES):
            qs = qs.filter(instructor_user=request.user)

        state = (request.query_params.get('state') or '').strip().lower()
        if state == 'draft':
            qs = qs.filter(is_published=False, archived_at__isnull=True)
        elif state == 'published':
            qs = qs.filter(is_published=True, archived_at__isnull=True)
        elif state == 'archived':
            qs = qs.filter(archived_at__isnull=False)
        elif state == 'scheduled':
            qs = qs.filter(publish_at__isnull=False, is_published=False)

        search = (request.query_params.get('q') or '').strip()
        if search:
            qs = qs.filter(Q(title__icontains=search) | Q(slug__icontains=search))
        track = request.query_params.get('track')
        if track:
            qs = qs.filter(track_id=track)
        category = request.query_params.get('category')
        if category:
            qs = qs.filter(category_id=category)

        qs = qs.annotate(
            studio_chapter_count=Count('chapters', distinct=True),
            studio_lesson_count=Count('chapters__lessons', distinct=True),
            studio_published_lesson_count=Count(
                'chapters__lessons',
                filter=Q(chapters__lessons__is_active=True),
                distinct=True,
            ),
            studio_enrollment_count=Count('enrollments', distinct=True),
        ).order_by('-updated_at', 'title')

        page = self.paginate_queryset(qs)
        rows = list(page if page is not None else qs)
        payload = [
            {
                'id': course.pk,
                'slug': course.slug,
                'title': course.title,
                'subtitle': course.subtitle,
                'difficulty': course.difficulty,
                'is_published': course.is_published,
                'is_active': course.is_active,
                'publish_at': course.publish_at.isoformat() if course.publish_at else None,
                'published_at': course.published_at.isoformat() if course.published_at else None,
                'archived_at': course.archived_at.isoformat() if course.archived_at else None,
                'track': course.track.title if course.track_id else None,
                'category': course.category.title if course.category_id else None,
                'instructor': course.instructor,
                'instructor_user': course.instructor_user_id,
                'chapter_count': course.studio_chapter_count,
                'lesson_count': course.studio_lesson_count,
                'published_lesson_count': course.studio_published_lesson_count,
                'enrollment_count': course.studio_enrollment_count,
                'updated_at': course.updated_at.isoformat(),
            }
            for course in rows
        ]
        if page is not None:
            return self.get_paginated_response(payload)
        return Response(payload)

    # ── Bundle ────────────────────────────────────────────────────────────────

    def _bundle_payload(self, course):
        """Whole-course read in a fixed number of queries.

        Lesson and exercise counts ride along as annotations on the prefetched
        querysets, so nothing here loops back to the database per row - the flat admin
        serializers did, which is exactly the N+1 the specification rules out.
        """
        chapters = list(
            course.chapters.order_by('order', 'pk').prefetch_related(
                Prefetch(
                    'lessons',
                    queryset=Lesson.objects.order_by('order', 'pk').annotate(
                        exercise_count=Count('exercises')
                    ).prefetch_related('exercises'),
                )
            )
        )
        stats = course.enrollments.aggregate(
            enrollments=Count('id'),
            completed=Count('id', filter=Q(status='completed')),
        )
        payload = {
            'course': {
                'id': course.pk,
                'slug': course.slug,
                'title': course.title,
                'subtitle': course.subtitle,
                'description': course.description,
                'thumbnail': course.thumbnail,
                'cover_image': (course.cover_image.url if course.cover_image else ''),
                'category': course.category_id,
                'category_title': course.category.title if course.category else '',
                'track': course.track_id,
                'track_title': course.track.title if course.track else '',
                'academic_class': course.academic_class,
                'difficulty': course.difficulty,
                'language': course.language,
                'instructor': course.instructor,
                'instructor_user': course.instructor_user_id,
                'instructor_user_name': (
                    course.instructor_user.get_full_name() or course.instructor_user.username
                    if course.instructor_user else ''
                ),
                'prerequisites': course.prerequisites,
                'prerequisite_courses': list(
                    course.prerequisite_courses.values('id', 'title', 'slug')
                ),
                'learning_objectives': course.learning_objectives or [],
                'tags': course.tags or [],
                'is_free': course.is_free,
                'order': course.order,
                'is_published': course.is_published,
                'is_active': course.is_active,
                'is_archived': course.is_archived,
                'certification_enabled': course.certification_enabled,
                'certification_passing_score': course.certification_passing_score,
                'require_all_lessons': course.require_all_lessons,
                'require_final_assessment': course.require_final_assessment,
                'sequential_learning': course.sequential_learning,
                'xp_completion_reward': course.xp_completion_reward,
                'manual_estimated_hours': course.manual_estimated_hours,
                'estimated_hours': course.estimated_hours,
                'publish_at': course.publish_at.isoformat() if course.publish_at else None,
                'published_at': course.published_at.isoformat() if course.published_at else None,
                'archived_at': course.archived_at.isoformat() if course.archived_at else None,
                'created_at': course.created_at.isoformat(),
                'updated_at': course.updated_at.isoformat(),
            },
            'chapters': [
                {
                    'id': chapter.pk,
                    'title': chapter.title,
                    'slug': chapter.slug,
                    'description': chapter.description,
                    'order': chapter.order,
                    'xp_reward': chapter.xp_reward,
                    'is_active': chapter.is_active,
                    'source_type': chapter.source_type,
                    'verification_status': chapter.verification_status,
                    'publication_state': chapter.publication_state,
                    'lesson_count': len(chapter.lessons.all()),
                    'published_lesson_count': chapter.published_lesson_count,
                    'lessons': [
                        {
                            'id': lesson.pk,
                            'chapter': chapter.pk,
                            'title': lesson.title,
                            'slug': lesson.slug,
                            'content_type': lesson.content_type,
                            'learning_objective': lesson.learning_objective,
                            'content_body': lesson.content_body,
                            'video_url': lesson.video_url,
                            'video_duration_seconds': lesson.video_duration_seconds,
                            'order': lesson.order,
                            'duration_minutes': lesson.duration_minutes,
                            'estimated_reading_minutes': lesson.estimated_reading_minutes,
                            'xp_reward': lesson.xp_reward,
                            'is_free_preview': lesson.is_free_preview,
                            'is_active': lesson.is_active,
                            'is_required': lesson.is_required,
                            'prerequisite': lesson.prerequisite_id,
                            'completion_condition': lesson.completion_condition or {},
                            'instructor_notes': lesson.instructor_notes,
                            'source_type': lesson.source_type,
                            'verification_status': lesson.verification_status,
                            'exercise_count': lesson.exercise_count,
                            'exercises': [
                                self._exercise_payload(exercise)
                                for exercise in lesson.exercises.all()
                            ],
                            'updated_at': lesson.updated_at.isoformat(),
                        }
                        for lesson in chapter.lessons.all()
                    ],
                }
                for chapter in chapters
            ],
            'resources': [
                {
                    'id': resource.pk,
                    'title': resource.title,
                    'resource_type': resource.resource_type,
                    'url': resource.file_url,
                    'description': resource.description,
                    'order': resource.order,
                    'is_active': resource.is_active,
                }
                for resource in course.resources.order_by('order', 'pk')
            ],
            'stats': {
                'chapter_count': len(chapters),
                'lesson_count': sum(len(c.lessons.all()) for c in chapters),
                'published_lesson_count': sum(c.published_lesson_count for c in chapters),
                'enrollment_count': stats['enrollments'] or 0,
                'completion_count': stats['completed'] or 0,
                'total_xp': course.total_xp,
            },
            'permissions': {
                'can_edit': has_capability(self.request.user, COURSE_STUDIO_EDIT),
                'can_publish': has_capability(self.request.user, COURSE_PUBLISH),
                'can_archive': has_capability(self.request.user, COURSE_ARCHIVE),
            },
        }
        return payload

    @action(detail=True, methods=['get'])
    def bundle(self, request, pk=None):
        course = self.get_object()
        return Response(self._bundle_payload(course))

    def retrieve(self, request, *args, **kwargs):
        # ``retrieve`` mirrors ``bundle`` so the workspace can be opened by either URL.
        return self.bundle(request, pk=kwargs.get('pk'))

    def update(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        """Autosave target for the studio: course metadata only, with conflict guard."""
        course = self.get_object()
        expected = _parse_dt(request.data.get('expected_updated_at'))
        if expected is not None and course.updated_at > expected:
            return Response({
                'detail': 'This course changed since you last loaded it.',
                'code': 'conflict',
                'current_updated_at': course.updated_at.isoformat(),
            }, status=status.HTTP_409_CONFLICT)

        sections = request.data.get('sections')
        course_fields = request.data.get('course')
        if course_fields is None:
            course_fields = {
                key: value
                for key, value in request.data.items()
                if key in CourseStudioSerializer().fields
            }
        if not course_fields and not sections:
            return Response({'detail': 'Nothing to save.'}, status=status.HTTP_400_BAD_REQUEST)
        if (
            'instructor_user' in course_fields
            and not has_capability(request.user, ALL_CAPABILITIES)
            and str(course_fields['instructor_user']) != str(course.instructor_user_id)
        ):
            return Response({
                'instructor_user': [
                    'Only a platform administrator can reassign a course.'
                ],
            }, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            serializer = CourseStudioSerializer(
                course, data=course_fields or {}, partial=True, context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            course = serializer.save()
            record_admin_action(
                request.user, 'course.studio_save', obj=course,
                label=course.title,
                detail={'fields': sorted((course_fields or {}).keys())},
                request=request,
            )
        return Response(self._bundle_payload(course))

    def create(self, request, *args, **kwargs):
        """Step 1 of the wizard: create the draft so later steps autosave into a real row."""
        data = dict(request.data)
        data.pop('expected_updated_at', None)
        serializer = CourseStudioSerializer(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            course = serializer.save(
                slug=unique_slug(Course, data.get('slug') or data.get('title', 'course')),
                created_by=request.user if request.user.is_authenticated else None,
                is_published=False,
            )
            record_admin_action(request.user, 'course.create', obj=course,
                                label=course.title, request=request)
        return Response(self._bundle_payload(course), status=status.HTTP_201_CREATED)

    # ── Chapters ──────────────────────────────────────────────────────────────

    @action(detail=True, methods=['post'], url_path='chapters')
    def create_chapter(self, request, pk=None):
        course = self.get_object()
        serializer = ChapterStudioSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        slug = unique_slug(
            Chapter, request.data.get('slug') or request.data.get('title', 'chapter'),
            course=course,
        )
        chapter = serializer.save(course=course, slug=slug)
        record_admin_action(request.user, 'chapter.create', obj=chapter,
                            label=chapter.title, request=request)
        return Response(self._chapter_payload(chapter), status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['patch', 'put'], url_path=r'chapters/(?P<chapter_pk>[0-9]+)')
    def update_chapter(self, request, pk=None, chapter_pk=None):
        course = self.get_object()
        chapter = self._get_chapter(course, chapter_pk)
        serializer = ChapterStudioSerializer(chapter, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        chapter = serializer.save()
        record_admin_action(request.user, 'chapter.update', obj=chapter,
                            label=chapter.title,
                            detail={'fields': sorted(request.data.keys())}, request=request)
        return Response(self._chapter_payload(chapter))

    @action(detail=True, methods=['delete'], url_path=r'chapters/(?P<chapter_pk>[0-9]+)')
    def destroy_chapter(self, request, pk=None, chapter_pk=None):
        """Delete a chapter, refusing when learners have progress on it.

        ``Chapter`` cascades into lessons and lesson progress, so a hard delete would
        silently erase learner history. An administrator has to archive instead.
        """
        course = self.get_object()
        chapter = self._get_chapter(course, chapter_pk)
        from .models import LessonProgress

        in_use = LessonProgress.objects.filter(lesson__chapter=chapter).exists()
        if in_use:
            return Response({
                'detail': 'Learners have progress in this chapter. Archive it '
                          '(is_active=false) instead of deleting it.',
                'code': 'chapter_in_use',
            }, status=status.HTTP_409_CONFLICT)
        label = chapter.title
        chapter.delete()
        record_admin_action(request.user, 'chapter.delete', obj=course,
                            label=label, detail={'chapter_title': label}, request=request)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'], url_path=r'chapters/(?P<chapter_pk>[0-9]+)/duplicate')
    def duplicate_chapter(self, request, pk=None, chapter_pk=None):
        course = self.get_object()
        chapter = self._get_chapter(course, chapter_pk)
        with transaction.atomic():
            copy = self._copy_chapter(chapter, course)
        record_admin_action(request.user, 'chapter.duplicate', obj=copy,
                            label=copy.title,
                            detail={'source_chapter': chapter_pk}, request=request)
        return Response(self._chapter_payload(copy, include_lessons=True),
                        status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], url_path='chapters/reorder')
    def reorder_chapters(self, request, pk=None):
        course = self.get_object()
        try:
            order_by_id = self._validated_orders(request, Chapter, course_filter={'course': course})
        except ValueError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        if not order_by_id:
            return Response({'detail': 'No chapters supplied.'}, status=status.HTTP_400_BAD_REQUEST)
        with transaction.atomic():
            rows = list(Chapter.objects.filter(pk__in=order_by_id, course=course))
            for chapter in rows:
                chapter.order = order_by_id[chapter.pk]
            Chapter.objects.bulk_update(rows, ['order'])
        record_admin_action(request.user, 'chapter.reorder', obj=course, label=course.title,
                            detail={'count': len(rows)}, request=request)
        return Response({'status': 'ok', 'reordered': len(rows)})

    # ── Lessons ───────────────────────────────────────────────────────────────

    @action(detail=True, methods=['post'], url_path='lessons')
    def create_lesson(self, request, pk=None):
        course = self.get_object()
        chapter_pk = request.data.get('chapter')
        if not chapter_pk:
            return Response({'detail': 'A lesson must be created inside a chapter.'},
                            status=status.HTTP_400_BAD_REQUEST)
        chapter = self._get_chapter(course, chapter_pk)
        serializer = LessonStudioSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        slug = unique_slug(
            Lesson, request.data.get('slug') or request.data.get('title', 'lesson'),
            chapter=chapter,
        )
        lesson = serializer.save(chapter=chapter, slug=slug)
        record_admin_action(request.user, 'lesson.create', obj=lesson,
                            label=lesson.title, request=request)
        return Response(self._lesson_payload(lesson), status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['patch', 'put'], url_path=r'lessons/(?P<lesson_pk>[0-9]+)')
    def update_lesson(self, request, pk=None, lesson_pk=None):
        course = self.get_object()
        lesson = self._get_lesson(course, lesson_pk)
        expected = _parse_dt(request.data.get('expected_updated_at'))
        if expected is not None and lesson.updated_at > expected:
            return Response({
                'detail': 'This lesson changed since you last loaded it.',
                'code': 'conflict',
                'current_updated_at': lesson.updated_at.isoformat(),
            }, status=status.HTTP_409_CONFLICT)
        data = {k: v for k, v in request.data.items() if k in LessonStudioSerializer().fields}
        serializer = LessonStudioSerializer(lesson, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        lesson = serializer.save()
        record_admin_action(request.user, 'lesson.update', obj=lesson, label=lesson.title,
                            detail={'fields': sorted(data.keys())}, request=request)
        return Response(self._lesson_payload(lesson))

    @action(detail=True, methods=['delete'], url_path=r'lessons/(?P<lesson_pk>[0-9]+)')
    def destroy_lesson(self, request, pk=None, lesson_pk=None):
        course = self.get_object()
        lesson = self._get_lesson(course, lesson_pk)
        from .models import LessonProgress

        if LessonProgress.objects.filter(lesson=lesson).exists():
            return Response({
                'detail': 'Learners have progress in this lesson. Set it to draft or '
                          'archive it instead of deleting it.',
                'code': 'lesson_in_use',
            }, status=status.HTTP_409_CONFLICT)
        label = lesson.title
        lesson.delete()
        record_admin_action(request.user, 'lesson.delete', obj=course, label=label,
                            detail={'lesson_title': label}, request=request)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'], url_path=r'lessons/(?P<lesson_pk>[0-9]+)/duplicate')
    def duplicate_lesson(self, request, pk=None, lesson_pk=None):
        course = self.get_object()
        lesson = self._get_lesson(course, lesson_pk)
        with transaction.atomic():
            copy = self._copy_lesson(lesson, lesson.chapter)
        record_admin_action(request.user, 'lesson.duplicate', obj=copy, label=copy.title,
                            detail={'source_lesson': lesson_pk}, request=request)
        return Response(self._lesson_payload(copy), status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], url_path=r'lessons/(?P<lesson_pk>[0-9]+)/move')
    def move_lesson(self, request, pk=None, lesson_pk=None):
        """Move a lesson to another chapter and/or position, atomically.

        The destination chapter must belong to *this* course - otherwise a studio tab
        could smuggle a lesson across courses, which is the same class of hole the old
        unrestricted ``reorder`` endpoint left open.
        """
        course = self.get_object()
        lesson = self._get_lesson(course, lesson_pk)
        target_chapter = lesson.chapter
        if request.data.get('chapter') not in (None, lesson.chapter_id):
            target_chapter = self._get_chapter(course, request.data.get('chapter'))
        try:
            order = int(request.data.get('order', lesson.order))
        except (TypeError, ValueError):
            return Response({'detail': '"order" must be an integer.'},
                            status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            if target_chapter.pk != lesson.chapter_id:
                prerequisite = lesson.prerequisite
                if prerequisite is not None and prerequisite.chapter_id != target_chapter.pk:
                    # Leaving a chapter would orphan a same-chapter prerequisite rule, so
                    # clear it rather than store an arrangement the editor cannot express.
                    lesson.prerequisite = None
                lesson.chapter = target_chapter
            lesson.order = max(order, 0)
            lesson.save(update_fields=['chapter', 'order', 'prerequisite', 'updated_at'])
            # Dense re-numbering keeps the stored order unambiguous after an insert.
            renumber = list(target_chapter.lessons.order_by('order', 'pk'))
            for index, row in enumerate(renumber, start=1):
                row.order = index
            Lesson.objects.bulk_update(renumber, ['order'])
        record_admin_action(request.user, 'lesson.move', obj=lesson, label=lesson.title,
                            detail={'to_chapter': target_chapter.pk, 'order': lesson.order},
                            request=request)
        return Response(self._lesson_payload(lesson))

    @action(detail=True, methods=['post'], url_path='lessons/reorder')
    def reorder_lessons(self, request, pk=None):
        """Reorder lessons, optionally moving them between chapters of this course.

        Payload: ``{"items": [{"id": 5, "chapter": 2, "order": 1}, ...]}``. Every id is
        checked against the course before anything is written, so a partial or hostile
        list cannot touch rows this caller does not own.
        """
        course = self.get_object()
        items = request.data.get('items') or []
        if not isinstance(items, list):
            return Response({'detail': '"items" must be a list.'},
                            status=status.HTTP_400_BAD_REQUEST)
        cleaned = []
        for entry in items:
            if not isinstance(entry, dict):
                return Response({'detail': 'Each item must be an object.'},
                                status=status.HTTP_400_BAD_REQUEST)
            try:
                lesson_id = int(entry['id'])
                order = int(entry.get('order'))
            except (KeyError, TypeError, ValueError):
                return Response({'detail': 'Each item needs numeric "id" and "order".'},
                                status=status.HTTP_400_BAD_REQUEST)
            chapter_id = entry.get('chapter')
            cleaned.append({
                'id': lesson_id,
                'order': max(order, 0),
                'chapter': int(chapter_id) if chapter_id not in (None, '') else None,
            })

        ids = [entry['id'] for entry in cleaned]
        allowed_chapters = set(course.chapters.values_list('pk', flat=True))
        with transaction.atomic():
            lessons = {l.pk: l for l in Lesson.objects.select_for_update().filter(
                pk__in=ids, chapter__course=course
            )}
            missing = [i for i in ids if i not in lessons]
            if missing:
                return Response({
                    'detail': 'Lessons outside this course cannot be reordered here.',
                    'code': 'foreign_lesson', 'ids': missing,
                }, status=status.HTTP_400_BAD_REQUEST)
            foreign = [
                entry for entry in cleaned
                if entry['chapter'] is not None and entry['chapter'] not in allowed_chapters
            ]
            if foreign:
                return Response({
                    'detail': 'Destination chapter is not part of this course.',
                    'code': 'foreign_chapter',
                }, status=status.HTTP_400_BAD_REQUEST)

            rows = []
            for entry in cleaned:
                lesson = lessons[entry['id']]
                if entry['chapter'] is not None and entry['chapter'] != lesson.chapter_id:
                    target = Chapter.objects.get(pk=entry['chapter'], course=course)
                    if lesson.prerequisite_id and lesson.prerequisite.chapter_id != target.pk:
                        lesson.prerequisite = None
                    lesson.chapter = target
                lesson.order = entry['order']
                rows.append(lesson)
            Lesson.objects.bulk_update(rows, ['order', 'chapter', 'prerequisite'])
        record_admin_action(request.user, 'lesson.reorder', obj=course, label=course.title,
                            detail={'count': len(cleaned)}, request=request)
        return Response({'status': 'ok', 'reordered': len(cleaned)})

    @action(detail=True, methods=['post'], url_path='lessons/bulk-publish')
    def bulk_publish_lessons(self, request, pk=None):
        """Publish or draft a set of lessons at once (spec 3.3 'bulk publish lessons').

        XP is untouched: publishing changes visibility only. Rewards stay the business
        of ``services.xp.award_xp``, whose unique XPTransaction guard is what actually
        prevents a learner being paid twice for the same lesson.
        """
        course = self.get_object()
        ids = _coerce_int_list(request.data, 'lessons')
        publish = bool(request.data.get('is_active', True))
        if not ids:
            return Response({'detail': 'No lessons selected.'}, status=status.HTTP_400_BAD_REQUEST)
        with transaction.atomic():
            queryset = Lesson.objects.filter(pk__in=ids, chapter__course=course)
            if queryset.count() != len(set(ids)):
                return Response({
                    'detail': 'Some lessons are not part of this course.',
                    'code': 'foreign_lesson',
                }, status=status.HTTP_400_BAD_REQUEST)
            updated = queryset.update(is_active=publish)
        record_admin_action(request.user, 'lesson.bulk_publish', obj=course,
                            label=course.title,
                            detail={'count': updated, 'is_active': publish}, request=request)
        return Response({
            'status': 'ok',
            'updated': updated,
            'checklist': publishing.run_publish_check(course),
        })

    # ── Exercises ──────────────────────────────────────────────────────────────

    def _get_exercise(self, course, lesson_pk, exercise_pk):
        return get_object_or_404(
            Exercise, pk=exercise_pk, lesson_id=lesson_pk, lesson__chapter__course=course,
        )

    @action(detail=True, methods=['post'], url_path=r'lessons/(?P<lesson_pk>[0-9]+)/exercises')
    def create_exercise(self, request, pk=None, lesson_pk=None):
        course = self.get_object()
        lesson = self._get_lesson(course, lesson_pk)
        serializer = ExerciseStudioSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        slug = unique_slug(
            Exercise, request.data.get('slug') or request.data.get('title', 'exercise'),
            lesson=lesson,
        )
        exercise = serializer.save(lesson=lesson, slug=slug)
        record_admin_action(request.user, 'exercise.create', obj=exercise,
                            label=exercise.title, request=request)
        return Response(self._exercise_payload(exercise), status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['patch', 'put'], url_path=r'lessons/(?P<lesson_pk>[0-9]+)/exercises/(?P<exercise_pk>[0-9]+)')
    def update_exercise(self, request, pk=None, lesson_pk=None, exercise_pk=None):
        course = self.get_object()
        exercise = self._get_exercise(course, lesson_pk, exercise_pk)
        serializer = ExerciseStudioSerializer(exercise, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        exercise = serializer.save()
        record_admin_action(request.user, 'exercise.update', obj=exercise,
                            label=exercise.title, request=request)
        return Response(self._exercise_payload(exercise))

    @action(detail=True, methods=['delete'], url_path=r'lessons/(?P<lesson_pk>[0-9]+)/exercises/(?P<exercise_pk>[0-9]+)')
    def destroy_exercise(self, request, pk=None, lesson_pk=None, exercise_pk=None):
        course = self.get_object()
        exercise = self._get_exercise(course, lesson_pk, exercise_pk)
        label = exercise.title
        exercise.delete()
        record_admin_action(request.user, 'exercise.delete', obj=course,
                            label=label, detail={'lesson': exercise.lesson_id}, request=request)
        return Response(status=status.HTTP_204_NO_CONTENT)

    # ── Publishing ────────────────────────────────────────────────────────────

    @action(detail=True, methods=['get'])
    def checklist(self, request, pk=None):
        course = self.get_object()
        return Response(publishing.run_publish_check(course))

    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        course = self.get_object()
        report = publishing.run_publish_check(course)
        force = str(request.data.get('force', '')).lower() in ('1', 'true', 'yes')
        reason = str(request.data.get('reason') or request.data.get('override_reason') or '').strip()
        if not report['ok'] and not force:
            return Response({
                'detail': 'This course is not ready to publish.',
                'code': 'publish_blocked',
                'blocking': report['blocking'],
                'warnings': report['warnings'],
            }, status=status.HTTP_400_BAD_REQUEST)
        if not report['ok'] and not reason:
            # Publishing past a blocking issue is a deliberate override, so it has to
            # say why. The reason lands in the audit row and the checklist that stays
            # visible afterwards; without it an override is just an unexplained bug.
            return Response({
                'detail': 'An override reason is required to publish a course that '
                          'fails validation.',
                'code': 'override_reason_required',
                'blocking': report['blocking'],
            }, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            course.is_published = True
            course.is_active = True
            course.published_at = timezone.now()
            course.publish_at = None
            course.archived_at = None
            course.save(update_fields=[
                'is_published', 'is_active', 'published_at', 'publish_at', 'archived_at',
                'updated_at',
            ])
            record_admin_action(
                request.user, 'course.publish', obj=course, label=course.title,
                detail={
                    'forced': not report['ok'],
                    'override_reason': reason,
                    'blocking_at_override': [i['code'] for i in report['blocking']],
                    'warning_codes': [i['code'] for i in report['warnings']],
                },
                request=request,
            )
        return Response({'status': 'published', 'checklist': report,
                         'course': self._bundle_payload(course)['course']})

    @action(detail=True, methods=['post'])
    def unpublish(self, request, pk=None):
        course = self.get_object()
        course.is_published = False
        course.publish_at = None
        course.save(update_fields=['is_published', 'publish_at', 'updated_at'])
        record_admin_action(request.user, 'course.unpublish', obj=course,
                            label=course.title, request=request)
        return Response({'status': 'draft',
                         'course': self._bundle_payload(course)['course']})

    @action(detail=True, methods=['post'])
    def schedule(self, request, pk=None):
        course = self.get_object()
        publish_at = _parse_dt(request.data.get('publish_at'))
        if publish_at is None:
            return Response({'detail': 'A valid publish_at date-time is required.'},
                            status=status.HTTP_400_BAD_REQUEST)
        report = publishing.run_publish_check(course)
        if not report['ok']:
            # Scheduling is a promise to publish, so the same content rules apply now
            # rather than at 02:00 when nobody is watching.
            return Response({
                'detail': 'Fix the blocking issues before scheduling publication.',
                'code': 'publish_blocked',
                'blocking': report['blocking'],
                'warnings': report['warnings'],
            }, status=status.HTTP_400_BAD_REQUEST)
        with transaction.atomic():
            course.publish_at = publish_at
            course.is_published = False
            course.save(update_fields=['publish_at', 'is_published', 'updated_at'])
            record_admin_action(request.user, 'course.schedule', obj=course,
                                label=course.title,
                                detail={'publish_at': publish_at.isoformat()}, request=request)
        return Response({'status': 'scheduled',
                         'course': self._bundle_payload(course)['course']})

    @action(detail=True, methods=['post'])
    def unschedule(self, request, pk=None):
        course = self.get_object()
        course.publish_at = None
        course.save(update_fields=['publish_at', 'updated_at'])
        record_admin_action(request.user, 'course.unschedule', obj=course,
                            label=course.title, request=request)
        return Response({'status': 'unscheduled',
                         'course': self._bundle_payload(course)['course']})

    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        course = self.get_object()
        with transaction.atomic():
            course.is_published = False
            course.is_active = False
            course.archived_at = timezone.now()
            course.publish_at = None
            course.save(update_fields=[
                'is_published', 'is_active', 'archived_at', 'publish_at', 'updated_at',
            ])
            record_admin_action(request.user, 'course.archive', obj=course,
                                label=course.title, request=request)
        return Response({'status': 'archived',
                         'course': self._bundle_payload(course)['course']})

    @action(detail=True, methods=['post'])
    def unarchive(self, request, pk=None):
        course = self.get_object()
        course.archived_at = None
        course.is_active = True
        course.save(update_fields=['archived_at', 'is_active', 'updated_at'])
        record_admin_action(request.user, 'course.unarchive', obj=course,
                            label=course.title, request=request)
        return Response({'status': 'restored',
                         'course': self._bundle_payload(course)['course']})

    # ── Internals ─────────────────────────────────────────────────────────────

    def _get_chapter(self, course, chapter_pk):
        return get_object_or_404(Chapter, pk=chapter_pk, course=course)

    def _get_lesson(self, course, lesson_pk):
        return get_object_or_404(Lesson, pk=lesson_pk, chapter__course=course)

    def _validated_orders(self, request, model, *, course_filter):
        """Turn ``{"items": [{"id":1,"order":2}]}`` into ``{id: order}``, scope-checked."""
        items = request.data.get('items') or []
        if not isinstance(items, list):
            raise ValueError('"items" must be a list.')
        mapping = {}
        for entry in items:
            if not isinstance(entry, dict):
                raise ValueError('Each item must be an object.')
            try:
                mapping[int(entry['id'])] = max(int(entry.get('order')), 0)
            except (KeyError, TypeError, ValueError):
                raise ValueError('Each item needs numeric "id" and "order".')
        if mapping:
            allowed = set(model.objects.filter(**course_filter).filter(pk__in=mapping)
                          .values_list('pk', flat=True))
            foreign = [pk for pk in mapping if pk not in allowed]
            if foreign:
                raise ValueError('Refusing to reorder rows outside this course.')
        return mapping

    def _chapter_payload(self, chapter, include_lessons=False):
        data = {
            'id': chapter.pk,
            'title': chapter.title,
            'slug': chapter.slug,
            'description': chapter.description,
            'order': chapter.order,
            'xp_reward': chapter.xp_reward,
            'is_active': chapter.is_active,
            'source_type': chapter.source_type,
            'verification_status': chapter.verification_status,
            'publication_state': chapter.publication_state,
            'lesson_count': chapter.lesson_count,
            'published_lesson_count': chapter.published_lesson_count,
        }
        if include_lessons:
            data['lessons'] = [
                self._lesson_payload(lesson)
                for lesson in chapter.lessons.order_by('order', 'pk')
            ]
        return data

    def _lesson_payload(self, lesson):
        return {
            'id': lesson.pk,
            'chapter': lesson.chapter_id,
            'title': lesson.title,
            'slug': lesson.slug,
            'content_type': lesson.content_type,
            'learning_objective': lesson.learning_objective,
            'content_body': lesson.content_body,
            'video_url': lesson.video_url,
            'video_duration_seconds': lesson.video_duration_seconds,
            'order': lesson.order,
            'duration_minutes': lesson.duration_minutes,
            'estimated_reading_minutes': lesson.estimated_reading_minutes,
            'xp_reward': lesson.xp_reward,
            'is_free_preview': lesson.is_free_preview,
            'is_active': lesson.is_active,
            'is_required': lesson.is_required,
            'prerequisite': lesson.prerequisite_id,
            'completion_condition': lesson.completion_condition or {},
            'instructor_notes': lesson.instructor_notes,
            'source_type': lesson.source_type,
            'verification_status': lesson.verification_status,
            'exercise_count': lesson.exercises.count(),
            'updated_at': lesson.updated_at.isoformat(),
        }

    def _exercise_payload(self, exercise):
        return {
            'id': exercise.pk,
            'lesson': exercise.lesson_id,
            'title': exercise.title,
            'slug': exercise.slug,
            'exercise_type': exercise.exercise_type,
            'instructions': exercise.instructions,
            'context': exercise.context,
            'constraints': exercise.constraints,
            'expected_behavior': exercise.expected_behavior,
            'explain': exercise.explain,
            'difficulty': exercise.difficulty,
            'language': exercise.language,
            'starter_code': exercise.starter_code,
            'solution_code': exercise.solution_code,
            'expected_output': exercise.expected_output,
            'choices': exercise.choices or [],
            'test_cases': exercise.test_cases or [],
            'hidden_tests': exercise.hidden_tests or [],
            'xp_reward': exercise.xp_reward,
            'max_attempts': exercise.max_attempts,
            'is_final_assessment': exercise.is_final_assessment,
            'order': exercise.order,
            'is_active': exercise.is_active,
            'updated_at': exercise.updated_at.isoformat(),
        }

    def _copy_chapter(self, chapter, course, *, with_lessons=True):
        return copy_chapter(chapter, course, with_lessons=with_lessons)

    def _copy_lesson(self, lesson, chapter, *, with_exercises=True):
        return copy_lesson(lesson, chapter, with_exercises=with_exercises)


def copy_lesson(lesson, chapter, *, with_exercises=True, keep_visibility=False):
    """Clone a lesson, including its exercises.

    The original course-level ``duplicate()`` copied chapters and lessons but dropped
    every exercise, so a duplicated course quietly lost all of its practice work - the
    kind of data loss that stays invisible until a learner complains.

    ``keep_visibility`` is False by design: a clone starts as a draft, because nobody
    has reviewed it yet and auto-publishing somebody's copy is how unfinished lessons
    reach students.
    """
    copy = Lesson.objects.create(
        chapter=chapter,
        title=(lesson.title if keep_visibility else f'{lesson.title} (copy)'),
        slug=unique_slug(Lesson, lesson.slug, chapter=chapter),
        content_type=lesson.content_type,
        learning_objective=lesson.learning_objective,
        content_body=lesson.content_body,
        video_url=lesson.video_url,
        video_duration_seconds=lesson.video_duration_seconds,
        order=lesson.order + 1,
        duration_minutes=lesson.duration_minutes,
        xp_reward=lesson.xp_reward,
        is_free_preview=lesson.is_free_preview,
        is_active=bool(lesson.is_active and keep_visibility),
        is_required=lesson.is_required,
        estimated_reading_minutes=lesson.estimated_reading_minutes,
        completion_condition=dict(lesson.completion_condition or {}),
        instructor_notes=lesson.instructor_notes,
        source_type=lesson.source_type,
        verification_status=lesson.verification_status,
        textbook_board=lesson.textbook_board,
        textbook_class=lesson.textbook_class,
        textbook_unit=lesson.textbook_unit,
        textbook_topic=lesson.textbook_topic,
        textbook_pages=lesson.textbook_pages,
    )
    if with_exercises:
        for exercise in lesson.exercises.order_by('order', 'pk'):
            Exercise.objects.create(
                lesson=copy,
                title=exercise.title,
                slug=unique_slug(Exercise, exercise.slug, lesson=copy),
                exercise_type=exercise.exercise_type,
                instructions=exercise.instructions,
                context=exercise.context,
                constraints=exercise.constraints,
                expected_behavior=exercise.expected_behavior,
                explain=exercise.explain,
                difficulty=exercise.difficulty,
                language=exercise.language,
                starter_code=exercise.starter_code,
                solution_code=exercise.solution_code,
                expected_output=exercise.expected_output,
                choices=list(exercise.choices or []),
                test_cases=list(exercise.test_cases or []),
                hidden_tests=list(exercise.hidden_tests or []),
                xp_reward=exercise.xp_reward,
                max_attempts=exercise.max_attempts,
                is_final_assessment=exercise.is_final_assessment,
                order=exercise.order,
                is_active=bool(exercise.is_active and keep_visibility),
                source_type=exercise.source_type,
                verification_status=exercise.verification_status,
                textbook_board=exercise.textbook_board,
                textbook_class=exercise.textbook_class,
                textbook_unit=exercise.textbook_unit,
                textbook_topic=exercise.textbook_topic,
                textbook_pages=exercise.textbook_pages,
            )
    return copy


def copy_chapter(chapter, course, *, with_lessons=True, keep_visibility=False):
    copy = Chapter.objects.create(
        course=course,
        title=(chapter.title if keep_visibility else f'{chapter.title} (copy)'),
        slug=unique_slug(Chapter, chapter.slug, course=course),
        description=chapter.description,
        order=chapter.order + 1,
        xp_reward=chapter.xp_reward,
        is_active=bool(chapter.is_active and keep_visibility),
        source_type=chapter.source_type,
        verification_status=chapter.verification_status,
        textbook_board=chapter.textbook_board,
        textbook_class=chapter.textbook_class,
        textbook_unit=chapter.textbook_unit,
        textbook_topic=chapter.textbook_topic,
        textbook_pages=chapter.textbook_pages,
    )
    if with_lessons:
        for lesson in chapter.lessons.order_by('order', 'pk'):
            copy_lesson(lesson, copy, keep_visibility=keep_visibility)
    return copy


def duplicate_course(course, *, actor=None, keep_visibility=False):
    """Deep-copy a course with chapters, lessons, exercises and resources.

    Module-level rather than view-only so the legacy ``CourseAdminViewSet.duplicate``
    action and the studio share one implementation instead of two half-correct ones.
    """
    with transaction.atomic():
        copy = Course.objects.create(
            slug=unique_slug(Course, course.slug),
            title=f'{course.title} (Copy)',
            subtitle=course.subtitle,
            description=course.description,
            thumbnail=course.thumbnail,
            cover_image=course.cover_image.name if course.cover_image else '',
            track=course.track,
            category=course.category,
            academic_class=course.academic_class,
            difficulty=course.difficulty,
            language=course.language,
            instructor=course.instructor,
            instructor_user=course.instructor_user,
            prerequisites=course.prerequisites,
            learning_objectives=list(course.learning_objectives or []),
            tags=list(course.tags or []),
            is_free=course.is_free,
            order=course.order + 1,
            # A copy is always a draft: publishing someone's duplicate automatically
            # is how unreviewed content reaches students.
            is_published=bool(course.is_published and keep_visibility),
            is_active=True,
            certification_enabled=course.certification_enabled,
            certification_passing_score=course.certification_passing_score,
            require_all_lessons=course.require_all_lessons,
            require_final_assessment=course.require_final_assessment,
            sequential_learning=course.sequential_learning,
            xp_completion_reward=course.xp_completion_reward,
            manual_estimated_hours=course.manual_estimated_hours,
            created_by=actor,
        )
        for chapter in course.chapters.order_by('order', 'pk'):
            copy_chapter(chapter, copy, keep_visibility=keep_visibility)
        for resource in course.resources.order_by('order', 'pk'):
            Resource.objects.create(
                course=copy,
                title=resource.title,
                description=resource.description,
                resource_type=resource.resource_type,
                file_url=resource.file_url,
                file_name=resource.file_name,
                file_size=resource.file_size,
                order=resource.order,
                is_active=False,
            )
        copy.prerequisite_courses.set(list(course.prerequisite_courses.all()))
    return copy


class CourseCategorySerializer(serializers.ModelSerializer):
    course_count = serializers.SerializerMethodField()
    slug = serializers.SlugField(required=False, allow_blank=True)

    class Meta:
        model = CourseCategory
        fields = ['id', 'slug', 'title', 'order', 'is_active', 'course_count']
        read_only_fields = ['id']

    def validate_slug(self, value):
        """Suffix a colliding slug instead of refusing the whole create.

        The model declares ``slug`` unique, so DRF would otherwise reject a second
        "Databases" category with a field error. Categories are typed by hand by
        people who mean "another bucket with the same name", so the row is given a
        free suffix - same rule the studio applies to duplicated courses.
        """
        title = (self.initial_data.get('title') or '').strip() if self.initial_data else ''
        base = (value or '').strip() or slugify(title)
        if not base:
            raise serializers.ValidationError('A category needs a title or a slug.')
        return unique_slug(CourseCategory, base, exclude_pk=self.instance.pk if self.instance else None)

    def validate_title(self, value):
        if not (value or '').strip():
            raise serializers.ValidationError('The category needs a title.')
        return value.strip()

    def get_course_count(self, obj):
        # Annotated by the viewset's queryset so the list stays a single query.
        return getattr(obj, 'course_count', None) or obj.courses.count()


class CourseCategoryViewSet(viewsets.ModelViewSet):
    """Configurable course categories (spec 3.1: "categories should be configurable")."""

    queryset = CourseCategory.objects.annotate(course_count=Count('courses')).order_by('order', 'title')
    serializer_class = CourseCategorySerializer
    permission_classes = [HasAdminCapability]
    required_admin_capability = COURSE_STUDIO_VIEW

    def get_permissions(self):
        self.required_admin_capability = (
            COURSE_STUDIO_VIEW if self.action == 'list' else COURSE_STUDIO_EDIT
        )
        return [HasAdminCapability()]

    def perform_create(self, serializer):
        validated = dict(serializer.validated_data)
        # Categories are typed by hand in the studio, so two editors can invent the
        # same slug. Suffixing keeps the create succeeding instead of bouncing a
        # uniqueness error back at somebody who only wanted a new bucket.
        base = validated.get('slug') or validated.get('title', 'category')
        category = serializer.save(slug=unique_slug(CourseCategory, base))
        record_admin_action(self.request.user, 'category.create', obj=category,
                            label=category.title, request=self.request)

    def perform_destroy(self, instance):
        course = Course.objects.filter(category=instance).first()
        if course is not None:
            # ``category`` is SET_NULL, so this is safe - but an editor should be told
            # that the category is in use rather than watch courses silently go blank.
            record_admin_action(
                self.request.user, 'category.delete_in_use', obj=instance,
                label=instance.title,
                detail={'courses_affected': Course.objects.filter(category=instance).count()},
                request=self.request,
            )
        instance.delete()
