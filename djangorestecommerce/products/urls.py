from django.urls import path, include 
from djangorestecommerce.products.apis import (
    CategoryApiView, ProductApiView
)

urlpatterns = [
    path("", ProductApiView.as_view(), name="product-list"),
    path("<slug:slug>/", ProductApiView.as_view(), name="product-detail"),
    path("categories/", CategoryApiView.as_view(), name="category-list"),
    path("categories/<slug:slug>/", CategoryApiView.as_view(), name="category-detail"),
    
]