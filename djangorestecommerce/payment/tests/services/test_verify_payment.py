from decimal import Decimal
from unittest.mock import MagicMock, patch

from django.test import TestCase

from djangorestecommerce.cart.tests.factories import CartFactory, CartItemFactory
from djangorestecommerce.orders.tests.factories import OrderFactory
from djangorestecommerce.payment.models import Payment
from djangorestecommerce.payment.services import verify_payment
from djangorestecommerce.payment.tests.factories import PaymentFactory
from djangorestecommerce.products.tests.factories import ProductFactory
from djangorestecommerce.users.tests.factories import (
    ProfileFactory,
    ShippingAddressFactory,
)


class VerifyPaymentTest(TestCase):

    def setUp(self):
        self.profile = ProfileFactory()
        self.address = ShippingAddressFactory(customer=self.profile)
        self.cart = CartFactory(
            customer=self.profile,
            is_active=False,
            is_ordered=True,
        )
        self.product = ProductFactory(stock=10, price=Decimal("50000.00"))
        CartItemFactory(
            cart=self.cart,
            product=self.product,
            quantity=1,
            price=self.product.price,
        )
        self.order = OrderFactory(
            customer=self.profile,
            cart=self.cart,
            shipping_address=self.address,
            billing_address=self.address,
            total_price=Decimal("50000.00"),
            shipping_cost=Decimal("0.00"),
            tax_amount=Decimal("0.00"),
            discount_amount=Decimal("0.00"),
            payment_status="pending",
            status="pending",
        )
        self.authority = "A00000000000000000000000000000000099"
        self.payment = PaymentFactory(
            order=self.order,
            payment_id=self.authority,
            authority=self.authority,
            amount=self.order.get_total_amount(),
            status="pending",
        )

    @patch("djangorestecommerce.payment.services.send_mail")
    @patch("djangorestecommerce.payment.services.requests.post")
    def test_verify_payment_success(self, mock_post, mock_send_mail):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {
                "code": 100,
                "ref_id": "1234567890",
            }
        }
        mock_post.return_value = mock_response

        result = verify_payment(authority=self.authority, status="OK")

        self.assertTrue(result["success"])
        self.assertEqual(result["payment_status"], "completed")
        self.assertEqual(result["ref_id"], "1234567890")

        self.payment.refresh_from_db()
        self.order.refresh_from_db()

        self.assertEqual(self.payment.status, "completed")
        self.assertEqual(self.payment.ref_id, "1234567890")
        self.assertEqual(self.order.payment_status, "paid")
        self.assertEqual(self.order.status, "confirmed")

    def test_verify_already_completed_is_idempotent(self):
        self.payment.status = "completed"
        self.payment.ref_id = "999"
        self.payment.save(update_fields=["status", "ref_id"])

        result = verify_payment(authority=self.authority, status="OK")

        self.assertTrue(result["success"])
        self.assertEqual(result["message"], "Payment already verified")
        self.assertEqual(result["ref_id"], "999")

    @patch("djangorestecommerce.payment.services.release_stock_for_order")
    def test_verify_cancelled_by_user(self, mock_release):
        result = verify_payment(authority=self.authority, status="NOK")

        self.assertFalse(result["success"])
        self.assertEqual(result["payment_status"], "failed")

        self.payment.refresh_from_db()
        self.assertEqual(self.payment.status, "failed")
        mock_release.assert_called_once_with(order=self.order)

    def test_verify_payment_not_found(self):
        result = verify_payment(
            authority="NONEXISTENT_AUTHORITY",
            status="OK",
        )

        self.assertFalse(result["success"])
        self.assertIn("not found", result["message"].lower())

    @patch("djangorestecommerce.payment.services.release_stock_for_order")
    @patch("djangorestecommerce.payment.services.requests.post")
    def test_verify_gateway_rejects_payment(self, mock_post, mock_release):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {"code": -22},
            "errors": "Invalid authority",
        }
        mock_post.return_value = mock_response

        result = verify_payment(authority=self.authority, status="OK") 
        
        mock_release.assert_called_once_with(order=self.order)

        self.assertFalse(result["success"])
        self.assertEqual(result["payment_status"], "failed")

        self.payment.refresh_from_db()
        self.assertEqual(self.payment.status, "failed")
