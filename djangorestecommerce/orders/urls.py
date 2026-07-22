from django.urls import path, include 
from djangorestecommerce.orders.apis import OrderApiView 

urlpatterns = [
    path("", OrderApiView.as_view(), name="order-list"),
    path("<slug:slug>/", OrderApiView.as_view(), name="order-detail")
]