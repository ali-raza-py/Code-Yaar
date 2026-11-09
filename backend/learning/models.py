import hashlib
import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Count, OuterRef, Subquery, Sum
from django.db.models.functions import Coalesce
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.utils.text import slugify


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
        'community', 'announcements', 'competitions',
    )
    # Optional email categories. Security mail (verification, password
    # changes) deliberately has no key here: it is never optional.
    EMAIL_NOTIFICATION_PREFERENCE_KEYS = (
        'email_learning', 'email_competitions', 'email_achievements',
        'email_certificates', 'email_announcements',
    )
    EMAIL_DIGEST_CHOICES = (
        ('none', 'No digest'), ('daily', 'Daily digest'), ('weekly', 'Weekly digest'),
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
    first_login_at = models.DateTimeField(null=True, blank=True)
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
        if text.startswith(('http://', 'https://')):
            return text
        if getattr(settings, 'CLOUD_STORAGE_ENABLED', False):
            return value.url
        # Frontend and API commonly run on different origins. Keep legacy
        # root-relative values usable by pointing them at the configured API.
        path = text if text.startswith('/') else f'/{text}'
        return f"{settings.BACKEND_URL.rstrip('/')}{path}"

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


class CourseCategory(models.Model):
    """Configurable catalogue category for a course.

    Categories are data, not code: the Course Creation Studio offers these as a
    dropdown and an administrator can add or retire one without a deploy.
    """

    slug = models.SlugField(max_length=80, unique=True)
    title = models.CharField(max_length=120)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['order', 'title']
        verbose_name_plural = 'course categories'


class CourseQuerySet(models.QuerySet):
    """Course listings with content aggregates in a single query."""

    def with_catalogue_stats(self):
        def scalar(queryset, group_by, expression):
            inner = (
                queryset.order_by()
                .values(group_by)
                .annotate(value=expression)
                .values('value')[:1]
            )
            return Coalesce(
                Subquery(inner),
                0,
                output_field=models.IntegerField(),
            )

        active_chapters = Chapter.objects.filter(
            course=OuterRef('pk'),
            is_active=True,
        )
        active_lessons = Lesson.objects.filter(
            chapter__course=OuterRef('pk'),
            chapter__is_active=True,
            is_active=True,
        )
        active_exercises = Exercise.objects.filter(
            lesson__chapter__course=OuterRef('pk'),
            lesson__chapter__is_active=True,
            lesson__is_active=True,
            is_active=True,
        )
        return self.annotate(
            chapter_count_agg=scalar(active_chapters, 'course', Count('pk')),
            lesson_count_agg=scalar(active_lessons, 'chapter__course', Count('pk')),
            exercise_count_agg=scalar(
                active_exercises, 'lesson__chapter__course', Count('pk')
            ),
            lesson_xp_agg=scalar(active_lessons, 'chapter__course', Sum('xp_reward')),
            exercise_xp_agg=scalar(
                active_exercises, 'lesson__chapter__course', Sum('xp_reward')
            ),
            lesson_minutes_agg=scalar(
                active_lessons, 'chapter__course', Sum('duration_minutes')
            ),
        )


class Course(models.Model):
    """A course within a career track."""
    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('elementary', 'Elementary'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('expert', 'Expert'),
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
    # ── Course Creation Studio metadata ──
    category = models.ForeignKey(
        CourseCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='courses',
        help_text='Configurable catalogue grouping shown on course cards'
    )
    cover_image = models.ImageField(
        upload_to='course-covers/%Y/', null=True, blank=True,
        help_text='Wide hero image for the course page; falls back to thumbnail'
    )
    tags = models.JSONField(default=list, blank=True, help_text='Topic tags for search')
    # Account this course is assigned to. ``instructor`` above stays the display
    # name, so existing seeded courses keep their credit while instructor-scoped
    # permissions finally have a real relationship to check against.
    instructor_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='taught_courses',
        help_text='Instructor account with editorial access to this course'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_courses'
    )
    prerequisite_courses = models.ManyToManyField(
        'self', symmetrical=False, blank=True, related_name='unlocks'
    )
    sequential_learning = models.BooleanField(
        default=False,
        help_text='Learners must finish each lesson before the next one unlocks'
    )
    xp_completion_reward = models.PositiveIntegerField(
        default=0,
        help_text='Bonus XP granted once the whole course completes'
    )
    # Author-supplied estimate; 0 means "derive it from lesson durations" so the
    # published figure is never a guess when nobody has filled the field in.
    manual_estimated_hours = models.PositiveIntegerField(default=0)
    # ── Publication lifecycle: draft -> scheduled/published -> archived ──
    publish_at = models.DateTimeField(
        null=True, blank=True,
        help_text='Publish automatically at this time (set by the schedule action)'
    )
    published_at = models.DateTimeField(null=True, blank=True)
    archived_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CourseQuerySet.as_manager()

    def __str__(self):
        return self.title

    def _agg(self, name):
        """Annotation from ``CourseQuerySet.with_catalogue_stats``, or None
        when this instance was loaded without it."""
        return self.__dict__.get(name)

    @property
    def chapter_count(self):
        agg = self._agg('chapter_count_agg')
        if agg is not None:
            return agg
        return self.chapters.filter(is_active=True).count()

    @property
    def lesson_count(self):
        agg = self._agg('lesson_count_agg')
        if agg is not None:
            return agg
        return Lesson.objects.filter(
            chapter__course=self, chapter__is_active=True, is_active=True
        ).count()

    @property
    def exercise_count(self):
        agg = self._agg('exercise_count_agg')
        if agg is not None:
            return agg
        return Exercise.objects.filter(
            lesson__chapter__course=self,
            lesson__chapter__is_active=True,
            lesson__is_active=True,
            is_active=True,
        ).count()

    @property
    def total_xp(self):
        """Derived from published content, never stored/fabricated."""
        lesson_xp = self._agg('lesson_xp_agg')
        exercise_xp = self._agg('exercise_xp_agg')
        if lesson_xp is not None and exercise_xp is not None:
            return lesson_xp + exercise_xp
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
        minutes = self._agg('lesson_minutes_agg')
        if minutes is None:
            minutes = Lesson.objects.filter(
                chapter__course=self, chapter__is_active=True, is_active=True
            ).aggregate(s=models.Sum('duration_minutes'))['s'] or 0
        return max(1, round(minutes / 60))

    @property
    def is_archived(self):
        return self.archived_at is not None

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
    def published_lesson_count(self):
        return self.lessons.filter(is_active=True).count()

    @property
    def publication_state(self):
        """Derived from its lessons, never stored, so the curriculum tree and the
        learner-facing view cannot disagree about what is live."""
        total = self.lessons.count()
        if total == 0:
            return 'empty'
        published = self.published_lesson_count
        if published == 0:
            return 'draft'
        return 'published' if published == total else 'partial'

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
    # ``is_active`` remains the single learner-visibility flag for a lesson: the
    # studio's Publish/Draft control writes this and nothing else, precisely so
    # a second "published" column can never drift out of sync with it.
    is_active = models.BooleanField(default=True)
    is_required = models.BooleanField(
        default=True,
        help_text='Optional lessons are excluded from completion requirements'
    )
    prerequisite = models.ForeignKey(
        'self',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='dependents',
        help_text='Lesson that must be completed before this one unlocks'
    )
    estimated_reading_minutes = models.PositiveIntegerField(default=0)
    completion_condition = models.JSONField(
        default=dict, blank=True,
        help_text='How this lesson is judged complete, e.g. {"type": "mark_complete"}'
    )
    instructor_notes = models.TextField(
        blank=True, default='',
        help_text='Internal guidance for instructors; never shown to learners'
    )
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

    ``type`` records what happened, ``category`` drives the notification
    center filters, and ``dedupe_key`` lets repeatable code paths (commands,
    concurrent requests, replays) announce the same event exactly once.
    """

    class Type(models.TextChoices):
        # Legacy types — kept so historical rows stay valid; new services map
        # richer events onto the additions below.
        BADGE_UNLOCK = 'badge_unlock', 'Badge unlocked'
        STREAK_RECORD = 'streak_record', 'New streak record'
        TRACK_COMPLETE = 'track_complete', 'Learning track completed'
        XP_MILESTONE = 'xp_milestone', 'XP milestone reached'
        # Account & security
        WELCOME = 'welcome', 'Welcome to Code Yaar'
        EMAIL_VERIFIED = 'email_verified', 'Email verified'
        PASSWORD_CHANGED = 'password_changed', 'Password changed'
        ACCOUNT_SECURITY = 'account_security', 'Account security update'
        # Learning & practice
        COURSE_ENROLLED = 'course_enrolled', 'Course enrolled'
        COURSE_COMPLETED = 'course_completed', 'Course completed'
        STREAK_MILESTONE = 'streak_milestone', 'Streak milestone reached'
        CHALLENGE_SOLVED = 'challenge_solved', 'Challenge solved'
        # Competitions
        COMPETITION_REGISTERED = 'competition_registered', 'Competition registration confirmed'
        COMPETITION_APPROVED = 'competition_approved', 'Competition registration approved'
        COMPETITION_REJECTED = 'competition_rejected', 'Competition registration rejected'
        COMPETITION_WAITLISTED = 'competition_waitlisted', 'Competition application waitlisted'
        COMPETITION_REMINDER = 'competition_reminder', 'Competition reminder'
        TEAM_INVITATION = 'team_invitation', 'Competition team invitation'
        COMP_SUBMISSION_RECEIVED = 'submission_received', 'Competition submission received'
        COMP_SUBMISSION_REVIEWED = 'submission_reviewed', 'Competition submission reviewed'
        COMP_RESULTS_PUBLISHED = 'results_published', 'Competition results published'
        # Credentials & platform
        CERTIFICATE_ISSUED = 'certificate_issued', 'Certificate issued'
        ANNOUNCEMENT = 'announcement', 'Platform announcement'

    class Category(models.TextChoices):
        LEARNING = 'learning', 'Learning'
        COMPETITION = 'competition', 'Competitions'
        ACCOUNT = 'account', 'Account'
        ANNOUNCEMENT = 'announcement', 'Announcements'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    type = models.CharField(max_length=40, choices=Type.choices)
    category = models.CharField(
        max_length=20, choices=Category.choices, default=Category.LEARNING,
        help_text='Notification center filter group; derived from the type',
    )
    title = models.CharField(max_length=200)
    body = models.TextField(blank=True, default='')
    link = models.CharField(
        max_length=300, blank=True, default='',
        help_text='In-app path the notification opens, e.g. /achievements'
    )
    related_object_type = models.CharField(
        max_length=50, blank=True, default='',
        help_text='Loose identifier of the backing object, e.g. "competition"',
    )
    related_object_id = models.CharField(
        max_length=64, blank=True, default='',
        help_text='Natural identifier of the backing object (pk, slug or credential id)',
    )
    dedupe_key = models.CharField(
        max_length=150, null=True, blank=True, unique=True,
        help_text=('Event-derived idempotency token; a repeatable code path '
                   'writing the same key is a no-op'),
    )
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f"{self.user.username}: {self.title}"

    @property
    def is_unread(self) -> bool:
        return self.read_at is None

    @property
    def is_read(self) -> bool:
        return self.read_at is not None

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'read_at'], name='notif_user_read'),
            models.Index(
                fields=['user', 'read_at', 'category'], name='notif_user_read_cat',
            ),
            models.Index(fields=['user', '-created_at'], name='notif_user_created'),
        ]


class Announcement(models.Model):
    """Platform announcement authored and managed by administrators.

    ``status`` is the authoritative publishing state (draft → published ⇄
    unpublished → archived); ``is_published`` is kept in sync on save so the
    many existing ``is_published`` filters across the codebase stay honest.
    """

    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        PUBLISHED = 'published', 'Published'
        UNPUBLISHED = 'unpublished', 'Unpublished'
        ARCHIVED = 'archived', 'Archived'

    class Category(models.TextChoices):
        GENERAL = 'general', 'General'
        PLATFORM_UPDATES = 'platform_updates', 'Platform Updates'
        HACKATHONS = 'hackathons', 'Hackathons'
        COURSES = 'courses', 'Courses'
        COMPETITIONS = 'competitions', 'Competitions'
        MAINTENANCE = 'maintenance', 'Maintenance'
        IMPORTANT = 'important', 'Important Notices'

    class Priority(models.TextChoices):
        NORMAL = 'normal', 'Normal'
        IMPORTANT = 'important', 'Important'
        URGENT = 'urgent', 'Urgent'

    AUDIENCE_CHOICES = [
        ('all', 'Everyone'),
        ('students', 'Students'),
        ('instructors', 'Instructors'),
        ('admins', 'Administrators'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True, null=True)
    body = models.TextField()
    short_description = models.CharField(max_length=400, blank=True, default='')
    cover_image = models.ImageField(upload_to='announcement-covers/%Y/', blank=True, default='')
    category = models.CharField(max_length=30, choices=Category.choices, default=Category.GENERAL)
    priority = models.CharField(max_length=10, choices=Priority.choices, default=Priority.NORMAL)
    target_audience = models.CharField(max_length=50, default='all')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    is_published = models.BooleanField(default=False)
    scheduled_at = models.DateTimeField(null=True, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='created_announcements',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title) or 'announcement'
            candidate, suffix = base, 1
            while Announcement.objects.filter(slug=candidate).exclude(pk=self.pk).exists():
                candidate = f'{base}-{suffix}'
                suffix += 1
            self.slug = candidate[:220]
        # Keep the legacy boolean honest with the authoritative status field.
        self.is_published = self.status == self.Status.PUBLISHED
        update_fields = kwargs.get('update_fields')
        if update_fields is not None:
            # Partial saves must still persist the synced slug/boolean.
            kwargs['update_fields'] = list(
                set(update_fields) | {'slug', 'is_published'}
            )
        super().save(*args, **kwargs)

    @property
    def is_live(self):
        """Publicly visible right now: published, due, and not expired."""
        now = timezone.now()
        if self.status != self.Status.PUBLISHED:
            return False
        if self.scheduled_at and self.scheduled_at > now:
            return False
        if self.expires_at and self.expires_at <= now:
            return False
        return True


class PlatformUpdate(models.Model):
    """A changelog entry describing product improvements and new features.

    Distinct from :class:`Announcement` (time-sensitive communications):
    updates are the permanent, chronological record of what changed on the
    platform and are rendered on the public Updates/Changelog page.
    """

    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        PUBLISHED = 'published', 'Published'
        UNPUBLISHED = 'unpublished', 'Unpublished'
        ARCHIVED = 'archived', 'Archived'

    class Category(models.TextChoices):
        NEW_FEATURE = 'feature', 'New Feature'
        COURSE = 'course', 'Courses & Tracks'
        IMPROVEMENT = 'improvement', 'Improvement'
        BUG_FIX = 'bug_fix', 'Bug Fix'
        PERFORMANCE = 'performance', 'Performance'
        CERTIFICATE = 'certificate', 'Certificates'
        OTHER = 'other', 'Other'

    AUDIENCE_CHOICES = [
        ('all', 'Everyone'),
        ('students', 'Students'),
        ('instructors', 'Instructors'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True, null=True)
    version = models.CharField(max_length=40, blank=True, default='')
    category = models.CharField(max_length=20, choices=Category.choices, default=Category.NEW_FEATURE)
    summary = models.CharField(max_length=500, blank=True, default='')
    content = models.TextField()
    change_list = models.JSONField(default=list, blank=True, help_text='Detailed change bullets')
    cover_image = models.ImageField(upload_to='update-covers/%Y/', blank=True, default='')
    target_audience = models.CharField(max_length=20, choices=AUDIENCE_CHOICES, default='all')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    published_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='created_platform_updates',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-published_at', '-created_at']
        verbose_name_plural = 'platform updates'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title) or 'update'
            candidate, suffix = base, 1
            while PlatformUpdate.objects.filter(slug=candidate).exclude(pk=self.pk).exists():
                candidate = f'{base}-{suffix}'
                suffix += 1
            self.slug = candidate[:220]
        update_fields = kwargs.get('update_fields')
        if update_fields is not None and 'slug' not in update_fields:
            kwargs['update_fields'] = list(set(update_fields) | {'slug'})
        super().save(*args, **kwargs)


class EmailCampaign(models.Model):
    """One admin-composed bulk email run, tracked independently of publishing.

    Publishing content and emailing it are deliberately separate actions:
    a campaign is only created when an administrator explicitly chooses to
    email an audience, and ``status`` reflects the real transport outcome —
    ``sent`` means the SMTP backend accepted the messages, never merely that
    the campaign was queued.
    """

    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        QUEUED = 'queued', 'Queued'
        SENDING = 'sending', 'Sending'
        SENT = 'sent', 'Sent'
        PARTIAL = 'partial', 'Partially sent'
        FAILED = 'failed', 'Failed'

    class Audience(models.TextChoices):
        ALL = 'all', 'All registered users'
        STUDENTS = 'students', 'Students'
        INSTRUCTORS = 'instructors', 'Instructors'
        ADMINS = 'admins', 'Administrators'
        SPECIFIC = 'specific', 'Selected recipients'
        COMP_PARTICIPANTS = 'comp_participants', 'Hackathon participants'
        COMP_APPROVED = 'comp_approved', 'Approved hackathon applicants'
        COMP_PENDING = 'comp_pending', 'Pending hackathon applicants'
        COMP_WAITLISTED = 'comp_waitlisted', 'Waitlisted hackathon applicants'

    class Template(models.TextChoices):
        GENERAL = 'general', 'General announcement'
        NOTICE = 'notice', 'Important platform notice'
        UPDATE = 'platform_update', 'Platform update'
        COURSE = 'new_course', 'New course announcement'

    name = models.CharField(max_length=200, help_text='Internal campaign name')
    subject = models.CharField(max_length=200)
    heading = models.CharField(max_length=200, blank=True, default='')
    body = models.TextField(help_text='Message body (plain text; rendered into the branded template)')
    template = models.CharField(max_length=30, choices=Template.choices, default=Template.GENERAL)
    banner_image = models.ImageField(upload_to='campaign-banners/%Y/', blank=True, default='')
    cta_label = models.CharField(max_length=80, blank=True, default='')
    cta_url = models.URLField(blank=True, default='')
    audience = models.CharField(max_length=30, choices=Audience.choices, default=Audience.ALL)
    selected_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL, blank=True, related_name='selected_in_campaigns',
        help_text='Only used by the “selected recipients” audience',
    )
    custom_emails = models.JSONField(
        default=list, blank=True,
        help_text='External addresses (people without a Code Yaar account) for the selected-recipients audience',
    )
    cc_emails = models.JSONField(default=list, blank=True)
    bcc_emails = models.JSONField(default=list, blank=True)
    body_html = models.TextField(
        blank=True, default='',
        help_text='Rich-text (HTML) body for the free-form composer; sanitized server-side and personalized per recipient',
    )
    plain_text_alternative = models.TextField(
        blank=True, default='',
        help_text='Optional plain-text override; derived from the HTML body when left empty',
    )
    competition = models.ForeignKey(
        'Competition', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='email_campaigns',
        help_text='Required for hackathon-participant audiences',
    )
    related_announcement = models.ForeignKey(
        Announcement, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='email_campaigns',
    )
    related_update = models.ForeignKey(
        'PlatformUpdate', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='email_campaigns',
    )
    essential = models.BooleanField(
        default=False,
        help_text='Essential mail bypasses marketing preferences and the unsubscribe list',
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    recipient_count = models.PositiveIntegerField(default=0)
    sent_count = models.PositiveIntegerField(default=0)
    failed_count = models.PositiveIntegerField(default=0)
    skipped_count = models.PositiveIntegerField(default=0)
    sent_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='created_email_campaigns',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name


#: The starter set of template categories shown in the library's filter bar.
#: Administrators may type a new category name when creating a template; the
#: full list offered by the API is these defaults plus every category already
#: in use (see ``EmailTemplate.used_categories``). No extra table is needed to
#: hold them: a category persists as long as a template uses it.
EMAIL_TEMPLATE_CATEGORIES = [
    'Welcome & Onboarding',
    'Account Verification',
    'Password Reset',
    'Student Communications',
    'Course Enrollment',
    'Course Completion',
    'Certificates & Achievements',
    'Internship Opportunities',
    'Hackathons & Competitions',
    'Ambassador Programs',
    'Team Communications',
    'Partnership & Collaboration',
    'Important Announcements',
    'Custom Templates',
]


class EmailTemplate(models.Model):
    """A reusable, saved starting point for an admin-composed email.

    Deliberately *separate* from :class:`EmailCampaign`: a template stores no
    audience, recipients or delivery state — only the authored content
    (subject, heading, body, CTA, footer) with its ``{{variables}}`` left
    unrendered. Choosing a template on the composer copies this content into
    a fresh draft; the saved template itself is never mutated by sending, and
    personalization still happens per recipient at fan-out time exactly as for
    a hand-written email. This keeps the whole existing campaign/sending
    pipeline untouched.
    """

    name = models.CharField(max_length=200)
    category = models.CharField(
        max_length=80, default='Custom Templates',
        help_text='One of the preset categories, or a new category name typed by an administrator',
    )
    description = models.TextField(
        blank=True, default='', help_text='Internal note describing when to use this template',
    )
    subject = models.CharField(max_length=200)
    heading = models.CharField(max_length=200, blank=True, default='')
    preview_text = models.CharField(
        max_length=300, blank=True, default='',
        help_text='Short preheader shown in inbox previews before the body',
    )
    body_html = models.TextField(
        help_text='Rich-text (HTML) body; sanitized server-side and personalized per recipient when used',
    )
    plain_text = models.TextField(
        blank=True, default='',
        help_text='Optional plain-text body; derived from the HTML body when left empty',
    )
    cta_label = models.CharField(max_length=80, blank=True, default='')
    cta_url = models.CharField(max_length=500, blank=True, default='')
    footer_content = models.TextField(
        blank=True, default='',
        help_text='Optional closing line appended to the body when the template is used',
    )
    theme = models.CharField(
        max_length=40, default='emerald-signature', blank=True,
        help_text='Visual theme applied when rendering this template',
    )
    is_favorite = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='created_email_templates',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_favorite', '-updated_at']
        verbose_name = 'email template'
        verbose_name_plural = 'email templates'

    def __str__(self):
        return f'{self.name} ({self.category})'

    @classmethod
    def used_categories(cls):
        """Preset categories plus every distinct category already saved."""
        seen = list(EMAIL_TEMPLATE_CATEGORIES)
        for value in cls.objects.exclude(category='').values_list('category', flat=True).distinct():
            if value not in seen:
                seen.append(value)
        return seen


class EmailCampaignRecipient(models.Model):
    """Per-recipient delivery record for one campaign.

    The address is snapshotted at fan-out time so the history stays truthful
    even if the user later changes it; API responses must never expose the
    raw address to requests that are not super-admin.
    """

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        SENT = 'sent', 'Sent'
        RENDER_ONLY = 'render_only', 'Rendered (no real transport)'
        SKIPPED = 'skipped', 'Skipped (preference / unsubscribed)'
        FAILED = 'failed', 'Failed'

    campaign = models.ForeignKey(
        EmailCampaign, on_delete=models.CASCADE, related_name='recipients',
    )
    # Null for external custom addresses: people mailed without a Code Yaar account.
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True,
        related_name='campaign_emails',
    )
    email = models.CharField(max_length=254)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    error = models.CharField(max_length=500, blank=True, default='')
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        constraints = [
            # Dedupe on the snapshotted address itself: one copy per person per
            # campaign, whether the recipient is a registered user or an
            # external address (a NULL user would slip past a (campaign, user)
            # constraint on both SQLite and Postgres).
            models.UniqueConstraint(fields=['campaign', 'email'], name='unique_campaign_recipient'),
        ]
        indexes = [
            models.Index(fields=['campaign', 'status']),
        ]

    def __str__(self):
        return f'{self.campaign_id}:{self.status}'


class EmailTheme(models.Model):
    """A visual theme for transactional/composed emails."""

    slug = models.SlugField(max_length=40, unique=True)
    name = models.CharField(max_length=80)
    description = models.TextField(blank=True, default='')
    best_for = models.TextField(blank=True, default='')
    primary_color = models.CharField(max_length=20, default='#073D32')
    accent_color = models.CharField(max_length=20, default='#087F68')
    highlight_color = models.CharField(max_length=20, default='#A9EDCC')
    background_color = models.CharField(max_length=20, default='#FFFFFF')
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class EmailAutomationRule(models.Model):
    """Configuration for an event-driven automated email."""

    trigger = models.CharField(max_length=80, unique=True)
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True, default='')
    enabled = models.BooleanField(default=True)
    template = models.ForeignKey(
        'EmailTemplate', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='automation_rules',
    )
    theme = models.CharField(max_length=40, default='emerald-signature', blank=True)
    subject_override = models.CharField(max_length=200, blank=True, default='')
    delay_minutes = models.PositiveIntegerField(default=0)
    recipient_group = models.CharField(max_length=80, default='trigger_recipient')
    last_run_at = models.DateTimeField(null=True, blank=True)
    success_count = models.PositiveIntegerField(default=0)
    failure_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.trigger})'


class PlatformSetting(models.Model):
    key = models.CharField(max_length=100, unique=True)
    value = models.JSONField(default=dict)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.key


class MaintenanceSettings(models.Model):
    """The singleton configuration for platform maintenance mode."""

    is_enabled = models.BooleanField(default=False)
    maintenance_message = models.TextField(
        blank=True,
        default='',
        help_text='Message shown to visitors while maintenance mode is enabled.',
    )
    estimated_return_time = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    SINGLETON_PK = 1

    #: Where the short-lived read snapshot lives. The maintenance middleware
    #: and the public status endpoint run on every request, and the hosted
    #: database makes even a single-row SELECT a visible round trip; the
    #: snapshot collapses those to one read per TTL window, and `save()`
    #: invalidates it so a toggle is reflected immediately.
    CACHE_KEY = 'maintenance_settings_snapshot'
    CACHE_TTL_SECONDS = 15

    class Meta:
        verbose_name = 'Maintenance settings'
        verbose_name_plural = 'Maintenance settings'
        constraints = [
            models.CheckConstraint(
                condition=models.Q(id=1),
                name='maintenance_settings_singleton',
            ),
        ]

    def save(self, *args, **kwargs):
        self.pk = self.SINGLETON_PK
        super().save(*args, **kwargs)
        from django.core.cache import cache
        cache.delete(self.CACHE_KEY)

    @classmethod
    def get_solo(cls):
        settings, _ = cls.objects.get_or_create(pk=cls.SINGLETON_PK)
        return settings

    @classmethod
    def snapshot(cls):
        """Plain-data view of the singleton, cached for CACHE_TTL_SECONDS.

        Returns ``{is_enabled, message, estimated_return_time}`` where the
        time is an aware datetime or None. Read-only callers (middleware,
        status endpoint) use this instead of touching the database per
        request; writes invalidate the snapshot in `save()`.
        """
        from django.core.cache import cache
        cached = cache.get(cls.CACHE_KEY)
        if cached is not None:
            return cached
        row = cls.objects.filter(pk=cls.SINGLETON_PK).values(
            'is_enabled', 'maintenance_message', 'estimated_return_time',
        ).first()
        snapshot = {
            'is_enabled': bool(row and row['is_enabled']),
            'message': (row['maintenance_message'] if row else '') or '',
            'estimated_return_time': row['estimated_return_time'] if row else None,
        }
        cache.set(cls.CACHE_KEY, snapshot, cls.CACHE_TTL_SECONDS)
        return snapshot

    def __str__(self):
        return 'Maintenance mode'


class NotificationEmailLog(models.Model):
    """Delivery ledger for every event-triggered email, keyed for idempotency.

    ``email_key`` is an event-derived string (e.g. ``comp-reg:42``). The first
    claim creates the row inside the caller's transaction; the send itself
    only runs after that transaction commits. A ``sent`` or ``render_only``
    row turns later replays of the same event into no-ops, so command loops
    and concurrent requests can never mail the same event twice. Failures
    store an abbreviated transport reason — never credentials or bodies —
    which keeps retries possible and silent failures impossible.
    """

    class Status(models.TextChoices):
        QUEUED = 'queued', 'Queued for delivery after commit'
        SENT = 'sent', 'Sent'
        RENDER_ONLY = 'render_only', 'Rendered locally (no real transport configured)'
        FAILED = 'failed', 'Failed'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notification_email_log',
    )
    notification = models.ForeignKey(
        UserNotification,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='email_log',
    )
    email_key = models.CharField(max_length=180, unique=True)
    kind = models.CharField(
        max_length=60,
        help_text="Email preference kind, e.g. 'email_learning' or 'security'",
    )
    category = models.CharField(max_length=60, blank=True, default='')
    subject = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.QUEUED)
    error = models.CharField(max_length=500, blank=True, default='')
    attempted_at = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.email_key}: {self.status}"

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at'], name='notif_email_user_created'),
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


class Portfolio(models.Model):
    """A student's public developer portfolio.

    Portfolio-specific identity and publish state live here, deliberately
    separate from ``UserProfile``: a learner's account may be public while
    their portfolio stays unpublished, and vice versa. A public view is only
    served when ``is_published`` is true AND the owner's ``UserProfile`` is
    public (enforced at the API edge).
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='portfolio',
    )
    headline = models.CharField(
        max_length=160, blank=True, default='',
        help_text='Short professional introduction shown under the name'
    )
    about = models.TextField(
        blank=True, default='',
        help_text='A concise self-written introduction (never auto-generated)'
    )
    interests = models.JSONField(
        default=list, blank=True,
        help_text='Areas of interest as a list of short strings'
    )
    currently_learning = models.CharField(max_length=200, blank=True, default='')
    enjoys_building = models.CharField(max_length=200, blank=True, default='')

    is_published = models.BooleanField(
        default=False,
        help_text='Publish the portfolio so it is viewable at /profile/<username>/portfolio'
    )
    # ── Section visibility (what a public visitor may see) ──
    show_skills = models.BooleanField(default=True)
    show_achievements = models.BooleanField(default=True)
    show_learning_progress = models.BooleanField(default=True)
    show_social_links = models.BooleanField(default=True)
    show_location = models.BooleanField(default=True)
    show_contact = models.BooleanField(
        default=False,
        help_text='Offer a contact affordance; the email itself is never exposed'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def owner_can_contact(self) -> bool:
        return self.show_contact

    def __str__(self):
        return f"{self.user.username}'s portfolio"

    class Meta:
        ordering = ['-updated_at']


class Follow(models.Model):
    """A directed relationship between two learner accounts."""

    follower = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='following_relationships',
    )
    following = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='follower_relationships',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.follower.username} follows {self.following.username}'

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['follower', 'following'],
                name='unique_user_follow',
            ),
        ]
        ordering = ['-created_at']


