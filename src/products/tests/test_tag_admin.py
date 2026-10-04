from django.contrib import admin
from django.test import TestCase

from products.admin import ProductAdmin
from products.models import Category, Product, Tag

class TagAdminTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(name="Test Category", slug="test-category")
        cls.product = Product.objects.create(name="Test Product", price="9.99", category=cls.category)
        cls.tag = Tag.objects.create(name="wooden")

    def test_tag_model_is_registered_in_admin(self):
        """Test that the Tag model is registered in the Django admin site."""
        self.assertIn(Tag, admin.site._registry)

    def test_product_admin_has_tags_filter(self):
        """Test that ProductAdmin includes 'tags' in list_filter."""
        self.assertIn("tags", ProductAdmin.list_filter)

    def test_tag_model_admin_exists(self):
        """Test that a custom ModelAdmin exists for Tag."""
        tag_admin_class = admin.site._registry.get(Tag)
        self.assertIsNotNone(tag_admin_class)