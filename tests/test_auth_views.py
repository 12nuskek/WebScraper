"""
Tests for Account views.

This module contains tests for all account-related views including
authentication, registration, profile management, and permissions.
"""

import json
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from apps.auth.models import Profile
from .test_core import BaseTestCase

User = get_user_model()


class RegisterViewTestCase(APITestCase, BaseTestCase):
    """Tests for the RegisterView."""
    
    def setUp(self):
        """Set up test data."""
        super().setUp()
        self.register_url = '/auth/register/'
        self.valid_registration_data = {
            'email': 'newuser@example.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
            'first_name': 'New',
            'last_name': 'User'
        }
    
    def test_successful_registration(self):
        """Test successful user registration."""
        response = self.client.post(
            self.register_url,
            self.valid_registration_data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('message', response.data)
        self.assertIn('user', response.data)
        
        # Check that user was created
        user = User.objects.get(email='newuser@example.com')
        self.assertEqual(user.first_name, 'New')
        self.assertEqual(user.last_name, 'User')
        
        # Check that profile was created
        self.assertTrue(hasattr(user, 'profile'))
    
    def test_registration_with_mismatched_passwords(self):
        """Test registration with mismatched passwords."""
        data = self.valid_registration_data.copy()
        data['password_confirm'] = 'differentpassword'
        
        response = self.client.post(self.register_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)
    
    def test_registration_with_invalid_email(self):
        """Test registration with invalid email."""
        data = self.valid_registration_data.copy()
        data['email'] = 'invalid-email'
        
        response = self.client.post(self.register_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
    
    def test_registration_with_existing_email(self):
        """Test registration with already existing email."""
        # Create a user first
        self.create_user()
        
        data = self.valid_registration_data.copy()
        data['email'] = self.test_email  # Use existing email
        
        response = self.client.post(self.register_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
    
    def test_registration_with_weak_password(self):
        """Test registration with weak password."""
        data = self.valid_registration_data.copy()
        data['password'] = '123'
        data['password_confirm'] = '123'
        
        response = self.client.post(self.register_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)
    
    def test_registration_without_required_fields(self):
        """Test registration without required fields."""
        response = self.client.post(self.register_url, {}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
        self.assertIn('password', response.data)


class CustomTokenObtainPairViewTestCase(APITestCase, BaseTestCase):
    """Tests for the CustomTokenObtainPairView (login)."""
    
    def setUp(self):
        """Set up test data."""
        super().setUp()
        self.login_url = '/auth/login/'
        self.user = self.create_user()
    
    def test_successful_login(self):
        """Test successful user login."""
        response = self.client.post(
            self.login_url,
            {
                'email': self.test_email,
                'password': self.test_password
            },
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)
        
        # Check user data in response
        user_data = response.data['user']
        self.assertEqual(user_data['email'], self.test_email)
        self.assertEqual(user_data['id'], self.user.id)
    
    def test_login_with_invalid_credentials(self):
        """Test login with invalid credentials."""
        response = self.client.post(
            self.login_url,
            {
                'email': self.test_email,
                'password': 'wrongpassword'
            },
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotIn('access', response.data)
        self.assertNotIn('user', response.data)
    
    def test_login_with_nonexistent_user(self):
        """Test login with non-existent user."""
        response = self.client.post(
            self.login_url,
            {
                'email': 'nonexistent@example.com',
                'password': self.test_password
            },
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_login_with_missing_fields(self):
        """Test login with missing fields."""
        response = self.client.post(self.login_url, {}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LogoutViewTestCase(APITestCase, BaseTestCase):
    """Tests for the logout_view."""
    
    def setUp(self):
        """Set up test data."""
        super().setUp()
        self.logout_url = '/auth/logout/'
        self.user = self.create_user()
        self.refresh_token = RefreshToken.for_user(self.user)
        self.access_token = self.refresh_token.access_token
    
    def test_successful_logout(self):
        """Test successful logout."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        response = self.client.post(
            self.logout_url,
            {'refresh': str(self.refresh_token)},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
    
    def test_logout_without_authentication(self):
        """Test logout without authentication."""
        response = self.client.post(
            self.logout_url,
            {'refresh': str(self.refresh_token)},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_logout_without_refresh_token(self):
        """Test logout without refresh token."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        response = self.client.post(self.logout_url, {}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_logout_with_invalid_refresh_token(self):
        """Test logout with invalid refresh token."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        response = self.client.post(
            self.logout_url,
            {'refresh': 'invalid-token'},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)


class ProfileViewSetTestCase(APITestCase, BaseTestCase):
    """Tests for the ProfileViewSet."""
    
    def setUp(self):
        """Set up test data."""
        super().setUp()
        self.profile_url = '/profiles/me/'
        self.user = self.create_user()
        self.profile = Profile.objects.create(
            user=self.user,
            display_name='Test Display',
            bio='Test bio'
        )
        
        # Create token and authenticate
        self.refresh_token = RefreshToken.for_user(self.user)
        self.access_token = self.refresh_token.access_token
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
    
    def test_get_profile(self):
        """Test retrieving user profile."""
        response = self.client.get(self.profile_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['display_name'], 'Test Display')
        self.assertEqual(response.data['bio'], 'Test bio')
        self.assertEqual(response.data['user']['email'], self.user.email)
    
    def test_get_profile_creates_if_not_exists(self):
        """Test that GET creates profile if it doesn't exist."""
        # Delete the existing profile
        self.profile.delete()
        
        response = self.client.get(self.profile_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Profile should be created automatically
        self.assertTrue(Profile.objects.filter(user=self.user).exists())
    
    def test_update_profile(self):
        """Test updating user profile."""
        update_data = {
            'display_name': 'Updated Display Name',
            'bio': 'Updated bio'
        }
        
        response = self.client.put(
            self.profile_url,
            update_data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['display_name'], 'Updated Display Name')
        self.assertEqual(response.data['bio'], 'Updated bio')
        
        # Verify in database
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.display_name, 'Updated Display Name')
        self.assertEqual(self.profile.bio, 'Updated bio')
    
    def test_partial_update_profile(self):
        """Test partial update of user profile."""
        response = self.client.patch(
            self.profile_url,
            {'display_name': 'Partially Updated'},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['display_name'], 'Partially Updated')
        self.assertEqual(response.data['bio'], 'Test bio')  # Should remain unchanged
    
    def test_profile_access_without_authentication(self):
        """Test accessing profile without authentication."""
        self.client.credentials()  # Remove authentication
        
        response = self.client.get(self.profile_url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_profile_isolation_between_users(self):
        """Test that users can only access their own profiles."""
        # Create another user and their profile
        user2 = self.create_user(email='user2@example.com')
        profile2 = Profile.objects.create(
            user=user2,
            display_name='User2 Display'
        )
        
        # user1 should only see their own profile
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['display_name'], 'Test Display')
        self.assertNotEqual(response.data['display_name'], 'User2 Display')


class ProfileViewSetPermissionsTestCase(APITestCase, BaseTestCase):
    """Tests for ProfileViewSet permissions and edge cases."""
    
    def setUp(self):
        """Set up test data."""
        super().setUp()
        self.profile_url = '/profiles/me/'
        self.user = self.create_user()
        
    def test_queryset_filtering(self):
        """Test that queryset only returns current user's profile."""
        # Create multiple users with profiles
        user2 = self.create_user(email='user2@example.com')
        Profile.objects.create(user=self.user, display_name='User1')
        Profile.objects.create(user=user2, display_name='User2')
        
        # Authenticate as user1
        refresh_token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh_token.access_token}')
        
        response = self.client.get(self.profile_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['display_name'], 'User1')
    
    def test_get_object_creates_profile(self):
        """Test that get_object creates profile if it doesn't exist."""
        # Don't create a profile initially
        refresh_token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh_token.access_token}')
        
        # Profile shouldn't exist yet
        self.assertFalse(Profile.objects.filter(user=self.user).exists())
        
        response = self.client.get(self.profile_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Profile should now exist
        self.assertTrue(Profile.objects.filter(user=self.user).exists())