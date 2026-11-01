from rest_framework import serializers

from .models import (
    CareerTrack, Course, Chapter, Lesson, Exercise, Hint,
    Resource, Project, ProjectMilestone, Challenge, Enrollment,
    LessonProgress, ExerciseAttempt, XPTransaction, Achievement,
    UserAchievement, Progress, Certification, UserCertification,
    Skill, UserSkill, PracticalClass, PracticalSubject, Practical,
    PracticalProgress, PracticalBookmark,
)


# ─── Content Serializers ────────────────────────────────────────────────────
# Authentication serializers live in `learning.auth_serializers`.


class PracticalClassSerializer(serializers.ModelSerializer):
    subject_count = serializers.SerializerMethodField()

    class Meta:
        model = PracticalClass
        fields = ['id', 'slug', 'title', 'board', 'description', 'order', 'subject_count']

    def get_subject_count(self, obj):
        return obj.subjects.filter(is_active=True).count()


class PracticalSubjectSerializer(serializers.ModelSerializer):
    practical_count = serializers.SerializerMethodField()
    class_title = serializers.CharField(source='practical_class.title', read_only=True)
    class_slug = serializers.CharField(source='practical_class.slug', read_only=True)

    class Meta:
        model = PracticalSubject
        fields = [
            'id', 'slug', 'title', 'description', 'order', 'class_title',
            'class_slug', 'practical_count',
        ]

    def get_practical_count(self, obj):
        return obj.practicals.filter(is_active=True, is_published=True).count()


class PracticalListSerializer(serializers.ModelSerializer):
    subject_title = serializers.CharField(source='subject.title', read_only=True)
    class_title = serializers.CharField(source='practical_class.title', read_only=True)
    is_completed = serializers.SerializerMethodField()
    is_bookmarked = serializers.SerializerMethodField()

    class Meta:
        model = Practical
        fields = [
            'id', 'slug', 'title', 'description', 'practical_number', 'chapter_topic',
            'subject_title', 'class_title', 'order', 'is_completed',
            'is_bookmarked',
        ]

    def _user(self):
        request = self.context.get('request')
        return request.user if request and request.user.is_authenticated else None

    def get_is_completed(self, obj):
        user = self._user()
        return bool(user and obj.progress_entries.filter(
            user=user, completed_at__isnull=False
        ).exists())

    def get_is_bookmarked(self, obj):
        user = self._user()
        return bool(user and obj.bookmarks.filter(user=user).exists())


class PracticalDetailSerializer(PracticalListSerializer):
    class Meta(PracticalListSerializer.Meta):
        fields = PracticalListSerializer.Meta.fields + [
            'aim', 'apparatus', 'theory', 'procedure', 'observations',
            'calculations', 'result', 'precautions', 'diagrams',
        ]


class PracticalProgressSerializer(serializers.ModelSerializer):
    practical_slug = serializers.CharField(source='practical.slug', read_only=True)

    class Meta:
        model = PracticalProgress
        fields = ['id', 'practical', 'practical_slug', 'completed_at', 'updated_at']
        read_only_fields = ['id', 'completed_at', 'updated_at']


class PracticalBookmarkSerializer(serializers.ModelSerializer):
    practical_slug = serializers.CharField(source='practical.slug', read_only=True)

    class Meta:
        model = PracticalBookmark
        fields = ['id', 'practical', 'practical_slug', 'created_at']
        read_only_fields = ['id', 'created_at']


class HintSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hint
        fields = ['id', 'content', 'order', 'reveals_solution', 'xp_penalty']


class ExerciseListSerializer(serializers.ModelSerializer):
    """Lightweight exercise info for lesson view."""
    hint_count = serializers.SerializerMethodField()

    class Meta:
        model = Exercise
        fields = [
            'id', 'title', 'slug', 'exercise_type', 'difficulty',
            'language', 'xp_reward', 'order', 'hint_count',
        ]

    def get_hint_count(self, obj):
        return obj.hints.count()


