from django.urls import path
from . import views


app_name = 'orders'

urlpatterns = [
    path('', views.order_list, name='order_list'),
    path('add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('increase/<int:product_id>/', views.increase_quantity, name='increase_quantity'),
    path('decrease/<int:product_id>/', views.decrease_quantity, name='decrease_quantity'),
    path('payment/request/', views.payment_request, name='payment_request'),
    path('payment/verify/', views.payment_verify, name='payment_verify'),
]