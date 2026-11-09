"""Professionally written starter templates for the Email Templates Library.

Consumed by migration ``0036_seed_default_email_templates`` to install a
curated collection the first time the feature is deployed. The bodies keep the
``{{student_name}}`` / ``{{organization_name}}`` tokens *unrendered* on purpose:
personalization is applied per recipient later, by the existing composer
pipeline (:mod:`learning.services.email_composer`), never here.

These are the canonical defaults — editing them after seeding does not change
what already exists in the database, and the seed is idempotent (keyed on the
template name), so re-running it never duplicates or overwrites an admin's
edits.
"""

from __future__ import annotations


def _body(paragraphs: list[str]) -> str:
    return ''.join(paragraphs)


WELCOME_TEMPLATES = [
    {
        'name': 'Welcome to Code Yaar',
        'category': 'Welcome & Onboarding',
        'description': 'The first email a new student receives after creating an account.',
        'is_favorite': True,
        'subject': 'Welcome to Code Yaar, {{student_name}} 🚀',
        'heading': 'Welcome aboard, {{student_name}}!',
        'preview_text': 'Your coding journey starts here — set up your first track in minutes.',
        'body_html': _body([
            '<p>Hi {{student_name}},</p>',
            '<p>Welcome to <strong>Code Yaar</strong> — the learning platform built to take you from '
            'first line of code to job-ready developer. Your account ({{student_email}}) is ready to go.</p>',
            '<p>Here is how to make the most of your first week:</p>',
            '<ul>',
            '<li>Pick a <strong>learning track</strong> that matches your goal — web, Python, or '
            'game development are great starting points.</li>',
            '<li>Complete your first lesson and earn your first XP.</li>',
            '<li>Try the in-browser code editor; nothing to install.</li>',
            '</ul>',
            '<p>Stuck on anything? Reply to this email and a mentor will help. We are glad you are here.</p>',
        ]),
        'cta_label': 'Start my first lesson',
        'cta_url': '/dashboard',
        'footer_content': 'You are receiving this because you signed up for Code Yaar on {{current_date}}.',
    },
    {
        'name': 'Student Account Successfully Created',
        'category': 'Welcome & Onboarding',
        'description': 'Confirmation sent when an account is provisioned (e.g. by a school admin).',
        'subject': 'Your Code Yaar account is ready',
        'heading': 'Your account has been created',
        'preview_text': 'Here are your sign-in details and where to begin.',
        'body_html': _body([
            '<p>Hello {{student_name}},</p>',
            '<p>Your Code Yaar account has been set up successfully. You can now sign in with the '
            'email address <strong>{{student_email}}</strong> (Student ID: {{student_id}}).</p>',
            '<p>Once signed in, head to your dashboard to see the courses your instructor has '
            'assigned to you. Your progress, XP and certificates all live there.</p>',
            '<p>If you did not expect this account, please let us know right away so we can keep '
            'your information safe.</p>',
        ]),
        'cta_label': 'Sign in to Code Yaar',
        'cta_url': '/login',
        'footer_content': 'Created on {{current_date}} · Code Yaar',
    },
    {
        'name': 'Welcome to the Code Yaar Community',
        'category': 'Welcome & Onboarding',
        'description': 'A warmer, community-focused welcome highlighting people and events.',
        'subject': 'You are in — welcome to the Code Yaar community',
        'heading': 'Welcome to the community, {{student_name}}!',
        'preview_text': 'Meet the people, join an event, and start building together.',
        'body_html': _body([
            '<p>Hi {{student_name}},</p>',
            '<p>Beyond the courses, Code Yaar is a community of learners and mentors across Pakistan '
            'and beyond. Here is where the people are:</p>',
            '<ul>',
            '<li><strong>Hackathons</strong> — team up and build something real in a weekend.</li>',
            '<li><strong>Achievements &amp; leaderboards</strong> — earn badges and climb.</li>',
            '<li><strong>Mentor support</strong> — real developers review your work.</li>',
            '</ul>',
            '<p>Introduce yourself, join your first event, and don&apos;t be shy about asking '
            'questions. Everyone here started exactly where you are now.</p>',
        ]),
        'cta_label': 'Explore community events',
        'cta_url': '/competitions',
        'footer_content': 'Welcome aboard — {{organization_name}} team, {{current_date}}',
    },
]

