from rest_framework import serializers, viewsets, permissions, status, filters
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db.models import F, Sum, Count
from django.shortcuts import get_object_or_404
from django.utils import timezone

from .models import (
    UserProfile, CareerTrack, Course, Chapter, Lesson, Exercise, Hint,
    Resource, Project, Challenge, Enrollment, SnippetRun,
    LessonProgress, ExerciseAttempt, XPTransaction, Achievement,
    UserAchievement, Progress, Certification, UserCertification,
    Skill, UserSkill,
)
from .services.sandbox import get_sandbox
from .serializers import (
    UserSerializer, RegisterSerializer, UserProfileSerializer,
    CareerTrackSerializer, CareerTrackListSerializer,
    CourseListSerializer, CourseDetailSerializer,
    ChapterListSerializer, ChapterDetailSerializer,
    LessonListSerializer, LessonDetailSerializer,
    ExerciseListSerializer, ExerciseDetailSerializer,
    HintSerializer, ResourceSerializer,
    ProjectSerializer, ChallengeSerializer,
    EnrollmentSerializer, LessonProgressSerializer,
    ExerciseAttemptSerializer, XPTransactionSerializer,
    AchievementSerializer, UserAchievementSerializer,
    ProgressSerializer,
    CertificationSerializer, UserCertificationSerializer,
    SkillSerializer, UserSkillSerializer,
    ExerciseRunSerializer, ExerciseSubmitSerializer,
)
from .services.sandbox import validate_submission


# ─── Leaderboard Serializer ────────────────────────────────────────────────

class LeaderboardEntrySerializer(serializers.Serializer):
    rank = serializers.IntegerField()
    user_id = serializers.IntegerField()
    username = serializers.CharField()
    xp_points = serializers.IntegerField()
    level = serializers.IntegerField()
    streak_days = serializers.IntegerField()
    courses_completed = serializers.IntegerField()
    challenges_solved = serializers.IntegerField()


# ─── Lesson XP helper ──────────────────────────────────────────────────

def _award_lesson_xp(user, lesson):
    """Award lesson-completion XP exactly once (guarded by XPTransaction)."""
    already = XPTransaction.objects.filter(
        user=user,
        action='lesson_complete',
        content_type=ContentType.objects.get_for_model(lesson),
        object_id=lesson.id,
    ).exists()
    if already or lesson.xp_reward <= 0:
        return 0
    XPTransaction.objects.create(
        user=user,
        amount=lesson.xp_reward,
        action='lesson_complete',
        description=f'Lesson completed: {lesson.title}',
        content_type=ContentType.objects.get_for_model(lesson),
        object_id=lesson.id,
    )
    profile, _ = UserProfile.objects.get_or_create(user=user)
    profile.xp_points += lesson.xp_reward
    profile.save()
    return lesson.xp_reward


# ─── Sandbox snippet execution (lesson code blocks) ──────────────────────

SNIPPET_DAILY_LIMIT = 150


class SnippetRunSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=5000)
    language = serializers.ChoiceField(choices=['python'], default='python')


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def execute_snippet_view(request):
    """
    Run a lesson code snippet in the sandbox (read-only teaching examples).
    Authenticated only, with a per-user daily limit as an abuse guard.
    """
    serializer = SnippetRunSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    code = serializer.validated_data['code']

    today = timezone.now().date()
    counter, _ = SnippetRun.objects.get_or_create(user=request.user, date=today)
    if counter.count >= SNIPPET_DAILY_LIMIT:
        return Response(
            {'error': f'Daily run limit reached ({SNIPPET_DAILY_LIMIT}). '
                      'Try again tomorrow — your exercises are still available.'},
            status=status.HTTP_429_TOO_MANY_REQUESTS,
        )
    counter.count += 1
    counter.save()

    sandbox = get_sandbox()
    result = sandbox.execute(code=code, language=serializer.validated_data['language'])
    return Response({
        'status': result.status,
        'output': result.output,
        'error': result.error,
        'execution_time_ms': result.execution_time_ms,
    })


