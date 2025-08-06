from django.urls import path
from .views import ProductListView, ProductCreateView, ToggleFavoriteView

from . import views

urlpatterns = [

    path('', views.ProductListView.as_view(), name='product-list'),
    path('add/', views.ProductCreateView.as_view(), name='product-add'),
    path('<int:pk>/', views.ProductDetailView.as_view(), name='product-detail'),
    path('create/', ProductCreateView.as_view(), name='product-create'),
    # path('favorite/<int:product_id>/toggle/', toggle_favorite, name='toggle-favorite'),

]
# from .views import ProductListView, ProductDetailView, 
