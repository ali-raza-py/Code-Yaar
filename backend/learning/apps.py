from django.apps import AppConfig
from django.db.models.signals import post_migrate


class LearningConfig(AppConfig):
    name = 'learning'

    def ready(self):
        # Groups must be created after Django has generated model permissions,
        # which happens during each app's `post_migrate`. Connecting with
        # `sender=self` guarantees the learning permissions exist first.
        from .services.auth import sync_role_groups

        post_migrate.connect(
            sync_role_groups,
            sender=self,
            dispatch_uid='learning.sync_role_groups',
        )
