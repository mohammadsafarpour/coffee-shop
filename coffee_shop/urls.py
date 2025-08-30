from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin

from django.views.generic.base import TemplateView

from django.contrib.auth import views as auth_views
from django.views.generic.base import TemplateView
from products.views import ProductCreateView
from accounts.api_views import JWTLoginView

from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

from accounts.api_views import JWTLoginView, DecoratedTokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/v1/', include('accounts.api_urls')),
    path('api/v1/', include('products.api_urls')),
    path('api/v1/', include('orders.api_urls')),
    path('api/v1/', include('review.api_urls')),
    path('api/v1/', include('notification.api_urls')),
        
    path('api/v1/token/', JWTLoginView.as_view(), name='token_obtain_pair'),
    path('api/v1/token/refresh/', DecoratedTokenRefreshView.as_view(), name='token_refresh'),

    path('api/v1/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/v1/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/v1/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    path('', TemplateView.as_view(template_name='base.html'), name='home'),
    path('accounts/login/',auth_views.LoginView.as_view(template_name='accounts/login.html'),name='login'),
    path('accounts/logout/',auth_views.LogoutView.as_view(template_name='accounts/logout.html'),name='logout'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/', include('accounts.urls')),
    path('orders/', include('orders.urls'), name='orders'),
    path('products/', include('products.urls'), name='products'),
    path('create/', ProductCreateView.as_view(), name='product-create'),
    path('notification/', include('notification.urls')),
    path('review/', include('review.urls')),  
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
