from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api_views

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
router.register(r'competitions', api_views.CompetitionViewSet, basename='competition')

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
