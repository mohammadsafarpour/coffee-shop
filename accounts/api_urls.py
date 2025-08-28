# in accounts/api_urls.py

from rest_framework.routers import DefaultRouter
from rest_framework.authtoken import views as authtoken_views

from django.urls import path
from .api_views import AuthViewSet, ProfileViewSet, UserManagementViewSet, LoginOTPViewSet

router = DefaultRouter()
router.register('login-otp', LoginOTPViewSet, basename='login-otp')
router.register('auth', AuthViewSet, basename='auth')
router.register('profile', ProfileViewSet, basename='profile')
router.register('manage-users', UserManagementViewSet, basename='manage-users')

urlpatterns = [
    path('login/', authtoken_views.obtain_auth_token, name='api-login'),
] + router.urls