from django.urls import path, include
# from rest_framework.routers import DefaultRouter
from .views import (
    ProductListView, ProductCreateView, ProductDetailView,
    ProductCategoryView, product_reviews,
    add_to_favorites, remove_from_favorites,
    # Api_ProductViewSet, Api_CategoryViewSet, Api_ProductImageViewSet
)

# router = DefaultRouter()
# router.register(r'api_products', Api_ProductViewSet, basename='api_products')
# router.register(r'api_categories', Api_CategoryViewSet, basename='api_categories')
# router.register(r'api_product_images', Api_ProductImageViewSet, basename='api_product_images')

app_name = 'products'

urlpatterns = [

    path('', ProductListView.as_view(), name='product-list'),
    path('create/', ProductCreateView.as_view(), name='product-create'),
    path('<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('category/<slug:category_slug>/', ProductCategoryView.as_view(), name='product-category'),
    path('<int:product_id>/reviews/', product_reviews, name='product-reviews'),
    path('<int:product_id>/favorite/add/', add_to_favorites, name='add-to-favorites'),
    path('<int:product_id>/favorite/remove/', remove_from_favorites, name='remove-from-favorites'),
    path('<slug:category_slug>/', ProductCategoryView.as_view(), name='product_list_by_category'),
    # path('api/', include(router.urls)),
    

]