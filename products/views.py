from django.shortcuts import render
from rest_framework import viewsets, permissions
from .models import MerchantProduct, StudentProduct, TutorService, Review, Category
from .serializers import (
    MerchantProductSerializer,
    StudentProductSerializer,
    TutorServiceSerializer,
    ReviewSerializer,
    CategorySerializer,
)

class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user

class MerchantProductViewSet(viewsets.ModelViewSet):
    serializer_class = MerchantProductSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False) or not self.request.user.is_authenticated:
            return MerchantProduct.objects.none()
        return MerchantProduct.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class StudentProductViewSet(viewsets.ModelViewSet):
    serializer_class = StudentProductSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False) or not self.request.user.is_authenticated:
            return StudentProduct.objects.none()
        return StudentProduct.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class TutorServiceViewSet(viewsets.ModelViewSet):
    serializer_class = TutorServiceSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False) or not self.request.user.is_authenticated:
            return TutorService.objects.none()
        return TutorService.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False) or not self.request.user.is_authenticated:
            return Review.objects.none()
        return Review.objects.filter(reviewer=self.request.user)

    def perform_create(self, serializer):
        serializer.save(reviewer=self.request.user)

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]
