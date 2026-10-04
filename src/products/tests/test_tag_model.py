"""Tests for the Tag model."""
from django.test import TestCase
from products.models import Product, Tag


class TagModelTest(TestCase):
    """Tests for the Tag model attributes and relations."""

    def setUp(self) -> None:
        self.tag = Tag.objects.create(name="wooden")
        self.product = Product.objects.first()

    def test_str_returns_name(self) -> None:
        """Test that Tag returns its name as string representation."""
        self.assertEqual(str(self.tag), "wooden")

    def test_timestamps_auto_created(self) -> None:
        """Test that created_at and updated_at are auto-generated."""
        self.assertIsNotNone(self.tag.created_at)
        self.assertIsNotNone(self.tag.updated_at)

    def test_product_without_tags(self) -> None:
        """Test that a product without tags is valid."""
        self.assertEqual(list(self.product.tags.all()), [])