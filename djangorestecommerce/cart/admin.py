from django.contrib import admin
from djangorestecommerce.cart.models import Cart, CartItem
from django.utils.translation import gettext_lazy as _

# ------------------------------
# CartItem Inline (for display in CartAdmin)
# ------------------------------
class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 1   
    fields = ("product", "quantity", "get_total_price_item")
    readonly_fields = ("get_total_price_item",)

    def get_total_price_item(self, obj):
        return obj.get_total_price_item()
    get_total_price_item.short_description = "Total Price"


# ------------------------------
# Cart Admin
# ------------------------------
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("customer", "total_items", "total_price", "created_at", "updated_at")
    list_filter = ("created_at", "updated_at")
    search_fields = ("customer__user__email",)
    inlines = [CartItemInline]
    ordering = ("-created_at",)


# ------------------------------
# CartItem Admin
# ------------------------------
@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ("cart", "product", "quantity", "get_total_price_item")
    list_filter = ("cart", "product")
    search_fields = ("cart__user__email", "product__name")

    def get_total_price_item(self, obj):
        return obj.get_total_price_item()
    get_total_price_item.short_description = "Total Price"
