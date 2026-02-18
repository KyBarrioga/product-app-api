from django.urls import (path, include)
from .views import ProductViewSet, TagViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('products', ProductViewSet, basename='product')
router.register('tags', TagViewSet, basename='tags')

app_name = 'product'

urlpatterns = [
    path('', include(router.urls)),
]
