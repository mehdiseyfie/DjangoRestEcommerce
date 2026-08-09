from decimal import Decimal

from django.test import TestCase

from djangorestecommerce.cart.models import CartItem
from djangorestecommerce.cart.services import remove_cart_item
from djangorestecommerce.cart.tests.factories import CartFactory, CartItemFactory
from djangorestecommerce.products.tests.factories import ProductFactory


class RemoveCartItemTest(TestCase):

    def test_removes_item_and_updates_cart_totals(self):
        cart = CartFactory()
        product = ProductFactory(stock=10, price=Decimal("40.00"))
        item = CartItemFactory(
            cart=cart,
            product=product,
            quantity=2,
            price=product.price,
        )
        item_id = item.pk

        remove_cart_item(item=item)

        self.assertFalse(CartItem.objects.filter(pk=item_id).exists())
        cart.refresh_from_db()
        self.assertEqual(cart.total_items, 0)
        self.assertEqual(cart.total_price, Decimal("0.00"))