from decimal import Decimal

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status
from core.models import Product

from product.serializers import ProductSerializer

CREATE_PRODUCT_URL = reverse('product:product-create')
LIST_PRODUCT_URL = reverse('product:product-list')


def create_user(**params):
    """Helper function to create a new user"""
    return get_user_model().objects.create_user(**params)


def create_product(user, **params):
    """Helper function to create and return a sample product"""
    defaults = {
        'name': 'Sample Product',
        'description': 'Sample Description',
        'price': Decimal('19.99'),
        'user': user,
    }
    defaults.update(params)
    return Product.objects.create(**defaults)


class PublicProductAPITestCase(TestCase):
    """Test cases for Product API endpoints"""

    def setUp(self):
        """Set up test client and sample data"""
        self.client = APIClient()

    def test_authentication_required(self):
        """Test that authentication is required to access the endpoint"""
        response = self.client.post(CREATE_PRODUCT_URL, {})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateProductAPITestCase(TestCase):
    """Test cases for authenticated Product API endpoints"""

    def setUp(self):
        """Set up test client and sample data"""
        self.client = APIClient()
        self.user = create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)

    def test_retrieve_products(self):
        """Test retrieving a list of products"""
        create_product(user=self.user)
        create_product(user=self.user, name='Another Product')

        response = self.client.get(LIST_PRODUCT_URL)

        products = Product.objects.all().order_by('-id')
        serializer = ProductSerializer(products, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_product_list_limited_to_user(self):
        """Test that products returned are for the authenticated user"""
        other_user = create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass123'
        )
        create_product(user=other_user, name='Other Product')
        create_product(user=self.user, name='User Product')

        response = self.client.get(LIST_PRODUCT_URL)
        products = Product.objects.filter(user=self.user)
        serializer = ProductSerializer(products, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data, serializer.data)

    # def test_create_product(self):
    #     """Test creating a new product"""
    #     self.client.force_authenticate(user=self.user)
    #     product = create_product(user=self.user)
    #     print(f'Created product: {product.price, product.name,
    #       product.description, product.user, product.id}')

    # def test_list_products(self):
    #     """Test listing all products"""
    #     response = self.client.get('/api/products/')
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)

    # def test_retrieve_product(self):
    #     """Test retrieving a single product"""
    #     product = Product.objects.create(**self.product_data)
    #     response = self.client.get(f'/api/products/{product.id}/')
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)

    # def test_update_product(self):
    #     """Test updating a product"""
    #     product = Product.objects.create(**self.product_data)
    #     self.client.force_authenticate(user=self.user)
    #     updated_data = {**self.product_data, 'price': 39.99}
    #     response = self.client.put(f'/api/products/{product.id}/',
    #                  updated_data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)

    # def test_delete_product(self):
    #     """Test deleting a product"""
    #     product = Product.objects.create(**self.product_data)
    #     self.client.force_authenticate(user=self.user)
    #     response = self.client.delete(f'/api/products/{product.id}/')
    #     self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
