"""Course Creation Studio, publishing pipeline, capabilities and analytics (spec 1-4).

These tests exist because the admin panel's curriculum routes were linked but absent:
every ``create`` and ``[id]`` page for courses, chapters, lessons and exercises returned
404. The endpoints below are what replaces them, so the contract is pinned here -
including the guards that make the studio safe to hand to a non-superuser
(object scoping, optimistic-concurrency 409, validation-gated publish, append-only audit).
"""

from datetime import timedelta

from django.contrib.auth.models import Group, User
from django.core.management import call_command
from django.db.utils import IntegrityError
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from .models import (
    AdminActionLog, CareerTrack, Chapter, Course, CourseCategory, Enrollment,
    Exercise, Lesson, LessonProgress, UserProfile, record_admin_action,
)
from .services import admin_access


def make_course(**overrides):
    defaults = {
        'title': 'Python Foundations',
        'slug': 'python-foundations',
        'description': 'Variables, control flow and functions for absolute beginners.',
        'thumbnail': 'course-covers/python.png',
        'is_published': True,
        'is_active': True,
    }
    defaults.update(overrides)
    # ``Course.track`` is NOT NULL, and the studio serializer requires it, so a
    # fabricated course always needs one. Resolved lazily so tests that pass their
    # own track keep using it.
    if 'track' not in defaults and 'track_id' not in defaults:
        defaults['track'] = CareerTrack.objects.get_or_create(
            title='Test track', slug='shared-test-track')[0]
    for field in ('track', 'category', 'instructor_user', 'created_by'):
        value = defaults.get(field)
        if value is not None and not hasattr(value, 'pk'):
            defaults.pop(field)
            defaults[f'{field}_id'] = value
    return Course.objects.create(**defaults)


def make_chapter(course, order=1, **overrides):
    defaults = {
        'course': course, 'title': f'Chapter {order}', 'slug': f'ch-{course.pk}-{order}',
        'description': 'Chapter overview.', 'order': order,
    }
    defaults.update(overrides)
    return Chapter.objects.create(**defaults)


def make_lesson(chapter, order=1, **overrides):
    defaults = {
        'chapter': chapter, 'title': f'Lesson {order}', 'slug': f'ls-{chapter.pk}-{order}',
        'content_type': 'text', 'content_body': '# Intro\n\nBody text for the lesson.',
        'learning_objective': 'Explain what a variable is.',
        'order': order, 'is_active': True, 'duration_minutes': 10,
    }
    defaults.update(overrides)
    return Lesson.objects.create(**defaults)


class StudioAccountsMixin:
    """Client plus one account per role the capability layer knows about."""

    def setUp(self):
        self.client = APIClient()
        self.track = CareerTrack.objects.create(title='Backend', slug='backend-track')
        self.category = CourseCategory.objects.create(title='Python', slug='python-cat')

        self.super_admin = User.objects.create_superuser(
            username='root', password='pw', email='root@example.com')
        self.platform_admin = User.objects.create_user(
            username='staff-admin', password='pw', email='staff-admin@example.com',
            is_staff=True)
        UserProfile.objects.filter(user=self.platform_admin).update(role='admin')

        self.editor = User.objects.create_user(
            username='course-editor', password='pw', email='editor@example.com',
            is_staff=True)
        UserProfile.objects.filter(user=self.editor).update(role='admin')
        self.editor.groups.add(Group.objects.get_or_create(name='Course Editor')[0])

        self.instructor = User.objects.create_user(
            username='teacher', password='pw', email='teacher@example.com')
        # ``user_role()`` reads the profile field ('mentor') and the group, never a
        # string called 'instructor' - so both are set the way the real platform sets
        # them, otherwise this test would be granting access to a role that does not
        # exist outside the test.
        UserProfile.objects.filter(user=self.instructor).update(role='mentor')
        self.instructor.groups.add(Group.objects.get_or_create(name='Instructors')[0])

        self.student = User.objects.create_user(
            username='learner', password='pw', email='learner@example.com')
        UserProfile.objects.filter(user=self.student).update(role='student')

        self.course = make_course(track=self.track, category=self.category,
                                  created_by=self.platform_admin)
        self.assigned = make_course(title='Assigned Course', slug='assigned-course',
                                    track=self.track, instructor_user=self.instructor,
                                    created_by=self.platform_admin)

    def login(self, user):
        self.client.force_authenticate(user=user)
        return self.client

    def url(self, suffix='', pk=None):
        """Studio routes are router-generated, so every one of them ends in a slash:
        asking for ``.../chapters`` gets a 301 from ``CommonMiddleware`` and the test
        then reads ``.data`` off a redirect. Suffixes are normalised here."""
        base = '/api/admin/course-studio/'
        if pk is not None:
            base += f'{pk}/'
        if suffix and not suffix.endswith('/'):
            suffix += '/'
        return base + suffix


