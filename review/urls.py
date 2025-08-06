from django.urls import path
from . import views

urlpatterns = [
    path('<int:product_id>/', views.product_reviews, name='product_reviews'),
    path('add/<int:product_id>/', views.add_review, name='add_review'),
]
