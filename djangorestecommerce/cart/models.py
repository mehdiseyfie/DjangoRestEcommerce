from decimal import Decimal
from sys import maxsize
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models import F, Sum
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from djangorestecommerce.common.models import BaseModel
from djangorestecommerce.products.models import Product
from djangorestecommerce.users.models import Profile
import uuid


class Cart(BaseModel):
    customer = models.OneToOneField(
        Profile, on_delete=models.CASCADE,
        related_name="cart",
        verbose_name=_("Customer")
    )

    total_price = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name=_("Total Price"),default=Decimal("0.00")
    )
    total_items = models.PositiveIntegerField(
        default=0, verbose_name=_("Total Items")
    )
    
    slug = models.SlugField(max_length=225, unique=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_ordered = models.BooleanField(default=False)
    
    

    class Meta:
        verbose_name = _("Cart")
        verbose_name_plural = _("Carts")

    def save(self, *args, **kwargs):
        
        if not self.slug:
            self.slug = slugify(f"cart_{self.customer.user.email}_{str(uuid.uuid4())}")
        self.clean()
        super().save(*args, **kwargs)
    
    def clean(self):
        
        if self.total_price < 0 or self.total_items < 0:
            raise ValidationError("Total price or items cannot be negative.")
        
    def calculate_totals(self):

        totals = self.cartitems.aggregate( # type: ignore
            total_price=Sum(F('quantity') * F('price')),
            total_items=Sum('quantity')
        )
        self.total_price = totals['total_price'] or 0
        self.total_items = totals['total_items'] or 0
        self.save()
        
    def __str__(self):
        return f"Cart of {self.customer.user.email}"


class CartItem(BaseModel):
    cart = models.ForeignKey(
        Cart, on_delete=models.CASCADE,
        related_name="cartitems",
        verbose_name=_("Cart")
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE,
        related_name="cart_products", 
        verbose_name=_("Product")
    )
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00")) 
    
    slug = models.SlugField(max_length=225, unique=True, blank=True)

    class Meta:
        verbose_name = _("Cart Item")
        verbose_name_plural = _("Cart Items")
        ordering = ["-created_at"]

    def clean(self):
        
        if self.quantity <= 0:
            raise ValidationError("Quantity must be positive.")
        if self.price < 0:
            raise ValidationError("Price cannot be negative.")
        if self.product and self.quantity > self.product.stock:
            raise ValidationError(f"Insufficient stock for {self.product.name}")
        
    def get_total_price_item(self):
        return self.price * self.quantity

    def save(self, *args, old_quantity=None, old_price=None, **kwargs):
    
        try:
            with transaction.atomic():
                if not self.slug:
                    self.slug = slugify(str(uuid.uuid4()))
                if not self.price:
                    if not self.product or self.product.price is None:
                        raise ValidationError("Product price is not set")
                    self.price = self.product.price 

                is_new = self._state.adding
                if not is_new and old_quantity is not None and old_price is not None:
                    diff_quantity = self.quantity - old_quantity
                    diff_price = (self.quantity * self.price) - (old_quantity * old_price)
                else:
                    diff_quantity = self.quantity
                    diff_price = self.price * self.quantity

                super().save(*args, **kwargs)

                cart = self.cart
                cart.total_items += diff_quantity
                cart.total_price += diff_price
                cart.clean()
                cart.save(update_fields=["total_items", "total_price"])
        except Exception as e:
            raise ValidationError(f"Error saving CartItem: {str(e)}")


    def delete(self, *args, **kwargs):
        
        try:
            with transaction.atomic():
                cart = self.cart
                cart.total_items -= self.quantity
                cart.total_price -= (self.price * self.quantity)
                cart.clean()
                super().delete(*args, **kwargs)
                cart.save(update_fields=["total_items", "total_price"])
        except Exception as e:
            raise ValidationError(f"Error deleting CartItem: {str(e)}")

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Cart {self.cart.pk}"