class CourseCategoryTests(StudioAccountsMixin, TestCase):

    def test_categories_are_configurable_and_report_usage(self):
        self.login(self.platform_admin)
        response = self.client.post('/api/admin/course-categories/',
                                    {'title': 'Operating Systems', 'slug': 'operating-systems'},
                                    format='json')
        self.assertEqual(response.status_code, 201, response.data)
        listed = self.client.get('/api/admin/course-categories/')
        rows = listed.data['results'] if isinstance(listed.data, dict) else listed.data
        entry = next(row for row in rows if row['slug'] == 'operating-systems')
        self.assertEqual(entry['course_count'], 0)

    def test_duplicate_category_slug_is_suffixed_not_rejected(self):
        self.login(self.platform_admin)
        first = self.client.post('/api/admin/course-categories/',
                                 {'title': 'Databases', 'slug': 'databases'}, format='json')
        self.assertEqual(first.status_code, 201, first.data)
        second = self.client.post('/api/admin/course-categories/',
                                 {'title': 'Databases', 'slug': 'databases'}, format='json')
        self.assertEqual(second.status_code, 201, second.data)
        self.assertNotEqual(first.data['slug'], second.data['slug'])


class StudioAccessControlTests(StudioAccountsMixin, TestCase):

    def test_student_is_rejected_from_every_studio_route(self):
        self.login(self.student)
        for suffix, method in (('', 'get'), (f'{self.course.pk}/bundle/', 'get')):
            response = getattr(self.client, method)(f'/api/admin/course-studio/{suffix}')
            self.assertEqual(response.status_code, 403, (suffix, response.status_code))

    def test_list_is_scoped_to_the_instructors_own_courses(self):
        self.login(self.instructor)
        response = self.client.get('/api/admin/course-studio/')
        self.assertEqual(response.status_code, 200)
        slugs = {row['slug'] for row in response.data['results']}
        self.assertEqual(slugs, {'assigned-course'})

    def test_instructor_cannot_open_an_unassigned_course(self):
        self.login(self.instructor)
        response = self.client.get(self.url('bundle/', pk=self.course.pk))
        self.assertEqual(response.status_code, 403)

    def test_instructor_can_edit_a_course_assigned_to_them(self):
        self.login(self.instructor)
        response = self.client.patch(self.url('', pk=self.assigned.pk),
                                     {'description': 'Rewritten by the instructor.'},
                                     format='json')
        self.assertEqual(response.status_code, 200, response.data)
        self.assigned.refresh_from_db()
        self.assertEqual(self.assigned.description, 'Rewritten by the instructor.')

    def test_course_editor_group_cannot_publish(self):
        """A Course Editor has editorial hands but no publication authority."""
        chapter = make_chapter(self.course)
        lesson = make_lesson(chapter)
        lesson.content_body = 'x' * 40
        lesson.save(update_fields=['content_body'])
        self.login(self.editor)
        response = self.client.post(self.url('publish/', pk=self.course.pk), {}, format='json')
        self.assertEqual(response.status_code, 403, response.data)

    def test_course_editor_can_author_but_not_reassign_instructor(self):
        self.login(self.editor)
        created = self.client.post(self.url('chapters', pk=self.course.pk),
                                   {'title': 'Editor chapter'}, format='json')
        self.assertEqual(created.status_code, 201, created.data)
        moved = self.client.patch(self.url('', pk=self.course.pk),
                                  {'instructor_user': self.instructor.pk}, format='json')
        self.assertEqual(moved.status_code, 400, moved.data)


