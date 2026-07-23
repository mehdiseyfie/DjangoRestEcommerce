from django.db import transaction 
from djangorestecommerce.orders.models import (
    Order, OrderItem, Payment, ShippingAddress, Discount
)
from djangorestecommerce.cart.models import (
    Cart, CartItem
)
from djangorestecommerce.users.models import Profile 
from typing import Optional
from django.core.exceptions import ValidationError 
from decimal import Decimal

@transaction.atomic
def create_order_from_cart (
    *,
    customer: Profile, 
    cart: Cart, 
    shipping_method: str,
    shipping_address: Optional[ShippingAddress] = None,
    billing_address: Optional[ShippingAddress] = None, 
    discount_code: Optional[str]
) -> Order: 
    if not cart.cartitems.exists(): #type: ignore
        raise ValidationError("Cart is empty.")

    for cart_item in cart.cartitems.all(): #type: ignore
        if cart_item.product.stock < cart_item.quantity:
            raise ValidationError(f"Insufficient stock for {cart_item.product.name}")

    shipping_costs = {
        'standard': Decimal('100000.00'),
        'express': Decimal('200000.00'),
        'overnight': Decimal('300000.00'),
        'pickup': Decimal('0.00')
    }
    shipping_cost = shipping_costs.get(shipping_method, Decimal('100000.00'))
    order = Order(
        customer=customer,
        cart=cart,
        total_price=cart.total_price,
        total_items=cart.total_items,
        status="pending",
        payment_status="pending",
        payment_gateway="zarinpal",
        shipping_method=shipping_method or 'standard',
        shipping_cost=shipping_cost,
    )

    if shipping_address is not None:
        order.shipping_address = shipping_address #type: ignore
    if billing_address is not None:
        order.billing_address = billing_address #type: ignore
    elif shipping_address is not None:
        order.billing_address = shipping_address #type: ignore

    order.save()

    for item in cart.cartitems.all(): #type: ignore
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            price=item.price
        )

    order.calculate_totals()

    cart.is_ordered = True
    cart.is_active = False
    cart.save()

    return order
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    