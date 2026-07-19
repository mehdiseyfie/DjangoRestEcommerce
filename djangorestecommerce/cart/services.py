from djangorestecommerce.users.models import Profile 
from djangorestecommerce.cart.models import Cart, CartItem
from djangorestecommerce.products.models import Product
from django.core.exceptions import ValidationError
from django.db import transaction

@transaction.atomic
def get_cart_or_create(customer: Profile) -> Cart: 
    try: 
        return Cart.objects.get(customer=customer) 
    except Cart.DoesNotExist: 
        return Cart.objects.create(customer=customer) 

@transaction.atomic
def add_item_to_cart(cart: Cart, product: Product, quantity: int) -> CartItem: 
    if quantity <= 0:
        raise ValidationError("Quantity must be positive")
    
    if product.stock < quantity:
        raise ValidationError(f"Insufficient stock. Available: {product.stock}")
    try: 
        cart_item = CartItem.objects.get(cart=cart, product=product) 
        old_quantity = cart_item.quantity 
        old_price = cart_item.price 
        total_quantity = old_quantity + quantity 
        cart_item.quantity = total_quantity
        cart_item.save(old_quantity=old_quantity, old_price=old_price) 
        
    except CartItem.DoesNotExist: 
        cart_item = CartItem.objects.create(cart=cart, product=product, quantity=quantity)  
        
    return cart_item 


@transaction.atomic
def update_cart_item(
            item: CartItem,
            quantity: int
            ) -> CartItem: 
    if quantity <= 0:
        raise ValidationError("Quantity must be positive") 
    if item.product.stock < quantity:
        raise ValidationError(f"Insufficient stock. Available: {item.product.stock}")  
    
    old_quantity = item.quantity 
    old_price = item.price 
    
    item.quantity = quantity 
    
    item.save(old_quantity=old_quantity, old_price=old_price)
    
    return item


