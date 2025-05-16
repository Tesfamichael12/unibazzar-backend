from django.urls import path, include

from .views import (
    UserRegistrationView, EmailVerificationView, CustomTokenObtainPairView,
    LogoutView, ResendVerificationEmailView, PasswordResetConfirmPageView,
    UniversityListView
)
from .views_profile import UserListingsView # Added

app_name = 'users'

urlpatterns = [
    # Registration and verification
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('verify-email/<str:uidb64>/<str:token>/', EmailVerificationView.as_view(), name='verify-email'),
    path('resend-verification-email/', ResendVerificationEmailView.as_view(), name='resend-verification-email'),

    # Custom JWT login view (checks email verification)
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),

    # Logout
    path('logout/', LogoutView.as_view(), name='logout'),

    # University List
    path('universities/', UniversityListView.as_view(), name='university-list'),

    # User Listings
    path('<int:user_id>/listings/', UserListingsView.as_view(), name='user-all-listings'), # Added

    # Include profile-related URLs ( /me/, /me/avatar/, etc.)
    path('', include('users.urls_profile')),

    # URL pattern for the password reset form page
    path('password-reset-confirm-page/', PasswordResetConfirmPageView.as_view(), name='password_reset_confirm_page'),
]