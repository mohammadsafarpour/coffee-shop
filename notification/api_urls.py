from django.urls import path
from . import api_views

urlpatterns = [
    path('unread-count/', api_views.UnreadNotificationsCountView.as_view(), name='unread-count'),
    path('delete/<int:notification_id>/', api_views.DeleteNotificationView.as_view(), name='delete-notification'),
    path('mark/<int:notification_id>/', api_views.MarkNotificationAsRead.as_view(), name='mark-notification')
]