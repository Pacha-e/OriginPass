"""The health endpoint: 200 while the database accepts connections, 503 when it refuses them."""

from unittest.mock import patch

from django.db import OperationalError
from django.test import SimpleTestCase
from django.urls import resolve

from pages import views


class HealthzTests(SimpleTestCase):
    def test_a_visitor_gets_ok_while_the_database_answers(self):
        with patch("pages.views.connection"):
            response = self.client.get("/healthz/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_a_database_that_does_not_answer_gets_503_without_error_details(self):
        with patch("pages.views.connection") as mock_connection:
            mock_connection.cursor.side_effect = OperationalError("internal detail")

            response = self.client.get("/healthz/")

        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json(), {"status": "unavailable"})
        self.assertNotIn("internal detail", response.content.decode())

    def test_the_health_url_is_served_by_healthz_and_not_by_the_home_page(self):
        match = resolve("/healthz/")

        self.assertIs(match.func, views.healthz)
        self.assertIsNot(match.func, views.home)
