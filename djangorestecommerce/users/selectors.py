from .models import Profile, BaseUser 
from django.db.models import QuerySet 
from djangorestecommerce.users.models import ShippingAddress
from typing import Optional 
from django.shortcuts import get_object_or_404

def get_profile(user:BaseUser) -> Profile:
    return Profile.objects.get(user=user) 

def get_shipping_addresses_by_profile(customer: Profile) -> QuerySet[ShippingAddress]:
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
