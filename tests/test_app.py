import unittest
from unittest.mock import patch

from angel2500.app import create_app


class AppTests(unittest.TestCase):
    def setUp(self):
        self.client = create_app().test_client()

    def test_health(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["trading"], "disabled")

    def test_auth_missing_configuration(self):
        with patch.dict("os.environ", {}, clear=True):
            self.assertEqual(self.client.post("/api/chat", json={"message": "hi"}).status_code, 503)

    def test_rejects_unauthorized(self):
        with patch.dict("os.environ", {"ANGEL_API_TOKEN": "test-secret"}, clear=True):
            self.assertEqual(self.client.post("/api/chat", json={"message": "hi"}).status_code, 401)

    def test_validation(self):
        with patch.dict("os.environ", {"ANGEL_API_TOKEN": "test-secret"}, clear=True):
            response = self.client.post("/api/chat", headers={"Authorization": "Bearer test-secret"}, json={"message": ""})
            self.assertEqual(response.status_code, 400)

    def test_chat_mocked(self):
        with patch.dict("os.environ", {"ANGEL_API_TOKEN": "test-secret"}, clear=True):
            with patch("angel2500.app.answer_question", return_value="pong"):
                response = self.client.post("/api/chat", headers={"Authorization": "Bearer test-secret"}, json={"message": "ping"})
                self.assertEqual(response.json["answer"], "pong")


if __name__ == "__main__":
    unittest.main()