class StudentProject(models.Model):
    """A project a learner has actually built, shown on their portfolio.

    Distinct from the curriculum ``Project`` model, which is a platform-defined
    learning template. A ``StudentProject`` is owned by a learner, carries the
    narrative behind the work (problem, decisions, challenges, lessons) and
    links out to real repositories and demos. Nothing here is fabricated: a
    demo/repo link is only shown when the owner supplied it.
    """
    CATEGORY_CHOICES = [
        ('web_development', 'Web Development'),
        ('ai', 'Artificial Intelligence'),
        ('machine_learning', 'Machine Learning'),
        ('backend', 'Backend Development'),
        ('frontend', 'Frontend Development'),
        ('mobile', 'Mobile Applications'),
        ('developer_tools', 'Developer Tools'),
        ('automation', 'Automation'),
        ('data_science', 'Data Science'),
        ('other', 'Other'),
    ]
    STATUS_CHOICES = [
        ('in_progress', 'In progress'),
        ('completed', 'Completed'),
        ('archived', 'Archived'),
    ]
    VISIBILITY_CHOICES = [
        ('public', 'Public'),
        ('private', 'Private'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='portfolio_projects',
    )
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220)
    short_description = models.CharField(max_length=300)
    overview = models.TextField(blank=True, default='', help_text='Longer explanation of what/why')
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='other')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='completed')
    cover_image = models.ImageField(
        upload_to='portfolio-covers/', null=True, blank=True,
        help_text='Cover image for the project card'
    )
    github_url = models.URLField(blank=True, default='')
    live_demo_url = models.URLField(blank=True, default='')
    docs_url = models.URLField(blank=True, default='')
    problem_statement = models.TextField(blank=True, default='')
    solution = models.TextField(blank=True, default='')
    technical_details = models.TextField(blank=True, default='')
    challenges = models.TextField(blank=True, default='')
    lessons_learned = models.TextField(blank=True, default='')
    contributions = models.TextField(blank=True, default='', help_text='The owner\'s role/contributions')
    technologies = models.JSONField(
        default=list, blank=True,
        help_text='List of technology name strings used in the project'
    )
    start_date = models.DateField(null=True, blank=True)
    completion_date = models.DateField(null=True, blank=True)
    featured = models.BooleanField(default=False)
    display_order = models.PositiveIntegerField(default=0)
    visibility = models.CharField(
        max_length=10, choices=VISIBILITY_CHOICES, default='public',
        help_text='Private projects never appear through public endpoints'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.title}"

    class Meta:
        ordering = ['display_order', '-updated_at']
        unique_together = ['user', 'slug']
        indexes = [
            models.Index(fields=['user', 'featured']),
            models.Index(fields=['user', 'visibility']),
        ]


