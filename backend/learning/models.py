import hashlib

from django.core.exceptions import ValidationError
from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone


def hash_auth_token(raw_token: str) -> str:
    """SHA-256 a raw authentication token before it touches the database."""
    return hashlib.sha256(raw_token.encode('utf-8')).hexdigest()


class UserProfile(models.Model):
    """Extended user profile with learning-specific fields.

    This is the platform's student profile. It extends Django's established
    ``auth.User`` instead of replacing it, so existing enrolments, progress,
    attempts, and certificates keep their foreign keys.
    """
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('mentor', 'Mentor'),
        ('admin', 'Admin'),
    ]
    EDUCATION_LEVEL_CHOICES = [
        ('school', 'School'),
        ('high_school', 'High school'),
        ('undergraduate', 'Undergraduate'),
        ('graduate', 'Graduate'),
        ('bootcamp', 'Bootcamp'),
        ('self_taught', 'Self taught'),
        ('other', 'Other'),
    ]
    # Fixed keys for account-level notification preferences. Values live on
    # ``notification_preferences``; unknown keys are rejected at the API edge.
    NOTIFICATION_PREFERENCE_KEYS = (
        'achievements', 'learning_reminders', 'streak_reminders',
        'community', 'announcements',
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    # ImageField stores the same varchar column a URLField did, so historical
    # absolute-URL values survive unchanged; uploads write media-relative paths
    # under ``avatars/``. ``api`` serializers render either form as a URL.
    avatar = models.ImageField(
        upload_to='avatars/%Y/', blank=True, default='',
        help_text='Profile picture uploaded by the learner (or a legacy URL)'
    )
    bio = models.TextField(blank=True, default='')
    location = models.CharField(max_length=100, blank=True, default='')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    institution = models.CharField(max_length=200, blank=True, default='')
    education_level = models.CharField(
        max_length=20, choices=EDUCATION_LEVEL_CHOICES, blank=True, default=''
    )
    github_url = models.URLField(blank=True, default='')
    linkedin_url = models.URLField(blank=True, default='')
    website_url = models.URLField(blank=True, default='')
    email_verified = models.BooleanField(default=False)
    email_verified_at = models.DateTimeField(null=True, blank=True)
    xp_points = models.PositiveIntegerField(default=0)
    streak_days = models.PositiveIntegerField(default=0)
    longest_streak = models.PositiveIntegerField(default=0)
    level = models.PositiveIntegerField(default=1)
    # ── Privacy: what a public viewer (anyone but the owner) may see ──
    is_profile_public = models.BooleanField(
        default=True,
        help_text='Uncheck to hide the profile from /profile/<username> visitors'
    )
    show_badges = models.BooleanField(default=True, help_text='Display earned badges publicly')
    show_activity = models.BooleanField(default=True, help_text='Display recent learning activity publicly')
    show_courses = models.BooleanField(default=True, help_text='Display completed courses publicly')
    notification_preferences = models.JSONField(
        default=dict, blank=True,
        help_text='Account-level toggles keyed by NOTIFICATION_PREFERENCE_KEYS'
    )
    deletion_requested_at = models.DateTimeField(
        null=True, blank=True,
        help_text='Set when the learner requests account deletion; an admin action follows'
    )
    last_active_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def full_name(self):
        return self.user.get_full_name().strip() or self.user.username

    def avatar_url(self) -> str:
        """Render the avatar whether it is a media file or a legacy URL string."""
        value = self.avatar
        if not value:
            return ''
        text = getattr(value, 'name', '') or str(value)
        if text.startswith(('http://', 'https://', '/')):
            return text
        return value.url

    def get_notification_preference(self, key: str) -> bool:
        """Preferences default to on until the learner opts out explicitly."""
        value = (self.notification_preferences or {}).get(key)
        return True if value is None else bool(value)

    def __str__(self):
        return f"{self.user.username}'s profile"

    class Meta:
        ordering = ['-xp_points']


class CareerTrack(models.Model):
    """A learning track: the discovery layer above courses.

    Tracks group courses into meaningful paths (board classes, web
    development, AI...). Programming languages are course metadata, never
    navigation items, so a track is defined by what a learner can become —
    not by which syntax a course happens to teach.
    """
    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    CATEGORY_CHOICES = [
        ('school_board', 'School & Board Education'),
        ('programming', 'Programming'),
        ('web', 'Web Development'),
        ('ai', 'Artificial Intelligence'),
        ('other', 'Other'),
    ]

    slug = models.SlugField(max_length=100, unique=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    icon = models.CharField(max_length=50, blank=True, default='')
    category = models.CharField(
        max_length=30, choices=CATEGORY_CHOICES, default='other',
        help_text='Discovery-page grouping shown on track cards'
    )
    cover_image = models.ImageField(
        upload_to='track-covers/', null=True, blank=True,
        help_text='Optional cover illustration for the track cards and detail page'
    )
    learning_objectives = models.JSONField(
        default=list, blank=True,
        help_text='What a learner can do after finishing this track'
    )
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='beginner')
    estimated_hours = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True, help_text='Uncheck to archive the track')
    is_published = models.BooleanField(
        default=False,
        help_text='Only published tracks appear on the learner-facing Tracks page'
    )
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    @property
    def published_courses(self):
        return self.courses.filter(is_active=True, is_published=True).order_by('order', 'title')

    class Meta:
        ordering = ['order', 'title']


