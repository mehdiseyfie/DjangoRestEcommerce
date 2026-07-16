from rest_framework import(status, serializers)
from rest_framework.views import APIView 
from rest_framework.response import Response 
from djangorestecommerce.products.models import(
    Category, Product
)
from drf_spectacular.utils import extend_schema 
from djangorestecommerce.products.selectors import (
    get_category_by_slug, 
    get_all_categories, 
    get_product_by_slug,
    get_all_products
)
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication 



class CategoryApiView(APIView): 
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    class OutputCategorySerializer(serializers.ModelSerializer): 
        class Meta: 
            model = Category 
            fields = (
                "name",
                "slug",
                "description",
                
            ) 
    @extend_schema(responses=OutputCategorySerializer())
    def get(self, request, slug=None): 
        if slug: 
            category = get_category_by_slug(slug=slug) 
            serializer = self.OutputCategorySerializer(
                category, context={"request", request}
            )
            return Response(serializer.data, status=status.HTTP_200_OK) 
        else: 
            categories = get_all_categories()
            serializer = self.OutputCategorySerializer(
                categories, many=True, context={"request":request}
            )
        return Response(serializer.data, status=status.HTTP_200_OK)

class ProductApiView(APIView):
    permission_classes = [IsAuthenticated] 
    authentication_classes = [JWTAuthentication] 
    
    class OutputProductSerializer(serializers.ModelSerializer): 
        category = serializers.CharField(source="category.name")
        
        class Meta: 
            model = Product 
            fields = "__all__" 
    
    @extend_schema(responses=OutputProductSerializer) 
    def get(self, request, slug=None):
        if slug: 
            product = get_product_by_slug(slug=slug) 
            serializer = self.OutputProductSerializer(
                product, context={"request", request}
            )
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            products = get_all_products() 
            serializer = self.OutputProductSerializer(
                products, many=True, context={"request":request}
            )
            return Response(serializer.data, status=status.HTTP_200_OK) 
        
            
            
            
            
            

        
        
        
        
        
        
        
        
        
        
        