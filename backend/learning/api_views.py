from datetime import timedelta

from rest_framework import serializers, viewsets, permissions, status, filters
from rest_framework.decorators import api_view, permission_classes, action, throttle_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import F, Sum, Count, Q, Avg, Case, When, Value, IntegerField
from django.http import FileResponse, HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone

from .models import (
    UserProfile, CareerTrack, Course, Chapter, Lesson, Exercise, Hint,
    Resource, Project, Challenge, ChallengeSubmission, Enrollment, SnippetRun,
    LessonProgress, ExerciseAttempt, XPTransaction, Achievement,
    UserAchievement, Progress, Certification, UserCertification,
    Skill, UserSkill,
    PracticalClass, PracticalSubject, Practical, PracticalProgress,
    PracticalBookmark, LearningActivity, UserNotification,
)
from .services.sandbox import get_sandbox, DevelopmentSandbox
from .services.xp import award_xp, deduct_xp
from .services.achievements import award_eligible_achievements
from .services.completion import evaluate_course_completion
from .services.progress import (
    MEANINGFUL_ACTIVITY_TYPES,
    record_learning_activity,
    streak_summary,
)
from .permissions import IsEmailVerified, IsAdministrator
from .serializers import (
    CareerTrackSerializer, CareerTrackListSerializer,
    CourseListSerializer, CourseDetailSerializer,
    ChapterListSerializer, ChapterDetailSerializer,
    LessonListSerializer, LessonDetailSerializer,
    ExerciseListSerializer, ExerciseDetailSerializer,
    HintSerializer, ResourceSerializer,
    ProjectSerializer, ChallengeSerializer,
    ChallengeDetailSerializer, ChallengeRunSerializer, ChallengeSubmitSerializer,
    EnrollmentSerializer, LessonProgressSerializer,
    ExerciseAttemptSerializer, XPTransactionSerializer,
    AchievementSerializer, UserAchievementSerializer,
    UserNotificationSerializer, NotificationPreferenceSerializer,
    AvatarUploadSerializer,
    ProgressSerializer,
    CertificationSerializer, UserCertificationSerializer,
    SkillSerializer, UserSkillSerializer,
    ExerciseRunSerializer, ExerciseSubmitSerializer,
    PracticalClassSerializer, PracticalSubjectSerializer,
    PracticalListSerializer, PracticalDetailSerializer,
    PracticalProgressSerializer, PracticalBookmarkSerializer,
    PracticalClassAdminSerializer, PracticalSubjectAdminSerializer,
    PracticalAdminSerializer,
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
    transaction = award_xp(
        user, lesson.xp_reward, 'lesson_complete', obj=lesson,
        description=f'Lesson completed: {lesson.title}',
    )
    return transaction.amount if transaction else 0


def _badge_announcements(newly_awarded):
    """Compact payload describing badges unlocked by this action.

    Lets completion responses announce unlocks in-band, so the client shows
    the toast immediately rather than polling the notifications feed.
    """
    return [
        {
            'slug': ua.achievement.slug,
            'title': ua.achievement.title,
            'description': ua.achievement.description,
            'icon': ua.achievement.icon,
            'category': ua.achievement.category,
            'difficulty': ua.achievement.difficulty,
            'xp_bonus': ua.achievement.xp_bonus,
            'public_id': ua.public_id,
            'credential_id': ua.credential_id,
        }
        for ua in newly_awarded
    ]


# ─── Sandbox snippet execution (lesson code blocks) ──────────────────────

SNIPPET_DAILY_LIMIT = 150


class SnippetRunSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=5000)
    # Only languages the configured sandbox really executes. JavaScript/Java
    # snippets stay non-runnable in the UI rather than pretending to run.
    language = serializers.ChoiceField(choices=['python', 'cpp'], default='python')


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


# ─── Content ViewSets ───────────────────────────────────────────────────────

