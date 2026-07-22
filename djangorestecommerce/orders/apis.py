from rest_framework import (
    serializers,
    status
)
from rest_framework.views import (
    APIView
)
from rest_framework.response import (
    Response
)
from rest_framework.permissions import (
    IsAuthenticated
)
from rest_framework_simplejwt.authentication import (
    JWTAuthentication
)
from drf_spectacular.utils import (
    extend_schema
)
from djangorestecommerce.orders.models import (
    Order,
    OrderItem,
    Payment,
    ShippingAddress
    
) 
from phonenumber_field.serializerfields import PhoneNumberField

from djangorestecommerce.users.selectors import get_profile 
from djangorestecommerce.orders.selectors import(
    get_customer_order_by_slug,
    get_all_orders_by_customer
)


class OrderApiView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication] 
    
    class InputCreateOrderSerializer(serializers.Serializer):
        
        shipping_method = serializers.ChoiceField(
                                                choices=[
                                                        'standard', 
                                                        'express', 
                                                        'overnight', 
                                                        'pickup'
                                                        ],
                                                default='standard'
                                                          )
        discount_code = serializers.CharField(required=False,
                                          allow_blank=True, 
                                          max_length=50) 
        shipping_address_id = serializers.IntegerField(required=False, allow_null=True)
        billing_address_id = serializers.IntegerField(required=False, allow_null=True) 
    
    class InputUpdateOrderSerializer(serializers.Serializer): 
        quantity = serializers.IntegerField()
    
    class OutputOrderItemSerializer(serializers.ModelSerializer):
        
        class Meta:
            model = OrderItem
            fields = "__all__" 
            
    class OutpuPaymentSerializer(serializers.ModelSerializer): 
    
        class Meta: 
            model = Payment 
            fields = "__all__"

    class OutputShippingAddressSerializer(serializers.ModelSerializer):
        """Output serializer for shipping address"""
        
        class Meta:
            model = ShippingAddress
            fields = (
                "id",
                "first_name",
                "last_name",
                "company",
                "address_line_1",
                "address_line_2",
                "city",
                "state",
                "postal_code",
                "country",
                "phone",
                "is_default",
                "created_at"
            )
    
    class OutputOrderSerializer(serializers.ModelSerializer): 
        items = serializers.SerializerMethodField()
        customer_email = serializers.EmailField(
            source="customer.user.email",
            read_only=True
        )
        customer_phone = PhoneNumberField(
            source="customer.user.phone",
            read_only=True
        )
        cart_slug = serializers.SlugField(
            source="cart.slug",
            read_only=True
        )
        payment = serializers.SerializerMethodField()
        total_amount = serializers.SerializerMethodField()
        shipping_address = serializers.SerializerMethodField() 
        billing_address = serializers.SerializerMethodField() 
        
        
        class Meta: 
            model = Order 
            fields = (
            "id",
            "slug",
            "items",
            "customer_email",
            "customer_phone",
            "cart_slug",
            "payment",
            "total_amount",
            "total_items", 
            "status",
            "payment_status",
            "payment_gateway",
            "tracking_number",
            "shipping_address", 
            "billing_address", 
            "shipping_method", 
            "shipping_cost", 
            "tax_amount"
            ) 
        
        def get_items(self, obj): 
            return OrderApiView.OutputOrderItemSerializer(
                obj.orderitems.all(),
                many=True,
                context=self.context
                ).data 
            
        def get_payment(self, obj): 
            payment = getattr(obj, "payment", None) 
            
            if not payment:
                return None
            
            return OrderApiView.OutpuPaymentSerializer(
                payment, 
                context=self.context
            ).data
        
        def get_total_amount(self, obj): 
            return obj.get_total_amount() 
        
        def get_shipping_address(self, obj): 
            if not obj.shipping_address:
                return None 
            
            return OrderApiView.OutputShippingAddressSerializer(
                obj.shipping_address, 
                context=self.context
            ).data 
            
        
        def get_billing_address(self, obj): 
            if not obj.billing_address: 
                return None 
            return OrderApiView.OutputShippingAddressSerializer(
                obj.billing_address,
                context=self.context
            ).data 
        
    @extend_schema(responses=OutputOrderSerializer)
    def get(self, request, slug=None): 
        profile = get_profile(user=request.user) 
        if slug: 
            order = get_customer_order_by_slug(customer=profile, slug=slug) 
            if order is None or order.customer != profile: 
                return Response(
                    {
                    "error": "you don't have access to this order."
                    },
                     status=status.HTTP_403_FORBIDDEN           
                    ) 
            serializer = self.OutputOrderSerializer(
                order,
                context={"request": request}
            )
            return Response(serializer.data, status=status.HTTP_200_OK) 
        else: 
            orders = get_all_orders_by_customer(customer=profile) 
            serializer = self.OutputOrderSerializer(
                orders,
                many=True, 
                context={"request": request}
            )
            return Response(serializer.data, status=status.HTTP_200_OK) 
        
        
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            