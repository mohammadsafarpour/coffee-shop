# from rest_framework import viewsets, permissions, filters
# from django_filters.rest_framework import DjangoFilterBackend
# from .models import Product, Category, ProductImage
# from .serializers import ProductSerializer, CategorySerializer, ProductImageSerializer

# class Api_CategoryViewSet(viewsets.ReadOnlyModelViewSet):
#     queryset = Category.objects.all()
#     serializer_class = CategorySerializer
#     permission_classes = [permissions.AllowAny]

# class Api_ProductViewSet(viewsets.ModelViewSet):
#     queryset = Product.objects.filter(is_active=True)
#     serializer_class = ProductSerializer
#     permission_classes = [permissions.AllowAny]
#     filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
#     filterset_fields = ['category', 'price']
#     search_fields = ['name', 'description']
#     ordering_fields = ['price', 'created_at']
#     ordering = ['-created_at']

# class Api_ProductImageViewSet(viewsets.ModelViewSet):
#     queryset = ProductImage.objects.all()
#     serializer_class = ProductImageSerializer
#     permission_classes = [permissions.IsAuthenticated]

#============================new one ====================

from rest_framework import viewsets, permissions
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from .models import Product, Category, ProductImage, Ingredient
from .serializers import (
    ProductSerializer, 
    CategorySerializer, 
    ProductImageSerializer,
    IngredientSerializer
)

class Api_CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'


class Api_ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category__slug', 'price']
    search_fields = ['name', 'description', 'category__name']
    ordering_fields = ['price', 'created_at']
    ordering = ['-created_at']
    lookup_field = 'slug'


class Api_ProductImageViewSet(viewsets.ModelViewSet):
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class Api_IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]