from django.contrib import admin
from .models import (
    UserProfile, CareerTrack, Course, Chapter, Lesson, Exercise, Hint,
    Resource, Project, ProjectMilestone, Challenge, Enrollment,
    LessonProgress, ExerciseAttempt, XPTransaction, Achievement,
    UserAchievement, Progress, Certification, UserCertification,
    Skill, UserSkill,
)


# ─── Inlines ────────────────────────────────────────────────────────────────

class ChapterInline(admin.TabularInline):
    model = Chapter
    extra = 1
    fields = ['title', 'slug', 'order', 'xp_reward', 'is_active']
    ordering = ['order']
    prepopulated_fields = {'slug': ('title',)}


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1
    fields = ['title', 'slug', 'content_type', 'order', 'xp_reward', 'duration_minutes', 'is_free_preview']
    ordering = ['order']
    prepopulated_fields = {'slug': ('title',)}


class ExerciseInline(admin.TabularInline):
    model = Exercise
    extra = 0
    fields = ['title', 'slug', 'exercise_type', 'difficulty', 'xp_reward', 'order', 'is_active']
    ordering = ['order']
    prepopulated_fields = {'slug': ('title',)}


class HintInline(admin.TabularInline):
    model = Hint
    extra = 1
    fields = ['content', 'order', 'reveals_solution', 'xp_penalty']
    ordering = ['order']


class ProjectMilestoneInline(admin.TabularInline):
    model = ProjectMilestone
    extra = 1
    fields = ['title', 'description', 'order']
    ordering = ['order']


class CourseInline(admin.TabularInline):
    model = Course
    extra = 0
    fields = ['title', 'slug', 'difficulty', 'estimated_hours', 'is_active', 'order']
    ordering = ['order']
    prepopulated_fields = {'slug': ('title',)}


class CertificationInline(admin.TabularInline):
    model = Certification
    extra = 0
    fields = ['title', 'passing_score', 'is_active']


class ResourceInline(admin.TabularInline):
    model = Resource
    extra = 0
    fields = ['title', 'resource_type', 'file_url', 'order', 'is_active']
    ordering = ['order']


# ─── Model Admins ───────────────────────────────────────────────────────────

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'xp_points', 'level', 'streak_days', 'created_at']
    list_filter = ['role', 'level']
    search_fields = ['user__username', 'user__email', 'bio']
    raw_id_fields = ['user']


@admin.register(CareerTrack)
class CareerTrackAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'difficulty', 'estimated_hours', 'is_active', 'order']
    list_filter = ['difficulty', 'is_active']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}
    ordering = ['order']
    inlines = [CourseInline, CertificationInline]


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'track', 'difficulty', 'language', 'estimated_hours', 'total_xp', 'is_published', 'is_active']
    list_filter = ['track', 'difficulty', 'language', 'is_free', 'is_active', 'is_published']
    search_fields = ['title', 'description', 'subtitle']
    prepopulated_fields = {'slug': ('title',)}
    ordering = ['track', 'order']
    inlines = [ChapterInline, ResourceInline]
    fieldsets = (
        (None, {
            'fields': ('track', 'title', 'subtitle', 'slug', 'description', 'thumbnail')
        }),
        ('Configuration', {
            'fields': ('difficulty', 'language', 'estimated_hours', 'total_xp', 'instructor', 'prerequisites')
        }),
        ('Content', {
            'fields': ('learning_objectives', 'is_free', 'is_active', 'is_published', 'order')
        }),
    )


@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'order', 'lesson_count', 'exercise_count', 'xp_reward', 'is_active']
    list_filter = ['course__track', 'course', 'is_active']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}
    ordering = ['course', 'order']
    inlines = [LessonInline]

    def lesson_count(self, obj):
        return obj.lessons.count()

    def exercise_count(self, obj):
        return Exercise.objects.filter(lesson__chapter=obj).count()


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'chapter', 'content_type', 'order', 'xp_reward', 'duration_minutes', 'is_free_preview']
    list_filter = ['content_type', 'is_free_preview', 'chapter__course__track', 'chapter__course']
    search_fields = ['title', 'content_body', 'learning_objective']
    prepopulated_fields = {'slug': ('title',)}
    ordering = ['chapter__course', 'chapter__order', 'order']
    inlines = [ExerciseInline]
    fieldsets = (
        (None, {
            'fields': ('chapter', 'title', 'slug', 'content_type', 'learning_objective')
        }),
        ('Content', {
            'fields': ('content_body', 'video_url', 'video_duration_seconds')
        }),
        ('Configuration', {
            'fields': ('order', 'duration_minutes', 'xp_reward', 'is_free_preview', 'is_active')
        }),
    )


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ['title', 'lesson', 'exercise_type', 'difficulty', 'language', 'xp_reward', 'order', 'is_active']
    list_filter = ['exercise_type', 'difficulty', 'language', 'is_active', 'lesson__chapter__course']
    search_fields = ['title', 'instructions', 'context']
    prepopulated_fields = {'slug': ('title',)}
    ordering = ['lesson__chapter__course', 'lesson__chapter__order', 'lesson__order', 'order']
    inlines = [HintInline]
    fieldsets = (
        (None, {
            'fields': ('lesson', 'title', 'slug', 'exercise_type', 'difficulty', 'language')
        }),
        ('Instructions', {
            'fields': ('instructions', 'context', 'constraints', 'expected_behavior')
        }),
        ('Code', {
            'fields': ('starter_code', 'solution_code', 'expected_output')
        }),
        ('Choices (MCQ/MSQ)', {
            'fields': ('choices',),
            'classes': ('collapse',),
        }),
        ('Validation', {
            'fields': ('test_cases', 'hidden_tests'),
            'classes': ('collapse',),
        }),
        ('Configuration', {
            'fields': ('order', 'xp_reward', 'max_attempts', 'is_active')
        }),
    )


