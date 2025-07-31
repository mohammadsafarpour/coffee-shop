from django.urls import path
from django.contrib.auth import views
from .forms import EmailAuthenticationForm

urlpatterns = [
    path('login/', auth_views.Loginview.as_view(
        template_name = 'accounts/login.html'
    ))
]

