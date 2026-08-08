from django.test import TestCase

from djangorestecommerce.users.models import BaseUser
from djangorestecommerce.users.services import create_user
from djangorestecommerce.users.tests.factories import BaseUserFactory


class CreateUserTest(TestCase):

    def test_create_user_with_validated_data(self):
        fake_user = BaseUserFactory.build()
        password = "TestPassword1718@M"

        user = create_user(
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
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_admin)
        self.assertIsNotNone(user.pk)
        self.assertTrue(BaseUser.objects.filter(email=user.email).exists())