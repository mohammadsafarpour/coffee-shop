from rest_framework import serializers
from .models import Product, Category, ProductImage

# -----------------------------
#   Category Serializer
# -----------------------------
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'title', 'slug']


# -----------------------------
#   ProductImage Serializer
# -----------------------------
class ProductImageSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(use_url=True)

    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'alt_text']


# -----------------------------
#   Product Serializer
# -----------------------------
class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    image_main = serializers.ImageField(read_only=True, use_url=True)
    images = ProductImageSerializer(source="productimage_set", many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'title', 'slug', 'description',
            'price', 'is_active', 'created_at',
            'category', 'image_main', 'images'
        ]
