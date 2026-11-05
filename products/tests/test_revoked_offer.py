"""An offer made before a revocation must not complete after it (FR38, FR39).

Creating an offer refuses a revoked product, but the offer itself stays open.
Accepting it later must refuse too, or a revoked passport changes hands.
"""

# ---- External imports ----
from django.test import TestCase

# ---- Internal imports ----
from products.models import CustodyTransfer, TransferState
from test_support.factories import make_company, make_product, make_user


# ---- Public API ----
class RevokedProductOfferTests(TestCase):
    def setUp(self):
        self.owner = make_user(email="maker@tuchin.co")
        self.buyer = make_user(email="buyer@example.com")
        self.product = make_product(company=make_company(owner=self.owner, status="APPROVED"))
        self.offer = CustodyTransfer.objects.create(
            product=self.product,
            from_holder=self.owner,
            to_holder=self.buyer,
            note="",
        )
        self.product.revoke(actor=self.owner, reason="Counterfeit reports")

    def test_an_offer_made_before_revocation_cannot_be_accepted(self):
        with self.assertRaises(ValueError):
            self.offer.accept(actor=self.buyer)

        self.offer.refresh_from_db()
        self.assertEqual(self.offer.state, TransferState.INITIATED)

    def test_the_holder_does_not_change_when_such_an_offer_is_refused(self):
        with self.assertRaises(ValueError):
            self.offer.accept(actor=self.buyer)

        self.product.refresh_from_db()
        self.assertEqual(self.product.current_holder, self.owner)
