from django.test import TestCase

from djangorestecommerce.cart.selectors import get_cart_by_customer
from djangorestecommerce.cart.tests.factories import CartFactory
from djangorestecommerce.users.tests.factories import ProfileFactory


class GetCartByCustomerTest(TestCase):

    def test_returns_active_cart_for_customer(self):
        profile = ProfileFactory()
        cart = CartFactory(customer=profile, is_active=True)

        result = get_cart_by_customer(customer=profile)

        self.assertEqual(result, cart)

    def test_returns_none_when_no_active_cart(self):
        profile = ProfileFactory()
        CartFactory(customer=profile, is_active=False)

        result = get_cart_by_customer(customer=profile)

        self.assertIsNone(result)

    def test_returns_none_when_customer_has_no_cart(self):
        profile = ProfileFactory()

        result = get_cart_by_customer(customer=profile)

        self.assertIsNone(result)