"""The error pages are rendered by Django's own handlers, from this project's templates."""

from django.test import TestCase


class ErrorPageTests(TestCase):
    def test_an_unknown_address_renders_the_project_404_page(self):
        response = self.client.get("/no-such-page/")

        self.assertContains(response, "Página no encontrada", status_code=404)
        self.assertTemplateUsed(response, "404.html")
