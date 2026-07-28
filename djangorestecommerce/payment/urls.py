from django.urls import path 
from djangorestecommerce.payment.apis import (
    OrderPaymentApiView, 
    OrderPaymentCallbackApiView
)


urlpatterns = [
    path(
        "callback/",
        OrderPaymentCallbackApiView.as_view(),
        name="order-payment-callback"
        ),
    path(
        "<slug:slug>/",
        OrderPaymentApiView.as_view(),
        name="order-payment"
        ),
]