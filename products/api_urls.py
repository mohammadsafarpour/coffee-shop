from rest_framework.routers import DefaultRouter
from .api_views import (
    Api_ProductViewSet,
    Api_CategoryViewSet,
    Api_ProductImageViewSet,
    Api_IngredientViewSet,
)

router = DefaultRouter()
router.register(r'products', Api_ProductViewSet, basename='products')
router.register(r'categories', Api_CategoryViewSet, basename='categories')
router.register(r'product-images', Api_ProductImageViewSet, basename='product-images')
router.register(r'ingredients', Api_IngredientViewSet, basename='ingredient')

urlpatterns = router.urls