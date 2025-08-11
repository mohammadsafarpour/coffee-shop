from django.urls import path
from .views import ProductListView, ProductCreateView #, toggle_favorite

from . import views

urlpatterns = [

    path('', views.ProductListView.as_view(), name='product-list'),
    path('add/', views.ProductCreateView.as_view(), name='product-add'),
    path('<int:pk>/', views.ProductDetailView.as_view(), name='product-detail'),
    path('create/', ProductCreateView.as_view(), name='product-create'),
    # path('toggle-favorite/<int:product_id>/', views.toggle_favorite, name='toggle-favorite'),
    
]