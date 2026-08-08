from django.test import TestCase

from djangorestecommerce.users.models import BaseUser, Profile
from djangorestecommerce.users.services import register
from djangorestecommerce.users.tests.factories import BaseUserFactory


class RegisterTest(TestCase):

    def test_register_with_validated_data(self):
        fake_user = BaseUserFactory.build()
        password = "TestPassword1718@M"

        user = register(
            phone=str(fake_user.phone),
            email=fake_user.email,
            first_name=fake_user.first_name,
            last_name=fake_user.last_name,
            password=password,
        )

        self.assertEqual(str(user.phone), str(fake_user.phone))
        self.assertEqual(user.email, fake_user.email.lower())
        self.assertEqual(user.first_name, fake_user.first_name)
        self.assertEqual(user.last_name, fake_user.last_name)
        self.assertTrue(user.check_password(password))
        self.assertIsNotNone(user.pk)
        self.assertTrue(BaseUser.objects.filter(email=user.email).exists())
        self.assertTrue(Profile.objects.filter(user=user).exists())
        self.assertEqual(Profile.objects.filter(user=user).count(), 1)

    def test_register_duplicate_email_raises(self):
        existing = BaseUserFactory()

        with self.assertRaises(Exception):
            register(
                phone="+14155559999",
                email=existing.email,
                first_name="X",
                last_name="Y",
                password="TestPassword1718@M",
            )