class ExerciseDetailSerializer(serializers.ModelSerializer):
    """Full exercise with instructions, starter code, and hints.

    Security: correct-answer flags and test expectations are never sent to
    the client. Grading happens server-side; the explanation is only
    returned by the submit endpoint once the learner has attempted it.
    """
    hints = HintSerializer(many=True, read_only=True)
    lesson_title = serializers.CharField(source='lesson.title', read_only=True)
    chapter_title = serializers.CharField(source='lesson.chapter.title', read_only=True)
    choices = serializers.SerializerMethodField()
    expected_output = serializers.SerializerMethodField()

    class Meta:
        model = Exercise
        fields = [
            'id', 'title', 'slug', 'exercise_type', 'difficulty', 'language',
            'lesson_title', 'chapter_title',
            'instructions', 'context', 'constraints', 'expected_behavior',
            'starter_code', 'expected_output',
            'choices',
            'xp_reward', 'max_attempts', 'order',
            'hints',
        ]

    def get_choices(self, obj):
        return [
            {'id': c.get('id'), 'text': c.get('text')}
            for c in (obj.choices or [])
        ]

    def get_expected_output(self, obj):
        # For output-prediction items the expected output IS the answer, so
        # it must never reach the client. For code exercises it is the spec
        # the learner is asked to satisfy and stays visible.
        if obj.exercise_type == 'output_prediction':
            return ''
        return obj.expected_output


