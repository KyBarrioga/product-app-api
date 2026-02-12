"""
Docstring for app.user.views
"""

from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Product
from .serializers import ProductSerializer, ProductDetailSerializer


class ProductViewSet(viewsets.ModelViewSet):
    """View to create a new product"""
    serializer_class = ProductSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Product.objects.all()

    def get_queryset(self):
        """Retrieve products for authenticated user"""
        return self.queryset.filter(user=self.request.user).order_by('-id')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# class CreateTokenView(ObtainAuthToken):
#     """View to create a new auth token for user"""
#     serializer_class = AuthTokenSerializer
#     renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES

#     def post(self, request, *args, **kwargs):
#         return super().post(request, *args, **kwargs)


# class ManageUserView(generics.RetrieveUpdateAPIView):
#     """View to retrieve authenticated user"""
#     serializer_class = UserSerializer
#     authentication_classes = [authentication.TokenAuthentication]
#     permission_classes = [permissions.IsAuthenticated]

#     def get_object(self):
#         """Retrieve and return authenticated user"""
#         return self.request.user
