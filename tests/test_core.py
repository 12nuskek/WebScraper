"""
Core tests for the WebScraper project.

This module contains general application tests, utilities, and base test classes.
"""

import os
import sys
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(project_root, 'scraping-backend'))

User = get_user_model()


class BaseTestCase(TestCase):
    """Base test case with common utilities for all tests."""
    
    def setUp(self):
        """Set up test data used by the test methods."""
        self.test_email = "test@example.com"
        self.test_password = "testpass123"
        self.test_user_data = {
            'email': self.test_email,
            'password': self.test_password,
            'first_name': 'Test',
            'last_name': 'User'
        }
    
    def create_user(self, **kwargs):
        """Helper method to create a test user."""
        data = self.test_user_data.copy()
        data.update(kwargs)
        return User.objects.create_user(**data)
    
    def create_superuser(self, **kwargs):
        """Helper method to create a test superuser."""
        data = self.test_user_data.copy()
        data.update(kwargs)
        if 'email' not in kwargs:
            data['email'] = 'admin@example.com'
        return User.objects.create_superuser(**data)


class CoreApplicationTestCase(BaseTestCase):
    """Tests for core application functionality."""
    
    def test_django_setup(self):
        """Test that Django is properly configured."""
        from django.conf import settings
        self.assertIsInstance(settings.SECRET_KEY, str)
        self.assertIn('apps.core', settings.INSTALLED_APPS)
        self.assertIn('apps.accounts', settings.INSTALLED_APPS)
        self.assertIn('apps.projects', settings.INSTALLED_APPS)
        self.assertIn('apps.scraper', settings.INSTALLED_APPS)
        self.assertIn('apps.jobs', settings.INSTALLED_APPS)
    
    def test_database_connection(self):
        """Test that database connection works."""
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            self.assertEqual(result[0], 1)
    
    def test_user_model_configured(self):
        """Test that custom user model is properly configured."""
        from django.conf import settings
        self.assertEqual(settings.AUTH_USER_MODEL, 'accounts.User')
    
    def test_rest_framework_configured(self):
        """Test that Django REST Framework is properly configured."""
        from django.conf import settings
        self.assertIn('rest_framework', settings.INSTALLED_APPS)
        self.assertIn('rest_framework_simplejwt', settings.INSTALLED_APPS)


class TestUtilitiesTestCase(BaseTestCase):
    """Tests for test utilities and helpers."""
    
    def test_base_test_case_setup(self):
        """Test that base test case is properly set up."""
        self.assertEqual(self.test_email, "test@example.com")
        self.assertEqual(self.test_password, "testpass123")
        self.assertIsInstance(self.test_user_data, dict)
    
    def test_create_user_helper(self):
        """Test the create_user helper method."""
        user = self.create_user()
        self.assertEqual(user.email, self.test_email)
        self.assertTrue(user.check_password(self.test_password))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
    
    def test_create_superuser_helper(self):
        """Test the create_superuser helper method."""
        superuser = self.create_superuser()
        self.assertEqual(superuser.email, 'admin@example.com')
        self.assertTrue(superuser.check_password(self.test_password))
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)
    
    def test_create_user_with_custom_data(self):
        """Test creating a user with custom data."""
        custom_email = "custom@example.com"
        user = self.create_user(email=custom_email, first_name="Custom")
        self.assertEqual(user.email, custom_email)
        self.assertEqual(user.first_name, "Custom")