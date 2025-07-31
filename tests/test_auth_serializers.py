"""
Tests for Account serializers.

This module contains tests for all account-related serializers including
UserRegistrationSerializer, UserSerializer, and ProfileSerializer.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from rest_framework import serializers
from apps.auth.models import Profile
from apps.auth.serializers import (
    UserRegistrationSerializer,
    UserSerializer,
    ProfileSerializer
)
from .test_core import BaseTestCase

User = get_user_model()


class UserRegistrationSerializerTestCase(BaseTestCase):
    """Tests for the UserRegistrationSerializer."""
    
    def setUp(self):
        """Set up test data."""
        super().setUp()
        self.valid_data = {
            'email': 'newuser@example.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
            'first_name': 'New',
            'last_name': 'User'
        }
    
    def test_valid_serializer(self):
        """Test serializer with valid data."""
        serializer = UserRegistrationSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())
    
    def test_serializer_create_user(self):
        """Test that serializer creates user correctly."""
        serializer = UserRegistrationSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())
        
        user = serializer.save()
        
        self.assertIsInstance(user, User)
        self.assertEqual(user.email, 'newuser@example.com')
        self.assertEqual(user.first_name, 'New')
        self.assertEqual(user.last_name, 'User')
        self.assertTrue(user.check_password('testpass123'))
    
    def test_serializer_creates_profile(self):
        """Test that serializer creates associated profile."""
        serializer = UserRegistrationSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())
        
        user = serializer.save()
        
        # Profile should be created automatically
        self.assertTrue(hasattr(user, 'profile'))
        self.assertIsInstance(user.profile, Profile)
    
    def test_password_mismatch_validation(self):
        """Test validation when passwords don't match."""
        data = self.valid_data.copy()
        data['password_confirm'] = 'differentpassword'
        
        serializer = UserRegistrationSerializer(data=data)
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)
        self.assertIn("Passwords don't match", str(serializer.errors))
    
    def test_invalid_email_validation(self):
        """Test validation with invalid email."""
        data = self.valid_data.copy()
        data['email'] = 'invalid-email'
        
        serializer = UserRegistrationSerializer(data=data)
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)
    
    def test_weak_password_validation(self):
        """Test validation with weak password."""
        data = self.valid_data.copy()
        data['password'] = '123'
        data['password_confirm'] = '123'
        
        serializer = UserRegistrationSerializer(data=data)
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('password', serializer.errors)
    
    def test_missing_required_fields(self):
        """Test validation with missing required fields."""
        serializer = UserRegistrationSerializer(data={})
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)
        self.assertIn('password', serializer.errors)
        self.assertIn('password_confirm', serializer.errors)
    
    def test_password_confirm_removed_from_validated_data(self):
        """Test that password_confirm is removed during create."""
        serializer = UserRegistrationSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())
        
        # Mock create to check validated_data
        original_create_user = User.objects.create_user
        validated_data_captured = None
        
        def mock_create_user(**kwargs):
            nonlocal validated_data_captured
            validated_data_captured = kwargs
            return original_create_user(**kwargs)
        
        User.objects.create_user = mock_create_user
        
        try:
            user = serializer.save()
            self.assertNotIn('password_confirm', validated_data_captured)
        finally:
            User.objects.create_user = original_create_user
    
    def test_serializer_fields(self):
        """Test that serializer has correct fields."""
        serializer = UserRegistrationSerializer()
        fields = serializer.fields.keys()
        
        expected_fields = {'email', 'password', 'password_confirm', 'first_name', 'last_name'}
        self.assertEqual(set(fields), expected_fields)
    
    def test_password_write_only(self):
        """Test that password fields are write-only."""
        serializer = UserRegistrationSerializer()
        
        self.assertTrue(serializer.fields['password'].write_only)
        self.assertTrue(serializer.fields['password_confirm'].write_only)


