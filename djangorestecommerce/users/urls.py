from django.urls import path
from .apis import (
    RegisterApi,
    ProfileApi, 
    ShippingAddressApiView
)


urlpatterns = [
    path('register/', RegisterApi.as_view(),name="register"),
    path('profile/', ProfileApi.as_view(),name="profile"),
    path(
        "shipping-address/", 
        ShippingAddressApiView.as_view(), 
        name="list-shipping-address"
    ),
    path(
        "shipping-address/<int:id>/",
        ShippingAddressApiView.as_view(),
        name="shipping-address-detail"
    )
    
]
