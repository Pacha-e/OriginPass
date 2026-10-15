"""FR57: five failed attempts in fifteen minutes lock the (email, IP) pair for
fifteen minutes, and the locked answer is the same one a wrong password gets
(FR04).

The trick being tested: the lock must never announce itself. A test that
asserted "we are locked" by string-matching a lockout message would lock the
implementation into leaking that fact to a crawler.
"""

from datetime import timedelta

from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.forms import AUTHENTICATION_ERROR
from accounts.models import LoginAttempt
from test_support.factories import OWNER_PASSWORD, make_user


class LoginThrottleTests(TestCase):
    def setUp(self):
        self.user = make_user(email="holder@example.com")
        self.url = reverse("accounts:login")
        # The form demands a CSRF token unless the test client plays by the
        # real rules; Client enforces them when enforce_csrf_checks is on,
        # which is the point.
        self.client = Client(enforce_csrf_checks=True)

    def _post(self, email="holder@example.com", password="wrong-password"):
        # The login form takes its CSRF from the GET; the shortcut of a raw
        # POST would fail before the throttle even runs. Two-stepping mirrors
        # what a real attacker would face.
        self.client.get(self.url)
        csrftoken = self.client.cookies["csrftoken"].value
        return self.client.post(
            self.url,
            {"email": email, "password": password, "csrfmiddlewaretoken": csrftoken},
        )

    def test_first_failure_returns_the_plain_authentication_error(self):
        response = self._post()
        self.assertContains(response, AUTHENTICATION_ERROR, status_code=200)

    def test_fifth_failure_locks_the_address(self):
        for _ in range(LoginAttempt.MAX_FAILURES):
            self._post()
        attempt = LoginAttempt.objects.get(email=self.user.email)
        self.assertIsNotNone(attempt.locked_until)
        self.assertGreater(attempt.locked_until, timezone.now())

    def test_locked_address_gets_the_same_message_as_a_wrong_password(self):
        for _ in range(LoginAttempt.MAX_FAILURES):
            self._post()
        response = self._post()
        self.assertContains(response, AUTHENTICATION_ERROR, status_code=200)
        self.assertNotContains(response, "locked", status_code=200)

    def test_a_successful_login_wipes_the_streak(self):
        for _ in range(3):
            self._post()
        attempt = LoginAttempt.objects.get(email=self.user.email)
        self.assertEqual(attempt.failed_count, 3)
        # Now with the right password.
        self.client.get(self.url)
        csrftoken = self.client.cookies["csrftoken"].value
        response = self.client.post(
            self.url,
            {
                "email": self.user.email,
                "password": OWNER_PASSWORD,
                "csrfmiddlewaretoken": csrftoken,
            },
        )
        self.assertEqual(response.status_code, 302)
        attempt.refresh_from_db()
        self.assertEqual(attempt.failed_count, 0)
        self.assertIsNone(attempt.locked_until)

    def test_a_fail_streak_older_than_the_window_resets(self):
        for _ in range(LoginAttempt.MAX_FAILURES):
            self._post()
        attempt = LoginAttempt.objects.get(email=self.user.email)
        attempt.first_failed_at = timezone.now() - timedelta(
            minutes=LoginAttempt.WINDOW_MINUTES + 1
        )
        attempt.failed_count = 1
        attempt.locked_until = None
        attempt.save()
        self._post()
        attempt.refresh_from_db()
        # Outside the window the streak starts over at 1, not 2.
        self.assertEqual(attempt.failed_count, 1)

    def test_other_address_from_same_ip_is_not_locked(self):
        # The lock is per (email, IP), not per IP alone: a shared office NAT
        # must not hold a colleague hostage.
        for _ in range(LoginAttempt.MAX_FAILURES):
            self._post(email="attacker@example.com")
        attempt = LoginAttempt.objects.get(email="attacker@example.com")
        self.assertTrue(attempt.is_locked())
        response = self._post(email="holder@example.com")
        self.assertContains(response, AUTHENTICATION_ERROR, status_code=200)

    def test_an_address_longer_than_the_column_is_refused_not_crashed(self):
        """Defect: an address over 254 characters failed the insert with a server error."""
        response = self._post(email="a" * 300 + "@example.com")
        self.assertContains(response, AUTHENTICATION_ERROR, status_code=200)

    def test_changing_the_case_of_the_address_does_not_dodge_the_lock(self):
        for _ in range(LoginAttempt.MAX_FAILURES):
            self._post(email="Holder@Example.com")
        self.assertTrue(LoginAttempt.is_locked_out("holder@example.com", "127.0.0.1"))