SECURITY_TEMPLATES = [
    {
        'name': 'Verify Your Email Address',
        'category': 'Account Verification',
        'description': 'Sent after sign-up to confirm ownership of the email address.',
        'is_favorite': True,
        'subject': 'Confirm your email to activate Code Yaar',
        'heading': 'One quick step to activate your account',
        'preview_text': 'Verify your address to unlock lessons, projects and certificates.',
        'body_html': _body([
            '<p>Hi {{student_name}},</p>',
            '<p>To keep Code Yaar safe and to make sure your certificates are issued to a real '
            'address, please confirm that <strong>{{student_email}}</strong> belongs to you.</p>',
            '<p>Verification takes only a few seconds and unlocks lessons, code exercises, '
            'leaderboards and course completion certificates.</p>',
            '<p>If the button does not work, copy this page&apos;s sign-in link or reply to this '
            'email for help.</p>',
        ]),
        'cta_label': 'Verify my email',
        'cta_url': '/verify-email',
        'footer_content': 'Did not create a Code Yaar account? You can safely ignore this email.',
    },
    {
        'name': 'Password Reset Instructions',
        'category': 'Password Reset',
        'description': 'Triggered when a user requests a password reset.',
        'is_favorite': True,
        'subject': 'Reset your Code Yaar password',
        'heading': 'We received your password reset request',
        'preview_text': 'Choose a new password to get back into your account.',
        'body_html': _body([
            '<p>Hi {{student_name}},</p>',
            '<p>Someone requested a password reset for the account <strong>{{student_email}}</strong> '
            'on {{current_date}}. Click the button below to choose a new password. The link expires '
            'shortly for your security.</p>',
            '<p>If you did not request this, you can ignore the email — your current password stays '
            'active and nothing will change.</p>',
            '<p>For your safety, Code Yaar staff will never ask you for your password by email.</p>',
        ]),
        'cta_label': 'Reset my password',
        'cta_url': '/reset-password',
        'footer_content': 'Request received on {{current_date}} · If you did not make this request, ignore this email.',
    },
    {
        'name': 'Important Account Security Notice',
        'category': 'Account Verification',
        'description': 'Proactive notice about a security event such as a new sign-in or setting change.',
        'subject': 'Security notice: important update to your account',
        'heading': 'A security change on your account',
        'preview_text': 'Review a recent change so your account stays protected.',
        'body_html': _body([
            '<p>Dear {{student_name}},</p>',
            '<p>We are writing to let you know about a recent security-related change to your '
            'Code Yaar account (ID {{student_id}}). This can be a new sign-in, a password change, '
            'or an updated recovery email.</p>',
            '<p><strong>If this was you:</strong> no action is needed. Great — your account is '
            'protected.</p>',
            '<p><strong>If this was not you:</strong> reset your password immediately and review '
            'your account details. We recommend a unique password you do not use anywhere else.</p>',
        ]),
        'cta_label': 'Review my account security',
        'cta_url': '/profile/settings',
        'footer_content': 'Notice generated on {{current_date}} · Your security matters to us.',
    },
]

