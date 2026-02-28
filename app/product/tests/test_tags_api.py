"""
Docstring for app.user.tests.test_tags_api
"""
from decimal import Decimal
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from core.models import Tag, Product
from product.serializers import TagSerializer

TAGS_URL = reverse('product:tags-list')


def create_user(**params):
    """
    Helper function to create a user.
    """
    return get_user_model().objects.create_user(**params)


def detail_url(tag_id):
    """
    Return tag detail URL.
    """
    return reverse('product:tags-detail', args=[tag_id])


class PublicTagsAPITests(TestCase):
    """
    Test case for the Tags API endpoint.
    """

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """
        Test that authentication is required to access the tags API.
        """
        response = self.client.get(TAGS_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsAPITests(TestCase):
    """
    Test case for the Tags API endpoint for authenticated users.
    """

    def setUp(self):
        self.user = create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_tags(self):
        """
        Test retrieving tags for the authenticated user.
        """
        Tag.objects.create(user=self.user, name='Vegan')
        Tag.objects.create(user=self.user, name='Dessert')

        response = self.client.get(TAGS_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['name'], 'Dessert')
        self.assertEqual(response.data[1]['name'], 'Vegan')

    def test_retrieve_tags_by_user(self):
        """
        Test that tags returned are for the authenticated user.
        """
        other_user = create_user(
            email='other@example.com',
            username='otheruser',
            password='testpass123'
        )
        Tag.objects.create(user=self.user, name='Vegan')
        Tag.objects.create(user=other_user, name='Dessert')

        tags = Tag.objects.filter(user=self.user)
        serializer = TagSerializer(tags, many=True)
        response = self.client.get(TAGS_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_tags_limited_to_user(self):
        """
        Test that only tags for the authenticated user are returned.
        """
        other_user = create_user(
            email='other@example.com',
            username='otheruser',
            password='testpass123'
        )
        Tag.objects.create(user=self.user, name='Vegan')
        Tag.objects.create(user=other_user, name='Dessert')

        tags = Tag.objects.filter(user=self.user)
        serializer = TagSerializer(tags, many=True)
        response = self.client.get(TAGS_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_update_tag(self):
        """
        Test updating a tag.
        """
        tag = Tag.objects.create(user=self.user, name='Vegan')
        payload = {'name': 'Vegetarian'}
        url = detail_url(tag.id)
        response = self.client.patch(url, payload)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        tag.refresh_from_db()
        self.assertEqual(tag.name, payload['name'])

    def test_delete_tag(self):
        """
        Test deleting a tag.
        """
        tag = Tag.objects.create(user=self.user, name='Vegan')
        url = detail_url(tag.id)
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Tag.objects.filter(id=tag.id).exists())

    def test_filter_tags_assigned_to_products(self):
        """
        Test filtering tags by those assigned to products.
        """
        tag1 = Tag.objects.create(user=self.user, name='Vegan')
        tag2 = Tag.objects.create(user=self.user, name='Dessert')
        product = Product.objects.create(
            name='Product 1',
            description='Sample Description',
            price=Decimal('19.99'),
            user=self.user
        )
        product.tags.add(tag1)

        response = self.client.get(TAGS_URL, {'assigned_only': 1})

        serializer1 = TagSerializer(tag1)
        serializer2 = TagSerializer(tag2)
        self.assertIn(serializer1.data, response.data)
        self.assertNotIn(serializer2.data, response.data)

    def test_filtered_tags_unique(self):
        """
        Test that filtered tags returns a unique list.
        """
        tag = Tag.objects.create(user=self.user, name='Vegan')
        Tag.objects.create(user=self.user, name='Dessert')
        product1 = Product.objects.create(
            name='Product 1',
            description='Sample Description',
            price=Decimal('19.99'),
            user=self.user
        )
        product2 = Product.objects.create(
            name='Product 2',
            description='Sample Description',
            price=Decimal('19.99'),
            user=self.user
        )
        product1.tags.add(tag)
        product2.tags.add(tag)

        response = self.client.get(TAGS_URL, {'assigned_only': 1})

        self.assertEqual(len(response.data), 1)
