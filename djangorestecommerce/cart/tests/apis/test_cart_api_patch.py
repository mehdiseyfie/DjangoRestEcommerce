from decimal import Decimal

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from djangorestecommerce.cart.tests.factories import CartFactory, CartItemFactory
from djangorestecommerce.users.tests.factories import ProfileFactory


class CartApiPatchTest(APITestCase):
    """
    Regression tests for bug #3: PATCH /cart/<slug>/ was returning 400
    (Bad Request) for a non-existent item slug instead of 404 (Not Found),
    because the view's `except Exception` block was catching the Http404
    raised by `get_item_by_slug` (which uses get_object_or_404).
    """

    def setUp(self):
        self.profile = ProfileFactory()
        self.client = APIClient()
        self.client.force_authenticate(user=self.profile.user)

    def test_patch_with_nonexistent_item_slug_returns_404(self):
        # Cart exists for the authenticated customer, but no item has
        # this slug.
        CartFactory(customer=self.profile)
        url = reverse("api:cart:cart-detail-by-slug", args=["this-slug-does-not-exist"])

        response = self.client.patch(url, data={"quantity": 2}, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_with_item_belonging_to_another_customer_returns_404(self):
        # Item exists, but belongs to a different customer's cart.
        other_cart = CartFactory()
        other_item = CartItemFactory(cart=other_cart)
        CartFactory(customer=self.profile)  # our own (empty) cart
        url = reverse("api:cart:cart-detail-by-slug", args=[other_item.slug])

        response = self.client.patch(url, data={"quantity": 2}, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_with_valid_item_slug_updates_quantity(self):
        # Sanity/happy-path check, so the 404 fix above isn't verified in
        # isolation from the working case.
        cart = CartFactory(customer=self.profile)
        item = CartItemFactory(cart=cart, quantity=1, price=Decimal("20.00"))
        url = reverse("api:cart:cart-detail-by-slug", args=[item.slug])

        response = self.client.patch(url, data={"quantity": 3}, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["quantity"], 3)
