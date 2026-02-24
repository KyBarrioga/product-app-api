"""
Tests for core models.
"""

from decimal import Decimal

from django.test import TestCase
from django.contrib.auth import get_user_model
from core import models


def create_user(**params):
    """Helper function to create a new user"""
    return get_user_model().objects.create_user(**params)


class ModelsTests(TestCase):
    """Test for models"""

    def test_create_user_with_email_successful(self):
        """Test creating a user with an email is successful"""
        email = 'test@example.com'
        password = 'testpass123'
        username = 'testuser'
        user = get_user_model().objects.create_user(
            username=username,
            email=email,
            password=password,
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test the email for a new user is normalized"""
        sample_emails = [
            ['test@EXAMPLE.com', 'test@example.com'],
            ['Test2@example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.COM', 'TEST3@example.com'],
            ['test4@Example.COM', 'test4@example.com']
        ]

        for i, (email, expected) in enumerate(sample_emails):
            user = get_user_model().objects.create_user(
                username='testuser{}'.format(i),
                email=email,
                password='testpass123'
            )
            print(
                f'Created user {user.username} with email \
                    {user.email} expected {expected}')
            self.assertEqual(user.email, expected)

    def test_create_user_without_email_raises_error(self):
        """Test creating a user without an email raises a ValueError."""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(
                username='testuser',
                email='',
                password='testpass123'
            )

    def test_create_superuser(self):
        """Test creating a superuser"""
        user = get_user_model().objects.create_superuser(
            username='superuser',
            email='superuser@example.com',
            password='superpass123'
        )
        self.assertTrue(user.is_superuser)

    def test_create_product(self):
        """Test creating a product is successful"""
        user = get_user_model().objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        product = models.Product.objects.create(
            user=user,
            name='Sample Product',
            price=Decimal('10.00'),
            description='Sample description'
        )
        self.assertEqual(product.name, 'Sample Product')
        self.assertEqual(product.price, Decimal('10.00'))
        self.assertEqual(product.description, 'Sample description')
        self.assertEqual(product.user, user)

    def test_create_tag(self):
        """Test creating a tag is successful"""
        user = create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        tag = models.Tag.objects.create(
            user=user,
            name='Test Tag'
        )
        self.assertEqual(tag.name, 'Test Tag')
        self.assertEqual(tag.user, user)

    def test_create_ingredient(self):
        """Test creating an ingredient is successful"""
        user = create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        ingredient = models.Ingredients.objects.create(
            user=user,
            name='Test Ingredient'
        )
        self.assertEqual(ingredient.name, 'Test Ingredient')
        self.assertEqual(ingredient.user, user)