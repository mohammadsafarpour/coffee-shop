"""
URL configuration for coffee_shop project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.views.generic.base import TemplateView
from products.views import ProductCreateView #,ProductListView

# from drf_yasg.views import get_schema_view
# from drf_yasg import openapi
# from rest_framework import permissions
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

# security_definitions = {
#     'Token': {
#         'type': 'apiKey',
#         'in': 'header',
#         'name': 'Authorization'
#     }
# }

# schema_view = get_schema_view(
#    openapi.Info(
#       title="Coffee Shop API",
#       default_version='v1',
#       description="مستندات API برای پروژه کافه",
#       contact=openapi.Contact(email="contact@tamizcafe.local"),
#       license=openapi.License(name="MIT License"),
#    ),
#    public=True,
#    permission_classes=(permissions.AllowAny,),
# )


urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/v1/', include('accounts.api_urls')),
    path('api/v1/', include('products.api_urls')),
    path('api/v1/', include('orders.api_urls')),
    # path('api/v1/review/', include('review.api_urls')),
    # path('api/v1/notification/', include('notification.api_urls')),

    # path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    # path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

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
