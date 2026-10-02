from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType


class UserProfile(models.Model):
    """Extended user profile with learning-specific fields."""
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('mentor', 'Mentor'),
        ('admin', 'Admin'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    avatar = models.URLField(blank=True, default='')
    bio = models.TextField(blank=True, default='')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    xp_points = models.PositiveIntegerField(default=0)
    streak_days = models.PositiveIntegerField(default=0)
    level = models.PositiveIntegerField(default=1)
    last_active_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s profile"

    class Meta:
        ordering = ['-xp_points']


class CareerTrack(models.Model):
    """A learning track/career path (e.g., Full Stack, Backend, Frontend, DevOps)."""
    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]

    slug = models.SlugField(max_length=100, unique=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    icon = models.CharField(max_length=50, blank=True, default='')
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='beginner')
    estimated_hours = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

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
    ]

    slug = models.SlugField(max_length=100, unique=True)
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=300, blank=True, default='')
    description = models.TextField()
    thumbnail = models.URLField(blank=True, default='')
    track = models.ForeignKey(
        CareerTrack,
        on_delete=models.CASCADE,
        related_name='courses'
    )
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='beginner')
    language = models.CharField(max_length=20, choices=LANGUAGE_CHOICES, default='python')
    estimated_hours = models.PositiveIntegerField(default=0)
    total_xp = models.PositiveIntegerField(default=0)
    instructor = models.CharField(max_length=200, blank=True, default='')
    prerequisites = models.TextField(blank=True, default='None')
    learning_objectives = models.JSONField(default=list, blank=True, help_text='List of skills learned')
    is_free = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    @property
    def chapter_count(self):
        return self.chapters.count()

    @property
    def lesson_count(self):
        return Lesson.objects.filter(chapter__course=self).count()

    @property
    def exercise_count(self):
        return Exercise.objects.filter(lesson__chapter__course=self).count()

    class Meta:
        ordering = ['track', 'order', 'title']


class Chapter(models.Model):
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


class Lesson(models.Model):
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


class Exercise(models.Model):
    """An exercise within a lesson. Supports multiple types."""
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


class XPTransaction(models.Model):
    """Tracks all XP earned/spent by a user."""
    ACTION_CHOICES = [
        ('lesson_complete', 'Lesson Complete'),
        ('exercise_complete', 'Exercise Complete'),
        ('chapter_complete', 'Chapter Complete'),
        ('course_complete', 'Course Complete'),
        ('hint_used', 'Hint Used'),
        ('streak_bonus', 'Streak Bonus'),
        ('manual_adjustment', 'Manual Adjustment'),
    ]

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


class Achievement(models.Model):
    """An achievement/badge that can be earned."""
    CATEGORY_CHOICES = [
        ('course', 'Course Completion'),
        ('chapter', 'Chapter Completion'),
        ('streak', 'Streak'),
        ('exercise', 'Exercise Mastery'),
        ('skill', 'Skill'),
        ('special', 'Special'),
    ]

    slug = models.SlugField(max_length=100, unique=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    icon = models.CharField(max_length=50, blank=True, default='')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='special')
    xp_bonus = models.PositiveIntegerField(default=0)
    # Condition for earning (JSON for flexibility)
    condition_type = models.CharField(max_length=100, help_text='e.g., course_complete, streak_7')
    condition_value = models.CharField(max_length=200, blank=True, default='', help_text='e.g., course slug, number')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['category', 'title']


class UserAchievement(models.Model):
    """An achievement earned by a user."""
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

    def __str__(self):
        return f"{self.user.username} earned {self.achievement.title}"

    class Meta:
        unique_together = ['user', 'achievement']
        ordering = ['-earned_at']


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
    """A standalone coding challenge (separate from course exercises)."""
    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]

    slug = models.SlugField(max_length=100, unique=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='beginner')
    topic = models.CharField(max_length=100)
    estimated_minutes = models.PositiveIntegerField(default=0)
    starter_code = models.TextField(blank=True, default='')
    solution_code = models.TextField(blank=True, default='')
    xp_reward = models.PositiveIntegerField(default=50)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"[{self.difficulty}] {self.title}"

    class Meta:
        ordering = ['topic', 'difficulty', 'title']


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