class Course(models.Model):
    """A course within a career track."""
    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    LANGUAGE_CHOICES = [
        ('python', 'Python'),
        ('javascript', 'JavaScript'),
        ('cpp', 'C++'),
        ('java', 'Java'),
        ('other', 'Other'),
    ]

    slug = models.SlugField(max_length=100, unique=True)
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=300, blank=True, default='')
    description = models.TextField()
    thumbnail = models.URLField(blank=True, default='')
    track = models.ForeignKey(
        CareerTrack,
        # PROTECT keeps an accidental track deletion from cascading into
        # published courses and learner progress; the admin guides the user
        # to move or archive instead.
        on_delete=models.PROTECT,
        related_name='courses'
    )
    # Academic class for board-textbook courses (e.g. "Class X"); blank for
    # general catalogue courses. Lets track pages sequence school classes.
    academic_class = models.CharField(max_length=50, blank=True, default='')
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='beginner')
    language = models.CharField(max_length=20, choices=LANGUAGE_CHOICES, default='python')
    instructor = models.CharField(max_length=200, blank=True, default='')
    prerequisites = models.TextField(blank=True, default='None')
    learning_objectives = models.JSONField(default=list, blank=True, help_text='List of skills learned')
    is_free = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    is_published = models.BooleanField(default=False)
    # ── Certification policy (configurable per course) ──
    certification_enabled = models.BooleanField(
        default=True,
        help_text='Whether completing this course can earn a verifiable certificate'
    )
    certification_passing_score = models.PositiveIntegerField(
        default=70,
        help_text='Minimum final-assessment percentage (0-100) required to certify'
    )
    require_all_lessons = models.BooleanField(
        default=True,
        help_text='Learner must complete every published lesson before certification'
    )
    require_final_assessment = models.BooleanField(
        default=True,
        help_text='Learner must pass the exercises flagged as the final assessment'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    @property
    def chapter_count(self):
        return self.chapters.filter(is_active=True).count()

    @property
    def lesson_count(self):
        return Lesson.objects.filter(
            chapter__course=self, chapter__is_active=True, is_active=True
        ).count()

    @property
    def exercise_count(self):
        return Exercise.objects.filter(
            lesson__chapter__course=self,
            lesson__chapter__is_active=True,
            lesson__is_active=True,
            is_active=True,
        ).count()

    @property
    def total_xp(self):
        """Derived from published content, never stored/fabricated."""
        lesson_xp = Lesson.objects.filter(
            chapter__course=self, chapter__is_active=True, is_active=True
        ).aggregate(s=models.Sum('xp_reward'))['s'] or 0
        exercise_xp = Exercise.objects.filter(
            lesson__chapter__course=self,
            lesson__chapter__is_active=True,
            lesson__is_active=True,
            is_active=True,
        ).aggregate(s=models.Sum('xp_reward'))['s'] or 0
        return lesson_xp + exercise_xp

    @property
    def estimated_hours(self):
        """Derived from actual lesson durations."""
        minutes = Lesson.objects.filter(
            chapter__course=self, chapter__is_active=True, is_active=True
        ).aggregate(s=models.Sum('duration_minutes'))['s'] or 0
        return max(1, round(minutes / 60))

    class Meta:
        ordering = ['track', 'order', 'title']


class SourceReference(models.Model):
    """
    Curriculum provenance for textbook-derived content.

    Records where a chapter or lesson came from — board, class, textbook unit,
    the topic name exactly as printed, and the printed page range — so a learner
    or reviewer can check it against the physical book. It also carries a
    verification status, which is the guard that stops un-reviewed material
    being published as official board syllabus.

    Left blank on content that is not textbook-derived (e.g. the general
    Python/JavaScript catalogue), so the existing courses stay unaffected.
    """
    SOURCE_TYPE_CHOICES = [
        ('', '— Not textbook-derived —'),
        ('official', 'Official — appears in the board textbook'),
        ('supplementary', 'Supplementary — practice built around official topics'),
        ('additional', 'Additional — beyond the textbook, clearly labelled'),
    ]
    VERIFICATION_STATUS_CHOICES = [
        ('', '— Not tracked —'),
        ('unverified', 'Not yet checked against the textbook'),
        ('verified', 'Verified against the textbook'),
        ('needs_review', 'Flagged for manual review — textbook wording unclear'),
    ]

    source_type = models.CharField(
        max_length=20, choices=SOURCE_TYPE_CHOICES, blank=True, default='',
        help_text='How this content relates to the board textbook'
    )
    verification_status = models.CharField(
        max_length=20, choices=VERIFICATION_STATUS_CHOICES, blank=True, default='',
        help_text='Official content must be verified before it is published'
    )
    textbook_board = models.CharField(
        max_length=50, blank=True, default='',
        help_text='e.g. "Sindh Board"'
    )
    textbook_class = models.CharField(
        max_length=20, blank=True, default='',
        help_text='e.g. "Class X"'
    )
    textbook_unit = models.CharField(
        max_length=100, blank=True, default='',
        help_text='Unit/chapter exactly as printed, e.g. "Unit 3"'
    )
    textbook_topic = models.CharField(
        max_length=200, blank=True, default='',
        help_text='Original topic name exactly as printed, e.g. "3.3.4 Escape Sequences"'
    )
    textbook_pages = models.CharField(
        max_length=50, blank=True, default='',
        help_text='Printed page number or range, e.g. "56" or "56-57"'
    )

    class Meta:
        abstract = True

    @property
    def has_textbook_reference(self):
        return bool(self.source_type)

    @property
    def textbook_reference_label(self):
        """Human-readable citation, or '' when the content is not textbook-derived."""
        parts = [p for p in (self.textbook_unit, self.textbook_topic) if p]
        if not parts:
            return ''
        label = ' > '.join(parts)
        return f'{label} (p. {self.textbook_pages})' if self.textbook_pages else label

    def clean(self):
        super().clean()
        if self.source_type == 'official' and self.verification_status != 'verified':
            raise ValidationError({
                'verification_status': (
                    'Official board-textbook content can only be saved as '
                    '"verified" once it has been checked against the textbook. '
                    'Use "needs_review" or set the source type to '
                    '"supplementary"/"additional" instead.'
                )
            })
        if self.source_type and not self.textbook_class:
            raise ValidationError({
                'textbook_class': (
                    'Textbook-derived content must state which class it belongs to.'
                )
            })


class Chapter(SourceReference):
    """A chapter within a course, grouping related lessons."""
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='chapters'
    )
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=100)
    description = models.TextField(blank=True, default='')
    order = models.PositiveIntegerField(default=0)
    xp_reward = models.PositiveIntegerField(default=500, help_text='XP earned on chapter completion')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.course.title} > {self.title}"

    @property
    def lesson_count(self):
        return self.lessons.count()

    @property
    def exercise_count(self):
        return Exercise.objects.filter(lesson__chapter=self).count()

    class Meta:
        ordering = ['course', 'order']
        unique_together = ['course', 'slug']
        verbose_name_plural = 'chapters'


