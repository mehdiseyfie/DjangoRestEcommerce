from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from djangorestecommerce.cart.models import CartItem
from djangorestecommerce.cart.tests.factories import CartFactory, CartItemFactory
from djangorestecommerce.users.tests.factories import ProfileFactory


class CartApiDeleteTest(APITestCase):
    """
    Regression tests for bug #3 on DELETE /cart/<slug>/.
    Same root cause as the PATCH case: get_item_by_slug raises Http404,
    which used to be swallowed by `except Exception` and turned into 400.
    """

    def setUp(self):
        self.profile = ProfileFactory()
        self.client = APIClient()
        self.client.force_authenticate(user=self.profile.user)

    def test_delete_with_nonexistent_item_slug_returns_404(self):
        CartFactory(customer=self.profile)
        url = reverse("api:cart:cart-detail-by-slug", args=["this-slug-does-not-exist"])

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_with_item_belonging_to_another_customer_returns_404(self):
        other_cart = CartFactory()
        other_item = CartItemFactory(cart=other_cart)
        CartFactory(customer=self.profile)
        url = reverse("api:cart:cart-detail-by-slug", args=[other_item.slug])

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        # Make sure the (wrong) item was NOT deleted as a side effect.
        self.assertTrue(CartItem.objects.filter(pk=other_item.pk).exists())

    def test_delete_with_valid_item_slug_removes_item(self):
        cart = CartFactory(customer=self.profile)
        item = CartItemFactory(cart=cart)
        url = reverse("api:cart:cart-detail-by-slug", args=[item.slug])

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(CartItem.objects.filter(pk=item.pk).exists())
