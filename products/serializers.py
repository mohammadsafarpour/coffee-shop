from rest_framework import serializers
from .models import Product, Category, ProductImage

# -----------------------------
#   Category Serializer
# -----------------------------
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = [
            'id', 
            'name',
            'slug', 
            'description', 
            'price', 
            'is_active', 
            'stock',
            'api_tags',
            'api_main_image',
        ]


# -----------------------------
#   ProductImage Serializer
# -----------------------------
class ProductImageSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(use_url=True)

    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'alt_text']

# -----------------------------
#   Category Serializer
# -----------------------------
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']


# -----------------------------
#   Product Serializer
# -----------------------------
class ProductSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    image_main = serializers.ImageField(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            'id',
            'category',
            'name',
            'slug',
            'description',
            'price',
            'is_active',
            'stock',
            'api_tags',
            'image_main',
            'images'
        ]