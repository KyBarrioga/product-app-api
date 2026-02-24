"""
Docstring for app.user.tests.test_ingredients_api
"""
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from core.models import Ingredients
from product.serializers import IngredientsSerializer

INGREDIENTS_URL = reverse('product:ingredients-list')

def create_user(**params):
    """
    Helper function to create a user.
    """
    return get_user_model().objects.create_user(**params)


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
        response = self.client.get(reverse(INGREDIENTS_URL))
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

        ingredients = Ingredients.objects.filter(user=self.user).order_by('-name')
        serializer = IngredientsSerializer(ingredients, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)