class UserSerializerTestCase(BaseTestCase):
    """Tests for the UserSerializer."""
    
    def setUp(self):
        """Set up test data."""
        super().setUp()
        self.user = self.create_user()
    
    def test_serializer_representation(self):
        """Test serializer representation of user data."""
        serializer = UserSerializer(self.user)
        data = serializer.data
        
        self.assertEqual(data['email'], self.user.email)
        self.assertEqual(data['first_name'], self.user.first_name)
        self.assertEqual(data['last_name'], self.user.last_name)
    
    def test_serializer_fields(self):
        """Test that serializer has correct fields."""
        serializer = UserSerializer()
        fields = serializer.fields.keys()
        
        expected_fields = {'email', 'first_name', 'last_name'}
        self.assertEqual(set(fields), expected_fields)
    
    def test_email_read_only(self):
        """Test that email field is read-only."""
        serializer = UserSerializer()
        
        self.assertIn('email', serializer.fields)
        self.assertTrue(serializer.fields['email'].read_only)
    
    def test_update_user_data(self):
        """Test updating user data through serializer."""
        update_data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'email': 'shouldnotchange@example.com'  # Should be ignored
        }
        
        serializer = UserSerializer(self.user, data=update_data, partial=True)
        self.assertTrue(serializer.is_valid())
        
        updated_user = serializer.save()
        
        self.assertEqual(updated_user.first_name, 'Updated')
        self.assertEqual(updated_user.last_name, 'Name')
        self.assertEqual(updated_user.email, self.user.email)  # Should not change


