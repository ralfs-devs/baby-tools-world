from django.contrib import admin
from django.test import TestCase

from products.admin import ProductAdmin
from products.models import Tag


class TagAdminTestCase(TestCase):

    def test_tag_model_is_registered_in_admin(self) -> None:
        """Test that Tag is registered with a custom ModelAdmin in the admin site."""
        tag_admin = admin.site._registry.get(Tag)
        self.assertIsNotNone(tag_admin)
        self.assertIsInstance(tag_admin, admin.ModelAdmin)

    def test_product_admin_has_tags_filter(self) -> None:
        """Test that ProductAdmin includes 'tags' in list_filter."""
        self.assertIn("tags", ProductAdmin.list_filter)
