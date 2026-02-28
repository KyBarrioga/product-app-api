from decimal import Decimal

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status
from core.models import Product, Tag, Ingredients

import tempfile
import os
from PIL import Image
# from unittest.mock import patch

from product.serializers import (ProductSerializer, ProductDetailSerializer)

# CREATE_PRODUCT_URL = reverse('product:product-create')
# LIST_PRODUCT_URL = reverse('product:product-list')
PRODUCT_URL = reverse('product:product-list')


def detail_url(product_id):
    """Return product detail URL"""
    return reverse('product:product-detail', args=[product_id])


def image_upload_url(product_id):
    """Return URL for product image upload"""
    return reverse('product:product-upload-image', args=[product_id])


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

    def test_create_product_with_new_tags(self):
        """
        Test creating a product with new tags.
        """
        payload = {
            'name': 'Avocado Toast',
            'description':
                'Delicious avocado toast with a sprinkle of chili flakes.',
            'price': 5.00,
            'tags': [{'name': 'Breakfast'}, {'name': 'Healthy'}]
        }
        response = self.client.post(PRODUCT_URL, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        product = Product.objects.get(user=self.user)
        self.assertEqual(product.tags.count(), 2)
        self.assertTrue(product.tags.filter(name='Breakfast').exists())
        self.assertTrue(product.tags.filter(name='Healthy').exists())

    def test_create_product_with_existing_tags(self):
        """
        Test creating a product with existing tags.
        """
        Tag.objects.create(user=self.user, name='Breakfast')
        payload = {
            'name': 'Avocado Toast',
            'description':
                'Delicious avocado toast with a sprinkle of chili flakes.',
            'price': 5.00,
            'tags': [{'name': 'Breakfast'}, {'name': 'Healthy'}]
        }
        response = self.client.post(PRODUCT_URL, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        product = Product.objects.get(user=self.user)
        self.assertEqual(product.tags.count(), 2)
        self.assertTrue(product.tags.filter(name='Breakfast').exists())
        self.assertTrue(product.tags.filter(name='Healthy').exists())

    def test_create_product_with_tags(self):
        """Test creating a product with tags"""
        payload = {
            'name': 'Product with Tags',
            'description': 'Description with tags',
            'price': Decimal('49.99'),
            'tags': [{'name': 'Tag1'}, {'name': 'Tag2'}],
        }
        response = self.client.post(PRODUCT_URL, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        product = Product.objects.get(user=self.user)
        self.assertEqual(product.tags.count(), 2)
        self.assertTrue(product.tags.filter(name='Tag1').exists())
        self.assertTrue(product.tags.filter(name='Tag2').exists())

    def test_create_tag_on_update_product(self):
        """Test creating a tag when updating a product"""
        product = create_product(user=self.user)
        url = detail_url(product.id)
        payload = {
            'name': 'Updated Product',
            'tags': [{'name': 'New Tag'}],
        }
        response = self.client.patch(url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        new_tag = Tag.objects.get(user=self.user, name='New Tag')
        self.assertIn(new_tag, product.tags.all())
        self.assertTrue(product.tags.filter(name='New Tag').exists())

    def test_update_product_assign_tag(self):
        """Test assigning an existing tag when updating a product"""
        product = create_product(user=self.user)
        first_tag = Tag.objects.create(user=self.user, name='First Tag')
        product.tags.add(first_tag)
        url = detail_url(product.id)
        second_tag = Tag.objects.create(user=self.user, name='Second Tag')
        payload = {
            'tags': [{'name': 'Second Tag'}],
        }
        response = self.client.patch(url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(second_tag, product.tags.all())
        self.assertNotIn(first_tag, product.tags.all())

    def test_clear_product_tags(self):
        """Test clearing a product's tags"""
        product = create_product(user=self.user)
        tag = Tag.objects.create(user=self.user, name='Tag to Clear')
        product.tags.add(tag)
        url = detail_url(product.id)
        payload = {
            'tags': [],
        }
        response = self.client.patch(url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(product.tags.count(), 0)
        self.assertFalse(product.tags.filter(name='Tag to Clear').exists())

    def test_create_product_with_new_ingredients(self):
        """Test creating a product with new ingredients"""
        payload = {
            'name': 'Pasta',
            'description': 'Delicious pasta with tomato sauce.',
            'price': Decimal('12.99'),
            'ingredients': [{'name': 'Pasta'}, {'name': 'Tomato Sauce'}],
        }
        response = self.client.post(PRODUCT_URL, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        product = Product.objects.filter(user=self.user)
        self.assertEqual(product.count(), 1)
        product = Product.objects.get(user=self.user)
        self.assertEqual(product.ingredients.count(), 2)

        for ingredient in payload['ingredients']:
            self.assertTrue(
                product.ingredients.filter(name=ingredient['name']).exists()
            )

    def test_create_product_with_existing_ingredients(self):
        """Test creating a product with existing ingredients"""
        Ingredients.objects.create(user=self.user, name='Cabbage')
        payload = {
            'name': 'Soup',
            'description': 'Delicious soup with vegetables.',
            'price': Decimal('8.99'),
            'ingredients': [{'name': 'Cabbage'}, {'name': 'Vegetables'}],
        }
        response = self.client.post(PRODUCT_URL, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        product = Product.objects.filter(user=self.user)
        self.assertEqual(product.count(), 1)
        product = Product.objects.get(user=self.user)
        self.assertEqual(product.ingredients.count(), 2)

        for ingredient in payload['ingredients']:
            self.assertTrue(
                product.ingredients.filter(name=ingredient['name']).exists()
            )

    def test_create_ingredient_on_update_product(self):
        """Test creating an ingredient when updating a product"""
        product = create_product(user=self.user)
        url = detail_url(product.id)
        payload = {
            'name': 'Updated Product',
            'ingredients': [{'name': 'New Ingredient'}],
        }
        response = self.client.patch(url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        product = Product.objects.get(id=product.id)  # Refresh product from DB
        self.assertEqual(product.name, 'Updated Product')  # Check name update

        new_ingredient = Ingredients.objects.get(
            user=self.user, name='New Ingredient')
        self.assertIn(new_ingredient, product.ingredients.all())
        self.assertTrue(
            product.ingredients.filter(name='New Ingredient').exists()
        )

    def test_update_product_assign_ingredient(self):
        """Test assigning an existing ingredient when updating a product"""
        product = create_product(user=self.user)
        first_ingredient = Ingredients.objects.create(
            user=self.user, name='First Ingredient')
        product.ingredients.add(first_ingredient)
        url = detail_url(product.id)
        second_ingredient = Ingredients.objects.create(
            user=self.user, name='Second Ingredient')
        payload = {
            'ingredients': [{'name': 'Second Ingredient'}],
        }
        response = self.client.patch(url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(second_ingredient, product.ingredients.all())
        self.assertNotIn(first_ingredient, product.ingredients.all())

    def test_clear_product_ingredients(self):
        """Test clearing a product's ingredients"""
        product = create_product(user=self.user)
        ingredient = Ingredients.objects.create(
            user=self.user, name='Ingredient to Clear')
        product.ingredients.add(ingredient)
        url = detail_url(product.id)
        payload = {
            'ingredients': [],
        }
        response = self.client.patch(url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(product.ingredients.count(), 0)
        self.assertFalse(
            product.ingredients.filter(name='Ingredient to Clear').exists()
        )

    def test_filter_by_tags(self):
        """Test filtering products by tags"""
        product1 = create_product(user=self.user, name='Product 1')
        product2 = create_product(user=self.user, name='Product 2')
        tag1 = Tag.objects.create(user=self.user, name='Tag1')
        tag2 = Tag.objects.create(user=self.user, name='Tag2')
        product1.tags.add(tag1)
        product2.tags.add(tag2)
        product3 = create_product(user=self.user, name='Product 3')

        response = self.client.get(
            PRODUCT_URL, {'tags': f'{tag1.id},{tag2.id}'})
        serializer1 = ProductSerializer(product1)
        serializer2 = ProductSerializer(product2)
        serializer3 = ProductSerializer(product3)

        self.assertIn(serializer1.data, response.data)
        self.assertIn(serializer2.data, response.data)
        self.assertNotIn(serializer3.data, response.data)

    def test_filter_by_ingredients(self):
        """Test filtering products by ingredients"""
        product1 = create_product(user=self.user, name='Product 1')
        product2 = create_product(user=self.user, name='Product 2')
        ingredient1 = Ingredients.objects.create(
            user=self.user, name='Ingredient1')
        ingredient2 = Ingredients.objects.create(
            user=self.user, name='Ingredient2')
        product1.ingredients.add(ingredient1)
        product2.ingredients.add(ingredient2)
        product3 = create_product(user=self.user, name='Product 3')

        response = self.client.get(
            PRODUCT_URL, {'ingredients': f'{ingredient1.id},{ingredient2.id}'})
        serializer1 = ProductSerializer(product1)
        serializer2 = ProductSerializer(product2)
        serializer3 = ProductSerializer(product3)

        self.assertIn(serializer1.data, response.data)
        self.assertIn(serializer2.data, response.data)
        self.assertNotIn(serializer3.data, response.data)


class ProductImageUploadTests(TestCase):
    """Test cases for uploading product images"""

    def setUp(self):
        """Set up test client and sample data"""
        self.client = APIClient()
        self.user = create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        self.product = create_product(user=self.user)

    def tearDown(self):
        """Clean up any created files after tests"""
        self.product.refresh_from_db()
        if self.product.image:
            if os.path.exists(self.product.image.path):
                # self.product.image.delete()  # Delete the image file
                os.remove(self.product.image.path)

    def test_upload_product_image(self):
        """Test uploading an image to a product"""
        url = image_upload_url(self.product.id)
        with tempfile.NamedTemporaryFile(suffix='.jpg') as temp_image:
            image = Image.new('RGB', (100, 100))
            image.save(temp_image, format='JPEG')
            temp_image.seek(0)
            response = self.client.post(
                url, {'image': temp_image}, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.product.refresh_from_db()
        self.assertIn('image', response.data)
        self.assertTrue(os.path.exists(self.product.image.path))

    def test_upload_product_image_invalid(self):
        """Test uploading an invalid image"""
        url = image_upload_url(self.product.id)
        response = self.client.post(
            url, {'image': 'notanimage'}, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
