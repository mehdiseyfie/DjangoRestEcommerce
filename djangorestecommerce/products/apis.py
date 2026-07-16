from rest_framework import(status, serializers)
from rest_framework.views import APIView 
from rest_framework.response import Response 
from djangorestecommerce.products.models import(
    Category, Product
)
from drf_spectacular.utils import extend_schema 
from djangorestecommerce.products.selectors import (
    get_category_by_slug, get_all_categories
)
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication 



class CategoryApiView(APIView): 
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    class OutputCategory(serializers.ModelSerializer): 
        class Meta: 
            model = Category 
            fields = (
                "name",
                "slug",
                "description",
                
            ) 
    @extend_schema(responses=OutputCategory())
    def get(self, request, slug=None): 
        if slug: 
            category = get_category_by_slug(slug=slug) 
            serializer = self.OutputCategory(
                category, context={"request", request}
            )
            return Response(serializer.data, status=status.HTTP_200_OK) 
        else: 
            categories = get_all_categories()
            serializer = self.OutputCategory(
                categories, many=True, context={"request":request}
            )
        return Response(serializer.data, status=status.HTTP_200_OK)
        
        
        
        
        
        
        
        
        
        
        
        