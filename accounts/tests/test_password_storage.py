"""DBR11 - Store passwords as salted hashes, and never the plain text."""

from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from test_support.factories import make_user

PASSWORD = "Vueltiao-2026"


class PasswordStorageTests(TestCase):
    """DBR11 - Store passwords as salted hashes."""

    def test_the_password_is_stored_as_a_one_way_hash(self):
        user = make_user("weaver@tuchin.co")

        self.assertNotEqual(user.password, PASSWORD)
        self.assertNotIn(PASSWORD, user.password)
        self.assertTrue(user.password.startswith("pbkdf2_sha256$"))
        self.assertTrue(user.check_password(PASSWORD))

    def test_the_salt_is_unique_to_the_record(self):
        first = make_user("one@tuchin.co")
        second = make_user("two@tuchin.co")

        # Same password, different stored value: the salt differs per record.
        self.assertNotEqual(first.password, second.password)

    def test_no_plain_text_password_reaches_the_database(self):
        self.client.post(
            reverse("accounts:register"),
            {"email": "weaver@tuchin.co", "password1": PASSWORD, "password2": PASSWORD},
        )

        stored = User.objects.values_list("password", flat=True)

        self.assertFalse(any(PASSWORD in value for value in stored))
