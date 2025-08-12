from django.urls import path
from . import views

app_name = 'notification'

urlpatterns = [
    path('', views.notification_list, name='notification-list'),
    path('mark-as-read/<int:notification_id>/', views.mark_notification_as_read, name='mark-notification-as-read'),
]