class ProjectImage(models.Model):
    """Additional screenshots for a ``StudentProject``."""
    project = models.ForeignKey(
        StudentProject,
        on_delete=models.CASCADE,
        related_name='images',
    )
    image = models.ImageField(upload_to='portfolio-project-images/')
    alt_text = models.CharField(max_length=200, blank=True, default='')
    display_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.project.title} image #{self.display_order}"

    class Meta:
        ordering = ['display_order']


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
    learning_objective = models.TextField(
        blank=True,
        default='',
        help_text='What the learner practices by completing this challenge',
    )
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


class Competition(models.Model):
    """A published learner competition managed by an authorized organizer."""

    FORMAT_CHOICES = [('individual', 'Individual'), ('team', 'Team'), ('both', 'Individual or team')]
    DELIVERY_CHOICES = [('online', 'Online'), ('offline', 'Offline'), ('hybrid', 'Hybrid')]
    DIFFICULTY_CHOICES = [('beginner', 'Beginner'), ('intermediate', 'Intermediate'), ('advanced', 'Advanced')]

    organizer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='organized_competitions')
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    short_description = models.CharField(max_length=400)
    description = models.TextField()
    banner = models.ImageField(upload_to='competition-banners/%Y/', blank=True, default='')
    category = models.CharField(max_length=80)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='beginner')
    format = models.CharField(max_length=20, choices=FORMAT_CHOICES, default='individual')
    delivery_mode = models.CharField(max_length=20, choices=DELIVERY_CHOICES, default='online')
    location = models.CharField(max_length=250, blank=True, default='')
    registration_start = models.DateTimeField()
    registration_deadline = models.DateTimeField()
    competition_start = models.DateTimeField()
    competition_end = models.DateTimeField()
    submission_deadline = models.DateTimeField()
    judging_end = models.DateTimeField(null=True, blank=True)
    results_announcement = models.DateTimeField(null=True, blank=True)
    participant_limit = models.PositiveIntegerField(null=True, blank=True)
    minimum_team_size = models.PositiveIntegerField(default=1)
    maximum_team_size = models.PositiveIntegerField(default=1)
    eligibility_rules = models.JSONField(default=list, blank=True)
    competition_rules = models.JSONField(default=list, blank=True)
    problem_statement = models.TextField(blank=True, default='')
    submission_configuration = models.JSONField(default=dict, blank=True)
    prize_information = models.TextField(blank=True, default='')
    # ── Hackathon-management extensions (registration, guidance, contact) ──
    tags = models.JSONField(default=list, blank=True)
    host_name = models.CharField(max_length=200, blank=True, default='', help_text='Display name of the organizing body')
    time_zone = models.CharField(max_length=60, default='UTC')
    registration_fee = models.DecimalField(max_digits=8, decimal_places=2, default=0, help_text='0 means free participation')
    participation_instructions = models.TextField(blank=True, default='')
    evaluation_criteria = models.JSONField(default=list, blank=True)
    submission_requirements = models.TextField(blank=True, default='')
    contact_information = models.CharField(max_length=250, blank=True, default='')
    external_resources = models.JSONField(default=list, blank=True, help_text='List of {title, url} links')
    is_archived = models.BooleanField(default=False)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['is_published', 'registration_deadline'])]

    def __str__(self):
        return self.title

    @property
    def status(self):
        if self.is_archived:
            return 'archived'
        if not self.is_published:
            return 'draft'
        now = timezone.now()
        if now < self.registration_start:
            return 'upcoming'
        if now <= self.registration_deadline:
            if (self.registration_deadline - now).total_seconds() <= 72 * 3600:
                return 'registration_closing_soon'
            return 'registration_open'
        if now < self.competition_start:
            return 'registration_closed'
        if now <= self.submission_deadline:
            return 'submission_open' if now > self.competition_end else 'ongoing'
        if self.judging_end and now <= self.judging_end:
            return 'judging'
        return 'completed'


