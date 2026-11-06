from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api_views
from . import admin_views
from . import analytics_views
from . import studio_views

router = DefaultRouter()
router.register(r'tracks', api_views.CareerTrackViewSet, basename='track')
router.register(r'courses', api_views.CourseViewSet, basename='course')
router.register(r'projects', api_views.ProjectViewSet, basename='project')
router.register(r'challenges', api_views.ChallengeViewSet, basename='challenge')
router.register(r'enrollments', api_views.EnrollmentViewSet, basename='enrollment')
router.register(r'lesson-progress', api_views.LessonProgressViewSet, basename='lesson-progress')
router.register(r'attempts', api_views.ExerciseAttemptViewSet, basename='exercise-attempt')
router.register(r'progress', api_views.ProgressViewSet, basename='progress')
router.register(r'xp', api_views.XPTransactionViewSet, basename='xp-transaction')
router.register(r'achievements', api_views.AchievementViewSet, basename='achievement')
router.register(r'my-achievements', api_views.UserAchievementViewSet, basename='user-achievement')
router.register(r'certifications', api_views.CertificationViewSet, basename='certification')
router.register(r'my-certifications', api_views.UserCertificationViewSet, basename='user-certification')
router.register(r'skills', api_views.SkillViewSet, basename='skill')
router.register(r'my-skills', api_views.UserSkillViewSet, basename='user-skill')
router.register(r'practical-classes', api_views.PracticalClassViewSet, basename='practical-class')
router.register(r'practical-subjects', api_views.PracticalSubjectViewSet, basename='practical-subject')
router.register(r'practicals', api_views.PracticalViewSet, basename='practical')
router.register(r'practical-progress', api_views.PracticalProgressViewSet, basename='practical-progress')
router.register(r'practical-bookmarks', api_views.PracticalBookmarkViewSet, basename='practical-bookmark')
router.register(r'portfolio/projects', api_views.StudentProjectViewSet, basename='student-project')
router.register(r'admin/practical-classes', api_views.PracticalClassAdminViewSet, basename='admin-practical-class')
router.register(r'admin/practical-subjects', api_views.PracticalSubjectAdminViewSet, basename='admin-practical-subject')
router.register(r'admin/practicals', api_views.PracticalAdminViewSet, basename='admin-practical')
router.register(r'admin/tracks', admin_views.CareerTrackAdminViewSet, basename='admin-track')
router.register(r'admin/courses', admin_views.CourseAdminViewSet, basename='admin-course')
router.register(r'admin/chapters', admin_views.ChapterAdminViewSet, basename='admin-chapter')
router.register(r'admin/lessons', admin_views.LessonAdminViewSet, basename='admin-lesson')
router.register(r'admin/exercises', admin_views.ExerciseAdminViewSet, basename='admin-exercise')
router.register(r'admin/students', admin_views.StudentAdminViewSet, basename='admin-student')
router.register(r'admin/instructors', admin_views.InstructorAdminViewSet, basename='admin-instructor')
router.register(r'admin/enrollments', admin_views.EnrollmentAdminViewSet, basename='admin-enrollment')
router.register(r'admin/competitions', admin_views.CompetitionAdminViewSet, basename='admin-competition')
router.register(r'admin/announcements', admin_views.AnnouncementAdminViewSet, basename='admin-announcement')
router.register(r'admin/platform-updates', admin_views.PlatformUpdateAdminViewSet, basename='admin-platform-update')
router.register(r'admin/registration-form-fields', admin_views.RegistrationFormFieldAdminViewSet, basename='admin-registration-form-field')
# Course Creation Studio: one bundle per course plus nested curriculum authoring.
router.register(r'admin/course-studio', studio_views.CourseStudioViewSet, basename='admin-course-studio')
router.register(r'admin/course-categories', studio_views.CourseCategoryViewSet,
                basename='admin-course-category')
