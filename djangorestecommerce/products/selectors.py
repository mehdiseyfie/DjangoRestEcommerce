from django.db.models import QuerySet
from djangorestecommerce.products.models import(
    Category, Product
)
from django.shortcuts import get_object_or_404

def get_category_by_slug(slug: str) -> Category: 
    return get_object_or_404(Category, slug=slug) 

def get_all_categories() -> QuerySet[Category]: 
    return Category.objects.all()