from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, CategoryViewSet

app_name = 'products'

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'categories', CategoryViewSet, basename='category')


urlpatterns = [
    path('', include(router.urls)),
    path('', views.ProductListView.as_view(), name='product-list'),
    path('create/', views.ProductCreateView.as_view(), name='product-create'),
    path('<int:pk>/', views.ProductDetailView.as_view(), name='product-detail'),
    path('favorites/add/<int:product_id>/', views.add_to_favorites, name='add-to-favorites'),
    path('favorites/remove/<int:product_id>/', views.remove_from_favorites, name='remove-from-favorites'),
    path('category/<slug:category_slug>/', views.ProductCategoryView.as_view(), name='product_list_by_category'),
    
]