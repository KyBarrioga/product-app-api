"""
Docstring for app.user.views
"""

from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Ingredients, Product, Tag
from .serializers import (ProductSerializer,
                          ProductDetailSerializer, TagSerializer,
                          IngredientsSerializer)


class ProductViewSet(viewsets.ModelViewSet):
    """View to manage Product APIs"""
    serializer_class = ProductSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Product.objects.all()

    def get_queryset(self):
        """Retrieve products for authenticated user"""
        return self.queryset.filter(user=self.request.user).order_by('-id')

    def perform_create(self, serializer):
        """Create a new product"""
        serializer.save(user=self.request.user)

    def get_serializer_class(self):
        """Return appropriate serializer class"""
        if self.action == 'list':
            return ProductDetailSerializer
        return self.serializer_class


class TagViewSet(viewsets.GenericViewSet, mixins.ListModelMixin,
                 mixins.CreateModelMixin, mixins.UpdateModelMixin,
                 mixins.DestroyModelMixin):
    """View to manage Tag APIs"""
    serializer_class = TagSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Tag.objects.all()

    def get_queryset(self):
        """Retrieve tags for authenticated user"""
        return self.queryset.filter(user=self.request.user).order_by('-id')

    def perform_create(self, serializer):
        """Create a new tag"""
        serializer.save(user=self.request.user)


class IngredientsViewSet(viewsets.GenericViewSet, mixins.ListModelMixin,
                         mixins.CreateModelMixin, mixins.UpdateModelMixin,
                         mixins.DestroyModelMixin):
    """View to manage Ingredients APIs"""
    serializer_class = IngredientsSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Ingredients.objects.all()

    def get_queryset(self):
        """Retrieve ingredients for authenticated user"""
        return self.queryset.filter(user=self.request.user).order_by('-id')

    def perform_create(self, serializer):
        """Create a new ingredient"""
        serializer.save(user=self.request.user)