# ─── Auth Views ─────────────────────────────────────────────────────────────

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register_view(request):
    """Register a new user and return auth token."""
    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    token, _ = Token.objects.get_or_create(user=user)
    return Response({
        'token': token.key,
        'user': UserSerializer(user).data,
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_view(request):
    """Authenticate user and return auth token."""
    from django.contrib.auth import authenticate
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(username=username, password=password)
    if user is None:
        return Response(
            {'error': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    token, _ = Token.objects.get_or_create(user=user)
    return Response({
        'token': token.key,
        'user': UserSerializer(user).data,
    })


@api_view(['GET', 'PUT', 'PATCH'])
@permission_classes([permissions.IsAuthenticated])
def profile_view(request):
    """Get or update the current user's profile."""
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'GET':
        return Response(UserProfileSerializer(profile).data)
    serializer = UserProfileSerializer(profile, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)


# ─── Content ViewSets ───────────────────────────────────────────────────────

class CareerTrackViewSet(viewsets.ReadOnlyModelViewSet):
    """List and retrieve career tracks."""
    queryset = CareerTrack.objects.filter(is_active=True)
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'

    def get_serializer_class(self):
        if self.action == 'list':
            return CareerTrackListSerializer
        return CareerTrackSerializer


class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    """List and retrieve courses."""
    queryset = Course.objects.filter(is_active=True, is_published=True)
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'subtitle']
    ordering_fields = ['title', 'estimated_hours', 'order', 'total_xp']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CourseDetailSerializer
        return CourseListSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        track = self.request.query_params.get('track')
        difficulty = self.request.query_params.get('difficulty')
        language = self.request.query_params.get('language')
        if track:
            qs = qs.filter(track__slug=track)
        if difficulty:
            qs = qs.filter(difficulty=difficulty)
        if language:
            qs = qs.filter(language=language)
        return qs

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def enroll(self, request, slug=None):
        """Enroll the current user in a course."""
        course = self.get_object()
        enrollment, created = Enrollment.objects.get_or_create(
            user=request.user,
            course=course,
            defaults={'status': 'active'}
        )
        if not created:
            return Response(
                {'detail': 'Already enrolled.', 'enrollment_id': enrollment.id},
                status=status.HTTP_200_OK
            )
        return Response(
            EnrollmentSerializer(enrollment).data,
            status=status.HTTP_201_CREATED
        )


class ChapterViewSet(viewsets.ReadOnlyModelViewSet):
    """List and retrieve chapters for a course."""
    permission_classes = [permissions.AllowAny]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ChapterDetailSerializer
        return ChapterListSerializer

    def get_queryset(self):
        course_slug = self.kwargs.get('course_slug')
        return Chapter.objects.filter(
            course__slug=course_slug,
            course__is_active=True,
            is_active=True
        ).order_by('order')


class LessonViewSet(viewsets.ReadOnlyModelViewSet):
    """List and retrieve lessons."""
    permission_classes = [permissions.AllowAny]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return LessonDetailSerializer
        return LessonListSerializer

    def get_queryset(self):
        qs = Lesson.objects.filter(
            chapter__course__is_active=True,
            is_active=True
        ).order_by('chapter__order', 'order')

        course_slug = self.kwargs.get('course_slug')
        chapter_slug = self.kwargs.get('chapter_slug')

        if course_slug:
            qs = qs.filter(chapter__course__slug=course_slug)
        if chapter_slug:
            qs = qs.filter(chapter__slug=chapter_slug)

        return qs

    def get_object(self, queryset=None):
        """
        The course-scoped retrieve URL captures the lesson ``slug`` while the
        completion route captures ``pk``; DRF's default lookup only knows
        about ``pk``. Resolve whichever kwarg the matched pattern provided.
        """
        if 'slug' in self.kwargs:
            obj = get_object_or_404(
                self.filter_queryset(self.get_queryset()), slug=self.kwargs['slug']
            )
            self.check_object_permissions(self.request, obj)
            return obj
        return super().get_object(queryset)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def complete(self, request, pk=None):
        """
        Mark a lesson complete from the reading view.

        Honest rule: a lesson with exercises is only completed when every
        active exercise has a correct attempt (which the submit endpoint
        already tracks). Exercise-free lessons are completed on request —
        this is self-reported reading completion.
        """
        lesson = self.get_object()
        user = request.user

        progress, _ = LessonProgress.objects.get_or_create(
            user=user, lesson=lesson, defaults={'status': 'in_progress'}
        )
        enrollment, _ = Enrollment.objects.get_or_create(
            user=user, course=lesson.chapter.course, defaults={'status': 'active'}
        )

        total_exercises = lesson.exercises.filter(is_active=True).count()
        solved_exercises = ExerciseAttempt.objects.filter(
            user=user, exercise__lesson=lesson, status='correct',
        ).values('exercise').distinct().count()

        xp_awarded = 0
        if progress.status not in ('completed', 'mastered'):
            if total_exercises == 0:
                progress.status = 'completed'
                progress.completed_at = timezone.now()
                progress.save()
                xp_awarded = _award_lesson_xp(user, lesson)
            elif solved_exercises >= total_exercises:
                # All exercises are actually solved; finalize completion + XP once.
                progress.status = 'completed'
                progress.completed_at = timezone.now()
                progress.save()
                xp_awarded = _award_lesson_xp(user, lesson)
            else:
                progress.status = 'in_progress'
                progress.save()

        enrollment.last_lesson = lesson
        enrollment.last_activity_at = timezone.now()
        enrollment.save()

        remaining = max(total_exercises - solved_exercises, 0)
        return Response({
            'status': progress.status,
            'xp_awarded': xp_awarded,
            'exercises_remaining': remaining,
            'message': (
                'Lesson completed.' if progress.status == 'completed' else
                f'Solve {remaining} more exercise{"s" if remaining != 1 else ""} to complete this lesson.'
            ),
        })


class ExerciseViewSet(viewsets.ReadOnlyModelViewSet):
    """List and retrieve exercises."""
    permission_classes = [permissions.AllowAny]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ExerciseDetailSerializer
        return ExerciseListSerializer

    def get_queryset(self):
        qs = Exercise.objects.filter(
            lesson__chapter__course__is_active=True,
            is_active=True
        ).order_by('lesson__chapter__order', 'lesson__order', 'order')

        lesson_id = self.kwargs.get('lesson_id')
        if lesson_id:
            qs = qs.filter(lesson_id=lesson_id)

        return qs

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def run(self, request, pk=None):
        """Run code without validation (just execute)."""
        exercise = self.get_object()
        serializer = ExerciseRunSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        code = serializer.validated_data.get('code', exercise.starter_code)

        # Development adapter: simulate execution
        # In production, this calls the sandbox service
        result = self._execute_code(exercise, code)

        # Create attempt record
        attempt = ExerciseAttempt.objects.create(
            user=request.user,
            exercise=exercise,
            status=result['status'],
            submitted_code=code,
            output=result.get('output', ''),
            error_message=result.get('error', ''),
            attempt_number=ExerciseAttempt.objects.filter(
                user=request.user, exercise=exercise
            ).count() + 1,
        )

        return Response({
            'status': result['status'],
            'output': result.get('output', ''),
            'error': result.get('error', ''),
            'attempt_id': attempt.id,
        })

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def submit(self, request, pk=None):
        """Submit exercise for validation."""
        exercise = self.get_object()
        serializer = ExerciseSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        code = serializer.validated_data.get('code', exercise.starter_code)
        selected_answer = serializer.validated_data.get('selected_answer')
        time_spent = serializer.validated_data.get('time_spent_seconds', 0)

        # Validate based on exercise type
        result = self._validate_exercise(exercise, code, selected_answer)

        # Create attempt
        attempt = ExerciseAttempt.objects.create(
            user=request.user,
            exercise=exercise,
            status=result['status'],
            submitted_code=code,
            selected_answer=selected_answer,
            output=result.get('output', ''),
            error_message=result.get('error', ''),
            feedback=result.get('feedback', ''),
            test_results=result.get('test_results', []),
            time_spent_seconds=time_spent,
            xp_earned=result.get('xp_earned', 0),
            attempt_number=ExerciseAttempt.objects.filter(
                user=request.user, exercise=exercise
            ).count() + 1,
        )

        # If correct, award XP and update progress; auto-enroll so progress
        # is never lost for learners who started reading before enrolling.
        if result['status'] == 'correct':
            Enrollment.objects.get_or_create(
                user=request.user, course=exercise.lesson.chapter.course,
                defaults={'status': 'active'},
            )
            self._award_xp(request.user, exercise, attempt)
            self._update_lesson_progress(request.user, exercise.lesson)

        return Response({
            'status': result['status'],
            'feedback': result.get('feedback', ''),
            'output': result.get('output', ''),
            'error': result.get('error', ''),
            'test_results': result.get('test_results', []),
            'xp_earned': result.get('xp_earned', 0),
            'correct_answer': result.get('correct_answer'),
            'explain': result.get('explain', ''),
            'attempt_id': attempt.id,
        })

    @action(detail=True, methods=['get'], permission_classes=[permissions.AllowAny])
    def hint(self, request, pk=None):
        """Get the next available hint for this exercise."""
        exercise = self.get_object()
        hints_used = ExerciseAttempt.objects.filter(
            user=request.user, exercise=exercise
        ).count() if request.user.is_authenticated else 0

        next_hint = exercise.hints.filter(order__gt=hints_used).first()
        if not next_hint:
            next_hint = exercise.hints.first()  # fallback to first hint

        if not next_hint:
            return Response({'hint': None, 'message': 'No hints available.'})

        # Deduct XP penalty if hint is used (authenticated learners only)
        if request.user.is_authenticated and next_hint.xp_penalty > 0:
            XPTransaction.objects.create(
                user=request.user,
                amount=-next_hint.xp_penalty,
                action='hint_used',
                description=f'Hint used on {exercise.title}',
                content_type=ContentType.objects.get_for_model(exercise),
                object_id=exercise.id,
            )
            profile, _ = UserProfile.objects.get_or_create(user=request.user)
            profile.xp_points = max(0, profile.xp_points - next_hint.xp_penalty)
            profile.save()

        return Response({
            'hint': next_hint.content,
            'order': next_hint.order,
            'reveals_solution': next_hint.reveals_solution,
            'xp_penalty': next_hint.xp_penalty,
        })

    def _execute_code(self, exercise, code):
        """Execute learner code in the configured sandbox service."""
        sandbox = get_sandbox()
        # Feed the first test case's stdin so programs using input() can be
        # run directly from the editor.
        stdin = ''
        for test in (exercise.test_cases or []):
            if isinstance(test.get('input'), str) and test['input']:
                stdin = test['input']
                break
        result = sandbox.execute(code=code, language=exercise.language, stdin=stdin)
        if result.status == 'success':
            return {'status': 'correct', 'output': result.output, 'error': ''}
        return {
            'status': 'error',
            'output': result.output,
            'error': result.error or 'Your program raised an error.',
        }

    def _validate_exercise(self, exercise, code, selected_answer):
        """
        Validate an exercise submission via the shared validation service
        (single source of truth with the sandbox layer).
        """
        result = validate_submission(exercise, code, selected_answer)
        # Map the service 'pending' state onto the client-facing 'running'
        # status: the submission is recorded, but automated evaluation of
        # runnable code is not available yet — never reported as a pass.
        status = 'running' if result.status == 'pending' else result.status
        return {
            'status': status,
            'feedback': result.feedback,
            'test_results': result.test_results,
            'xp_earned': result.xp_earned,
            'correct_answer': result.correct_answer,
            # Revealed only now that the learner has attempted the exercise.
            'explain': exercise.explain,
        }

    def _award_xp(self, user, exercise, attempt):
        """Award XP for correct exercise completion."""
        xp = exercise.xp_reward
        # Reduce XP if hints were used
        hints_penalty = sum(
            h.xp_penalty for h in exercise.hints.filter(order__lte=attempt.hints_used)
        )
        xp = max(10, xp - hints_penalty)  # minimum 10 XP

        attempt.xp_earned = xp
        attempt.save()

        # Update user XP
        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.xp_points += xp
        profile.save()

        # Record transaction
        XPTransaction.objects.create(
            user=user,
            amount=xp,
            action='exercise_complete',
            description=f'Completed: {exercise.title}',
            content_type=ContentType.objects.get_for_model(exercise),
            object_id=exercise.id,
        )

    def _update_lesson_progress(self, user, lesson):
        """Update lesson progress when exercise is completed."""
        progress, _ = LessonProgress.objects.get_or_create(
            user=user,
            lesson=lesson,
            defaults={'status': 'in_progress'}
        )

        # Check if all active exercises in the lesson are solved
        total_exercises = lesson.exercises.filter(is_active=True).count()
        completed_exercises = ExerciseAttempt.objects.filter(
            user=user,
            exercise__lesson=lesson,
            status='correct',
        ).values('exercise').distinct().count()

        if total_exercises > 0 and completed_exercises >= total_exercises \
                and progress.status not in ('completed', 'mastered'):
            progress.status = 'completed'
            progress.completed_at = timezone.now()
            progress.save()

            # Award lesson XP exactly once (guarded against re-award)
            _award_lesson_xp(user, lesson)

        # Update enrollment's last_lesson
        enrollment = Enrollment.objects.filter(
            user=user, course=lesson.chapter.course
        ).first()
        if enrollment:
            enrollment.last_lesson = lesson
            enrollment.last_activity_at = timezone.now()
            enrollment.save()


class ProjectViewSet(viewsets.ReadOnlyModelViewSet):
    """List and retrieve projects."""
    queryset = Project.objects.filter(is_active=True)
    serializer_class = ProjectSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['title', 'estimated_hours']

    def get_queryset(self):
        qs = super().get_queryset()
        track = self.request.query_params.get('track')
        difficulty = self.request.query_params.get('difficulty')
        if track:
            qs = qs.filter(track__slug=track)
        if difficulty:
            qs = qs.filter(difficulty=difficulty)
        return qs


class ChallengeViewSet(viewsets.ReadOnlyModelViewSet):
    """List and retrieve challenges."""
    queryset = Challenge.objects.filter(is_active=True)
    serializer_class = ChallengeSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'topic']
    ordering_fields = ['title', 'estimated_minutes']

    def get_queryset(self):
        qs = super().get_queryset()
        topic = self.request.query_params.get('topic')
        difficulty = self.request.query_params.get('difficulty')
        if topic:
            qs = qs.filter(topic__icontains=topic)
        if difficulty:
            qs = qs.filter(difficulty=difficulty)
        return qs


# ─── Progress ViewSets ──────────────────────────────────────────────────────

class EnrollmentViewSet(viewsets.ModelViewSet):
    """Manage course enrollments for the current user."""
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Enrollment.objects.filter(user=self.request.user).select_related('course', 'course__track')


class LessonProgressViewSet(viewsets.ModelViewSet):
    """Manage lesson progress for the current user."""
    serializer_class = LessonProgressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return LessonProgress.objects.filter(user=self.request.user).select_related(
            'lesson', 'lesson__chapter', 'lesson__chapter__course'
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ExerciseAttemptViewSet(viewsets.ReadOnlyModelViewSet):
    """View exercise attempts for the current user."""
    serializer_class = ExerciseAttemptSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ExerciseAttempt.objects.filter(user=self.request.user).select_related('exercise')


class ProgressViewSet(viewsets.ModelViewSet):
    """Manage generic progress entries for the current user."""
    serializer_class = ProgressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Progress.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# ─── Gamification Views ─────────────────────────────────────────────────────

class XPTransactionViewSet(viewsets.ReadOnlyModelViewSet):
    """View XP history for the current user."""
    serializer_class = XPTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return XPTransaction.objects.filter(user=self.request.user)


class AchievementViewSet(viewsets.ReadOnlyModelViewSet):
    """List all achievements."""
    queryset = Achievement.objects.filter(is_active=True)
    serializer_class = AchievementSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'


class UserAchievementViewSet(viewsets.ReadOnlyModelViewSet):
    """View achievements earned by the current user."""
    serializer_class = UserAchievementSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserAchievement.objects.filter(user=self.request.user).select_related('achievement')


# ─── Certification & Skill Views ────────────────────────────────────────────

class CertificationViewSet(viewsets.ReadOnlyModelViewSet):
    """List available certifications."""
    queryset = Certification.objects.filter(is_active=True)
    serializer_class = CertificationSerializer
    permission_classes = [permissions.AllowAny]


class UserCertificationViewSet(viewsets.ReadOnlyModelViewSet):
    """List certifications earned by the current user."""
    serializer_class = UserCertificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserCertification.objects.filter(user=self.request.user)


class SkillViewSet(viewsets.ReadOnlyModelViewSet):
    """List all skills."""
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    permission_classes = [permissions.AllowAny]


class UserSkillViewSet(viewsets.ModelViewSet):
    """Manage skills for the current user."""
    serializer_class = UserSkillSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserSkill.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# ─── Leaderboard Serializer ────────────────────────────────────────────────

class LeaderboardEntrySerializer(serializers.Serializer):
    rank = serializers.IntegerField()
    user_id = serializers.IntegerField()
    username = serializers.CharField()
    xp_points = serializers.IntegerField()
    level = serializers.IntegerField()
    streak_days = serializers.IntegerField()
    courses_completed = serializers.IntegerField()
    challenges_solved = serializers.IntegerField()


# ─── Leaderboard View ───────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def leaderboard_view(request):
    """Get the global leaderboard ranked by XP."""
    limit = int(request.query_params.get('limit', 50))
    offset = int(request.query_params.get('offset', 0))

    profiles = UserProfile.objects.select_related('user').order_by('-xp_points')
    total = profiles.count()
    page = profiles[offset:offset + limit]

    entries = []
    for rank, profile in enumerate(page, start=offset + 1):
        courses_completed = Enrollment.objects.filter(
            user=profile.user, status='completed'
        ).count()
        challenges_solved = ExerciseAttempt.objects.filter(
            user=profile.user, status='correct'
        ).values('exercise').distinct().count()

        entries.append({
            'rank': rank,
            'user_id': profile.user.id,
            'username': profile.user.username,
            'xp_points': profile.xp_points,
            'level': profile.level,
            'streak_days': profile.streak_days,
            'courses_completed': courses_completed,
            'challenges_solved': challenges_solved,
        })

    return Response({
        'total': total,
        'limit': limit,
        'offset': offset,
        'entries': entries,
    })


# ─── Profile Stats View ─────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def profile_stats_view(request):
    """Get comprehensive profile stats for the current user."""
    user = request.user
    profile, _ = UserProfile.objects.get_or_create(user=user)

    # Enrollment stats
    total_enrollments = Enrollment.objects.filter(user=user).count()
    active_enrollments = Enrollment.objects.filter(user=user, status='active').count()
    completed_courses = Enrollment.objects.filter(user=user, status='completed').count()

    # Exercise stats
    total_attempts = ExerciseAttempt.objects.filter(user=user).count()
    correct_attempts = ExerciseAttempt.objects.filter(user=user, status='correct').count()
    unique_exercises_solved = ExerciseAttempt.objects.filter(
        user=user, status='correct'
    ).values('exercise').distinct().count()

    # Lesson stats
    lessons_completed = LessonProgress.objects.filter(
        user=user, status__in=['completed', 'mastered']
    ).count()
    lessons_in_progress = LessonProgress.objects.filter(
        user=user, status='in_progress'
    ).count()

    # XP breakdown
    xp_by_action = XPTransaction.objects.filter(user=user).values('action').annotate(
        total=Sum('amount')
    )
    xp_breakdown = {item['action']: item['total'] for item in xp_by_action}

    # Recent XP transactions
    recent_xp = XPTransaction.objects.filter(user=user).order_by('-created_at')[:10]
    xp_history = [
        {
            'id': t.id,
            'amount': t.amount,
            'action': t.action,
            'description': t.description,
            'created_at': t.created_at.isoformat(),
        }
        for t in recent_xp
    ]

    # Achievements
    achievements_earned = UserAchievement.objects.filter(
        user=user
    ).select_related('achievement').count()
    total_achievements = Achievement.objects.filter(is_active=True).count()

    # Skills
    skills = UserSkill.objects.filter(user=user).select_related('skill')
    skills_data = [
        {
            'id': us.id,
            'name': us.skill.name,
            'category': us.skill.category,
            'proficiency': us.proficiency,
            'icon': us.skill.icon,
        }
        for us in skills
    ]

    # Certifications
    certs = UserCertification.objects.filter(user=user).select_related('certification')
    certs_data = [
        {
            'id': uc.id,
            'title': uc.certification.title,
            'track_title': uc.certification.track.title,
            'credential_id': uc.credential_id,
            'earned_at': uc.earned_at.isoformat(),
        }
        for uc in certs
    ]

    # Active enrollments detail
    active_enrollments_data = []
    for enrollment in Enrollment.objects.filter(user=user, status='active').select_related('course', 'course__track')[:5]:
        active_enrollments_data.append({
            'id': enrollment.id,
            'course_slug': enrollment.course.slug,
            'course_title': enrollment.course.title,
            'track_title': enrollment.course.track.title,
            'progress_percentage': enrollment.progress_percentage,
            'enrolled_at': enrollment.enrolled_at.isoformat(),
        })

    return Response({
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'date_joined': user.date_joined.isoformat(),
        },
        'profile': {
            'avatar': profile.avatar,
            'bio': profile.bio,
            'role': profile.role,
            'xp_points': profile.xp_points,
            'streak_days': profile.streak_days,
            'level': profile.level,
            'last_active_at': profile.last_active_at.isoformat() if profile.last_active_at else None,
        },
        'stats': {
            'total_enrollments': total_enrollments,
            'active_enrollments': active_enrollments,
            'completed_courses': completed_courses,
            'total_attempts': total_attempts,
            'correct_attempts': correct_attempts,
            'unique_exercises_solved': unique_exercises_solved,
            'lessons_completed': lessons_completed,
            'lessons_in_progress': lessons_in_progress,
            'achievements_earned': achievements_earned,
            'total_achievements': total_achievements,
        },
        'xp_breakdown': xp_breakdown,
        'xp_history': xp_history,
        'skills': skills_data,
        'certifications': certs_data,
        'active_enrollments': active_enrollments_data,
    })


# ─── Settings View ──────────────────────────────────────────────────────────

@api_view(['GET', 'PUT', 'PATCH'])
@permission_classes([permissions.IsAuthenticated])
def settings_view(request):
    """Get or update user account settings (username, email, password)."""
    user = request.user

    if request.method == 'GET':
        return Response({
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'has_password': user.has_usable_password(),
        })

    # Update user fields
    username = request.data.get('username')
    email = request.data.get('email')
    first_name = request.data.get('first_name')
    last_name = request.data.get('last_name')
    current_password = request.data.get('current_password')
    new_password = request.data.get('new_password')

    # Validate username uniqueness
    if username and username != user.username:
        if User.objects.filter(username=username).exclude(id=user.id).exists():
            return Response(
                {'error': 'Username already taken.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        user.username = username

    if email:
        user.email = email
    if first_name is not None:
        user.first_name = first_name
    if last_name is not None:
        user.last_name = last_name

    # Handle password change
    if new_password:
        if not current_password:
            return Response(
                {'error': 'Current password is required to change password.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if not user.check_password(current_password):
            return Response(
                {'error': 'Current password is incorrect.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if len(new_password) < 8:
            return Response(
                {'error': 'New password must be at least 8 characters.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        user.set_password(new_password)
        # Regenerate token after password change
        Token.objects.filter(user=user).delete()

    user.save()

    response_data = {
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
    }

    # If password was changed, return new token
    if new_password:
        token, _ = Token.objects.get_or_create(user=user)
        response_data['token'] = token.key

    return Response(response_data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def settings_profile_view(request):
    """Update profile-specific settings (avatar, bio, role)."""
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    serializer = UserProfileSerializer(profile, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)
