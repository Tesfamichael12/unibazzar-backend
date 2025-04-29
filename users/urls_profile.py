from django.urls import path
from .views_profile import (
    UserProfileView, ProfilePictureUploadView, EmailChangeView,
    PhoneNumberUpdateView, PasswordChangeView
)

urlpatterns = [
    # User profile
    path('me/', UserProfileView.as_view(), name='user_profile'),
    path('me/avatar/', ProfilePictureUploadView.as_view(), name='profile_picture'),
    path('me/email/', EmailChangeView.as_view(), name='change_email'),
    path('me/phone/', PhoneNumberUpdateView.as_view(), name='update_phone'),
    path('me/password/', PasswordChangeView.as_view(), name='change_password'),
] 