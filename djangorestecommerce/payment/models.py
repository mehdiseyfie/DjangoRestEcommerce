from django.db import models
from django.db.models import constraints
from djangorestecommerce.common.models import BaseModel 
from djangorestecommerce.orders.models import (
    Order
)
from django.core.exceptions import ValidationError 
from django.utils.translation import gettext_lazy as _




class Payment(BaseModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="payments", verbose_name=_("Order"))
    payment_id = models.CharField(max_length=100, unique=True, verbose_name=_("Payment ID"))
    authority = models.CharField(max_length=100, blank=True, verbose_name=_("Authority"))
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Amount"))
    gateway = models.CharField(max_length=50, default='zarinpal', verbose_name=_("Payment Gateway"))
    status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('completed', 'Completed'), ('failed', 'Failed'), ('refunded', 'Refunded')],
        default='pending', verbose_name=_("Status")
    )
    ref_id = models.CharField(max_length=100, blank=True, verbose_name=_("Ref ID"))
    transaction_id = models.CharField(max_length=100, blank=True, verbose_name=_("Transaction ID"))
    gateway_response = models.TextField(blank=True, verbose_name=_("Gateway Response"))

    class Meta:
        verbose_name = _("Payment")
        verbose_name_plural = _("Payments")
        ordering = ['-created_at'] 
        constraints = [
            models.UniqueConstraint(
                fields=["order"], 
                condition=models.Q(status="completed"), 
                name="unique_completed_payment_per_order", 
            )
        ]

    def clean(self):
        if self.amount < 0:
            raise ValidationError("Payment amount cannot be negative.")
        if self.status == 'completed' and self.order.payment_status != 'paid':
            raise ValidationError("Completed payment requires order payment status to be paid.")

    def __str__(self):
        return f"Payment {self.payment_id} for Order {self.order.slug}" #type:ignore