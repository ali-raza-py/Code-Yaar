"""Tests for the Developer Portfolio & Project Showcase feature.

Covers the security-critical behaviours the brief demands: ownership is
enforced server-side, private projects never leak through public endpoints,
uploads/URLs are validated, and publishing + privacy toggles behave.
"""

import io

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from PIL import Image
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.test import APIClient

from .models import (
    UserProfile, Portfolio, StudentProject, ProjectImage, Skill, UserSkill, Follow,
    Achievement, UserAchievement,
)
from .serializers import _validate_project_image


def _png_upload(name='cover.png'):
    """Build a real (tiny) PNG so ImageField validation is exercised honestly."""
    buf = io.BytesIO()
    Image.new('RGB', (4, 4), (200, 30, 30)).save(buf, format='PNG')
    return SimpleUploadedFile(name, buf.getvalue(), content_type='image/png')


class _Namespace:
    """Minimal stand-in for an uploaded file, for direct validator tests."""

    def __init__(self, size, content_type):
        self.size = size
        self.content_type = content_type


class PortfolioProjectCrudTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='dev', password='pw', email='dev@example.com')
        UserProfile.objects.create(user=self.user, email_verified=True)
        self.client.force_authenticate(user=self.user)

    def _create(self, **overrides):
        payload = {
            'title': 'My App',
            'short_description': 'A useful app.',
            'overview': 'Does things.',
            'category': 'web_development',
            'technologies': ['Python', 'React'],
        }
        payload.update(overrides)
        return self.client.post('/api/portfolio/projects/', payload, format='json')

    def test_create_project(self):
        response = self._create()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(StudentProject.objects.filter(user=self.user).count(), 1)
        project = StudentProject.objects.get(user=self.user)
        self.assertEqual(project.slug, 'my-app')
        self.assertEqual(project.visibility, 'public')

    def test_slug_unique_per_user(self):
        self._create(title='Same')
        self._create(title='Same')
        slugs = list(StudentProject.objects.filter(user=self.user).values_list('slug', flat=True))
        self.assertEqual(sorted(slugs), ['same', 'same-2'])

    def test_list_scoped_to_owner(self):
        self._create()
        other = User.objects.create_user(username='other', password='pw')
        UserProfile.objects.create(user=other)
        StudentProject.objects.create(user=other, slug='theirs', title='Theirs',
                                      short_description='x', category='other')
        response = self.client.get('/api/portfolio/projects/')
        titles = [r['title'] for r in response.data['results']]
        self.assertEqual(titles, ['My App'])

    def test_edit_project(self):
        self._create()
        project = StudentProject.objects.get(user=self.user)
        response = self.client.patch(
            f'/api/portfolio/projects/{project.id}/',
            {'title': 'Renamed'}, format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        project.refresh_from_db()
        self.assertEqual(project.title, 'Renamed')
        self.assertEqual(project.slug, 'renamed')

    def test_delete_project(self):
        self._create()
        project = StudentProject.objects.get(user=self.user)
        response = self.client.delete(f'/api/portfolio/projects/{project.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(StudentProject.objects.filter(id=project.id).exists())

    def test_another_user_cannot_access_project(self):
        self._create()
        project = StudentProject.objects.get(user=self.user)
        attacker = User.objects.create_user(username='attacker', password='pw')
        UserProfile.objects.create(user=attacker)
        self.client.force_authenticate(user=attacker)
        for method, url in [
            ('get', f'/api/portfolio/projects/{project.id}/'),
            ('patch', f'/api/portfolio/projects/{project.id}/'),
            ('delete', f'/api/portfolio/projects/{project.id}/'),
        ]:
            with self.subTest(method=method):
                response = getattr(self.client, method)(
                    url, {'title': 'hijack'} if method == 'patch' else None,
                    format='json',
                )
                self.assertIn(response.status_code, (
                    status.HTTP_404_NOT_FOUND, status.HTTP_403_FORBIDDEN,
                ))
        self.assertTrue(StudentProject.objects.filter(id=project.id).exists())

    def test_requires_authentication(self):
        self.client.force_authenticate(user=None)
        self.assertEqual(self.client.get('/api/portfolio/me/').status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(self.client.get('/api/portfolio/projects/').status_code, status.HTTP_401_UNAUTHORIZED)


class PortfolioFeaturedAndReorderTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='feat', password='pw')
        UserProfile.objects.create(user=self.user)
        self.client.force_authenticate(user=self.user)

    def _make(self, title, featured=False):
        return StudentProject.objects.create(
            user=self.user, title=title, slug=title.lower().replace(' ', '-'),
            short_description='x', category='other', featured=featured,
        )

    def test_featured_cap_enforced(self):
        for i in range(3):
            self._make(f'Project {i}', featured=True)
        response = self.client.post('/api/portfolio/projects/', {
            'title': 'Fourth', 'short_description': 'x',
            'category': 'other', 'featured': True,
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('featured', response.data)

    def test_reorder_persists(self):
        a = self._make('A')
        b = self._make('B')
        response = self.client.post('/api/portfolio/projects/reorder/', {
            'items': [{'id': a.id, 'display_order': 5}, {'id': b.id, 'display_order': 1}],
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        a.refresh_from_db(); b.refresh_from_db()
        self.assertEqual((a.display_order, b.display_order), (5, 1))

    def test_reorder_rejects_foreign_ids(self):
        other = User.objects.create_user(username='o', password='pw')
        foreign = StudentProject.objects.create(user=other, title='F', slug='f',
                                                short_description='x', category='other')
        response = self.client.post('/api/portfolio/projects/reorder/', {
            'items': [{'id': foreign.id, 'display_order': 1}],
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class PortfolioPublishTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='pub', password='pw')
        self.profile = UserProfile.objects.create(user=self.user, is_profile_public=True)
        self.client.force_authenticate(user=self.user)

    def test_me_get_creates_lazily(self):
        self.assertFalse(Portfolio.objects.filter(user=self.user).exists())
        response = self.client.get('/api/portfolio/me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(Portfolio.objects.filter(user=self.user).exists())

    def test_publish_and_unpublish(self):
        self.client.post('/api/portfolio/publish/', {}, format='json')
        self.assertTrue(Portfolio.objects.get(user=self.user).is_published)
        self.client.post('/api/portfolio/unpublish/', {}, format='json')
        self.assertFalse(Portfolio.objects.get(user=self.user).is_published)

    def test_public_portfolio_only_when_published(self):
        StudentProject.objects.create(user=self.user, title='P', slug='p',
                                      short_description='x', category='other', visibility='public')
        # Not published yet -> 404 for anonymous visitors.
        self.client.force_authenticate(user=None)
        self.assertEqual(self.client.get('/api/portfolio/pub/').status_code, status.HTTP_404_NOT_FOUND)
        # Publish, then it is visible.
        self.client.force_authenticate(user=self.user)
        self.client.post('/api/portfolio/publish/', {}, format='json')
        self.client.force_authenticate(user=None)
        response = self.client.get('/api/portfolio/pub/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['projects']), 1)

    def test_private_account_can_publish_portfolio_independently(self):
        self.profile.is_profile_public = False
        self.profile.save()
        self.client.post('/api/portfolio/publish/', {}, format='json')
        self.client.force_authenticate(user=None)
        response = self.client.get('/api/portfolio/pub/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class PortfolioVisibilityLeakTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='vis', password='pw')
        UserProfile.objects.create(user=self.user, is_profile_public=True)
        self.client.force_authenticate(user=self.user)
        StudentProject.objects.create(user=self.user, title='Shown', slug='shown',
                                      short_description='x', category='other', visibility='public')
        StudentProject.objects.create(user=self.user, title='Secret', slug='secret',
                                      short_description='x', category='other', visibility='private')
        self.client.post('/api/portfolio/publish/', {}, format='json')
        self.client.force_authenticate(user=None)

    def test_private_project_absent_from_public_portfolio(self):
        response = self.client.get('/api/portfolio/vis/')
        titles = [p['title'] for p in response.data['projects']]
        self.assertEqual(titles, ['Shown'])

    def test_private_project_detail_is_404(self):
        self.assertEqual(
            self.client.get('/api/portfolio/vis/projects/secret/').status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_public_project_detail_available(self):
        response = self.client.get('/api/portfolio/vis/projects/shown/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Shown')
        self.assertNotIn('visibility', response.data)


class PortfolioSkillAchievementPrivacyTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='sec', password='pw')
        self.profile = UserProfile.objects.create(user=self.user, is_profile_public=True, show_badges=True)
        skill = Skill.objects.create(name='Python', category='Programming Languages')
        UserSkill.objects.create(user=self.user, skill=skill, proficiency=3)
        achievement = Achievement.objects.create(
            slug='first-course', title='First Course', description='d',
            category='course', difficulty='beginner', condition_type='course_complete',
        )
        UserAchievement.objects.create(user=self.user, achievement=achievement, status='active')
        self.portfolio = Portfolio.objects.create(user=self.user, is_published=True)
        self.client.force_authenticate(user=None)

    def test_skills_and_achievements_visible_by_default(self):
        response = self.client.get('/api/portfolio/sec/')
        self.assertTrue(response.data['skills']['visible'])
        self.assertTrue(response.data['achievements']['visible'])
        self.assertEqual(response.data['achievements']['items'][0]['title'], 'First Course')

    def test_show_skills_false_hides_skills(self):
        self.client.force_authenticate(user=self.user)
        self.client.patch('/api/portfolio/me/', {'show_skills': False}, format='json')
        self.client.force_authenticate(user=None)
        response = self.client.get('/api/portfolio/sec/')
        self.assertFalse(response.data['skills']['visible'])
        self.assertEqual(response.data['skills']['groups'], [])

    def test_show_achievements_false_hides_achievements(self):
        self.client.force_authenticate(user=self.user)
        self.client.patch('/api/portfolio/me/', {'show_achievements': False}, format='json')
        self.client.force_authenticate(user=None)
        response = self.client.get('/api/portfolio/sec/')
        self.assertFalse(response.data['achievements']['visible'])

    def test_location_and_social_gated(self):
        self.profile.location = 'Karachi'
        self.profile.github_url = 'https://github.com/sec'
        self.profile.save()
        self.client.force_authenticate(user=self.user)
        self.client.patch('/api/portfolio/me/',
                          {'show_location': False, 'show_social_links': False}, format='json')
        self.client.force_authenticate(user=None)
        response = self.client.get('/api/portfolio/sec/')
        self.assertEqual(response.data['location'], '')
        self.assertEqual(response.data['social_links'], {})


class PortfolioMediaAndUrlValidationTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='media', password='pw')
        UserProfile.objects.create(user=self.user)
        self.client.force_authenticate(user=self.user)

    def test_invalid_github_url_rejected(self):
        response = self.client.post('/api/portfolio/projects/', {
            'title': 'X', 'short_description': 'x', 'category': 'other',
            'github_url': 'not-a-url',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('github_url', response.data)

    def test_cover_image_uploaded(self):
        response = self.client.post('/api/portfolio/projects/', {
            'title': 'With Cover', 'short_description': 'x', 'category': 'other',
            'cover_image': _png_upload(),
        }, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['cover_image_url'])
    def test_add_and_remove_project_image(self):
        project = StudentProject.objects.create(user=self.user, title='P', slug='p',
                                                short_description='x', category='other')
        response = self.client.post(
            f'/api/portfolio/projects/{project.id}/images/',
            {'image': _png_upload('shot.png'), 'alt_text': 'A screenshot'},
            format='multipart',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        image_id = response.data['id']
        self.assertEqual(ProjectImage.objects.filter(project=project).count(), 1)
        delete = self.client.delete(f'/api/portfolio/projects/{project.id}/images/{image_id}/')
        self.assertEqual(delete.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(ProjectImage.objects.filter(project=project).count(), 0)

    def test_rejects_oversize_image(self):
        huge = _Namespace(size=6 * 1024 * 1024, content_type='image/png')
        with self.assertRaises(ValidationError):
            _validate_project_image(huge, 'cover_image')

    def test_rejects_disallowed_type(self):
        gif = _Namespace(size=1024, content_type='image/gif')
        with self.assertRaises(ValidationError):
            _validate_project_image(gif, 'cover_image')

    def test_accepts_valid_png(self):
        ok = _Namespace(size=1024, content_type='image/png')
        self.assertIs(_validate_project_image(ok, 'cover_image'), ok)


class PortfolioFollowTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.owner = User.objects.create_user(username='follow-owner', password='pw')
        UserProfile.objects.create(user=self.owner, is_profile_public=True)
        Portfolio.objects.create(user=self.owner, is_published=True)
        self.follower = User.objects.create_user(username='follower', password='pw')
        UserProfile.objects.create(user=self.follower, is_profile_public=True)
        self.client.force_authenticate(user=self.follower)

    def test_follow_and_unfollow_are_idempotent(self):
        first = self.client.post('/api/users/follow-owner/follow/')
        second = self.client.post('/api/users/follow-owner/follow/')
        self.assertEqual(first.status_code, status.HTTP_200_OK)
        self.assertEqual(second.data['followers_count'], 1)
        self.assertEqual(Follow.objects.count(), 1)

        removed = self.client.delete('/api/users/follow-owner/follow/')
        self.assertEqual(removed.data['following'], False)
        self.assertEqual(Follow.objects.count(), 0)

    def test_self_follow_is_rejected(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post('/api/users/follow-owner/follow/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_public_portfolio_exposes_relationship_state(self):
        response = self.client.get('/api/portfolio/follow-owner/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['followers_count'], 0)
        self.assertFalse(response.data['is_following'])
        self.client.post('/api/users/follow-owner/follow/')
        response = self.client.get('/api/portfolio/follow-owner/')
        self.assertEqual(response.data['followers_count'], 1)
        self.assertTrue(response.data['is_following'])
