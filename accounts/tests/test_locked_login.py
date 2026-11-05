"""A locked address must not reveal whether its password was right (FR57, FR04).

The lock answers with the same message a wrong password gets. Checking the
password while locked would still tell a prober whether the guess was correct,
because the answer differs by one message. The password must not be checked at
all during the lock.
"""

# ---- External imports ----
from unittest.mock import patch

from django.test import Client, TestCase
from django.urls import reverse

# ---- Internal imports ----
from accounts.forms import AUTHENTICATION_ERROR
from test_support.factories import OWNER_PASSWORD, make_user


# ---- Public API ----
class LockedLoginTests(TestCase):
    def setUp(self):
        self.user = make_user(email="holder@example.com")
        self.url = reverse("accounts:login")
        self.client = Client(enforce_csrf_checks=True)

    def _post(self, password):
        self.client.get(self.url)
        csrftoken = self.client.cookies["csrftoken"].value
        return self.client.post(
            self.url,
            {
                "email": "holder@example.com",
                "password": password,
                "csrfmiddlewaretoken": csrftoken,
            },
        )

    def _lock(self):
        for _ in range(5):
            self._post("wrong-password")

    def test_a_locked_address_does_not_check_the_password(self):
        self._lock()

        with patch("accounts.forms.authenticate") as authenticate:
            self._post(OWNER_PASSWORD)

        authenticate.assert_not_called()

    def test_a_locked_address_with_a_wrong_password_shows_one_error(self):
        self._lock()

        response = self._post("guess-that-is-wrong")

        self.assertContains(response, str(AUTHENTICATION_ERROR), count=1)
