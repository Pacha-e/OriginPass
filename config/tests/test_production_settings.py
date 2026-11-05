"""The settings a deployment depends on: static files served with DEBUG off."""

from django.conf import settings
from django.test import SimpleTestCase


class StaticFilesSettingsTests(SimpleTestCase):
    def test_whitenoise_serves_static_files_right_after_security_middleware(self):
        security = settings.MIDDLEWARE.index("django.middleware.security.SecurityMiddleware")

        self.assertEqual(
            settings.MIDDLEWARE[security + 1], "whitenoise.middleware.WhiteNoiseMiddleware"
        )
