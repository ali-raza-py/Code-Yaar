"""
Admin REST API views for Code Yaar platform administration.

All endpoints are guarded by IsAdministrator (or higher-privilege checks).
They reuse the existing models, serializers, and business logic.
"""
from django.conf import settings
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.db.models import Count, Sum, Q, Avg, F
from django.utils import timezone
from rest_framework import viewsets, permissions, status, filters, serializers
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from .models import (
    UserProfile, CareerTrack, Course, Chapter, Lesson, Exercise,
    Resource, Challenge, Enrollment, Achievement, UserAchievement,
    Certification, UserCertification, Competition, UserNotification,
    AuthenticationAuditLog, Announcement, LessonProgress, PlatformSetting, MaintenanceSettings, Practical, PracticalClass, PracticalSubject,
    CompetitionRegistration, RegistrationFormField, PlatformUpdate,
    EmailCampaign, EmailCampaignRecipient,
    seed_default_registration_fields,
)
from .permissions import IsAdministrator, IsSuperAdmin
from .services.auth import audit
from .services import email_campaigns
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
    from django.contrib.auth import get_user_model
    User = get_user_model()

    total_students = UserProfile.objects.filter(role='student').count()
    active_students = UserProfile.objects.filter(
        role='student', last_active_at__gte=timezone.now() - timezone.timedelta(days=7)
    ).count()

    total_courses = Course.objects.filter(is_active=True).count()
    published_courses = Course.objects.filter(is_active=True, is_published=True).count()

    total_tracks = CareerTrack.objects.count()
    published_tracks = CareerTrack.objects.filter(is_published=True).count()

    total_enrollments = Enrollment.objects.count()
    active_enrollments = Enrollment.objects.filter(status='active').count()
    completed_courses = Enrollment.objects.filter(status='completed').count()

    total_assessments = Exercise.objects.filter(
        is_final_assessment=True, is_active=True
    ).count()

    total_challenges = Challenge.objects.filter(is_active=True).count()

    certificates_issued = UserCertification.objects.count()

    active_competitions = Competition.objects.filter(
        is_published=True
    ).count()

    return Response({
        'totalStudents': total_students,
        'activeStudents': active_students,
        'totalCourses': total_courses,
        'publishedCourses': published_courses,
        'totalTracks': total_tracks,
        'publishedTracks': published_tracks,
        'totalEnrollments': total_enrollments,
        'activeEnrollments': active_enrollments,
        'completedCourses': completed_courses,
        'totalAssessments': total_assessments,
        'totalChallenges': total_challenges,
        'certificatesIssued': certificates_issued,
        'activeCompetitions': active_competitions,
    })


@api_view(['GET'])
@permission_classes([IsAdministrator])
def admin_recent_activity(request):
    """Return recent administrative activity."""
    limit = int(request.query_params.get('limit', 20))

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

    return Response(activities)


@api_view(['GET'])
@permission_classes([IsAdministrator])
def admin_top_courses(request):
    """Return top courses by enrollment count."""
    limit = int(request.query_params.get('limit', 10))

    courses = Course.objects.filter(is_active=True).annotate(
        enrollment_count=Count('enrollments'),
        completed_count=Count('enrollments', filter=Q(enrollments__status='completed')),
    ).order_by('-enrollment_count')[:limit]

    result = []
    for course in courses:
        total_lessons = Lesson.objects.filter(chapter__course=course).count()
        completed_lessons = LessonProgress.objects.filter(
            lesson__chapter__course=course, status='completed'
        ).count() if total_lessons > 0 else 0
        completion_rate = round((completed_lessons / total_lessons) * 100) if total_lessons > 0 else 0

        result.append({
            'id': course.id,
            'title': course.title,
            'track': course.track.title,
            'enrollments': course.enrollment_count,
            'completionRate': completion_rate,
        })

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
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_courses_count(self, obj):
        return obj.courses.count()

    def get_published_courses_count(self, obj):
        return obj.courses.filter(is_active=True, is_published=True).count()


class CareerTrackAdminViewSet(viewsets.ModelViewSet):
    queryset = CareerTrack.objects.all()
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
        return obj.chapters.count()

    def get_lesson_count(self, obj):
        return Lesson.objects.filter(chapter__course=obj).count()

    def get_exercise_count(self, obj):
        return Exercise.objects.filter(lesson__chapter__course=obj).count()

    def get_enrollment_count(self, obj):
        return obj.enrollments.count()

    def get_completion_rate(self, obj):
        total = obj.enrollments.count()
        if total == 0:
            return 0
        completed = obj.enrollments.filter(status='completed').count()
        return round((completed / total) * 100)


class CourseAdminViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.select_related('track').all()
    serializer_class = CourseAdminSerializer
    permission_classes = [IsAdministrator]
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
        course = self.get_object()
        course.is_published = True
        course.is_active = True
        course.save(update_fields=['is_published', 'is_active'])
        return Response(self.get_serializer(course).data)

    @action(detail=True, methods=['post'])
    def unpublish(self, request, pk=None):
        course = self.get_object()
        course.is_published = False
        course.save(update_fields=['is_published'])
        return Response(self.get_serializer(course).data)

    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        course = self.get_object()
        new_course = Course.objects.create(
            slug=f"{course.slug}-copy",
            title=f"{course.title} (Copy)",
            subtitle=course.subtitle,
            description=course.description,
            thumbnail=course.thumbnail,
            track=course.track,
            academic_class=course.academic_class,
            difficulty=course.difficulty,
            language=course.language,
            instructor=course.instructor,
            prerequisites=course.prerequisites,
            learning_objectives=course.learning_objectives,
            is_free=course.is_free,
            order=course.order + 1,
            is_published=False,
            is_active=True,
        )
        # Duplicate chapters and lessons
        for chapter in course.chapters.all():
            new_chapter = Chapter.objects.create(
                course=new_course,
                title=chapter.title,
                slug=chapter.slug,
                description=chapter.description,
                order=chapter.order,
                xp_reward=chapter.xp_reward,
                is_active=chapter.is_active,
                source_type=chapter.source_type,
                verification_status=chapter.verification_status,
                textbook_board=chapter.textbook_board,
                textbook_class=chapter.textbook_class,
                textbook_unit=chapter.textbook_unit,
                textbook_topic=chapter.textbook_topic,
                textbook_pages=chapter.textbook_pages,
            )
            for lesson in chapter.lessons.all():
                new_lesson = Lesson.objects.create(
                    chapter=new_chapter,
                    title=lesson.title,
                    slug=lesson.slug,
                    content_type=lesson.content_type,
                    learning_objective=lesson.learning_objective,
                    content_body=lesson.content_body,
                    video_url=lesson.video_url,
                    video_duration_seconds=lesson.video_duration_seconds,
                    order=lesson.order,
                    duration_minutes=lesson.duration_minutes,
                    xp_reward=lesson.xp_reward,
                    is_free_preview=lesson.is_free_preview,
                    is_active=lesson.is_active,
                    source_type=lesson.source_type,
                    verification_status=lesson.verification_status,
                    textbook_board=lesson.textbook_board,
                    textbook_class=lesson.textbook_class,
                    textbook_unit=lesson.textbook_unit,
                    textbook_topic=lesson.textbook_topic,
                    textbook_pages=lesson.textbook_pages,
                )
        return Response(self.get_serializer(new_course).data, status=status.HTTP_201_CREATED)

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
                'enrollment_count': e.user.enrollments.count(),
                'completed_courses': e.user.enrollments.filter(status='completed').count(),
                'completed_lessons': LessonProgress.objects.filter(user=e.user, status='completed').count(),
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
        return obj.lessons.count()

    def get_exercise_count(self, obj):
        return Exercise.objects.filter(lesson__chapter=obj).count()


class ChapterAdminViewSet(viewsets.ModelViewSet):
    queryset = Chapter.objects.select_related('course').all()
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
        items = request.data.get('items', [])
        course_id = request.data.get('course_id')
        with transaction.atomic():
            for item in items:
                Chapter.objects.filter(id=item['id']).update(order=item['order'])
        return Response({'status': 'ok'})


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
        return obj.exercises.count()


class LessonAdminViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.select_related('chapter', 'chapter__course').all()
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
        items = request.data.get('items', [])
        with transaction.atomic():
            for item in items:
                Lesson.objects.filter(id=item['id']).update(order=item['order'])
        return Response({'status': 'ok'})


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
        return obj.user.enrollments.count()

    def get_completed_courses(self, obj):
        return obj.user.enrollments.filter(status='completed').count()

    def get_completed_lessons(self, obj):
        return LessonProgress.objects.filter(user=obj.user, status='completed').count()


class StudentAdminViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = UserProfile.objects.filter(role='student').select_related('user')
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

        certificates = UserCertification.objects.filter(user=user)
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

    class Meta:
        model = Enrollment
        fields = [
            'id', 'user', 'student_name', 'student_email', 'course', 'course_title',
            'course_slug', 'track_title', 'enrolled_at', 'completed_at',
            'last_activity_at', 'status', 'progress_percentage',
        ]
        read_only_fields = ['id', 'enrolled_at', 'completed_at', 'last_activity_at']


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
        return obj.user_achievements.count()