class Lesson(SourceReference):
    """A single lesson within a chapter."""
    CONTENT_TYPE_CHOICES = [
        ('video', 'Video'),
        ('text', 'Text'),
        ('interactive', 'Interactive'),
        ('exercise', 'Exercise'),
    ]
    STATE_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('needs_practice', 'Needs Practice'),
        ('mastered', 'Mastered'),
    ]

    chapter = models.ForeignKey(
        Chapter,
        on_delete=models.CASCADE,
        related_name='lessons'
    )
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=100)
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPE_CHOICES, default='text')
    learning_objective = models.CharField(
        max_length=300, blank=True, default='',
        help_text='What the learner will be able to do after this lesson'
    )
    content_body = models.TextField(blank=True, default='', help_text='Main lesson content (markdown)')
    video_url = models.URLField(blank=True, default='')
    video_duration_seconds = models.PositiveIntegerField(default=0)
    order = models.PositiveIntegerField(default=0)
    duration_minutes = models.PositiveIntegerField(default=0)
    xp_reward = models.PositiveIntegerField(default=50)
    is_free_preview = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.chapter.course.title} > {self.chapter.title} > {self.title}"

    class Meta:
        ordering = ['chapter__course', 'chapter__order', 'order']
        unique_together = ['chapter', 'slug']


class Exercise(SourceReference):
    """
    An exercise within a lesson. Supports multiple types.

    Carries its own source reference because the textbook's EXERCISE and LAB
    ACTIVITIES blocks sit on different pages than the teaching content they
    follow — a question lifted from p.46 needs to cite p.46, not the lesson's
    pages.
    """
    TYPE_CHOICES = [
        ('code', 'Code Exercise'),
        ('multiple_choice', 'Multiple Choice'),
        ('multiple_select', 'Multiple Select'),
        ('debugging', 'Debugging Exercise'),
        ('output_prediction', 'Output Prediction'),
        ('fill_blank', 'Fill in the Blank'),
    ]
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]
    LANGUAGE_CHOICES = [
        ('python', 'Python'),
        ('javascript', 'JavaScript'),
        ('cpp', 'C++'),
        ('java', 'Java'),
        ('none', 'None'),
    ]

    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name='exercises'
    )
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=100)
    exercise_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='code')
    instructions = models.TextField(help_text='What the learner must do')
    context = models.TextField(blank=True, default='', help_text='Why this exercise matters')
    constraints = models.TextField(blank=True, default='', help_text='Rules/limitations')
    expected_behavior = models.TextField(blank=True, default='', help_text='Expected outcome')
    explain = models.TextField(
        blank=True, default='',
        help_text='Explanation revealed to the learner after they submit an attempt'
    )
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='easy')
    language = models.CharField(max_length=10, choices=LANGUAGE_CHOICES, default='python')
    starter_code = models.TextField(blank=True, default='')
    solution_code = models.TextField(blank=True, default='')
    # For multiple choice/select
    choices = models.JSONField(default=list, blank=True, help_text='List of choice objects [{id, text, is_correct}]')
    # For output prediction
    expected_output = models.TextField(blank=True, default='')
    # Validation
    test_cases = models.JSONField(default=list, blank=True, help_text='Test cases for validation')
    hidden_tests = models.JSONField(default=list, blank=True, help_text='Hidden test cases')
    # Scoring
    xp_reward = models.PositiveIntegerField(default=100)
    max_attempts = models.PositiveIntegerField(default=0, help_text='0 = unlimited')
    is_final_assessment = models.BooleanField(
        default=False,
        help_text='Counts toward the course final-assessment grade used for certification'
    )
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.lesson.title} > {self.title}"

    class Meta:
        ordering = ['lesson', 'order']
        unique_together = ['lesson', 'slug']


