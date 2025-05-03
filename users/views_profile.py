from rest_framework import status, generics, permissions, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .serializers import (
    UserProfileSerializer, UserProfileUpdateSerializer, ProfilePictureSerializer,
    EmailChangeSerializer, PhoneNumberUpdateSerializer, PasswordChangeSerializer,
    StudentProfileSerializer, MerchantProfileSerializer, TutorProfileSerializer, CampusAdminProfileSerializer
)
from .utils import send_verification_email
from .models import StudentProfile, MerchantProfile, TutorProfile, CampusAdminProfile

User = get_user_model()

class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user

class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    serializer_class_update = UserProfileUpdateSerializer

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return self.serializer_class_update
        return self.serializer_class

    def get_object(self):
        return self.request.user
    
    @swagger_auto_schema(
        operation_summary="Get User Profile",
        operation_description="Retrieve the profile details of the currently authenticated user.",
        responses={
            200: UserProfileSerializer(),
            401: "Unauthorized (User not authenticated)"
        }
    )
    def get(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        operation_summary="Update User Profile (Full)",
        operation_description="Update the entire profile of the currently authenticated user. All fields are required.",
        request_body=UserProfileUpdateSerializer,
        responses={
            200: UserProfileSerializer(),
            400: "Invalid input data",
            401: "Unauthorized"
        }
    )
    def put(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data, partial=False)
        
        if serializer.is_valid():
            serializer.save()
            # Return the full profile after update
            return Response(UserProfileSerializer(user).data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(
        operation_summary="Update User Profile (Partial)",
        operation_description="Partially update the profile of the currently authenticated user. Only include fields to be updated.",
        request_body=UserProfileUpdateSerializer,
        responses={
            200: UserProfileSerializer(),
            400: "Invalid input data",
            401: "Unauthorized"
        }
    )
    def patch(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            # Return the full profile after update
            return Response(UserProfileSerializer(user).data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProfilePictureUploadView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(
        operation_summary="Upload Profile Picture",
        operation_description="Upload or replace the profile picture for the authenticated user. Use multipart/form-data.",
        request_body=ProfilePictureSerializer,
        responses={
            200: openapi.Response(
                description="Profile picture updated successfully",
                examples={
                    "application/json": {
                        "status": "success",
                        "message": "Profile picture updated successfully",
                        "profile_picture": "http://example.com/media/profile_pictures/uuid.jpg"
                    }
                }
            ),
            400: "Invalid input (e.g., no file, invalid file type)",
            401: "Unauthorized"
        },
        manual_parameters=[openapi.Parameter(
            name='profile_picture', 
            in_=openapi.IN_FORM, 
            type=openapi.TYPE_FILE, 
            required=True, 
            description='Profile picture file to upload'
        )]
    )
    def post(self, request):
        serializer = ProfilePictureSerializer(
            request.user, 
            data=request.data,
            partial=True
        )
        
        if serializer.is_valid():
            # Delete old profile picture if exists
            if request.user.profile_picture:
                request.user.profile_picture.delete(save=False)
            
            serializer.save()
            return Response({
                'status': 'success',
                'message': 'Profile picture updated successfully',
                'profile_picture': request.build_absolute_uri(request.user.profile_picture.url) if request.user.profile_picture else None
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(
        operation_summary="Remove Profile Picture",
        operation_description="Remove the profile picture for the authenticated user.",
        responses={
            200: openapi.Response(
                description="Profile picture removed successfully",
                examples={
                    "application/json": {
                        "status": "success",
                        "message": "Profile picture removed successfully"
                    }
                }
            ),
            400: openapi.Response(
                description="No profile picture exists to remove",
                examples={
                    "application/json": {
                        "status": "error",
                        "message": "No profile picture to remove"
                    }
                }
            ),
            401: "Unauthorized"
        }
    )
    def delete(self, request):
        user = request.user
        
        if user.profile_picture:
            user.profile_picture.delete(save=False)
            user.profile_picture = None
            user.save()
            
            return Response({
                'status': 'success',
                'message': 'Profile picture removed successfully'
            })
        
        return Response({
            'status': 'error',
            'message': 'No profile picture to remove'
        }, status=status.HTTP_400_BAD_REQUEST)

class EmailChangeView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(
        operation_summary="Change Email Address",
        operation_description="Initiate the process to change the user's email address. Sends a verification email to the new address.",
        request_body=EmailChangeSerializer,
        responses={
            200: openapi.Response(
                description="Email change initiated. Verification required.",
                examples={
                    "application/json": {
                        "status": "success",
                        "message": "Email updated. Please check your inbox to verify the new email."
                    }
                }
            ),
            400: "Invalid input (e.g., email already in use, invalid format)",
            401: "Unauthorized"
        }
    )
    def patch(self, request):
        serializer = EmailChangeSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            user = request.user
            new_email = serializer.validated_data['email']
            
            # Store the new email temporarily
            user.email = new_email
            user.is_email_verified = False
            user.save()
            
            # Send verification email
            send_verification_email(user, request)
            
            return Response({
                'status': 'success',
                'message': 'Email updated. Please check your inbox to verify the new email.'
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PhoneNumberUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(
        operation_summary="Update Phone Number",
        operation_description="Update the phone number for the authenticated user.",
        request_body=PhoneNumberUpdateSerializer,
        responses={
            200: openapi.Response(
                description="Phone number updated successfully",
                examples={
                    "application/json": {
                        "status": "success",
                        "message": "Phone number updated successfully",
                        "phone_number": "+1234567890"
                    }
                }
            ),
            400: "Invalid input (e.g., invalid phone number format)",
            401: "Unauthorized"
        }
    )
    def patch(self, request):
        serializer = PhoneNumberUpdateSerializer(data=request.data)
        
        if serializer.is_valid():
            user = request.user
            user.phone_number = serializer.validated_data['phone_number']
            user.save()
            
            return Response({
                'status': 'success',
                'message': 'Phone number updated successfully',
                'phone_number': user.phone_number
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PasswordChangeView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(
        operation_summary="Change Password",
        operation_description="Change the password for the authenticated user. Requires the current password.",
        request_body=PasswordChangeSerializer,
        responses={
            200: openapi.Response(
                description="Password changed successfully",
                 examples={
                    "application/json": {
                        "status": "success",
                        "message": "Password changed successfully"
                    }
                }
            ),
            400: "Invalid input (e.g., current password incorrect, new passwords don't match, new password too weak)",
            401: "Unauthorized"
        }
    )
    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            user = request.user
            
            # Check if current password is correct
            if not user.check_password(serializer.validated_data['current_password']):
                return Response({
                    'status': 'error',
                    'message': 'Current password is incorrect'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Set new password
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            
            return Response({
                'status': 'success',
                'message': 'Password changed successfully'
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class StudentProfileViewSet(viewsets.ModelViewSet):
    serializer_class = StudentProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False) or not self.request.user.is_authenticated:
            return StudentProfile.objects.none()
        return StudentProfile.objects.filter(user=self.request.user)
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class MerchantProfileViewSet(viewsets.ModelViewSet):
    serializer_class = MerchantProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False) or not self.request.user.is_authenticated:
            return MerchantProfile.objects.none()
        return MerchantProfile.objects.filter(user=self.request.user)
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class TutorProfileViewSet(viewsets.ModelViewSet):
    serializer_class = TutorProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False) or not self.request.user.is_authenticated:
            return TutorProfile.objects.none()
        return TutorProfile.objects.filter(user=self.request.user)
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class CampusAdminProfileViewSet(viewsets.ModelViewSet):
    serializer_class = CampusAdminProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False) or not self.request.user.is_authenticated:
            return CampusAdminProfile.objects.none()
        return CampusAdminProfile.objects.filter(user=self.request.user)
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)