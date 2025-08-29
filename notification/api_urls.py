from rest_framework.routers import DefaultRouter
from .api_views import NotificationViewSet, NotificationActionViewSet

router = DefaultRouter()

router.register('notifications', NotificationViewSet, basename='notification')

router.register('actions', NotificationActionViewSet, basename='notification-actions')

urlpatterns = router.urls