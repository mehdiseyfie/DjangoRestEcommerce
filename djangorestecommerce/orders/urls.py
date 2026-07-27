from django.urls import path
from djangorestecommerce.orders.apis import (
    OrderApiView,
    OrderPaymentApiView,
    OrderPaymentCallbackApiView
)

urlpatterns = [
    path("", OrderApiView.as_view(), name="order-list"),

   
    path(
        "payment/callback/",
        OrderPaymentCallbackApiView.as_view(),
        name="order-payment-callback"
    ),
    path(
        "payment/<slug:slug>/",
        OrderPaymentApiView.as_view(),
        name="order-payment"
    ),

    path("<slug:slug>/", OrderApiView.as_view(), name="order-detail"),
]