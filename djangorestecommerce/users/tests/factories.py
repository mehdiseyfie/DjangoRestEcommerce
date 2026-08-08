import factory

from djangorestecommerce.users.models import BaseUser, Profile, ShippingAddress
from djangorestecommerce.utils.tests.base import faker


class BaseUserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = BaseUser

    first_name = factory.LazyAttribute(lambda _: faker.unique.first_name())
    last_name = factory.LazyAttribute(lambda _: faker.unique.last_name())
    phone = factory.Sequence(lambda n: f"+1415555{(n % 9000) + 1000:04d}")
    email = factory.LazyAttribute(lambda _: faker.unique.email())
    is_active = True
    is_admin = False

    @factory.post_generation
    def password(obj, create, extracted, **kwargs):
        password = extracted or "TestPassword1718@M"
        obj.set_password(password)  # type: ignore
        if create:
            obj.save()  # type: ignore


class ProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Profile

    user = factory.SubFactory(BaseUserFactory)


class ShippingAddressFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ShippingAddress

    customer = factory.SubFactory(ProfileFactory)
    first_name = factory.LazyAttribute(lambda _: faker.unique.first_name())
    last_name = factory.LazyAttribute(lambda _: faker.unique.last_name())
    company = factory.LazyAttribute(lambda _: faker.unique.company())
    address = factory.LazyAttribute(lambda _: faker.unique.address())
    city = factory.LazyAttribute(lambda _: faker.unique.city())
    state = factory.LazyAttribute(lambda _: faker.unique.street_name())
    postal_code = factory.LazyAttribute(lambda _: faker.unique.postcode())
    country = factory.LazyAttribute(lambda _: faker.unique.country())
    phone = factory.Sequence(lambda n: f"+1415555{(n % 9000) + 2000:04d}")
    is_default = False