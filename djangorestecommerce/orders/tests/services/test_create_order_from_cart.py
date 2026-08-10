from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase

from djangorestecommerce.cart.models import Cart
from djangorestecommerce.cart.tests.factories import CartFactory, CartItemFactory
from djangorestecommerce.orders.models import Order, OrderItem
from djangorestecommerce.orders.services import create_order_from_cart
from djangorestecommerce.products.tests.factories import ProductFactory
from djangorestecommerce.users.tests.factories import (
    ProfileFactory,
    ShippingAddressFactory,
)


class CreateOrderFromCartTest(TestCase):

    def _cart_with_item(self, *, stock=10, quantity=2, price=Decimal("100.00")):
        profile = ProfileFactory()
        cart = CartFactory(customer=profile, is_active=True, is_ordered=False)
        product = ProductFactory(stock=stock, price=price)
        CartItemFactory(
            cart=cart,
            product=product,
            quantity=quantity,
            price=price,
        )
        cart.refresh_from_db()
        return profile, cart, product

    def test_creates_order_from_cart_successfully(self):
        profile, cart, product = self._cart_with_item()
        address = ShippingAddressFactory(customer=profile)

        order = create_order_from_cart(
            customer=profile,
            cart=cart,
            shipping_method="standard",
            shipping_address=address,
            billing_address=None,
            discount_code=None,
        )

        self.assertIsNotNone(order.pk)
        self.assertEqual(order.customer, profile)
        self.assertEqual(order.cart, cart)
        self.assertEqual(order.status, "pending")
        self.assertEqual(order.payment_status, "pending")
        self.assertEqual(order.shipping_method, "standard")
        self.assertEqual(order.shipping_cost, Decimal("100000.00"))
        self.assertEqual(order.shipping_address, address)
        self.assertEqual(order.billing_address, address)  # fallback به shipping
        self.assertEqual(OrderItem.objects.filter(order=order).count(), 1)

        item = OrderItem.objects.get(order=order)
        self.assertEqual(item.product, product)
        self.assertEqual(item.quantity, 2)
        self.assertEqual(item.price, Decimal("100.00"))

        cart.refresh_from_db()
        self.assertTrue(cart.is_ordered)
        self.assertFalse(cart.is_active)

        # سبد فعال جدید برای مشتری
        self.assertTrue(
            Cart.objects.filter(customer=profile, is_active=True, is_ordered=False).exists()
        )

        product.refresh_from_db()
        self.assertEqual(product.stock, 8)

    def test_shipping_cost_by_method(self):
        profile, cart, _ = self._cart_with_item()
        address = ShippingAddressFactory(customer=profile)

        order = create_order_from_cart(
            customer=profile,
            cart=cart,
            shipping_method="express",
            shipping_address=address,
            billing_address=None,
            discount_code=None,
        )

        self.assertEqual(order.shipping_cost, Decimal("200000.00"))

    def test_raises_when_cart_is_empty(self):
        profile = ProfileFactory()
        cart = CartFactory(customer=profile, is_active=True, is_ordered=False)

        with self.assertRaises(ValidationError) as ctx:
            create_order_from_cart(
                customer=profile,
                cart=cart,
                shipping_method="standard",
                shipping_address=None,
                billing_address=None,
                discount_code=None,
            )

        self.assertIn("empty", str(ctx.exception).lower())

    def test_raises_when_cart_already_ordered(self):
        profile, cart, _ = self._cart_with_item()
        cart.is_ordered = True
        cart.is_active = False
        cart.save(update_fields=["is_ordered", "is_active"])

        with self.assertRaises(ValidationError) as ctx:
            create_order_from_cart(
                customer=profile,
                cart=cart,
                shipping_method="standard",
                shipping_address=None,
                billing_address=None,
                discount_code=None,
            )

        self.assertIn("ordered", str(ctx.exception).lower())

    def test_raises_when_insufficient_stock(self):
        profile, cart, product = self._cart_with_item(stock=1, quantity=5)

        with self.assertRaises(ValidationError) as ctx:
            create_order_from_cart(
                customer=profile,
                cart=cart,
                shipping_method="standard",
                shipping_address=None,
                billing_address=None,
                discount_code=None,
            )

        self.assertIn("stock", str(ctx.exception).lower())
        product.refresh_from_db()
        self.assertEqual(product.stock, 1)
        self.assertFalse(Order.objects.filter(cart=cart).exists())

    def test_pickup_has_zero_shipping_cost(self):
        profile, cart, _ = self._cart_with_item()
        address = ShippingAddressFactory(customer=profile)

        order = create_order_from_cart(
            customer=profile,
            cart=cart,
            shipping_method="pickup",
            shipping_address=address,
            billing_address=None,
            discount_code=None,
        )

        self.assertEqual(order.shipping_cost, Decimal("0.00"))