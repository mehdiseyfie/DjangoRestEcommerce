from decimal import Decimal

import factory

from djangorestecommerce.cart.models import Cart, CartItem
from djangorestecommerce.products.tests.factories import ProductFactory
from djangorestecommerce.users.tests.factories import ProfileFactory
from djangorestecommerce.utils.tests.base import faker


class CartFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Cart

    customer = factory.SubFactory(ProfileFactory)
    total_price = Decimal("0.00")
    total_items = 0
    is_active = True
    is_ordered = False


class CartItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CartItem

    cart = factory.SubFactory(CartFactory)
    product = factory.SubFactory(ProductFactory, stock=100)
    quantity = factory.LazyAttribute(lambda _: faker.random_int(min=1, max=5))
    price = Decimal("0.00")