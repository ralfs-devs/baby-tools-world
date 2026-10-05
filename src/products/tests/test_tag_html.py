from django.test import TestCase
from django.urls import reverse

from btw_app.utils import log_execution
from products.models import Category, Product, Tag


class TagTemplateTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(name="Test Category", slug="test-category")
        cls.product = Product.objects.create(name="Test Product", price="9.99", category=cls.category)

    @log_execution
    def test_product_detail_shows_heading_and_tags(self):
        """Test that the tag heading and assigned tags are rendered."""
        tag = Tag.objects.create(name="wooden")
        self.product.tags.add(tag)
        url = reverse("product_detail", args=[self.category.slug, self.product.pk])
        resp = self.client.get(url)
        self.assertContains(resp, "Product-Tags")
        self.assertContains(resp, "wooden")

    @log_execution
    def test_product_detail_without_tags_fallback(self):
        """Test the fallback label when a product has no tags."""
        url = reverse("product_detail", args=[self.category.slug, self.product.pk])
        resp = self.client.get(url)
        self.assertContains(resp, "Product-Tags")
        self.assertContains(resp, "no tags available")