LEARNING_TEMPLATES = [
    {
        'name': 'Course Enrollment Confirmation',
        'category': 'Course Enrollment',
        'description': 'Confirms a student has been enrolled in a course.',
        'subject': "You're enrolled, {{student_name}}! Let's begin",
        'heading': 'Your enrollment is confirmed',
        'preview_text': 'Your course is on your dashboard and ready to start.',
        'body_html': _body([
            '<p>Hi {{student_name}},</p>',
            '<p>Great news — you are now enrolled on Code Yaar ({{student_email}}). Your course has '
            'been added to your dashboard, and you can start the first lesson whenever you are ready.</p>',
            '<p>A few tips for success: set a small weekly goal, finish each exercise before moving '
            'on, and use the code editor to practice what you learn in every chapter.</p>',
            '<p>Your progress saves automatically, so you can pick up on any device.</p>',
        ]),
        'cta_label': 'Go to my course',
        'cta_url': '/dashboard',
        'footer_content': 'Enrolled on {{current_date}} · Happy learning!',
    },
    {
        'name': 'New Course Available',
        'category': 'Course Enrollment',
        'description': "Announces a newly published course relevant to a student's interests.",
        'subject': 'A new course just landed on Code Yaar',
        'heading': 'Fresh content, picked for you',
        'preview_text': 'See what is new and start learning today.',
        'body_html': _body([
            '<p>Hi {{student_name}},</p>',
            '<p>We just published a new course on Code Yaar, and we think it fits what you have '
            'been learning. New chapters arrive with hands-on exercises, real projects and a '
            'certificate on completion.</p>',
            '<p>Explore the curriculum on your dashboard and enroll to track your progress from '
            'the very first lesson.</p>',
        ]),
        'cta_label': 'See the new course',
        'cta_url': '/learn',
        'footer_content': 'Announced on {{current_date}} · {{organization_name}}',
    },
    {
        'name': 'Course Completion Congratulations',
        'category': 'Course Completion',
        'description': "Congratulates a student who just finished all lessons in a course.",
        'is_favorite': True,
        'subject': 'Congratulations, {{student_name}} — you finished! 🎉',
        'heading': 'Course complete. Well done!',
        'preview_text': 'You earned it. Here is your next best step.',
        'body_html': _body([
            '<p>Hi {{student_name}},</p>',
            '<p>You did it — you completed the course on Code Yaar! Finishing is very different from '
            'starting, and the consistency you showed is exactly what makes a developer.</p>',
            '<p>What to do next:</p>',
            '<ul>',
            '<li>Claim your <strong>certificate</strong> and share it.</li>',
            '<li>Build a portfolio project to put your new skills to work.</li>',
            '<li>Start the next track to keep the momentum going.</li>',
            '</ul>',
            '<p>We are proud of you. On to the next one!</p>',
        ]),
        'cta_label': 'Claim my certificate',
        'cta_url': '/certificates',
        'footer_content': 'Completed on {{current_date}} · Keep building with {{organization_name}}',
    },
    {
        'name': 'Certificate Successfully Issued',
        'category': 'Certificates & Achievements',
        'description': 'Delivers a newly issued, verifiable completion certificate.',
        'subject': 'Your Code Yaar certificate is ready, {{student_name}}',
        'heading': 'Your certificate has been issued',
        'preview_text': 'Download and share your verifiable certificate.',
        'body_html': _body([
            '<p>Dear {{student_name}},</p>',
            '<p>Congratulations! Your Code Yaar certificate for completing your course has been '
            'issued to <strong>{{student_email}}</strong> and is now available in your account.</p>',
            '<p>Each certificate carries a unique credential ID and a verification link, so '
            'employers and institutions can confirm it is genuine. Add it to LinkedIn or your CV '
            'with confidence.</p>',
        ]),
        'cta_label': 'View &amp; download certificate',
        'cta_url': '/certificates',
        'footer_content': 'Issued on {{current_date}} · {{organization_name}}',
    },
    {
        'name': 'New Achievement Unlocked',
        'category': 'Certificates & Achievements',
        'description': 'Celebrates a badge or milestone a student just earned.',
        'subject': 'Achievement unlocked: nice work, {{student_name}}!',
        'heading': 'You just earned a new achievement',
        'preview_text': 'Another badge for your profile — keep the streak alive.',
        'body_html': _body([
            '<p>Hey {{student_name}},</p>',
            '<p>You just unlocked a new achievement on Code Yaar! Achievements mark the real '
            'milestones — streaks kept, exercises mastered, projects shipped — and this one is now '
            'on your profile for everyone to see.</p>',
            '<p>Check your XP total on the leaderboard and see how close the next milestone is. '
            'Momentum compounds; keep it rolling.</p>',
        ]),
        'cta_label': 'View my achievements',
        'cta_url': '/profile',
        'footer_content': 'Earned on {{current_date}} · {{organization_name}}',
    },
]