class Hint(models.Model):
    """Progressive hints for an exercise."""
    exercise = models.ForeignKey(
        Exercise,
        on_delete=models.CASCADE,
        related_name='hints'
    )
    content = models.TextField(help_text='Hint text shown to learner')
    order = models.PositiveIntegerField(default=0, help_text='Order of reveal (1 = first hint)')
    reveals_solution = models.BooleanField(default=False, help_text='If true, this hint shows the solution')
    xp_penalty = models.PositiveIntegerField(default=0, help_text='XP deducted when using this hint')

    def __str__(self):
        return f"Hint {self.order} for {self.exercise.title}"

    class Meta:
        ordering = ['exercise', 'order']


class Resource(models.Model):
    """Course resources: datasets, cheat sheets, reference material."""
    TYPE_CHOICES = [
        ('dataset', 'Dataset'),
        ('cheat_sheet', 'Cheat Sheet'),
        ('slides', 'Slides'),
        ('reference', 'Reference'),
        ('starter_file', 'Starter File'),
        ('other', 'Other'),
    ]

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='resources'
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, default='')
    resource_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='other')
    file_url = models.URLField(blank=True, default='')
    file_name = models.CharField(max_length=200, blank=True, default='')
    file_size_bytes = models.PositiveIntegerField(default=0)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.course.title} > {self.title}"

    class Meta:
        ordering = ['course', 'order']


class Enrollment(models.Model):
    """A user's enrollment in a course."""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('dropped', 'Dropped'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='enrollments'
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='enrollments'
    )
    enrolled_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    last_activity_at = models.DateTimeField(null=True, blank=True)
    last_lesson = models.ForeignKey(
        Lesson,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='+',
        help_text='Last lesson the learner was on (for resume)'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')

    def __str__(self):
        return f"{self.user.username} enrolled in {self.course.title}"

    @property
    def progress_percentage(self):
        total_lessons = Lesson.objects.filter(chapter__course=self.course).count()
        if total_lessons == 0:
            return 0
        completed = LessonProgress.objects.filter(
            user=self.user,
            lesson__chapter__course=self.course,
            status='completed'
        ).count()
        return round((completed / total_lessons) * 100)

    class Meta:
        unique_together = ['user', 'course']
        ordering = ['-enrolled_at']


class LessonProgress(models.Model):
    """Tracks a user's progress on a specific lesson."""
    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('needs_practice', 'Needs Practice'),
        ('mastered', 'Mastered'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='lesson_progress'
    )
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name='progress_entries'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_started')
    time_spent_seconds = models.PositiveIntegerField(default=0)
    video_watched_seconds = models.PositiveIntegerField(default=0)
    completed_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.lesson.title} ({self.status})"

    class Meta:
        unique_together = ['user', 'lesson']
        ordering = ['lesson__chapter__order', 'lesson__order']


