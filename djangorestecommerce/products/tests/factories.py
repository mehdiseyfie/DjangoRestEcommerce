from decimal import Decimal

import factory

from djangorestecommerce.products.models import (
    Category,
    Product,
    ProductImage,
    Review,
)
from djangorestecommerce.users.tests.factories import BaseUserFactory
from djangorestecommerce.utils.tests.base import faker


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category

    name = factory.LazyAttribute(lambda _: faker.unique.word().title())
    description = factory.LazyAttribute(lambda _: faker.text(max_nb_chars=120))
    # slug در save مدل از name ساخته می‌شود


class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Product

    category = factory.SubFactory(CategoryFactory)
    name = factory.LazyAttribute(lambda _: faker.unique.word().title())
    description = factory.LazyAttribute(lambda _: faker.text(max_nb_chars=200))
    price = factory.LazyAttribute(
        lambda _: Decimal(str(faker.pydecimal(left_digits=4, right_digits=2, positive=True)))
    )
    stock = factory.LazyAttribute(lambda _: faker.random_int(min=1, max=100))
    available = True
    newest_product = False
    # slug در save مدل از name ساخته می‌شود


class ProductImageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ProductImage

    product = factory.SubFactory(ProductFactory)
    image = factory.django.ImageField(filename="test_product.jpg")


class ReviewFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Review

    product = factory.SubFactory(ProductFactory)
    user = factory.SubFactory(BaseUserFactory)
    rating = factory.LazyAttribute(lambda _: faker.random_int(min=1, max=5))
    comment = factory.LazyAttribute(lambda _: faker.text(max_nb_chars=100))