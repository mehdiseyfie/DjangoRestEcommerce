from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase

from djangorestecommerce.cart.tests.factories import CartFactory, CartItemFactory
from djangorestecommerce.orders.services import reverse_stock_for_cart
from djangorestecommerce.products.tests.factories import ProductFactory


class ReverseStockForCartTest(TestCase):

    def test_decreases_stock_for_each_cart_item(self):
        cart = CartFactory()
        product = ProductFactory(stock=10, price=Decimal("100.00"))
        CartItemFactory(cart=cart, product=product, quantity=3, price=product.price)

        reverse_stock_for_cart(cart=cart)

        product.refresh_from_db()
        self.assertEqual(product.stock, 7)

    def test_raises_when_insufficient_stock(self):
        cart = CartFactory()
        product = ProductFactory(stock=2, price=Decimal("50.00"))
        CartItemFactory(cart=cart, product=product, quantity=5, price=product.price)

        with self.assertRaises(ValidationError) as ctx:
            reverse_stock_for_cart(cart=cart)

        self.assertIn("stock", str(ctx.exception).lower())
        product.refresh_from_db()
        self.assertEqual(product.stock, 2)