from django.shortcuts import get_object_or_404
from django.db.models import QuerySet
from djangorestecommerce.users.models import Profile 
from typing import Optional
from djangorestecommerce.orders.models import (
    Order,
    OrderItem,
    ShippingAddress
) 

def get_customer_order_by_slug(customer: Profile, slug: str) -> Order: 
    return get_object_or_404(Order, customer=customer, slug=slug) 

def get_all_orders_by_customer(customer: Profile) -> QuerySet[Order]: 
    return Order.objects.filter(customer=customer) 

def get_shipping_addresses(customer: Profile) -> QuerySet[ShippingAddress]:
    """Get all shipping addresses for customer"""
    return ShippingAddress.objects.filter(
        customer=customer
    ).order_by('-is_default', '-created_at') 
    

def get_default_shipping_address(customer: Profile) -> Optional[ShippingAddress]:
    """Get default shipping address"""
    try:
        return ShippingAddress.objects.get(
            customer=customer,
            is_default=True
        )
    except ShippingAddress.DoesNotExist:
        return None


def get_shipping_address_by_id(address_id: int, customer: Profile) -> ShippingAddress:
    """Get specific shipping address"""
    return get_object_or_404(
        ShippingAddress.objects.filter(customer=customer),
        id=address_id
    )