class CurriculumBuilderTests(StudioAccountsMixin, TestCase):
    """The wizard step that builds chapters and lessons, including drag-and-drop moves."""

    def test_wizard_create_then_autosave_returns_bundle(self):
        self.login(self.platform_admin)
        created = self.client.post('/api/admin/course-studio/', {
            'title': 'Data Structures 101',
            'slug': 'data-structures-101',
            'description': 'Arrays, linked lists and stacks.',
            'track': self.track.pk,
            'category': self.category.pk,
            'learning_objectives': ['Model a list', 'Compare insertion costs'],
            'tags': ['dsa'],
        }, format='json')
        self.assertEqual(created.status_code, 201, created.data)
        bundle = created.data
        self.assertEqual(bundle['course']['slug'], 'data-structures-101')
        self.assertFalse(bundle['course']['is_published'])
        self.assertEqual(bundle['chapters'], [])
        self.assertEqual(set(bundle['permissions']), {'can_edit', 'can_publish', 'can_archive'})
        self.assertTrue(bundle['permissions']['can_edit'])

        pk = bundle['course']['id']
        saved = self.client.patch(self.url('', pk=pk),
                                  {'course': {'subtitle': 'Hands-on arrays'}}, format='json')
        self.assertEqual(saved.status_code, 200, saved.data)
        Course.objects.get(pk=pk).refresh_from_db()
        self.assertEqual(Course.objects.get(pk=pk).subtitle, 'Hands-on arrays')

    def test_duplicate_slug_is_suffixed_instead_of_crashing(self):
        """The old duplicate() hard-coded ``-copy`` and blew up on the second run."""
        self.login(self.platform_admin)
        slugs = []
        for _ in range(3):
            response = self.client.post('/api/admin/course-studio/', {
                'title': 'Web Basics', 'slug': 'web-basics',
                'description': 'HTML and CSS from scratch.',
                'track': self.track.pk,
            }, format='json')
            self.assertEqual(response.status_code, 201, response.data)
            slugs.append(response.data['course']['slug'])
        self.assertEqual(slugs, ['web-basics', 'web-basics-2', 'web-basics-3'])

    def test_stale_autosave_conflicts_with_409(self):
        self.login(self.platform_admin)
        stale = (timezone.now() - timedelta(seconds=30)).isoformat()
        response = self.client.patch(self.url('', pk=self.course.pk),
                                     {'description': 'Written by a stale tab.',
                                      'expected_updated_at': stale}, format='json')
        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.data['code'], 'conflict')
        self.assertIn('current_updated_at', response.data)
        self.course.refresh_from_db()
        self.assertNotEqual(self.course.description, 'Written by a stale tab.')

    def test_chapter_and_lesson_creation_with_derived_publication_state(self):
        self.login(self.platform_admin)
        chapter = self.client.post(self.url('chapters', pk=self.course.pk),
                                   {'title': 'Getting set up'}, format='json')
        self.assertEqual(chapter.status_code, 201, chapter.data)
        chapter_pk = chapter.data['id']

        draft = self.client.post(self.url('lessons', pk=self.course.pk),
                                 {'chapter': chapter_pk, 'title': 'Install Python',
                                  'content_body': 'Download and install.',
                                  'learning_objective': 'Install the interpreter',
                                  'is_active': False}, format='json')
        self.assertEqual(draft.status_code, 201, draft.data)
        self.assertFalse(draft.data['is_active'])

        bundle = self.client.get(self.url('bundle/', pk=self.course.pk)).data
        row = bundle['chapters'][0]
        # One lesson, none live: derived state is a draft, not an empty chapter.
        self.assertEqual(row['publication_state'], 'draft')
        self.assertEqual(bundle['stats']['lesson_count'], 1)

        live = self.client.post(self.url('lessons', pk=self.course.pk),
                                {'chapter': chapter_pk, 'title': 'First script',
                                 'content_body': 'Print hello.'}, format='json')
        self.assertEqual(live.status_code, 201, live.data)
        bundle = self.client.get(self.url('bundle/', pk=self.course.pk)).data
        self.assertEqual(bundle['chapters'][0]['publication_state'], 'partial')
        self.assertEqual(bundle['chapters'][0]['published_lesson_count'], 1)

    def test_blank_titles_are_refused_not_persisted(self):
        self.login(self.platform_admin)
        response = self.client.post(self.url('chapters', pk=self.course.pk),
                                    {'title': '   '}, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(self.course.chapters.count(), 0)

    def test_duplicate_lesson_copies_content_as_draft_with_suffixed_slug(self):
        chapter = make_chapter(self.course)
        lesson = make_lesson(chapter)
        Exercise.objects.create(
            lesson=lesson, title='Warm-up', exercise_type='multiple_choice',
            instructions='Pick the right one.', is_active=True,
            choices=[{'id': 'a', 'text': 'yes', 'is_correct': True},
                     {'id': 'b', 'text': 'no', 'is_correct': False}],
        )
        self.login(self.platform_admin)
        response = self.client.post(self.url(f'lessons/{lesson.pk}/duplicate', pk=self.course.pk),
                                    {}, format='json')
        self.assertEqual(response.status_code, 201, response.data)
        copy = Lesson.objects.exclude(pk=lesson.pk).get()
        self.assertNotEqual(copy.slug, lesson.slug)
        self.assertFalse(copy.is_active, 'a duplicate must not go live on the learner side')
        self.assertEqual(copy.exercises.count(), 1)
        self.assertEqual(copy.content_body, lesson.content_body)

    def test_duplicate_chapter_keeps_lesson_order_and_drafts_visibility(self):
        chapter = make_chapter(self.course)
        make_lesson(chapter, order=1)
        make_lesson(chapter, order=2)
        self.login(self.platform_admin)
        response = self.client.post(
            self.url(f'chapters/{chapter.pk}/duplicate', pk=self.course.pk), {}, format='json')
        self.assertEqual(response.status_code, 201, response.data)
        copies = list(Chapter.objects.exclude(pk=chapter.pk))
        self.assertEqual(len(copies), 1)
        self.assertEqual(copies[0].lessons.count(), 2)
        self.assertFalse(any(l.is_active for l in copies[0].lessons.all()))

    def test_move_lesson_between_chapters_renumbers_dense_and_clears_foreign_prerequisite(self):
        first = make_chapter(self.course, order=1)
        second = make_chapter(self.course, order=2)
        a1 = make_lesson(first, order=1)
        make_lesson(first, order=2)
        moving = make_lesson(first, order=3, prerequisite=a1)

        self.login(self.platform_admin)
        response = self.client.post(
            self.url(f'lessons/{moving.pk}/move', pk=self.course.pk),
            {'chapter': second.pk, 'order': 1}, format='json')
        self.assertEqual(response.status_code, 200, response.data)
        moving.refresh_from_db()
        self.assertEqual(moving.chapter_id, second.pk)
        self.assertIsNone(moving.prerequisite_id,
                          'a same-chapter prerequisite cannot survive the move')
        self.assertEqual(list(second.lessons.order_by('order').values_list('order', flat=True)),
                         [1])

    def test_move_into_another_courses_chapter_is_refused(self):
        foreign_course = make_course(title='Other', slug='other-course')
        foreign_chapter = make_chapter(foreign_course)
        lesson = make_lesson(make_chapter(self.course))
        self.login(self.platform_admin)
        response = self.client.post(
            self.url(f'lessons/{lesson.pk}/move', pk=self.course.pk),
            {'chapter': foreign_chapter.pk}, format='json')
        self.assertEqual(response.status_code, 404, response.data)
        lesson.refresh_from_db()
        self.assertEqual(lesson.chapter.course_id, self.course.pk)

    def test_reorder_rejects_rows_outside_the_course(self):
        own = make_lesson(make_chapter(self.course))
        other = make_lesson(make_chapter(make_course(title='Other', slug='other-course')))
        self.login(self.platform_admin)
        response = self.client.post(self.url('lessons/reorder', pk=self.course.pk),
                                    {'items': [{'id': own.pk, 'order': 2},
                                               {'id': other.pk, 'order': 1}]}, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['code'], 'foreign_lesson')
        own.refresh_from_db()
        self.assertEqual(own.order, 1)

    def test_reorder_chapters_and_bulk_publish_lessons(self):
        one = make_chapter(self.course, order=1)
        two = make_chapter(self.course, order=2)
        first_lesson = make_lesson(one, order=1, is_active=False)
        second_lesson = make_lesson(two, order=1, is_active=False)

        self.login(self.platform_admin)
        reordered = self.client.post(self.url('chapters/reorder', pk=self.course.pk),
                                     {'items': [{'id': two.pk, 'order': 1},
                                                {'id': one.pk, 'order': 2}]}, format='json')
        self.assertEqual(reordered.status_code, 200, reordered.data)
        two.refresh_from_db()
        one.refresh_from_db()
        self.assertEqual((two.order, one.order), (1, 2))

        bulk = self.client.post(self.url('lessons/bulk-publish', pk=self.course.pk),
                                {'lessons': [first_lesson.pk, second_lesson.pk],
                                 'is_active': True}, format='json')
        self.assertEqual(bulk.status_code, 200, bulk.data)
        self.assertEqual(bulk.data['updated'], 2)
        self.assertTrue(Lesson.objects.filter(pk__in=[first_lesson.pk, second_lesson.pk],
                                             is_active=True).count() == 2)
        self.assertIn('checklist', bulk.data)

    def test_bulk_publish_cannot_touch_another_courses_lesson(self):
        foreign = make_lesson(make_chapter(make_course(title='Other', slug='other-course')))
        own = make_lesson(make_chapter(self.course))
        self.login(self.platform_admin)
        response = self.client.post(self.url('lessons/bulk-publish', pk=self.course.pk),
                                    {'lessons': [own.pk, foreign.pk]}, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['code'], 'foreign_lesson')
        foreign.refresh_from_db()
        self.assertTrue(foreign.is_active)

    def test_lesson_with_learner_progress_cannot_be_deleted(self):
        lesson = make_lesson(make_chapter(self.course))
        enrollment = Enrollment.objects.create(user=self.student, course=self.course)
        LessonProgress.objects.create(user=self.student, lesson=lesson, status='completed')
        self.login(self.platform_admin)
        response = self.client.delete(self.url(f'lessons/{lesson.pk}', pk=self.course.pk))
        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.data['code'], 'lesson_in_use')
        self.assertTrue(Lesson.objects.filter(pk=lesson.pk).exists())

    def test_clean_lesson_delete_is_audited(self):
        lesson = make_lesson(make_chapter(self.course))
        self.login(self.platform_admin)
        response = self.client.delete(self.url(f'lessons/{lesson.pk}', pk=self.course.pk))
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Lesson.objects.filter(pk=lesson.pk).exists())
        self.assertTrue(AdminActionLog.objects.filter(action='lesson.delete').exists())


