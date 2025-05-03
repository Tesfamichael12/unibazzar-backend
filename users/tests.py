from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from .models import University
import json

User = get_user_model()

class AuthenticationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('register')
        self.login_url = reverse('token_obtain_pair')
        
        # Create a university
        self.university = University.objects.create(name="Addis Ababa University")
        
        # Create a verified user
        self.verified_user = User.objects.create_user(
            email='verified@example.com',
            username='verified@example.com',
            password='Test@123',
            full_name='Verified User',
            role='student',
            university=self.university,
            is_email_verified=True
        )
        
        # Create an unverified user
        self.unverified_user = User.objects.create_user(
            email='unverified@example.com',
            username='unverified@example.com',
            password='Test@123',
            full_name='Unverified User',
            role='student',
            university=self.university,
            is_email_verified=False
        )
    
    def test_user_registration(self):
        """Test user registration"""
        data = {
            'full_name': 'Test User',
            'email': 'test@example.com',
            'password': 'Test@123',
            'confirm_password': 'Test@123',
            'role': 'student',
            'university': self.university.id
        }
        
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 3)  # 2 from setUp + 1 new
        
        # Check that the user is created but not verified
        user = User.objects.get(email='test@example.com')
        self.assertFalse(user.is_email_verified)
    
    def test_login_verified_user(self):
        """Test login with verified user"""
        data = {
            'email': 'verified@example.com',
            'password': 'Test@123'
        }
        
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
    
    def test_login_unverified_user(self):
        """Test login with unverified user"""
        data = {
            'email': 'unverified@example.com',
            'password': 'Test@123'
        }
        
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('Email not verified', response.data['message'])

class UserProfileTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.profile_url = reverse('user_profile')
        
        # Create a university
        self.university = University.objects.create(name="Addis Ababa University")
        
        # Create a test user
        self.user = User.objects.create_user(
            email='test@example.com',
            username='test@example.com',
            password='Test@123',
            full_name='Test User',
            role='student',
            university=self.university,
            is_email_verified=True
        )
        
        # Authenticate the client
        self.client.force_authenticate(user=self.user)
    
    def test_get_profile(self):
        """Test retrieving user profile"""
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.user.email)
        self.assertEqual(response.data['full_name'], self.user.full_name)
    
    def test_update_profile(self):
        """Test updating user profile"""
        data = {
            'full_name': 'Updated Name',
            'role': 'merchant',
            'bio': 'This is my bio'
        }
        
        response = self.client.patch(self.profile_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Refresh user from database
        self.user.refresh_from_db()
        self.assertEqual(self.user.full_name, 'Updated Name')
        self.assertEqual(self.user.role, 'merchant')
        self.assertEqual(self.user.bio, 'This is my bio')
    
    def test_update_phone_number(self):
        """Test updating phone number"""
        url = reverse('update_phone')
        data = {
            'phone_number': '+251912345678'
        }
        
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Refresh user from database
        self.user.refresh_from_db()
        self.assertEqual(self.user.phone_number, '+251912345678')
    
    def test_change_password(self):
        """Test changing password"""
        url = reverse('change_password')
        data = {
            'current_password': 'Test@123',
            'new_password': 'NewTest@123',
            'confirm_new_password': 'NewTest@123'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify the password was changed
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('NewTest@123'))

class UniversityListTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('university-list') # Assuming you have a URL named 'university-list'
        University.objects.create(name="Test University 1")
        University.objects.create(name="Test University 2")

    def test_list_universities(self):
        """Test retrieving the list of universities"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2) # Assuming pagination is enabled
        self.assertEqual(response.data['results'][0]['name'], "Test University 1")
        self.assertEqual(response.data['results'][1]['name'], "Test University 2")