class CompetitionRegistration(models.Model):
    STATUS_CHOICES = [
        ('registered', 'Registered'), ('pending', 'Pending Approval'),
        ('approved', 'Approved'), ('rejected', 'Rejected'),
        ('waitlisted', 'Waitlisted'),
        ('withdrawn', 'Withdrawn'), ('disqualified', 'Disqualified'),
    ]
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE, related_name='registrations')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='competition_registrations')
    team = models.ForeignKey('CompetitionTeam', on_delete=models.SET_NULL, null=True, blank=True, related_name='registrations')
    registration_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='registered')
    registration_data = models.JSONField(default=dict, blank=True)
    reference = models.CharField(max_length=40, unique=True, blank=True, editable=False)
    rules_accepted_at = models.DateTimeField()
    registered_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['competition', 'user'], name='unique_competition_registration'),
        ]
        ordering = ['-registered_at']

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = f'REG-{uuid.uuid4().hex[:10].upper()}'
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.reference} ({self.registration_status})'


class RegistrationFormField(models.Model):
    """One field of a per-hackathon registration form.

    The default field set is seeded automatically for every competition so
    administrators start from the standard questions and customize from
    there; nothing about a registration form is hardcoded in the frontend.
    """

    class FieldType(models.TextChoices):
        SHORT_TEXT = 'short_text', 'Short text'
        LONG_TEXT = 'long_text', 'Long text'
        EMAIL = 'email', 'Email'
        PHONE = 'phone', 'Phone'
        NUMBER = 'number', 'Number'
        DROPDOWN = 'dropdown', 'Dropdown'
        MULTIPLE_CHOICE = 'multiple_choice', 'Multiple choice'
        CHECKBOXES = 'checkboxes', 'Checkboxes'
        URL = 'url', 'URL'
        DATE = 'date', 'Date'

    competition = models.ForeignKey(
        Competition, on_delete=models.CASCADE, related_name='form_fields',
    )
    label = models.CharField(max_length=200)
    field_key = models.SlugField(max_length=80)
    field_type = models.CharField(max_length=20, choices=FieldType.choices, default=FieldType.SHORT_TEXT)
    description = models.CharField(max_length=400, blank=True, default='')
    placeholder = models.CharField(max_length=200, blank=True, default='')
    required = models.BooleanField(default=False)
    options = models.JSONField(default=list, blank=True, help_text='Choices for dropdown/multiple_choice/checkboxes')
    validation = models.JSONField(default=dict, blank=True, help_text='Optional min/max/min_length/max_length bounds')
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False, help_text='Part of the auto-seeded default field set')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['competition', 'order', 'id']
        constraints = [
            models.UniqueConstraint(fields=['competition', 'field_key'], name='unique_competition_form_field'),
        ]
        indexes = [models.Index(fields=['competition', 'is_active', 'order'])]

    def __str__(self):
        return f'{self.competition_id}:{self.label}'


