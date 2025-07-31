"""
Tests for Profile model.

This module contains tests for the Profile model including
relationships with User, model methods, and profile-specific functionality.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError
from apps.accounts.models import Profile
from .test_core import BaseTestCase

User = get_user_model()


class ProfileModelTestCase(BaseTestCase):
    """Tests for the Profile model."""
    
    def setUp(self):
        """Set up test data."""
        super().setUp()
        self.user = self.create_user()
    
    def test_profile_creation(self):
        """Test basic profile creation."""
        profile = Profile.objects.create(user=self.user)
        self.assertIsInstance(profile, Profile)
        self.assertEqual(profile.user, self.user)
        # display_name is set from user's first_name by default
        self.assertEqual(profile.display_name, self.user.first_name)
        self.assertEqual(profile.bio, '')
        # Avatar field returns ImageFieldFile object even when None
        self.assertFalse(profile.avatar)
    
    def test_profile_creation_with_data(self):
        """Test profile creation with complete data."""
        profile = Profile.objects.create(
            user=self.user,
            display_name='Test Display Name',
            bio='This is a test bio.'
        )
        self.assertEqual(profile.display_name, 'Test Display Name')
        self.assertEqual(profile.bio, 'This is a test bio.')
    
    def test_profile_string_representation(self):
        """Test profile __str__ method."""
        profile = Profile.objects.create(user=self.user)
        expected_str = f"{self.user.email}'s profile"
        self.assertEqual(str(profile), expected_str)
    
    def test_one_to_one_relationship_with_user(self):
        """Test one-to-one relationship with User model."""
        profile = Profile.objects.create(user=self.user)
        
        # Test forward relationship
        self.assertEqual(profile.user, self.user)
        
        # Test reverse relationship
        self.assertEqual(self.user.profile, profile)
    
    def test_profile_uniqueness_per_user(self):
        """Test that each user can have only one profile."""
        Profile.objects.create(user=self.user)
        
        # Attempting to create another profile for the same user should fail
        with self.assertRaises(IntegrityError):
            Profile.objects.create(user=self.user)
    
    def test_profile_cascade_delete(self):
        """Test that profile is deleted when user is deleted."""
        profile = Profile.objects.create(user=self.user)
        profile_id = profile.id
        
        # Delete the user
        self.user.delete()
        
        # Profile should also be deleted
        with self.assertRaises(Profile.DoesNotExist):
            Profile.objects.get(id=profile_id)
    
    def test_profile_model_meta_options(self):
        """Test model meta options."""
        self.assertEqual(Profile._meta.db_table, 'accounts_profile')
        self.assertEqual(Profile._meta.verbose_name, 'Profile')
        self.assertEqual(Profile._meta.verbose_name_plural, 'Profiles')
    
    def test_profile_save_with_default_display_name(self):
        """Test that save() method sets default display_name from user's first_name."""
        # Create user with first_name
        user_with_name = self.create_user(
            email='named@example.com',
            first_name='John'
        )
        
        # Create profile without display_name
        profile = Profile(user=user_with_name)
        profile.save()
        
        # display_name should be set to user's first_name
        self.assertEqual(profile.display_name, 'John')
    
    def test_profile_save_without_default_display_name(self):
        """Test save() method when user has no first_name."""
        # Create user without first_name
        user_no_name = self.create_user(
            email='noname@example.com',
            first_name=''
        )
        
        # Create profile without display_name
        profile = Profile(user=user_no_name)
        profile.save()
        
        # display_name should remain empty
        self.assertEqual(profile.display_name, '')
    
    def test_profile_save_preserves_existing_display_name(self):
        """Test that save() method doesn't overwrite existing display_name."""
        # Create user with first_name
        user_with_name = self.create_user(
            email='named@example.com',
            first_name='John'
        )
        
        # Create profile with custom display_name
        profile = Profile(user=user_with_name, display_name='Custom Name')
        profile.save()
        
        # display_name should not be overwritten
        self.assertEqual(profile.display_name, 'Custom Name')
    
    def test_profile_with_avatar(self):
        """Test profile with avatar image."""
        # Create a simple test image file
        test_image = SimpleUploadedFile(
            name='test_avatar.jpg',
            content=b'fake_image_content',
            content_type='image/jpeg'
        )
        
        profile = Profile.objects.create(
            user=self.user,
            avatar=test_image
        )
        
        self.assertTrue(profile.avatar)
        self.assertIn('avatars/', profile.avatar.name)
    
    def test_profile_fields_blank_allowed(self):
        """Test that display_name and bio can be blank."""
        # Create user without first_name to test empty display_name
        user_no_name = self.create_user(
            email='noname@example.com',
            first_name=''
        )
        profile = Profile.objects.create(
            user=user_no_name,
            display_name='',
            bio=''
        )
        
        # Should not raise validation errors
        profile.full_clean()
        self.assertEqual(profile.display_name, '')
        self.assertEqual(profile.bio, '')
    
    def test_profile_avatar_null_allowed(self):
        """Test that avatar can be null."""
        profile = Profile.objects.create(
            user=self.user,
            avatar=None
        )
        
        # Should not raise validation errors
        profile.full_clean()
        # ImageField returns ImageFieldFile object, check if it's falsy
        self.assertFalse(profile.avatar)
    
    def test_profile_display_name_max_length(self):
        """Test display_name max length validation."""
        long_name = 'x' * 61  # 61 characters, exceeds max_length of 60
        
        profile = Profile(
            user=self.user,
            display_name=long_name
        )
        
        with self.assertRaises(Exception):  # ValidationError on full_clean()
            profile.full_clean()
    
    def test_profile_bio_text_field(self):
        """Test that bio can store long text."""
        long_bio = 'This is a very long bio. ' * 100  # Very long text
        
        profile = Profile.objects.create(
            user=self.user,
            bio=long_bio
        )
        
        self.assertEqual(profile.bio, long_bio)
        # Should not raise validation errors
        profile.full_clean()
    
    def test_multiple_profiles_different_users(self):
        """Test that multiple profiles can exist for different users."""
        user2 = self.create_user(email='user2@example.com')
        user3 = self.create_user(email='user3@example.com')
        
        profile1 = Profile.objects.create(user=self.user)
        profile2 = Profile.objects.create(user=user2)
        profile3 = Profile.objects.create(user=user3)
        
        self.assertEqual(Profile.objects.count(), 3)
        self.assertNotEqual(profile1.user, profile2.user)
        self.assertNotEqual(profile2.user, profile3.user)