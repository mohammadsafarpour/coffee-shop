from django.urls import path
from . import views

app_name = 'notification'

urlpatterns = [
    path('', views.notification_list, name='notification-list'),
    path('<int:notification_id>/', views.notification_detail, name='notification-detail'),
    path('mark-as-read/<int:notification_id>/', views.mark_notification_as_read, name='mark-notification-as-read'),
    path('mark-as-unread/<int:notification_id>/', views.mark_notification_as_unread, name='mark-notification-as-unread'),
    path('delete/<int:notification_id>/', views.delete_notification, name='delete-notification'),
    path('mark-all-as-read/', views.mark_all_notifications_as_read, name='mark-all-notifications-as-read'),
    path('clear-all/', views.clear_all_notifications, name='clear-all-notifications'),
]