class PublicationPipelineTests(StudioAccountsMixin, TestCase):
    """Spec 4: validation-gated publish, scheduled publication, archive."""

    def ready_course(self, title='Ready Course', slug='ready-course', **overrides):
        """A course that genuinely passes publication validation.

        ``require_final_assessment`` defaults True on the model, so a publishable course
        needs an assessable exercise - building one here keeps the pipeline tests honest
        instead of quietly switching the requirement off.
        """
        course = make_course(title=title, slug=slug, is_published=False,
                             category=self.category, subtitle='A short summary.',
                             learning_objectives=['Ship a small program'], **overrides)
        chapter = make_chapter(course)
        lesson = make_lesson(chapter)
        Exercise.objects.create(
            lesson=lesson, title='Final check', exercise_type='multiple_choice',
            instructions='Choose the correct answer.', is_active=True,
            is_final_assessment=True,
            choices=[{'id': 'a', 'text': 'right', 'is_correct': True},
                     {'id': 'b', 'text': 'wrong', 'is_correct': False}],
        )
        return course

    def test_checklist_separates_blockers_from_warnings(self):
        course = make_course(title='Thin Course', slug='thin-course', is_published=False,
                             description='', thumbnail='')
        self.login(self.platform_admin)
        report = self.client.get(self.url('checklist/', pk=course.pk)).data
        self.assertFalse(report['ok'])
        codes = {issue['code'] for issue in report['blocking']}
        self.assertIn('course_missing_description', codes)
        self.assertIn('course_missing_thumbnail', codes)
        self.assertIn('course_no_chapters', codes)
        # A warning never blocks: no objectives set is advisory, not a defect.
        self.assertIn('course_missing_objectives',
                      {issue['code'] for issue in report['warnings']})

    def test_publish_is_refused_while_validation_fails(self):
        course = make_course(title='Empty Course', slug='empty-course', is_published=False)
        self.login(self.platform_admin)
        response = self.client.post(self.url('publish/', pk=course.pk), {}, format='json')
        self.assertEqual(response.status_code, 400, response.data)
        self.assertEqual(response.data['code'], 'publish_blocked')
        course.refresh_from_db()
        self.assertFalse(course.is_published)

    def test_force_publish_without_a_reason_is_refused(self):
        """Overriding validation is allowed, but never silently."""
        course = make_course(title='Empty Course', slug='empty-course', is_published=False)
        self.login(self.platform_admin)
        response = self.client.post(self.url('publish/', pk=course.pk),
                                    {'force': 'true'}, format='json')
        self.assertEqual(response.status_code, 400, response.data)
        self.assertEqual(response.data['code'], 'override_reason_required')
        course.refresh_from_db()
        self.assertFalse(course.is_published)

    def test_publish_succeeds_once_the_course_is_complete(self):
        course = self.ready_course()
        self.login(self.platform_admin)
        response = self.client.post(self.url('publish/', pk=course.pk), {}, format='json')
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(response.data['status'], 'published')
        course.refresh_from_db()
        self.assertTrue(course.is_published)
        self.assertIsNotNone(course.published_at)
        row = AdminActionLog.objects.filter(action='course.publish').first()
        self.assertFalse(row.detail['forced'])

    def test_audited_override_records_the_reason(self):
        course = make_course(title='Urgent Course', slug='urgent-course', is_published=False)
        self.login(self.platform_admin)
        response = self.client.post(self.url('publish/', pk=course.pk), {
            'force': 'true', 'reason': 'Publisher asked for it before the inspection window.',
        }, format='json')
        self.assertEqual(response.status_code, 200, response.data)
        row = AdminActionLog.objects.filter(action='course.publish').first()
        self.assertTrue(row.detail['forced'])
        self.assertEqual(
            row.detail['override_reason'],
            'Publisher asked for it before the inspection window.')
        self.assertIn('course_no_chapters', row.detail['blocking_at_override'])

    def test_unpublish_returns_the_course_to_draft_without_deleting_content(self):
        course = self.ready_course()
        self.login(self.platform_admin)
        self.client.post(self.url('publish/', pk=course.pk), {}, format='json')
        response = self.client.post(self.url('unpublish/', pk=course.pk), {}, format='json')
        self.assertEqual(response.status_code, 200, response.data)
        course.refresh_from_db()
        self.assertFalse(course.is_published)
        self.assertEqual(course.chapters.count(), 1)
        self.assertEqual(course.chapters.first().lessons.count(), 1)

    def test_scheduling_a_course_that_fails_validation_is_refused(self):
        course = make_course(title='Weak Course', slug='weak-course', is_published=False)
        self.login(self.platform_admin)
        response = self.client.post(self.url('schedule/', pk=course.pk), {
            'publish_at': (timezone.now() + timedelta(days=1)).isoformat(),
        }, format='json')
        self.assertEqual(response.status_code, 400, response.data)
        self.assertEqual(response.data['code'], 'publish_blocked')
        course.refresh_from_db()
        self.assertIsNone(course.publish_at)

    def test_schedule_then_unschedule_clears_the_pending_publication(self):
        course = self.ready_course()
        self.login(self.platform_admin)
        response = self.client.post(self.url('schedule/', pk=course.pk), {
            'publish_at': (timezone.now() + timedelta(days=1)).isoformat(),
        }, format='json')
        self.assertEqual(response.status_code, 200, response.data)
        course.refresh_from_db()
        self.assertIsNotNone(course.publish_at)
        self.assertFalse(course.is_published)

        cleared = self.client.post(self.url('unschedule/', pk=course.pk), {}, format='json')
        self.assertEqual(cleared.status_code, 200, cleared.data)
        course.refresh_from_db()
        self.assertIsNone(course.publish_at)

    def test_the_cron_command_publishes_only_courses_that_are_due_and_valid(self):
        due = self.ready_course(slug='due-course', title='Due Course')
        due.publish_at = timezone.now() - timedelta(minutes=5)
        due.save(update_fields=['publish_at'])

        not_due = self.ready_course(slug='later-course', title='Later Course')
        not_due.publish_at = timezone.now() + timedelta(days=2)
        not_due.save(update_fields=['publish_at'])

        decayed = self.ready_course(slug='decayed-course', title='Decayed Course')
        decayed.publish_at = timezone.now() - timedelta(minutes=5)
        decayed.save(update_fields=['publish_at'])
        # Content can rot after scheduling; an unattended publish must re-check it.
        Lesson.objects.filter(chapter__course=decayed).update(is_active=False)

        call_command('publish_scheduled_courses')

        due.refresh_from_db()
        self.assertTrue(due.is_published)
        self.assertIsNone(due.publish_at)
        not_due.refresh_from_db()
        self.assertFalse(not_due.is_published)
        self.assertIsNotNone(not_due.publish_at)
        decayed.refresh_from_db()
        self.assertFalse(decayed.is_published)
        self.assertIsNotNone(decayed.publish_at, 'a blocked course stays visible as scheduled')
        self.assertTrue(AdminActionLog.objects.filter(
            action='course.scheduled_publish', target_id=due.pk).exists())

    def test_dry_run_publishes_nothing(self):
        course = self.ready_course()
        course.publish_at = timezone.now() - timedelta(minutes=1)
        course.save(update_fields=['publish_at'])
        call_command('publish_scheduled_courses', dry_run=True)
        course.refresh_from_db()
        self.assertFalse(course.is_published)

    def test_archive_hides_the_course_and_unarchive_restores_it(self):
        course = self.ready_course()
        self.login(self.platform_admin)
        self.client.post(self.url('publish/', pk=course.pk), {}, format='json')

        archived = self.client.post(self.url('archive/', pk=course.pk), {}, format='json')
        self.assertEqual(archived.status_code, 200, archived.data)
        course.refresh_from_db()
        self.assertIsNotNone(course.archived_at)
        self.assertFalse(course.is_published)
        self.assertFalse(course.is_active)

        restored = self.client.post(self.url('unarchive/', pk=course.pk), {}, format='json')
        self.assertEqual(restored.status_code, 200, restored.data)
        course.refresh_from_db()
        self.assertIsNone(course.archived_at)
        self.assertTrue(course.is_active)
        self.assertTrue(AdminActionLog.objects.filter(
            action='course.archive', target_id=course.pk).exists())

    def test_a_course_editor_cannot_publish_but_an_academic_manager_can(self):
        course = self.ready_course()
        academic = User.objects.create_user(
            username='academic-manager', password='pw', email='academic@example.com',
            is_staff=True)
        academic.groups.add(Group.objects.get_or_create(name='Academic Manager')[0])

        self.login(self.editor)
        blocked = self.client.post(self.url('publish/', pk=course.pk), {}, format='json')
        self.assertEqual(blocked.status_code, 403, blocked.data)

        self.login(academic)
        allowed = self.client.post(self.url('publish/', pk=course.pk), {}, format='json')
        self.assertEqual(allowed.status_code, 200, allowed.data)


