from django.shortcuts import get_object_or_404
from django.db.models import QuerySet
from djangorestecommerce.users.models import Profile 
from djangorestecommerce.orders.models import (Order, OrderItem) 

def get_customer_order_by_slug(customer: Profile, slug: str) -> Order: 
    return get_object_or_404(Order, customer=customer, slug=slug) 

def get_all_orders_by_customer(customer: Profile) -> QuerySet[Order]: 
    return Order.objects.filter(customer=customer) 

    