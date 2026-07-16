from django.urls import path, include 
from djangorestecommerce.products.apis import (
    CategoryApiView
)

urlpatterns = [
    path("categories/", CategoryApiView.as_view(), name="category-list"),
    path("categories/<slug:slug>/", CategoryApiView.as_view(), name="category-detail"),
    
]