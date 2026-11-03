from rest_framework import serializers

from .models import (
    CareerTrack, Course, Chapter, Lesson, Exercise, Hint,
    Resource, Project, ProjectMilestone, Challenge, Enrollment,
    LessonProgress, ExerciseAttempt, XPTransaction, Achievement,
    UserAchievement, Progress, Certification, UserCertification,
    Skill, UserSkill, PracticalClass, PracticalSubject, Practical,
    PracticalProgress, PracticalBookmark, UserNotification,
    UserProfile, Portfolio, StudentProject, ProjectImage,
    Competition, CompetitionRegistration, CompetitionTeam,
    CompetitionSubmission, CompetitionResult,
)


# ─── Content Serializers ────────────────────────────────────────────────────
# Authentication serializers live in `learning.auth_serializers`.


class CompetitionListSerializer(serializers.ModelSerializer):
    status = serializers.CharField(read_only=True)
    organizer_name = serializers.CharField(source='organizer.get_full_name', read_only=True)
    participant_count = serializers.IntegerField(read_only=True)
    registration_status = serializers.SerializerMethodField()

    class Meta:
        model = Competition
        fields = [
            'id', 'slug', 'title', 'short_description', 'banner', 'category',
            'difficulty', 'format', 'delivery_mode', 'registration_deadline',
            'competition_start', 'competition_end', 'participant_limit',
            'participant_count', 'prize_information', 'status', 'organizer_name',
            'registration_status',
        ]

    def get_registration_status(self, obj):
        user = self.context.get('request').user
        if not user.is_authenticated:
            return None
        return obj.registrations.filter(user=user).values_list(
            'registration_status', flat=True
        ).first()


class CompetitionDetailSerializer(CompetitionListSerializer):
    class Meta(CompetitionListSerializer.Meta):
        fields = CompetitionListSerializer.Meta.fields + [
            'description', 'location', 'registration_start', 'submission_deadline',
            'judging_end', 'results_announcement', 'minimum_team_size',
            'maximum_team_size', 'eligibility_rules', 'competition_rules',
            'problem_statement', 'submission_configuration',
        ]


class CompetitionRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompetitionRegistration
        fields = ['id', 'team', 'registration_status', 'registration_data', 'rules_accepted_at', 'registered_at']
        read_only_fields = ['id', 'registration_status', 'registered_at']


class CompetitionSubmissionSerializer(serializers.ModelSerializer):
    competition_slug = serializers.CharField(source='registration.competition.slug', read_only=True)

    class Meta:
        model = CompetitionSubmission
        fields = [
            'id', 'competition_slug', 'project_title', 'description', 'github_url',
            'demo_url', 'additional_data', 'status', 'organizer_feedback',
            'submitted_at', 'updated_at',
        ]
        read_only_fields = ['id', 'competition_slug', 'status', 'organizer_feedback', 'submitted_at', 'updated_at']


class CompetitionResultSerializer(serializers.ModelSerializer):
    participant_name = serializers.SerializerMethodField()
    project_title = serializers.CharField(source='registration.submission.project_title', read_only=True)

    class Meta:
        model = CompetitionResult
        fields = ['rank', 'participant_name', 'project_title', 'final_score', 'award']

    def get_participant_name(self, obj):
        if obj.registration.team_id:
            return obj.registration.team.name
        profile = getattr(obj.registration.user, 'profile', None)
        return profile.full_name if profile else obj.registration.user.username


class PracticalClassSerializer(serializers.ModelSerializer):
    subject_count = serializers.SerializerMethodField()

    class Meta:
        model = PracticalClass
        fields = ['id', 'slug', 'title', 'board', 'thumbnail', 'description', 'order', 'subject_count']

    def get_subject_count(self, obj):
        return obj.subjects.filter(is_active=True).count()


