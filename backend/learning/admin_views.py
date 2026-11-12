"""
Admin REST API views for Code Yaar platform administration.

All endpoints are guarded by IsAdministrator (or higher-privilege checks).
They reuse the existing models, serializers, and business logic.
"""
import logging

from django.conf import settings
from django.contrib.auth.models import User
from django.db import DatabaseError, transaction
from django.core.cache import cache
from django.shortcuts import get_object_or_404
from django.db.models import Count, Sum, Q, Avg, F
from django.utils import timezone
from django.utils.text import slugify
from rest_framework import viewsets, permissions, status, filters, serializers
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.throttling import ScopedRateThrottle

logger = logging.getLogger(__name__)

from .models import (
    UserProfile, CareerTrack, Course, Chapter, Lesson, Exercise,
    Resource, Challenge, Enrollment, Achievement, UserAchievement,
    Certification, UserCertification, Competition, UserNotification,
    AuthenticationAuditLog, Announcement, LessonProgress, PlatformSetting, MaintenanceSettings, Practical, PracticalClass, PracticalSubject,
    CompetitionRegistration, RegistrationFormField, PlatformUpdate,
    EmailCampaign, EmailCampaignRecipient, EmailTemplate, EmailTheme, EmailAutomationRule,
    record_admin_action,
    seed_default_registration_fields,
)
from .permissions import (
    HasAdminCapability, IsAdministrator, IsSuperAdmin, ScopedCourseAccess,
)
from .services.auth import audit, user_role, ADMIN_GROUP, INSTRUCTOR_GROUP
from .services import email_campaigns, email_composer, publishing
from .services.admin_access import (
    ROLE_GROUPS, PLATFORM_CONFIG, ROLES_MANAGE, admin_roles as resolve_admin_roles,
    capabilities as resolve_capabilities, can_manage_roles, has_capability,
)
from .services.notifications import notify
from .serializers import (
    CareerTrackSerializer, CourseListSerializer, CourseDetailSerializer,
    ChapterListSerializer, ChapterDetailSerializer, LessonListSerializer,
    LessonDetailSerializer, ExerciseListSerializer, ExerciseDetailSerializer,
    ResourceSerializer, ChallengeSerializer, ChallengeDetailSerializer,
    PracticalClassAdminSerializer, PracticalSubjectAdminSerializer,
    PracticalAdminSerializer, AchievementSerializer,
)


# ─── Dashboard ─────────────────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsAdministrator])
def admin_dashboard_stats(request):
    """Return aggregate platform statistics."""
    cache_key = 'admin-dashboard-stats-v1'
    cached = cache.get(cache_key)
    if cached is not None:
        return Response(cached)
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()

        student_counts = UserProfile.objects.filter(role='student').aggregate(
            total=Count('id'),
            active=Count(
                'id',
                filter=Q(last_active_at__gte=timezone.now() - timezone.timedelta(days=7)),
            ),
        )
        course_counts = Course.objects.aggregate(
            total=Count('id', filter=Q(is_active=True)),
            published=Count('id', filter=Q(is_active=True, is_published=True)),
            scheduled=Count('id', filter=Q(publish_at__isnull=False, is_published=False)),
            archived=Count('id', filter=Q(archived_at__isnull=False)),
        )
        track_counts = CareerTrack.objects.aggregate(
            total=Count('id'),
            published=Count('id', filter=Q(is_published=True)),
        )
        enrollment_counts = Enrollment.objects.aggregate(
            total=Count('id'),
            active=Count('id', filter=Q(status='active')),
            completed=Count('id', filter=Q(status='completed')),
        )

        total_assessments = Exercise.objects.filter(
            is_final_assessment=True, is_active=True
        ).count()

        total_challenges = Challenge.objects.filter(is_active=True).count()

        # Cards the specification lists that this endpoint did not answer: how much content
        # exists at all, how many registrations are waiting on a human, and how many courses
        # are queued to publish themselves. Each is one COUNT, no joins beyond the table.
        total_lessons = Lesson.objects.filter(is_active=True).count()
        pending_registrations = CompetitionRegistration.objects.filter(
            registration_status='pending',
        ).count()
        certificates_issued = UserCertification.objects.count()

        active_competitions = Competition.objects.filter(
            is_published=True
        ).count()

        payload = {
            'totalStudents': student_counts['total'],
            'activeStudents': student_counts['active'],
            'totalCourses': course_counts['total'],
            'publishedCourses': course_counts['published'],
            'totalTracks': track_counts['total'],
            'publishedTracks': track_counts['published'],
            'totalEnrollments': enrollment_counts['total'],
            'activeEnrollments': enrollment_counts['active'],
            'completedCourses': enrollment_counts['completed'],
            'totalAssessments': total_assessments,
            'totalChallenges': total_challenges,
            'totalLessons': total_lessons,
            'pendingRegistrations': pending_registrations,
            'scheduledCourses': course_counts['scheduled'],
            'archivedCourses': course_counts['archived'],
            'certificatesIssued': certificates_issued,
            'activeCompetitions': active_competitions,
        }
    except DatabaseError:
        logger.exception('admin-dashboard-stats database failure')
        return Response({'detail': 'Database temporarily unavailable.'}, status=503)
    cache.set(cache_key, payload, 15)
    return Response(payload)


@api_view(['GET'])
@permission_classes([IsAdministrator])
def admin_recent_activity(request):
    """Return recent administrative activity."""
    try:
        limit = min(max(int(request.query_params.get('limit', 20)), 1), 100)
    except (TypeError, ValueError):
        return Response({'detail': 'limit must be a positive integer.'}, status=400)
    cache_key = f'admin-recent-activity-v1-{limit}'
    cached = cache.get(cache_key)
    if cached is not None:
        return Response(cached)

    try:
        logs = AuthenticationAuditLog.objects.select_related('user').order_by('-created_at')[:limit]

        activities = []
        for log in logs:
            activities.append({
                'id': str(log.id),
                'action': log.event,
                'admin': log.user.username if log.user else 'System',
                'target': log.identifier or '',
                'timestamp': log.created_at.isoformat(),
                'metadata': log.metadata or {},
            })
    except DatabaseError:
        logger.exception('admin-recent-activity database failure')
        return Response({'detail': 'Database temporarily unavailable.'}, status=503)

    cache.set(cache_key, activities, 15)
    return Response(activities)


@api_view(['GET'])
@permission_classes([IsAdministrator])
def admin_top_courses(request):
    """Return top courses by enrollment count."""
    try:
        limit = min(max(int(request.query_params.get('limit', 10)), 1), 100)
    except (TypeError, ValueError):
        return Response({'detail': 'limit must be a positive integer.'}, status=400)
    cache_key = f'admin-top-courses-v2-{limit}'
    cached = cache.get(cache_key)
    if cached is not None:
        return Response(cached)

    try:
        courses = Course.objects.filter(is_active=True).select_related('track').annotate(
            enrollment_count=Count('enrollments'),
            completed_count=Count('enrollments', filter=Q(enrollments__status='completed')),
            total_lessons=Count(
                'chapters__lessons',
                filter=Q(chapters__is_active=True, chapters__lessons__is_active=True),
                distinct=True,
            ),
            completed_lessons=Count(
                'chapters__lessons__progress_entries',
                filter=Q(
                    chapters__is_active=True,
                    chapters__lessons__is_active=True,
                    chapters__lessons__progress_entries__status='completed',
                ),
                distinct=True,
            ),
        ).order_by('-enrollment_count')[:limit]

        result = []
        for course in courses:
            total_lessons = course.total_lessons
            completed_lessons = course.completed_lessons if total_lessons > 0 else 0
            completion_rate = round((completed_lessons / total_lessons) * 100) if total_lessons > 0 else 0

            result.append({
                'id': course.id,
                'title': course.title,
                'track': course.track.title,
            'enrollments': course.enrollment_count,
            'completionRate': completion_rate,
        })

    cache.set(cache_key, result, 15)
    return Response(result)


# ─── Career Tracks (Admin) ─────────────────────────────────────────────────────

class CareerTrackAdminSerializer(serializers.ModelSerializer):
    courses_count = serializers.SerializerMethodField()
    published_courses_count = serializers.SerializerMethodField()

    class Meta:
        model = CareerTrack
        fields = [
            'id', 'slug', 'title', 'description', 'icon', 'category',
            'cover_image', 'learning_objectives', 'difficulty',
            'estimated_hours', 'order', 'is_published', 'is_active',
            'created_at', 'updated_at', 'courses_count', 'published_courses_count',
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']

    def create(self, validated_data):
        title = validated_data.get('title', '')
        base_slug = slugify(title) or 'track'
        slug = base_slug
        suffix = 2
        while CareerTrack.objects.filter(slug=slug).exists():
            slug = f'{base_slug}-{suffix}'
            suffix += 1
        validated_data['slug'] = slug
        return super().create(validated_data)

    def get_courses_count(self, obj):
        return obj.admin_courses_count if hasattr(obj, 'admin_courses_count') else obj.courses.count()

    def get_published_courses_count(self, obj):
        if hasattr(obj, 'admin_published_courses_count'):
            return obj.admin_published_courses_count
        return obj.courses.filter(is_active=True, is_published=True).count()


class CareerTrackAdminViewSet(viewsets.ModelViewSet):
    # Explicit ordering: the aggregate annotations below descope the
    # model's Meta ordering, which would otherwise page nondeterministically.
    queryset = CareerTrack.objects.order_by('order', 'title').annotate(
        admin_courses_count=Count('courses', distinct=True),
        admin_published_courses_count=Count(
            'courses',
            filter=Q(courses__is_active=True, courses__is_published=True),
            distinct=True,
        ),
    )
    serializer_class = CareerTrackAdminSerializer
    permission_classes = [IsAdministrator]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'slug']
    ordering_fields = ['title', 'order', 'created_at']

    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        track = self.get_object()
        track.is_published = True
        track.is_active = True
        track.save(update_fields=['is_published', 'is_active'])
        return Response(self.get_serializer(track).data)

    @action(detail=True, methods=['post'])
    def unpublish(self, request, pk=None):
        track = self.get_object()
        track.is_published = False
        track.save(update_fields=['is_published'])
        return Response(self.get_serializer(track).data)

    @action(detail=False, methods=['post'])
    def reorder(self, request):
        items = request.data.get('items', [])
        with transaction.atomic():
            for item in items:
                CareerTrack.objects.filter(id=item['id']).update(order=item['order'])
        return Response({'status': 'ok'})


# ─── Courses (Admin) ───────────────────────────────────────────────────────────