class CapabilityMatrixTests(TestCase):
    """The capability layer the studio and analytics endpoints are gated on."""

    def setUp(self):
        self.track = CareerTrack.objects.create(title='Backend', slug='backend-track')

    def account(self, username, *, staff=False, superuser=False, role='student', groups=()):
        user = User.objects.create_user(
            username=username, password='pw', email=f'{username}@example.com',
            is_staff=staff, is_superuser=superuser)
        UserProfile.objects.filter(user=user).update(role=role)
        for name in groups:
            user.groups.add(Group.objects.get_or_create(name=name)[0])
        user = User.objects.get(pk=user.pk)
        UserProfile.objects.filter(user=user).update(role=role)
        return user

    def test_a_legacy_administrator_without_groups_keeps_every_capability(self):
        admin = self.account('plain-admin', staff=True, role='admin')
        self.assertTrue(admin_access.has_capability(admin, admin_access.COURSE_PUBLISH))
        self.assertTrue(admin_access.has_capability(admin, admin_access.ROLES_MANAGE))

    def test_assigning_a_group_scopes_an_administrator_to_that_group(self):
        editor = self.account('scoped-editor', staff=True, role='admin',
                              groups=['Course Editor'])
        self.assertTrue(admin_access.has_capability(editor, admin_access.COURSE_STUDIO_EDIT))
        self.assertFalse(admin_access.has_capability(editor, admin_access.COURSE_PUBLISH))
        self.assertFalse(admin_access.has_capability(editor, admin_access.STUDENT_READ))

    def test_a_course_editor_writes_content_but_never_publishes_or_reads_learners(self):
        editor = self.account('editor-only', groups=['Course Editor'])
        caps = admin_access.capabilities(editor)
        self.assertIn(admin_access.COURSE_STUDIO_VIEW, caps)
        self.assertNotIn(admin_access.COURSE_ARCHIVE, caps)
        self.assertNotIn(admin_access.STUDENT_READ, caps)

    def test_instructor_capabilities_are_scoped_to_assigned_courses(self):
        instructor = self.account('mentor', role='mentor', groups=['Instructors'])
        self.assertTrue(admin_access.has_capability(instructor, admin_access.COURSE_STUDIO_EDIT))
        self.assertFalse(admin_access.has_capability(instructor, admin_access.COURSE_PUBLISH))

        other = make_course(title='Unassigned', slug='unassigned-course', track=self.track)
        assigned = make_course(title='Mine', slug='mine-course', track=self.track,
                               instructor_user=instructor)
        from .permissions import ScopedCourseAccess
        view = type('Stub', (), {})
        request = type('Req', (), {'user': instructor})()
        permission = ScopedCourseAccess()
        self.assertFalse(permission.has_object_permission(request, view, other))
        self.assertTrue(permission.has_object_permission(request, view, assigned))

    def test_a_student_holds_no_administrative_capabilities(self):
        student = self.account('plain-student', groups=['Students'])
        self.assertEqual(admin_access.capabilities(student), frozenset())
        self.assertEqual(admin_access.admin_roles(student), [])

    def test_roles_are_additive_across_groups(self):
        both = self.account('two-hats', groups=['Course Editor', 'Communication Manager'])
        caps = admin_access.capabilities(both)
        self.assertIn(admin_access.COURSE_STUDIO_EDIT, caps)
        self.assertIn(admin_access.CAMPAIGN_MANAGE, caps)
        self.assertEqual(
            set(admin_access.admin_roles(both)), {'course_editor', 'communication_manager'})


