from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase

from djangorestecommerce.cart.services import update_cart_item
from djangorestecommerce.cart.tests.factories import CartFactory, CartItemFactory
from djangorestecommerce.products.tests.factories import ProductFactory


class UpdateCartItemTest(TestCase):

    def test_updates_quantity_and_cart_totals(self):
        cart = CartFactory()
        product = ProductFactory(stock=20, price=Decimal("30.00"))
        item = CartItemFactory(
            cart=cart,
            product=product,
            quantity=2,
            price=product.price,
        )

        updated = update_cart_item(item=item, quantity=5)

        self.assertEqual(updated.quantity, 5)
        cart.refresh_from_db()
        self.assertEqual(cart.total_items, 5)
        self.assertEqual(cart.total_price, Decimal("150.00"))

    def test_raises_when_quantity_is_not_positive(self):
        item = CartItemFactory(quantity=2)

        with self.assertRaises(ValidationError):
            update_cart_item(item=item, quantity=0)

    def test_raises_when_insufficient_stock(self):
        product = ProductFactory(stock=3)
        item = CartItemFactory(product=product, quantity=1, price=product.price)

        with self.assertRaises(ValidationError) as ctx:
            update_cart_item(item=item, quantity=10)

        self.assertIn("Insufficient stock", str(ctx.exception))