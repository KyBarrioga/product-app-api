from decimal import Decimal

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status
from core.models import Product

from product.serializers import (ProductSerializer, ProductDetailSerializer)

# CREATE_PRODUCT_URL = reverse('product:product-create')
# LIST_PRODUCT_URL = reverse('product:product-list')
PRODUCT_URL = reverse('product:product-list')


def detail_url(product_id):
    """Return product detail URL"""
    return reverse('product:product-detail', args=[product_id])


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
        response = self.client.post(PRODUCT_URL, {})
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

        response = self.client.get(PRODUCT_URL)

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

        response = self.client.get(PRODUCT_URL)
        products = Product.objects.filter(user=self.user)
        serializer = ProductSerializer(products, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data, serializer.data)

    def test_get_product_detail(self):
        """Test retrieving product detail"""
        product = create_product(user=self.user)
        url = detail_url(product.id)
        response = self.client.get(url)

        serializer = ProductDetailSerializer(product)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_product(self):
        """Test creating a new product"""
        payload = {
            'name': 'New Product',
            'description': 'New Description',
            'price': Decimal('29.99'),
        }
        response = self.client.post(PRODUCT_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        product = Product.objects.get(id=response.data['id'])
        for key in payload:
            self.assertEqual(getattr(product, key), payload[key])
        self.assertEqual(product.user, self.user)

    def test_partial_update_product(self):
        """Test updating a product with PATCH"""
        product = create_product(user=self.user)
        url = detail_url(product.id)
        payload = {'name': 'Updated Product'}
        response = self.client.patch(url, payload)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        product.refresh_from_db()
        self.assertEqual(product.name, payload['name'])

    def test_full_update_product(self):
        """Test updating a product with PUT"""
        product = create_product(
            user=self.user,
            name='Original Product',
            description='Original Description',
            price=Decimal('19.99'),
        )
        url = detail_url(product.id)
        payload = {
            'name': 'Updated Product',
            'description': 'Updated Description',
            'price': Decimal('39.99'),
        }
        response = self.client.put(url, payload)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        product.refresh_from_db()
        for key in payload:
            self.assertEqual(getattr(product, key), payload[key])

    def test_update_product_user_returns_error(self):
        """Test that updating the product user returns an error"""
        product = create_product(user=self.user)
        url = detail_url(product.id)
        new_user = create_user(
            username='newuser',
            email='newuser@example.com',
            password='newpass123'
        )
        payload = {'user': new_user.id}
        response = self.client.patch(url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_product(self):
        """Test deleting a product"""
        product = create_product(user=self.user)
        url = detail_url(product.id)
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Product.objects.filter(id=product.id).exists())

    def test_delete_other_users_product(self):
        """Test that deleting another user's product returns an error"""
        other_user = create_user(
            username='otheruser',
            email='otheruser@example.com',
            password='otherpass123'
        )
        product = create_product(user=other_user)
        url = detail_url(product.id)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
