from django.urls import path
from rest_framework.routers import DefaultRouter
from .views_profile import (
    UserProfileView, ProfilePictureUploadView, EmailChangeView,
    PhoneNumberUpdateView, PasswordChangeView, StudentProfileViewSet, MerchantProfileViewSet, TutorProfileViewSet, CampusAdminProfileViewSet
)

router = DefaultRouter()
router.register(r'student-profiles', StudentProfileViewSet, basename='student-profile')
router.register(r'merchant-profiles', MerchantProfileViewSet, basename='merchant-profile')
router.register(r'tutor-profiles', TutorProfileViewSet, basename='tutor-profile')
router.register(r'campus-admin-profiles', CampusAdminProfileViewSet, basename='campus-admin-profile')

urlpatterns = [
    # User profile
    path('me/', UserProfileView.as_view(), name='user_profile'),
    path('me/avatar/', ProfilePictureUploadView.as_view(), name='profile_picture'),
    path('me/email/', EmailChangeView.as_view(), name='change_email'),
    path('me/phone/', PhoneNumberUpdateView.as_view(), name='update_phone'),
    path('me/password/', PasswordChangeView.as_view(), name='change_password'),
]

urlpatterns += router.urls