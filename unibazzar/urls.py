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
        description="API documentation for UniBazzar",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@unibazzar.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Home page
    path('', TemplateView.as_view(template_name='home.html'), name='home'),

    # API Documentation (Swagger/Redoc)
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    # Redirect '/swagger/' to '/api/docs/'
    path('swagger/', RedirectView.as_view(url='/api/docs/', permanent=True), name='swagger-redirect'),

    # SimpleJWT Token Authentication Endpoints (Refresh and Verify only)
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    # User App Endpoints (Includes custom Login, Registration, Profile, etc.)
    path('api/users/', include('users.urls')),

    # Products App Endpoints
    path('api/products/', include('products.urls')),

    # Chatbot App Endpoints
    path('api/chatbot/', include('chatbot.urls')),

    # Password Reset Endpoints (from django-rest-passwordreset)
    path('api/password_reset/', include('django_rest_passwordreset.urls', namespace='password_reset')),

    # Django Allauth URLs (Primarily for social auth flows if used)
    path('accounts/', include('allauth.urls')),

    # DRF Login/Logout URLs (For Browsable API)
    path('api/auth-drf/', include('rest_framework.urls', namespace='rest_framework')),

    # dj-rest-auth URLs
    path('dj-rest-auth/', include('dj_rest_auth.urls')),
    path('dj-rest-auth/registration/', include('dj_rest_auth.registration.urls')),
    # path('dj-rest-auth/google/', include('users.urls_social')), # Commented out due to ModuleNotFoundError
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)