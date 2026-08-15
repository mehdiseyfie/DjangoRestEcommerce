from django.http import Http404
from django.test import TestCase

from djangorestecommerce.products.selectors import get_product_by_slug
from djangorestecommerce.products.tests.factories import ProductFactory


class GetProductBySlugTest(TestCase):

    def test_returns_product_for_existing_slug(self):
        product = ProductFactory()

        result = get_product_by_slug(slug=product.slug)

        self.assertEqual(result, product)
        self.assertEqual(result.slug, product.slug)

    def test_raises_404_when_slug_does_not_exist(self):
        with self.assertRaises(Http404):
            get_product_by_slug(slug="non-existent-product-slug")
