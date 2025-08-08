from django.urls import path
from .views import SignUpView, DashboardView, ProfileEditView

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('profile/edit/', ProfileEditView.as_view(), name='profile-edit'),

]