class ExerciseAttempt(models.Model):
    """Tracks a user's attempt at an exercise."""
    STATUS_CHOICES = [
        ('running', 'Running'),
        ('incorrect', 'Incorrect'),
        ('correct', 'Correct'),
        ('error', 'Runtime Error'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='exercise_attempts'
    )
    exercise = models.ForeignKey(
        Exercise,
        on_delete=models.CASCADE,
        related_name='attempts'
    )
    # Client-supplied idempotency key: a replayed submission (double-click,
    # retried network request) carries the same id and is returned the
    # original result instead of being re-graded or re-awarded.
    submission_id = models.CharField(
        max_length=64, null=True, blank=True, unique=True,
        help_text='Unique per logical submission; replays resolve to this record'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='running')
    submitted_code = models.TextField(blank=True, default='')
    selected_answer = models.JSONField(null=True, blank=True, help_text='For MCQ/MSQ')
    output = models.TextField(blank=True, default='')
    error_message = models.TextField(blank=True, default='')
    feedback = models.TextField(blank=True, default='', help_text='Specific feedback for this attempt')
    test_results = models.JSONField(default=list, blank=True)
    hints_used = models.PositiveIntegerField(default=0)
    time_spent_seconds = models.PositiveIntegerField(default=0)
    xp_earned = models.PositiveIntegerField(default=0)
    attempt_number = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.exercise.title} (#{self.attempt_number})"

    class Meta:
        ordering = ['-created_at']
        constraints = [
            # Two submissions may never resolve to the same idempotency key.
            models.UniqueConstraint(
                fields=['submission_id'],
                condition=~models.Q(submission_id__isnull=True),
                name='unique_exercise_attempt_submission_id',
            ),
        ]


class SnippetRun(models.Model):
    """Daily counter of sandboxed snippet runs per user (abuse guard)."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='snippet_runs'
    )
    date = models.DateField()
    count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} snippet runs {self.date}: {self.count}"

    class Meta:
        unique_together = ['user', 'date']
        ordering = ['-date']


# Actions whose award must exist at most once per user + referenced object.
# Repeated merit (e.g. several streak bonuses) is intentionally not awarded for
# these; the database itself refuses a second award row. Module level because a
# nested `Meta` body is executed with module globals as its only outer scope —
# it cannot see attributes defined in the class body around it. Iteration order
# of a frozenset of strings is randomised per process, so migration authoring
# must go through `sorted()`; otherwise every `makemigrations` run sees a
# different `action__in` list and emits a spurious remove/recreate pair.
UNIQUE_AWARD_ACTIONS = frozenset({
    'lesson_complete', 'exercise_complete', 'chapter_complete', 'course_complete',
    'achievement_bonus', 'challenge_complete',
})


class XPTransaction(models.Model):
    """Tracks all XP earned/spent by a user."""
    ACTION_CHOICES = [
        ('lesson_complete', 'Lesson Complete'),
        ('exercise_complete', 'Exercise Complete'),
        ('chapter_complete', 'Chapter Complete'),
        ('course_complete', 'Course Complete'),
        ('challenge_complete', 'Challenge Complete'),
        ('hint_used', 'Hint Used'),
        ('achievement_bonus', 'Achievement Bonus'),
        ('streak_bonus', 'Streak Bonus'),
        ('manual_adjustment', 'Manual Adjustment'),
    ]
    # Kept on the class for callers that read it from the model (see xp.py).
    UNIQUE_AWARD_ACTIONS = UNIQUE_AWARD_ACTIONS

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='xp_transactions'
    )
    amount = models.IntegerField(help_text='Positive for earned, negative for spent')
    action = models.CharField(max_length=30, choices=ACTION_CHOICES)
    description = models.CharField(max_length=300, blank=True, default='')
    # Generic FK to associate with specific content
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}: {self.amount:+d} XP ({self.action})"

    class Meta:
        ordering = ['-created_at']
        constraints = [
            # Database-level guarantee: one award transaction per user, action
            # and referenced content item. Concurrent duplicate requests can
            # never produce a second XP award for the same completion.
            models.UniqueConstraint(
                fields=['user', 'action', 'content_type', 'object_id'],
                condition=models.Q(action__in=sorted(UNIQUE_AWARD_ACTIONS))
                             & ~models.Q(content_type__isnull=True)
                             & ~models.Q(object_id__isnull=True),
                name='unique_xp_award_per_user_action_reference',
            ),
        ]


class Achievement(models.Model):
    """An achievement/badge that can be earned."""
    CATEGORY_CHOICES = [
        ('course', 'Course Completion'),
        ('chapter', 'Chapter Completion'),
        ('streak', 'Streak'),
        ('exercise', 'Exercise Mastery'),
        ('skill', 'Skill'),
        ('special', 'Special'),
        ('excellence', 'Excellence Award'),
        ('project', 'Project Builder'),
    ]
    # The platform-wide difficulty taxonomy. Distinct from the XP-derived
    # ``badge_art.level_label`` tier: difficulty says how demanding earning
    # the badge is, the tier says how valuable the award is.
    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]

    slug = models.SlugField(max_length=100, unique=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    icon = models.CharField(max_length=50, blank=True, default='')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='special')
    difficulty = models.CharField(
        max_length=20, choices=DIFFICULTY_CHOICES, default='beginner'
    )
    xp_bonus = models.PositiveIntegerField(default=0)
    # Condition for earning (JSON for flexibility)
    condition_type = models.CharField(max_length=100, help_text='e.g., course_complete, streak_7')
    condition_value = models.CharField(max_length=200, blank=True, default='', help_text='e.g., course slug, number')
    how_to_earn = models.TextField(
        blank=True, default='',
        help_text='Learner-facing guidance shown on locked badges'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['category', 'title']


def _generate_badge_public_id() -> str:
    import secrets
    return secrets.token_urlsafe(20)


class UserAchievement(models.Model):
    """An achievement earned by a user."""

    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'
        REVOKED = 'revoked', 'Revoked'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='achievements'
    )
    achievement = models.ForeignKey(
        Achievement,
        on_delete=models.CASCADE,
        related_name='user_achievements'
    )
    earned_at = models.DateTimeField(auto_now_add=True)
    public_id = models.CharField(
        max_length=40, unique=True, editable=False, default=_generate_badge_public_id,
    )
    credential_id = models.CharField(max_length=32, unique=True, editable=False)
    recipient_name = models.CharField(max_length=250, blank=True, default='')
    status = models.CharField(
        max_length=12, choices=Status.choices, default=Status.ACTIVE,
    )

    def __str__(self):
        return f"{self.user.username} earned {self.achievement.title}"

    class Meta:
        unique_together = ['user', 'achievement']
        ordering = ['-earned_at']

    @property
    def is_valid(self) -> bool:
        return self.status == self.Status.ACTIVE

    def verification_url(self) -> str:
        return f"{settings.SITE_URL}/verify/badge/{self.credential_id}"

    def save(self, *args, **kwargs):
        if not self.public_id:
            self.public_id = _generate_badge_public_id()
        if not self.credential_id:
            self.credential_id = self._mint_credential_id()
        if not self.recipient_name:
            full = (self.user.get_full_name() or '').strip()
            self.recipient_name = full or self.user.username
        super().save(*args, **kwargs)

    def _mint_credential_id(self) -> str:
        import secrets
        from django.utils import timezone
        year = timezone.localdate().year
        while True:
            token = secrets.token_hex(3).upper()
            candidate = f'CY-BDG-{year}-{token}'
            if not UserAchievement.objects.filter(credential_id=candidate).exists():
                return candidate


class UserNotification(models.Model):
    """In-app notification generated by verified platform events.

    Rows are only ever written by server-side services when the underlying
    event actually happened (badge truly unlocked, streak truly extended,
    course truly completed). ``read_at`` marks the moment the learner saw
    and dismissed it.
    """

    class Type(models.TextChoices):
        BADGE_UNLOCK = 'badge_unlock', 'Badge unlocked'
        STREAK_RECORD = 'streak_record', 'New streak record'
        TRACK_COMPLETE = 'track_complete', 'Learning track completed'
        XP_MILESTONE = 'xp_milestone', 'XP milestone reached'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    type = models.CharField(max_length=20, choices=Type.choices)
    title = models.CharField(max_length=200)
    body = models.TextField(blank=True, default='')
    link = models.CharField(
        max_length=300, blank=True, default='',
        help_text='In-app path the notification opens, e.g. /achievements'
    )
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}: {self.title}"

    @property
    def is_unread(self) -> bool:
        return self.read_at is None

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'read_at'], name='notif_user_read'),
        ]


class Project(models.Model):
    """A hands-on project for building practical skills."""
    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]

    slug = models.SlugField(max_length=100, unique=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    thumbnail = models.URLField(blank=True, default='')
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='beginner')
    technologies = models.JSONField(default=list, blank=True)
    estimated_hours = models.PositiveIntegerField(default=0)
    track = models.ForeignKey(
        CareerTrack,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='projects'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['title']


class ProjectMilestone(models.Model):
    """A milestone/step within a project."""
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='milestones'
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, default='')
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.project.title} > {self.title}"

    class Meta:
        ordering = ['project', 'order']


class Challenge(models.Model):
    """A standalone coding challenge (separate from course exercises).

    A challenge is a self-contained program problem: the learner writes a
    program that reads from standard input and writes to standard output, so
    it can be genuinely executed and graded by the same sandbox that handles
    course exercises (see ``learning.services.sandbox``). ``sample_tests`` are
    shown in the workspace for "Run"; ``hidden_tests`` are used only by
    "Submit" and are never sent to a client.
    """
    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    LANGUAGE_CHOICES = [
        ('python', 'Python'),
        ('cpp', 'C++'),
    ]

    slug = models.SlugField(max_length=100, unique=True)
    title = models.CharField(max_length=200)
    description = models.TextField(help_text='One-line summary shown on the card')
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='beginner')
    topic = models.CharField(max_length=100)
    estimated_minutes = models.PositiveIntegerField(default=0)
    # Languages offered in the workspace. Only these appear in the selector and
    # only the ones with matching starter/solution/test code can be submitted.
    languages = models.JSONField(
        default=list, blank=True,
        help_text="Ordered language codes the learner may choose, e.g. ['python', 'cpp']"
    )
    starter_code = models.TextField(blank=True, default='', help_text='Python starter code')
    starter_code_cpp = models.TextField(blank=True, default='', help_text='C++ starter code')
    solution_code = models.TextField(blank=True, default='', help_text='Reference Python solution')
    solution_code_cpp = models.TextField(blank=True, default='', help_text='Reference C++ solution')

    # Rich, learner-facing problem content.
    problem_statement = models.TextField(blank=True, default='')
    requirements = models.JSONField(default=list, blank=True, help_text='Bullet list of what to do')
    input_description = models.TextField(blank=True, default='')
    output_description = models.TextField(blank=True, default='')
    constraints = models.JSONField(default=list, blank=True, help_text='List of constraint lines')
    examples = models.JSONField(
        default=list, blank=True,
        help_text="List of {input, output, explanation} shown in the workspace"
    )
    hints = models.JSONField(
        default=list, blank=True,
        help_text="Ordered list of hint strings, revealed one at a time"
    )
    solution_explanation = models.TextField(blank=True, default='')
    time_complexity = models.CharField(max_length=100, blank=True, default='')
    space_complexity = models.CharField(max_length=100, blank=True, default='')

    # Grading. Sample tests are visible; hidden tests grade submissions.
    sample_tests = models.JSONField(
        default=list, blank=True,
        help_text="Visible tests [{'input', 'expected_output'}] run by 'Run'"
    )
    hidden_tests = models.JSONField(
        default=list, blank=True,
        help_text="Hidden tests used only by 'Submit'; never sent to clients"
    )

    xp_reward = models.PositiveIntegerField(default=50)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"[{self.difficulty}] {self.title}"

    def starter_for(self, language: str) -> str:
        return self.starter_code_cpp if language == 'cpp' else self.starter_code

    def solution_for(self, language: str) -> str:
        return self.solution_code_cpp if language == 'cpp' else self.solution_code

    def supported_languages(self) -> list[str]:
        return list(self.languages) if self.languages else ['python']

    class Meta:
        ordering = ['topic', 'difficulty', 'title']


class PracticalClass(models.Model):
    """A school class grouping practical subjects."""

    BOARD_CHOICES = [
        ('stb', 'Sindh Textbook Board'),
    ]

    slug = models.SlugField(max_length=100, unique=True)
    title = models.CharField(max_length=100)
    board = models.CharField(max_length=20, choices=BOARD_CHOICES, default='stb')
    thumbnail = models.URLField(blank=True, default='')
    description = models.TextField(blank=True, default='')
    order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['order', 'title']
        verbose_name = 'practical class'
        verbose_name_plural = 'practical classes'


class PracticalSubject(models.Model):
    """A subject within a school class."""

    practical_class = models.ForeignKey(
        PracticalClass,
        on_delete=models.CASCADE,
        related_name='subjects',
    )
    slug = models.SlugField(max_length=100)
    title = models.CharField(max_length=100)
    image = models.URLField(blank=True, default='')
    description = models.TextField(blank=True, default='')
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.practical_class.title} > {self.title}'

    class Meta:
        ordering = ['practical_class', 'order', 'title']
        constraints = [
            models.UniqueConstraint(
                fields=['practical_class', 'slug'],
                name='unique_practical_subject_slug_per_class',
            ),
        ]


class Practical(models.Model):
    """A flexible, publishable practical exercise.

    The structured text fields cover common school-lab formats. ``diagrams``
    stores a list of approved image URLs so subjects can add visuals without
    changing the frontend schema.
    """

    practical_class = models.ForeignKey(
        PracticalClass,
        on_delete=models.CASCADE,
        related_name='practicals',
    )
    subject = models.ForeignKey(
        PracticalSubject,
        on_delete=models.CASCADE,
        related_name='practicals',
    )
    slug = models.SlugField(max_length=150, unique=True)
    title = models.CharField(max_length=250)
    practical_number = models.PositiveIntegerField(default=1)
    description = models.TextField(blank=True, default='')
    chapter_topic = models.CharField(max_length=250, blank=True, default='')
    aim = models.TextField(blank=True, default='')
    apparatus = models.TextField(blank=True, default='')
    theory = models.TextField(blank=True, default='')
    procedure = models.TextField(blank=True, default='')
    observations = models.TextField(blank=True, default='')
    calculations = models.TextField(blank=True, default='')
    result = models.TextField(blank=True, default='')
    precautions = models.TextField(blank=True, default='')
    diagrams = models.JSONField(
        default=list,
        blank=True,
        help_text='List of image objects, for example [{url, caption}].',
    )
    order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.practical_class.title} > {self.subject.title} > {self.title}'

    class Meta:
        ordering = ['subject', 'order', 'practical_number', 'title']
        constraints = [
            models.UniqueConstraint(
                fields=['subject', 'practical_number'],
                name='unique_practical_number_per_subject',
            ),
        ]

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.subject_id and self.practical_class_id:
            if self.subject.practical_class_id != self.practical_class_id:
                raise ValidationError({
                    'subject': 'The subject must belong to the selected practical class.',
                })


class PracticalProgress(models.Model):
    """Completion state for a practical in a learner's account."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='practical_progress',
    )
    practical = models.ForeignKey(
        Practical,
        on_delete=models.CASCADE,
        related_name='progress_entries',
    )
    completed_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'practical'],
                name='unique_practical_progress_per_user',
            ),
        ]


