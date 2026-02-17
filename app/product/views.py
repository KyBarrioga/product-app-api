"""
Docstring for app.user.views
"""

from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Product
from .serializers import (ProductSerializer, ProductDetailSerializer)


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
