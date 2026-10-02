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

urlpatterns = [
    # Auth endpoints
    path('auth/register/', api_views.register_view, name='api-register'),
    path('auth/login/', api_views.login_view, name='api-login'),
    path('auth/profile/', api_views.profile_view, name='api-profile'),

    # Profile stats
    path('profile/stats/', api_views.profile_stats_view, name='api-profile-stats'),

    # Settings
    path('settings/account/', api_views.settings_view, name='api-settings'),
    path('settings/profile/', api_views.settings_profile_view, name='api-settings-profile'),

    # Leaderboard
    path('leaderboard/', api_views.leaderboard_view, name='api-leaderboard'),

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

    # Exercises for a lesson
    path(
        'lessons/<int:lesson_id>/exercises/',
        api_views.ExerciseViewSet.as_view({'get': 'list'}),
        name='lesson-exercises',
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

    # Router URLs
    path('', include(router.urls)),
]
