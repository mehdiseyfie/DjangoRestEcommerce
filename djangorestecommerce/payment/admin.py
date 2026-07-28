from django.contrib import admin
from djangorestecommerce.payment.models import Payment 

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['order', 'id', 'amount', 'gateway', 'status', 'created_at']
    list_filter = ['gateway', 'status']
    search_fields = ['payment_id', 'order__id']