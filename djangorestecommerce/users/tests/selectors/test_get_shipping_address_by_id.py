from django.http import Http404
from django.test import TestCase

from djangorestecommerce.users.selectors import get_shipping_address_by_id
from djangorestecommerce.users.tests.factories import (
    ProfileFactory,
    ShippingAddressFactory,
)


class GetShippingAddressByIdTest(TestCase):

    def test_returns_address_for_owner(self):
        profile = ProfileFactory()
        address = ShippingAddressFactory(customer=profile)

        result = get_shipping_address_by_id(
            address_id=address.id,
            customer=profile,
        )

        self.assertEqual(result, address)
        self.assertEqual(result.customer, profile)

    def test_raises_404_for_other_customer_address(self):
        owner = ProfileFactory()
        other = ProfileFactory()
        address = ShippingAddressFactory(customer=owner)

        with self.assertRaises(Http404):
            get_shipping_address_by_id(
                address_id=address.id,
                customer=other,
            )

    def test_raises_404_when_address_does_not_exist(self):
        profile = ProfileFactory()

        with self.assertRaises(Http404):
            get_shipping_address_by_id(
                address_id=999999,
                customer=profile,
            )