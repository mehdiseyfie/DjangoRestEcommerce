from django.db import transaction
from django.db.models import F
from djangorestecommerce.orders.models import (
    Order, OrderItem
)
from djangorestecommerce.cart.models import (
    Cart
)
from djangorestecommerce.products.models import Product
from djangorestecommerce.users.models import (
    Profile, 
    ShippingAddress
)
from typing import Optional
from django.core.exceptions import ValidationError 
from decimal import Decimal 


def reverse_stock_for_cart(cart: Cart) -> None: 
    
    for cart_item in cart.cartitems.all(): #type: ignore 
        #updated_rows is count of fields been changed. if not any fields changed returned 0.
        update_rows = Product.objects.filter(
            pk=cart_item.product_id, 
            stock__gte=cart_item.quantity
        ).update(
            stock=F("stock") - cart_item.quantity
        ) 
        
        if update_rows == 0: 
            raise ValidationError(
                f"Insuficient stock for {cart_item.product.name}"
            )
            
            
            
def release_stock_for_order(order: Order) -> None:
    for item in order.orderitems.all(): #type: ignore 
        Product.objects.filter(
            pk=item.product_id
        ).update(
            stock=F("stock") + item.quantity
        )

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
    
    cart = Cart.objects.select_for_update().get(slug=cart.slug)
    
    if not cart.cartitems.exists(): #type: ignore
        raise ValidationError("Cart is empty.") 
    
    if cart.is_ordered or not cart.is_active:
        raise ValidationError(
            "This cart has already been ordered."
        )

    reverse_stock_for_cart(cart=cart)

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
    
    Cart.objects.create(customer=customer)

    return order





























