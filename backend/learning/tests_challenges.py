"""End-to-end tests for the standalone Practice challenges (spec: /challenges).

Covers the full learner journey the workspace page depends on:

- Public listing and detail are safe: no hidden tests or reference solutions.
- ``run`` grades the visible sample tests and requires an account.
- ``submit`` grades the hidden tests server-side, awards XP exactly once,
  replays an already-processed ``submission_id`` without re-grading, and
  rejects a bare starter scaffold.

The code is genuinely executed through the configured ``SubprocessSandbox``,
so these tests assert on real verdicts — never fabricated ones.
"""

from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from .models import (
    Challenge, ChallengeSubmission, UserProfile, XPTransaction,
)


SUM_TWO_STARTER = (
    'import sys\n\n'
    'def solve(a, b):\n'
    '    # Return the sum of a and b.\n'
    '    return 0\n\n'
    'data = sys.stdin.read().split()\n'
    'print(solve(int(data[0]), int(data[1])) if len(data) > 1 else 0)\n'
)

SUM_TWO_SOLUTION = (
    'import sys\n\n'
    'def solve(a, b):\n'
    '    return a + b\n\n'
    'data = sys.stdin.read().split()\n'
    'print(solve(int(data[0]), int(data[1])) if len(data) > 1 else 0)\n'
)


class ChallengeJourneyTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='learner', password='pass123', email='learner@example.com',
        )
        self.profile = UserProfile.objects.create(
            user=self.user, xp_points=0, email_verified=True,
        )

        self.challenge = Challenge.objects.create(
            slug='sum-two', title='Sum Two', description='Add two numbers.',
            difficulty='beginner', topic='Basics', estimated_minutes=5,
            languages=['python'],
            starter_code=SUM_TWO_STARTER,
            solution_code=SUM_TWO_SOLUTION,
            problem_statement='Read two integers and print their sum.',
            requirements=['Read two space-separated integers.', 'Print their sum.'],
            hints=['a + b'],
            sample_tests=[{'input': '2 3', 'expected_output': '5'}],
            hidden_tests=[
                {'input': '10 20', 'expected_output': '30'},
                {'input': '-5 5', 'expected_output': '0'},
            ],
            xp_reward=75, is_active=True,
        )

    # ── Public, unauthenticated reads ────────────────────────────────────────

    def test_list_is_public_and_safe(self):
        response = self.client.get('/api/challenges/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        row = next(r for r in response.data['results'] if r['slug'] == 'sum-two')
        self.assertFalse(row['solved'])
        self.assertEqual(row['attempts'], 0)
        # The card projection must never leak grading content.
        self.assertNotIn('hidden_tests', row)
        self.assertNotIn('solution_code', row)

    def test_detail_is_public_and_never_leaks_solutions(self):
        response = self.client.get('/api/challenges/sum-two/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for leaked in ('hidden_tests', 'solution_code', 'solution_code_cpp',
                       'solution_explanation', 'reference_solution'):
            self.assertNotIn(leaked, response.data)
        # Learner-facing content is present.
        self.assertIn('sample_tests', response.data)
        self.assertIn('problem_statement', response.data)

    def test_run_requires_authentication(self):
        self.client.force_authenticate(user=None)
        response = self.client.post(
            '/api/challenges/sum-two/run/', {'code': SUM_TWO_SOLUTION, 'language': 'python'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # ── Authenticated run (sample tests) ──────────────────────────────────────

    def test_run_with_correct_code_passes_sample_tests(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            '/api/challenges/sum-two/run/', {'code': SUM_TWO_SOLUTION, 'language': 'python'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['test_results']
        self.assertTrue(results)
        self.assertTrue(all(t['status'] == 'passed' for t in results))
        self.assertIn('1/1', response.data['summary'])

    def test_run_with_wrong_code_fails_sample_tests(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            '/api/challenges/sum-two/run/', {'code': SUM_TWO_STARTER, 'language': 'python'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(any(t['status'] != 'passed' for t in response.data['test_results']))

    def test_run_rejects_unsupported_language(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            '/api/challenges/sum-two/run/', {'code': SUM_TWO_SOLUTION, 'language': 'cpp'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # ── Authenticated submit (hidden tests + XP) ──────────────────────────────

    def test_submit_correct_awards_xp_once_and_reveals_solution(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            '/api/challenges/sum-two/submit/',
            {'code': SUM_TWO_SOLUTION, 'language': 'python', 'time_spent_seconds': 42},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'correct')
        self.assertTrue(response.data['solved'])
        self.assertEqual(response.data['xp_earned'], 75)
        self.assertIn('reference_solution', response.data)

        self.assertTrue(
            XPTransaction.objects.filter(
                user=self.user, action='challenge_complete',
            ).exists()
        )
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.xp_points, 75)

    def test_submit_starter_only_is_incorrect_and_no_xp(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            '/api/challenges/sum-two/submit/',
            {'code': SUM_TWO_STARTER, 'language': 'python'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'incorrect')
        self.assertEqual(response.data['xp_earned'], 0)
        self.assertFalse(ChallengeSubmission.objects.filter(status='correct').exists())

    def test_submit_replays_same_submission_id_without_regrading(self):
        self.client.force_authenticate(user=self.user)
        payload = {'code': SUM_TWO_SOLUTION, 'language': 'python',
                   'submission_id': '11111111-2222-3333-4444-555555555555'}
        first = self.client.post('/api/challenges/sum-two/submit/', payload, format='json')
        self.assertEqual(first.data['xp_earned'], 75)

        replay = self.client.post('/api/challenges/sum-two/submit/', payload, format='json')
        self.assertEqual(replay.status_code, status.HTTP_200_OK)
        self.assertTrue(replay.data['duplicate'])
        self.assertEqual(replay.data['xp_earned'], 0)
        # Still exactly one graded submission and one XP award.
        self.assertEqual(
            ChallengeSubmission.objects.filter(submission_id=payload['submission_id']).count(), 1,
        )
        self.assertEqual(XPTransaction.objects.filter(action='challenge_complete').count(), 1)

    def test_resubmitting_solution_does_not_double_award_xp(self):
        self.client.force_authenticate(user=self.user)
        url = '/api/challenges/sum-two/submit/'
        self.client.post(url, {'code': SUM_TWO_SOLUTION, 'language': 'python'}, format='json')
        second = self.client.post(
            url,
            {'code': SUM_TWO_SOLUTION, 'language': 'python',
             'submission_id': '99999999-8888-7777-6666-555555555555'},
            format='json',
        )
        self.assertTrue(second.data['solved'])
        # The unique challenge_complete guard keeps the second award at zero.
        self.assertEqual(second.data['xp_earned'], 0)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.xp_points, 75)
        self.assertEqual(
            XPTransaction.objects.filter(action='challenge_complete').count(), 1,
        )

    def test_solved_flag_reflects_correct_submission(self):
        self.client.force_authenticate(user=self.user)
        self.client.post(
            '/api/challenges/sum-two/submit/',
            {'code': SUM_TWO_SOLUTION, 'language': 'python'}, format='json',
        )
        detail = self.client.get('/api/challenges/sum-two/')
        self.assertTrue(detail.data['solved'])
        self.assertGreaterEqual(detail.data['attempts'], 1)

        listing = self.client.get('/api/challenges/')
        row = next(r for r in listing.data['results'] if r['slug'] == 'sum-two')
        self.assertTrue(row['solved'])