#: The fifteen default questions seeded for every new hackathon form.
FormFieldType = RegistrationFormField.FieldType
DEFAULT_REGISTRATION_FIELDS = [
    ('Full name', 'full_name', FormFieldType.SHORT_TEXT, True),
    ('Email address', 'email_address', FormFieldType.EMAIL, True),
    ('Username', 'username', FormFieldType.SHORT_TEXT, True),
    ('Phone number', 'phone_number', FormFieldType.PHONE, False),
    ('Educational institution', 'institution', FormFieldType.SHORT_TEXT, True),
    ('Current education level', 'education_level', FormFieldType.DROPDOWN, True),
    ('City', 'city', FormFieldType.SHORT_TEXT, True),
    ('Country', 'country', FormFieldType.SHORT_TEXT, True),
    ('Programming experience', 'programming_experience', FormFieldType.DROPDOWN, True),
    ('Skills and technologies', 'skills', FormFieldType.LONG_TEXT, False),
    ('GitHub profile URL', 'github_url', FormFieldType.URL, False),
    ('LinkedIn profile URL', 'linkedin_url', FormFieldType.URL, False),
    ('Portfolio URL', 'portfolio_url', FormFieldType.URL, False),
    ('Project idea or motivation', 'project_idea', FormFieldType.LONG_TEXT, False),
    ('Participation type', 'participation_type', FormFieldType.MULTIPLE_CHOICE, True),
]