class CourseAdminSerializer(serializers.ModelSerializer):
    track_title = serializers.CharField(source='track.title', read_only=True)
    chapter_count = serializers.SerializerMethodField()
    lesson_count = serializers.SerializerMethodField()
    exercise_count = serializers.SerializerMethodField()
    enrollment_count = serializers.SerializerMethodField()
    completion_rate = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            'id', 'slug', 'title', 'subtitle', 'description', 'thumbnail',
            'track', 'track_title', 'academic_class', 'difficulty', 'language',
            'instructor', 'prerequisites', 'learning_objectives', 'is_free',
            'order', 'is_published', 'is_active', 'certification_enabled',
            'certification_passing_score', 'require_all_lessons',
            'require_final_assessment', 'created_at', 'updated_at',
            'chapter_count', 'lesson_count', 'exercise_count',
            'enrollment_count', 'completion_rate',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_chapter_count(self, obj):
        if hasattr(obj, 'admin_chapter_count'):
            return obj.admin_chapter_count
        return obj.chapters.count()

    def get_lesson_count(self, obj):
        if hasattr(obj, 'admin_lesson_count'):
            return obj.admin_lesson_count
        return Lesson.objects.filter(chapter__course=obj).count()

    def get_exercise_count(self, obj):
        if hasattr(obj, 'admin_exercise_count'):
            return obj.admin_exercise_count
        return Exercise.objects.filter(lesson__chapter__course=obj).count()

    def get_enrollment_count(self, obj):
        if hasattr(obj, 'admin_enrollment_count'):
            return obj.admin_enrollment_count
        return obj.enrollments.count()

    def get_completion_rate(self, obj):
        if hasattr(obj, 'admin_enrollment_count'):
            total = obj.admin_enrollment_count
        else:
            total = obj.enrollments.count()
        if total == 0:
            return 0
        if hasattr(obj, 'admin_completed_enrollment_count'):
            completed = obj.admin_completed_enrollment_count
        else:
            completed = obj.enrollments.filter(status='completed').count()
        return round((completed / total) * 100)


class CourseAdminViewSet(viewsets.ModelViewSet):
    # Ordered before the multi-join annotations, which descope Meta ordering.
    queryset = Course.objects.select_related('track').order_by(
        'track', 'order', 'title',
    ).annotate(
        admin_chapter_count=Count('chapters', distinct=True),
        admin_lesson_count=Count('chapters__lessons', distinct=True),
        admin_exercise_count=Count('chapters__lessons__exercises', distinct=True),
        admin_enrollment_count=Count('enrollments', distinct=True),
        admin_completed_enrollment_count=Count(
            'enrollments', filter=Q(enrollments__status='completed'), distinct=True,
        ),
    ).all()
    serializer_class = CourseAdminSerializer
    # ``HasAdminCapability`` with no declared capability resolves to the historical
    # administrator check, so this is the same gate as before - it just no longer has
    # to be re-tightened when a scoped admin role is added to the panel.
    permission_classes = [HasAdminCapability, ScopedCourseAccess]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'subtitle']
    ordering_fields = ['title', 'order', 'created_at']

    def get_queryset(self):
        qs = super().get_queryset()
        track = self.request.query_params.get('track')
        if track:
            qs = qs.filter(track_id=track)
        return qs

    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        """Publish a course, but not through its content problems.

        This used to set ``is_published=True`` with no questions asked, so an empty
        course went live into the student catalogue. ``?force`` still exists for a
        genuine override, and every override is written to the audit log with the
        reason and the exact blockers that were waved away.
        """
        course = self.get_object()
        report = publishing.run_publish_check(course)
        force = str(request.data.get('force', '')).lower() in ('1', 'true', 'yes')
        if not report['ok'] and not force:
            return Response({
                'detail': 'This course is not ready to publish.',
                'code': 'publish_blocked',
                'blocking': report['blocking'],
                'warnings': report['warnings'],
            }, status.HTTP_400_BAD_REQUEST)

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
                'override_reason': request.data.get('reason', ''),
                'blocked_codes': [i['code'] for i in report['blocking']],
                'warning_codes': [i['code'] for i in report['warnings']],
            },
            request=request,
        )
        return Response(self.get_serializer(course).data)

    @action(detail=True, methods=['post'])
    def unpublish(self, request, pk=None):
        course = self.get_object()
        course.is_published = False
        course.publish_at = None
        course.save(update_fields=['is_published', 'publish_at', 'updated_at'])
        record_admin_action(request.user, 'course.unpublish', obj=course,
                            label=course.title, request=request)
        return Response(self.get_serializer(course).data)

    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """Deep-copy a course through the shared studio implementation.

        The previous inline copy walked chapters and lessons but never touched
        exercises, so every duplicated course lost all of its practice work, and its
        ``f"{slug}-copy"`` collided on the second duplicate.
        """
        from .studio_views import duplicate_course

        course = self.get_object()
        copy = duplicate_course(course, actor=request.user)
        record_admin_action(request.user, 'course.duplicate', obj=copy, label=copy.title,
                            detail={'source_course': course.pk}, request=request)
        return Response(self.get_serializer(copy).data, status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'])
    def chapters(self, request, pk=None):
        course = self.get_object()
        chapters = course.chapters.all().order_by('order')
        serializer = ChapterAdminSerializer(chapters, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def students(self, request, pk=None):
        course = self.get_object()
        enrollments = Enrollment.objects.filter(course=course).select_related('user', 'user__profile')
        # One grouped query per stat for the whole page instead of three
        # per-student COUNT round trips — the hosted database makes each
        # extra trip visible latency on a course with hundreds of students.
        user_ids = [e.user_id for e in enrollments]
        enrollment_count_map = {
            row['user_id']: row['n']
            for row in Enrollment.objects.filter(user_id__in=user_ids)
            .values('user_id').annotate(n=Count('id'))
        }
        completed_courses_map = {
            row['user_id']: row['n']
            for row in Enrollment.objects.filter(user_id__in=user_ids, status='completed')
            .values('user_id').annotate(n=Count('id'))
        }
        completed_lessons_map = {
            row['user_id']: row['n']
            for row in LessonProgress.objects.filter(user_id__in=user_ids, status='completed')
            .values('user_id').annotate(n=Count('id'))
        }
        students = []
        for e in enrollments:
            profile = getattr(e.user, 'profile', None)
            students.append({
                'id': e.user.id,
                'username': e.user.username,
                'email': e.user.email,
                'first_name': e.user.first_name,
                'last_name': e.user.last_name,
                'full_name': profile.full_name if profile else e.user.username,
                'avatar': profile.avatar_url() if profile else '',
                'role': profile.role if profile else 'student',
                'institution': profile.institution if profile else '',
                'education_level': profile.education_level if profile else '',
                'xp_points': profile.xp_points if profile else 0,
                'streak_days': profile.streak_days if profile else 0,
                'level': profile.level if profile else 1,
                'is_profile_public': profile.is_profile_public if profile else True,
                'date_joined': e.user.date_joined.isoformat(),
                'last_active_at': profile.last_active_at.isoformat() if profile and profile.last_active_at else None,
                'enrollment_count': enrollment_count_map.get(e.user_id, 0),
                'completed_courses': completed_courses_map.get(e.user_id, 0),
                'completed_lessons': completed_lessons_map.get(e.user_id, 0),
            })
        return Response(students)


# ─── Chapters (Admin) ──────────────────────────────────────────────────────────

class ChapterAdminSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True)
    lesson_count = serializers.SerializerMethodField()
    exercise_count = serializers.SerializerMethodField()

    class Meta:
        model = Chapter
        fields = [
            'id', 'title', 'slug', 'description', 'course', 'course_title',
            'order', 'xp_reward', 'is_active', 'source_type',
            'verification_status', 'textbook_board', 'textbook_class',
            'textbook_unit', 'textbook_topic', 'textbook_pages',
            'created_at', 'updated_at', 'lesson_count', 'exercise_count',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_lesson_count(self, obj):
        # The list queryset carries the counts as annotations; per-row
        # COUNTs turn a 20-row page into 40 extra round trips on the
        # hosted database. Direct instantiations fall back to the manager.
        if hasattr(obj, 'admin_lesson_count'):
            return obj.admin_lesson_count
        return obj.lessons.count()

    def get_exercise_count(self, obj):
        if hasattr(obj, 'admin_exercise_count'):
            return obj.admin_exercise_count
        return Exercise.objects.filter(lesson__chapter=obj).count()


class ChapterAdminViewSet(viewsets.ModelViewSet):
    # Ordered before the annotations, which descope Meta ordering.
    queryset = Chapter.objects.select_related('course').order_by('course', 'order', 'title').annotate(
        admin_lesson_count=Count('lessons', distinct=True),
        admin_exercise_count=Count('lessons__exercises', distinct=True),
    )
    serializer_class = ChapterAdminSerializer
    permission_classes = [IsAdministrator]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'slug']
    ordering_fields = ['title', 'order', 'created_at']

    def get_queryset(self):
        qs = super().get_queryset()
        course = self.request.query_params.get('course')
        if course:
            qs = qs.filter(course_id=course)
        return qs

    @action(detail=False, methods=['post'], url_path='reorder')
    def reorder(self, request):
        """Reorder chapters inside one course.

        The previous version wrote ``order`` onto whatever ids the caller sent, with no
        check that those chapters belonged to the course it bothered to read out of the
        payload and then ignore - so one request could renumber rows in an unrelated
        course. Ids are now validated against ``course_id`` before anything is written.
        """
        items = request.data.get('items', [])
        course_id = request.data.get('course_id')
        if not isinstance(items, list):
            return Response({'detail': '"items" must be a list.'}, status.HTTP_400_BAD_REQUEST)
        mapping = {}
        for entry in items:
            if not isinstance(entry, dict):
                return Response({'detail': 'Each item must be an object.'},
                                status.HTTP_400_BAD_REQUEST)
            try:
                mapping[int(entry['id'])] = max(int(entry.get('order')), 0)
            except (KeyError, TypeError, ValueError):
                return Response({'detail': 'Each item needs numeric "id" and "order".'},
                                status.HTTP_400_BAD_REQUEST)
        if not mapping:
            return Response({'detail': 'No chapters supplied.'}, status.HTTP_400_BAD_REQUEST)

        queryset = Chapter.objects.filter(pk__in=mapping)
        if course_id not in (None, ''):
            queryset = queryset.filter(course_id=course_id)
        elif not has_capability(request.user, '*'):
            # Without an explicit course scope, only a platform administrator may
            # renumber chapters, so a scoped role cannot widen its own reach.
            return Response({
                'detail': '"course_id" is required when reordering chapters.',
                'code': 'course_scope_required',
            }, status.HTTP_400_BAD_REQUEST)
        with transaction.atomic():
            rows = list(queryset)
            if len(rows) != len(mapping):
                return Response({
                    'detail': 'Some chapters are outside the supplied course.',
                    'code': 'foreign_chapter',
                }, status.HTTP_400_BAD_REQUEST)
            for chapter in rows:
                chapter.order = mapping[chapter.pk]
            Chapter.objects.bulk_update(rows, ['order'])
        if course_id not in (None, ''):
            course = Course.objects.filter(pk=course_id).first()
            if course is not None:
                record_admin_action(request.user, 'chapter.reorder', obj=course,
                                    label=course.title, detail={'count': len(rows)},
                                    request=request)
        return Response({'status': 'ok', 'reordered': len(rows)})


# ─── Lessons (Admin) ───────────────────────────────────────────────────────────

class LessonAdminSerializer(serializers.ModelSerializer):
    chapter_title = serializers.CharField(source='chapter.title', read_only=True)
    course_title = serializers.CharField(source='chapter.course.title', read_only=True)
    exercise_count = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = [
            'id', 'title', 'slug', 'content_type', 'chapter', 'chapter_title',
            'course_title', 'learning_objective', 'content_body', 'video_url',
            'video_duration_seconds', 'order', 'duration_minutes', 'xp_reward',
            'is_free_preview', 'is_active', 'source_type', 'verification_status',
            'textbook_board', 'textbook_class', 'textbook_unit', 'textbook_topic',
            'textbook_pages', 'created_at', 'updated_at', 'exercise_count',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_exercise_count(self, obj):
        # The list queryset carries the count as an annotation; per-row
        # COUNTs turn a 20-row page into 20 extra round trips on the
        # hosted database. Direct instantiations (retrieve, scripts)
        # fall back to the manager.
        if hasattr(obj, 'admin_exercise_count'):
            return obj.admin_exercise_count
        return obj.exercises.count()


class LessonAdminViewSet(viewsets.ModelViewSet):
    queryset = (
        Lesson.objects.select_related('chapter', 'chapter__course')
        .annotate(admin_exercise_count=Count('exercises', distinct=True))
        .all()
    )
    serializer_class = LessonAdminSerializer
    permission_classes = [IsAdministrator]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'content_body', 'slug']
    ordering_fields = ['title', 'order', 'created_at']

    def get_queryset(self):
        qs = super().get_queryset()
        chapter = self.request.query_params.get('chapter')
        course = self.request.query_params.get('course')
        if chapter:
            qs = qs.filter(chapter_id=chapter)
        if course:
            qs = qs.filter(chapter__course_id=course)
        return qs

    @action(detail=False, methods=['post'], url_path='reorder')
    def reorder(self, request):
        """Reorder lessons, scoped to a course or chapter when supplied.

        Same hardening as chapter reorder: ids are verified against the requested
        scope before any ``order`` value is written, so a caller cannot renumber rows
        it has not named.
        """
        items = request.data.get('items', [])
        if not isinstance(items, list):
            return Response({'detail': '"items" must be a list.'}, status.HTTP_400_BAD_REQUEST)
        mapping = {}
        for entry in items:
            if not isinstance(entry, dict):
                return Response({'detail': 'Each item must be an object.'},
                                status.HTTP_400_BAD_REQUEST)
            try:
                mapping[int(entry['id'])] = max(int(entry.get('order')), 0)
            except (KeyError, TypeError, ValueError):
                return Response({'detail': 'Each item needs numeric "id" and "order".'},
                                status.HTTP_400_BAD_REQUEST)
        if not mapping:
            return Response({'detail': 'No lessons supplied.'}, status.HTTP_400_BAD_REQUEST)

        params = request.query_params
        course_id = request.data.get('course_id') or params.get('course')
        chapter_id = request.data.get('chapter_id') or params.get('chapter')
        queryset = Lesson.objects.filter(pk__in=mapping)
        if chapter_id not in (None, ''):
            queryset = queryset.filter(chapter_id=chapter_id)
        if course_id not in (None, ''):
            queryset = queryset.filter(chapter__course_id=course_id)
        with transaction.atomic():
            rows = list(queryset)
            if len(rows) != len(mapping):
                return Response({
                    'detail': 'Some lessons are outside the supplied scope.',
                    'code': 'foreign_lesson',
                }, status.HTTP_400_BAD_REQUEST)
            for lesson in rows:
                lesson.order = mapping[lesson.pk]
            Lesson.objects.bulk_update(rows, ['order'])
        return Response({'status': 'ok', 'reordered': len(rows)})


# ─── Exercises (Admin) ─────────────────────────────────────────────────────────

class ExerciseAdminSerializer(serializers.ModelSerializer):
    lesson_title = serializers.CharField(source='lesson.title', read_only=True)
    chapter_title = serializers.CharField(source='lesson.chapter.title', read_only=True)
    course_title = serializers.CharField(source='lesson.chapter.course.title', read_only=True)

    class Meta:
        model = Exercise
        fields = [
            'id', 'title', 'slug', 'exercise_type', 'lesson', 'lesson_title',
            'chapter_title', 'course_title', 'instructions', 'context',
            'constraints', 'expected_behavior', 'explain', 'difficulty',
            'language', 'starter_code', 'solution_code', 'expected_output',
            'choices', 'test_cases', 'hidden_tests', 'xp_reward',
            'max_attempts', 'is_final_assessment', 'order', 'is_active',
            'source_type', 'verification_status', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ExerciseAdminViewSet(viewsets.ModelViewSet):
    queryset = Exercise.objects.select_related('lesson', 'lesson__chapter', 'lesson__chapter__course').all()
    serializer_class = ExerciseAdminSerializer
    permission_classes = [IsAdministrator]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'instructions', 'slug']
    ordering_fields = ['title', 'order', 'created_at']

    def get_queryset(self):
        qs = super().get_queryset()
        lesson = self.request.query_params.get('lesson')
        if lesson:
            qs = qs.filter(lesson_id=lesson)
        return qs


# ─── Students (Admin) ──────────────────────────────────────────────────────────

class StudentAdminSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    date_joined = serializers.DateTimeField(source='user.date_joined', read_only=True)
    enrollment_count = serializers.SerializerMethodField()
    completed_courses = serializers.SerializerMethodField()
    completed_lessons = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'full_name',
            'avatar', 'role', 'institution', 'education_level', 'xp_points',
            'streak_days', 'level', 'is_profile_public', 'date_joined',
            'last_active_at', 'enrollment_count', 'completed_courses',
            'completed_lessons',
        ]
        read_only_fields = ['id', 'date_joined']

    def get_enrollment_count(self, obj):
        return obj.admin_enrollment_count if hasattr(obj, 'admin_enrollment_count') else obj.user.enrollments.count()

    def get_completed_courses(self, obj):
        if hasattr(obj, 'admin_completed_courses'):
            return obj.admin_completed_courses
        return obj.user.enrollments.filter(status='completed').count()

    def get_completed_lessons(self, obj):
        if hasattr(obj, 'admin_completed_lessons'):
            return obj.admin_completed_lessons
        return LessonProgress.objects.filter(user=obj.user, status='completed').count()


