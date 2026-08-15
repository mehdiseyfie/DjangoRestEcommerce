from django.http import Http404
from django.test import TestCase

from djangorestecommerce.products.selectors import get_category_by_slug
from djangorestecommerce.products.tests.factories import CategoryFactory


class GetCategoryBySlugTest(TestCase):

    def test_returns_category_for_existing_slug(self):
        category = CategoryFactory()

        result = get_category_by_slug(slug=category.slug)

        self.assertEqual(result, category)
        self.assertEqual(result.slug, category.slug)

    def test_raises_404_when_slug_does_not_exist(self):
        with self.assertRaises(Http404):
            get_category_by_slug(slug="non-existent-slug")