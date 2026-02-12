from django.urls import (path, include)
from .views import ProductViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('products', ProductViewSet, basename='product')

app_name = 'product'

urlpatterns = [
    path('', include(router.urls)),
    path('create/', ProductViewSet.as_view({'post': 'create'}), name='product-create'),
    path('list/', ProductViewSet.as_view({'get': 'list'}), name='product-list'),
]
