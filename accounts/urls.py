from django.urls import path
from .views import SignUpView, DashboardView, ProfileEditView, ProfileFavoritesView, ProfileRemoveFavoriteView, ProfileNotificationsView


urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('profile/edit/', ProfileEditView.as_view(), name='profile-edit'),
    path('profile/<int:user_id>/favorites/', ProfileFavoritesView.as_view(), name='profile-favorites'),
    path('profile/<int:user_id>/notifications/', ProfileNotificationsView.as_view(), name='profile-notifications'),
    path('profile/<int:user_id>/remove-favorite/<int:product_id>/', ProfileRemoveFavoriteView.as_view(), name='remove-from-favorites'),
    
]