from django.urls import path
from . import views
# from .views import ProductListView, ProductCreateView, ProductCategoryView, ProductDetailView #, toggle_favorite

app_name = 'products'

urlpatterns = [

    path('', views.ProductListView.as_view(), name='product-list'),
    path('create/', views.ProductCreateView.as_view(), name='product-create'),
    path('<int:pk>/', views.ProductDetailView.as_view(), name='product-detail'),
    path('favorites/add/<int:product_id>/', views.add_to_favorites, name='add-to-favorites'),
    path('favorites/remove/<int:product_id>/', views.remove_from_favorites, name='remove-from-favorites'),
    path('category/<slug:category_slug>/', views.ProductCategoryView.as_view(), name='product_list_by_category'),
    # path('add/', views.ProductCreateView.as_view(), name='product-add'),
    # path('category/<slug:category_slug>/', views.product_list_by_category, name='product_list_by_category'),
    # path('toggle-favorite/<int:product_id>/', views.toggle_favorite, name='toggle-favorite'),
    
]