router.register(r'admin/hackathon-registrations', admin_views.CompetitionRegistrationAdminViewSet, basename='admin-hackathon-registration')
router.register(r'admin/email-campaigns', admin_views.EmailCampaignAdminViewSet, basename='admin-email-campaign')
router.register(r'admin/email-templates', admin_views.EmailTemplateAdminViewSet, basename='admin-email-template')
router.register(r'admin/achievements', admin_views.AchievementAdminViewSet, basename='admin-achievement')
router.register(r'admin/certificates', admin_views.CertificateAdminViewSet, basename='admin-certificate')
router.register(r'admin/audit-logs', admin_views.AuditLogAdminViewSet, basename='admin-audit-log')
router.register(r'competitions', api_views.CompetitionViewSet, basename='competition')
router.register(r'announcements', api_views.AnnouncementViewSet, basename='announcement')
router.register(r'platform-updates', api_views.PlatformUpdateViewSet, basename='platform-update')

urlpatterns = [
    # Authentication lives in `learning.auth_urls` (mounted at /api/auth/).

    # Profile stats
    path('profile/stats/', api_views.profile_stats_view, name='api-profile-stats'),
    path('progress/', api_views.progress_dashboard_view, name='api-progress-dashboard'),

    # Profile picture upload / removal (multipart, throttled)
    path('profile/avatar/', api_views.avatar_view, name='api-avatar'),

    # Notification preferences: both the long-standing profile route and the
    # notifications-scoped alias (GET shows effective values, PATCH updates).
    path('profile/preferences/', api_views.notification_preferences_view,
         name='api-notification-preferences'),
    path('notifications/preferences/', api_views.notification_preferences_api_view,
         name='api-notification-preferences-alias'),

    # In-app notifications
    path('notifications/', api_views.notifications_view, name='api-notifications'),
    path('notifications/unread-count/', api_views.notifications_unread_count_view,
         name='api-notifications-unread-count'),
    path('notifications/read-all/', api_views.notifications_read_all_view,
         name='api-notifications-read-all'),
    path('notifications/<int:pk>/read/', api_views.notification_read_view,
         name='api-notification-read'),
    path('notifications/<int:pk>/', api_views.notification_delete_view,
         name='api-notification-delete'),

    # Public, shareable profile
    path('users/<str:username>/', api_views.public_profile_view, name='api-public-profile'),
    path('users/<str:username>/follow/', api_views.follow_user_view, name='api-user-follow'),
    path('users/<str:username>/followers/', api_views.user_followers_view, name='api-user-followers'),
    path('users/<str:username>/following/', api_views.user_following_view, name='api-user-following'),

    # Account deletion request (recorded for admin follow-up)
    path('account/deletion-request/', api_views.account_deletion_request_view,
         name='api-account-deletion-request'),

    # Public badge verification + owner downloads
    path('badges/verify/<str:identifier>/', api_views.verify_badge, name='badge-verify'),
    path('badges/verify/<str:identifier>/image.png', api_views.public_badge_image, name='badge-verify-image'),
    path('badges/verify/<str:identifier>/share.png', api_views.public_badge_share_image, name='badge-verify-share-image'),
    path('badges/<str:identifier>/download/', api_views.download_badge, name='badge-download'),

    # Leaderboard
    path('leaderboard/', api_views.leaderboard_view, name='api-leaderboard'),

    # Portfolio management (owner). These specific segments are matched before
    # the ``portfolio/<username>/`` public routes below and before the router,
    # so they never collide with ``portfolio/projects/``.
    path('portfolio/me/', api_views.portfolio_me_view, name='api-portfolio-me'),
    path('portfolio/publish/', api_views.portfolio_publish_view, name='api-portfolio-publish'),
    path('portfolio/unpublish/', api_views.portfolio_unpublish_view, name='api-portfolio-unpublish'),

    # Course chapters
    path(
        'courses/<slug:course_slug>/chapters/',
        api_views.ChapterViewSet.as_view({'get': 'list'}),
        name='course-chapters',
    ),
    path(
        'courses/<slug:course_slug>/chapters/<slug:slug>/',
        api_views.ChapterViewSet.as_view({'get': 'retrieve'}),
        name='chapter-detail',
    ),

    # Course lessons
    path(
        'courses/<slug:course_slug>/lessons/',
        api_views.LessonViewSet.as_view({'get': 'list'}),
        name='course-lessons',
    ),
    path(
        'courses/<slug:course_slug>/lessons/<slug:slug>/',
        api_views.LessonViewSet.as_view({'get': 'retrieve'}),
        name='course-lesson-detail',
    ),

    # Chapter lessons
    path(
        'courses/<slug:course_slug>/chapters/<slug:chapter_slug>/lessons/',
        api_views.LessonViewSet.as_view({'get': 'list'}),
        name='chapter-lessons',
    ),

    # Lesson completion (mark reading/exercises complete)
    path(
        'lessons/<int:pk>/complete/',
        api_views.LessonViewSet.as_view({'post': 'complete'}),
        name='lesson-complete',
    ),

    # Sandbox snippet execution (lesson "Run" buttons)
    path('execute/', api_views.execute_snippet_view, name='api-execute'),

    # Exercises for a lesson
    path(
        'lessons/<int:lesson_id>/exercises/',
        api_views.ExerciseViewSet.as_view({'get': 'list'}),
        name='lesson-exercises',
    ),

    # Exercise detail (instructions, starter code, sanitized choices)
    path(
        'exercises/<int:pk>/',
        api_views.ExerciseViewSet.as_view({'get': 'retrieve'}),
        name='exercise-detail',
    ),

    # Exercise actions
    path(
        'exercises/<int:pk>/run/',
        api_views.ExerciseViewSet.as_view({'post': 'run'}),
        name='exercise-run',
    ),
    path(
        'exercises/<int:pk>/submit/',
        api_views.ExerciseViewSet.as_view({'post': 'submit'}),
        name='exercise-submit',
    ),
    path(
        'exercises/<int:pk>/hint/',
        api_views.ExerciseViewSet.as_view({'get': 'hint'}),
        name='exercise-hint',
    ),

    # Certificate issuance, download, and public verification are mounted once
    # in config/urls.py under the same api/ prefix; including them again here
    # produced a urls.W005 duplicate-pattern warning.

    # Admin dashboard
    path('admin/dashboard/stats/', admin_views.admin_dashboard_stats, name='admin-dashboard-stats'),
    path('admin/dashboard/recent-activity/', admin_views.admin_recent_activity, name='admin-dashboard-recent-activity'),
    path('admin/dashboard/top-courses/', admin_views.admin_top_courses, name='admin-dashboard-top-courses'),

    # Analytics (spec section 2): charted overview + CSV extracts for offline reporting.
    path('admin/analytics/overview/', analytics_views.admin_analytics_overview,
         name='admin-analytics-overview'),
    path('admin/analytics/export/', analytics_views.admin_analytics_export,
         name='admin-analytics-export'),
    path('admin/settings/', admin_views.admin_settings, name='admin-settings'),
    path('admin/email/settings/', admin_views.email_settings, name='admin-email-settings'),
    # One-click opt-out for non-essential campaign mail (signed token, public)
    path('email/unsubscribe/<str:token>/', api_views.email_unsubscribe_view,
         name='api-email-unsubscribe'),
    path('platform/status/', admin_views.public_platform_status, name='platform-status'),
    path('admin/roles/', admin_views.admin_roles, name='admin-roles'),
    # Router URLs
    path('', include(router.urls)),

    # Public portfolio routes are matched AFTER the router so that
    # ``portfolio/projects/`` (an owner endpoint) is never captured here as a
    # ``username``. The public project detail route is listed before the
    # portfolio catch so ``<username>`` does not swallow ``projects``.
    path('portfolio/<str:username>/projects/<slug:slug>/',
         api_views.public_project_detail_view, name='api-portfolio-public-project'),
    path('portfolio/<str:username>/',
         api_views.public_portfolio_view, name='api-portfolio-public'),
]
