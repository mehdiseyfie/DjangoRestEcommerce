from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase

from djangorestecommerce.cart.models import CartItem
from djangorestecommerce.cart.services import add_item_to_cart
from djangorestecommerce.cart.tests.factories import CartFactory, CartItemFactory
from djangorestecommerce.products.tests.factories import ProductFactory


class AddItemToCartTest(TestCase):

    def test_adds_new_item_to_cart(self):
        cart = CartFactory()
        product = ProductFactory(stock=10, price=Decimal("100.00"))

        item = add_item_to_cart(cart=cart, product=product, quantity=2)

        self.assertEqual(item.cart, cart)
        self.assertEqual(item.product, product)
        self.assertEqual(item.quantity, 2)
        self.assertEqual(item.price, product.price)
        self.assertEqual(CartItem.objects.filter(cart=cart).count(), 1)

        cart.refresh_from_db()
        self.assertEqual(cart.total_items, 2)
        self.assertEqual(cart.total_price, Decimal("200.00"))

    def test_increases_quantity_when_product_already_in_cart(self):
        cart = CartFactory()
        product = ProductFactory(stock=20, price=Decimal("50.00"))
        CartItemFactory(cart=cart, product=product, quantity=2, price=product.price)

        item = add_item_to_cart(cart=cart, product=product, quantity=3)

        self.assertEqual(item.quantity, 5)
        self.assertEqual(CartItem.objects.filter(cart=cart, product=product).count(), 1)

        cart.refresh_from_db()
        self.assertEqual(cart.total_items, 5)
        self.assertEqual(cart.total_price, Decimal("250.00"))

    def test_raises_when_quantity_is_not_positive(self):
        cart = CartFactory()
        product = ProductFactory(stock=10)

        with self.assertRaises(ValidationError):
            add_item_to_cart(cart=cart, product=product, quantity=0)

        with self.assertRaises(ValidationError):
            add_item_to_cart(cart=cart, product=product, quantity=-1)

    def test_raises_when_insufficient_stock(self):
        cart = CartFactory()
        product = ProductFactory(stock=2)

        with self.assertRaises(ValidationError) as ctx:
            add_item_to_cart(cart=cart, product=product, quantity=5)

        self.assertIn("Insufficient stock", str(ctx.exception))