from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from .api_views import ReviewViewSet, ProductReviewViewSet
from products.api_views import Api_ProductViewSet

router = DefaultRouter()
router.register(r'products', Api_ProductViewSet, basename='products')
router.register(r'reviews', ReviewViewSet, basename='reviews')

products_router = routers.NestedDefaultRouter(router, r'products', lookup='product')
products_router.register(r'reviews', ProductReviewViewSet, basename='product-reviews')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(products_router.urls)),
]