class PracticalBookmark(models.Model):
    """A learner's bookmark for a practical."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='practical_bookmarks',
    )
    practical = models.ForeignKey(
        Practical,
        on_delete=models.CASCADE,
        related_name='bookmarks',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'practical'],
                name='unique_practical_bookmark_per_user',
            ),
        ]


class LearningActivity(models.Model):
    """A meaningful learner event used for history, analytics, and streaks."""

    TYPE_CHOICES = [
        ('course_started', 'Course started'),
        ('lesson_completed', 'Lesson completed'),
        ('practical_completed', 'Practical completed'),
        ('quiz_attempted', 'Quiz attempted'),
        ('course_completed', 'Course completed'),
        ('bookmark_created', 'Bookmark created'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='learning_activities',
    )
    activity_type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    title = models.CharField(max_length=250)
    status = models.CharField(max_length=30, default='completed')
    course = models.ForeignKey(
        Course, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='learning_activities',
    )
    lesson = models.ForeignKey(
        Lesson, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='learning_activities',
    )
    practical = models.ForeignKey(
        Practical, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='learning_activities',
    )
    exercise = models.ForeignKey(
        Exercise, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='learning_activities',
    )
    dedupe_key = models.CharField(max_length=180, unique=True)
    activity_date = models.DateField()
    occurred_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-occurred_at']
        indexes = [
            models.Index(fields=['user', 'activity_date']),
            models.Index(fields=['user', 'activity_type', '-occurred_at']),
        ]


class ChallengeSubmission(models.Model):
    """One scored submission of a challenge, kept as history and completion.

    Mirrors the integrity rules of ``ExerciseAttempt``: a repeat request that
    carries an already-processed ``submission_id`` replays its stored result,
    and XP is awarded at most once per user + challenge (guarded by the
    ``challenge_complete`` unique constraint on XPTransaction).
    """
    STATUS_CHOICES = [
        ('correct', 'Correct'),
        ('incorrect', 'Incorrect'),
        ('error', 'Error'),
        ('running', 'Running'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='challenge_submissions'
    )
    challenge = models.ForeignKey(
        Challenge,
        on_delete=models.CASCADE,
        related_name='submissions'
    )
    submission_id = models.UUIDField(null=True, blank=True, db_index=True)
    language = models.CharField(max_length=10, default='python')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='running')
    submitted_code = models.TextField(blank=True, default='')
    output = models.TextField(blank=True, default='')
    error_message = models.TextField(blank=True, default='')
    feedback = models.TextField(blank=True, default='')
    test_results = models.JSONField(default=list, blank=True)
    xp_earned = models.PositiveIntegerField(default=0)
    time_spent_seconds = models.PositiveIntegerField(default=0)
    attempt_number = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.challenge.title} ({self.status})"

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'challenge', 'status']),
        ]


class Progress(models.Model):
    """Generic progress tracker (kept for backward compatibility)."""
    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='progress_entries'
    )
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_started')
    score = models.FloatField(null=True, blank=True)
    time_spent_minutes = models.PositiveIntegerField(default=0)
    completed_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.content_type} ({self.status})"

    class Meta:
        unique_together = ['user', 'content_type', 'object_id']
        ordering = ['-updated_at']


class Certification(models.Model):
    """A certification offered for a career track."""
    track = models.ForeignKey(
        CareerTrack,
        on_delete=models.CASCADE,
        related_name='certifications'
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    badge_icon = models.URLField(blank=True, default='')
    passing_score = models.FloatField(default=70.0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.track.title})"

    class Meta:
        ordering = ['track', 'title']


class UserCertification(models.Model):
    """A certification earned by a user."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='certifications'
    )
    certification = models.ForeignKey(
        Certification,
        on_delete=models.CASCADE,
        related_name='user_certifications'
    )
    earned_at = models.DateTimeField(auto_now_add=True)
    credential_id = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return f"{self.user.username} - {self.certification.title}"

    class Meta:
        unique_together = ['user', 'certification']
        ordering = ['-earned_at']


