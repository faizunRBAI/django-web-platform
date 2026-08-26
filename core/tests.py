"""Tests for the landing page and the deploy health endpoint.

The verify stage curls both of these against the live instance, so a
regression here is caught in CI before it reaches the server.
"""
from django.test import SimpleTestCase


class HealthEndpointTests(SimpleTestCase):
    def test_health_returns_ok_json(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_health_content_type_is_json(self):
        response = self.client.get("/health")
        self.assertEqual(response["Content-Type"], "application/json")


class LandingPageTests(SimpleTestCase):
    def test_home_renders_html_page(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/html", response["Content-Type"])

    def test_home_uses_index_template(self):
        response = self.client.get("/")
        self.assertTemplateUsed(response, "index.html")
