"""
    Serializers for product API
"""


from rest_framework import serializers
from core.models import Product, Tag


class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'user', 'price']
        read_only_fields = ['id', 'user']

    def validate(self, attrs):
        # Check if 'user' is present in the input data (even if read-only)
        if 'user' in self.initial_data:
            raise serializers.ValidationError({
                'user': 'You cannot update the user of a product.'
            })
        return super().validate(attrs)

    def create(self, validated_data):
        return Product.objects.create(**validated_data)

    def retrieve(self, instance):
        return instance

    def update(self, instance, validated_data):
        # Raise error if user is in update data
        if 'user' in validated_data:
            raise serializers.ValidationError({
                'user': 'You cannot update the user of a product.'
            })
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get(
            'description', instance.description)
        instance.price = validated_data.get('price', instance.price)
        instance.save()
        return instance


class ProductDetailSerializer(ProductSerializer):
    class Meta(ProductSerializer.Meta):
        model = Product
        fields = ProductSerializer.Meta.fields + ['description']
        read_only_fields = ProductSerializer.Meta.read_only_fields + \
            ['id', 'user']


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']
