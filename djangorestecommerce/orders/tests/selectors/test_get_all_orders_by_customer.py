from django.test import TestCase

from djangorestecommerce.cart.tests.factories import CartFactory
from djangorestecommerce.orders.selectors import get_all_orders_by_customer
from djangorestecommerce.orders.tests.factories import OrderFactory
from djangorestecommerce.users.tests.factories import ProfileFactory


class GetAllOrdersByCustomerTest(TestCase):

    def test_returns_all_orders_for_customer(self):
        profile = ProfileFactory()
        other = ProfileFactory()

        cart1 = CartFactory(customer=profile, is_active=True, is_ordered=False)
        order1 = OrderFactory(customer=profile, cart=cart1)

        cart1.is_active = False
        cart1.is_ordered = True
        cart1.save(update_fields=["is_active", "is_ordered"])

        cart2 = CartFactory(customer=profile, is_active=True, is_ordered=False)
        order2 = OrderFactory(customer=profile, cart=cart2)

        OrderFactory(customer=other)

        result = list(get_all_orders_by_customer(customer=profile))

        self.assertEqual(len(result), 2)
        self.assertIn(order1, result)
        self.assertIn(order2, result)

    def test_returns_empty_queryset_when_no_orders(self):
        profile = ProfileFactory()

        result = get_all_orders_by_customer(customer=profile)

        self.assertEqual(result.count(), 0)

    def test_does_not_return_other_customers_orders(self):
        profile = ProfileFactory()
        other = ProfileFactory()
        OrderFactory(customer=other)

        result = get_all_orders_by_customer(customer=profile)

        self.assertEqual(result.count(), 0)