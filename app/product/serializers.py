"""
    Serializers for product API
"""


from rest_framework import serializers
from core.models import Ingredients, Product, Tag


class IngredientsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredients
        fields = ['id', 'name']
        read_only_fields = ['id']


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']


class ProductSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, required=False)
    ingredients = IngredientsSerializer(many=True, required=False)

    class Meta:
        model = Product
        fields = ['id', 'name', 'description',
                  'user', 'price', 'tags', 'ingredients']
        read_only_fields = ['id', 'user']

    def validate(self, attrs):
        # Check if 'user' is present in the input data (even if read-only)
        if 'user' in self.initial_data:
            raise serializers.ValidationError({
                'user': 'You cannot update the user of a product.'
            })
        return super().validate(attrs)

    def create(self, validated_data):
        """Create a new product."""
        tags = validated_data.pop('tags', [])
        ingredients = validated_data.pop('ingredients', [])
        product = Product.objects.create(**validated_data)
        user = self.context['request'].user

        for ingredient in ingredients:
            ingredient_obj, created = Ingredients.objects.get_or_create(
                user=user,
                **ingredient
            )
            product.ingredients.add(ingredient_obj)

        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(
                user=user,
                **tag
            )
            product.tags.add(tag_obj)

        return product

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

        # Update tags similar to create logic
        tags = validated_data.pop('tags', None)
        ingredients = validated_data.pop('ingredients', None)
        if tags is not None:
            auth_user = self.context['request'].user
            instance.tags.clear()
            for tag in tags:
                tag_obj, created = Tag.objects.get_or_create(
                    user=auth_user, **tag)
                instance.tags.add(tag_obj)

        if ingredients is not None:
            auth_user = self.context['request'].user
            instance.ingredients.clear()
            for ingredient in ingredients:
                ingredient_obj, created = Ingredients.objects.get_or_create(
                    user=auth_user, **ingredient)
                instance.ingredients.add(ingredient_obj)

        return instance


class ProductDetailSerializer(ProductSerializer):
    class Meta(ProductSerializer.Meta):
        model = Product
        fields = ProductSerializer.Meta.fields + ['description']
        read_only_fields = ProductSerializer.Meta.read_only_fields + \
            ['id', 'user']


class ProductImageSerializer(serializers.ModelSerializer):
    """Serializer for uploading images to products."""

    class Meta:
        model = Product
        fields = ['id', 'image']
        read_only_fields = ['id']
        extra_kwargs = {'image': {'required': 'True'}}