class AnalyticsEndpointTests(StudioAccountsMixin, TestCase):

    def test_overview_reports_real_counts_and_declares_unavailable_surfaces(self):
        enrollment = Enrollment.objects.create(user=self.student, course=self.course)
        LessonProgress.objects.create(user=self.student, lesson=make_lesson(make_chapter(self.course)),
                                      status='completed')
        self.login(self.platform_admin)
        data = self.client.get('/api/admin/analytics/overview/').data
        self.assertEqual(data['education']['total_enrollments'], 1)
        self.assertEqual(data['education']['total_lesson_completions'], 1)
        # Series points are chart input: every bucket present, period + value only.
        self.assertTrue(all(set(point) == {'period', 'value'}
                            for point in data['education']['enrollments']))
        self.assertIn('total_students', data['students'])
        # Quizzes do not exist yet, so the API says so instead of inventing a chart.
        self.assertTrue(any(item['id'] == 'quiz_performance' for item in data['unavailable']))
        self.assertEqual(enrollment.course_id, self.course.pk)

    def test_overview_honours_the_requested_window_and_bucket(self):
        self.login(self.platform_admin)
        data = self.client.get('/api/admin/analytics/overview/?bucket=day&from='
                               f'{(timezone.now() - timedelta(days=3)).date().isoformat()}').data
        self.assertEqual(data['range']['bucket'], 'day')
        self.assertLessEqual(len(data['range']['from']), 10)

    def test_csv_export_streams_rows_for_the_requested_report(self):
        self.login(self.platform_admin)
        response = self.client.get('/api/admin/analytics/export/?report=registrations')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        body = b''.join(response.streaming_content).decode() \
            if getattr(response, 'streaming', False) else response.content.decode()
        self.assertIn('email', body.splitlines()[0])

    def test_an_unknown_report_name_lists_what_is_available(self):
        self.login(self.platform_admin)
        response = self.client.get('/api/admin/analytics/export/?report=ghosts')
        self.assertEqual(response.status_code, 400)
        self.assertIn('registrations', response.data['available'])

    def test_export_needs_a_capability_analytics_view_alone_does_not_grant(self):
        self.login(self.instructor)
        self.assertEqual(self.client.get('/api/admin/analytics/overview/').status_code, 200)
        self.assertEqual(self.client.get('/api/admin/analytics/export/?report=registrations')
                         .status_code, 403)

    def test_a_student_cannot_read_analytics(self):
        self.login(self.student)
        self.assertEqual(self.client.get('/api/admin/analytics/overview/').status_code, 403)


