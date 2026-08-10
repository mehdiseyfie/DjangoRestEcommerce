from decimal import Decimal
from unittest.mock import MagicMock, patch

from django.core.exceptions import ValidationError
from django.test import TestCase

from djangorestecommerce.orders.tests.factories import OrderFactory
from djangorestecommerce.payment.models import Payment
from djangorestecommerce.payment.services import initiate_payment
from djangorestecommerce.users.tests.factories import (
    ProfileFactory,
    ShippingAddressFactory,
)


class InitiatePaymentTest(TestCase):

    def setUp(self):
        self.profile = ProfileFactory()
        self.address = ShippingAddressFactory(customer=self.profile)
        self.order = OrderFactory(
            customer=self.profile,
            shipping_address=self.address,
            billing_address=self.address,
            total_price=Decimal("100000.00"),
            shipping_cost=Decimal("100000.00"),
            tax_amount=Decimal("0.00"),
            discount_amount=Decimal("0.00"),
            payment_status="pending",
        )
        self.callback_url = "https://example.com/callback"

    @patch("djangorestecommerce.payment.services.requests.post")
    def test_initiate_payment_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {
                "code": 100,
                "authority": "A00000000000000000000000000000000001",
            }
        }
        mock_post.return_value = mock_response

        result = initiate_payment(
            order=self.order,
            callback_url=self.callback_url,
            email="user@example.com",
            mobile="+989121234567",
        )

        self.assertTrue(result["success"])
        self.assertIn("authority", result)
        self.assertEqual(result["authority"], "A00000000000000000000000000000000001")
        self.assertIn("payment_url", result)
        self.assertTrue(
            Payment.objects.filter(
                order=self.order,
                authority="A00000000000000000000000000000000001",
                status="pending",
            ).exists()
        )
        mock_post.assert_called_once()

    def test_raises_when_order_already_paid(self):
        self.order.payment_status = "paid"
        self.order.status = "confirmed"
        self.order.save(update_fields=["payment_status", "status"])

        with self.assertRaises(ValidationError) as ctx:
            initiate_payment(
                order=self.order,
                callback_url=self.callback_url,
                email=None,
                mobile=None,
            )

        self.assertIn("paid", str(ctx.exception).lower())

    @patch("djangorestecommerce.payment.services.requests.post")
    def test_raises_when_gateway_returns_error(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {"code": -11},
            "errors": {"code": -11, "message": "Invalid merchant"},
        }
        mock_post.return_value = mock_response

        with self.assertRaises(ValidationError):
            initiate_payment(
                order=self.order,
                callback_url=self.callback_url,
                email=None,
                mobile=None,
            )

        self.assertFalse(Payment.objects.filter(order=self.order).exists())

    @patch("djangorestecommerce.payment.services.requests.post")
    def test_raises_when_gateway_unavailable(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 503
        mock_post.return_value = mock_response

        with self.assertRaises(ValidationError) as ctx:
            initiate_payment(
                order=self.order,
                callback_url=self.callback_url,
                email=None,
                mobile=None,
            )

        self.assertIn("unavailable", str(ctx.exception).lower())