class CareerTrackViewSet(viewsets.ReadOnlyModelViewSet):
    """List and retrieve published learning tracks.

    The learner-facing Tracks page is driven entirely by these records:
    admins create, categorize, sequence and publish tracks in the dashboard
    — nothing about the hierarchy is hardcoded in the frontend.
    """
    queryset = CareerTrack.objects.filter(is_active=True, is_published=True)
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['order', 'title', 'estimated_hours']

    def get_serializer_class(self):
        if self.action == 'list':
            return CareerTrackListSerializer
        return CareerTrackSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        category = self.request.query_params.get('category')
        if category:
            qs = qs.filter(category=category)
        # Tracks without a single openable course are not a browseable
        # destination, so they never reach the learner-facing list.
        qs = qs.filter(courses__is_active=True, courses__is_published=True).distinct()
        return qs

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[permissions.IsAuthenticated, IsEmailVerified],
    )
    def enroll(self, request, slug=None):
        """Enroll the current user in every published course of a track.

        Follows the same rules as course enrollment (idempotent
        get_or_create), so re-clicking Enroll never duplicates rows and
        already-started courses keep their progress untouched.
        """
        track = self.get_object()
        courses = list(track.published_courses)
        if not courses:
            return Response(
                {'detail': 'This track has no published courses yet.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        enrolled, newly = [], []
        for course in courses:
            enrollment, created = Enrollment.objects.get_or_create(
                user=request.user, course=course, defaults={'status': 'active'}
            )
            enrolled.append(enrollment)
            if created:
                newly.append(course.slug)
        return Response(
            EnrollmentSerializer(enrolled, many=True).data,
            status=status.HTTP_201_CREATED if newly else status.HTTP_200_OK,
        )


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

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[permissions.IsAuthenticated, IsEmailVerified],
    )
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
        record_learning_activity(
            request.user, 'course_started', f'Started {course.title}',
            course=course,
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
    """List and retrieve lessons; completing one is the only write action."""
    permission_classes = [permissions.AllowAny]
    # These routes are wired with explicit `as_view({'post': ...})` mappings in
    # api_urls.py, which drop the per-action kwargs a router would apply, so the
    # requirement is resolved from `self.action` instead.
    action_permissions = {
        'complete': [permissions.IsAuthenticated],
    }

    def get_permissions(self):
        classes = self.action_permissions.get(self.action, self.permission_classes)
        return [permission() for permission in classes]

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

    def get_object(self):
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
        return super().get_object()

    @action(detail=True, methods=['post'])
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
        if progress.status == 'completed':
            record_learning_activity(
                user, 'lesson_completed', f'Completed {lesson.title}',
                course=lesson.chapter.course, lesson=lesson,
            )

        # Re-evaluate strict, server-side course completion now that lesson
        # state may have changed.
        evaluate_course_completion(user, lesson.chapter.course)
        awarded = award_eligible_achievements(user, lesson=lesson)

        remaining = max(total_exercises - solved_exercises, 0)
        return Response({
            'status': progress.status,
            'xp_awarded': xp_awarded,
            'exercises_remaining': remaining,
            'awarded_badges': _badge_announcements(awarded),
            'message': (
                'Lesson completed.' if progress.status == 'completed' else
                f'Solve {remaining} more exercise{"s" if remaining != 1 else ""} to complete this lesson.'
            ),
        })


class ExerciseViewSet(viewsets.ReadOnlyModelViewSet):
    """List and retrieve exercises."""
    permission_classes = [permissions.AllowAny]
    # See LessonViewSet.action_permissions: explicit `as_view` mappings do not
    # carry the per-action kwargs, so `self.action` decides.
    action_permissions = {
        'run': [permissions.IsAuthenticated],
        'submit': [permissions.IsAuthenticated, IsEmailVerified],
    }

    def get_permissions(self):
        classes = self.action_permissions.get(self.action, self.permission_classes)
        return [permission() for permission in classes]

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

    @action(detail=True, methods=['post'])
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

    @action(
        detail=True,
        methods=['post'],
    )
    def submit(self, request, pk=None):
        """Submit exercise for validation.

        Integrity rules (backend-enforced, never delegated to the client):
        - A repeated request carrying an already-processed ``submission_id``
          returns the original result without re-grading or re-awarding XP.
        - XP is computed server-side and awarded at most once per user and
          exercise, so repeated perfect scores cannot farm unlimited XP.
        - Configured ``max_attempts`` limits are enforced per exercise.
        """
        exercise = self.get_object()
        serializer = ExerciseSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        submission_id = serializer.validated_data.get('submission_id') or None

        # Idempotent replay: the same logical submission returns its own
        # stored result — no new attempt, no grading, no XP.
        if submission_id:
            existing = ExerciseAttempt.objects.filter(
                submission_id=submission_id
            ).first()
            if existing is not None:
                if existing.user_id != request.user.id:
                    return Response(
                        {'detail': 'This submission id belongs to another account.'},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                return Response({
                    'status': existing.status,
                    'feedback': existing.feedback,
                    'output': existing.output,
                    'error': existing.error_message,
                    'test_results': existing.test_results,
                    'xp_earned': 0,
                    'xp_total': existing.xp_earned,
                    'explain': exercise.explain,
                    'attempt_id': existing.id,
                    'duplicate': True,
                })

        code = serializer.validated_data.get('code', exercise.starter_code)
        selected_answer = serializer.validated_data.get('selected_answer')
        time_spent = serializer.validated_data.get('time_spent_seconds', 0)

        prior_count = ExerciseAttempt.objects.filter(
            user=request.user, exercise=exercise
        ).count()
        already_solved = ExerciseAttempt.objects.filter(
            user=request.user, exercise=exercise, status='correct'
        ).exists()
        if (exercise.max_attempts > 0 and prior_count >= exercise.max_attempts
                and not already_solved):
            return Response(
                {'detail': 'Attempt limit reached for this exercise.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            # Validate based on exercise type
            result = self._validate_exercise(exercise, code, selected_answer)

            # Create attempt
            attempt = ExerciseAttempt.objects.create(
                user=request.user,
                exercise=exercise,
                submission_id=submission_id,
                status=result['status'],
                submitted_code=code,
                selected_answer=selected_answer,
                output=result.get('output', ''),
                error_message=result.get('error', ''),
                feedback=result.get('feedback', ''),
                test_results=result.get('test_results', []),
                time_spent_seconds=time_spent,
                attempt_number=prior_count + 1,
            )

            # If correct, award XP and update progress; auto-enroll so progress
            # is never lost for learners who started reading before enrolling.
            xp_awarded = 0
            awarded = []
            if result['status'] == 'correct':
                Enrollment.objects.get_or_create(
                    user=request.user, course=exercise.lesson.chapter.course,
                    defaults={'status': 'active'},
                )
                xp_awarded = self._award_xp(request.user, exercise, attempt)
                self._update_lesson_progress(request.user, exercise.lesson)
                evaluate_course_completion(request.user, exercise.lesson.chapter.course)
                awarded = award_eligible_achievements(request.user, lesson=exercise.lesson)
            if exercise.is_final_assessment:
                record_learning_activity(
                    request.user, 'quiz_attempted', f'Attempted {exercise.title}',
                    course=exercise.lesson.chapter.course,
                    lesson=exercise.lesson, exercise=exercise,
                    status='passed' if result['status'] == 'correct' else 'needs_practice',
                )

        return Response({
            'status': result['status'],
            'feedback': result.get('feedback', ''),
            'output': result.get('output', ''),
            'error': result.get('error', ''),
            'test_results': result.get('test_results', []),
            'xp_earned': xp_awarded,
            'awarded_badges': _badge_announcements(awarded),
            'correct_answer': result.get('correct_answer'),
            'explain': result.get('explain', ''),
            'attempt_id': attempt.id,
            'duplicate': False,
        })

    @action(detail=True, methods=['get'])
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
            deduct_xp(
                request.user, next_hint.xp_penalty, 'hint_used', obj=next_hint,
                description=f'Hint used on {exercise.title}',
            )

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
        """Award XP for a correct exercise, at most once per user+exercise.

        The server computes the amount from the exercise configuration; any
        client-suggested value is ignored. A re-solve of an already-credited
        exercise earns nothing further (previous awards are returned so the
        client can display the total).
        """
        xp = exercise.xp_reward
        # Reduce XP if hints were used
        hints_penalty = sum(
            h.xp_penalty for h in exercise.hints.filter(order__lte=attempt.hints_used)
        )
        xp = max(10, xp - hints_penalty)  # minimum 10 XP

        created = award_xp(
            user, xp, 'exercise_complete', obj=exercise,
            description=f'Completed: {exercise.title}',
        )
        if created is None:
            # Already credited for this exercise — report the original award.
            prior = XPTransaction.objects.filter(
                user=user, action='exercise_complete',
                content_type=ContentType.objects.get_for_model(exercise),
                object_id=exercise.id,
            ).first()
            already = prior.amount if prior else 0
            attempt.xp_earned = already
            attempt.save(update_fields=['xp_earned'])
            return 0

        attempt.xp_earned = created.amount
        attempt.save(update_fields=['xp_earned'])
        return created.amount

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
    """List, retrieve, run and submit challenges."""
    queryset = Challenge.objects.filter(is_active=True)
    serializer_class = ChallengeSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'topic']
    ordering_fields = ['title', 'estimated_minutes']

    action_permissions = {
        'run': [permissions.IsAuthenticated],
        'submit': [permissions.IsAuthenticated, IsEmailVerified],
    }

    def get_permissions(self):
        classes = self.action_permissions.get(
            self.action, self.permission_classes
        )
        return [permission() for permission in classes]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ChallengeDetailSerializer
        return ChallengeSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user

        if user.is_authenticated:
            qs = qs.annotate(
                solved_count=Count(
                    'submissions',
                    filter=Q(
                        submissions__user=user,
                        submissions__status='correct',
                    ),
                    distinct=True,
                ),
                attempt_count=Count(
                    'submissions',
                    filter=Q(submissions__user=user),
                    distinct=True,
                ),
            )

        topic = self.request.query_params.get('topic')
        difficulty = self.request.query_params.get('difficulty')

        if topic:
            qs = qs.filter(topic__icontains=topic)

        if difficulty:
            qs = qs.filter(difficulty=difficulty)

        return qs

    @staticmethod
    def _test_dicts(test_results) -> list[dict]:
        return [
            {
                'test': tr.test_number,
                'status': tr.status,
                'message': tr.message,
                'expected': getattr(tr, 'expected', ''),
                'actual': getattr(tr, 'actual', ''),
            }
            for tr in test_results
        ]

    def _run_challenge_tests(self, challenge, code, language, tests):
        sandbox = get_sandbox()

        if isinstance(sandbox, DevelopmentSandbox):
            return None, [
                {
                    'test': i + 1,
                    'status': 'pending',
                    'message': (
                        'Automated evaluation is not available '
                        'on this server yet.'
                    ),
                    'expected': str(t.get('expected_output', '')),
                    'actual': '',
                }
                for i, t in enumerate(tests)
            ]

        results = sandbox.run_tests(
            code=code,
            language=language,
            test_cases=tests,
        )
        return sandbox, self._test_dicts(results)

    @action(detail=True, methods=['post'])
    def run(self, request, slug=None):
        challenge = self.get_object()
        serializer = ChallengeRunSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        language = serializer.validated_data.get('language', 'python')

        if language not in challenge.supported_languages():
            return Response(
                {'detail': f'{language} is not offered for this challenge.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        code = (
            serializer.validated_data.get('code')
            or challenge.starter_for(language)
        )

        if not code.strip():
            return Response({
                'status': 'error',
                'output': '',
                'error': 'No code to run.',
                'test_results': [],
                'runtime_ms': 0,
            })

        _, test_results = self._run_challenge_tests(
            challenge,
            code,
            language,
            challenge.sample_tests or challenge.hidden_tests,
        )

        passed = sum(
            1 for test in test_results
            if test['status'] == 'passed'
        )

        return Response({
            'status': 'success',
            'output': '',
            'error': '',
            'test_results': test_results,
            'summary': (
                f'{passed}/{len(test_results)} sample tests passed'
                if test_results else 'No sample tests defined.'
            ),
        })

    @action(detail=True, methods=['post'])
    def submit(self, request, slug=None):
        challenge = self.get_object()
        serializer = ChallengeSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        submission_id = (
            serializer.validated_data.get('submission_id') or None
        )

        # Idempotent replay: the ID must belong to this user AND challenge.
        if submission_id:
            existing = ChallengeSubmission.objects.filter(
                submission_id=submission_id
            ).first()

            if existing is not None:
                if existing.user_id != request.user.id:
                    return Response(
                        {
                            'detail': (
                                'This submission id belongs '
                                'to another account.'
                            )
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                if existing.challenge_id != challenge.id:
                    return Response(
                        {
                            'detail': (
                                'This submission id belongs '
                                'to another challenge.'
                            )
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                return Response(
                    self._submission_payload(
                        challenge,
                        existing,
                        replay=True,
                    )
                )

        language = serializer.validated_data.get('language', 'python')

        if language not in challenge.supported_languages():
            return Response(
                {'detail': f'{language} is not offered for this challenge.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        code = serializer.validated_data.get('code') or ''
        time_spent = serializer.validated_data.get(
            'time_spent_seconds', 0
        )

        if (
            not code.strip()
            or code.strip() == challenge.starter_for(language).strip()
        ):
            return Response({
                'status': 'incorrect',
                'feedback': (
                    "It looks like you haven't written a solution yet. "
                    'Implement the function and try again.'
                ),
                'test_results': [],
                'xp_earned': 0,
                'xp_total': challenge.xp_reward,
                'solved': challenge.submissions.filter(
                    user=request.user,
                    status='correct',
                ).exists(),
                'duplicate': False,
                'awarded_badges': [],
            })

        hidden = challenge.hidden_tests or challenge.sample_tests

        sandbox, test_results = self._run_challenge_tests(
            challenge,
            code,
            language,
            hidden,
        )

        if sandbox is None:
            verdict_status = 'running'
            all_passed = False
            feedback = (
                'Your submission was saved, but this server has no code '
                'evaluator connected yet, so we cannot confirm correctness.'
            )
        else:
            all_passed = bool(test_results) and all(
                test['status'] == 'passed'
                for test in test_results
            )

            verdict_status = 'correct' if all_passed else 'incorrect'

            if all_passed:
                count = len(test_results)
                feedback = (
                    f'All {count} test'
                    f'{"es" if count != 1 else ""} passed. Great work.'
                )
            else:
                failure = next(
                    (
                        test for test in test_results
                        if test['status'] != 'passed'
                    ),
                    None,
                )

                if failure is None:
                    feedback = (
                        'No runnable test cases are defined '
                        'for this challenge yet.'
                    )
                elif failure['status'] == 'error':
                    feedback = (
                        f'Your program raised an error on test '
                        f'{failure["test"]}: {failure["message"]}'
                    )
                else:
                    feedback = (
                        f'Test {failure["test"]} failed. '
                        f'Expected {failure["expected"]!r}, '
                        f'got {failure["actual"]!r}.'
                    )

        attempt_number = ChallengeSubmission.objects.filter(
            user=request.user,
            challenge=challenge,
        ).count() + 1

        xp_awarded = 0

        with transaction.atomic():
            submission = ChallengeSubmission.objects.create(
                user=request.user,
                challenge=challenge,
                submission_id=submission_id,
                language=language,
                status=verdict_status,
                submitted_code=code,
                feedback=feedback,
                test_results=test_results,
                time_spent_seconds=time_spent,
                attempt_number=attempt_number,
            )

            if all_passed:
                created = award_xp(
                    request.user,
                    challenge.xp_reward,
                    'challenge_complete',
                    obj=challenge,
                    description=(
                        f'Challenge completed: {challenge.title}'
                    ),
                )

                if created is not None:
                    xp_awarded = created.amount

                submission.xp_earned = xp_awarded
                submission.status = 'correct'
                submission.save(
                    update_fields=['xp_earned', 'status']
                )

        awarded = award_eligible_achievements(request.user)

        payload = self._submission_payload(
            challenge,
            submission,
            replay=False,
        )
        payload['feedback'] = feedback
        payload['test_results'] = test_results
        payload['xp_earned'] = xp_awarded
        payload['awarded_badges'] = _badge_announcements(awarded)

        return Response(payload)

    def _submission_payload(self, challenge, submission, *, replay):
        solved = ChallengeSubmission.objects.filter(
            user=submission.user,
            challenge=challenge,
            status='correct',
        ).exists()

        data = {
            'status': submission.status,
            'feedback': submission.feedback,
            'test_results': submission.test_results,
            'xp_earned': 0 if replay else submission.xp_earned,
            'xp_total': submission.xp_earned,
            'solved': solved,
            'attempt_id': submission.id,
            'duplicate': replay,
            'awarded_badges': [],
        }

        if solved:
            data['solution_explanation'] = (
                challenge.solution_explanation
            )
            data['time_complexity'] = challenge.time_complexity
            data['space_complexity'] = challenge.space_complexity
            data['reference_solution'] = challenge.solution_for(
                submission.language
            )

        return data



class PracticalClassViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PracticalClass.objects.filter(is_active=True, is_published=True)
    serializer_class = PracticalClassSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'


class PracticalSubjectViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PracticalSubjectSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'

    def get_queryset(self):
        qs = PracticalSubject.objects.filter(
            practical_class__is_active=True,
            practical_class__is_published=True,
            is_active=True,
        ).select_related('practical_class')
        class_slug = self.request.query_params.get('class')
        if class_slug:
            qs = qs.filter(practical_class__slug=class_slug)
        return qs


class PracticalViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'chapter_topic', 'subject__title']
    ordering_fields = ['title', 'practical_number', 'order']

    def get_serializer_class(self):
        return PracticalDetailSerializer if self.action == 'retrieve' else PracticalListSerializer

    def get_queryset(self):
        qs = Practical.objects.filter(
            practical_class__is_active=True,
            practical_class__is_published=True,
            subject__is_active=True,
            is_active=True,
            is_published=True,
        ).select_related('practical_class', 'subject')
        subject_slug = self.request.query_params.get('subject')
        class_slug = self.request.query_params.get('class')
        if subject_slug:
            qs = qs.filter(subject__slug=subject_slug)
        if class_slug:
            qs = qs.filter(practical_class__slug=class_slug)
        return qs

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[permissions.IsAuthenticated],
    )
    def complete(self, request, slug=None):
        practical = self.get_object()
        progress, _ = PracticalProgress.objects.get_or_create(
            user=request.user,
            practical=practical,
        )
        if request.method == 'DELETE':
            progress.completed_at = None
            progress.save(update_fields=['completed_at', 'updated_at'])
        else:
            if progress.completed_at is None:
                progress.completed_at = timezone.now()
                progress.save(update_fields=['completed_at', 'updated_at'])
            record_learning_activity(
                request.user, 'practical_completed',
                f'Completed {practical.title}', practical=practical,
            )
        return Response(PracticalProgressSerializer(progress).data)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[permissions.IsAuthenticated],
    )
    def bookmark(self, request, slug=None):
        practical = self.get_object()
        if request.method == 'DELETE':
            PracticalBookmark.objects.filter(
                user=request.user, practical=practical
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        bookmark, created = PracticalBookmark.objects.get_or_create(
            user=request.user,
            practical=practical,
        )
        record_learning_activity(
            request.user, 'bookmark_created',
            f'Bookmarked {practical.title}', practical=practical,
            status='saved',
        )
        return Response(
            PracticalBookmarkSerializer(bookmark).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class PracticalProgressViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PracticalProgressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return PracticalProgress.objects.filter(
            user=self.request.user
        ).select_related('practical')


class PracticalBookmarkViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PracticalBookmarkSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return PracticalBookmark.objects.filter(
            user=self.request.user
        ).select_related('practical')


class PracticalClassAdminViewSet(viewsets.ModelViewSet):
    queryset = PracticalClass.objects.all()
    serializer_class = PracticalClassAdminSerializer
    permission_classes = [IsAdministrator]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'slug', 'description']
    ordering_fields = ['title', 'order', 'is_active']


class PracticalSubjectAdminViewSet(viewsets.ModelViewSet):
    queryset = PracticalSubject.objects.select_related('practical_class').all()
    serializer_class = PracticalSubjectAdminSerializer
    permission_classes = [IsAdministrator]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'slug', 'description', 'practical_class__title']
    ordering_fields = ['title', 'order', 'is_active']

    def get_queryset(self):
        qs = super().get_queryset()
        practical_class = self.request.query_params.get('practical_class')
        if practical_class:
            qs = qs.filter(practical_class_id=practical_class)
        return qs


class PracticalAdminViewSet(viewsets.ModelViewSet):
    queryset = Practical.objects.select_related('practical_class', 'subject').all()
    serializer_class = PracticalAdminSerializer
    permission_classes = [IsAdministrator]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'slug', 'description', 'subject__title']
    ordering_fields = ['title', 'practical_number', 'order', 'is_published']

    def get_queryset(self):
        qs = super().get_queryset()
        practical_class = self.request.query_params.get('practical_class')
        subject = self.request.query_params.get('subject')
        if practical_class:
            qs = qs.filter(practical_class_id=practical_class)
        if subject:
            qs = qs.filter(subject_id=subject)
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
        enrollment = serializer.save(user=self.request.user)
        record_learning_activity(
            self.request.user, 'course_started',
            f'Started {enrollment.course.title}', course=enrollment.course,
        )


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


def resolve_badge(identifier: str) -> UserAchievement | None:
    if not identifier:
        return None
    return (
        UserAchievement.objects.filter(
            Q(public_id=identifier) | Q(credential_id__iexact=identifier)
        )
        .select_related('achievement', 'user')
        .first()
    )


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def verify_badge(request, identifier):
    """Public badge verification against the real earned-achievement row."""
    badge = resolve_badge(identifier)
    if not badge:
        return Response(
            {'valid': False, 'found': False, 'kind': 'badge',
             'detail': 'No badge matches this identifier.'},
            status=status.HTTP_404_NOT_FOUND,
        )
    achievement = badge.achievement
    from .badge_art import level_label, palette_for
    _, _, category_label = palette_for(achievement)
    return Response({
        'valid': badge.is_valid,
        'found': True,
        'kind': 'badge',
        'public_id': badge.public_id,
        'credential_id': badge.credential_id,
        'recipient_name': badge.recipient_name,
        'title': achievement.title,
        'description': achievement.description,
        'category': achievement.category,
        'category_label': category_label,
        'level_label': level_label(achievement),
        'skill_name': achievement.title,
        'issued_at': badge.earned_at.isoformat() if badge.earned_at else None,
        'issuer': 'Code Yaar Academy',
        'status': badge.status,
        'revoked': badge.status == UserAchievement.Status.REVOKED,
        'verification_url': badge.verification_url(),
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def download_badge(request, identifier):
    """Serve official badge SVG or PNG to the owner (or staff)."""
    badge = resolve_badge(identifier)
    if not badge:
        return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
    if not (request.user == badge.user or request.user.is_staff):
        return Response({'detail': 'Not allowed.'}, status=status.HTTP_403_FORBIDDEN)
    from .badge_art import render_badge_png, render_badge_svg
    fmt = (request.query_params.get('format') or 'png').lower()
    if fmt == 'svg':
        svg = render_badge_svg(badge)
        response = HttpResponse(svg, content_type='image/svg+xml')
        response['Content-Disposition'] = (
            f'attachment; filename="code-yaar-{badge.credential_id}.svg"'
        )
        return response
    buf = render_badge_png(badge)
    return FileResponse(
        buf, as_attachment=True,
        filename=f'code-yaar-{badge.credential_id}.png',
        content_type='image/png',
    )


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def public_badge_image(request, identifier):
    """Public PNG for Open Graph / verification pages. 404 if unknown."""
    badge = resolve_badge(identifier)
    if not badge or not badge.is_valid:
        return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
    from .badge_art import render_badge_png
    buf = render_badge_png(badge)
    return FileResponse(buf, content_type='image/png')


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def public_badge_share_image(request, identifier):
    """Public LinkedIn-ready achievement graphic (badge + branding + verify URL).

    ``?preset=square`` (default, 1200×1200) or ``?preset=wide`` (1200×627).
    Rendered from the real earned-achievement row; 404 if unknown/invalid.
    """
    badge = resolve_badge(identifier)
    if not badge or not badge.is_valid:
        return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
    from .badge_share_art import render_badge_share_png
    preset = (request.query_params.get('preset') or 'square').lower()
    if preset not in ('square', 'wide'):
        preset = 'square'
    buf = render_badge_share_png(badge, preset)
    return FileResponse(buf, content_type='image/png')


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


# ─── Student Progress Dashboard ────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def progress_dashboard_view(request):
    """Return server-derived analytics for the authenticated learner."""
    user = request.user
    today = timezone.localdate()
    streaks = streak_summary(user)
    enrollments = list(
        Enrollment.objects.filter(user=user)
        .select_related('course', 'course__track')
        .annotate(
            total_lessons=Count(
                'course__chapters__lessons',
                filter=Q(course__chapters__is_active=True,
                         course__chapters__lessons__is_active=True),
                distinct=True,
            ),
            completed_lessons=Count(
                'course__chapters__lessons__progress_entries',
                filter=Q(
                    course__chapters__is_active=True,
                    course__chapters__lessons__is_active=True,
                    course__chapters__lessons__progress_entries__user=user,
                    course__chapters__lessons__progress_entries__status__in=[
                        'completed', 'mastered'
                    ],
                ),
                distinct=True,
            ),
        )
    )
    courses = []
    for enrollment in enrollments:
        total = enrollment.total_lessons or 0
        completed = enrollment.completed_lessons or 0
        courses.append({
            'id': enrollment.course_id, 'slug': enrollment.course.slug,
            'title': enrollment.course.title, 'status': enrollment.status,
            'total_lessons': total, 'completed_lessons': completed,
            'remaining_lessons': max(total - completed, 0),
            'total_practicals': None, 'completed_practicals': None,
            'progress_percentage': round((completed / total) * 100) if total else 0,
            'last_accessed_at': enrollment.last_activity_at.isoformat()
                if enrollment.last_activity_at else None,
        })

    practical_qs = Practical.objects.filter(
        practical_class__is_active=True, practical_class__is_published=True,
        subject__is_active=True, is_active=True, is_published=True,
    )
    practical_total = practical_qs.count()
    practical_completed = PracticalProgress.objects.filter(
        user=user, completed_at__isnull=False, practical__in=practical_qs,
    ).count()
    assessments = ExerciseAttempt.objects.filter(
        user=user, exercise__is_final_assessment=True,
        exercise__is_active=True, exercise__lesson__is_active=True,
        exercise__lesson__chapter__is_active=True,
    )
    assessment_stats = assessments.aggregate(
        total=Count('id'),
        average=Avg(Case(
            When(status='correct', then=Value(100)),
            default=Value(0), output_field=IntegerField(),
        )),
        passed=Count('id', filter=Q(status='correct')),
    )

    all_activities = LearningActivity.objects.filter(
        user=user,
        activity_type__in=MEANINGFUL_ACTIVITY_TYPES,
    )
    activity_qs = all_activities
    if request.query_params.get('type'):
        activity_qs = activity_qs.filter(
            activity_type=request.query_params['type']
        )
    if request.query_params.get('from'):
        activity_qs = activity_qs.filter(
            activity_date__gte=request.query_params['from']
        )
    if request.query_params.get('to'):
        activity_qs = activity_qs.filter(
            activity_date__lte=request.query_params['to']
        )
    activities = []
    for activity in activity_qs.select_related(
        'course', 'lesson__chapter__course', 'practical__subject'
    )[:30]:
        associated_title = (
            activity.course.title if activity.course else
            activity.lesson.chapter.course.title if activity.lesson else
            activity.practical.subject.title if activity.practical else None
        )
        activities.append({
            'id': activity.id, 'type': activity.activity_type,
            'title': activity.title, 'status': activity.status,
            'associated_title': associated_title,
            'date': activity.occurred_at.isoformat(),
            'activity_date': activity.activity_date.isoformat(),
        })

    daily_counts = {
        row['activity_date']: row['count']
        for row in all_activities.filter(
            activity_date__gte=today - timedelta(days=6),
            activity_date__lte=today,
        ).values('activity_date').annotate(count=Count('id'))
    }
    weekly_activity = [{
        'date': (today - timedelta(days=offset)).isoformat(),
        'count': daily_counts.get(today - timedelta(days=offset), 0),
    } for offset in range(6, -1, -1)]

    contribution_start = today - timedelta(days=364)
    contribution_rows = all_activities.filter(
        activity_date__gte=contribution_start,
        activity_date__lte=today,
    ).values('activity_date', 'activity_type').annotate(count=Count('id'))
    contribution_counts = {}
    for row in contribution_rows:
        day = contribution_counts.setdefault(row['activity_date'], {
            'lessons_completed': 0,
            'practicals_completed': 0,
            'quizzes_completed': 0,
            'total_activities': 0,
        })
        count = row['count']
        if row['activity_type'] == 'lesson_completed':
            day['lessons_completed'] = count
        elif row['activity_type'] == 'practical_completed':
            day['practicals_completed'] = count
        elif row['activity_type'] == 'quiz_attempted':
            day['quizzes_completed'] = count
        day['total_activities'] += count

    contribution_data = []
    for offset in range(364, -1, -1):
        activity_date = today - timedelta(days=offset)
        day = contribution_counts.get(activity_date, {
            'lessons_completed': 0,
            'practicals_completed': 0,
            'quizzes_completed': 0,
            'total_activities': 0,
        })
        total = day['total_activities']
        intensity = 0 if not total else 1 if total == 1 else 2 if total == 2 else 3 if total <= 4 else 4
        contribution_data.append({
            'date': activity_date.isoformat(),
            **day,
            'intensity': intensity,
        })

    subjects = PracticalSubject.objects.filter(
        practical_class__is_active=True, practical_class__is_published=True,
        is_active=True,
    ).annotate(
        total=Count(
            'practicals',
            filter=Q(practicals__is_active=True, practicals__is_published=True),
            distinct=True,
        ),
        completed=Count(
            'practicals__progress_entries',
            filter=Q(
                practicals__is_active=True, practicals__is_published=True,
                practicals__progress_entries__user=user,
                practicals__progress_entries__completed_at__isnull=False,
            ),
            distinct=True,
        ),
    ).select_related('practical_class')
    subject_progress = [{
        'id': item.id, 'title': item.title,
        'class_title': item.practical_class.title,
        'total': item.total or 0, 'completed': item.completed or 0,
        'percentage': round((item.completed / item.total) * 100)
            if item.total else 0,
    } for item in subjects]

    classes = PracticalClass.objects.filter(
        is_active=True, is_published=True,
    ).annotate(
        total=Count(
            'practicals',
            filter=Q(
                practicals__is_active=True,
                practicals__is_published=True,
                practicals__subject__is_active=True,
            ),
            distinct=True,
        ),
        completed=Count(
            'practicals__progress_entries',
            filter=Q(
                practicals__is_active=True,
                practicals__is_published=True,
                practicals__subject__is_active=True,
                practicals__progress_entries__user=user,
                practicals__progress_entries__completed_at__isnull=False,
            ),
            distinct=True,
        ),
    )
    class_progress = [{
        'id': item.id,
        'title': item.title,
        'total': item.total or 0,
        'completed': item.completed or 0,
        'percentage': round((item.completed / item.total) * 100)
            if item.total else 0,
    } for item in classes]

    total_lessons = sum(item['total_lessons'] for item in courses)
    lessons_completed = sum(item['completed_lessons'] for item in courses)
    lesson_recent = all_activities.filter(
        activity_type='lesson_completed',
        activity_date__gte=today - timedelta(days=6),
    ).count()
    insights = [
        f'You completed {lesson_recent} lesson{"s" if lesson_recent != 1 else ""} this week.',
        f'You have {max(practical_total - practical_completed, 0)} practicals remaining.',
    ]
    if assessment_stats['total']:
        insights.append(
            f'Your assessment average is {round(assessment_stats["average"] or 0)}%.'
        )
    if not lesson_recent:
        insights.append('You have not completed a lesson recently.')

    return Response({
        'overview': {
            'overall_percentage': round((lessons_completed / total_lessons) * 100)
                if total_lessons else 0,
            'total_courses': len(courses),
            'completed_courses': sum(item['status'] == 'completed' for item in courses),
            'in_progress_courses': sum(item['status'] == 'active' for item in courses),
            'lessons_completed': lessons_completed, 'lessons_total': total_lessons,
            'practicals_completed': practical_completed,
            'practicals_total': practical_total,
            'quizzes_attempted': assessment_stats['total'] or 0,
            'average_quiz_score': round(assessment_stats['average'] or 0),
            'highest_quiz_score': 100 if assessment_stats['passed'] else 0,
            'learning_time_seconds': LessonProgress.objects.filter(user=user)
                .aggregate(total=Sum('time_spent_seconds'))['total'] or 0,
            'current_streak': streaks['current'], 'longest_streak': streaks['longest'],
        },
        'courses': courses, 'subjects': subject_progress,
        'classes': class_progress,
        'weekly_activity': weekly_activity,
        'quiz_performance': [
            {'date': item.created_at.date().isoformat(),
             'score': 100 if item.status == 'correct' else 0}
            for item in assessments.order_by('created_at')[:30]
        ],
        'active_dates': streaks['active_dates'],
        'contribution_data': contribution_data,
        'total_learning_activities': sum(
            item['total_activities'] for item in contribution_data
        ),
        'active_learning_days': sum(
            item['total_activities'] > 0 for item in contribution_data
        ),
        'activities': activities, 'insights': insights,
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
    all_achievements = Achievement.objects.filter(is_active=True)
    total_achievements = all_achievements.count()
    from .badge_art import level_label, palette_for
    from .services.achievements import measure_progress
    earned_records = {
        item.achievement_id: item
        for item in UserAchievement.objects.filter(
            user=user, achievement__is_active=True,
        )
    }
    achievements_data = []
    next_badge = None
    for achievement in all_achievements:
        record = earned_records.get(achievement.id)
        _, _, category_label = palette_for(achievement)
        current, target = measure_progress(user, achievement)
        achievements_data.append({
            'id': achievement.id,
            'slug': achievement.slug,
            'title': achievement.title,
            'description': achievement.description,
            'icon': achievement.icon,
            'category': achievement.category,
            'category_label': category_label,
            'difficulty': achievement.difficulty,
            'difficulty_label': achievement.get_difficulty_display(),
            'how_to_earn': achievement.how_to_earn,
            'level_label': level_label(achievement),
            'xp_bonus': achievement.xp_bonus,
            'earned': record is not None,
            'earned_at': record.earned_at.isoformat() if record else None,
            'public_id': record.public_id if record else None,
            'credential_id': record.credential_id if record else None,
            'recipient_name': record.recipient_name if record else None,
            'verification_url': record.verification_url() if record else None,
            'status': record.status if record else None,
            'progress': {
                'current': min(current, target),
                'target': target,
                'complete': current >= target,
            },
        })
        # Next achievable: the closest locked badge with any progress.
        if record is None and current > 0 and current < target:
            ratio = current / target if target else 0
            if next_badge is None or ratio > next_badge['_ratio']:
                next_badge = {
                    'slug': achievement.slug,
                    'title': achievement.title,
                    'description': achievement.description,
                    'how_to_earn': achievement.how_to_earn,
                    'difficulty': achievement.difficulty,
                    'difficulty_label': achievement.get_difficulty_display(),
                    'progress': {'current': current, 'target': target},
                    '_ratio': ratio,
                }
    if next_badge is not None:
        next_badge.pop('_ratio', None)

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
            'avatar': profile.avatar_url(),
            'bio': profile.bio,
            'location': profile.location,
            'role': profile.role,
            'website_url': profile.website_url,
            'xp_points': profile.xp_points,
            'streak_days': profile.streak_days,
            'longest_streak': profile.longest_streak,
            'level': profile.level,
            'is_profile_public': profile.is_profile_public,
            'show_badges': profile.show_badges,
            'show_activity': profile.show_activity,
            'show_courses': profile.show_courses,
            'notification_preferences': profile.notification_preferences,
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
        'achievements': achievements_data,
        'next_badge': next_badge,
        'skills': skills_data,
        'certifications': certs_data,
        'active_enrollments': active_enrollments_data,
    })


# ─── Avatar upload, notifications, preferences, public profile ────────────

AVATAR_MAX_PIXELS = 512


class AvatarUploadThrottle(ScopedRateThrottle):
    scope = 'avatar_upload'


def _encode_avatar(image_bytes, content_type):
    """Re-open, centre-crop to square, resize and re-encode to bounded JPEG.

    Re-encoding strips EXIF/metadata and any payload a malicious file could
    hide, and guarantees a real raster lands in storage. Pillow already
    validated the bytes are a decodable image in the serializer.
    """
    import io
    from PIL import Image, ImageOps

    img = Image.open(io.BytesIO(image_bytes))
    img = ImageOps.exif_transpose(img)
    img = img.convert('RGB')
    width, height = img.size
    side = min(width, height)
    left = (width - side) // 2
    top = (height - side) // 2
    img = img.crop((left, top, left + side, top + side))
    img.thumbnail((AVATAR_MAX_PIXELS, AVATAR_MAX_PIXELS), Image.LANCZOS)
    out = io.BytesIO()
    img.save(out, format='JPEG', quality=88, optimize=True)
    out.seek(0)
    return out.read(), 'image/jpeg'


@api_view(['POST', 'DELETE'])
@permission_classes([permissions.IsAuthenticated])
@throttle_classes([AvatarUploadThrottle])
def avatar_view(request):
    """Upload or remove the signed-in learner's profile picture."""
    from django.core.files.base import ContentFile

    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'DELETE':
        if profile.avatar:
            profile.avatar.delete(save=False)
        profile.avatar = ''
        profile.save(update_fields=['avatar'])
        return Response({'avatar': '', 'detail': 'Profile picture removed.'})

    serializer = AvatarUploadSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    upload = serializer.validated_data['file']
    raw = upload.read()
    try:
        data, _ = _encode_avatar(raw, upload.content_type)
    except Exception:
        return Response(
            {'file': ['The image could not be processed. Try another file.']},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if profile.avatar:
        profile.avatar.delete(save=False)
    filename = f"avatar_{request.user.pk}.jpg"
    profile.avatar.save(filename, ContentFile(data), save=True)
    return Response({'avatar': profile.avatar_url()})


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def notifications_view(request):
    """List the learner's notifications, newest first, with an unread count."""
    qs = UserNotification.objects.filter(user=request.user)
    unread = qs.filter(read_at__isnull=True).count()
    page = self_paginate(request, qs)
    data = UserNotificationSerializer(page.object_list, many=True).data
    return Response({
        'results': data,
        'unread_count': unread,
        'next': page.has_next(),
        'previous': page.has_previous(),
    })


def self_paginate(request, queryset, default_size=20):
    """Small manual paginator reusing the project's PAGE_SIZE convention."""
    from django.core.paginator import Paginator

    try:
        size = int(request.query_params.get('page_size') or default_size)
    except ValueError:
        size = default_size
    size = max(1, min(size, 100))
    paginator = Paginator(queryset, size)
    try:
        page_number = int(request.query_params.get('page') or 1)
    except ValueError:
        page_number = 1
    return paginator.get_page(page_number)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def notification_read_view(request, pk):
    notification = get_object_or_404(
        UserNotification, pk=pk, user=request.user,
    )
    if notification.read_at is None:
        notification.read_at = timezone.now()
        notification.save(update_fields=['read_at'])
    return Response({'id': notification.id, 'unread': False})


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def notifications_read_all_view(request):
    updated = UserNotification.objects.filter(
        user=request.user, read_at__isnull=True,
    ).update(read_at=timezone.now())
    return Response({'marked_read': updated})


@api_view(['PATCH'])
@permission_classes([permissions.IsAuthenticated])
def notification_preferences_view(request):
    """Persist account-level notification toggles on the profile."""
    serializer = NotificationPreferenceSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    prefs = dict(profile.notification_preferences or {})
    prefs.update(serializer.validated_data)
    profile.notification_preferences = prefs
    profile.save(update_fields=['notification_preferences'])
    return Response({'notification_preferences': prefs})


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def account_deletion_request_view(request):
    """Record a deletion request for admin follow-up; never deletes in-line."""
    from .models import AuthenticationAuditLog

    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if profile.deletion_requested_at is None:
        profile.deletion_requested_at = timezone.now()
        profile.save(update_fields=['deletion_requested_at'])
    AuthenticationAuditLog.objects.create(
        user=request.user,
        event='profile_updated',
        identifier=request.user.username,
        metadata={'deletion_requested': True},
    )
    return Response({
        'detail': 'Your deletion request was recorded. Our team reviews these '
                  'requests; your account and data stay intact until then.',
        'requested_at': profile.deletion_requested_at.isoformat(),
    })


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def public_profile_view(request, username):
    """Shareable public profile, honoring the owner's privacy choices.

    Never exposes email or any sensitive account field. Unknown users and
    profiles the owner made private both resolve to a 404 so a probe cannot
    distinguish 'does not exist' from 'hidden by choice'.
    """
    from django.contrib.auth import get_user_model

    User = get_user_model()
    user = User.objects.filter(username__iexact=username).select_related('profile').first()
    profile = getattr(user, 'profile', None) if user else None
    if user is None or profile is None or not profile.is_profile_public:
        return Response({'detail': 'Profile not found.'}, status=status.HTTP_404_NOT_FOUND)

    completed_courses = Enrollment.objects.filter(
        user=user, status='completed',
    ).select_related('course', 'course__track')
    tracks_completed = []
    if profile.show_courses:
        seen = set()
        for enrollment in completed_courses:
            track = enrollment.course.track
            if track.pk not in seen:
                seen.add(track.pk)
                tracks_completed.append({'slug': track.slug, 'title': track.title})

    badges_data = []
    if profile.show_badges:
        earned = UserAchievement.objects.filter(
            user=user, status='active', achievement__is_active=True,
        ).select_related('achievement')
        for ua in earned:
            badges_data.append({
                'slug': ua.achievement.slug,
                'title': ua.achievement.title,
                'description': ua.achievement.description,
                'icon': ua.achievement.icon,
                'category': ua.achievement.category,
                'difficulty': ua.achievement.difficulty,
                'earned_at': ua.earned_at.isoformat(),
                'verification_url': ua.verification_url(),
            })

    activity = []
    if profile.show_activity:
        recent = XPTransaction.objects.filter(user=user).order_by('-created_at')[:8]
        activity = [{
            'amount': t.amount,
            'action': t.action,
            'description': t.description,
            'created_at': t.created_at.isoformat(),
        } for t in recent if t.description]

    return Response({
        'username': user.username,
        'display_name': profile.full_name,
        'avatar': profile.avatar_url(),
        'bio': profile.bio,
        'location': profile.location,
        'joined_at': user.date_joined.isoformat(),
        'github_url': profile.github_url,
        'linkedin_url': profile.linkedin_url,
        'website_url': profile.website_url,
        'stats': {
            'level': profile.level,
            'xp_points': profile.xp_points,
            'streak_days': profile.streak_days,
            'longest_streak': profile.longest_streak,
            'courses_completed': completed_courses.count(),
            'badges_earned': len(badges_data),
        },
        'show_badges': profile.show_badges,
        'show_courses': profile.show_courses,
        'show_activity': profile.show_activity,
        'badges': badges_data,
        'tracks_completed': tracks_completed,
        'recent_activity': activity,
    })
