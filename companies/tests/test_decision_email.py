"""FR53: the applicant is emailed the decision, with the stored reason.

The first version of these emails could not be rendered at all: approving or
rejecting an application failed with a template error, so the decision was the
thing that broke. These tests render the real templates.
"""

from django.core import mail
from django.test import TestCase
from django.urls import reverse

from test_support.factories import ADMIN_PASSWORD, make_admin, make_company


class DecisionEmailTests(TestCase):
    def setUp(self):
        self.company = make_company(email="weaver@tuchin.co")
        self.client.login(email=make_admin().email, password=ADMIN_PASSWORD)

    def test_an_approval_is_emailed_to_the_owner(self):
        self.client.post(reverse("companies:review_approve", args=[self.company.pk]))
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["weaver@tuchin.co"])
        self.assertIn(self.company.legal_name, mail.outbox[0].body)

    def test_a_rejection_carries_its_reason(self):
        self.client.post(
            reverse("companies:review_reject", args=[self.company.pk]),
            {"reason": "The registry code does not match."},
        )
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("The registry code does not match.", mail.outbox[0].body)
