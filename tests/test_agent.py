import os
import tempfile
import unittest
from unittest.mock import patch

from angel2500.integrations import _validate_url, IntegrationError, available_connectors
from angel2500.agent import get_task


class ConnectorTests(unittest.TestCase):
    def test_rejects_insecure_url(self):
        with self.assertRaises(IntegrationError):
            _validate_url("http://example.com/data")

    def test_rejects_embedded_credentials(self):
        with self.assertRaises(IntegrationError):
            _validate_url("https://user:password@example.com")

    def test_enabled_connector_names(self):
        with patch.dict(os.environ, {"ANGEL_CONNECTORS": "weather, github, weather"}):
            self.assertEqual(available_connectors(), ["github", "weather"])

    def test_missing_task(self):
        with tempfile.TemporaryDirectory() as d:
            with patch.dict(os.environ, {"ANGEL_DB_PATH": os.path.join(d, "tasks.db")}):
                self.assertIsNone(get_task("nonexistent"))


if __name__ == "__main__":
    unittest.main()
