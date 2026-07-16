from django.urls import path, include

urlpatterns = [
    path("authentication/", include(("djangorestecommerce.authentication.urls", "authentication"))),
    path("users/", include(("djangorestecommerce.users.urls", "users"))),
    path("products/", include(("djangorestecommerce.products.urls", "products"))),
    
]