class StudentAdminViewSet(viewsets.ReadOnlyModelViewSet):
    # Ordered before the annotations, which would otherwise descope Meta
    # ordering and page students nondeterministically.
    queryset = UserProfile.objects.filter(role='student').select_related('user').order_by(
        '-xp_points', 'id',
    ).annotate(
        admin_enrollment_count=Count('user__enrollments', distinct=True),
        admin_completed_courses=Count(
            'user__enrollments',
            filter=Q(user__enrollments__status='completed'),
            distinct=True,
        ),
        admin_completed_lessons=Count(
            'user__lesson_progress',
            filter=Q(user__lesson_progress__status='completed'),
            distinct=True,
        ),
    )
    serializer_class = StudentAdminSerializer
    permission_classes = [IsAdministrator]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['user__username', 'user__email', 'user__first_name', 'user__last_name']
    ordering_fields = ['xp_points', 'level', 'created_at']

    @action(detail=True, methods=['get'])
    def detail(self, request, pk=None):
        profile = self.get_object()
        user = profile.user

        enrollments = Enrollment.objects.filter(user=user).select_related('course', 'course__track')
        enrollment_data = []
        for e in enrollments:
            enrollment_data.append({
                'id': e.id,
                'course': e.course.id,
                'course_title': e.course.title,
                'course_slug': e.course.slug,
                'track_title': e.course.track.title,
                'enrolled_at': e.enrolled_at.isoformat(),
                'completed_at': e.completed_at.isoformat() if e.completed_at else None,
                'last_activity_at': e.last_activity_at.isoformat() if e.last_activity_at else None,
                'status': e.status,
                'progress_percentage': e.progress_percentage,
            })

        achievements = UserAchievement.objects.filter(user=user).select_related('achievement')
        achievement_data = []
        for ua in achievements:
            achievement_data.append({
                'id': ua.id,
                'achievement': {
                    'id': ua.achievement.id,
                    'title': ua.achievement.title,
                    'description': ua.achievement.description,
                    'icon': ua.achievement.icon,
                },
                'earned_at': ua.earned_at.isoformat(),
                'status': ua.status,
            })

        certificates = UserCertification.objects.filter(user=user).select_related('certification')
        certificate_data = []
        for uc in certificates:
            certificate_data.append({
                'id': uc.id,
                'certification': {
                    'id': uc.certification.id,
                    'title': uc.certification.title,
                },
                'earned_at': uc.earned_at.isoformat(),
                'credential_id': uc.credential_id,
            })

        return Response({
            'id': profile.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'full_name': profile.full_name,
            'avatar': profile.avatar_url(),
            'role': profile.role,
            'institution': profile.institution,
            'education_level': profile.education_level,
            'xp_points': profile.xp_points,
            'streak_days': profile.streak_days,
            'level': profile.level,
            'date_joined': user.date_joined.isoformat(),
            'last_active_at': profile.last_active_at.isoformat() if profile.last_active_at else None,
            'enrollments': enrollment_data,
            'achievements': achievement_data,
            'certificates': certificate_data,
        })


# ─── Instructors (Admin) ───────────────────────────────────────────────────────

class InstructorAdminSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    assigned_courses_count = serializers.SerializerMethodField()
    assigned_courses = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'full_name', 'avatar', 'institution', 'assigned_courses_count',
            'assigned_courses',
        ]
        read_only_fields = ['id']

    def get_assigned_courses_count(self, obj):
        return Course.objects.filter(instructor=obj.user.username).count()

    def get_assigned_courses(self, obj):
        courses = Course.objects.filter(instructor=obj.user.username).values('id', 'title', 'slug')
        return list(courses)


class InstructorAdminViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = UserProfile.objects.filter(role__in=['mentor', 'admin']).select_related('user')
    serializer_class = InstructorAdminSerializer
    permission_classes = [IsAdministrator]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['user__username', 'user__email', 'user__first_name', 'user__last_name']

    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        profile = self.get_object()
        course_ids = request.data.get('course_ids', [])
        Course.objects.filter(id__in=course_ids).update(instructor=profile.user.username)
        return Response({'status': 'ok', 'assigned': len(course_ids)})

    @action(detail=True, methods=['post'])
    def unassign(self, request, pk=None):
        profile = self.get_object()
        course_id = request.data.get('course_id')
        Course.objects.filter(id=course_id, instructor=profile.user.username).update(instructor='')
        return Response({'status': 'ok'})


# ─── Enrollments (Admin) ───────────────────────────────────────────────────────

class EnrollmentAdminSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='user.username', read_only=True)
    student_email = serializers.CharField(source='user.email', read_only=True)
    course_title = serializers.CharField(source='course.title', read_only=True)
    course_slug = serializers.CharField(source='course.slug', read_only=True)
    track_title = serializers.CharField(source='course.track.title', read_only=True)
    progress_percentage = serializers.SerializerMethodField()

    class Meta:
        model = Enrollment
        fields = [
            'id', 'user', 'student_name', 'student_email', 'course', 'course_title',
            'course_slug', 'track_title', 'enrolled_at', 'completed_at',
            'last_activity_at', 'status', 'progress_percentage',
        ]
        read_only_fields = ['id', 'enrolled_at', 'completed_at', 'last_activity_at']

    def get_progress_percentage(self, obj):
        # The list view attaches page-batched counts (see the viewset);
        # `Enrollment.progress_percentage` costs two COUNT round trips
        # per row on the hosted database, so it only serves as the
        # fallback for single-object renders outside the list.
        total = getattr(obj, 'admin_progress_total_lessons', None)
        if total is None:
            return obj.progress_percentage
        completed = obj.admin_progress_completed_lessons
        return round((completed / total) * 100) if total else 0


class EnrollmentAdminViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Enrollment.objects.select_related('user', 'course', 'course__track').all()
    serializer_class = EnrollmentAdminSerializer
    permission_classes = [IsAdministrator]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['user__username', 'user__email', 'course__title']
    ordering_fields = ['enrolled_at', 'status']

    def get_queryset(self):
        qs = super().get_queryset()
        course = self.request.query_params.get('course')
        student = self.request.query_params.get('student')
        status_filter = self.request.query_params.get('status')
        if course:
            qs = qs.filter(course_id=course)
        if student:
            qs = qs.filter(user_id=student)
        if status_filter:
            qs = qs.filter(status=status_filter)
        return qs

    def paginate_queryset(self, queryset):
        """Attach page-batched progress counts to the returned rows.

        The serializer's progress percentage otherwise runs two COUNT
        queries per enrollment; the whole page is answered with one
        grouped query per side instead. Values mirror the model
        property exactly (all course lessons; the learner's completed
        LessonProgress rows for that course).
        """
        page = super().paginate_queryset(queryset)
        if not page:
            return page
        course_ids = list({e.course_id for e in page})
        totals = {
            row['chapter__course_id']: row['n']
            for row in Lesson.objects.filter(chapter__course_id__in=course_ids)
            .values('chapter__course_id').annotate(n=Count('id'))
        }
        completed = {
            (row['user_id'], row['lesson__chapter__course_id']): row['n']
            for row in LessonProgress.objects.filter(
                user_id__in={e.user_id for e in page},
                status='completed',
                lesson__chapter__course_id__in=course_ids,
            ).values('user_id', 'lesson__chapter__course_id').annotate(n=Count('id'))
        }
        for enrollment in page:
            enrollment.admin_progress_total_lessons = totals.get(enrollment.course_id, 0)
            enrollment.admin_progress_completed_lessons = completed.get(
                (enrollment.user_id, enrollment.course_id), 0,
            )
        return page


# ─── Competitions (Admin) ───────────────────────────────────────────────────────

class CompetitionAdminSerializer(serializers.ModelSerializer):
    organizer_name = serializers.CharField(source='organizer.username', read_only=True)
    participant_count = serializers.SerializerMethodField()
    status = serializers.CharField(read_only=True)

    class Meta:
        model = Competition
        fields = [
            'id', 'slug', 'title', 'short_description', 'description', 'banner',
            'category', 'difficulty', 'format', 'delivery_mode', 'location',
            'registration_start', 'registration_deadline', 'competition_start',
            'competition_end', 'submission_deadline', 'judging_end',
            'results_announcement', 'participant_limit', 'minimum_team_size',
            'maximum_team_size', 'eligibility_rules', 'competition_rules',
            'problem_statement', 'submission_configuration', 'prize_information',
            'tags', 'host_name', 'time_zone', 'registration_fee',
            'participation_instructions', 'evaluation_criteria',
            'submission_requirements', 'contact_information', 'external_resources',
            'is_archived',
            'is_published', 'organizer', 'organizer_name', 'participant_count',
            'status', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'status', 'organizer']

    def validate_external_resources(self, value):
        if not isinstance(value, list) or any(
            not isinstance(item, dict) or 'url' not in item for item in value
        ):
            raise serializers.ValidationError(
                'External resources must be a list of {title, url} objects.'
            )
        return value

    def validate(self, attrs):
        start = attrs.get('registration_start') or getattr(self.instance, 'registration_start', None)
        deadline = attrs.get('registration_deadline') or getattr(self.instance, 'registration_deadline', None)
        comp_start = attrs.get('competition_start') or getattr(self.instance, 'competition_start', None)
        comp_end = attrs.get('competition_end') or getattr(self.instance, 'competition_end', None)
        submission = attrs.get('submission_deadline') or getattr(self.instance, 'submission_deadline', None)
        errors = {}
        if start and deadline and deadline < start:
            errors['registration_deadline'] = 'Registration cannot close before it opens.'
        if comp_start and comp_end and comp_end < comp_start:
            errors['competition_end'] = 'The event cannot end before it starts.'
        if comp_end and submission and submission < comp_end:
            errors['submission_deadline'] = 'Submissions must stay open at least until the event ends.'
        if errors:
            raise serializers.ValidationError(errors)
        return attrs

    def get_participant_count(self, obj):
        return obj.registrations.count()


class CompetitionAdminViewSet(viewsets.ModelViewSet):
    """Hackathon/competition management.

    Every new event automatically receives the standard registration form
    (seeded default fields), which the form builder then customizes per event.
    """

    queryset = Competition.objects.select_related('organizer').all()
    serializer_class = CompetitionAdminSerializer
    permission_classes = [IsAdministrator]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'short_description', 'description']
    ordering_fields = ['title', 'created_at', 'registration_deadline']

    def perform_create(self, serializer):
        competition = serializer.save(organizer=self.request.user)
        seed_default_registration_fields(competition)

    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        competition = self.get_object()
        if competition.is_published:
            return Response(self.get_serializer(competition).data)
        competition.is_published = True
        competition.save(update_fields=['is_published'])
        audit(
            'competition_published', request=request, user=request.user,
            identifier=str(competition.pk), metadata={'title': competition.title},
        )
        return Response(self.get_serializer(competition).data)

    @action(detail=True, methods=['post'])
    def unpublish(self, request, pk=None):
        competition = self.get_object()
        competition.is_published = False
        competition.save(update_fields=['is_published'])
        audit(
            'competition_unpublished', request=request, user=request.user,
            identifier=str(competition.pk), metadata={'title': competition.title},
        )
        return Response(self.get_serializer(competition).data)

    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        """Remove from active listings while retaining all records."""
        competition = self.get_object()
        competition.is_archived = True
        competition.is_published = False
        competition.save(update_fields=['is_archived', 'is_published'])
        audit(
            'competition_archived', request=request, user=request.user,
            identifier=str(competition.pk), metadata={'title': competition.title},
        )
        return Response(self.get_serializer(competition).data)

    @action(detail=True, methods=['post'])
    def unarchive(self, request, pk=None):
        competition = self.get_object()
        competition.is_archived = False
        competition.save(update_fields=['is_archived'])
        audit(
            'competition_unarchived', request=request, user=request.user,
            identifier=str(competition.pk), metadata={'title': competition.title},
        )
        return Response(self.get_serializer(competition).data)


# ─── Achievements (Admin) ───────────────────────────────────────────────────────

class AchievementAdminSerializer(serializers.ModelSerializer):
    earned_count = serializers.SerializerMethodField()

    class Meta:
        model = Achievement
        fields = [
            'id', 'slug', 'title', 'description', 'icon', 'category',
            'difficulty', 'xp_bonus', 'condition_type', 'condition_value',
            'how_to_earn', 'is_active', 'created_at', 'earned_count',
        ]
        read_only_fields = ['id', 'created_at']

    def get_earned_count(self, obj):
        # Annotation-first, same hosted-database N+1 reason as lesson counts.
        if hasattr(obj, 'admin_earned_count'):
            return obj.admin_earned_count
        return obj.user_achievements.count()


class AchievementAdminViewSet(viewsets.ModelViewSet):
    queryset = Achievement.objects.annotate(
        admin_earned_count=Count('user_achievements'),
    )
    serializer_class = AchievementAdminSerializer
    permission_classes = [IsAdministrator]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'slug']
    ordering_fields = ['title', 'created_at']


# ─── Certificates (Admin) ───────────────────────────────────────────────────────

class CertificateAdminSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='user.username', read_only=True)
    student_email = serializers.CharField(source='user.email', read_only=True)
    course_title = serializers.CharField(source='certification.track.title', read_only=True)

    class Meta:
        model = UserCertification
        fields = [
            'id', 'user', 'student_name', 'student_email', 'certification',
            'course_title', 'earned_at', 'credential_id',
        ]
        read_only_fields = ['id', 'earned_at', 'credential_id']


class CertificateAdminViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = UserCertification.objects.select_related('user', 'certification', 'certification__track').all()
    serializer_class = CertificateAdminSerializer
    permission_classes = [IsAdministrator]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['user__username', 'user__email', 'credential_id']
    ordering_fields = ['earned_at']

    @action(detail=True, methods=['post'])
    def revoke(self, request, pk=None):
        cert = self.get_object()
        # Mark as revoked by updating status if model supports it
        return Response({'status': 'revoked', 'id': cert.id})


# ─── Announcements (Admin) ─────────────────────────────────────────────────────

class AnnouncementAdminSerializer(serializers.ModelSerializer):
    """Admin view of an announcement.

    ``status`` transitions never travel through plain writes: they happen
    only via the publish/unpublish/archive endpoints, which is where the
    Super Admin gate and the audit trail live. ``is_published`` remains as
    a read-only mirror so older clients keep working.
    """

    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    is_published = serializers.BooleanField(read_only=True)
    category = serializers.ChoiceField(choices=Announcement.Category.choices, required=False)
    priority = serializers.ChoiceField(choices=Announcement.Priority.choices, required=False)
    target_audience = serializers.ChoiceField(
        choices=Announcement.AUDIENCE_CHOICES, required=False,
    )

    class Meta:
        model = Announcement
        fields = [
            'id', 'title', 'slug', 'body', 'short_description', 'cover_image',
            'category', 'priority', 'target_audience', 'status', 'is_published',
            'scheduled_at', 'published_at', 'expires_at',
            'created_by', 'created_by_name', 'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'slug', 'status', 'is_published', 'published_at',
            'created_by', 'created_by_name', 'created_at', 'updated_at',
        ]


class AnnouncementAdminViewSet(viewsets.ModelViewSet):
    """Announcement CRUD plus an enforced publishing workflow.

    Registering this viewset at ``admin/announcements/`` is what restores the
    admin panel's publishing controls: the views existed but were never
    routed, so every announcement API call 404'd behind the UI.
    """

    queryset = Announcement.objects.select_related('created_by').all()
    serializer_class = AnnouncementAdminSerializer
    permission_classes = [IsAdministrator]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'body']
    ordering_fields = ['created_at', 'published_at']

    def get_permissions(self):
        if self.action in ('publish', 'unpublish', 'archive', 'email_draft'):
            # Only Super Admins move global content in/out of public view
            # or stage bulk mail off an announcement.
            return [IsSuperAdmin()]
        return [permission() for permission in self.permission_classes]

    def perform_create(self, serializer):
        announcement = serializer.save(created_by=self.request.user)
        audit(
            'announcement_created', request=self.request, user=self.request.user,
            identifier=str(announcement.pk), metadata={'title': announcement.title},
        )

    def perform_destroy(self, instance):
        audit(
            'announcement_deleted', request=self.request, user=self.request.user,
            identifier=str(instance.pk), metadata={'title': instance.title},
        )
        instance.delete()

    def _set_status(self, request, status_value, event):
        announcement = self.get_object()
        if announcement.status == status_value:
            # Idempotent guard against double-publish from impatient clicks.
            return Response(AnnouncementAdminSerializer(announcement).data)
        announcement.status = status_value
        if status_value == Announcement.Status.PUBLISHED and not announcement.published_at:
            announcement.published_at = timezone.now()
        announcement.save()
        audit(
            event, request=request, user=request.user,
            identifier=str(announcement.pk),
            metadata={'title': announcement.title, 'status': status_value},
        )
        return Response(AnnouncementAdminSerializer(announcement).data)

    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        return self._set_status(request, Announcement.Status.PUBLISHED, 'announcement_published')

    @action(detail=True, methods=['post'])
    def unpublish(self, request, pk=None):
        return self._set_status(request, Announcement.Status.UNPUBLISHED, 'announcement_unpublished')

    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        return self._set_status(request, Announcement.Status.ARCHIVED, 'announcement_archived')

    @action(detail=True, methods=['post'], url_path='email-draft')
    def email_draft(self, request, pk=None):
        """Stage a DRAFT campaign prefilled from this announcement.

        Publishing and emailing stay separate actions: nothing is queued
        here — the admin still reviews, previews, and confirms in the
        campaign composer.
        """
        announcement = self.get_object()
        audience = (
            announcement.target_audience
            if announcement.target_audience in EmailCampaign.Audience.values
            else EmailCampaign.Audience.ALL
        )
        campaign = EmailCampaign.objects.create(
            name=f'Announcement: {announcement.title}'[:200],
            subject=announcement.title,
            heading=announcement.title,
            body=announcement.short_description or announcement.body[:1500],
            template=(
                EmailCampaign.Template.NOTICE
                if announcement.priority == Announcement.Priority.URGENT
                else EmailCampaign.Template.GENERAL
            ),
            audience=audience,
            related_announcement=announcement,
            created_by=request.user,
        )
        return Response(
            EmailCampaignAdminSerializer(campaign).data, status=status.HTTP_201_CREATED,
        )



