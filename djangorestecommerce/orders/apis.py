from django.http import Http404
from rest_framework import (
    serializers,
    status
)
from djangorestecommerce.api.mixins import ApiPaginationMixin
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
from djangorestecommerce.cart.selectors import get_cart_by_customer
from djangorestecommerce.orders.models import (
    Order,
    OrderItem
) 
from djangorestecommerce.payment.models import Payment
from djangorestecommerce.users.apis import ShippingAddressApiView
from phonenumber_field.serializerfields import PhoneNumberField

from djangorestecommerce.users.selectors import (
    get_profile, 
    get_shipping_address_by_id, 
    get_default_shipping_address
)
from djangorestecommerce.payment.apis import OrderPaymentApiView
from djangorestecommerce.orders.selectors import(
    get_customer_order_by_slug,
    get_all_orders_by_customer, 
) 
from djangorestecommerce.orders.services import (
    create_order_from_cart, 
)
from djangorestecommerce.payment.services import (
    initiate_payment
)

class OrderApiView(ApiPaginationMixin, APIView):
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
            
        def get_payment(self, obj: Order): 
            payment = obj.payments.order_by("-created_at").first() #type: ignore
            
            if not payment:
                return None
            
            return OrderPaymentApiView.OutputPaymentSerializer(
                payment, 
                context=self.context
            ).data
        
        def get_total_amount(self, obj): 
            return obj.get_total_amount() 
        
        def get_shipping_address(self, obj): 
            if not obj.shipping_address:
                return None 
            
            return ShippingAddressApiView.OutputShippingAddressSerializer(
                obj.shipping_address, 
                context=self.context
            ).data 
            
        
        def get_billing_address(self, obj): 
            if not obj.billing_address: 
                return None 
            return ShippingAddressApiView.OutputShippingAddressSerializer(
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
            page = self.paginate_queryset(orders) 
            if page is not None: 
                serializer = self.OutputOrderSerializer(
                    page, many=True, context={"request":request}
                )
                return self.get_paginated_response(serializer.data)
            
            serializer = self.OutputOrderSerializer(
                orders,
                many=True, 
                context={"request": request}
            )
            return Response(serializer.data, status=status.HTTP_200_OK) 
    
    @extend_schema(
        request=InputCreateOrderSerializer,
        responses={
            201: {
                "type": "object",
                "properties": {
                    "order_slug": {"type": "string"},
                    "payment_url": {"type": "string"},
                    "authority": {"type": "string"},
                    "payment_id": {"type": "integer"},
                }
            }
        }
    )
    def post(self, request): 
        profile = get_profile(user=request.user) 
        serializer = self.InputCreateOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True) 
        validated_data = serializer.validated_data 
        
        try: 
            cart = get_cart_by_customer(customer=profile) 
            if not cart: 
                return Response(
                    {
                        "error": "you don't have any cart.",
                    },
                    status=status.HTTP_404_NOT_FOUND
                ) 
            if cart.customer != profile: 
                return Response(
                    {
                        "error": "you don't have access to this cart."
                    },
                    status=status.HTTP_403_FORBIDDEN
                ) 
            shipping_address = None
            billing_address = None

            if validated_data.get('shipping_address_id'): #type: ignore
                shipping_address = get_shipping_address_by_id(
                    address_id=validated_data['shipping_address_id'],  # type: ignore
                    customer=profile
                )
            else:
                # Use default address
                shipping_address = get_default_shipping_address(
                    customer=profile)

            if validated_data.get('billing_address_id'): #type: ignore
                billing_address = get_shipping_address_by_id(
                    address_id=validated_data['billing_address_id'],  # type: ignore
                    customer=profile
                ) 
            
            order = create_order_from_cart(
                customer=profile,
                cart=cart, 
                shipping_address = shipping_address, 
                billing_address = billing_address,
                shipping_method = validated_data.get("shipping_method"), 
                discount_code = validated_data.get("discount_code")
            )
            
            callback_url = request.build_absolute_uri(
                '/api/payment/callback/'
            )
            
            email = request.user.email if hasattr(request.user,"email") else None
            phone = str(request.user.phone) if hasattr(request.user.phone,"phone") else None 
            payment_result = initiate_payment(
                order=order,
                callback_url=callback_url,
                email=email,
                mobile=phone
            ) 
            
            if payment_result["success"]: 
                return Response(
                    {
                        "order_slug": order.slug,
                        "payment_url": payment_result["payment_url"],
                        "authority": payment_result["authority"],
                        "payment_id": payment_result["payment_id"],
                    },
                    status=status.HTTP_201_CREATED
                )
            
            return Response(
                {
                    "error": "Payment initiation failed",
                    "order_slug": order.slug,
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except Http404:
            raise
            
        except Exception as ex: 
            return Response(
                {
                    "error": str(ex)
                },
                status=status.HTTP_400_BAD_REQUEST
            ) 
    