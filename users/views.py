from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.contrib.auth import authenticate
from django.db import transaction
import requests as http_requests
import json
import os
from django.http import HttpResponseRedirect
from django.template.loader import render_to_string
from django.http import HttpResponse
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.shortcuts import render, redirect
from django.views import View
from django.http import JsonResponse
from django.urls import get_resolver
from rest_framework.pagination import PageNumberPagination

from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer,
    UserProfileSerializer, UserProfileUpdateSerializer, ProfilePictureSerializer,
    EmailChangeSerializer, PhoneNumberUpdateSerializer, PasswordChangeSerializer,
    ResendVerificationEmailSerializer, UniversitySerializer
)
from .tokens import email_verification_token
from .utils import send_verification_email
from .models import University, User

User = get_user_model()

class UserRegistrationView(generics.CreateAPIView):
    """
    API endpoint for user registration.
    Creates a new user account and sends a verification email.
    """
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    @swagger_auto_schema(
        operation_summary="Register User",
        operation_description="Register a new user account and send a verification email.",
        request_body=UserRegistrationSerializer,
        responses={
            201: openapi.Response(
                description="User registered successfully",
                examples={
                    "application/json": {
                        "status": "success",
                        "message": "User registered successfully.",
                        "user_id": 1,
                        "email": "user@example.com",
                        "email_verification": "Verification email sent. Please check your inbox."
                    }
                }
            ),
            400: openapi.Response(
                description="Invalid input data",
                examples={
                    "application/json": {
                        "email": ["Enter a valid email address."],
                        "password": ["This field may not be blank."]
                    }
                }
            ),
            500: openapi.Response(
                description="Server error",
                examples={
                    "application/json": {
                        "status": "error",
                        "message": "An error occurred during registration. Please try again."
                    }
                }
            )
        }
    )
    def post(self, request, *args, **kwargs):
        try:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                try:
                    with transaction.atomic():
                        user = serializer.save()
                    # Send verification email outside transaction
                    success, error_message = send_verification_email(user, request)
                    response_data = {
                        'status': 'success',
                        'message': 'User registered successfully.',
                        'user_id': user.id,
                        'email': user.email
                    }
                    if success:
                        response_data['email_verification'] = 'Verification email sent. Please check your inbox.'
                    else:
                        response_data['email_verification'] = f'Failed to send verification email: {error_message}'
                    return Response(response_data, status=status.HTTP_201_CREATED)
                except Exception as e:
                    return Response({
                        'status': 'error',
                        'message': f'An error occurred during registration: {str(e)}'
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': f'An unexpected error occurred: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class EmailVerificationView(APIView):
    """
    API endpoint to verify a user's email address.
    Handles the verification link sent to the user's email.
    """
    permission_classes = [permissions.AllowAny]
    
    @swagger_auto_schema(
        operation_summary="Verify Email",
        operation_description="Verify user's email address using the link sent to their inbox.",
        manual_parameters=[
            openapi.Parameter(
                name='uidb64',
                in_=openapi.IN_PATH,
                description='Base64 encoded user ID',
                type=openapi.TYPE_STRING,
                required=True
            ),
            openapi.Parameter(
                name='token',
                in_=openapi.IN_PATH,
                description='Verification token',
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={
            200: openapi.Response(
                description="Email verified successfully. Renders an HTML page.",
                schema=openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_BINARY)
            ),
            400: openapi.Response(
                description="Invalid or expired verification link. Renders an HTML page.",
                schema=openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_BINARY)
            )
        }
    )
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        
        if user is not None and email_verification_token.check_token(user, token):
            user.is_email_verified = True
            user.save()
            
            # Get the frontend login URL for the button
            frontend_url = os.environ.get('FRONTEND_URL', 'http://localhost:3000')
            login_url = f"{frontend_url}/login"
            
            # Render the success HTML template
            html_content = render_to_string('users/email_verification_success.html', {
                'login_url': login_url,
                'site_name': 'UniBazzar',
            })
            
            return HttpResponse(html_content)
        
        # If verification failed, render the failure template
        frontend_url = os.environ.get('FRONTEND_URL', 'http://localhost:3000')
        login_url = f"{frontend_url}/login"
        resend_url = f"{frontend_url}/resend-verification"
        
        html_content = render_to_string('users/email_verification_failed.html', {
            'login_url': login_url,
            'resend_url': resend_url,
            'site_name': 'UniBazzar',
        })
        
        return HttpResponse(html_content)

class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom token view that checks if user's email is verified before issuing tokens
    """
    @swagger_auto_schema(
        operation_summary="Login (Email/Password)",
        operation_description="Login with email and password. Returns JWT access and refresh tokens.",
        request_body=UserLoginSerializer,
        responses={
            200: openapi.Response(
                description="Login successful",
                examples={
                    "application/json": {
                        "status": "success",
                        "refresh": "refresh_token_here",
                        "access": "access_token_here"
                    }
                }
            ),
            401: openapi.Response(
                description="Invalid credentials or email not verified",
                examples={
                    "application/json": {
                        "status": "error",
                        "message": "Invalid email or password."
                    }
                }
            ),
             400: openapi.Response(
                description="Invalid input",
                examples={
                    "application/json": {
                        "email": ["This field is required."],
                        "password": ["This field is required."]
                    }
                }
            )
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        
        user = authenticate(request, email=email, password=password)
        
        if user is None:
            return Response({
                'status': 'error',
                'message': 'Invalid email or password.'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        if not user.is_email_verified:
            return Response({
                'status': 'error',
                'message': 'Email not verified. Please verify your email to login.'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'status': 'success',
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_200_OK)

class LogoutView(APIView):
    """
    API endpoint to log out a user by blacklisting their refresh token
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(
        operation_summary="Logout",
        operation_description="Log out a user by blacklisting their refresh token. Requires authentication.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['refresh'],
            properties={
                'refresh': openapi.Schema(type=openapi.TYPE_STRING, description='Refresh token')
            }
        ),
        responses={
            200: openapi.Response(
                description="Logged out successfully",
                examples={
                    "application/json": {
                        "status": "success",
                        "message": "Logged out successfully"
                    }
                }
            ),
            400: openapi.Response(
                description="Invalid token or other error",
                 examples={
                    "application/json": {
                        "status": "error",
                        "message": "Token is invalid or expired"
                    }
                }
            )
        }
    )
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            token = RefreshToken(refresh_token)
            token.blacklist()
            
            return Response({
                'status': 'success',
                'message': 'Logged out successfully'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

class ResendVerificationEmailView(APIView):
    """
    API endpoint to resend the verification email
    """
    permission_classes = [permissions.AllowAny]
    
    @swagger_auto_schema(
        operation_summary="Resend Verification Email",
        operation_description="Resend the verification email to a user's email address.",
        request_body=ResendVerificationEmailSerializer,
        responses={
            200: openapi.Response(
                description="Verification email sent successfully",
                 examples={
                    "application/json": {
                        "status": "success",
                        "message": "Verification email sent successfully."
                    }
                }
            ),
            400: openapi.Response(
                description="Invalid request (e.g., missing email, email already verified)",
                examples={
                    "application/json": {
                        "status": "error",
                        "message": "Email is required."
                    }
                }
            ),
            404: openapi.Response(
                description="User not found",
                 examples={
                    "application/json": {
                        "status": "error",
                        "message": "User with this email does not exist."
                    }
                }
            )
        }
    )
    def post(self, request):
        serializer = ResendVerificationEmailSerializer(data=request.data)
        if not serializer.is_valid():
             return Response({
                'status': 'error',
                'message': serializer.errors.get('email', ['Invalid request.'])[0]
            }, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data['email']
        
        try:
            user = User.objects.get(email=email)
            
            if user.is_email_verified:
                return Response({
                    'status': 'error',
                    'message': 'Email is already verified.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            success, error_message = send_verification_email(user, request)

            if success:
                return Response({
                    'status': 'success',
                    'message': 'Verification email sent successfully.'
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'status': 'error',
                    'message': f'Failed to send verification email: {error_message}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except User.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'User with this email does not exist.'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': f'An unexpected error occurred: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# --- University List View --- #

class UniversityListView(generics.ListAPIView):
    """
    API endpoint to list all universities.
    Uses pagination.
    """
    queryset = University.objects.all()
    serializer_class = UniversitySerializer
    permission_classes = [permissions.AllowAny] # Allow anyone to view universities
    pagination_class = PageNumberPagination # Use standard pagination

    @swagger_auto_schema(
        operation_summary="List Universities",
        operation_description="Retrieve a paginated list of all universities.",
        responses={
            200: UniversitySerializer(many=True),
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

# --- Password Reset Confirmation Page --- #

class PasswordResetConfirmPageView(View):
    template_name = 'users/password_reset_confirm_form.html'

    def get(self, request, *args, **kwargs):
        token = request.GET.get('token')
        if not token:
            # Handle error: Token is missing
            # You might want to redirect to an error page or show a message
            return render(request, self.template_name, {'error': 'Invalid reset link: Token missing.'})
            
        # You could optionally validate the token here using 
        # django_rest_passwordreset logic if needed before rendering,
        # but the main validation happens on the POST API call.
        
        context = {'token': token}
        return render(request, self.template_name, context)