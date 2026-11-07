"""The SMTP connection is configured from the environment, never from the code."""

import importlib
import os
from unittest import mock

from django.test import SimpleTestCase

import config.settings

SMTP_ENVIRONMENT = {
    "EMAIL_BACKEND": "django.core.mail.backends.smtp.EmailBackend",
    "EMAIL_HOST": "smtp.gmail.com",
    "EMAIL_PORT": "587",
    "EMAIL_HOST_USER": "originpass@example.com",
    "EMAIL_HOST_PASSWORD": "app-password",
    "EMAIL_USE_TLS": "True",
}
EMAIL_NAMES = [*SMTP_ENVIRONMENT, "DEFAULT_FROM_EMAIL"]


class EmailSettingsTests(SimpleTestCase):
    def _settings_with(self, environment):
        clean = {key: value for key, value in os.environ.items() if key not in EMAIL_NAMES}
        with (
            mock.patch.dict(os.environ, {**clean, **environment}, clear=True),
            mock.patch("dotenv.load_dotenv"),
        ):
            return importlib.reload(config.settings)

    def tearDown(self):
        importlib.reload(config.settings)

    def test_smtp_settings_read_from_environment(self):
        settings = self._settings_with(SMTP_ENVIRONMENT)

        self.assertEqual(settings.EMAIL_BACKEND, SMTP_ENVIRONMENT["EMAIL_BACKEND"])
        self.assertEqual(settings.EMAIL_HOST, "smtp.gmail.com")
        self.assertEqual(settings.EMAIL_PORT, 587)
        self.assertEqual(settings.EMAIL_HOST_USER, "originpass@example.com")
        self.assertEqual(settings.EMAIL_HOST_PASSWORD, "app-password")
        self.assertTrue(settings.EMAIL_USE_TLS)

    def test_console_backend_by_default(self):
        settings = self._settings_with({})

        self.assertEqual(settings.EMAIL_BACKEND, "django.core.mail.backends.console.EmailBackend")
        self.assertEqual(settings.EMAIL_PORT, 587)
        self.assertTrue(settings.EMAIL_USE_TLS)
        self.assertEqual(settings.EMAIL_HOST_PASSWORD, "")
