from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from djangorestecommerce.users.models import (
    BaseUser,
    Profile, 
    ShippingAddress
)


@admin.register(BaseUser)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'phone', 'first_name', 'last_name', 'is_active', 'is_admin')
    list_filter = ('is_admin', 'is_active', 'is_superuser')
    search_fields = ('email', 'first_name', 'last_name', 'phone')
    ordering = ('-created_at',)
    
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'phone')}),
        (_('Permissions'), {'fields': ('is_active', 'is_admin', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'created_at', 'updated_at')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'phone', 'password1', 'password2', 'first_name', 'last_name'),
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at', 'last_login')

class ShippingAddressInline(admin.TabularInline): 
    model = ShippingAddress 
    fk_name = "customer" 
    extra = 1 
    
    fields = (
        "first_name", "last_name", "address", "city",
        "state", "postal_code", "country", "phone", "is_default",
    )
    


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user',)
    search_fields = ('user__email', 'user__first_name', 'user__last_name')
    readonly_fields = ('user',)
    inlines = [ShippingAddressInline]
    
    fieldsets = (
        (None, {'fields': ('user',)}), 
    )

@admin.register(ShippingAddress)
class ShippingAddressAdmin(admin.ModelAdmin):
    list_display = ['customer', 'first_name', 'last_name', 'city', 'country', 'is_default']
    list_filter = ['is_default', 'country']
    search_fields = ['first_name', 'last_name', 'city']

    
    
    
    
    
    
    
    
    
    
    