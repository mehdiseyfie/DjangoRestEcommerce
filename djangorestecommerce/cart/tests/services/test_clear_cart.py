from decimal import Decimal

from django.test import TestCase

from djangorestecommerce.cart.models import CartItem
from djangorestecommerce.cart.services import clear_cart
from djangorestecommerce.cart.tests.factories import CartFactory, CartItemFactory
from djangorestecommerce.products.tests.factories import ProductFactory


class ClearCartTest(TestCase):

    def test_clears_all_items_and_resets_totals(self):
        cart = CartFactory()
        product1 = ProductFactory(stock=10, price=Decimal("10.00"))
        product2 = ProductFactory(stock=10, price=Decimal("20.00"))
        CartItemFactory(cart=cart, product=product1, quantity=1, price=product1.price)
        CartItemFactory(cart=cart, product=product2, quantity=2, price=product2.price)

        clear_cart(cart=cart)

        self.assertEqual(CartItem.objects.filter(cart=cart).count(), 0)
        cart.refresh_from_db()
        self.assertEqual(cart.total_items, 0)
        self.assertEqual(cart.total_price, Decimal("0.00"))

    def test_clear_empty_cart_is_safe(self):
        cart = CartFactory()

        clear_cart(cart=cart)

        cart.refresh_from_db()
        self.assertEqual(cart.total_items, 0)
        self.assertEqual(cart.total_price, Decimal("0.00"))