from django.contrib import admin, messages
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import (
    UserProfile, CareerTrack, Course, Chapter, Lesson, Exercise, Hint,
    Resource, Project, ProjectMilestone, Challenge, Enrollment,
    LessonProgress, ExerciseAttempt, XPTransaction, Achievement,
    UserAchievement, Progress, Certification, UserCertification,
    Skill, UserSkill, EmailVerificationToken, PasswordResetToken,
    AuthenticationAuditLog, PracticalClass, PracticalSubject, Practical,
    PracticalProgress, PracticalBookmark, LearningActivity,
)

User = get_user_model()


# ─── Textbook provenance ────────────────────────────────────────────────
# Chapter, Lesson and Exercise all inherit SourceReference, so the same block
# appears on each. Content editors fill these in from the admin alone — adding
# or correcting a textbook citation needs no code change and no re-deploy.
TEXTBOOK_REFERENCE_FIELDSET = (
    'Textbook source reference', {
        'fields': (
            ('source_type', 'verification_status'),
            ('textbook_board', 'textbook_class'),
            ('textbook_unit', 'textbook_topic'),
            'textbook_pages',
        ),
        'description': (
            'Where this content comes from in the board textbook. "Official" '
            'content cannot be saved until it is marked verified; material that '
            'goes beyond the book must be labelled supplementary or additional '
            'so it is never presented as board syllabus.'
        ),
        'classes': ('collapse',),
    },
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
    """Courses of a track, ordered the way learners should follow them.

    Publishing and sequencing live right here: drag-free reordering via the
    ``order`` field, draft control via ``is_published``.
    """

    model = Course
    extra = 0
    fields = ['order', 'title', 'slug', 'academic_class', 'language',
              'difficulty', 'is_published', 'is_active']
    ordering = ['order', 'title']
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


class PracticalSubjectInline(admin.TabularInline):
    model = PracticalSubject
    extra = 1
    fields = ['title', 'slug', 'order', 'is_active']
    ordering = ['order']
    prepopulated_fields = {'slug': ('title',)}


# ─── Model Admins ───────────────────────────────────────────────────────────

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'role', 'email_verified', 'xp_points', 'level',
        'streak_days', 'institution', 'created_at',
    ]
    list_filter = ['role', 'email_verified', 'education_level', 'level']
    search_fields = [
        'user__username', 'user__email', 'user__first_name', 'user__last_name',
        'institution', 'bio',
    ]
    raw_id_fields = ['user']
    readonly_fields = ['email_verified_at', 'created_at', 'updated_at']
    show_full_result_count = False
    fieldsets = (
        ('Account', {'fields': ('user', 'role', 'email_verified', 'email_verified_at')}),
        ('Student profile', {
            'fields': (
                'avatar', 'bio', 'institution', 'education_level',
                'github_url', 'linkedin_url',
            ),
        }),
        ('Progress', {
            'fields': ('xp_points', 'streak_days', 'level', 'last_active_at'),
        }),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


class StudentProfileInline(admin.StackedInline):
    """Edit the platform profile from the standard user page."""

    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Student profile'
    fields = (
        'role', 'avatar', 'bio', 'institution', 'education_level',
        'github_url', 'linkedin_url', 'email_verified', 'email_verified_at',
        'xp_points', 'streak_days', 'level', 'last_active_at',
    )
    readonly_fields = ['email_verified_at', 'xp_points', 'streak_days', 'level', 'last_active_at']


if admin.site.is_registered(User):
    admin.site.unregister(User)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Account admin with verification and role visibility.

    Passwords stay hashed behind Django's standard widget; token hashes are
    never shown anywhere in the admin.
    """

    inlines = [StudentProfileInline]
    list_display = [
        'username', 'email', 'full_name_display', 'role_display',
        'email_verified_display', 'is_active', 'is_staff', 'date_joined',
    ]
    list_filter = BaseUserAdmin.list_filter + (
        'profile__email_verified', 'profile__role',
    )
    search_fields = ['username', 'email', 'first_name', 'last_name']
    actions = ['activate_accounts', 'deactivate_accounts']
    show_full_result_count = False

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('profile')

    @admin.display(description='Name', ordering='first_name')
    def full_name_display(self, obj):
        return obj.get_full_name().strip() or '—'

    @admin.display(description='Role', ordering='profile__role')
    def role_display(self, obj):
        profile = getattr(obj, 'profile', None)
        return profile.get_role_display() if profile else 'Student'

    @admin.display(description='Email verified', boolean=True, ordering='profile__email_verified')
    def email_verified_display(self, obj):
        profile = getattr(obj, 'profile', None)
        return bool(profile and profile.email_verified)

    @admin.action(description='Activate selected accounts')
    def activate_accounts(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} account(s) activated.')

    @admin.action(description='Deactivate selected accounts')
    def deactivate_accounts(self, request, queryset):
        updated = queryset.exclude(pk=request.user.pk).update(is_active=False)
        self.message_user(request, f'{updated} account(s) deactivated.')


@admin.register(CareerTrack)
class CareerTrackAdmin(admin.ModelAdmin):
    """Learning-track management: create, categorize, publish, archive.

    Tracks are the learner-facing discovery layer, so the dashboard mirrors
    the hierarchy students see: cover image, category, objectives, and the
    course shelf below in recommended sequence.
    """

    list_display = ['title', 'category', 'course_summary', 'difficulty',
                    'estimated_hours', 'publish_state', 'is_active', 'order']
    list_filter = ['category', 'is_published', 'is_active', 'difficulty']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}
    ordering = ['order', 'title']
    inlines = [CourseInline, CertificationInline]
    actions = ['publish_tracks', 'unpublish_tracks', 'archive_tracks']
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'description', 'cover_image', 'icon'),
        }),
        ('Organization', {
            'fields': ('category', 'difficulty', 'estimated_hours', 'order'),
        }),
        ('Learning objectives', {
            'fields': ('learning_objectives',),
            'description': 'What a learner can do after finishing this track (JSON list).',
        }),
        ('Publication', {
            'fields': ('is_published', 'is_active'),
            'description': (
                '"Published" shows the track to learners; unchecking '
                '"active" archives it without touching course data.'
            ),
        }),
    )

    @admin.display(description='Courses')
    def course_summary(self, obj):
        total = obj.courses.count()
        published = obj.courses.filter(is_active=True, is_published=True).count()
        return f'{published} published / {total} total'

    @admin.display(description='State', boolean=True, ordering='is_published')
    def publish_state(self, obj):
        return obj.is_published and obj.is_active

    @admin.action(description='Publish selected tracks to learners')
    def publish_tracks(self, request, queryset):
        updated = queryset.update(is_published=True, is_active=True)
        self.message_user(request, f'{updated} track(s) published.')

    @admin.action(description='Unpublish selected tracks (hidden from learners)')
    def unpublish_tracks(self, request, queryset):
        updated = queryset.update(is_published=False)
        self.message_user(request, f'{updated} track(s) unpublished.')

    @admin.action(description='Archive selected tracks (soft delete)')
    def archive_tracks(self, request, queryset):
        updated = queryset.update(is_published=False, is_active=False)
        self.message_user(request, f'{updated} track(s) archived. Courses and learner progress are untouched.')

    def _protection_message(self, request, error, count=1):
        """Turn a ProtectedError into actionable guidance. Deleting a track
        that still holds courses is always a mistake or needs reassignment
        first — never a silent cascade."""
        self.message_user(
            request,
            'Cannot delete track(s) that still contain courses. Move the '
            'courses to another track (edit each course) or use the '
            '“Archive” action instead. Blocked objects: '
            + ', '.join(str(item) for item in error.protected_objects[:5]),
            level=messages.ERROR,
        )

    def delete_model(self, request, obj):
        try:
            super().delete_model(request, obj)
        except ProtectedError as error:
            self._protection_message(request, error)

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            try:
                obj.delete()
            except ProtectedError as error:
                self._protection_message(request, error)


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
            'fields': ('difficulty', 'language', 'academic_class', 'instructor', 'prerequisites')
        }),
        ('Content', {
            'fields': ('learning_objectives', 'is_free', 'is_active', 'is_published', 'order')
        }),
        ('Certification policy', {
            'fields': ('certification_enabled', 'require_all_lessons',
                       'require_final_assessment', 'certification_passing_score'),
            'description': 'Rules used to decide when a verifiable certificate is earned.',
        }),
    )

    def get_queryset(self, request):
        lesson_minutes = Lesson.objects.filter(
            chapter__course=OuterRef('pk'),
            chapter__is_active=True,
            is_active=True,
        ).values('chapter__course').annotate(
            total=Sum('duration_minutes'),
        ).values('total')[:1]
        lesson_xp = Lesson.objects.filter(
            chapter__course=OuterRef('pk'),
            chapter__is_active=True,
            is_active=True,
        ).values('chapter__course').annotate(
            total=Sum('xp_reward'),
        ).values('total')[:1]
        exercise_xp = Exercise.objects.filter(
            lesson__chapter__course=OuterRef('pk'),
            lesson__chapter__is_active=True,
            lesson__is_active=True,
            is_active=True,
        ).values('lesson__chapter__course').annotate(
            total=Sum('xp_reward'),
        ).values('total')[:1]
        return super().get_queryset(request).annotate(
            admin_lesson_minutes=Subquery(lesson_minutes),
            admin_lesson_xp=Subquery(lesson_xp),
            admin_exercise_xp=Subquery(exercise_xp),
        ).annotate(
            admin_total_xp=ExpressionWrapper(
                F('admin_lesson_xp') + F('admin_exercise_xp'),
                output_field=IntegerField(),
            ),
        ).select_related('track')

    @admin.display(description='Estimated hours', ordering='admin_lesson_minutes')
    def estimated_hours_display(self, obj):
        return max(1, round((obj.admin_lesson_minutes or 0) / 60))

    @admin.display(description='Total XP', ordering='admin_total_xp')
    def total_xp_display(self, obj):
        return (obj.admin_lesson_xp or 0) + (obj.admin_exercise_xp or 0)


@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'order', 'lesson_count', 'exercise_count', 'xp_reward',
                    'source_type', 'verification_status', 'is_active']
    list_filter = ['course__track', 'course', 'source_type', 'verification_status', 'is_active']
    search_fields = ['title', 'description', 'textbook_unit', 'textbook_topic', 'textbook_pages']
    prepopulated_fields = {'slug': ('title',)}
    ordering = ['course', 'order']
    inlines = [LessonInline]
    fieldsets = (
        (None, {
            'fields': ('course', 'title', 'slug', 'description')
        }),
        ('Configuration', {
            'fields': ('order', 'xp_reward', 'is_active')
        }),
        TEXTBOOK_REFERENCE_FIELDSET,
    )

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            admin_lesson_count=Count('lessons', distinct=True),
            admin_exercise_count=Count('lessons__exercises', distinct=True),
        ).select_related('course')

    @admin.display(description='Lessons', ordering='admin_lesson_count')
    def lesson_count(self, obj):
        return obj.admin_lesson_count

    @admin.display(description='Exercises', ordering='admin_exercise_count')
    def exercise_count(self, obj):
        return obj.admin_exercise_count


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'chapter', 'content_type', 'order', 'xp_reward', 'duration_minutes',
                    'source_type', 'verification_status', 'is_free_preview']
    list_filter = ['content_type', 'source_type', 'verification_status', 'is_free_preview',
                   'chapter__course__track', 'chapter__course']
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
        TEXTBOOK_REFERENCE_FIELDSET,
    )


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ['title', 'lesson', 'exercise_type', 'difficulty', 'language', 'xp_reward',
                    'order', 'source_type', 'verification_status', 'is_active']
    list_filter = ['exercise_type', 'difficulty', 'language', 'source_type',
                   'verification_status', 'is_active', 'lesson__chapter__course']
    search_fields = ['title', 'instructions', 'context', 'textbook_topic', 'textbook_pages']
    prepopulated_fields = {'slug': ('title',)}
    ordering = ['lesson__chapter__course', 'lesson__chapter__order', 'lesson__order', 'order']
    inlines = [HintInline]
    fieldsets = (
        (None, {
            'fields': ('lesson', 'title', 'slug', 'exercise_type', 'difficulty', 'language')
        }),
        ('Instructions', {
            'fields': ('instructions', 'context', 'constraints', 'expected_behavior', 'explain')
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
            'fields': ('order', 'xp_reward', 'max_attempts', 'is_final_assessment', 'is_active')
        }),
        TEXTBOOK_REFERENCE_FIELDSET,
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


@admin.register(PracticalClass)
class PracticalClassAdmin(admin.ModelAdmin):
    list_display = ['title', 'board', 'slug', 'order', 'subject_count', 'is_active']
    list_filter = ['board', 'is_active']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}
    ordering = ['order', 'title']
    fields = [
        'title', 'slug', 'board', 'thumbnail', 'description', 'order',
        'is_published', 'is_active',
    ]
    inlines = [PracticalSubjectInline]

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            admin_subject_count=Count(
                'subjects',
                filter=Q(subjects__is_active=True),
                distinct=True,
            ),
        )

    @admin.display(description='Subjects')
    def subject_count(self, obj):
        return obj.admin_subject_count


@admin.register(PracticalSubject)
class PracticalSubjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'practical_class', 'slug', 'practical_count', 'is_active']
    list_filter = ['practical_class', 'is_active']
    search_fields = ['title', 'description', 'practical_class__title']
    prepopulated_fields = {'slug': ('title',)}
    ordering = ['practical_class', 'order', 'title']

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            admin_practical_count=Count(
                'practicals',
                filter=Q(
                    practicals__is_active=True,
                    practicals__is_published=True,
                ),
                distinct=True,
            ),
        ).select_related('practical_class')

    @admin.display(description='Published practicals')
    def practical_count(self, obj):
        return obj.admin_practical_count


@admin.register(Practical)
class PracticalAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'practical_number', 'practical_class', 'subject',
        'is_published', 'is_active', 'updated_at',
    ]
    list_filter = ['practical_class', 'subject', 'is_published', 'is_active']
    search_fields = ['title', 'chapter_topic', 'subject__title']
    prepopulated_fields = {'slug': ('title',)}
    ordering = ['subject', 'order', 'practical_number']
    fieldsets = (
        (None, {
            'fields': (
                'practical_class', 'subject', 'title', 'slug',
                'practical_number', 'description', 'chapter_topic', 'order',
            ),
        }),
        ('Content', {
            'fields': (
                'aim', 'apparatus', 'theory', 'procedure', 'observations',
                'calculations', 'result', 'precautions', 'diagrams',
            ),
        }),
        ('Publishing', {'fields': ('is_published', 'is_active')}),
    )


@admin.register(PracticalProgress)
class PracticalProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'practical', 'completed_at', 'updated_at']
    list_filter = ['practical__practical_class', 'practical__subject']
    search_fields = ['user__username', 'practical__title']
    raw_id_fields = ['user', 'practical']
    date_hierarchy = 'updated_at'


@admin.register(PracticalBookmark)
class PracticalBookmarkAdmin(admin.ModelAdmin):
    list_display = ['user', 'practical', 'created_at']
    list_filter = ['practical__practical_class', 'practical__subject']
    search_fields = ['user__username', 'practical__title']
    raw_id_fields = ['user', 'practical']
    date_hierarchy = 'created_at'


@admin.register(LearningActivity)
class LearningActivityAdmin(admin.ModelAdmin):
    list_display = ['user', 'activity_type', 'title', 'status', 'activity_date', 'occurred_at']
    list_filter = ['activity_type', 'status', 'activity_date']
    search_fields = ['user__username', 'title']
    raw_id_fields = ['user', 'course', 'lesson', 'practical', 'exercise']
    date_hierarchy = 'activity_date'


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'status', 'progress_percentage', 'enrolled_at', 'last_activity_at']
    list_filter = ['status', 'course__track']
    search_fields = ['user__username', 'course__title']
    raw_id_fields = ['user', 'course', 'last_lesson']
    date_hierarchy = 'enrolled_at'

    def get_queryset(self, request):
        total_lessons = Lesson.objects.filter(
            chapter__course=OuterRef('course_id'),
        ).values('chapter__course').annotate(
            total=Count('pk'),
        ).values('total')[:1]
        completed_lessons = LessonProgress.objects.filter(
            user=OuterRef('user_id'),
            lesson__chapter__course=OuterRef('course_id'),
            status='completed',
        ).values('lesson__chapter__course').annotate(
            total=Count('pk'),
        ).values('total')[:1]
        return super().get_queryset(request).select_related(
            'user', 'course',
        ).annotate(
            admin_total_lessons=Subquery(total_lessons),
            admin_completed_lessons=Subquery(completed_lessons),
        )

    def progress_percentage(self, obj):
        total = obj.admin_total_lessons or 0
        completed = obj.admin_completed_lessons or 0
        percentage = round((completed / total) * 100) if total else 0
        return f"{percentage}%"


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


# ─── Authentication models ──────────────────────────────────────────────────


class SingleUseTokenAdmin(admin.ModelAdmin):
    """Verification/reset tokens — hashes are deliberately never displayed."""

    list_display = ['user', 'created_at', 'expires_at', 'used_at', 'status']
    list_filter = ['created_at', 'used_at']
    search_fields = ['user__username', 'user__email']
    raw_id_fields = ['user']
    readonly_fields = ['user', 'created_at', 'expires_at', 'used_at']
    date_hierarchy = 'created_at'

    @admin.display(description='Status')
    def status(self, obj):
        if obj.used_at:
            return 'Used'
        return 'Expired' if obj.is_expired else 'Active'

    def has_add_permission(self, request):
        return False


@admin.register(EmailVerificationToken)
class EmailVerificationTokenAdmin(SingleUseTokenAdmin):
    pass


@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(SingleUseTokenAdmin):
    pass


@admin.register(AuthenticationAuditLog)
class AuthenticationAuditLogAdmin(admin.ModelAdmin):
    """Read-only trail of authentication events for abuse investigations."""

    list_display = ['created_at', 'event', 'user', 'identifier', 'ip_address']
    list_filter = ['event', 'created_at']
    search_fields = ['user__username', 'user__email', 'identifier', 'ip_address']
    raw_id_fields = ['user']
    readonly_fields = [
        'user', 'event', 'identifier', 'ip_address', 'user_agent',
        'metadata', 'created_at',
    ]
    date_hierarchy = 'created_at'

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
