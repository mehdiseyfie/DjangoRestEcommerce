from decimal import Decimal

import factory
from django.utils import timezone

from djangorestecommerce.cart.tests.factories import CartFactory
from djangorestecommerce.orders.models import Discount, Order, OrderItem
from djangorestecommerce.products.tests.factories import ProductFactory
from djangorestecommerce.users.tests.factories import (
    ProfileFactory,
    ShippingAddressFactory,
)
from djangorestecommerce.utils.tests.base import faker


class OrderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Order

    customer = factory.SubFactory(ProfileFactory)
    cart = factory.SubFactory(
        CartFactory,
        customer=factory.SelfAttribute("..customer"),
        is_active=True,
        is_ordered=False,
    )
    total_price = Decimal("0.00")
    total_items = 0
    status = "pending"
    payment_status = "pending"
    payment_gateway = "zarinpal"
    shipping_method = "standard"
    shipping_cost = Decimal("100000.00")
    tax_amount = Decimal("0.00")
    discount_amount = Decimal("0.00")
    shipping_address = factory.SubFactory(
        ShippingAddressFactory,
        customer=factory.SelfAttribute("..customer"),
    )
    billing_address = factory.LazyAttribute(lambda o: o.shipping_address)


class OrderItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = OrderItem

    order = factory.SubFactory(OrderFactory)
    product = factory.SubFactory(ProductFactory, stock=100)
    quantity = factory.LazyAttribute(lambda _: faker.random_int(min=1, max=5))
    price = factory.LazyAttribute(
        lambda o: o.product.price if o.product_id else Decimal("10.00")
    )


class DiscountFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Discount

    code = factory.LazyAttribute(
        lambda _: faker.unique.bothify(text="DISC-####").upper()
    )
    discount_type = "percentage"
    value = Decimal("10.00")
    valid_from = factory.LazyFunction(timezone.now)
    valid_until = factory.LazyAttribute(
        lambda _: timezone.now() + timezone.timedelta(days=30) #type: ignore
    )
    max_usage = 100
    used_count = 0
    is_active = True