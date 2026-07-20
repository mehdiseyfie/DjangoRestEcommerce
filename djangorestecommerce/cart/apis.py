from profile import Profile
from typing import Any

from rest_framework import (
    serializers, status
)
from rest_framework.views import APIView 
from rest_framework.response import Response 
from rest_framework.permissions import IsAuthenticated 
from rest_framework_simplejwt.authentication import JWTAuthentication 
from djangorestecommerce.cart.models import (
    Cart,
    CartItem
)
from djangorestecommerce.products.models import (
    Product
)
from drf_spectacular.utils import extend_schema 
from djangorestecommerce.users.selectors import (
    get_profile
)
from djangorestecommerce.cart.selectors import (
    get_cart_by_slug,
    get_cart_by_customer,
    get_item_by_slug
)
from djangorestecommerce.cart.services import(
    get_cart_or_create, 
    add_item_to_cart, 
    update_cart_item, 
    remove_cart_item
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
                
    class InputUpdateCartItemSerializer(serializers.Serializer):
        quantity = serializers.IntegerField() 
    
        
        
    
    class OutputCartSerializer(serializers.ModelSerializer): 
        items = serializers.SlugRelatedField(source="cartitems", many=True, read_only=True, slug_field="slug")
        
        
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
    
    @extend_schema(
        request=InputUpdateCartItemSerializer,
        responses=OutputCartItemSerializer)
    def patch(self, request, slug):
        profile = get_profile(user=request.user) 
        serializer = self.InputUpdateCartItemSerializer(data=request.data) 
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        try:
            cart = get_cart_by_customer(customer=profile)
            if not cart:
                return Response(
                    {"error": "you don't have any cart."}, 
                    status=status.HTTP_404_NOT_FOUND
                    )
            item = get_item_by_slug(cart=cart, slug=slug) 
            if not item: 
                return Response(
                        {"error": f"not exist any item with this slug{slug}"}
                        )
            updated_item = update_cart_item(
                item=item,
                quantity=validated_data["quantity"]
            )
            serializer = self.OutputCartItemSerializer(
                updated_item, context={"request": request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as ex: 
            return Response(
                {"error": str(ex)}, status=status.HTTP_400_BAD_REQUEST
            ) 
    @extend_schema(responses={204:None})
    def delete(self, request, slug): 
        
        profile = get_profile(user=request.user)
        try: 
            cart = get_cart_by_customer(customer=profile) 
            if not cart: 
                return Response(
                    {"error": "you don't have any car"},
                    status=status.HTTP_404_NOT_FOUND
                )
            item = get_item_by_slug(cart=cart, slug=slug) 
            remove_cart_item(item=item)
            return Response(status=status.HTTP_204_NO_CONTENT)
        
        except Exception as ex: 
            return Response(
                            {"error": str(ex)}, 
                            status=status.HTTP_400_BAD_REQUEST
                            ) 

        
        
        
            
            
        
    
        
        
    
    
    
    
    
    
    
    
    