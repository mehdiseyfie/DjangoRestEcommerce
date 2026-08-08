from django.test import TestCase

from djangorestecommerce.users.models import Profile
from djangorestecommerce.users.selectors import get_profile
from djangorestecommerce.users.tests.factories import (
    BaseUserFactory,
    ProfileFactory,
)


class GetProfileTest(TestCase):

    def test_get_profile_returns_profile_for_user(self):
        profile = ProfileFactory()

        result = get_profile(user=profile.user)

        self.assertEqual(result, profile)
        self.assertEqual(result.user, profile.user)

    def test_get_profile_raises_when_profile_does_not_exist(self):
        user = BaseUserFactory()

        with self.assertRaises(Profile.DoesNotExist):
            get_profile(user=user)