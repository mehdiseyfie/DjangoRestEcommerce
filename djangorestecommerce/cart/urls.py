from django.urls import path, include 
from djangorestecommerce.cart.apis import CartApiView 

urlpatterns = [
        path("<slug:slug>/", CartApiView.as_view(), name="cart-detail-by-slug"),
        path("", CartApiView.as_view(), name="cart-detail"),

        ] 
