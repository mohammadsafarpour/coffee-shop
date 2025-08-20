from rest_framework import serializers
from .models import Product, Category, ProductImage, Ingredient

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'alt_text']

class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ['id', 'name']

class ProductSerializer(serializers.ModelSerializer):
   
    category = CategorySerializer(read_only=True)
    
    images = ProductImageSerializer(many=True, read_only=True)
    ingredients = IngredientSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 
            'name', 
            'slug', 
            'description', 
            'price', 
            'stock', 
            'is_active',
            'category', 
            'images',
            'ingredients',
        ]