class AchievementAdminViewSet(viewsets.ModelViewSet):
    queryset = Achievement.objects.all()
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
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.SerializerMethodField()

    class Meta:
        model = EmailCampaignRecipient
        fields = ['id', 'user', 'username', 'email', 'status', 'error', 'sent_at', 'created_at']
        read_only_fields = fields

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

    class Meta:
        model = EmailCampaign
        fields = [
            'id', 'name', 'subject', 'heading', 'body', 'template', 'banner_image',
            'cta_label', 'cta_url', 'audience', 'competition', 'essential',
            'related_announcement', 'related_update', 'status', 'recipient_count',
            'sent_count', 'failed_count', 'skipped_count', 'sent_at',
            'created_by', 'created_by_name', 'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'status', 'recipient_count', 'sent_count', 'failed_count',
            'skipped_count', 'sent_at', 'created_by', 'created_by_name',
            'created_at', 'updated_at',
        ]


class EmailCampaignAdminViewSet(viewsets.ModelViewSet):
    """Compose, preview, and send platform email campaigns.

    Every route requires Super Admin; sending additionally requires an
    explicit ``confirm`` flag and only works from a draft, so a resent
    request can never double-mail the audience.
    """

    queryset = EmailCampaign.objects.select_related('created_by', 'competition').all()
    serializer_class = EmailCampaignAdminSerializer
    permission_classes = [IsSuperAdmin]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'subject']
    ordering_fields = ['created_at', 'sent_at', 'status']

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['get'], url_path='audience-count')
    def audience_count(self, request, pk=None):
        campaign = self.get_object()
        return Response({
            'audience': campaign.audience,
            'count': email_campaigns.audience_count(campaign),
        })

    @action(detail=True, methods=['get'])
    def preview(self, request, pk=None):
        """Render the campaign exactly as one recipient would see it."""
        campaign = self.get_object()
        html, text = email_campaigns.render_campaign_email(campaign, request.user)
        return Response({'html': html, 'text': text})

    @action(detail=True, methods=['post'])
    def test(self, request, pk=None):
        """Send the campaign to the requesting admin's own address only."""
        campaign = self.get_object()
        if not request.user.email:
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
                'template': campaign.template,
                'cta_label': campaign.cta_label,
                'cta_url': campaign.cta_url,
            },
            request.user,
        )
        audit(
            'email_campaign_test_sent', request=request, user=request.user,
            identifier=str(campaign.pk), metadata={'result': result['status']},
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
        count = email_campaigns.audience_count(campaign)
        if count == 0:
            return Response(
                {'detail': 'This audience has no recipients yet.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        campaign.status = EmailCampaign.Status.QUEUED
        campaign.save(update_fields=['status', 'updated_at'])
        audit(
            'email_campaign_queued', request=request, user=request.user,
            identifier=str(campaign.pk), metadata={'audience': campaign.audience, 'count': count},
        )
        pk = campaign.pk
        transaction.on_commit(
            lambda: email_campaigns.dispatch_campaign(EmailCampaign.objects.get(pk=pk))
        )
        return Response(
            {'status': campaign.status, 'estimated_recipients': count},
            status=status.HTTP_202_ACCEPTED,
        )

    @action(detail=True, methods=['get'], url_path='recipients')
    def recipients(self, request, pk=None):
        campaign = self.get_object()
        qs = campaign.recipients.select_related('user').all()
        status_filter = request.query_params.get('status')
        if status_filter:
            qs = qs.filter(status=status_filter)
        page = self.paginate_queryset(qs)
        serializer = EmailCampaignRecipientAdminSerializer(
            page if page is not None else qs, many=True, context={'request': request},
        )
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)


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
    settings = MaintenanceSettings.objects.filter(pk=MaintenanceSettings.SINGLETON_PK).first()
    return Response({
        'maintenance_mode': bool(settings and settings.is_enabled),
        'maintenance_message': (settings.maintenance_message if settings else '') or
            'We are making improvements and will be back shortly.',
        'estimated_return_time': (
            settings.estimated_return_time.isoformat()
            if settings and settings.estimated_return_time else ''
        ),
    })


# ─── Roles (Admin) ─────────────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsAdministrator])
def admin_roles(request):
    """Return available roles."""
    return Response([
        {'id': 1, 'name': 'Super Admin', 'permissions': ['all']},
        {'id': 2, 'name': 'Content Admin', 'permissions': ['courses', 'tracks', 'chapters', 'lessons', 'exercises']},
        {'id': 3, 'name': 'Instructor', 'permissions': ['assigned_courses', 'assessments']},
        {'id': 4, 'name': 'Moderator', 'permissions': ['moderation']},
    ])
