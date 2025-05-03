from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.views.generic.base import RedirectView, TemplateView

# Import SimpleJWT views
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView,
)

# Schema view for Swagger documentation
schema_view = get_schema_view(
    openapi.Info(
        title="UniBazzar API",
        default_version='v1',
        description="Complete API documentation for UniBazzar marketplace application",
        terms_of_service="https://www.unibazzar.com/terms/",
        contact=openapi.Contact(email="contact@unibazzar.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    authentication_classes=[],
    patterns=[
        path('admin/', admin.site.urls),
        path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
        path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
        path('api/users/', include('users.urls')),
        path('api/password_reset/', include('django_rest_passwordreset.urls', namespace='password_reset')),
        path('accounts/', include('allauth.urls')),
        path('api/auth-drf/', include('rest_framework.urls', namespace='rest_framework'))
    ],
)

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Home page
    path('', TemplateView.as_view(template_name='home.html'), name='home'),

    # API Documentation (Swagger/Redoc)
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    # Redirect '/swagger/' to '/api/docs/'
    path('swagger/', RedirectView.as_view(url='/api/docs/', permanent=True), name='swagger-redirect'),

    # SimpleJWT Token Authentication Endpoints (Refresh and Verify only)
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    # User App Endpoints (Includes custom Login, Registration, Profile, etc.)
    path('api/users/', include('users.urls')),

    # Password Reset Endpoints (from django-rest-passwordreset)
    path('api/password_reset/', include('django_rest_passwordreset.urls', namespace='password_reset')),

    # Django Allauth URLs (Primarily for social auth flows if used)
    path('accounts/', include('allauth.urls')),

    # DRF Login/Logout URLs (For Browsable API)
    path('api/auth-drf/', include('rest_framework.urls', namespace='rest_framework')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 