from decimal import Decimal

import factory

from djangorestecommerce.orders.tests.factories import OrderFactory
from djangorestecommerce.payment.models import Payment
from djangorestecommerce.utils.tests.base import faker


class PaymentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Payment

    order = factory.SubFactory(OrderFactory)
    payment_id = factory.LazyAttribute(
        lambda _: faker.unique.bothify(text="A" + "?" * 35).upper()
    )
    authority = factory.LazyAttribute(lambda o: o.payment_id)
    amount = factory.LazyAttribute(
        lambda o: o.order.get_total_amount() if o.order_id else Decimal("100.00")
    )
    gateway = "zarinpal"
    status = "pending"
    ref_id = ""
    transaction_id = ""
    gateway_response = ""