class Skill(models.Model):
    """A skill that can be tracked and measured."""
    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, blank=True, default='')

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['category', 'name']


class UserSkill(models.Model):
    """A user's proficiency in a specific skill."""
    PROFICIENCY_CHOICES = [
        (1, 'Novice'),
        (2, 'Beginner'),
        (3, 'Intermediate'),
        (4, 'Advanced'),
        (5, 'Expert'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='skills'
    )
    skill = models.ForeignKey(
        Skill,
        on_delete=models.CASCADE,
        related_name='user_skills'
    )
    proficiency = models.PositiveSmallIntegerField(choices=PROFICIENCY_CHOICES, default=1)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.skill.name} ({self.proficiency}/5)"

    class Meta:
        unique_together = ['user', 'skill']
        ordering = ['-proficiency']


# ─── Authentication ─────────────────────────────────────────────────────────


class EmailVerificationToken(models.Model):
    """Single-use, time-limited email verification token.

    Only the SHA-256 hash is persisted: the raw token exists solely inside
    the emailed link, so a database leak cannot be replayed.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='email_verification_tokens',
    )
    token_hash = models.CharField(max_length=64, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'used_at'], name='auth_email_token_user_used'),
        ]

    def __str__(self):
        return f"Email verification for user {self.user_id}"

    @property
    def is_expired(self):
        return timezone.now() >= self.expires_at

    @property
    def is_usable(self):
        return self.used_at is None and not self.is_expired


class PasswordResetToken(models.Model):
    """Single-use, time-limited password reset token (hash-only storage)."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='password_reset_tokens',
    )
    token_hash = models.CharField(max_length=64, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'used_at'], name='auth_reset_token_user_used'),
        ]

    def __str__(self):
        return f"Password reset for user {self.user_id}"

    @property
    def is_expired(self):
        return timezone.now() >= self.expires_at

    @property
    def is_usable(self):
        return self.used_at is None and not self.is_expired


