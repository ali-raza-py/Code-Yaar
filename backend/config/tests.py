from unittest.mock import patch

from django.db import OperationalError
from django.test import SimpleTestCase


class ReadinessCheckTests(SimpleTestCase):
    @patch('config.urls.connection')
    def test_readiness_probe_executes_read_only_query(self, connection_mock):
        cursor = connection_mock.cursor.return_value.__enter__.return_value
        cursor.fetchone.return_value = (1,)

        response = self.client.get('/api/health/ready/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'status': 'ok', 'database': 'ok'})
        cursor.execute.assert_called_once_with('SELECT 1')

    @patch('config.urls.connection')
    def test_readiness_probe_hides_database_error_details(self, connection_mock):
        connection_mock.cursor.side_effect = OperationalError('unavailable')

        with self.assertLogs('config.urls', level='ERROR'):
            response = self.client.get('/api/health/ready/')
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json(), {'status': 'unavailable'})
