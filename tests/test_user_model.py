"""
Tests for User model and UserManager.

This module contains tests for the custom User model and UserManager
including authentication, user creation, and model methods.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils import timezone
from .test_core import BaseTestCase

User = get_user_model()


class UserManagerTestCase(BaseTestCase):
    """Tests for the custom UserManager."""
    
    def test_create_user(self):
        """Test creating a regular user."""
        user = User.objects.create_user(
            email='user@example.com',
            password='testpass123'
        )
        self.assertEqual(user.email, 'user@example.com')
        self.assertTrue(user.check_password('testpass123'))
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
    
    def test_create_user_with_extra_fields(self):
        """Test creating a user with extra fields."""
        user = User.objects.create_user(
            email='user@example.com',
            password='testpass123',
            first_name='John',
            last_name='Doe'
        )
        self.assertEqual(user.first_name, 'John')
        self.assertEqual(user.last_name, 'Doe')
    
    def test_create_user_without_email(self):
        """Test that creating a user without email raises ValueError."""
        with self.assertRaises(ValueError) as context:
            User.objects.create_user(email='', password='testpass123')
        
        self.assertEqual(str(context.exception), 'The Email field must be set')
    
    def test_create_user_normalizes_email(self):
        """Test that email is normalized when creating a user."""
        user = User.objects.create_user(
            email='User@EXAMPLE.COM',
            password='testpass123'
        )
        self.assertEqual(user.email, 'User@example.com')
    
    def test_create_superuser(self):
        """Test creating a superuser."""
        superuser = User.objects.create_superuser(
            email='admin@example.com',
            password='adminpass123'
        )
        self.assertEqual(superuser.email, 'admin@example.com')
        self.assertTrue(superuser.check_password('adminpass123'))
        self.assertTrue(superuser.is_active)
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)
    
    def test_create_superuser_without_is_staff(self):
        """Test that creating a superuser with is_staff=False raises ValueError."""
        with self.assertRaises(ValueError) as context:
            User.objects.create_superuser(
                email='admin@example.com',
                password='adminpass123',
                is_staff=False
            )
        
        self.assertEqual(str(context.exception), 'Superuser must have is_staff=True.')
    
    def test_create_superuser_without_is_superuser(self):
        """Test that creating a superuser with is_superuser=False raises ValueError."""
        with self.assertRaises(ValueError) as context:
            User.objects.create_superuser(
                email='admin@example.com',
                password='adminpass123',
                is_superuser=False
            )
        
        self.assertEqual(str(context.exception), 'Superuser must have is_superuser=True.')


class UserModelTestCase(BaseTestCase):
    """Tests for the User model."""
    
    def test_user_creation(self):
        """Test basic user creation."""
        user = self.create_user()
        self.assertIsInstance(user, User)
        self.assertEqual(user.email, self.test_email)
        self.assertTrue(user.is_active)
    
    def test_user_string_representation(self):
        """Test user __str__ method."""
        user = self.create_user()
        self.assertEqual(str(user), user.email)
    
    def test_email_uniqueness(self):
        """Test that email field is unique."""
        self.create_user()
        with self.assertRaises(IntegrityError):
            self.create_user()  # Same email
    
    def test_get_full_name(self):
        """Test get_full_name method."""
        user = self.create_user(first_name='John', last_name='Doe')
        self.assertEqual(user.get_full_name(), 'John Doe')
    
    def test_get_full_name_with_empty_names(self):
        """Test get_full_name with empty first or last name."""
        user = self.create_user(first_name='John', last_name='')
        self.assertEqual(user.get_full_name(), 'John')
        
        user = self.create_user(email='test2@example.com', first_name='', last_name='Doe')
        self.assertEqual(user.get_full_name(), 'Doe')
        
        user = self.create_user(email='test3@example.com', first_name='', last_name='')
        self.assertEqual(user.get_full_name(), '')
    
    def test_get_short_name(self):
        """Test get_short_name method."""
        user = self.create_user(first_name='John')
        self.assertEqual(user.get_short_name(), 'John')
    
    def test_date_joined_auto_set(self):
        """Test that date_joined is automatically set."""
        before_creation = timezone.now()
        user = self.create_user()
        after_creation = timezone.now()
        
        self.assertGreaterEqual(user.date_joined, before_creation)
        self.assertLessEqual(user.date_joined, after_creation)
    
    def test_username_field(self):
        """Test that USERNAME_FIELD is set to email."""
        self.assertEqual(User.USERNAME_FIELD, 'email')
    
    def test_required_fields(self):
        """Test that REQUIRED_FIELDS is empty."""
        self.assertEqual(User.REQUIRED_FIELDS, [])
    
    def test_user_permissions(self):
        """Test user permissions functionality."""
        user = self.create_user()
        
        # Test that user can have permissions (from PermissionsMixin)
        self.assertFalse(user.is_superuser)
        self.assertEqual(user.get_all_permissions(), set())
        self.assertFalse(user.has_perm('some.permission'))
    
    def test_user_model_meta_options(self):
        """Test model meta options."""
        self.assertEqual(User._meta.db_table, 'accounts_user')
        self.assertEqual(User._meta.verbose_name, 'User')
        self.assertEqual(User._meta.verbose_name_plural, 'Users')
    
    def test_password_hashing(self):
        """Test that passwords are properly hashed."""
        user = self.create_user()
        # Password should be hashed, not stored in plain text
        self.assertNotEqual(user.password, self.test_password)
        self.assertTrue(user.check_password(self.test_password))
        self.assertFalse(user.check_password('wrongpassword'))
    
    def test_user_inactive(self):
        """Test inactive user."""
        user = self.create_user(is_active=False)
        self.assertFalse(user.is_active)
    
    def test_user_staff_status(self):
        """Test user staff status."""
        user = self.create_user(is_staff=True)
        self.assertTrue(user.is_staff)
        self.assertFalse(user.is_superuser)  # Staff doesn't mean superuser