def seed_default_registration_fields(competition):
    """Create the default registration fields for one competition.

    Idempotent: existing field keys are left untouched so re-running after a
    manual customization never duplicates or overwrites admin edits.
    """
    existing = set(
        RegistrationFormField.objects.filter(competition=competition).values_list('field_key', flat=True)
    )
    defaults = {
        'education_level': ['Class 9-10', 'Class 11-12', 'Diploma / Associate', 'Bachelor', 'Master or higher', 'Self-taught'],
        'programming_experience': ['Complete beginner', 'Some basics', 'Intermediate', 'Advanced'],
        'participation_type': ['Individual', 'Team'],
    }
    created = []
    for order, (label, key, ftype, required) in enumerate(DEFAULT_REGISTRATION_FIELDS, 1):
        if key in existing:
            continue
        created.append(RegistrationFormField.objects.create(
            competition=competition,
            label=label,
            field_key=key,
            field_type=ftype,
            required=required,
            options=defaults.get(key, []),
            order=order,
            is_default=True,
        ))
    return created


class CompetitionTeam(models.Model):
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE, related_name='teams')
    name = models.CharField(max_length=120)
    leader = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='competition_teams_led')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['competition', 'name'], name='unique_competition_team_name'),
        ]


class CompetitionTeamMember(models.Model):
    INVITATION_CHOICES = [('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')]
    team = models.ForeignKey(CompetitionTeam, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='competition_team_memberships')
    invitation_status = models.CharField(max_length=20, choices=INVITATION_CHOICES, default='pending')
    joined_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['team', 'user'], name='unique_team_member'),
        ]


