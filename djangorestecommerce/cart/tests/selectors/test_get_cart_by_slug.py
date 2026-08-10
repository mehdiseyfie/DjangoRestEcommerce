from django.http import Http404
from django.test import TestCase

from djangorestecommerce.cart.selectors import get_cart_by_slug
from djangorestecommerce.cart.tests.factories import CartFactory


class GetCartBySlugTest(TestCase):

    def test_returns_cart_by_slug(self):
        cart = CartFactory()

        result = get_cart_by_slug(slug=cart.slug)

        self.assertEqual(result, cart)

    def test_raises_404_when_slug_does_not_exist(self):
        with self.assertRaises(Http404):
            get_cart_by_slug(slug="non-existent-slug")