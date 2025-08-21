from django.urls import path
from .views import OrderHistoryApiView


urlpatterns = [
    path('history/', OrderHistoryApiView.as_view(), name='order-history-api'),
]