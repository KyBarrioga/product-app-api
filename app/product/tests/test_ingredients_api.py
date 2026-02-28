"""
Docstring for app.user.tests.test_ingredients_api
"""
from decimal import Decimal
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from core.models import Ingredients, Product
from product.serializers import IngredientsSerializer

INGREDIENTS_URL = reverse('product:ingredients-list')


def create_user(**params):
    """
    Helper function to create a user.
    """
    return get_user_model().objects.create_user(**params)


def detail_url(tag_id):
    """
    Return ingredient detail URL.
    """
    return reverse('product:ingredients-detail', args=[tag_id])


class PublicIngredientsAPITests(TestCase):
    """
    Test case for the Ingredients API endpoint.
    """

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """
        Test that authentication is required to access the ingredients API.
        """
        response = self.client.get(INGREDIENTS_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsAPITests(TestCase):
    """
    Test case for the Ingredients API endpoint for authenticated users.
    """

    def setUp(self):
        self.user = create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_ingredients(self):
        """Test retrieving a list of ingredients."""
        Ingredients.objects.create(user=self.user, name='Ingredient 1')
        Ingredients.objects.create(user=self.user, name='Ingredient 2')

        response = self.client.get(INGREDIENTS_URL)

        ingredients = Ingredients.objects.all().order_by('-name')
        serializer = IngredientsSerializer(ingredients, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        """Test that ingredients returned are for the authenticated user."""
        user2 = create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )
        Ingredients.objects.create(user=user2, name='Ingredient 3')
        Ingredients.objects.create(user=self.user, name='Ingredient 4')

        response = self.client.get(INGREDIENTS_URL)

        ingredients = Ingredients.objects.filter(
            user=self.user).order_by('-name')
        serializer = IngredientsSerializer(ingredients, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_update_ingredient(self):
        """Test updating an ingredient."""
        ingredient = Ingredients.objects.create(
            user=self.user, name='Ingredient 5')

        payload = {'name': 'Updated Ingredient'}
        url = detail_url(ingredient.id)
        response = self.client.patch(url, payload)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ingredient.refresh_from_db()
        self.assertEqual(ingredient.name, payload['name'])

    def test_delete_ingredient(self):
        """Test deleting an ingredient."""
        ingredient = Ingredients.objects.create(
            user=self.user, name='Ingredient 6')

        url = detail_url(ingredient.id)
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Ingredients.objects.filter(id=ingredient.id).exists())

    def test_filter_ingredients_assigned_to_products(self):
        """Test listing ingredients to those assigned to products."""
        ingredient1 = Ingredients.objects.create(
            user=self.user, name='Ingredient 7')
        ingredient2 = Ingredients.objects.create(
            user=self.user, name='Ingredient 8')
        product = Product.objects.create(
            name='Product 1',
            description='Sample Description',
            price=Decimal('19.99'),
            user=self.user,
        )
        product.ingredients.add(ingredient1)

        response = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})

        serializer1 = IngredientsSerializer(ingredient1)
        serializer2 = IngredientsSerializer(ingredient2)
        self.assertIn(serializer1.data, response.data)
        self.assertNotIn(serializer2.data, response.data)

    def test_filtered_ingredients_unique(self):
        """Test filtered ingredients returns a unique list."""
        ingredient = Ingredients.objects.create(
            user=self.user, name='Ingredient 9')
        Ingredients.objects.create(user=self.user, name='Ingredient 10')
        product1 = Product.objects.create(
            name='Sample Product',
            description='Sample Description',
            price=Decimal('19.99'),
            user=self.user,
        )
        product2 = Product.objects.create(
            name='Sample Product 2',
            description='Sample Description 2',
            price=Decimal('29.99'),
            user=self.user,
        )

        product1.ingredients.add(ingredient)
        product2.ingredients.add(ingredient)

        response = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})

        self.assertEqual(len(response.data), 1)
