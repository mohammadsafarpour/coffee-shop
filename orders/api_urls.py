from django.urls import path
from rest_framework.routers import DefaultRouter
from .api_views import CartViewSet, OrderViewSet

router = DefaultRouter()
router.register('cart', CartViewSet, basename='cart')
router.register('orders', OrderViewSet, basename='order')

urlpatterns = [
] + router.urls