class CompetitionSubmission(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'), ('submitted', 'Submitted'), ('under_review', 'Under Review'),
        ('accepted', 'Accepted'), ('rejected', 'Rejected'), ('needs_revision', 'Needs Revision'),
    ]
    registration = models.OneToOneField(CompetitionRegistration, on_delete=models.CASCADE, related_name='submission')
    project_title = models.CharField(max_length=200, blank=True, default='')
    description = models.TextField(blank=True, default='')
    github_url = models.URLField(blank=True, default='')
    demo_url = models.URLField(blank=True, default='')
    additional_data = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    organizer_feedback = models.TextField(blank=True, default='')
    submitted_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']


class CompetitionResult(models.Model):
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE, related_name='results')
    registration = models.OneToOneField(CompetitionRegistration, on_delete=models.CASCADE, related_name='result')
    rank = models.PositiveIntegerField()
    final_score = models.DecimalField(max_digits=7, decimal_places=2)
    award = models.CharField(max_length=120, blank=True, default='')
    is_published = models.BooleanField(default=False)

    class Meta:
        ordering = ['rank', '-final_score']
        constraints = [
            models.UniqueConstraint(fields=['competition', 'rank'], name='unique_competition_rank'),
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


class AdminActionLog(models.Model):
    """Append-only record of consequential administrator actions.

    ``AuthenticationAuditLog`` only covers sign-in traffic, so the admin platform
    needs its own trail for the things that actually change learner data:
    publishing a course, overriding the publish checklist, promoting or deactivating
    a competition application, launching a campaign, editing roles. Rows are written
    through :func:`record_admin_action` and are guarded against edit and delete here
    so the history stays trustworthy even against an administrator with database
    access through the app.
    """

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='admin_actions',
    )
    actor_role = models.CharField(
        max_length=40, blank=True, default='',
        help_text='Effective role captured at the time of the action, since roles change later'
    )
    action = models.CharField(max_length=60, help_text='e.g. course.publish, lesson.bulk_publish')
    target_type = models.CharField(max_length=60, blank=True, default='')
    target_id = models.CharField(max_length=60, blank=True, default='')
    target_label = models.CharField(max_length=250, blank=True, default='')
    detail = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['action', '-created_at'], name='adminlog_action_created'),
            models.Index(fields=['actor', '-created_at'], name='adminlog_actor_created'),
        ]

    def __str__(self):
        return f"{self.action} {self.target_type}#{self.target_id} @ {self.created_at:%Y-%m-%d %H:%M}"

    def save(self, *args, **kwargs):
        if self.pk is not None:
            raise IntegrityError('AdminActionLog rows are append-only and cannot be modified.')
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise IntegrityError('AdminActionLog rows are append-only and cannot be deleted.')


def record_admin_action(actor, action, *, obj=None, label='', detail=None, request=None):
    """Write one audit row, tolerating a missing actor (management commands).

    Audit failure must never mask the operation it is recording, so callers keep
    working even if this raises; the log is written outside the caller's transaction
    intent on purpose.
    """
    ip = None
    if request is not None:
        x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR', '')
        ip = (x_forwarded.split(',')[0].strip() if x_forwarded
              else request.META.get('REMOTE_ADDR'))
    # Imported lazily: ``learning.services.auth`` pulls in this module, so a
    # top-level import would close a circular dependency at app-load time.
    from .services.auth import user_role
    actor_id = actor.pk if getattr(actor, 'pk', None) is not None else None
    return AdminActionLog.objects.create(
        actor_id=actor_id,
        actor_role=(user_role(actor) if actor_id is not None else 'system'),
        action=action,
        target_type=obj.__class__.__name__ if obj is not None else '',
        target_id=str(getattr(obj, 'pk', '') or ''),
        target_label=label or (str(obj)[:250] if obj is not None else ''),
        detail=detail or {},
        ip_address=ip,
    )
