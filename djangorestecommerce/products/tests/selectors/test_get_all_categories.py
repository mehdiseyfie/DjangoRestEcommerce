from django.test import TestCase

from djangorestecommerce.products.selectors import get_all_categories
from djangorestecommerce.products.tests.factories import CategoryFactory


class GetAllCategoriesTest(TestCase):

    def test_returns_all_categories(self):
        category1 = CategoryFactory()
        category2 = CategoryFactory()

        result = list(get_all_categories())

        self.assertEqual(len(result), 2)
        self.assertIn(category1, result)
        self.assertIn(category2, result)

    def test_returns_empty_queryset_when_no_categories(self):
        result = get_all_categories()

        self.assertEqual(result.count(), 0)