OPPORTUNITY_TEMPLATES = [
    {
        'name': 'Internship Opportunity',
        'category': 'Internship Opportunities',
        'description': 'Shares a relevant internship opening with eligible students.',
        'is_favorite': True,
        'subject': 'An internship opportunity we think fits you',
        'heading': 'A role worth your attention',
        'preview_text': 'Hand-picked for Code Yaar learners — apply while spots are open.',
        'body_html': _body([
            '<p>Hi {{student_name}},</p>',
            '<p>An internship opportunity has come through the Code Yaar network that matches the '
            'skills you have been building. These roles are shared with our active learners first, '
            'and spots are limited.</p>',
            '<p>Read the full description and requirements, and apply early — strong candidates '
            'often secure interviews before the deadline. Need help polishing your CV or portfolio? '
            'Reply and a mentor can take a look.</p>',
        ]),
        'cta_label': 'See the opportunity',
        'cta_url': '/opportunities',
        'footer_content': 'Shared on {{current_date}} · {{organization_name}} careers',
    },
    {
        'name': 'Hackathon Announcement',
        'category': 'Hackathons & Competitions',
        'description': 'Invites students to register for an upcoming hackathon.',
        'subject': 'Registration is open for the next Code Yaar hackathon',
        'heading': 'Build something in 48 hours',
        'preview_text': 'Teams, mentors and prizes are ready — grab your spot.',
        'body_html': _body([
            '<p>Hi {{student_name}},</p>',
            '<p>Our next hackathon is live for registration. It is the fastest way to turn what '
            'you have learned into a real project, meet other builders, and get feedback from '
            'mentors and judges.</p>',
            '<ul>',
            '<li>Form or join a team (solo entries welcome too).</li>',
            '<li>Ship a working prototype over the weekend.</li>',
            '<li>Win prizes, certificates and swag.</li>',
            '</ul>',
            '<p>Seats fill quickly, so register now and start planning your idea.</p>',
        ]),
        'cta_label': 'Register for the hackathon',
        'cta_url': '/competitions',
        'footer_content': 'Announced on {{current_date}} · {{organization_name}} events',
    },
    {
        'name': 'Competition Registration',
        'category': 'Hackathons & Competitions',
        'description': 'Confirms a student has registered for a competition.',
        'subject': "You're registered — see you at the competition, {{student_name}}",
        'heading': 'Registration confirmed',
        'preview_text': 'Your spot is locked in. Here is what happens next.',
        'body_html': _body([
            '<p>Hi {{student_name}},</p>',
            '<p>Your registration for the Code Yaar competition is confirmed under '
            '<strong>{{student_email}}</strong> (ID {{student_id}}). You are in!</p>',
            '<p>Next steps: watch the event page for the schedule and rules, prepare your '
            'environment, and make sure you have not missed any eligibility requirements. We will '
            'email reminders as the dates approach.</p>',
            '<p>Good luck — we cannot wait to see what you build.</p>',
        ]),
        'cta_label': 'View event details',
        'cta_url': '/competitions',
        'footer_content': 'Registered on {{current_date}} · {{organization_name}}',
    },
    {
        'name': 'Campus Ambassador Selection',
        'category': 'Ambassador Programs',
        'description': 'Notifies a student that they were selected as a campus ambassador.',
        'subject': 'You are a Code Yaar Campus Ambassador! 🎉',
        'heading': 'Congratulations — you are selected',
        'preview_text': 'Here is your onboarding kit and first mission.',
        'body_html': _body([
            '<p>Dear {{student_name}},</p>',
            '<p>We are thrilled to welcome you as a <strong>Code Yaar Campus Ambassador</strong>! '
            'Your applications and initiative stood out, and we are excited to partner with you to '
            'bring coding to more students on your campus.</p>',
            '<p>As an ambassador you get early access to events, exclusive swag, mentorship, and a '
            'certificate recognizing your leadership. Your onboarding guide and first mission are '
            'waiting in the ambassador portal.</p>',
        ]),
        'cta_label': 'Open the ambassador portal',
        'cta_url': '/ambassador',
        'footer_content': 'Selected on {{current_date}} · Let build together, {{organization_name}}',
    },
]

