import json

from django.db import connection
from django.db.models import JSONField
from django.test import SimpleTestCase

from learning.management.commands.migrate_sqlite_to_postgres import prepare_json_value


class PrepareJsonValueTests(SimpleTestCase):
    def test_decodes_sqlite_json_object_for_postgres_jsonb(self):
        value = prepare_json_value('{"enabled":true}', JSONField(), connection)

        self.assertEqual(value.obj, {'enabled': True})

    def test_preserves_json_string_values(self):
        value = prepare_json_value(json.dumps('hello'), JSONField(), connection)

        self.assertEqual(value.obj, 'hello')

    def test_preserves_null(self):
        self.assertIsNone(prepare_json_value(None, JSONField(), connection))

    def test_rejects_invalid_json(self):
        with self.assertRaises(json.JSONDecodeError):
            prepare_json_value('not-json', JSONField(), connection)
