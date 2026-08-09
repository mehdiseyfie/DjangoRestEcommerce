from django.test import TestCase

from djangorestecommerce.cart.models import Cart
from djangorestecommerce.cart.services import get_cart_or_create
from djangorestecommerce.cart.tests.factories import CartFactory
from djangorestecommerce.users.tests.factories import ProfileFactory


class GetCartOrCreateTest(TestCase):

    def test_returns_existing_active_cart(self):
        profile = ProfileFactory()
        existing = CartFactory(customer=profile, is_active=True)

        cart = get_cart_or_create(customer=profile)

        self.assertEqual(cart, existing)
        self.assertEqual(Cart.objects.filter(customer=profile, is_active=True).count(), 1)

    def test_creates_cart_when_none_exists(self):
        profile = ProfileFactory()

        cart = get_cart_or_create(customer=profile)

        self.assertIsNotNone(cart.pk)
        self.assertEqual(cart.customer, profile)
        self.assertTrue(cart.is_active)
        self.assertFalse(cart.is_ordered)
        self.assertEqual(cart.total_items, 0)
        self.assertEqual(cart.total_price, 0)
        self.assertTrue(Cart.objects.filter(customer=profile, is_active=True).exists())

    def test_does_not_return_inactive_cart(self):
        profile = ProfileFactory()
        CartFactory(customer=profile, is_active=False, is_ordered=True)

        cart = get_cart_or_create(customer=profile)

        self.assertTrue(cart.is_active)
        self.assertFalse(cart.is_ordered)
        self.assertEqual(Cart.objects.filter(customer=profile, is_active=True).count(), 1)