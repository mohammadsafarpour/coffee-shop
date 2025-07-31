from django.urls import path
from .views import SignUpView, DashboardView

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    # path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'),
    #     name='login'),

]