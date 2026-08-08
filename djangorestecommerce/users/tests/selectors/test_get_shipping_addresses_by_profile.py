from django.test import TestCase

from djangorestecommerce.users.selectors import get_shipping_addresses_by_profile
from djangorestecommerce.users.tests.factories import (
    ProfileFactory,
    ShippingAddressFactory,
)


class GetShippingAddressesByProfileTest(TestCase):

    def test_returns_all_addresses_for_customer(self):
        profile = ProfileFactory()
        other_profile = ProfileFactory()

        addr1 = ShippingAddressFactory(customer=profile, is_default=False)
        addr2 = ShippingAddressFactory(customer=profile, is_default=True)
        ShippingAddressFactory(customer=other_profile)

        result = list(get_shipping_addresses_by_profile(customer=profile))

        self.assertEqual(len(result), 2)
        self.assertIn(addr1, result)
        self.assertIn(addr2, result)

    def test_orders_by_default_first_then_created_at(self):
        profile = ProfileFactory()

        addr_normal = ShippingAddressFactory(customer=profile, is_default=False)
        addr_default = ShippingAddressFactory(customer=profile, is_default=True)

        result = list(get_shipping_addresses_by_profile(customer=profile))

        self.assertEqual(result[0], addr_default)
        self.assertEqual(result[1], addr_normal)

    def test_returns_empty_queryset_when_no_addresses(self):
        profile = ProfileFactory()

        result = get_shipping_addresses_by_profile(customer=profile)

        self.assertEqual(result.count(), 0)