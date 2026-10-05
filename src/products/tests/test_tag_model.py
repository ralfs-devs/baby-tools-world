from django.core.exceptions import ValidationError
from django.test import TestCase

from products.models import Category, Product, Tag

# from btw_app.utils import log_execution


class TagTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(name="Test Category", slug="test-category")
        cls.product = Product.objects.create(name="Test Product", price="9.99", category=cls.category)
        cls.tag_wooden = Tag.objects.create(name="wooden")
        cls.tag_colorful = Tag.objects.create(name="colorful")

    # SUCCESS TESTS
    # @log_execution
    def test_successful_tag_creation(self):
        """Test that a tag is created with auto-generated timestamps."""
        self.tag_wooden.full_clean()
        self.assertTrue(Tag.objects.filter(name="wooden").exists())
        self.assertEqual(self.tag_wooden.name, "wooden")
        self.assertIsNotNone(Tag.objects.first().created_at)
        self.assertIsNotNone(Tag.objects.first().updated_at)

    # @log_execution
    def test_tag_string_representation(self):
        """Test that Tag returns its name as string representation."""
        self.assertEqual(str(self.tag_wooden), "wooden")

    # @log_execution
    def test_product_tags_optional(self):
        """Test that a product without tags is valid."""
        self.product.full_clean()
        self.assertEqual(list(self.product.tags.all()), [])

    # @log_execution
    def test_product_tag_assignment(self):
        """Test assigning a tag to a product via the ManyToMany relation."""
        self.product.tags.add(self.tag_wooden)
        self.assertIn(self.tag_wooden, self.product.tags.all())
        self.assertIn(self.product, self.tag_wooden.products.all())

    # MANY TO MANY RELATION TESTS
    # @log_execution
    def test_add_multiple_tags_to_product(self):
        """Test that multiple tags can be assigned to a product."""
        self.product.tags.add(self.tag_wooden, self.tag_colorful)
        self.assertEqual(self.product.tags.count(), 2)

    # @log_execution
    def test_remove_tag_from_product(self):
        """Test that a tag can be removed from a product."""
        self.product.tags.add(self.tag_wooden, self.tag_colorful)
        self.product.tags.remove(self.tag_wooden)
        self.assertEqual(self.product.tags.count(), 1)

    # @log_execution
    def test_clear_all_tags_from_product(self):
        """Test that all tags can be removed from a product at once."""
        self.product.tags.add(self.tag_wooden, self.tag_colorful)
        self.product.tags.clear()
        self.assertEqual(self.product.tags.count(), 0)

    # @log_execution
    def test_same_tag_on_multiple_products(self):
        """Test that one tag can be shared across multiple products."""
        other_product = Product.objects.create(name="Other Product", price="4.99", category=self.category)
        self.product.tags.add(self.tag_wooden)
        other_product.tags.add(self.tag_wooden)
        self.assertEqual(self.tag_wooden.products.count(), 2)

    # @log_execution
    def test_deleting_tag_keeps_product(self):
        """Test that deleting a tag does not delete the product."""
        self.product.tags.add(self.tag_wooden)
        self.tag_wooden.delete()
        self.assertTrue(Product.objects.filter(pk=self.product.pk).exists())
        self.assertEqual(self.product.tags.count(), 0)

    # @log_execution
    def test_deleting_product_keeps_tag(self):
        """Test that deleting a product does not delete the tag."""
        self.product.tags.add(self.tag_wooden)
        self.product.delete()
        self.assertTrue(Tag.objects.filter(pk=self.tag_wooden.pk).exists())
        self.assertEqual(self.tag_wooden.products.count(), 0)

    # FAILURE TESTS
    # @log_execution
    def test_failure_tag_creation_without_name(self):
        """Test that tag creation fails without a name."""
        tag = Tag()
        with self.assertRaises(ValidationError):
            tag.full_clean()

    # @log_execution
    def test_failure_tag_creation_with_too_long_name(self):
        """Test that tag creation fails with name > 50 characters."""
        tag = Tag(name="a" * 51)
        with self.assertRaises(ValidationError):
            tag.full_clean()

    # @log_execution
    def test_failure_tag_creation_with_duplicate_name(self):
        """Test that duplicate tag names are rejected."""
        tag = Tag(name="wooden")
        with self.assertRaises(ValidationError):
            tag.full_clean()