class LessonListSerializer(serializers.ModelSerializer):
    """Lightweight lesson info for sidebar."""
    exercise_count = serializers.SerializerMethodField()
    progress_status = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = [
            'id', 'title', 'slug', 'content_type', 'order',
            'duration_minutes', 'xp_reward', 'exercise_count', 'progress_status',
        ]

    def get_exercise_count(self, obj):
        return obj.exercises.filter(is_active=True).count()

    def get_progress_status(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            progress = LessonProgress.objects.filter(
                user=request.user, lesson=obj
            ).first()
            if progress:
                return progress.status
        return 'not_started'


class LessonDetailSerializer(serializers.ModelSerializer):
    """Full lesson with content and exercises."""
    exercises = serializers.SerializerMethodField()
    chapter_title = serializers.CharField(source='chapter.title', read_only=True)
    course_title = serializers.CharField(source='chapter.course.title', read_only=True)
    course_slug = serializers.CharField(source='chapter.course.slug', read_only=True)
    exercise_count = serializers.SerializerMethodField()
    progress_status = serializers.SerializerMethodField()
    prev_lesson = serializers.SerializerMethodField()
    next_lesson = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = [
            'id', 'title', 'slug', 'content_type', 'chapter_title', 'course_title',
            'course_slug',
            'learning_objective', 'content_body', 'video_url', 'video_duration_seconds',
            'order', 'duration_minutes', 'xp_reward', 'is_free_preview',
            'exercise_count', 'progress_status', 'prev_lesson', 'next_lesson',
            'exercises',
        ]

    def get_exercise_count(self, obj):
        return obj.exercises.filter(is_active=True).count()

    def get_exercises(self, obj):
        exercises = obj.exercises.filter(is_active=True)
        return ExerciseListSerializer(exercises, many=True, context=self.context).data

    def get_progress_status(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            progress = LessonProgress.objects.filter(
                user=request.user, lesson=obj
            ).first()
            if progress:
                return progress.status
        return 'not_started'

    def _sibling(self, obj, direction):
        """Previous/next lesson across the whole course, by content order."""
        qs = Lesson.objects.filter(
            chapter__course=obj.chapter.course,
            chapter__is_active=True,
            is_active=True,
        ).order_by('chapter__order', 'order')
        if direction == 'prev':
            return qs.filter(chapter__order=obj.chapter.order).filter(order__lt=obj.order).last() \
                or qs.filter(chapter__order__lt=obj.chapter.order).last()
        return qs.filter(chapter__order=obj.chapter.order).filter(order__gt=obj.order).first() \
            or qs.filter(chapter__order__gt=obj.chapter.order).order_by('chapter__order', 'order').first()

    def get_prev_lesson(self, obj):
        lesson = self._sibling(obj, 'prev')
        return {'slug': lesson.slug, 'title': lesson.title} if lesson else None

    def get_next_lesson(self, obj):
        lesson = self._sibling(obj, 'next')
        return {'slug': lesson.slug, 'title': lesson.title} if lesson else None


class ChapterListSerializer(serializers.ModelSerializer):
    """
    Lightweight chapter for the course sidebar.

    Only published content is nested: retired chapters/lessons stay in the
    database so learner progress survives re-seeding, but they must never
    appear in the course map a learner navigates.
    """
    lessons = serializers.SerializerMethodField()
    progress_percentage = serializers.SerializerMethodField()
    is_final_assessment = serializers.SerializerMethodField()

    class Meta:
        model = Chapter
        fields = [
            'id', 'title', 'slug', 'order', 'xp_reward',
            'lessons', 'progress_percentage', 'is_final_assessment',
        ]

    def get_lessons(self, obj):
        lessons = obj.lessons.filter(is_active=True)
        return LessonListSerializer(lessons, many=True, context=self.context).data

    def get_is_final_assessment(self, obj):
        return Exercise.objects.filter(
            lesson__chapter=obj,
            lesson__is_active=True,
            is_final_assessment=True,
            is_active=True,
        ).exists()

    def get_progress_percentage(self, obj):
        lessons = obj.lessons.filter(is_active=True)
        total = lessons.count()
        if total == 0:
            return 0
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            completed = LessonProgress.objects.filter(
                user=request.user,
                lesson__in=lessons,
                status__in=['completed', 'mastered']
            ).count()
            return round((completed / total) * 100)
        return 0


class ChapterDetailSerializer(serializers.ModelSerializer):
    """Full chapter with lesson details."""
    lessons = serializers.SerializerMethodField()
    exercise_count = serializers.SerializerMethodField()

    class Meta:
        model = Chapter
        fields = [
            'id', 'title', 'slug', 'description', 'order', 'xp_reward',
            'lessons', 'exercise_count',
        ]

    def get_lessons(self, obj):
        lessons = obj.lessons.filter(is_active=True)
        return LessonDetailSerializer(lessons, many=True, context=self.context).data

    def get_exercise_count(self, obj):
        return Exercise.objects.filter(
            lesson__chapter=obj, lesson__is_active=True, is_active=True
        ).count()


class ResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resource
        fields = ['id', 'title', 'description', 'resource_type', 'file_url', 'file_name', 'file_size_bytes', 'order']


class CourseListSerializer(serializers.ModelSerializer):
    track_title = serializers.CharField(source='track.title', read_only=True)
    chapter_count = serializers.IntegerField(read_only=True, default=0)
    lesson_count = serializers.SerializerMethodField()
    exercise_count = serializers.SerializerMethodField()
    enrolled = serializers.SerializerMethodField()
    estimated_hours = serializers.IntegerField(read_only=True)
    total_xp = serializers.IntegerField(read_only=True)

    class Meta:
        model = Course
        fields = [
            'id', 'slug', 'title', 'subtitle', 'description', 'thumbnail',
            'track', 'track_title', 'difficulty', 'language',
            'estimated_hours', 'total_xp', 'chapter_count', 'lesson_count',
            'exercise_count', 'is_free', 'enrolled',
        ]

    def get_lesson_count(self, obj):
        return obj.lesson_count

    def get_exercise_count(self, obj):
        return obj.exercise_count

    def get_enrolled(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            return Enrollment.objects.filter(user=request.user, course=obj).exists()
        return False


class CourseDetailSerializer(serializers.ModelSerializer):
    """Full course with published chapters, resources, and enrollment info."""
    chapters = serializers.SerializerMethodField()
    resources = ResourceSerializer(many=True, read_only=True)
    track_title = serializers.CharField(source='track.title', read_only=True)
    lesson_count = serializers.SerializerMethodField()
    exercise_count = serializers.SerializerMethodField()
    enrolled = serializers.SerializerMethodField()
    enrollment_id = serializers.SerializerMethodField()
    resume_lesson = serializers.SerializerMethodField()
    progress_percentage = serializers.SerializerMethodField()
    estimated_hours = serializers.IntegerField(read_only=True)
    total_xp = serializers.IntegerField(read_only=True)

    class Meta:
        model = Course
        fields = [
            'id', 'slug', 'title', 'subtitle', 'description', 'thumbnail',
            'track', 'track_title', 'difficulty', 'language',
            'estimated_hours', 'total_xp', 'instructor', 'prerequisites',
            'learning_objectives', 'is_free',
            'chapters', 'resources', 'lesson_count', 'exercise_count',
            'enrolled', 'enrollment_id', 'resume_lesson', 'progress_percentage',
        ]

    def get_chapters(self, obj):
        # Sorted by content order so chapters follow the intended path and
        # the final assessment always comes last.
        chapters = obj.chapters.filter(is_active=True).order_by('order', 'id')
        return ChapterListSerializer(chapters, many=True, context=self.context).data

    def get_lesson_count(self, obj):
        return obj.lesson_count

    def get_exercise_count(self, obj):
        return obj.exercise_count

    def get_enrolled(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            return Enrollment.objects.filter(user=request.user, course=obj).exists()
        return False

    def get_enrollment_id(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            enrollment = Enrollment.objects.filter(user=request.user, course=obj).first()
            return enrollment.id if enrollment else None
        return None

    def get_resume_lesson(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            enrollment = Enrollment.objects.filter(user=request.user, course=obj).first()
            if enrollment and enrollment.last_lesson:
                return LessonListSerializer(enrollment.last_lesson, context=self.context).data
            # Find first incomplete lesson
            first_incomplete = Lesson.objects.filter(
                chapter__course=obj, chapter__is_active=True, is_active=True
            ).exclude(
                id__in=LessonProgress.objects.filter(
                    user=request.user, status__in=['completed', 'mastered']
                ).values_list('lesson_id', flat=True)
            ).order_by('chapter__order', 'order').first()
            if first_incomplete:
                return LessonListSerializer(first_incomplete, context=self.context).data
        return None

    def get_progress_percentage(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            total = Lesson.objects.filter(chapter__course=obj).count()
            if total == 0:
                return 0
            completed = LessonProgress.objects.filter(
                user=request.user,
                lesson__chapter__course=obj,
                status__in=['completed', 'mastered']
            ).count()
            return round((completed / total) * 100)
        return 0


class CareerTrackSerializer(serializers.ModelSerializer):
    courses = CourseListSerializer(many=True, read_only=True)
    course_count = serializers.SerializerMethodField()

    class Meta:
        model = CareerTrack
        fields = [
            'id', 'slug', 'title', 'description', 'icon',
            'difficulty', 'estimated_hours', 'courses', 'course_count',
        ]

    def get_course_count(self, obj):
        return obj.courses.filter(is_active=True).count()


class CareerTrackListSerializer(serializers.ModelSerializer):
    course_count = serializers.SerializerMethodField()

    class Meta:
        model = CareerTrack
        fields = [
            'id', 'slug', 'title', 'description', 'icon',
            'difficulty', 'estimated_hours', 'course_count',
        ]

    def get_course_count(self, obj):
        return obj.courses.filter(is_active=True).count()


class ProjectMilestoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectMilestone
        fields = ['id', 'title', 'description', 'order']


class ProjectSerializer(serializers.ModelSerializer):
    track_title = serializers.CharField(source='track.title', read_only=True, default=None)
    milestones = ProjectMilestoneSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = [
            'id', 'slug', 'title', 'description', 'thumbnail',
            'difficulty', 'technologies', 'estimated_hours',
            'track', 'track_title', 'milestones',
        ]


class ChallengeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Challenge
        fields = [
            'id', 'slug', 'title', 'description',
            'difficulty', 'topic', 'estimated_minutes', 'xp_reward',
            'starter_code',
        ]


# ─── Progress Serializers ───────────────────────────────────────────────────

class EnrollmentSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True)
    track_title = serializers.CharField(source='course.track.title', read_only=True)
    progress_percentage = serializers.IntegerField(read_only=True)
    course_slug = serializers.CharField(source='course.slug', read_only=True)

    class Meta:
        model = Enrollment
        fields = [
            'id', 'course', 'course_slug', 'course_title', 'track_title',
            'enrolled_at', 'completed_at', 'last_activity_at',
            'status', 'progress_percentage',
        ]
        read_only_fields = ['enrolled_at', 'completed_at', 'last_activity_at']


class LessonProgressSerializer(serializers.ModelSerializer):
    lesson_title = serializers.CharField(source='lesson.title', read_only=True)
    chapter_title = serializers.CharField(source='lesson.chapter.title', read_only=True)

    class Meta:
        model = LessonProgress
        fields = [
            'id', 'lesson', 'lesson_title', 'chapter_title',
            'status', 'time_spent_seconds', 'video_watched_seconds',
            'completed_at', 'updated_at',
        ]
        # Completion status and its timestamp are derived by the server from
        # real evidence (solved exercises / graded assessments). A learner can
        # track time but must never self-grant a completion via the API.
        read_only_fields = ['status', 'completed_at', 'updated_at', 'lesson']


class ProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Progress
        fields = [
            'id', 'content_type', 'object_id', 'status', 'score',
            'time_spent_minutes', 'completed_at', 'updated_at',
        ]
        read_only_fields = ['updated_at']


class ExerciseAttemptSerializer(serializers.ModelSerializer):
    exercise_title = serializers.CharField(source='exercise.title', read_only=True)

    class Meta:
        model = ExerciseAttempt
        fields = [
            'id', 'exercise', 'exercise_title', 'status',
            'submitted_code', 'selected_answer', 'output', 'error_message',
            'feedback', 'test_results', 'hints_used',
            'time_spent_seconds', 'xp_earned', 'attempt_number', 'created_at',
        ]
        read_only_fields = ['created_at']


class XPTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = XPTransaction
        fields = ['id', 'amount', 'action', 'description', 'created_at']
        read_only_fields = ['created_at']


class AchievementSerializer(serializers.ModelSerializer):
    earned = serializers.SerializerMethodField()
    level_label = serializers.SerializerMethodField()
    category_label = serializers.SerializerMethodField()

    class Meta:
        model = Achievement
        fields = [
            'id', 'slug', 'title', 'description', 'icon', 'category',
            'category_label', 'xp_bonus', 'earned', 'level_label',
        ]

    def get_earned(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            return UserAchievement.objects.filter(user=request.user, achievement=obj).exists()
        return False

    def get_level_label(self, obj):
        from .badge_art import level_label
        return level_label(obj)

    def get_category_label(self, obj):
        return obj.get_category_display()


class UserAchievementSerializer(serializers.ModelSerializer):
    achievement = AchievementSerializer(read_only=True)
    verification_url = serializers.SerializerMethodField()
    is_valid = serializers.BooleanField(read_only=True)

    class Meta:
        model = UserAchievement
        fields = [
            'id', 'achievement', 'earned_at', 'public_id', 'credential_id',
            'recipient_name', 'status', 'is_valid', 'verification_url',
        ]
        read_only_fields = ['earned_at', 'public_id', 'credential_id']

    def get_verification_url(self, obj):
        return obj.verification_url()


# ─── Certification Serializers ──────────────────────────────────────────────

class CertificationSerializer(serializers.ModelSerializer):
    track_title = serializers.CharField(source='track.title', read_only=True)

    class Meta:
        model = Certification
        fields = [
            'id', 'title', 'description', 'badge_icon',
            'passing_score', 'track', 'track_title',
        ]


class UserCertificationSerializer(serializers.ModelSerializer):
    certification = CertificationSerializer(read_only=True)

    class Meta:
        model = UserCertification
        fields = ['id', 'certification', 'earned_at', 'credential_id']
        read_only_fields = ['earned_at', 'credential_id']


# ─── Skill Serializers ──────────────────────────────────────────────────────

class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['id', 'name', 'category', 'icon']


class UserSkillSerializer(serializers.ModelSerializer):
    skill = SkillSerializer(read_only=True)

    class Meta:
        model = UserSkill
        fields = ['id', 'skill', 'proficiency', 'updated_at']
        read_only_fields = ['updated_at']


# ─── Exercise Submission Serializers ────────────────────────────────────────

class ExerciseRunSerializer(serializers.Serializer):
    """For running code without validation."""
    code = serializers.CharField(required=False, allow_blank=True)
    selected_answer = serializers.JSONField(required=False, allow_null=True)


class ExerciseSubmitSerializer(serializers.Serializer):
    """For submitting exercise for validation."""
    code = serializers.CharField(required=False, allow_blank=True)
    selected_answer = serializers.JSONField(required=False, allow_null=True)
    time_spent_seconds = serializers.IntegerField(required=False, default=0)
    # Optional client-generated idempotency key. A replayed Submit (double
    # click / retried request) reuses it so the server can return the original
    # result instead of re-grading or re-awarding. Never trusted for XP amount.
    submission_id = serializers.CharField(
        required=False, allow_blank=True, max_length=64,
        help_text='Unique per logical submission; replays resolve to the same result',
    )
    # NOTE: any client-suggested 'xp_earned' / 'xp' is deliberately ignored —
    # the backend is the only authority on XP.
