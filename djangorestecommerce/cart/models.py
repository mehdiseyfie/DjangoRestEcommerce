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
    customer = models.ForeignKey(
        Profile, on_delete=models.CASCADE,
        related_name="carts",
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
        constraints = [
            
            models.UniqueConstraint(
            fields=["customer"],
            condition=models.Q(is_active=True), 
            name="unique_active_cart_per_customer",
            )
        ]

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
        self.total_price = totals['total_price'] or Decimal("0.00")
        self.total_items = totals['total_items'] or 0 
        self.clean()
        self.save(update_fields=["total_price", "total_items"])
        
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
    price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    ) 
    
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

    def save(self, *args, **kwargs):
    
        try:
            with transaction.atomic():
                if not self.slug:
                    self.slug = slugify(str(uuid.uuid4()))
                if self.price is None:
                    if not self.product or self.product.price is None:
                        raise ValidationError("Product price is not set")
                    self.price = self.product.price 
                self.clean()
                super().save(*args, **kwargs)
                cart = Cart.objects.select_for_update().get(pk=self.cart_id) #type: ignore
                cart.calculate_totals()
        except Exception as e:
            raise ValidationError(f"Error saving CartItem: {str(e)}")


    def delete(self, *args, **kwargs):
        
        try:
            with transaction.atomic(): 
                cart = Cart.objects.select_for_update().get(pk=self.cart_id) #type: ignore
                super().delete(*args, **kwargs)
                cart.calculate_totals() 
        except Exception as e:
            raise ValidationError(f"Error deleting CartItem: {str(e)}")

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Cart {self.cart.pk}"