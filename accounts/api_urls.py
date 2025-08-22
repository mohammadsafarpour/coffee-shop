from django.urls import path, include
from rest_framework import routers
from .api_views import CustomUserViewSet, CustomAuthToken, CustomAuthTokenView

router = routers.DefaultRouter()
router.register(r'users', CustomUserViewSet, basename='users')



urlpatterns = [
    path('', include(router.urls)),
    path('api-token-auth/', CustomAuthToken.as_view(), name='api-token-auth'),
    path('api-token-auth-view/', CustomAuthTokenView.as_view(), name='api-token-auth-view'),
]