@admin.register(Hint)
class HintAdmin(admin.ModelAdmin):
    list_display = ['exercise', 'order', 'reveals_solution', 'xp_penalty']
    list_filter = ['reveals_solution', 'exercise__lesson__chapter__course']
    search_fields = ['content', 'exercise__title']
    raw_id_fields = ['exercise']


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'resource_type', 'file_name', 'order', 'is_active']
    list_filter = ['resource_type', 'is_active', 'course']
    search_fields = ['title', 'description']
    raw_id_fields = ['course']
    ordering = ['course', 'order']


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'difficulty', 'track', 'estimated_hours', 'is_active']
    list_filter = ['difficulty', 'track', 'is_active']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ProjectMilestoneInline]


@admin.register(Challenge)
class ChallengeAdmin(admin.ModelAdmin):
    list_display = ['title', 'difficulty', 'topic', 'estimated_minutes', 'xp_reward', 'is_active']
    list_filter = ['difficulty', 'topic', 'is_active']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}
    ordering = ['topic', 'difficulty']


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'status', 'progress_percentage', 'enrolled_at', 'last_activity_at']
    list_filter = ['status', 'course__track']
    search_fields = ['user__username', 'course__title']
    raw_id_fields = ['user', 'course', 'last_lesson']
    date_hierarchy = 'enrolled_at'

    def progress_percentage(self, obj):
        return f"{obj.progress_percentage}%"


@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'lesson', 'status', 'time_spent_seconds', 'completed_at', 'updated_at']
    list_filter = ['status', 'lesson__chapter__course']
    search_fields = ['user__username', 'lesson__title']
    raw_id_fields = ['user', 'lesson']
    date_hierarchy = 'updated_at'


@admin.register(ExerciseAttempt)
class ExerciseAttemptAdmin(admin.ModelAdmin):
    list_display = ['user', 'exercise', 'status', 'attempt_number', 'hints_used', 'xp_earned', 'created_at']
    list_filter = ['status', 'exercise__exercise_type', 'exercise__lesson__chapter__course']
    search_fields = ['user__username', 'exercise__title']
    raw_id_fields = ['user', 'exercise']
    date_hierarchy = 'created_at'


@admin.register(XPTransaction)
class XPTransactionAdmin(admin.ModelAdmin):
    list_display = ['user', 'amount', 'action', 'description', 'created_at']
    list_filter = ['action']
    search_fields = ['user__username', 'description']
    raw_id_fields = ['user']
    date_hierarchy = 'created_at'


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'condition_type', 'xp_bonus', 'is_active']
    list_filter = ['category', 'is_active']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}


@admin.register(UserAchievement)
class UserAchievementAdmin(admin.ModelAdmin):
    list_display = ['user', 'achievement', 'earned_at']
    list_filter = ['achievement__category']
    search_fields = ['user__username', 'achievement__title']
    raw_id_fields = ['user', 'achievement']
    date_hierarchy = 'earned_at'


@admin.register(Progress)
class ProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'content_type', 'status', 'score', 'time_spent_minutes', 'updated_at']
    list_filter = ['status', 'content_type']
    search_fields = ['user__username']
    raw_id_fields = ['user']
    date_hierarchy = 'updated_at'


@admin.register(Certification)
class CertificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'track', 'passing_score', 'is_active']
    list_filter = ['track', 'is_active']
    search_fields = ['title', 'description']


@admin.register(UserCertification)
class UserCertificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'certification', 'earned_at', 'credential_id']
    list_filter = ['certification__track']
    search_fields = ['user__username', 'credential_id']
    raw_id_fields = ['user', 'certification']
    date_hierarchy = 'earned_at'


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'icon']
    list_filter = ['category']
    search_fields = ['name']


@admin.register(UserSkill)
class UserSkillAdmin(admin.ModelAdmin):
    list_display = ['user', 'skill', 'proficiency', 'updated_at']
    list_filter = ['proficiency', 'skill__category']
    search_fields = ['user__username', 'skill__name']
    raw_id_fields = ['user', 'skill']
