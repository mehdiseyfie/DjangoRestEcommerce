from django.test import TestCase

from djangorestecommerce.users.models import ShippingAddress
from djangorestecommerce.users.services import create_shipping_address
from djangorestecommerce.users.tests.factories import (
    ProfileFactory,
    ShippingAddressFactory,
)


class CreateShippingAddressTest(TestCase):

    def test_create_shipping_address_with_validated_data(self):
        profile = ProfileFactory()
        fake = ShippingAddressFactory.build(customer=profile)

        shipping_address = create_shipping_address(
            customer=profile,
            first_name=fake.first_name,
            last_name=fake.last_name,
            company=fake.company,
            address=fake.address,
            city=fake.city,
            state=fake.state,
            postal_code=fake.postal_code,
            country=fake.country,
            phone=str(fake.phone),
        )

        self.assertEqual(shipping_address.customer, profile)
        self.assertEqual(shipping_address.first_name, fake.first_name)
        self.assertEqual(shipping_address.last_name, fake.last_name)
        self.assertEqual(shipping_address.company, fake.company)
        self.assertEqual(shipping_address.address, fake.address)
        self.assertEqual(shipping_address.city, fake.city)
        self.assertEqual(shipping_address.state, fake.state)
        self.assertEqual(shipping_address.postal_code, fake.postal_code)
        self.assertEqual(shipping_address.country, fake.country)
        self.assertEqual(str(shipping_address.phone), str(fake.phone))
        self.assertIsNotNone(shipping_address.pk)
        self.assertFalse(shipping_address.is_default)
        self.assertEqual(
            ShippingAddress.objects.filter(customer=profile).count(),
            1,
        )