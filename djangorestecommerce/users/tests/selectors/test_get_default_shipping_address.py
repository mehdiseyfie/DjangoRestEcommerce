from django.test import TestCase

from djangorestecommerce.users.selectors import get_default_shipping_address
from djangorestecommerce.users.tests.factories import (
    ProfileFactory,
    ShippingAddressFactory,
)


class GetDefaultShippingAddressTest(TestCase):

    def test_returns_default_address(self):
        profile = ProfileFactory()
        ShippingAddressFactory(customer=profile, is_default=False)
        default_address = ShippingAddressFactory(customer=profile, is_default=True)

        result = get_default_shipping_address(customer=profile)

        self.assertEqual(result, default_address)
        if result is None:
            self.fail("get_default_shipping_address() returned None for a profile with a default address")
        self.assertTrue(result.is_default)

    def test_returns_none_when_no_default(self):
        profile = ProfileFactory()
        ShippingAddressFactory(customer=profile, is_default=False)

        result = get_default_shipping_address(customer=profile)

        self.assertIsNone(result)

    def test_returns_none_when_no_addresses(self):
        profile = ProfileFactory()

        result = get_default_shipping_address(customer=profile)

        self.assertIsNone(result)