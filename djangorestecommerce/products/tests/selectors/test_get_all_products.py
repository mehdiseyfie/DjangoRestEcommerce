from django.test import TestCase

from djangorestecommerce.products.selectors import get_all_products
from djangorestecommerce.products.tests.factories import ProductFactory


class GetAllProductsTest(TestCase):

    def test_returns_all_products(self):
        product1 = ProductFactory()
        product2 = ProductFactory()

        result = list(get_all_products())

        self.assertEqual(len(result), 2)
        self.assertIn(product1, result)
        self.assertIn(product2, result)

    def test_returns_empty_queryset_when_no_products(self):
        result = get_all_products()

        self.assertEqual(result.count(), 0)
