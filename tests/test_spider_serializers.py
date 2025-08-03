"""
Test cases for Spider serializers.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError

from apps.spider.models import Spider
from apps.spider.serializers import SpiderSerializer, SpiderSettingsSerializer
from apps.projects.models import Project
from .test_core import BaseTestCase

User = get_user_model()


class SpiderSettingsSerializerTest(BaseTestCase):
    """Test cases for SpiderSettingsSerializer."""

    def test_valid_full_settings(self):
        """Test validation of complete settings structure."""
        settings_data = {
            'block_images': True,
            'block_images_and_css': False,
            'tiny_profile': True,
            'profile': 'mobile',
            'user_agent': 'Mozilla/5.0 Custom Bot',
            'window_size': '1920x1080',
            'headless': True,
            'wait_for_complete_page_load': False,
            'reuse_driver': True,
            'max_retry': 5,
            'parallel': 4,
            'cache': True
        }
        
        serializer = SpiderSettingsSerializer(data=settings_data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data, settings_data)

    def test_valid_partial_settings(self):
        """Test validation of partial settings structure."""
        settings_data = {
            'headless': True,
            'max_retry': 3,
            'user_agent': 'Simple Bot'
        }
        
        serializer = SpiderSettingsSerializer(data=settings_data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data, settings_data)

    def test_valid_empty_settings(self):
        """Test validation of empty settings structure."""
        settings_data = {}
        
        serializer = SpiderSettingsSerializer(data=settings_data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data, settings_data)

    def test_invalid_max_retry_negative(self):
        """Test validation fails for negative max_retry."""
        settings_data = {'max_retry': -1}
        
        serializer = SpiderSettingsSerializer(data=settings_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('max_retry', serializer.errors)

    def test_invalid_parallel_zero(self):
        """Test validation fails for zero parallel."""
        settings_data = {'parallel': 0}
        
        serializer = SpiderSettingsSerializer(data=settings_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('parallel', serializer.errors)

    def test_invalid_parallel_negative(self):
        """Test validation fails for negative parallel."""
        settings_data = {'parallel': -1}
        
        serializer = SpiderSettingsSerializer(data=settings_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('parallel', serializer.errors)

    def test_boolean_fields_accept_various_values(self):
        """Test boolean fields accept various truthy/falsy values."""
        boolean_fields = [
            'block_images', 'block_images_and_css', 'tiny_profile',
            'headless', 'wait_for_complete_page_load', 'reuse_driver', 'cache'
        ]
        
        for field in boolean_fields:
            with self.subTest(field=field):
                # Test valid boolean
                settings_data = {field: True}
                serializer = SpiderSettingsSerializer(data=settings_data)
                self.assertTrue(serializer.is_valid())
                
                # Test string true (DRF converts this)
                settings_data = {field: "true"}
                serializer = SpiderSettingsSerializer(data=settings_data)
                self.assertTrue(serializer.is_valid())
                
                # Test false
                settings_data = {field: False}
                serializer = SpiderSettingsSerializer(data=settings_data)
                self.assertTrue(serializer.is_valid())


class SpiderSerializerTest(BaseTestCase):
    """Test cases for SpiderSerializer."""

    def setUp(self):
        """Set up test data."""
        super().setUp()
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.project = Project.objects.create(
            owner=self.user,
            name='Test Project',
            notes='Test project notes'
        )

    def test_valid_spider_with_structured_settings(self):
        """Test creating spider with valid structured settings."""
        spider_data = {
            'project': self.project.id,
            'name': 'test-spider',
            'start_urls_json': ['https://example.com'],
            'settings_json': {
                'block_images': True,
                'headless': False,
                'max_retry': 3,
                'parallel': 2,
                'user_agent': 'Custom Bot'
            },
            'parse_rules_json': {'title': 'h1'}
        }
        
        serializer = SpiderSerializer(data=spider_data)
        self.assertTrue(serializer.is_valid())
        
        spider = serializer.save()
        self.assertEqual(spider.name, 'test-spider')
        self.assertEqual(spider.settings_json['block_images'], True)
        self.assertEqual(spider.settings_json['max_retry'], 3)

    def test_spider_with_null_settings(self):
        """Test creating spider with null settings."""
        spider_data = {
            'project': self.project.id,
            'name': 'minimal-spider',
            'start_urls_json': ['https://example.com'],
            'settings_json': None
        }
        
        serializer = SpiderSerializer(data=spider_data)
        self.assertTrue(serializer.is_valid())
        
        spider = serializer.save()
        self.assertIsNone(spider.settings_json)

    def test_spider_with_empty_settings(self):
        """Test creating spider with empty settings object."""
        spider_data = {
            'project': self.project.id,
            'name': 'empty-settings-spider',
            'start_urls_json': ['https://example.com'],
            'settings_json': {}
        }
        
        serializer = SpiderSerializer(data=spider_data)
        self.assertTrue(serializer.is_valid())
        
        spider = serializer.save()
        self.assertEqual(spider.settings_json, {})

    def test_invalid_settings_not_dict(self):
        """Test validation fails when settings_json is not a dict."""
        spider_data = {
            'project': self.project.id,
            'name': 'invalid-spider',
            'start_urls_json': ['https://example.com'],
            'settings_json': "not a dict"
        }
        
        serializer = SpiderSerializer(data=spider_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('settings_json', serializer.errors)

    def test_invalid_settings_structure(self):
        """Test validation fails with invalid settings structure."""
        spider_data = {
            'project': self.project.id,
            'name': 'invalid-spider',
            'start_urls_json': ['https://example.com'],
            'settings_json': {
                'max_retry': -1,  # Invalid: negative value
                'parallel': 0,    # Invalid: must be at least 1
                'headless': "not a boolean"  # Invalid: not a boolean
            }
        }
        
        serializer = SpiderSerializer(data=spider_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('settings_json', serializer.errors)

    def test_valid_settings_with_all_fields(self):
        """Test validation passes with all valid settings fields."""
        spider_data = {
            'project': self.project.id,
            'name': 'full-spider',
            'start_urls_json': ['https://example.com'],
            'settings_json': {
                'block_images': True,
                'block_images_and_css': False,
                'tiny_profile': True,
                'profile': 'mobile',
                'user_agent': 'Mozilla/5.0 Custom Bot',
                'window_size': '1920x1080',
                'headless': True,
                'wait_for_complete_page_load': False,
                'reuse_driver': True,
                'max_retry': 5,
                'parallel': 4,
                'cache': True
            }
        }
        
        serializer = SpiderSerializer(data=spider_data)
        self.assertTrue(serializer.is_valid())
        
        spider = serializer.save()
        self.assertEqual(spider.settings_json['block_images'], True)
        self.assertEqual(spider.settings_json['max_retry'], 5)
        self.assertEqual(spider.settings_json['parallel'], 4)
        self.assertEqual(spider.settings_json['profile'], 'mobile')

    def test_serializer_output_includes_settings(self):
        """Test serializer output includes settings_json correctly."""
        spider = Spider.objects.create(
            project=self.project,
            name='output-test-spider',
            start_urls_json=['https://example.com'],
            settings_json={
                'headless': True,
                'max_retry': 2,
                'user_agent': 'Test Bot'
            }
        )
        
        serializer = SpiderSerializer(spider)
        data = serializer.data
        
        self.assertEqual(data['settings_json']['headless'], True)
        self.assertEqual(data['settings_json']['max_retry'], 2)
        self.assertEqual(data['settings_json']['user_agent'], 'Test Bot')

    def test_update_spider_settings(self):
        """Test updating spider with new settings."""
        spider = Spider.objects.create(
            project=self.project,
            name='update-spider',
            start_urls_json=['https://example.com'],
            settings_json={'headless': False}
        )
        
        update_data = {
            'settings_json': {
                'headless': True,
                'max_retry': 5,
                'parallel': 3
            }
        }
        
        serializer = SpiderSerializer(spider, data=update_data, partial=True)
        self.assertTrue(serializer.is_valid())
        
        updated_spider = serializer.save()
        self.assertEqual(updated_spider.settings_json['headless'], True)
        self.assertEqual(updated_spider.settings_json['max_retry'], 5)
        self.assertEqual(updated_spider.settings_json['parallel'], 3)
