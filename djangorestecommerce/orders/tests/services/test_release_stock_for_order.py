from decimal import Decimal

from django.test import TestCase

from djangorestecommerce.orders.services import release_stock_for_order
from djangorestecommerce.orders.tests.factories import OrderFactory, OrderItemFactory
from djangorestecommerce.products.tests.factories import ProductFactory


class ReleaseStockForOrderTest(TestCase):

    def test_increases_stock_for_each_order_item(self):
        order = OrderFactory()
        product = ProductFactory(stock=5, price=Decimal("20.00"))
        OrderItemFactory(
            order=order,
            product=product,
            quantity=3,
            price=product.price,
        )

        release_stock_for_order(order=order)

        product.refresh_from_db()
        self.assertEqual(product.stock, 8)