# ─── Platform updates / changelog (Admin) ──────────────────────────────────

class PlatformUpdateAdminSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = PlatformUpdate
        fields = [
            'id', 'title', 'slug', 'version', 'category', 'summary', 'content',
            'change_list', 'cover_image', 'target_audience', 'status',
            'published_at', 'created_by', 'created_by_name', 'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'slug', 'status', 'published_at',
            'created_by', 'created_by_name', 'created_at', 'updated_at',
        ]


class PlatformUpdateAdminViewSet(viewsets.ModelViewSet):
    """Changelog entries with the same enforced publishing workflow."""

    queryset = PlatformUpdate.objects.select_related('created_by').all()
    serializer_class = PlatformUpdateAdminSerializer
    permission_classes = [IsAdministrator]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'content', 'version']
    ordering_fields = ['created_at', 'published_at']

    def get_permissions(self):
        if self.action in ('publish', 'unpublish', 'archive', 'email_draft'):
            return [IsSuperAdmin()]
        return [permission() for permission in self.permission_classes]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def _set_status(self, request, status_value, event):
        update = self.get_object()
        if update.status == status_value:
            return Response(PlatformUpdateAdminSerializer(update).data)
        update.status = status_value
        if status_value == PlatformUpdate.Status.PUBLISHED and not update.published_at:
            update.published_at = timezone.now()
        update.save()
        audit(
            event, request=request, user=request.user, identifier=str(update.pk),
            metadata={'title': update.title, 'status': status_value},
        )
        return Response(PlatformUpdateAdminSerializer(update).data)

    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        return self._set_status(request, PlatformUpdate.Status.PUBLISHED, 'platform_update_published')

    @action(detail=True, methods=['post'])
    def unpublish(self, request, pk=None):
        return self._set_status(request, PlatformUpdate.Status.UNPUBLISHED, 'platform_update_unpublished')

    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        return self._set_status(request, PlatformUpdate.Status.ARCHIVED, 'platform_update_archived')

    @action(detail=True, methods=['post'], url_path='email-draft')
    def email_draft(self, request, pk=None):
        """Stage a DRAFT platform-update campaign for admin confirmation."""
        update = self.get_object()
        campaign = EmailCampaign.objects.create(
            name=f'Update: {update.title}'[:200],
            subject=f"What's new: {update.title}"[:200],
            heading=update.title,
            body=update.summary or update.content[:1500],
            template=EmailCampaign.Template.UPDATE,
            audience=EmailCampaign.Audience.ALL,
            cta_label='See the changelog',
            cta_url=f"{settings.FRONTEND_URL}/updates/{update.slug}",
            related_update=update,
            created_by=request.user,
        )
        return Response(
            EmailCampaignAdminSerializer(campaign).data, status=status.HTTP_201_CREATED,
        )


# ─── Hackathon registration form builder (Admin) ────────────────────────────

class RegistrationFormFieldAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegistrationFormField
        fields = [
            'id', 'competition', 'label', 'field_key', 'field_type', 'description',
            'placeholder', 'required', 'options', 'validation', 'order',
            'is_active', 'is_default', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'is_default', 'created_at', 'updated_at']

    def validate_validation(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError('Validation must be an object.')
        allowed = {'min', 'max', 'min_length', 'max_length'}
        unknown = set(value) - allowed
        if unknown:
            raise serializers.ValidationError(f'Unsupported validation keys: {sorted(unknown)}')
        return value

    def validate_options(self, value):
        if not isinstance(value, list) or any(
            not isinstance(item, (str, int, float)) for item in value
        ):
            raise serializers.ValidationError('Options must be a flat list of values.')
        return value

    def validate_field_key(self, value):
        if value == 'rules_accepted':
            raise serializers.ValidationError('This key is reserved by the registration flow.')
        return value

    def validate(self, attrs):
        field_type = attrs.get('field_type', getattr(self.instance, 'field_type', None))
        options = attrs.get('options', getattr(self.instance, 'options', []))
        if field_type in ('dropdown', 'multiple_choice', 'checkboxes') and not options:
            raise serializers.ValidationError({'options': 'Choice fields need at least one option.'})
        return attrs


class RegistrationFormFieldAdminViewSet(viewsets.ModelViewSet):
    """Per-hackathon registration questions: add, edit, reorder, remove."""

    queryset = RegistrationFormField.objects.select_related('competition').all()
    serializer_class = RegistrationFormFieldAdminSerializer
    permission_classes = [IsAdministrator]

    def get_queryset(self):
        qs = super().get_queryset()
        competition = self.request.query_params.get('competition')
        if competition:
            qs = qs.filter(competition_id=competition)
        return qs.order_by('competition', 'order', 'id')

    @action(detail=False, methods=['post'])
    def reorder(self, request):
        items = request.data.get('items', [])
        with transaction.atomic():
            for item in items:
                RegistrationFormField.objects.filter(id=item['id']).update(order=item['order'])
        return Response({'status': 'ok'})

    @action(detail=False, methods=['post'], url_path='reset-defaults')
    def reset_defaults(self, request):
        """Re-seed the standard questions for one competition (idempotent)."""
        competition = get_object_or_404(Competition, pk=request.data.get('competition'))
        created = seed_default_registration_fields(competition)
        return Response({'created': len(created)})


# ─── Hackathon applications / registrations (Admin) ──────────────────────

class CompetitionRegistrationAdminSerializer(serializers.ModelSerializer):
    participant_name = serializers.SerializerMethodField()
    participant_email = serializers.EmailField(source='user.email', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    competition_title = serializers.CharField(source='competition.title', read_only=True)
    competition_slug = serializers.CharField(source='competition.slug', read_only=True)

    class Meta:
        model = CompetitionRegistration
        fields = [
            'id', 'reference', 'competition', 'competition_title', 'competition_slug',
            'user', 'username', 'participant_name', 'participant_email', 'team',
            'registration_status', 'registration_data', 'registered_at', 'updated_at',
        ]
        read_only_fields = fields

    def get_participant_name(self, obj):
        return obj.user.get_full_name() or obj.user.username


class CompetitionRegistrationAdminViewSet(viewsets.ReadOnlyModelViewSet):
    """Review, filter, and decide hackathon applications.

    Decisions go through the ``update_status`` action so every change is
    audited and triggers the matching confirmation email; the read API never
    lets a client poke ``registration_status`` directly.
    """

    queryset = (
        CompetitionRegistration.objects
        .select_related('competition', 'user', 'team')
        .all()
    )
    serializer_class = CompetitionRegistrationAdminSerializer
    permission_classes = [IsAdministrator]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['user__username', 'user__email', 'user__first_name', 'user__last_name', 'reference']
    ordering_fields = ['registered_at', 'registration_status']

    def get_queryset(self):
        qs = super().get_queryset()
        competition = self.request.query_params.get('competition')
        if competition:
            qs = qs.filter(competition_id=competition)
        status_filter = self.request.query_params.get('status')
        if status_filter:
            qs = qs.filter(registration_status=status_filter)
        return qs

    DECISION_TEMPLATES = {
        'approved': 'competition_approved',
        'rejected': 'competition_registration_rejected',
        'waitlisted': 'competition_waitlisted',
    }

    @action(detail=True, methods=['post'], url_path='update-status')
    def update_status(self, request, pk=None):
        registration = self.get_object()
        new_status = request.data.get('status')
        allowed = dict(CompetitionRegistration.STATUS_CHOICES)
        if new_status not in allowed:
            return Response(
                {'detail': f'Unknown status. Choose one of: {", ".join(allowed)}'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        previous = registration.registration_status
        if previous != new_status:
            registration.registration_status = new_status
            # This view writes the decision notification itself below, so the
            # post-save signal stands down instead of sending a second mail.
            registration._notification_handled = True
            registration.save(update_fields=['registration_status', 'updated_at'])
            audit(
                'competition_registration_status_changed', request=request, user=request.user,
                identifier=str(registration.pk),
                metadata={'from': previous, 'to': new_status,
                          'competition': registration.competition.title},
            )
        competition = registration.competition
        template = self.DECISION_TEMPLATES.get(new_status)
        if template and previous != new_status:
            heading = {
                'approved': 'Application approved',
                'rejected': 'Application update',
                'waitlisted': 'You are on the waitlist',
            }[new_status]
            message = {
                'approved': (
                    f'Your application for {competition.title} was approved. '
                    'Watch your dashboard for event dates and submission details.'
                ),
                'rejected': (
                    f'After review, your application for {competition.title} '
                    'was not accepted this time. You are welcome to apply for '
                    'future events.'
                ),
                'waitlisted': (
                    f'Applications for {competition.title} are full so far, so '
                    'your application is on the waitlist. A spot frees up, you '
                    'will be the first to know.'
                ),
            }[new_status]
            notify(
                registration.user,
                type=(
                    'competition_approved' if new_status == 'approved'
                    else 'competition_rejected' if new_status == 'rejected'
                    else 'competition_waitlisted'
                ),
                title=f'{heading}: {competition.title}',
                body=message,
                link=f'/competitions/{competition.slug}',
                related_object_type='competition',
                related_object_id=competition.slug,
                dedupe_key=f'comp-decision:{registration.pk}:{new_status}',
                email_subject=f'{heading} — {competition.title}',
                email_context={
                    'preheader': message[:140],
                    'heading': heading,
                    'competition_title': competition.title,
                    'message': message,
                    'cta_url': f'{settings.FRONTEND_URL}/competitions/{competition.slug}',
                    'cta_label': 'View competition',
                    'info_rows': [
                        ['Reference', registration.reference],
                        ['Status', allowed[new_status]],
                    ],
                },
                email_key=f'comp-decision:{registration.pk}:{new_status}',
            )
        return Response(self.get_serializer(registration).data)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        qs = self.get_queryset()
        counts = {}
        for row in qs.values('registration_status').annotate(n=Count('id')):
            counts[row['registration_status']] = row['n']
        return Response({
            'total': sum(counts.values()),
            'by_status': counts,
        })

    @action(detail=False, methods=['get'])
    def export_csv(self, request):
        """Stream the filtered registrations as a CSV download."""
        import csv
        from django.http import HttpResponse

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="hackathon-registrations.csv"'
        writer = csv.writer(response)
        writer.writerow([
            'Reference', 'Hackathon', 'Participant', 'Username', 'Email',
            'Status', 'Registered at', 'Submitted answers',
        ])
        for row in self.filter_queryset(self.get_queryset()).iterator():
            answers = '; '.join(
                f'{key}: {value}' for key, value in (row.registration_data or {}).items()
            )
            writer.writerow([
                row.reference, row.competition.title,
                row.user.get_full_name() or row.user.username,
                row.user.username, row.user.email,
                row.get_registration_status_display(),
                row.registered_at.isoformat(), answers,
            ])
        audit(
            'hackathon_registrations_exported', request=request, user=request.user,
            identifier='', metadata={},
        )
        return response


# ─── Email campaigns (Admin, Super Admin only) ────────────────────────────

class EmailCampaignRecipientAdminSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()

    class Meta:
        model = EmailCampaignRecipient
        fields = ['id', 'user', 'username', 'email', 'status', 'error', 'sent_at', 'created_at']
        read_only_fields = fields

    def get_username(self, obj):
        # External custom addresses have no account behind the row.
        if obj.user_id and obj.user is not None:
            name = email_composer.display_name(obj.user)
            return name or obj.user.username
        return obj.email.partition('@')[0]

    def get_email(self, obj):
        # Addresses are masked unless the requester is a Super Admin: campaign
        # history stays inspectable without exposing the whole recipient list.
        request = self.context.get('request')
        if request is not None and getattr(request.user, 'is_superuser', False):
            return obj.email
        name, _, domain = obj.email.partition('@')
        return f'{name[:2]}***@{domain}' if domain else '***'


class EmailCampaignAdminSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    status = serializers.CharField(read_only=True)
    # The model's plain-text body is only required *alongside* nothing else:
    # composer drafts live in body_html, so the field must accept a blank
    # value here and the cross-check in validate() enforces "one or the other".
    body = serializers.CharField(required=False, allow_blank=True)
    selected_users = serializers.PrimaryKeyRelatedField(
        many=True, required=False,
        queryset=User.objects.filter(is_active=True),
    )
    custom_emails = serializers.ListField(
        child=serializers.CharField(max_length=254), required=False,
    )
    cc_emails = serializers.ListField(
        child=serializers.CharField(max_length=254), required=False,
    )
    bcc_emails = serializers.ListField(
        child=serializers.CharField(max_length=254), required=False,
    )

    class Meta:
        model = EmailCampaign
        fields = [
            'id', 'name', 'subject', 'heading', 'body', 'template', 'banner_image',
            'cta_label', 'cta_url', 'audience', 'competition', 'essential',
            'selected_users', 'custom_emails', 'cc_emails', 'bcc_emails',
            'body_html', 'plain_text_alternative',
            'related_announcement', 'related_update', 'status', 'recipient_count',
            'sent_count', 'failed_count', 'skipped_count', 'sent_at',
            'created_by', 'created_by_name', 'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'status', 'recipient_count', 'sent_count', 'failed_count',
            'skipped_count', 'sent_at', 'created_by', 'created_by_name',
            'created_at', 'updated_at',
        ]

    def validate_body_html(self, value):
        # Storing the sanitized form means the fan-out and every preview can
        # trust the database; raw admin markup never reaches an inbox.
        return email_composer.sanitize_html(value)

    def _validate_addresses(self, value, field):
        valid, invalid = email_composer.clean_address_list(value)
        if invalid:
            raise serializers.ValidationError(
                f'{field} contains invalid addresses: {", ".join(invalid)}'
            )
        return valid

    def validate_custom_emails(self, value):
        return self._validate_addresses(value, 'custom emails')

    def validate_cc_emails(self, value):
        return self._validate_addresses(value, 'CC addresses')

    def validate_bcc_emails(self, value):
        return self._validate_addresses(value, 'BCC addresses')

    def validate(self, attrs):
        audience = attrs.get('audience', getattr(self.instance, 'audience', 'all'))
        if audience == EmailCampaign.Audience.SPECIFIC:
            users = attrs.get('selected_users', getattr(self.instance, 'selected_users', None))
            emails = attrs.get('custom_emails', getattr(self.instance, 'custom_emails', None) or [])
            if not (users and list(users) or emails):
                raise serializers.ValidationError(
                    'Select at least one recipient: a registered student or a custom email address.'
                )
        body = attrs.get('body', getattr(self.instance, 'body', '') if self.instance else '')
        body_html = attrs.get(
            'body_html', getattr(self.instance, 'body_html', '') if self.instance else '',
        )
        if not (body.strip() or body_html.strip()):
            raise serializers.ValidationError('Write a message before saving the email.')
        warnings = email_composer.unknown_variables(
            attrs.get('subject', getattr(self.instance, 'subject', '')),
            attrs.get('heading', getattr(self.instance, 'heading', '')),
            body,
            body_html,
        )
        if warnings:
            raise serializers.ValidationError({
                'subject': f'Unknown variable(s): {{{{{warnings[0]}}}}}. Supported: '
                + ', '.join(f'{{{{{key}}}}}' for key, _ in email_composer.PERSONALIZATION_KEYS) + '.',
            })
        return attrs


class EmailCampaignAdminViewSet(viewsets.ModelViewSet):
    """Compose, preview, and send platform email campaigns.

    Every route requires Super Admin; sending additionally requires an
    explicit ``confirm`` flag and only works from a draft, so a resent
    request can never double-mail the audience. The "Send Official Email"
    composer uses the same lifecycle with ``audience=specific``.
    """

    queryset = EmailCampaign.objects.select_related('created_by', 'competition').all()
    serializer_class = EmailCampaignAdminSerializer
    permission_classes = [IsSuperAdmin]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'subject', 'recipients__email', 'recipients__user__username']
    ordering_fields = ['created_at', 'sent_at', 'status']

    def get_throttles(self):
        # Rate-limit the actions that can put mail on the wire, per administrator.
        if self.action in ('send', 'test', 'resend_failed'):
            scope = 'email_campaign_send'
            throttle = ScopedRateThrottle()
            throttle.scope = scope
            throttle.rate = settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'].get(scope, '60/hour')
            return [throttle]
        return super().get_throttles()

    def get_queryset(self):
        qs = super().get_queryset().distinct()
        # History filters apply to the campaign list only. Other actions —
        # detail, send, recipients (which has its own status= filter for
        # recipient rows) — must keep the full queryset so get_object() can
        # find the campaign no matter what query params were passed.
        if self.action != 'list':
            return qs
        params = self.request.query_params
        if params.get('status'):
            qs = qs.filter(status=params['status'])
        from django.utils.dateparse import parse_date
        date_from = parse_date(params.get('date_from') or '')
        if date_from:
            qs = qs.filter(created_at__date__gte=date_from)
        date_to = parse_date(params.get('date_to') or '')
        if date_to:
            qs = qs.filter(created_at__date__lte=date_to)
        return qs

    def perform_create(self, serializer):
        campaign = serializer.save(created_by=self.request.user)
        audit(
            'email_campaign_draft_created', request=self.request, user=self.request.user,
            identifier=str(campaign.pk),
            metadata={'audience': campaign.audience, 'composed': bool(campaign.body_html)},
        )

    def perform_destroy(self, instance):
        audit(
            'email_campaign_draft_discarded', request=self.request, user=self.request.user,
            identifier=str(instance.pk), metadata={'status': instance.status},
        )
        instance.delete()

    @action(detail=True, methods=['get'], url_path='audience-count')
    def audience_count(self, request, pk=None):
        campaign = self.get_object()
        return Response({
            'audience': campaign.audience,
            'count': email_campaigns.planned_recipient_count(campaign),
        })

    @action(detail=False, methods=['get'], url_path='students-search')
    def students_search(self, request):
        """Look up registered students for the composer's recipient picker.

        Matches on name, email address and username (student ID) and returns
        only the three fields the composer needs — never any course or
        activity data. Search is server-side so addresses are not dumped.
        """
        term = (request.query_params.get('q') or '').strip()
        if not term:
            return Response({'results': []})
        from django.contrib.auth import get_user_model
        User = get_user_model()
        matches = (
            User.objects.filter(is_active=True, profile__role='student')
            .exclude(email='')
            .filter(
                Q(first_name__icontains=term) | Q(last_name__icontains=term)
                | Q(email__icontains=term) | Q(username__icontains=term)
            )
            .order_by('username')[:25]
        )
        results = [
            {
                'id': user.pk,
                'name': email_composer.display_name(user),
                'email': user.email,
                'student_id': user.username,
            }
            for user in matches
        ]
        return Response({'results': results})

    @action(detail=False, methods=['post'], url_path='validate-recipients')
    def validate_recipients(self, request):
        """Resolve a draft recipient selection into verified display rows.

        Used by the composer's "recipient verification" step: the admin sees
        exactly who each entry resolves to (name, address, ID, duplicate or
        invalid flags) before anything is queued.
        """
        user_ids = request.data.get('user_ids') or []
        emails = request.data.get('emails') or []
        from django.contrib.auth import get_user_model
        users = list(
            get_user_model().objects.filter(is_active=True, pk__in=user_ids)
            .exclude(email='')[:200]
        )
        known = {u.email.lower() for u in users}
        valid, invalid = email_composer.clean_address_list(emails)
        rows = [
            {
                'id': user.pk,
                'name': email_composer.display_name(user),
                'email': user.email,
                'student_id': user.username,
                'registered': True,
            }
            for user in users
        ]
        seen_duplicates = []
        for address in valid:
            if address in known:
                seen_duplicates.append(address)
                continue
            known.add(address)
            rows.append({
                'id': None,
                'name': address.partition('@')[0].replace('.', ' ').replace('_', ' ').title(),
                'email': address,
                'student_id': '',
                'registered': False,
            })
        return Response({
            'recipients': rows,
            'total': len(rows),
            'invalid': invalid,
            'duplicates_removed': seen_duplicates,
        })

    @action(detail=False, methods=['get'], url_path='sender-identity')
    def sender_identity(self, request):
        """The fixed Code Yaar sender shown above the composer.

        Read-only by design: administrators can never type a From address,
        so campaign mail cannot be used to spoof another sender.
        """
        from email.utils import parseaddr
        name, address = parseaddr(settings.DEFAULT_FROM_EMAIL)
        return Response({
            'sender_name': name or 'Code Yaar',
            'sender_email': address,
            'reply_to': settings.REPLY_TO_EMAIL or address,
        })

    @action(detail=True, methods=['get'])
    def preview(self, request, pk=None):
        """Render the campaign exactly as one recipient would see it.

        Composed mail is personalized per recipient, so the preview accepts
        ``?as_user=<id>`` to show one student's exact copy; without it the
        requesting admin's own identity fills the variables.
        """
        campaign = self.get_object()
        target = None
        as_user = request.query_params.get('as_user')
        if as_user and str(as_user).isdigit():
            target = User.objects.filter(pk=int(as_user), is_active=True).first()
        if email_campaigns.is_composed(campaign):
            viewer = target if target is not None else request.user
            name = email_composer.display_name(viewer)
            email = viewer.email or request.user.email
            student_id = viewer.username
            variables = email_campaigns.composed_variables(campaign, name, email, student_id)
            html, text = email_campaigns.render_composed_email(
                campaign, name=name, email=email, student_id=student_id,
                has_account=True, user=viewer,
            )
            subject = email_campaigns.composed_subject(campaign, variables)
        else:
            html, text = email_campaigns.render_campaign_email(campaign, target or request.user)
            subject = campaign.subject
        return Response({'html': html, 'text': text, 'subject': subject})

    @action(detail=True, methods=['post'])
    def test(self, request, pk=None):
        """Send one test copy — to the requesting admin unless a test address is given.

        The test rides the same render path as the real fan-out, so the admin
        sees exactly the personalized layout a recipient would receive.
        """
        campaign = self.get_object()
        to_email = email_composer.normalize_email(request.data.get('to'))
        if to_email and not email_composer.validate_email(to_email):
            return Response(
                {'detail': 'That test address is not a valid email address.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not to_email and not request.user.email:
            return Response(
                {'detail': 'Your account has no email address to test with.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        result = email_campaigns.send_test_email(
            {
                'subject': f'[TEST] {campaign.subject}',
                'heading': campaign.heading,
                'name': campaign.name,
                'body': campaign.body,
                'body_html': campaign.body_html,
                'plain_text': campaign.plain_text_alternative,
                'template': campaign.template,
                'cta_label': campaign.cta_label,
                'cta_url': campaign.cta_url,
            },
            request.user,
            to_email=to_email,
        )
        audit(
            'email_campaign_test_sent', request=request, user=request.user,
            identifier=str(campaign.pk),
            metadata={'result': result['status'], 'to_external': bool(to_email)},
        )
        return Response(result)

    @action(detail=True, methods=['post'])
    def send(self, request, pk=None):
        campaign = self.get_object()
        if request.data.get('confirm') is not True:
            return Response(
                {'detail': 'Sending requires explicit confirmation (confirm=true).'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if campaign.status != EmailCampaign.Status.DRAFT:
            return Response(
                {'detail': f'Campaign already {campaign.status}; emails never re-send to the same audience.'},
                status=status.HTTP_409_CONFLICT,
            )
        if campaign.audience.startswith('comp_') and not campaign.competition_id:
            return Response(
                {'detail': 'Pick the hackathon this campaign should reach.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        count = email_campaigns.planned_recipient_count(campaign)
        if count == 0:
            return Response(
                {'detail': 'This audience has no recipients yet.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        campaign.status = EmailCampaign.Status.QUEUED
        campaign.save(update_fields=['status', 'updated_at'])
        audit(
            'email_campaign_queued', request=request, user=request.user,
            identifier=str(campaign.pk),
            metadata={
                'audience': campaign.audience, 'count': count,
                'composed': email_campaigns.is_composed(campaign),
            },
        )
        pk = campaign.pk
        transaction.on_commit(
            lambda: email_campaigns.dispatch_campaign(EmailCampaign.objects.get(pk=pk))
        )
        return Response(
            {'status': campaign.status, 'estimated_recipients': count},
            status=status.HTTP_202_ACCEPTED,
        )

    @action(detail=True, methods=['post'], url_path='resend-failed')
    def resend_failed(self, request, pk=None):
        """Re-queue only the recipients whose delivery failed.

        Successful copies are never re-sent: the row-level unique constraint
        plus the PENDING filter mean exactly the failed addresses get a new
        attempt, and the campaign leaves ``failed``/``partial`` behind.
        """
        campaign = self.get_object()
        if request.data.get('confirm') is not True:
            return Response(
                {'detail': 'Resending requires explicit confirmation (confirm=true).'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if campaign.status not in (
            EmailCampaign.Status.SENT, EmailCampaign.Status.PARTIAL, EmailCampaign.Status.FAILED,
        ):
            return Response(
                {'detail': 'Only a finished campaign can have failed copies resent.'},
                status=status.HTTP_409_CONFLICT,
            )
        failed = campaign.recipients.filter(status=EmailCampaignRecipient.Status.FAILED)
        count = failed.count()
        if count == 0:
            return Response(
                {'detail': 'No failed recipients to resend to.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        failed.update(
            status=EmailCampaignRecipient.Status.PENDING, error='', sent_at=None,
        )
        campaign.status = EmailCampaign.Status.QUEUED
        campaign.save(update_fields=['status', 'updated_at'])
        audit(
            'email_campaign_resend_failed', request=request, user=request.user,
            identifier=str(campaign.pk), metadata={'count': count},
        )
        pk = campaign.pk
        transaction.on_commit(
            lambda: email_campaigns.dispatch_campaign(EmailCampaign.objects.get(pk=pk))
        )
        return Response(
            {'status': campaign.status, 'resending': count},
            status=status.HTTP_202_ACCEPTED,
        )

    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """Copy any sent or drafted email into a fresh draft."""
        source = self.get_object()
        clone = EmailCampaign.objects.create(
            name=f'Copy of {source.name}'[:200],
            subject=source.subject,
            heading=source.heading,
            body=source.body,
            body_html=source.body_html,
            plain_text_alternative=source.plain_text_alternative,
            template=source.template,
            banner_image=source.banner_image,
            cta_label=source.cta_label,
            cta_url=source.cta_url,
            audience=source.audience,
            competition=source.competition,
            custom_emails=list(source.custom_emails or []),
            cc_emails=list(source.cc_emails or []),
            bcc_emails=list(source.bcc_emails or []),
            essential=source.essential,
            related_announcement=source.related_announcement,
            related_update=source.related_update,
            created_by=request.user,
        )
        clone.selected_users.set(source.selected_users.all())
        audit(
            'email_campaign_duplicated', request=request, user=request.user,
            identifier=str(source.pk), metadata={'new_campaign': clone.pk},
        )
        return Response(
            EmailCampaignAdminSerializer(clone, context={'request': request}).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=['get'], url_path='recipients')
    def recipients(self, request, pk=None):
        campaign = self.get_object()
        qs = campaign.recipients.select_related('user').all()
        status_filter = request.query_params.get('status')
        if status_filter:
            qs = qs.filter(status=status_filter)
        search = (request.query_params.get('search') or '').strip()
        if search:
            qs = qs.filter(
                Q(email__icontains=search)
                | Q(user__username__icontains=search)
                | Q(user__first_name__icontains=search)
                | Q(user__last_name__icontains=search)
            )
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        from django.utils.dateparse import parse_date
        parsed_from = parse_date(date_from) if date_from else None
        parsed_to = parse_date(date_to) if date_to else None
        if parsed_from:
            qs = qs.filter(created_at__date__gte=parsed_from)
        if parsed_to:
            qs = qs.filter(created_at__date__lte=parsed_to)
        page = self.paginate_queryset(qs)
        serializer = EmailCampaignRecipientAdminSerializer(
            page if page is not None else qs, many=True, context={'request': request},
        )
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)


class EmailTemplateAdminSerializer(serializers.ModelSerializer):
    """A saved, reusable starting point for a composed email.

    Content-only: it never carries recipients or delivery state. The HTML
    body is allowlist-sanitized on save (same guard as the composer) and
    unknown ``{{variables}}`` are refused, so a template can neither store
    markup the mailer would not render nor reference a token the personalizer
    cannot fill. ``{{tokens}}`` stay unrendered here on purpose — they are
    substituted per recipient only when the template is actually used.
    """

    created_by_name = serializers.SerializerMethodField()
    variables_used = serializers.SerializerMethodField()

    class Meta:
        model = EmailTemplate
        fields = [
            'id', 'name', 'category', 'description', 'subject', 'heading',
            'preview_text', 'body_html', 'plain_text', 'cta_label', 'cta_url',
            'footer_content', 'theme', 'is_favorite', 'created_by', 'created_by_name',
            'variables_used', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']

    def get_created_by_name(self, obj):
        return obj.created_by.username if obj.created_by else ''

    def get_variables_used(self, obj):
        combined = ' '.join(
            part or '' for part in (obj.subject, obj.heading, obj.body_html, obj.footer_content)
        )
        return email_composer.used_variables(combined)

    def validate(self, attrs):
        subject = attrs.get('subject', getattr(self.instance, 'subject', ''))
        heading = attrs.get('heading', getattr(self.instance, 'heading', ''))
        body_html = attrs.get('body_html', getattr(self.instance, 'body_html', ''))
        footer = attrs.get('footer_content', getattr(self.instance, 'footer_content', ''))
        unknown = email_composer.unknown_variables(subject, heading, body_html, footer)
        if unknown:
            raise serializers.ValidationError({
                'subject': f'Unknown variable(s): {{{{{unknown[0]}}}}}. Supported: '
                + ', '.join(f'{{{{{key}}}}}' for key, _ in email_composer.PERSONALIZATION_KEYS) + '.',
            })
        return attrs

    def to_internal_value(self, data):
        validated = super().to_internal_value(data)
        if 'body_html' in validated:
            validated['body_html'] = email_composer.sanitize_html(validated['body_html'])
        if not validated.get('plain_text') and validated.get('body_html'):
            validated['plain_text'] = email_composer.plain_text_from_html(validated['body_html'])
        return validated


class EmailTemplateAdminViewSet(viewsets.ModelViewSet):
    """CRUD for the admin Email Templates library.

    Super Admin only, matching the composer/campaign permission boundary.
    Templates are content only and never send anything; ``duplicate`` copies a
    template into a new one, ``preview`` renders the branded layout as the
    requesting admin so its ``{{variables}}`` show filled exactly as a
    recipient would see them, and ``categories`` reports the preset list plus
    every category already in use so the UI can offer custom ones.
    """

    queryset = EmailTemplate.objects.select_related('created_by').all()
    serializer_class = EmailTemplateAdminSerializer
    permission_classes = [IsSuperAdmin]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'subject', 'description', 'category']
    ordering_fields = ['updated_at', 'created_at', 'name']
    ordering = ['-is_favorite', '-updated_at']

    def get_queryset(self):
        qs = super().get_queryset()
        if self.action != 'list':
            return qs
        category = self.request.query_params.get('category')
        if category == 'favorites':
            qs = qs.filter(is_favorite=True)
        elif category:
            qs = qs.filter(category=category)
        return qs

    def perform_create(self, serializer):
        template = serializer.save(created_by=self.request.user)
        audit(
            'email_template_created', request=self.request, user=self.request.user,
            identifier=str(template.pk), metadata={'category': template.category},
        )

    def perform_update(self, serializer):
        template = serializer.save()
        audit(
            'email_template_updated', request=self.request, user=self.request.user,
            identifier=str(template.pk), metadata={'category': template.category},
        )

    def perform_destroy(self, instance):
        audit(
            'email_template_deleted', request=self.request, user=self.request.user,
            identifier=str(instance.pk), metadata={'name': instance.name},
        )
        instance.delete()

    @action(detail=False, methods=['get'])
    def categories(self, request):
        """Preset categories plus every custom one already saved."""
        return Response({'categories': EmailTemplate.used_categories()})

    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """Copy a template into a fresh, independently editable one."""
        source = self.get_object()
        clone = EmailTemplate.objects.create(
            name=f'Copy of {source.name}'[:200],
            category=source.category,
            description=source.description,
            subject=source.subject,
            heading=source.heading,
            preview_text=source.preview_text,
            body_html=source.body_html,
            plain_text=source.plain_text,
            cta_label=source.cta_label,
            cta_url=source.cta_url,
            footer_content=source.footer_content,
            is_favorite=False,
            created_by=request.user,
        )
        audit(
            'email_template_duplicated', request=request, user=request.user,
            identifier=str(source.pk), metadata={'new_template': clone.pk},
        )
        return Response(
            EmailTemplateAdminSerializer(clone, context={'request': request}).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=['get'])
    def preview(self, request, pk=None):
        """Render the template in the branded layout, personalized for the viewer."""
        template = self.get_object()
        body_html = template.body_html
        if template.footer_content:
            from html import escape as _escape
            footer_paragraphs = [
                line.strip() for line in template.footer_content.splitlines() if line.strip()
            ]
            body_html += ''.join(f'<p>{_escape(paragraph)}</p>' for paragraph in footer_paragraphs)

        from types import SimpleNamespace
        as_campaign = SimpleNamespace(
            subject=template.subject,
            heading=template.heading,
            name=template.name,
            body='',
            body_html=body_html,
            plain_text_alternative=template.plain_text,
            cta_label=template.cta_label,
            cta_url=template.cta_url,
        )

        name = email_composer.display_name(request.user)
        email = request.user.email or ''
        html, text = email_campaigns.render_composed_email(
            as_campaign, name=name, email=email, student_id=request.user.username,
            has_account=True, user=request.user,
        )
        variables = email_composer.recipient_variables(
            name=name, email=email, student_id=request.user.username,
        )
        subject = email_composer.personalize(template.subject, variables)
        return Response({'html': html, 'text': text, 'subject': subject})


@api_view(['GET'])
@permission_classes([IsSuperAdmin])
def email_settings(request):
    """Transport configuration for the Email Settings panel.

    Credentials stay server-side: the response describes which settings are
    configured and shows the username, but the password is never included.
    """
    default = settings.MAILERS.get('default', {})
    options = default.get('OPTIONS', {})
    backend = default.get('BACKEND', '')
    is_smtp = 'smtp' in backend.lower()
    return Response({
        'backend': backend,
        'is_smtp': is_smtp,
        'host': options.get('host', '') if is_smtp else '',
        'port': options.get('port', None),
        'username': options.get('username', '') if is_smtp else '',
        'password_configured': bool(options.get('password')),
        'use_tls': options.get('use_tls', False),
        'use_ssl': options.get('use_ssl', False),
        'from_email': settings.DEFAULT_FROM_EMAIL,
        'delivery_ready': is_smtp and bool(options.get('host')),
        'note': (
            'SMTP credentials are configured through backend environment '
            'variables (EMAIL_HOST, EMAIL_PORT, EMAIL_HOST_USER, '
            'EMAIL_HOST_PASSWORD, EMAIL_USE_TLS) and are never exposed here.'
        ),
    })


# ─── Audit Logs (Admin) ─────────────────────────────────────────────────────────

class AuditLogAdminSerializer(serializers.ModelSerializer):
    admin_name = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = AuthenticationAuditLog
        fields = [
            'id', 'user', 'admin_name', 'event', 'identifier', 'ip_address',
            'user_agent', 'metadata', 'created_at',
        ]
        read_only_fields = fields


class EmailThemeAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailTheme
        fields = ['id', 'slug', 'name', 'description', 'best_for', 'primary_color',
                  'accent_color', 'highlight_color', 'background_color', 'is_default',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class EmailThemeAdminViewSet(viewsets.ModelViewSet):
    queryset = EmailTheme.objects.all()
    serializer_class = EmailThemeAdminSerializer
    permission_classes = [IsSuperAdmin]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering = ['name']


class EmailAutomationRuleAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailAutomationRule
        fields = ['id', 'trigger', 'name', 'description', 'enabled', 'template',
                  'theme', 'subject_override', 'delay_minutes', 'recipient_group',
                  'last_run_at', 'success_count', 'failure_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'last_run_at', 'success_count', 'failure_count', 'created_at', 'updated_at']


class EmailAutomationRuleAdminViewSet(viewsets.ModelViewSet):
    queryset = EmailAutomationRule.objects.select_related('template').all()
    serializer_class = EmailAutomationRuleAdminSerializer
    permission_classes = [IsSuperAdmin]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'trigger', 'description']
    ordering = ['name']

    @action(detail=True, methods=['post'])
    def toggle(self, request, pk=None):
        obj = self.get_object()
        obj.enabled = not obj.enabled
        obj.save(update_fields=['enabled', 'updated_at'])
        return Response(EmailAutomationRuleAdminSerializer(obj).data)

    @action(detail=True, methods=['post'])
    def test(self, request, pk=None):
        obj = self.get_object()
        to_email = request.data.get('to_email') or request.user.email
        from .services.email_campaigns import send_test_email
        from django.contrib.auth import get_user_model
        User = get_user_model()
        data = {
            'subject': obj.subject_override or (obj.template.subject if obj.template else 'Test'),
            'heading': (obj.template.heading if obj.template else obj.name),
            'body_html': (obj.template.body_html if obj.template else '<p>Test</p>'),
            'cta_label': (obj.template.cta_label if obj.template else ''),
            'cta_url': (obj.template.cta_url if obj.template else ''),
        }
        result = send_test_email(data, request.user, to_email=to_email)
        return Response(result)


class AuditLogAdminViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AuthenticationAuditLog.objects.select_related('user').all()
    serializer_class = AuditLogAdminSerializer
    permission_classes = [IsAdministrator]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['user__username', 'user__email', 'identifier', 'event']
    ordering_fields = ['created_at']

    def get_queryset(self):
        qs = super().get_queryset()
        event = self.request.query_params.get('event')
        if event:
            qs = qs.filter(event=event)
        return qs


# ─── Settings (Admin) ──────────────────────────────────────────────────────────

@api_view(['GET', 'PATCH'])
@permission_classes([IsSuperAdmin])
def admin_settings(request):
    """Return or update platform settings."""
    maintenance_settings = MaintenanceSettings.get_solo()
    setting, _ = PlatformSetting.objects.get_or_create(
        key='platform',
        defaults={'value': {
            'platform_name': 'Code Yaar',
            'maintenance_mode': False,
            'maintenance_message': '',
            'estimated_return_time': '',
            'enrollment_enabled': True,
        }},
    )
    values = setting.value
    if request.method == 'PATCH':
        allowed = {'platform_name', 'enrollment_enabled'}
        values.update({key: value for key, value in request.data.items() if key in allowed})
        setting.value = values
        setting.save(update_fields=['value', 'updated_at'])
        maintenance_updates = {}
        if 'maintenance_mode' in request.data:
            maintenance_updates['is_enabled'] = serializers.BooleanField().to_internal_value(
                request.data['maintenance_mode']
            )
        if 'maintenance_message' in request.data:
            maintenance_updates['maintenance_message'] = request.data['maintenance_message']
        if 'estimated_return_time' in request.data:
            parsed = serializers.DateTimeField(
                allow_null=True, required=False
            ).to_internal_value(request.data['estimated_return_time']) if request.data['estimated_return_time'] else None
            maintenance_updates['estimated_return_time'] = parsed
        if maintenance_updates:
            for key, value in maintenance_updates.items():
                setattr(maintenance_settings, key, value)
            maintenance_settings.save(update_fields=[*maintenance_updates, 'updated_at'])
    return Response({
        'platform_name': values.get('platform_name', 'Code Yaar'),
        'logo_light': '/brand/logo.png',
        'logo_dark': '/brand/logo.png',
        'default_course_visibility': 'published',
        'supported_classes': ['Class X', 'Class XI', 'Class XII'],
        'supported_subjects': ['Computer Science'],
        'default_difficulty_options': ['beginner', 'intermediate', 'advanced'],
        'enrollment_enabled': values.get('enrollment_enabled', True),
        'notification_preferences': values.get('notification_preferences', {}),
        'maintenance_mode': maintenance_settings.is_enabled,
        'maintenance_message': maintenance_settings.maintenance_message,
        'estimated_return_time': (
            maintenance_settings.estimated_return_time.isoformat()
            if maintenance_settings.estimated_return_time else ''
        ),
    })


@api_view(['GET'])
def public_platform_status(request):
    # The cached snapshot (invalidated on save) answers the frontend's
    # 15-second poll without a database round trip each time.
    try:
        snapshot = MaintenanceSettings.snapshot()
    except DatabaseError:
        logger.exception('public-platform-status database failure')
        return Response({'detail': 'Database temporarily unavailable.'}, status=503)
    return Response({
        'maintenance_mode': snapshot['is_enabled'],
        'maintenance_message': snapshot['message'] or
            'We are making improvements and will be back shortly.',
        'estimated_return_time': (
            snapshot['estimated_return_time'].isoformat()
            if snapshot['estimated_return_time'] else ''
        ),
    })


# ─── Roles (Admin) ─────────────────────────────────────────────────────────────

@api_view(['GET', 'POST'])
@permission_classes([IsAdministrator])
def admin_roles(request):
    """The real role directory, and super-user-only group assignment.

    This endpoint previously returned four hardcoded dictionaries that existed nowhere
    in the database - the roles page was a picture of a permission system. It now reads
    Django groups and the capability matrix, so what the panel shows is what the API
    actually enforces.

    Assignment is restricted to a super user, and nobody may change their own group
    membership: an administrator must not be able to hand themselves a privilege.
    """
    from django.contrib.auth.models import Group

    if request.method == 'GET':
        from .services.admin_access import (
            PLATFORM_ADMINISTRATOR_CAPABILITIES, ROLE_CAPABILITIES, SUPER_ADMIN_CAPABILITIES,
        )

        groups = {g.name: g for g in Group.objects.all()}
        rows = [{
            'id': 1,
            'name': 'Super Admin',
            'group': None,
            'description': 'Full platform control, including role assignment.',
            'capabilities': ['* (all capabilities)'],
            'member_count': User.objects.filter(is_superuser=True).count(),
            'label': 'Super Admin',
        }, {
            'id': 2,
            'name': 'Platform Administrator',
            'group': ADMIN_GROUP,
            'description': 'Runs the whole admin panel; role changes need a super user.',
            'capabilities': ['* (all capabilities)'],
            'member_count': groups[ADMIN_GROUP].user_set.count() if ADMIN_GROUP in groups else 0,
            'label': 'Platform Administrator',
        }]
        order = 3
        for spec_role, group_name in sorted(ROLE_GROUPS.items()):
            group = groups.get(group_name)
            rows.append({
                'id': order,
                'name': group_name,
                'group': group_name,
                'description': f'Scope-limited admin role ({spec_role}).',
                'capabilities': sorted(ROLE_CAPABILITIES[spec_role]),
                'member_count': group.user_set.count() if group else 0,
                'label': group_name,
            })
            order += 1
        rows.append({
            'id': order,
            'name': 'Instructor',
            'group': INSTRUCTOR_GROUP,
            'description': 'Editorial access to assigned courses only.',
            'capabilities': sorted(ROLE_CAPABILITIES['instructor']),
            'member_count': (
                groups[INSTRUCTOR_GROUP].user_set.count() if INSTRUCTOR_GROUP in groups else 0
            ),
            'label': 'Instructor',
        })
        return Response({
            'roles': rows,
            'your_roles': resolve_admin_roles(request.user),
            'your_capabilities': sorted(resolve_capabilities(request.user)),
            'can_assign_roles': can_manage_roles(request.user),
        })

    if not can_manage_roles(request.user):
        return Response({
            'detail': 'Only a super user can assign administrative roles.',
            'code': 'roles_locked',
        }, status.HTTP_403_FORBIDDEN)

    group_name = (request.data.get('group') or '').strip()
    user_id = request.data.get('user')
    operation = (request.data.get('action') or 'add').lower()
    valid_groups = {ADMIN_GROUP, INSTRUCTOR_GROUP, *ROLE_GROUPS.values()}
    if group_name not in valid_groups:
        return Response({'detail': 'Unknown role group.'}, status.HTTP_400_BAD_REQUEST)
    if str(user_id) == str(request.user.pk):
        # The self-escalation guard: a super user editing their own groups could remove
        # their own access by accident, and a non-super caller never reaches this line.
        return Response({
            'detail': 'You cannot change your own role assignments.',
            'code': 'self_modification_forbidden',
        }, status.HTTP_400_BAD_REQUEST)

    target = get_object_or_404(User, pk=user_id)
    group = Group.objects.get(name=group_name)
    if operation == 'remove':
        target.groups.remove(group)
        event = 'role.remove'
    else:
        target.groups.add(group)
        event = 'role.add'
    record_admin_action(
        request.user, event, obj=target, label=target.username,
        detail={'group': group_name}, request=request,
    )
    return Response({
        'status': 'ok',
        'user': target.username,
        'group': group_name,
        'roles': [name for name in target.groups.values_list('name', flat=True)],
    })
