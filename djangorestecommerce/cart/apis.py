from typing import Any

from rest_framework import (
    serializers, status
)
from rest_framework.views import APIView 
from rest_framework.response import Response 
from rest_framework.permissions import IsAuthenticated 
from rest_framework_simplejwt.authentication import JWTAuthentication 
from djangorestecommerce.cart.models import (
    Cart, CartItem
)
from djangorestecommerce.products.models import (
    Product
)
from drf_spectacular.utils import extend_schema 
from djangorestecommerce.users.selectors import (
    get_profile
)
from djangorestecommerce.cart.selectors import (
    get_cart_by_slug, get_cart_by_customer
)
from djangorestecommerce.cart.services import(
    get_cart_or_create, add_item_to_cart
)



class CartApiView(APIView):
    
    permission_classes = [IsAuthenticated] 
    authentication_classes = [JWTAuthentication]  
    
    class InputAddItemToCart(serializers.Serializer):
        product = serializers.SlugRelatedField(
            queryset=Product.objects.all(), slug_field="slug"
        )
        quantity = serializers.IntegerField() 
        
        def validate_product(self, value: Product):
            """Check stock availability"""
            if value.stock <= 0:
                raise serializers.ValidationError("This product is out of stock.")
            return value 
    
    class OutputCartItemSerializer(serializers.ModelSerializer): 
            
            class Meta: 
                model = CartItem 
                fields = "__all__" 
    
    class OutputCartSerializer(serializers.ModelSerializer): 
        items = serializers.StringRelatedField(source="cartitems", many=True)
        
        class Meta: 
            model = Cart 
            fields = (
                "items",
                "total_price",
                "total_items",
                "slug",
                "is_active",
                "is_ordered",
                
            ) 
    
    @extend_schema(responses=OutputCartSerializer)
    def get(self, request, slug=None): 
        profile = get_profile(user=request.user)
        if slug: 
            cart = get_cart_by_slug(slug=slug)
            if cart is None or cart.customer != profile: 
                return Response(
                    {"error": "you don't have access to this cart."
                     },
                    status=status.HTTP_403_FORBIDDEN
                    )
        else: 
            cart = get_cart_by_customer(customer=profile) 
            if not cart: 
                cart = get_cart_or_create(customer=profile) 
            
        serializer = self.OutputCartSerializer(
                cart, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK) 
    
    @extend_schema(
            request=InputAddItemToCart,
            responses=OutputCartSerializer
        )
    
    def post(self, request): 
        profile = get_profile(user=request.user) 
        serializer = self.InputAddItemToCart(data=request.data)  
        serializer.is_valid(raise_exception=True) 
        validated_data = serializer.validated_data 
        
        try: 
            cart = get_cart_or_create(customer=profile) 
            item = add_item_to_cart(
                cart=cart,
                product=validated_data.get("product"),
                quantity=validated_data.get("quantity"),
            )
            serializer = self.OutputCartItemSerializer(
                item, context={"request": request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as ex: 
            return Response({"error": str(ex)}, status=status.HTTP_400_BAD_REQUEST)
            

        
        
        
        
            
            
        
    
        
        
    
    
    
    
    
    
    
    
    