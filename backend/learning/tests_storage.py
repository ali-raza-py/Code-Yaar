from unittest.mock import patch

from django.test import SimpleTestCase, override_settings

from .models import UserProfile


class AvatarStorageUrlTests(SimpleTestCase):
    @override_settings(BACKEND_URL='https://api.example.test')
    def test_local_media_avatar_keeps_existing_api_url(self):
        profile = UserProfile(avatar='avatars/learner.png')

        self.assertEqual(
            profile.avatar_url(),
            'https://api.example.test/avatars/learner.png',
        )

    @override_settings(CLOUD_STORAGE_ENABLED=True)
    @patch(
        'django.core.files.storage.default_storage.url',
        return_value='https://media.example.test/avatars/learner.png?signature=test',
    )
    def test_cloud_media_avatar_uses_configured_storage_url(self, storage_url):
        profile = UserProfile(avatar='avatars/learner.png')

        self.assertEqual(
            profile.avatar_url(),
            'https://media.example.test/avatars/learner.png?signature=test',
        )
        storage_url.assert_called_once_with('avatars/learner.png')

    @override_settings(CLOUD_STORAGE_ENABLED=True)
    def test_legacy_external_avatar_url_is_preserved(self):
        profile = UserProfile(avatar='https://legacy.example.test/avatar.png')

        self.assertEqual(
            profile.avatar_url(),
            'https://legacy.example.test/avatar.png',
        )
