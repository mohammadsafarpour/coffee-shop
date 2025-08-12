from django.urls import path
from .views import ProductListView, ProductCreateView, ProductCategoryView #, toggle_favorite

from . import views
app_name = 'products'

urlpatterns = [

    path('', views.ProductListView.as_view(), name='product-list'),
    path('add/', views.ProductCreateView.as_view(), name='product-add'),
    path('<int:pk>/', views.ProductDetailView.as_view(), name='product-detail'),
    path('create/', ProductCreateView.as_view(), name='product-create'),
    path('category/<slug:category_slug>/', ProductCategoryView.as_view(), name='product_list_by_category'),
    # path('category/<slug:category_slug>/', views.product_list_by_category, name='product_list_by_category'),
    # path('toggle-favorite/<int:product_id>/', views.toggle_favorite, name='toggle-favorite'),
    
]