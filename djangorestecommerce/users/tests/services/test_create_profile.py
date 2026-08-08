from django.test import TestCase

from djangorestecommerce.users.models import Profile
from djangorestecommerce.users.services import create_profile
from djangorestecommerce.users.tests.factories import BaseUserFactory


class CreateProfileTest(TestCase):

    def test_create_profile(self):
        user = BaseUserFactory()

        profile = create_profile(user=user)

        self.assertEqual(profile.user, user)
        self.assertIsNotNone(profile.pk)
        self.assertTrue(Profile.objects.filter(user=user).exists())
        self.assertEqual(Profile.objects.filter(user=user).count(), 1)