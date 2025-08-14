from django.urls import path
from . import views

app_name = 'review'

urlpatterns = [
    path('<int:product_id>/', views.product_reviews, name='product_reviews'),
    path('add/<int:product_id>/', views.add_review, name='add_review'),
    path('my-reviews/', views.UserReviewsView.as_view(), name='user_reviews'),
]
