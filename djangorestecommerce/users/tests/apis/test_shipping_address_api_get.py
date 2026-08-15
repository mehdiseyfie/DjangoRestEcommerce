from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from djangorestecommerce.users.tests.factories import (
    ProfileFactory,
    ShippingAddressFactory,
)


class ShippingAddressApiGetTest(APITestCase):
    """
    Regression test for bug #3 on GET /users/shipping-address/<id>/.
    get_shipping_address_by_id() raises Http404 for an address that
    doesn't belong to the customer or doesn't exist; this used to be
    caught by `except Exception` and turned into a misleading 400.
    """

    def setUp(self):
        self.profile = ProfileFactory()
        self.client = APIClient()
        self.client.force_authenticate(user=self.profile.user)

    def test_get_with_nonexistent_id_returns_404(self):
        url = reverse("api:users:shipping-address-detail", args=[999999])

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_with_address_belonging_to_another_customer_returns_404(self):
        other_address = ShippingAddressFactory()  # different customer
        url = reverse("api:users:shipping-address-detail", args=[other_address.id])

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_with_own_address_returns_200(self):
        address = ShippingAddressFactory(customer=self.profile)
        url = reverse("api:users:shipping-address-detail", args=[address.id])

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
