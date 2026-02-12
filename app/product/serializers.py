"""
    Serializers for product API
"""


from rest_framework import serializers
from core.models import Product


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'user', 'price']
        read_only_fields = ['id', 'user']

    def create(self, validated_data):
        return Product.objects.create(**validated_data)

    def retrieve(self, instance):
        return instance

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get(
            'description', instance.description)
        instance.price = validated_data.get('price', instance.price)
        instance.save()
        return instance


class ProductDetailSerializer(ProductSerializer):
    class Meta(ProductSerializer.Meta):
        # Include user field for detailed view
        fields = ProductSerializer.Meta.fields + ['user']
