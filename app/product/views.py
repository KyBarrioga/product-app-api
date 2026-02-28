"""
Docstring for app.user.views
"""

from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from drf_spectacular.utils import (extend_schema_view,
                                   extend_schema, OpenApiParameter,
                                   OpenApiTypes)

from core.models import Ingredients, Product, Tag
from .serializers import (ProductImageSerializer, ProductSerializer,
                          ProductDetailSerializer, TagSerializer,
                          IngredientsSerializer)


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'assigned_only',
                OpenApiTypes.INT, enum=[0, 1],
                description=(
                    'Filter to ingredients assigned to products only '
                    '(0 or 1)'
                )
            )
        ]
    )
)
class ProductAttrViewSet(viewsets.GenericViewSet, mixins.ListModelMixin,
                         mixins.CreateModelMixin, mixins.UpdateModelMixin,
                         mixins.DestroyModelMixin):
    """Base viewset for user owned product attributes"""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Retrieve ingredients for authenticated user, with optional filtering.
        """
        assigned_only = self.request.query_params.get('assigned_only')
        queryset = self.queryset.filter(user=self.request.user)
        if assigned_only is not None:
            try:
                assigned_only = int(assigned_only)
            except (TypeError, ValueError):
                assigned_only = 0
            if assigned_only:
                queryset = queryset.filter(product__isnull=False).distinct()
        return queryset.order_by('-id')

    # Note: We do not need perform_create
    # def perform_create(self, serializer):
    #     """Create a new ingredient"""
    #     serializer.save(user=self.request.user)


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'tags',
                OpenApiTypes.STR,
                description='Comma separated list of tag IDs to filter'
            ),
            OpenApiParameter(
                'ingredients',
                OpenApiTypes.STR,
                description='Comma separated list of ingredient IDs to filter'
            )
        ]
    )
)
class ProductViewSet(viewsets.ModelViewSet):
    """View to manage Product APIs"""
    serializer_class = ProductSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Product.objects.all()

    def _params_to_ints(self, qs):
        """Convert a list of string IDs to a list of integers"""
        return [int(str_id) for str_id in qs.split(',')]

    def get_queryset(self):
        """Retrieve products for authenticated user"""
        tags = self.request.query_params.get('tags')
        ingredients = self.request.query_params.get('ingredients')
        queryset = self.queryset.filter(user=self.request.user)

        if tags:
            tag_ids = self._params_to_ints(tags)
            queryset = queryset.filter(tags__id__in=tag_ids)

        if ingredients:
            ingredient_ids = self._params_to_ints(ingredients)
            queryset = queryset.filter(ingredients__id__in=ingredient_ids)

        return queryset.order_by('-id').distinct()

    def perform_create(self, serializer):
        """Create a new product"""
        serializer.save(user=self.request.user)

    def get_serializer_class(self):
        """Return appropriate serializer class"""
        if self.action in ['list', 'retrieve']:
            return ProductDetailSerializer
        if self.action == 'upload_image':
            return ProductImageSerializer
        return self.serializer_class

    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """Endpoint for uploading an image to a product."""
        product = self.get_object()
        serializer = self.get_serializer(
            product,
            data=request.data
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TagViewSet(ProductAttrViewSet):
    """View to manage Tag APIs"""
    serializer_class = TagSerializer
    queryset = Tag.objects.all()


class IngredientsViewSet(ProductAttrViewSet):
    """View to manage Ingredients APIs"""
    serializer_class = IngredientsSerializer
    queryset = Ingredients.objects.all()
