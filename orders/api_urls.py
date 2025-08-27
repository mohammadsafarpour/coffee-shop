# from rest_framework.routers import DefaultRouter
# from .api_views import OrderHistoryViewset

# router = DefaultRouter()
# router.register('history', OrderHistoryViewset, basename='order-history')
# urlpatterns = router.urls

# By normal url: 
# from django.urls import path
# from .views import OrderHistoryAPIView

# urlpatterns = [
#     path('history/', OrderHistoryAPIView.as_view(), name='order-history-api'),
# ]

from rest_framework.routers import DefaultRouter
from .api_views import OrderHistoryViewSet

router = DefaultRouter()
router.register('history', OrderHistoryViewSet, basename='order-history')
urlpatterns = router.urls