class PracticalSubjectSerializer(serializers.ModelSerializer):
    practical_count = serializers.SerializerMethodField()
    class_title = serializers.CharField(source='practical_class.title', read_only=True)
    class_slug = serializers.CharField(source='practical_class.slug', read_only=True)

    class Meta:
        model = PracticalSubject
        fields = [
            'id', 'slug', 'title', 'image', 'description', 'order', 'class_title',
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


class PracticalClassAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = PracticalClass
        fields = [
            'id', 'slug', 'title', 'board', 'thumbnail', 'description',
            'order', 'is_published', 'is_active',
        ]

    def validate_board(self, value):
        if value != 'stb':
            raise serializers.ValidationError('Only STB practical classes are currently supported.')
        return value

    def validate_slug(self, value):
        if value not in {'class-9', 'class-10', 'class-11', 'class-12'}:
            raise serializers.ValidationError('Class must be 9, 10, 11, or 12.')
        return value

    def validate_title(self, value):
        if value.strip().lower() not in {'class 9', 'class 10', 'class 11', 'class 12'}:
            raise serializers.ValidationError('Class must be 9, 10, 11, or 12.')
        return value.strip()


class PracticalSubjectAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = PracticalSubject
        fields = ['id', 'practical_class', 'slug', 'title', 'image', 'description', 'order', 'is_active']

    def validate_title(self, value):
        if not value.strip():
            raise serializers.ValidationError('Subject name is required.')
        return value.strip()


class PracticalAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Practical
        fields = [
            'id', 'practical_class', 'subject', 'slug', 'title', 'description',
            'practical_number', 'chapter_topic', 'aim', 'apparatus', 'theory',
            'procedure', 'observations', 'calculations', 'result', 'precautions',
            'diagrams', 'order', 'is_published', 'is_active',
        ]

    def validate(self, attrs):
        practical_class = attrs.get('practical_class', getattr(self.instance, 'practical_class', None))
        subject = attrs.get('subject', getattr(self.instance, 'subject', None))
        if practical_class and subject and subject.practical_class_id != practical_class.id:
            raise serializers.ValidationError({
                'subject': 'The subject must belong to the selected class.',
            })
        diagrams = attrs.get('diagrams', getattr(self.instance, 'diagrams', []))
        if not isinstance(diagrams, list):
            raise serializers.ValidationError({'diagrams': 'Provide a list of image objects.'})
        for diagram in diagrams:
            if not isinstance(diagram, dict) or not isinstance(diagram.get('url'), str):
                raise serializers.ValidationError({
                    'diagrams': 'Each diagram must include an image URL.',
                })
        return attrs


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


def _media_url(request, file_field):
    """Absolute URL for an uploaded file, or None when unset."""
    if not file_field:
        return None
    url = file_field.url
    if request is not None:
        return request.build_absolute_uri(url)
    return url


class TextbookReferenceMixin:
    """
    Exposes the curriculum source citation (board, class, textbook unit, the
    topic name as printed, page numbers, plus the verification state) so the
    UI can always tell a learner which part of the textbook a piece of content
    came from — and flag anything that is supplementary rather than official.

    Returns None for content that isn't textbook-derived, so the general
    course catalogue renders unchanged.

    Concrete serializers must still declare
    `textbook_reference = serializers.SerializerMethodField()` themselves:
    DRF only collects declared fields from `Serializer` subclasses, so a field
    defined on a plain mixin is invisible to `ModelSerializer`.
    """

    def get_textbook_reference(self, obj):
        if not obj.source_type:
            return None
        return {
            'source_type': obj.source_type,
            'verification_status': obj.verification_status,
            'board': obj.textbook_board,
            'class': obj.textbook_class,
            'unit': obj.textbook_unit,
            'topic': obj.textbook_topic,
            'pages': obj.textbook_pages,
            'label': obj.textbook_reference_label,
        }


class HintSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hint
        fields = ['id', 'content', 'order', 'reveals_solution', 'xp_penalty']


class ExerciseListSerializer(TextbookReferenceMixin, serializers.ModelSerializer):
    """Lightweight exercise info for lesson view."""
    hint_count = serializers.SerializerMethodField()
    textbook_reference = serializers.SerializerMethodField()

    class Meta:
        model = Exercise
        fields = [
            'id', 'title', 'slug', 'exercise_type', 'difficulty',
            'language', 'xp_reward', 'order', 'hint_count',
            'textbook_reference',
        ]

    def get_hint_count(self, obj):
        return obj.hints.count()


class ExerciseDetailSerializer(TextbookReferenceMixin, serializers.ModelSerializer):
    """Full exercise with instructions, starter code, and hints.

    Security: correct-answer flags and test expectations are never sent to
    the client. Grading happens server-side; the explanation is only
    returned by the submit endpoint once the learner has attempted it.
    """
    hints = HintSerializer(many=True, read_only=True)
    textbook_reference = serializers.SerializerMethodField()
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
            'hints', 'textbook_reference',
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


class LessonDetailSerializer(TextbookReferenceMixin, serializers.ModelSerializer):
    """Full lesson with content and exercises."""
    exercises = serializers.SerializerMethodField()
    textbook_reference = serializers.SerializerMethodField()
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
            'exercises', 'textbook_reference',
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


class ChapterListSerializer(TextbookReferenceMixin, serializers.ModelSerializer):
    """
    Lightweight chapter for the course sidebar.

    Only published content is nested: retired chapters/lessons stay in the
    database so learner progress survives re-seeding, but they must never
    appear in the course map a learner navigates.
    """
    lessons = serializers.SerializerMethodField()
    textbook_reference = serializers.SerializerMethodField()
    progress_percentage = serializers.SerializerMethodField()
    is_final_assessment = serializers.SerializerMethodField()

    class Meta:
        model = Chapter
        fields = [
            'id', 'title', 'slug', 'order', 'xp_reward',
            'lessons', 'progress_percentage', 'is_final_assessment',
            'textbook_reference',
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
    progress_percentage = serializers.SerializerMethodField()
    estimated_hours = serializers.IntegerField(read_only=True)
    total_xp = serializers.IntegerField(read_only=True)

    class Meta:
        model = Course
        fields = [
            'id', 'slug', 'title', 'subtitle', 'description', 'thumbnail',
            'track', 'track_title', 'academic_class', 'difficulty', 'language',
            'estimated_hours', 'total_xp', 'chapter_count', 'lesson_count',
            'exercise_count', 'is_free', 'enrolled', 'progress_percentage',
        ]

    def get_lesson_count(self, obj):
        return obj.lesson_count

    def get_exercise_count(self, obj):
        return obj.exercise_count

    def _user(self, request):
        return getattr(getattr(request, 'user', None), 'is_authenticated', False) and request.user

    def get_enrolled(self, obj):
        user = self._user(self.context.get('request'))
        if user:
            return Enrollment.objects.filter(user=user, course=obj).exists()
        return False

    def get_progress_percentage(self, obj):
        """Lessons completed by the requester, same rule as the course
        detail endpoint (progress_percentage on CourseDetailSerializer)."""
        user = self._user(self.context.get('request'))
        if not user:
            return 0
        cache = self.context.setdefault('_course_progress_cache', {})
        if obj.id not in cache:
            total = Lesson.objects.filter(
                chapter__course=obj, chapter__is_active=True, is_active=True
            ).count()
            if total == 0:
                cache[obj.id] = 0
            else:
                completed = LessonProgress.objects.filter(
                    user=user,
                    lesson__chapter__course=obj,
                    lesson__is_active=True,
                    status__in=['completed', 'mastered'],
                ).count()
                cache[obj.id] = round((completed / total) * 100)
        return cache[obj.id]


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
    """Track detail: sequenced courses plus the requester's track progress.

    Progress is derived only from real rows (lessons completed, enrollments)
    — nothing is stored or fabricated on the track itself.
    """
    courses = serializers.SerializerMethodField()
    course_count = serializers.SerializerMethodField()
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    cover_url = serializers.SerializerMethodField()
    enrolled_course_count = serializers.SerializerMethodField()
    completed_course_count = serializers.SerializerMethodField()
    progress_percentage = serializers.SerializerMethodField()
    continue_url_slug = serializers.SerializerMethodField()
    total_xp = serializers.SerializerMethodField()

    class Meta:
        model = CareerTrack
        fields = [
            'id', 'slug', 'title', 'description', 'icon', 'category',
            'category_display', 'cover_url', 'learning_objectives',
            'difficulty', 'estimated_hours', 'courses', 'course_count',
            'total_xp', 'enrolled_course_count', 'completed_course_count',
            'progress_percentage', 'continue_url_slug',
        ]

    def get_courses(self, obj):
        # Only count/open what a learner can actually see: published courses
        # in the admin-curated recommended sequence.
        return CourseListSerializer(
            obj.published_courses, many=True, context=self.context
        ).data

    def get_course_count(self, obj):
        # Only count what a learner can actually open — unpublished draft
        # courses (e.g. Class XI/XII shells) must not inflate the number.
        return obj.courses.filter(is_active=True, is_published=True).count()

    def get_total_xp(self, obj):
        return sum(c.total_xp for c in obj.published_courses)

    def get_cover_url(self, obj):
        return _media_url(self.context.get('request'), obj.cover_image)

    def _progress_rows(self, obj):
        """(lessons_total, lessons_completed, courses, enrollments_by_course)
        for the requesting user; shared by the progress fields."""
        request = self.context.get('request')
        user = getattr(getattr(request, 'user', None), 'is_authenticated', False) and request.user
        courses = list(obj.published_courses)
        lessons_total = 0
        lessons_completed = 0
        enrollments = {}
        if courses:
            lessons_total = Lesson.objects.filter(
                chapter__course__in=courses, chapter__is_active=True, is_active=True
            ).count()
            if user:
                lessons_completed = LessonProgress.objects.filter(
                    user=user,
                    lesson__chapter__course__in=courses,
                    lesson__is_active=True,
                    status__in=['completed', 'mastered'],
                ).count()
                enrollments = {
                    e.course_id: e
                    for e in Enrollment.objects.filter(user=user, course__in=courses)
                }
        return lessons_total, lessons_completed, courses, enrollments

    def get_enrolled_course_count(self, obj):
        _, _, _, enrollments = self._progress_rows(obj)
        return len(enrollments)

    def get_completed_course_count(self, obj):
        _, _, _, enrollments = self._progress_rows(obj)
        return sum(1 for e in enrollments.values() if e.status == 'completed')

    def get_progress_percentage(self, obj):
        total, completed, _, _ = self._progress_rows(obj)
        return round((completed / total) * 100) if total else 0

    def get_continue_url_slug(self, obj):
        """Course the learner should resume: furthest in progress among
        enrolled-but-unfinished courses; None when nothing is underway."""
        request = self.context.get('request')
        user = getattr(getattr(request, 'user', None), 'is_authenticated', False) and request.user
        if not user:
            return None
        best_slug, best_progress = None, -1.0
        for course in obj.published_courses:
            enrollment = course.enrollments.filter(user=user).first()
            if enrollment is None or enrollment.status in ('completed', 'dropped'):
                continue
            total = Lesson.objects.filter(
                chapter__course=course, chapter__is_active=True, is_active=True
            ).count()
            if total == 0:
                progress = 0.0
            else:
                done = LessonProgress.objects.filter(
                    user=user, lesson__chapter__course=course,
                    lesson__is_active=True,
                    status__in=['completed', 'mastered'],
                ).count()
                progress = done / total
            if progress > best_progress:
                best_progress, best_slug = progress, course.slug
        return best_slug


class CareerTrackListSerializer(serializers.ModelSerializer):
    course_count = serializers.SerializerMethodField()
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    cover_url = serializers.SerializerMethodField()
    total_xp = serializers.SerializerMethodField()
    enrolled = serializers.SerializerMethodField()
    progress_percentage = serializers.SerializerMethodField()

    class Meta:
        model = CareerTrack
        fields = [
            'id', 'slug', 'title', 'description', 'icon', 'category',
            'category_display', 'cover_url', 'learning_objectives',
            'difficulty', 'estimated_hours', 'course_count', 'total_xp',
            'enrolled', 'progress_percentage',
        ]

    def get_course_count(self, obj):
        # Matches the course list endpoint, which only serves published courses.
        return obj.courses.filter(is_active=True, is_published=True).count()

    def get_total_xp(self, obj):
        cache = self.context.setdefault('_track_xp_cache', {})
        if obj.id not in cache:
            cache[obj.id] = sum(
                c.total_xp for c in obj.courses.filter(is_active=True, is_published=True)
            )
        return cache[obj.id]

    def get_cover_url(self, obj):
        return _media_url(self.context.get('request'), obj.cover_image)

    def _user_state(self, obj):
        request = self.context.get('request')
        user = getattr(getattr(request, 'user', None), 'is_authenticated', False) and request.user
        cache = self.context.setdefault('_track_enroll_cache', {})
        if not user:
            return None
        if obj.id not in cache:
            courses = list(obj.courses.filter(is_active=True, is_published=True))
            enrollments = list(
                Enrollment.objects.filter(user=user, course__in=courses)
            ) if courses else []
            total = Lesson.objects.filter(
                chapter__course__in=courses, chapter__is_active=True, is_active=True
            ).count() if courses else 0
            completed = LessonProgress.objects.filter(
                user=user,
                lesson__chapter__course__in=courses,
                lesson__is_active=True,
                status__in=['completed', 'mastered'],
            ).count() if courses else 0
            cache[obj.id] = {
                'enrolled': bool(enrollments),
                'progress': round((completed / total) * 100) if total else 0,
            }
        return cache[obj.id]

    def get_enrolled(self, obj):
        state = self._user_state(obj)
        return bool(state and state['enrolled'])

    def get_progress_percentage(self, obj):
        state = self._user_state(obj)
        return state['progress'] if state else 0


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
    """Card/list projection. Adds per-user ``solved`` and ``attempts``."""
    solved = serializers.SerializerMethodField()
    attempts = serializers.SerializerMethodField()

    class Meta:
        model = Challenge
        fields = [
            'id', 'slug', 'title', 'description',
            'difficulty', 'topic', 'estimated_minutes', 'xp_reward',
            'starter_code', 'solved', 'attempts',
        ]

    def get_solved(self, obj) -> bool:
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        if user is None or not user.is_authenticated:
            return False
        # The viewset annotates `solved_count` to keep this O(1) per row.
        annotated = getattr(obj, 'solved_count', None)
        if annotated is not None:
            return annotated > 0
        return obj.submissions.filter(user=user, status='correct').exists()

    def get_attempts(self, obj) -> int:
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        if user is None or not user.is_authenticated:
            return 0
        annotated = getattr(obj, 'attempt_count', None)
        if annotated is not None:
            return annotated
        return obj.submissions.filter(user=user).count()


class ChallengeDetailSerializer(serializers.ModelSerializer):
    """Full workspace content.

    Deliberately omits ``solution_code*`` and ``hidden_tests``: correctness is
    graded server-side, and the reference answers are only revealed after a
    learner solves the challenge (returned by the submit endpoint).
    """
    solved = serializers.SerializerMethodField()
    attempts = serializers.SerializerMethodField()

    class Meta:
        model = Challenge
        fields = [
            'id', 'slug', 'title', 'description', 'difficulty', 'topic',
            'estimated_minutes', 'xp_reward', 'languages',
            'starter_code', 'starter_code_cpp',
            'problem_statement', 'requirements', 'input_description',
            'output_description', 'constraints', 'examples', 'hints',
            'time_complexity', 'space_complexity',
            'sample_tests', 'solved', 'attempts',
        ]

    def get_solved(self, obj) -> bool:
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        if user is None or not user.is_authenticated:
            return False
        return obj.submissions.filter(user=user, status='correct').exists()

    def get_attempts(self, obj) -> int:
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        if user is None or not user.is_authenticated:
            return 0
        return obj.submissions.filter(user=user).count()


class ChallengeRunSerializer(serializers.Serializer):
    """Runs sample tests without awarding XP."""
    code = serializers.CharField(required=False, allow_blank=True)
    language = serializers.ChoiceField(choices=['python', 'cpp'], default='python')


class ChallengeSubmitSerializer(serializers.Serializer):
    """Submits hidden tests for grading and a one-time XP award."""
    code = serializers.CharField(required=False, allow_blank=True)
    language = serializers.ChoiceField(choices=['python', 'cpp'], default='python')
    submission_id = serializers.UUIDField(required=False, allow_null=True)
    time_spent_seconds = serializers.IntegerField(required=False, min_value=0, default=0)


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
    difficulty_label = serializers.SerializerMethodField()
    earned_at = serializers.SerializerMethodField()
    progress = serializers.SerializerMethodField()

    class Meta:
        model = Achievement
        fields = [
            'id', 'slug', 'title', 'description', 'icon', 'category',
            'category_label', 'difficulty', 'difficulty_label', 'how_to_earn',
            'xp_bonus', 'earned', 'earned_at', 'level_label', 'progress',
        ]
        read_only_fields = fields

    def _user_achievement(self, obj):
        """The requester's earned row for this badge, cached per request."""
        request = self.context.get('request')
        if not (request and hasattr(request, 'user') and request.user.is_authenticated):
            return None
        cache = self._earned_cache()
        if obj.pk not in cache:
            from .models import UserAchievement
            cache[obj.pk] = UserAchievement.objects.filter(
                user=request.user, achievement=obj,
            ).first()
        return cache[obj.pk]

    def _earned_cache(self):
        if not hasattr(self, '_earned_cache_map'):
            self._earned_cache_map = {}
        return self._earned_cache_map

    def get_earned(self, obj):
        row = self._user_achievement(obj)
        return bool(row and row.status == 'active')

    def get_earned_at(self, obj):
        row = self._user_achievement(obj)
        return row.earned_at.isoformat() if row else None

    def get_progress(self, obj):
        """Server-derived (current, target); hidden detail once earned."""
        request = self.context.get('request')
        if not (request and hasattr(request, 'user') and request.user.is_authenticated):
            return None
        from .services.achievements import measure_progress
        current, target = measure_progress(request.user, obj)
        return {
            'current': min(current, target),
            'target': target,
            'complete': current >= target,
        }

    def get_level_label(self, obj):
        from .badge_art import level_label
        return level_label(obj)

    def get_category_label(self, obj):
        return obj.get_category_display()

    def get_difficulty_label(self, obj):
        return obj.get_difficulty_display()


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


class UserNotificationSerializer(serializers.ModelSerializer):
    unread = serializers.SerializerMethodField()

    class Meta:
        model = UserNotification
        fields = [
            'id', 'type', 'category', 'title', 'body', 'link', 'unread',
            'created_at',
        ]
        read_only_fields = fields

    def get_unread(self, obj):
        return obj.read_at is None


class NotificationPreferenceSerializer(serializers.Serializer):
    """Validates the fixed set of account-level notification preferences.

    In-app toggles gate the notifications stored for the user; the ``email_*``
    toggles gate the transactional mail sent alongside them. Security email
    (verification, resets, password changes) intentionally has no key — it is
    never optional. ``email_digest`` folds in-app notifications the user has
    not already been emailed individually into a daily or weekly email.
    """

    achievements = serializers.BooleanField(required=False)
    learning_reminders = serializers.BooleanField(required=False)
    streak_reminders = serializers.BooleanField(required=False)
    community = serializers.BooleanField(required=False)
    announcements = serializers.BooleanField(required=False)
    competitions = serializers.BooleanField(required=False)

    email_learning = serializers.BooleanField(required=False)
    email_competitions = serializers.BooleanField(required=False)
    email_achievements = serializers.BooleanField(required=False)
    email_certificates = serializers.BooleanField(required=False)
    email_announcements = serializers.BooleanField(required=False)

    email_digest = serializers.ChoiceField(
        choices=['none', 'daily', 'weekly'],
        required=False,
    )


class AvatarUploadSerializer(serializers.Serializer):
    """Multipart avatar upload with content-aware image validation.

    The file is opened by Pillow (not just trusted by extension/MIME) and
    re-encoded server-side, so a malicious or corrupt payload never reaches
    storage. Size and format are enforced here; pixels are re-written to a
    bounded JPEG/PNG in the view.
    """

    MAX_BYTES = 5 * 1024 * 1024
    ALLOWED_FORMATS = {'JPEG', 'PNG', 'WEBP'}
    ALLOWED_CONTENT_TYPES = {'image/jpeg', 'image/jpg', 'image/png', 'image/webp'}

    file = serializers.FileField()

    def validate_file(self, value):
        from PIL import Image, UnidentifiedImageError

        if value.size > self.MAX_BYTES:
            raise serializers.ValidationError('Image must be 5 MB or smaller.')
        if getattr(value, 'content_type', '') and \
                value.content_type.lower() not in self.ALLOWED_CONTENT_TYPES:
            raise serializers.ValidationError('Upload a JPEG, PNG, or WebP image.')
        try:
            value.seek(0)
            with Image.open(value) as img:
                img.verify()
                fmt = (img.format or '').upper()
        except (UnidentifiedImageError, OSError, ValueError):
            raise serializers.ValidationError('That file is not a valid image.')
        finally:
            value.seek(0)
        if fmt not in self.ALLOWED_FORMATS:
            raise serializers.ValidationError('Upload a JPEG, PNG, or WebP image.')
        return value


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


# ─── Portfolio Serializers ─────────────────────────────────────────────────

MAX_PROJECT_IMAGE_BYTES = 5 * 1024 * 1024  # 5 MB
ALLOWED_PROJECT_IMAGE_TYPES = {'image/jpeg', 'image/png', 'image/webp'}
MAX_FEATURED_PROJECTS = 3


def _validate_project_image(image, field_name):
    """Enforce type + size on an uploaded project image."""
    if image is None:
        return image
    content_type = getattr(image, 'content_type', None)
    if content_type and content_type not in ALLOWED_PROJECT_IMAGE_TYPES:
        raise serializers.ValidationError({
            field_name: 'Unsupported image type. Use JPEG, PNG or WebP.'
        })
    size = getattr(image, 'size', None)
    if size is not None and size > MAX_PROJECT_IMAGE_BYTES:
        raise serializers.ValidationError({
            field_name: 'Image is too large. Maximum size is 5 MB.'
        })
    return image


class ProjectImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = ProjectImage
        fields = ['id', 'image', 'image_url', 'alt_text', 'display_order', 'created_at']
        read_only_fields = ['created_at', 'image_url']

    def get_image_url(self, obj):
        request = self.context.get('request')
        if not obj.image:
            return ''
        url = obj.image.url
        if request is not None and url.startswith('/'):
            return request.build_absolute_uri(url)
        return url

    def validate_image(self, value):
        return _validate_project_image(value, 'image')


class StudentProjectSerializer(serializers.ModelSerializer):
    """Owner-facing read/write serializer for a portfolio project."""
    images = ProjectImageSerializer(many=True, read_only=True)
    category_label = serializers.CharField(source='get_category_display', read_only=True)
    status_label = serializers.CharField(source='get_status_display', read_only=True)
    cover_image_url = serializers.SerializerMethodField()

    class Meta:
        model = StudentProject
        fields = [
            'id', 'title', 'slug', 'short_description', 'overview',
            'category', 'category_label', 'status', 'status_label',
            'cover_image', 'cover_image_url', 'github_url', 'live_demo_url', 'docs_url',
            'problem_statement', 'solution', 'technical_details',
            'challenges', 'lessons_learned', 'contributions',
            'technologies', 'start_date', 'completion_date',
            'featured', 'display_order', 'visibility',
            'images', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at', 'display_order']

    def get_cover_image_url(self, obj):
        request = self.context.get('request')
        if not obj.cover_image:
            return ''
        url = obj.cover_image.url
        if request is not None and url.startswith('/'):
            return request.build_absolute_uri(url)
        return url

    def validate_cover_image(self, value):
        return _validate_project_image(value, 'cover_image')

    def validate_technologies(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError('Technologies must be a list.')
        cleaned = [str(v).strip() for v in value if str(v).strip()]
        return cleaned[:40]

    def _unique_slug(self, title, instance=None):
        from django.utils.text import slugify
        base = slugify(title) or 'project'
        qs = StudentProject.objects.filter(user=self.context['request'].user)
        if instance is not None:
            qs = qs.exclude(pk=instance.pk)
        slug = base
        counter = 2
        while qs.filter(slug=slug).exists():
            slug = f'{base}-{counter}'
            counter += 1
        return slug

    def validate(self, attrs):
        title = attrs.get('title') or (self.instance.title if self.instance else '')
        if self.instance is None:
            attrs['slug'] = self._unique_slug(title)
        elif 'title' in attrs and attrs['title'] != self.instance.title:
            attrs['slug'] = self._unique_slug(attrs['title'], self.instance)

        # Enforce the featured cap without double-counting the edited row.
        if attrs.get('featured'):
            user = self.context['request'].user
            featured_qs = StudentProject.objects.filter(user=user, featured=True)
            if self.instance is not None:
                featured_qs = featured_qs.exclude(pk=self.instance.pk)
            if featured_qs.count() >= MAX_FEATURED_PROJECTS:
                raise serializers.ValidationError({
                    'featured': f'You can feature at most {MAX_FEATURED_PROJECTS} projects.'
                })
        return attrs


class StudentProjectPublicSerializer(serializers.ModelSerializer):
    """Safe projection served through public endpoints (owner-filtered)."""
    images = ProjectImageSerializer(many=True, read_only=True)
    category_label = serializers.CharField(source='get_category_display', read_only=True)
    status_label = serializers.CharField(source='get_status_display', read_only=True)
    cover_image_url = serializers.SerializerMethodField()

    class Meta:
        model = StudentProject
        fields = [
            'id', 'title', 'slug', 'short_description', 'overview',
            'category', 'category_label', 'status', 'status_label',
            'cover_image_url', 'github_url', 'live_demo_url', 'docs_url',
            'problem_statement', 'solution', 'technical_details',
            'challenges', 'lessons_learned', 'contributions',
            'technologies', 'start_date', 'completion_date',
            'featured', 'images',
        ]

    def get_cover_image_url(self, obj):
        request = self.context.get('request')
        if not obj.cover_image:
            return ''
        url = obj.cover_image.url
        if request is not None and url.startswith('/'):
            return request.build_absolute_uri(url)
        return url


class ProjectReorderSerializer(serializers.Serializer):
    """Validated list of {id, display_order} belonging to the requesting user."""
    items = serializers.ListField(
        child=serializers.DictField(child=serializers.IntegerField()),
        allow_empty=False,
    )

    def validate_items(self, value):
        user = self.context['request'].user
        ids = [int(item['id']) for item in value]
        owned = set(
            StudentProject.objects.filter(user=user, id__in=ids).values_list('id', flat=True)
        )
        missing = [i for i in ids if i not in owned]
        if missing:
            raise serializers.ValidationError(
                f'Unknown project ids for this user: {missing}'
            )
        return value


class PortfolioSerializer(serializers.ModelSerializer):
    """Owner-facing portfolio settings + identity pulled from ``UserProfile``."""
    full_name = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()
    avatar_url = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()
    github_url = serializers.SerializerMethodField()
    linkedin_url = serializers.SerializerMethodField()
    website_url = serializers.SerializerMethodField()

    class Meta:
        model = Portfolio
        fields = [
            'id', 'headline', 'about', 'interests', 'currently_learning',
            'enjoys_building', 'is_published', 'show_skills', 'show_achievements',
            'show_learning_progress', 'show_social_links', 'show_location',
            'show_contact', 'created_at', 'updated_at',
            'full_name', 'username', 'avatar_url', 'location',
            'github_url', 'linkedin_url', 'website_url',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def _profile(self, obj):
        return getattr(obj.user, 'profile', None)

    def get_full_name(self, obj):
        return obj.user.get_full_name().strip() or obj.user.username

    def get_username(self, obj):
        return obj.user.username

    def get_avatar_url(self, obj):
        profile = self._profile(obj)
        return profile.avatar_url() if profile else ''

    def get_location(self, obj):
        profile = self._profile(obj)
        return profile.location if profile else ''

    def get_github_url(self, obj):
        profile = self._profile(obj)
        return profile.github_url if profile else ''

    def get_linkedin_url(self, obj):
        profile = self._profile(obj)
        return profile.linkedin_url if profile else ''

    def get_website_url(self, obj):
        profile = self._profile(obj)
        return profile.website_url if profile else ''


class PublicPortfolioSerializer(serializers.ModelSerializer):
    """Privacy-filtered public portfolio payload.

    The view only reaches this serializer once the owner has published the
    portfolio and keeps their account public, so it never needs to decide
    whether the whole page is visible. Each section is still independently
    gated by the owner's toggles, and skills/achievements/journey are derived
    from real platform records - nothing here is fabricated or auto-written.
    """
    display_name = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()
    social_links = serializers.SerializerMethodField()
    contact_enabled = serializers.SerializerMethodField()
    about = serializers.SerializerMethodField()
    projects = serializers.SerializerMethodField()
    skills = serializers.SerializerMethodField()
    achievements = serializers.SerializerMethodField()
    learning_journey = serializers.SerializerMethodField()

    class Meta:
        model = Portfolio
        fields = [
            'username', 'display_name', 'avatar', 'headline', 'location',
            'social_links', 'contact_enabled', 'about', 'projects', 'skills',
            'achievements', 'learning_journey',
        ]

    def _profile(self, obj):
        return getattr(obj.user, 'profile', None)

    def get_display_name(self, obj):
        return obj.user.get_full_name().strip() or obj.user.username

    def get_username(self, obj):
        return obj.user.username

    def get_avatar(self, obj):
        profile = self._profile(obj)
        return profile.avatar_url() if profile else ''

    def get_location(self, obj):
        profile = self._profile(obj)
        if self.show_location and profile:
            return profile.location
        return ''

    @property
    def show_location(self):
        return self.instance.show_location if self.instance else False

    def get_social_links(self, obj):
        profile = self._profile(obj)
        if not obj.show_social_links or profile is None:
            return {}
        links = {}
        for key in ('github_url', 'linkedin_url', 'website_url'):
            value = getattr(profile, key, '')
            if value:
                links[key] = value
        return links

    def get_contact_enabled(self, obj):
        return bool(obj.show_contact)

    def get_about(self, obj):
        return {
            'text': obj.about,
            'interests': obj.interests or [],
            'currently_learning': obj.currently_learning,
            'enjoys_building': obj.enjoys_building,
        }

    def get_projects(self, obj):
        public_projects = (
            StudentProject.objects
            .filter(user=obj.user, visibility='public')
            .prefetch_related('images')
            .order_by('-featured', 'display_order', '-updated_at')
        )
        return StudentProjectPublicSerializer(
            public_projects, many=True, context=self.context,
        ).data

    def _demonstrated_skill_names(self, obj):
        """Skills backed by an actual completed course on the platform."""
        names = set()
        completed = Enrollment.objects.filter(
            user=obj.user, status='completed'
        ).select_related('course')
        for enrollment in completed:
            course = enrollment.course
            if course.language:
                names.add(course.language.lower())
        return names

    def get_skills(self, obj):
        if not obj.show_skills:
            return {'visible': False, 'groups': []}
        profile_rows = UserSkill.objects.filter(
            user=obj.user,
        ).select_related('skill')
        demonstrated = self._demonstrated_skill_names(obj)
        proficiency_labels = dict(UserSkill.PROFICIENCY_CHOICES)
        groups = {}
        for row in profile_rows:
            category = row.skill.category or 'Other'
            groups.setdefault(category, []).append({
                'name': row.skill.name,
                'proficiency': row.proficiency,
                'proficiency_label': proficiency_labels.get(row.proficiency, ''),
                # Self-reported unless a completed Code Yaar course evidences it.
                'demonstrated': row.skill.name.lower() in demonstrated,
            })
        return {
            'visible': True,
            'groups': [
                {'category': category, 'items': items}
                for category, items in sorted(groups.items())
            ],
        }

    def get_achievements(self, obj):
        profile = self._profile(obj)
        show_badges = getattr(profile, 'show_badges', True) if profile else True
        if not obj.show_achievements or not show_badges:
            return {'visible': False, 'items': []}
        earned = UserAchievement.objects.filter(
            user=obj.user, status='active', achievement__is_active=True,
        ).select_related('achievement').order_by('-earned_at')
        items = [{
            'slug': ua.achievement.slug,
            'title': ua.achievement.title,
            'description': ua.achievement.description,
            'icon': ua.achievement.icon,
            'category': ua.achievement.category,
            'difficulty': ua.achievement.difficulty,
            'earned_at': ua.earned_at.isoformat(),
            'verification_url': ua.verification_url(),
        } for ua in earned]
        return {'visible': True, 'items': items}

    def get_learning_journey(self, obj):
        if not obj.show_learning_progress:
            return {'visible': False, 'tracks_completed': [], 'courses_completed': []}
        profile = self._profile(obj)
        show_courses = getattr(profile, 'show_courses', True) if profile else True
        tracks_completed, courses_completed = [], []
        if show_courses:
            completed = Enrollment.objects.filter(
                user=obj.user, status='completed',
            ).select_related('course', 'course__track')
            seen_tracks = set()
            for enrollment in completed:
                course = enrollment.course
                courses_completed.append({
                    'title': course.title,
                    'track': course.track.title,
                    'completed_at': enrollment.completed_at.isoformat()
                    if enrollment.completed_at else None,
                })
                if course.track.pk not in seen_tracks:
                    seen_tracks.add(course.track.pk)
                    tracks_completed.append({
                        'slug': course.track.slug, 'title': course.track.title,
                    })
        return {
            'visible': True,
            'tracks_completed': tracks_completed,
            'courses_completed': courses_completed,
        }
