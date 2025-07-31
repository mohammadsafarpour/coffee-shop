from django.urls import path
from . import views

urlpatterns = [

    path('', views.ProductListView.as_view(), name='product-list'),
    path('add/', views.ProductCreateView.as_view(), name='product-add'),
]