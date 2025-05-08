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
    permission_classes = []  # Allow any user (authenticated or not)

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsOwnerOrReadOnly()]
        return []

    def get_queryset(self):
        return MerchantProduct.objects.all().order_by('id')

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class StudentProductViewSet(viewsets.ModelViewSet):
    serializer_class = StudentProductSerializer
    permission_classes = []

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsOwnerOrReadOnly()]
        return []

    def get_queryset(self):
        queryset = StudentProduct.objects.all().order_by('id')
        category_id = self.request.query_params.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        queryset = queryset.filter(id__gte=231)
        return queryset

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class TutorServiceViewSet(viewsets.ModelViewSet):
    serializer_class = TutorServiceSerializer
    permission_classes = []

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsOwnerOrReadOnly()]
        return []

    def get_queryset(self):
        queryset = TutorService.objects.all().order_by('id')
        category_id = self.request.query_params.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        queryset = queryset.filter(id__gte=210)
        return queryset

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
    queryset = Category.objects.all().order_by('id')
    serializer_class = CategorySerializer
    permission_classes = []  # Allow any user (authenticated or not)

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated()]
        return []
