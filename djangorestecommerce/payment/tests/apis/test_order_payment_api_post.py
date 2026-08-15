from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from djangorestecommerce.orders.tests.factories import OrderFactory
from djangorestecommerce.users.tests.factories import ProfileFactory


class OrderPaymentApiPostTest(APITestCase):
    """
    Regression test for bug #3 on POST /payment/<slug>/.
    get_order_by_slug() raises Http404 for an order that doesn't belong
    to the customer or doesn't exist; this used to be caught by
    `except Exception` and turned into a misleading 400.
    """

    def setUp(self):
        self.profile = ProfileFactory()
        self.client = APIClient()
        self.client.force_authenticate(user=self.profile.user)

    def test_post_with_nonexistent_order_slug_returns_404(self):
        url = reverse("api:payment:order-payment", args=["this-slug-does-not-exist"])

        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_post_with_order_belonging_to_another_customer_returns_404(self):
        other_order = OrderFactory()  # different customer
        url = reverse("api:payment:order-payment", args=[other_order.slug])

        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
