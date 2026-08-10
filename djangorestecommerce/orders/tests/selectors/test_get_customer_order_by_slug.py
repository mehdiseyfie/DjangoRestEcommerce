from django.http import Http404
from django.test import TestCase

from djangorestecommerce.orders.selectors import get_customer_order_by_slug
from djangorestecommerce.orders.tests.factories import OrderFactory
from djangorestecommerce.users.tests.factories import ProfileFactory


class GetCustomerOrderBySlugTest(TestCase):

    def test_returns_order_for_owner(self):
        profile = ProfileFactory()
        order = OrderFactory(customer=profile)

        result = get_customer_order_by_slug(customer=profile, slug=order.slug)

        self.assertEqual(result, order)
        self.assertEqual(result.customer, profile)

    def test_raises_404_for_other_customer_order(self):
        owner = ProfileFactory()
        other = ProfileFactory()
        order = OrderFactory(customer=owner)

        with self.assertRaises(Http404):
            get_customer_order_by_slug(customer=other, slug=order.slug)

    def test_raises_404_when_slug_does_not_exist(self):
        profile = ProfileFactory()

        with self.assertRaises(Http404):
            get_customer_order_by_slug(
                customer=profile,
                slug="non-existent-order-slug",
            )
