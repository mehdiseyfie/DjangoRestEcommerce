from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from djangorestecommerce.cart.tests.factories import CartFactory, CartItemFactory
from djangorestecommerce.users.tests.factories import ProfileFactory


class OrderApiPostTest(APITestCase):
    """
    Regression test for bug #3 on POST /orders/.
    get_shipping_address_by_id() (used for shipping_address_id /
    billing_address_id) raises Http404 for an address that doesn't
    belong to the customer or doesn't exist; this used to be caught by
    `except Exception` and turned into a misleading 400.
    """

    def setUp(self):
        self.profile = ProfileFactory()
        self.client = APIClient()
        self.client.force_authenticate(user=self.profile.user)

    def test_post_with_nonexistent_shipping_address_id_returns_404(self):
        cart = CartFactory(customer=self.profile)
        CartItemFactory(cart=cart)
        url = reverse("api:orders:order-list")

        response = self.client.post(
            url,
            data={
                "shipping_method": "standard",
                "shipping_address_id": 999999,  # does not exist
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
