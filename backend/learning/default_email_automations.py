"""Starter automation rules for the Email Studio."""

DEFAULT_EMAIL_AUTOMATIONS = [
    {'trigger': 'student_registered', 'name': 'Welcome Email', 'description': 'Sent when an account is successfully created.', 'theme': 'emerald-signature', 'recipient_group': 'newly_registered_student'},
    {'trigger': 'email_verification_requested', 'name': 'Email Verification', 'description': 'Sent when registration requires email verification.', 'theme': 'emerald-signature', 'recipient_group': 'unverified_student'},
    {'trigger': 'email_verified', 'name': 'Verification Confirmation', 'description': 'Sent when an email address is successfully verified.', 'theme': 'emerald-signature', 'recipient_group': 'verified_student'},
    {'trigger': 'first_login', 'name': 'Getting Started Email', 'description': 'Sent on first successful login only.', 'theme': 'emerald-signature', 'recipient_group': 'new_student'},
    {'trigger': 'password_reset_requested', 'name': 'Password Reset', 'description': 'Sent when a password reset is requested.', 'theme': 'emerald-signature', 'recipient_group': 'requesting_user'},
    {'trigger': 'password_changed', 'name': 'Password Changed Notification', 'description': 'Sent when a password is successfully changed.', 'theme': 'emerald-signature', 'recipient_group': 'account_owner'},
    {'trigger': 'course_enrolled', 'name': 'Enrollment Confirmation', 'description': 'Sent on successful enrollment.', 'theme': 'creative-grid', 'recipient_group': 'enrolled_student'},
    {'trigger': 'course_completed', 'name': 'Course Completion Congratulations', 'description': 'Sent when a course is officially completed.', 'theme': 'creative-grid', 'recipient_group': 'completing_student'},
    {'trigger': 'certificate_issued', 'name': 'Certificate Notification', 'description': 'Sent when a certificate is generated.', 'theme': 'creative-grid', 'recipient_group': 'certificate_owner'},
    {'trigger': 'course_published', 'name': 'New Course Published', 'description': 'Sent when an admin publishes a course.', 'theme': 'midnight-launch', 'recipient_group': 'relevant_students'},
    {'trigger': 'course_updated', 'name': 'Course Content Updated', 'description': 'Sent on significant course update (optional).', 'theme': 'creative-grid', 'recipient_group': 'enrolled_students', 'enabled': False},
    {'trigger': 'achievement_unlocked', 'name': 'Achievement Notification', 'description': 'Sent when an achievement is awarded.', 'theme': 'creative-grid', 'recipient_group': 'achieving_student'},
    {'trigger': 'badge_earned', 'name': 'Badge Notification', 'description': 'Sent when a badge is awarded.', 'theme': 'creative-grid', 'recipient_group': 'badge_owner'},
    {'trigger': 'weekly_learning_digest', 'name': 'Weekly Learning Digest', 'description': 'Scheduled weekly learning summary.', 'theme': 'creative-grid', 'recipient_group': 'active_students', 'enabled': False},
    {'trigger': 'learning_inactivity', 'name': 'Learning Inactivity Reminder', 'description': 'Sent after 7 days of inactivity.', 'theme': 'creative-grid', 'recipient_group': 'inactive_students', 'enabled': False},
    {'trigger': 'platform_announcement', 'name': 'Platform Announcement', 'description': 'Important platform announcement.', 'theme': 'midnight-launch', 'recipient_group': 'selected_students'},
    {'trigger': 'security_notification', 'name': 'Security Notification', 'description': 'Account-related security notification.', 'theme': 'emerald-signature', 'recipient_group': 'affected_users'},
    {'trigger': 'student_group_announcement', 'name': 'Student Group Announcement', 'description': 'Announcement to a selected student group.', 'theme': 'midnight-launch', 'recipient_group': 'selected_group'},
    {'trigger': 'hackathon_invitation', 'name': 'Hackathon or Event Invitation', 'description': 'Invitation to a hackathon or event.', 'theme': 'midnight-launch', 'recipient_group': 'invited_students'},
    {'trigger': 'team_notification', 'name': 'Team and Staff Notification', 'description': 'Notification to team and staff.', 'theme': 'midnight-launch', 'recipient_group': 'staff'},
]