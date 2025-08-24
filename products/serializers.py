# # from rest_framework import serializers
# # from .models import Product, Category, ProductImage

# # # -----------------------------
# # #   Category Serializer
# # # -----------------------------
# # class CategorySerializer(serializers.ModelSerializer):
# #     class Meta:
# #         model = Category
# #         fields = [
# #             'id', 
# #             'name',
# #             'slug', 
# #             'description', 
# #             'price', 
# #             'is_active', 
# #             'stock',
# #             'api_tags',
# #             'api_main_image',
# #         ]


# # # -----------------------------
# # #   ProductImage Serializer
# # # -----------------------------
# # class ProductImageSerializer(serializers.ModelSerializer):
# #     image = serializers.ImageField(use_url=True)

# #     class Meta:
# #         model = ProductImage
# #         fields = ['id', 'product', 'image', 'alt_text']

# # # -----------------------------
# # #   Category Serializer
# # # -----------------------------
# # class CategorySerializer(serializers.ModelSerializer):
# #     class Meta:
# #         model = Category
# #         fields = ['id', 'name', 'slug']


# # # -----------------------------
# # #   Product Serializer
# # # -----------------------------
# # class ProductSerializer(serializers.ModelSerializer):
# #     category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
# #     image_main = serializers.ImageField(read_only=True)
# #     images = ProductImageSerializer(many=True, read_only=True)

# #     class Meta:
# #         model = Product
# #         fields = fields = "__all__"

# #===================================== new one ================

# from rest_framework import serializers
# from .models import Product, Category, ProductImage, Ingredient

# # -----------------------------
# #   Category Serializer
# # -----------------------------
# class CategorySerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Category
#         fields = ['id', 'name', 'slug']
#         read_only_fields = ['slug']

# # -----------------------------
# #   Ingredient Serializer
# # -----------------------------
# class IngredientSerializer(serializers.ModelSerializer):
#     id = serializers.IntegerField(required=False)
#     class Meta:
#         model = Ingredient
#         fields = ['id', 'name']

# # -----------------------------
# #   ProductImage Serializer
# # -----------------------------
# class ProductImageSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ProductImage
#         fields = ['id', 'product','image', 'alt_text']

# # -----------------------------
# #   Product Serializer
# # -----------------------------
# class ProductSerializer(serializers.ModelSerializer):
#     category = CategorySerializer(read_only=True)
#     category_id = serializers.PrimaryKeyRelatedField(
#         queryset=Category.objects.all(), source='category', write_only=True
#     )
#     ingredients = IngredientSerializer(many=True)
#     images = ProductImageSerializer(many=True, read_only=True)

#     class Meta:
#         model = Product
#         fields = [
#             'id', 'name', 'slug', 'description', 'price', 'stock', 'is_active', 
#             'category', 'category_id', 'image', 'images', 'ingredients', 'created_at',
#         ]
#         read_only_fields = ['slug', 'created_at']

#     def _handle_ingredients(self, product, ingredients_data):
#         product.ingredients.all().delete()
#         for ingredient_data in ingredients_data:
#             Ingredient.objects.create(product=product, **ingredient_data)

#     def create(self, validated_data):
#         ingredients_data = validated_data.pop('ingredients', [])
#         product = Product.objects.create(**validated_data)
#         self._handle_ingredients(product, ingredients_data)
#         return product

#     def update(self, instance, validated_data):
#         ingredients_data = validated_data.pop('ingredients', None)
#         instance = super().update(instance, validated_data)
#         if ingredients_data is not None:
#             self._handle_ingredients(instance, ingredients_data)
#         return instance

#============================= second one ==============================

from rest_framework import serializers
from .models import Product, Category, ProductImage, Ingredient

# -----------------------------
#   Category Serializer
# -----------------------------
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']
        read_only_fields = ['slug']

# -----------------------------
#   Ingredient Serializer
# -----------------------------
class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ['name']

# -----------------------------
#   ProductImage Serializer
# -----------------------------
class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'alt_text']

# -----------------------------
#   Product Serializer
# -----------------------------
class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source='category', write_only=True
    )

    ingredients = IngredientSerializer(many=True, required=False)
    is_available = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description', 'price', 'stock', 'is_active', 
            'is_available',
            'category', 'category_id', 'image', 'images', 'ingredients', 'created_at',
        ]
        read_only_fields = ['slug', 'created_at']

    def get_is_available(self, obj):
        return obj.is_active and obj.stock > 0

    def _handle_ingredients(self, product, ingredients_data):
        product.ingredients.all().delete()
        for ingredient_data in ingredients_data:
            Ingredient.objects.create(product=product, **ingredient_data)

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients', [])
        product = Product.objects.create(**validated_data)
        self._handle_ingredients(product, ingredients_data)
        return product

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients', None)
        instance = super().update(instance, validated_data)
        if ingredients_data is not None:
            self._handle_ingredients(instance, ingredients_data)
        return instance