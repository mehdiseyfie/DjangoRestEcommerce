from django.http import Http404
from django.test import TestCase

from djangorestecommerce.cart.selectors import get_item_by_slug
from djangorestecommerce.cart.tests.factories import CartFactory, CartItemFactory


class GetItemBySlugTest(TestCase):

    def test_returns_item_for_cart(self):
        cart = CartFactory()
        item = CartItemFactory(cart=cart)

        result = get_item_by_slug(cart=cart, slug=item.slug)

        self.assertEqual(result, item)

    def test_raises_404_for_item_of_another_cart(self):
        cart1 = CartFactory()
        cart2 = CartFactory()
        item = CartItemFactory(cart=cart1)

        with self.assertRaises(Http404):
            get_item_by_slug(cart=cart2, slug=item.slug)

    def test_raises_404_when_slug_does_not_exist(self):
        cart = CartFactory()

        with self.assertRaises(Http404):
            get_item_by_slug(cart=cart, slug="missing-item-slug")