class AuthenticationAuditLog(models.Model):
    """Append-only authentication event trail.

    Never records passwords, password hashes, raw tokens, or token hashes;
    only the event, the account it belongs to (when known), and coarse
    request metadata needed to investigate abuse.
    """

    class Event(models.TextChoices):
        REGISTER = 'register', 'Registration'
        LOGIN_SUCCESS = 'login_success', 'Login succeeded'
        LOGIN_FAILED = 'login_failed', 'Login failed'
        LOGOUT = 'logout', 'Logout'
        TOKEN_REFRESH = 'token_refresh', 'Access token refreshed'
        TOKEN_REFRESH_FAILED = 'token_refresh_failed', 'Token refresh failed'
        EMAIL_VERIFIED = 'email_verified', 'Email verified'
        EMAIL_VERIFICATION_SENT = 'email_verification_sent', 'Verification email sent'
        EMAIL_VERIFICATION_FAILED = 'email_verification_failed', 'Verification failed'
        PASSWORD_RESET_REQUESTED = 'password_reset_requested', 'Password reset requested'
        PASSWORD_RESET_COMPLETED = 'password_reset_completed', 'Password reset completed'
        PASSWORD_CHANGED = 'password_changed', 'Password changed'
        PROFILE_UPDATED = 'profile_updated', 'Profile updated'
        PRIVILEGE_ESCALATION_BLOCKED = (
            'privilege_escalation_blocked',
            'Privilege escalation blocked',
        )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='authentication_events',
    )
    event = models.CharField(max_length=40, choices=Event.choices)
    identifier = models.CharField(
        max_length=254,
        blank=True,
        default='',
        help_text='Username or email supplied by the request, when relevant',
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, blank=True, default='')
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['event', 'created_at'], name='auth_audit_event_created'),
            models.Index(fields=['user', 'created_at'], name='auth_audit_user_created'),
        ]

    def __str__(self):
        return f"{self.event} @ {self.created_at:%Y-%m-%d %H:%M}"
