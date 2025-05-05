from rest_framework.routers import DefaultRouter
from .views import (
    MerchantProductViewSet,
    StudentProductViewSet,
    TutorServiceViewSet,
    ReviewViewSet,
    CategoryViewSet,
)

router = DefaultRouter()
router.register(r'merchant-products', MerchantProductViewSet, basename='merchantproduct')
router.register(r'student-products', StudentProductViewSet, basename='studentproduct')
router.register(r'tutor-services', TutorServiceViewSet, basename='tutorservice')
router.register(r'reviews', ReviewViewSet, basename='review')
router.register(r'categories', CategoryViewSet, basename='category')

urlpatterns = router.urls
