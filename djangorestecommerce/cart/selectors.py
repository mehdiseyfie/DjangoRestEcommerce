from djangorestecommerce.cart.models import (
    Cart, CartItem
)
from typing import Optional
from django.shortcuts import (get_object_or_404)
from django.db.models import QuerySet

from djangorestecommerce.users.models import Profile 

def get_cart_by_slug(slug: str) -> Cart: 
    return get_object_or_404(Cart, slug=slug) 

def get_cart_by_customer(customer:Profile) -> Optional[Cart]: 
    try:
        return Cart.objects.get(customer=customer) 
    except Cart.DoesNotExist: 
        return None  

def get_item_by_slug(cart: Cart, slug: str) -> CartItem: 
    return get_object_or_404(CartItem, cart=cart, slug=slug) 