class ProfileSerializerTestCase(BaseTestCase):
    """Tests for the ProfileSerializer."""
    
    def setUp(self):
        """Set up test data."""
        super().setUp()
        self.user = self.create_user()
        self.profile = Profile.objects.create(
            user=self.user,
            display_name='Test Display',
            bio='Test bio'
        )
    
    def test_serializer_representation(self):
        """Test serializer representation of profile data."""
        serializer = ProfileSerializer(self.profile)
        data = serializer.data
        
        self.assertEqual(data['display_name'], 'Test Display')
        self.assertEqual(data['bio'], 'Test bio')
        self.assertIn('user', data)
        self.assertEqual(data['user']['email'], self.user.email)
    
    def test_serializer_fields(self):
        """Test that serializer has correct fields."""
        serializer = ProfileSerializer()
        fields = serializer.fields.keys()
        
        expected_fields = {'id', 'display_name', 'bio', 'avatar', 'user'}
        self.assertEqual(set(fields), expected_fields)
    
    def test_read_only_fields(self):
        """Test that read-only fields are properly configured."""
        serializer = ProfileSerializer()
        
        self.assertTrue(serializer.fields['id'].read_only)
        self.assertTrue(serializer.fields['user'].read_only)
    
    def test_nested_user_serializer(self):
        """Test that user field uses nested UserSerializer."""
        serializer = ProfileSerializer(self.profile)
        data = serializer.data
        
        user_data = data['user']
        self.assertIn('email', user_data)
        self.assertIn('first_name', user_data)
        self.assertIn('last_name', user_data)
        self.assertEqual(user_data['email'], self.user.email)
    
    def test_update_profile_only(self):
        """Test updating profile fields only."""
        update_data = {
            'display_name': 'Updated Display',
            'bio': 'Updated bio'
        }
        
        serializer = ProfileSerializer(self.profile, data=update_data, partial=True)
        self.assertTrue(serializer.is_valid())
        
        updated_profile = serializer.save()
        
        self.assertEqual(updated_profile.display_name, 'Updated Display')
        self.assertEqual(updated_profile.bio, 'Updated bio')
        self.assertEqual(updated_profile.user, self.user)  # Should remain same
    
    def test_update_with_user_data(self):
        """Test that nested user data is ignored (user field is read-only)."""
        update_data = {
            'display_name': 'Updated Display',
            'user': {
                'first_name': 'Updated First',
                'last_name': 'Updated Last',
                'email': 'shouldnotchange@example.com'  # Should be ignored
            }
        }
        
        serializer = ProfileSerializer(self.profile, data=update_data, partial=True)
        self.assertTrue(serializer.is_valid())
        
        updated_profile = serializer.save()
        
        # Profile should be updated
        self.assertEqual(updated_profile.display_name, 'Updated Display')
        
        # User should NOT be updated (user field is read-only)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, self.test_user_data['first_name'])
        self.assertEqual(self.user.last_name, self.test_user_data['last_name'])
        self.assertEqual(self.user.email, self.test_email)
    
    def test_update_prevents_email_change(self):
        """Test that user field updates are ignored (read-only field)."""
        original_email = self.user.email
        original_first_name = self.user.first_name
        
        update_data = {
            'user': {
                'email': 'newemail@example.com',
                'first_name': 'Updated'
            }
        }
        
        serializer = ProfileSerializer(self.profile, data=update_data, partial=True)
        self.assertTrue(serializer.is_valid())
        
        serializer.save()
        
        # User fields should not change (user field is read-only)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, original_email)
        self.assertEqual(self.user.first_name, original_first_name)
    
    def test_create_profile_validation(self):
        """Test that serializer validates profile creation data."""
        profile_data = {
            'display_name': 'New Profile',
            'bio': 'New bio'
        }
        
        serializer = ProfileSerializer(data=profile_data)
        self.assertTrue(serializer.is_valid())
    
    def test_empty_profile_data_valid(self):
        """Test that empty profile data is valid."""
        profile_data = {
            'display_name': '',
            'bio': ''
        }
        
        serializer = ProfileSerializer(data=profile_data)
        self.assertTrue(serializer.is_valid())
    
    def test_display_name_max_length_validation(self):
        """Test display_name max length validation."""
        profile_data = {
            'display_name': 'x' * 61,  # Exceeds max_length of 60
            'bio': 'Valid bio'
        }
        
        serializer = ProfileSerializer(data=profile_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('display_name', serializer.errors)


class ProfileSerializerUpdateMethodTestCase(BaseTestCase):
    """Tests specifically for ProfileSerializer update method."""
    
    def setUp(self):
        """Set up test data."""
        super().setUp()
        self.user = self.create_user()
        self.profile = Profile.objects.create(
            user=self.user,
            display_name='Original Display',
            bio='Original bio'
        )
    
    def test_update_method_called(self):
        """Test that custom update method is called."""
        update_data = {
            'display_name': 'Updated Display'
        }
        
        serializer = ProfileSerializer(self.profile, data=update_data, partial=True)
        self.assertTrue(serializer.is_valid())
        
        # This should call the custom update method
        updated_profile = serializer.save()
        
        self.assertEqual(updated_profile.display_name, 'Updated Display')
        self.assertEqual(updated_profile.bio, 'Original bio')  # Should remain
    
    def test_update_separates_user_data(self):
        """Test that user data is ignored (user field is read-only)."""
        original_first_name = self.user.first_name
        original_last_name = self.user.last_name
        
        update_data = {
            'display_name': 'New Display',
            'bio': 'New bio',
            'user': {
                'first_name': 'New First',
                'last_name': 'New Last'
            }
        }
        
        serializer = ProfileSerializer(self.profile, data=update_data, partial=True)
        self.assertTrue(serializer.is_valid())
        
        updated_profile = serializer.save()
        
        # Profile fields should be updated
        self.assertEqual(updated_profile.display_name, 'New Display')
        self.assertEqual(updated_profile.bio, 'New bio')
        
        # User fields should NOT be updated (user field is read-only)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, original_first_name)
        self.assertEqual(self.user.last_name, original_last_name)
    
    def test_update_without_user_data(self):
        """Test update when no user data is provided."""
        original_first_name = self.user.first_name
        
        update_data = {
            'display_name': 'Only Profile Update'
        }
        
        serializer = ProfileSerializer(self.profile, data=update_data, partial=True)
        self.assertTrue(serializer.is_valid())
        
        serializer.save()
        
        # Profile should be updated
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.display_name, 'Only Profile Update')
        
        # User should remain unchanged
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, original_first_name)