class AdminActionLogTests(TestCase):

    def test_audit_rows_are_append_only(self):
        actor = User.objects.create_superuser(username='auditor', password='pw',
                                              email='auditor@example.com')
        course = make_course(title='Audit Me', slug='audit-me')
        row = record_admin_action(actor, 'course.create', obj=course, label=course.title)
        self.assertEqual(row.actor_role, 'administrator')
        with self.assertRaises(IntegrityError):
            row.delete()
        with self.assertRaises(IntegrityError):
            AdminActionLog.objects.create(pk=row.pk, actor=row.actor, action='tampered')


class AdminRolesDirectoryTests(StudioAccountsMixin, TestCase):

    def test_the_directory_describes_the_groups_and_capabilities_that_exist(self):
        self.login(self.super_admin)
        data = self.client.get('/api/admin/roles/').data
        names = {row['name'] for row in data['roles']}
        self.assertIn('Course Editor', names)
        self.assertIn('Student Support', names)
        course_editor = next(row for row in data['roles'] if row['name'] == 'Course Editor')
        self.assertIn(admin_access.COURSE_STUDIO_EDIT, course_editor['capabilities'])
        self.assertNotIn(admin_access.COURSE_PUBLISH, course_editor['capabilities'])
        self.assertTrue(data['can_assign_roles'])

    def test_only_a_superuser_may_assign_roles(self):
        self.login(self.platform_admin)
        data = self.client.get('/api/admin/roles/').data
        self.assertFalse(data['can_assign_roles'])
        response = self.client.post('/api/admin/roles/', {
            'user_id': self.editor.pk, 'groups': ['Academic Manager'],
        }, format='json')
        self.assertEqual(response.status_code, 403, response.data)

    def test_an_administrator_cannot_grant_themselves_more_power(self):
        self.login(self.super_admin)
        response = self.client.post('/api/admin/roles/', {
            'user_id': self.super_admin.pk, 'groups': ['Student Support'],
        }, format='json')
        self.assertEqual(response.status_code, 400, response.data)
        self.assertEqual(set(self.super_admin.groups.values_list('name', flat=True)), set())