TEAM_TEMPLATES = [
    {
        'name': 'Team Member Welcome',
        'category': 'Team Communications',
        'description': 'Welcomes a new teammate to the Code Yaar team.',
        'subject': 'Welcome to the team, {{student_name}}!',
        'heading': 'Glad you are here',
        'preview_text': 'A few things to get you set up and moving.',
        'body_html': _body([
            '<p>Hi {{student_name}},</p>',
            '<p>Welcome to the Code Yaar team! We hired you because we believe in what you can '
            'build with us, and we want your first week to be smooth.</p>',
            '<p>To get started: finish your account setup ({{student_email}}), meet your onboarding '
            'buddy, and skim the team handbook. Ask questions freely — nobody expects you to know '
            'everything on day one.</p>',
            '<p>We are genuinely excited to work with you.</p>',
        ]),
        'cta_label': 'Open onboarding checklist',
        'cta_url': '/dashboard',
        'footer_content': 'Joined on {{current_date}} · {{organization_name}}',
    },
    {
        'name': 'Internal Team Communication',
        'category': 'Team Communications',
        'description': 'A general internal update to the working team.',
        'subject': 'Team update: where we stand and whats next',
        'heading': 'A quick team sync',
        'preview_text': 'Priorities, blockers and the plan for the coming days.',
        'body_html': _body([
            '<p>Hi team,</p>',
            '<p>Here is a concise update so we are all aligned. This week we are focusing on the '
            'highest-impact items and clearing anything that is blocking progress.</p>',
            '<ul>',
            '<li><strong>Wins:</strong> what shipped and what went well.</li>',
            '<li><strong>Focus:</strong> the top priorities for the next few days.</li>',
            '<li><strong>Blockers:</strong> anything you need help or a decision on.</li>',
            '</ul>',
            '<p>Reply with updates on your area or flag anything that needs a decision from '
            'leadership. Thanks for the great work.</p>',
        ]),
        'cta_label': 'Add to the notes',
        'cta_url': '/dashboard',
        'footer_content': 'Sent on {{current_date}} · {{organization_name}} internal',
    },
    {
        'name': 'Growth Responsibilities',
        'category': 'Team Communications',
        'description': 'Outlines growth/marketing responsibilities for a team member.',
        'subject': 'Your growth responsibilities on Code Yaar',
        'heading': 'Growing our community, together',
        'preview_text': 'The goals, channels and metrics for your growth role.',
        'body_html': _body([
            '<p>Hi {{student_name}},</p>',
            '<p>As part of the growth team, your focus is bringing more learners onto Code Yaar and '
            'keeping them engaged. Concretely, that means owning a few channels end to end, '
            'tracking what works, and doubling down on it.</p>',
            '<ul>',
            '<li>Plan and post consistent, valuable content.</li>',
            '<li>Run small campaigns and measure sign-up and activation impact.</li>',
            '<li>Report what works so we can invest more there.</li>',
            '</ul>',
            '<p>Clear goals and the current metrics live in the growth board. Let us sync on your '
            'first priorities this week.</p>',
        ]),
        'cta_label': 'Open the growth board',
        'cta_url': '/dashboard',
        'footer_content': 'Shared on {{current_date}} · {{organization_name}} growth',
    },
    {
        'name': 'Backend Development Responsibilities',
        'category': 'Team Communications',
        'description': 'Outlines backend engineering responsibilities for a team member.',
        'subject': 'Your backend development responsibilities',
        'heading': 'Owning the platform backend',
        'preview_text': 'Scope, standards and first tasks for the backend role.',
        'body_html': _body([
            '<p>Hi {{student_name}},</p>',
            '<p>On the backend team you are responsible for the APIs and services that power '
            'Code Yaar. We value clean, tested, well-documented code and reliable, observable '
            'systems.</p>',
            '<ul>',
            '<li>Build and maintain Django REST endpoints with proper permissions and migrations.</li>',
            '<li>Write tests for every behavior change and keep the suite green.</li>',
            '<li>Watch performance, errors and data integrity in production.</li>',
            '</ul>',
            '<p>Your first tasks and our conventions are on the engineering board. Reach out '
            'anytime you want a design review or a second pair of eyes.</p>',
        ]),
        'cta_label': 'Open the engineering board',
        'cta_url': '/dashboard',
        'footer_content': 'Shared on {{current_date}} · {{organization_name}} engineering',
    },
    {
        'name': 'Partnership Invitation',
        'category': 'Partnership & Collaboration',
        'description': 'Opens a conversation with a potential partner organization.',
        'subject': 'A partnership opportunity with Code Yaar',
        'heading': 'Lets build something together',
        'preview_text': 'A short proposal for how our platforms can help each other.',
        'body_html': _body([
            '<p>Dear partner,</p>',
            '<p>I am reaching out from <strong>Code Yaar</strong>, a coding education platform with '
            'a growing community of motivated students. We see a natural fit between our missions '
            'and would love to explore a partnership.</p>',
            '<p>Together we could co-host events, share opportunities with our learners, or '
            'integrate offerings that benefit both audiences. I would value a short call to hear '
            'your thoughts and find the right starting point.</p>',
            '<p>Warm regards,<br />The Code Yaar team</p>',
        ]),
        'cta_label': 'Schedule a call',
        'cta_url': '/contact',
        'footer_content': 'Sent on {{current_date}} · {{organization_name}}',
    },
    {
        'name': 'Collaboration Proposal',
        'category': 'Partnership & Collaboration',
        'description': 'A more detailed proposal to collaborate on a specific initiative.',
        'subject': 'Collaboration proposal from Code Yaar',
        'heading': 'A concrete idea worth pairing on',
        'preview_text': 'Scope, value and next steps for a joint initiative.',
        'body_html': _body([
            '<p>Hello,</p>',
            '<p>Following our interest in working together, here is a focused collaboration '
            'proposal from Code Yaar. The goal is a specific initiative with clear value for both '
            'sides and a small, low-risk first step.</p>',
            '<ul>',
            '<li><strong>What:</strong> the joint initiative in a sentence.</li>',
            '<li><strong>Why:</strong> the value for each audience.</li>',
            '<li><strong>First step:</strong> a small pilot to prove the idea before scaling.</li>',
            '</ul>',
            '<p>If this direction excites you, let us set up a time to align on scope and '
            'ownership. Happy to adapt the plan to fit your priorities.</p>',
        ]),
        'cta_label': 'Discuss the proposal',
        'cta_url': '/contact',
        'footer_content': 'Proposed on {{current_date}} · {{organization_name}}',
    },
]


#: Every seeded template, in display order.
DEFAULT_EMAIL_TEMPLATES = (
    WELCOME_TEMPLATES
    + SECURITY_TEMPLATES
    + LEARNING_TEMPLATES
    + OPPORTUNITY_TEMPLATES
    + TEAM_TEMPLATES
)
