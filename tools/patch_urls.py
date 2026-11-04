p = 'backend/learning/api_urls.py'
s = open(p).read()
s = s.replace("from . import api_views", "from . import api_views\nfrom . import admin_views")
old = "router.register(r'admin/practicals', api_views.PracticalAdminViewSet, basename='admin-practical')"
new = old + "\nrouter.register(r'admin/tracks', admin_views.CareerTrackAdminViewSet, basename='admin-track')\nrouter.register(r'admin/courses', admin_views.CourseAdminViewSet, basename='admin-course')\nrouter.register(r'admin/chapters', admin_views.ChapterAdminViewSet, basename='admin-chapter')\nrouter.register(r'admin/lessons', admin_views.LessonAdminViewSet, basename='admin-lesson')\nrouter.register(r'admin/exercises', admin_views.ExerciseAdminViewSet, basename='admin-exercise')\nrouter.register(r'admin/students', admin_views.StudentAdminViewSet, basename='admin-student')\nrouter.register(r'admin/instructors', admin_views.InstructorAdminViewSet, basename='admin-instructor')\nrouter.register(r'admin/enrollments', admin_views.EnrollmentAdminViewSet, basename='admin-enrollment')\nrouter.register(r'admin/competitions', admin_views.CompetitionAdminViewSet, basename='admin-competition')\nrouter.register(r'admin/achievements', admin_views.AchievementAdminViewSet, basename='admin-achievement')\nrouter.register(r'admin/certificates', admin_views.CertificateAdminViewSet, basename='admin-certificate')\nrouter.register(r'admin/audit-logs', admin_views.AuditLogAdminViewSet, basename='admin-audit-log')"
s = s.replace(old, new)
old2 = "    # Router URLs\n    path('', include(router.urls)),"
new2 = "    # Admin dashboard\n    path('admin/dashboard/stats/', admin_views.admin_dashboard_stats, name='admin-dashboard-stats'),\n    path('admin/dashboard/recent-activity/', admin_views.admin_recent_activity, name='admin-dashboard-recent-activity'),\n    path('admin/dashboard/top-courses/', admin_views.admin_top_courses, name='admin-dashboard-top-courses'),\n    path('admin/settings/', admin_views.admin_settings, name='admin-settings'),\n    path('admin/roles/', admin_views.admin_roles, name='admin-roles'),\n    # Router URLs\n    path('', include(router.urls)),"
s = s.replace(old2, new2)
open(p, 'w').write(s)
print('done')
