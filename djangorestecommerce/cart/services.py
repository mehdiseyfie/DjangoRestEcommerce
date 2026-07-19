from djangorestecommerce.users.models import Profile 
from djangorestecommerce.cart.models import Cart 


def get_cart_or_create(customer: Profile) -> Cart: 
    try: 
        return Cart.objects.get(customer=customer) 
    except Cart.DoesNotExist: 
        return Cart.objects.create(customer=customer)