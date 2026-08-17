from djangorestecommerce.users.models import Profile 
from djangorestecommerce.cart.models import Cart, CartItem
from djangorestecommerce.products.models import Product
from django.core.exceptions import ValidationError
from django.db import transaction 
from decimal import Decimal

@transaction.atomic
def get_cart_or_create(customer: Profile) -> Cart: 
    cart = Cart.objects.filter(
        customer=customer, is_active=True
    ).first() 
    
    if cart: 
        return cart 
    return Cart.objects.create(customer=customer) 
    

@transaction.atomic
def add_item_to_cart(cart: Cart, product: Product, quantity: int) -> CartItem: 
    if quantity <= 0:
        raise ValidationError("Quantity must be positive")
    
    if product.stock < quantity:
        raise ValidationError(f"Insufficient stock. Available: {product.stock}")
    try: 
        cart_item = CartItem.objects.get(cart=cart, product=product) 
        cart_item.quantity += quantity
        cart_item.save()
        
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
     
    
    item.quantity = quantity 
    item.save()
    
    return item

@transaction.atomic
def remove_cart_item(item:CartItem)-> None: 
    item.delete() 

@transaction.atomic
def clear_cart(cart: Cart) -> None:
    cart.cartitems.all().delete() #type: ignore 
    cart.calculate_totals()
