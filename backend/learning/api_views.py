from rest_framework import serializers, viewsets, permissions, status, filters
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import F, Sum, Count, Q
from django.http import FileResponse, HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone

from .models import (
    UserProfile, CareerTrack, Course, Chapter, Lesson, Exercise, Hint,
    Resource, Project, Challenge, Enrollment, SnippetRun,
    LessonProgress, ExerciseAttempt, XPTransaction, Achievement,
    UserAchievement, Progress, Certification, UserCertification,
    Skill, UserSkill,
    PracticalClass, PracticalSubject, Practical, PracticalProgress,
    PracticalBookmark,
)
from .services.sandbox import get_sandbox
from .services.xp import award_xp, deduct_xp
from .services.achievements import award_eligible_achievements
from .services.completion import evaluate_course_completion
from .permissions import IsEmailVerified, IsAdministrator
from .serializers import (
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

        # Re-evaluate strict, server-side course completion now that lesson
        # state may have changed.
        evaluate_course_completion(user, lesson.chapter.course)
        award_eligible_achievements(user, lesson=lesson)

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
            if result['status'] == 'correct':
                Enrollment.objects.get_or_create(
                    user=request.user, course=exercise.lesson.chapter.course,
                    defaults={'status': 'active'},
                )
                xp_awarded = self._award_xp(request.user, exercise, attempt)
                self._update_lesson_progress(request.user, exercise.lesson)
                evaluate_course_completion(request.user, exercise.lesson.chapter.course)
                award_eligible_achievements(request.user, lesson=exercise.lesson)

        return Response({
            'status': result['status'],
            'feedback': result.get('feedback', ''),
            'output': result.get('output', ''),
            'error': result.get('error', ''),
            'test_results': result.get('test_results', []),
            'xp_earned': xp_awarded,
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
    earned_records = {
        item.achievement_id: item
        for item in UserAchievement.objects.filter(
            user=user, achievement__is_active=True,
        )
    }
    achievements_data = []
    for achievement in all_achievements:
        record = earned_records.get(achievement.id)
        _, _, category_label = palette_for(achievement)
        achievements_data.append({
            'id': achievement.id,
            'slug': achievement.slug,
            'title': achievement.title,
            'description': achievement.description,
            'icon': achievement.icon,
            'category': achievement.category,
            'category_label': category_label,
            'level_label': level_label(achievement),
            'xp_bonus': achievement.xp_bonus,
            'earned': record is not None,
            'earned_at': record.earned_at.isoformat() if record else None,
            'public_id': record.public_id if record else None,
            'credential_id': record.credential_id if record else None,
            'recipient_name': record.recipient_name if record else None,
            'verification_url': record.verification_url() if record else None,
            'status': record.status if record else None,
        })

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
        'achievements': achievements_data,
        'skills': skills_data,
        'certifications': certs_data,
        'active_enrollments': active_enrollments_data,
    })
