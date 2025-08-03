"""
Test cases for Spider views/API endpoints.
"""

import json
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from apps.spider.models import Spider
from apps.projects.models import Project
from .test_core import BaseTestCase

User = get_user_model()


class SpiderAPITest(APITestCase, BaseTestCase):
    """Test cases for Spider API endpoints."""

    def setUp(self):
        """Set up test data."""
        super().setUp()
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.client.force_authenticate(user=self.user)
        
        self.project = Project.objects.create(
            owner=self.user,
            name='Test Project',
            notes='Test project notes'
        )

    def test_create_spider_with_structured_settings(self):
        """Test creating a spider via API with structured settings."""
        spider_data = {
            'project': self.project.id,
            'name': 'api-test-spider',
            'start_urls_json': ['https://example.com', 'https://test.com'],
            'settings_json': {
                'block_images': True,
                'headless': False,
                'max_retry': 3,
                'parallel': 2,
                'user_agent': 'API Test Bot',
                'window_size': '1920x1080'
            },
            'parse_rules_json': {'title': 'h1', 'links': 'a[href]'}
        }
        
        url = reverse('spider-list')  # Adjust URL name based on your URL configuration
        response = self.client.post(url, data=spider_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'api-test-spider')
        self.assertEqual(response.data['settings_json']['block_images'], True)
        self.assertEqual(response.data['settings_json']['max_retry'], 3)
        self.assertEqual(response.data['settings_json']['user_agent'], 'API Test Bot')

    def test_create_spider_with_invalid_settings(self):
        """Test creating a spider with invalid settings structure."""
        spider_data = {
            'project': self.project.id,
            'name': 'invalid-spider',
            'start_urls_json': ['https://example.com'],
            'settings_json': {
                'max_retry': -1,  # Invalid: negative value
                'parallel': 0,    # Invalid: must be at least 1
                'headless': 'not_boolean'  # Invalid: not a boolean
            }
        }
        
        url = reverse('spider-list')
        response = self.client.post(url, data=spider_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('settings_json', response.data)

    def test_create_spider_with_null_settings(self):
        """Test creating a spider with null settings."""
        spider_data = {
            'project': self.project.id,
            'name': 'null-settings-spider',
            'start_urls_json': ['https://example.com'],
            'settings_json': None
        }
        
        url = reverse('spider-list')
        response = self.client.post(url, data=spider_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsNone(response.data['settings_json'])

    def test_update_spider_settings(self):
        """Test updating spider settings via API."""
        spider = Spider.objects.create(
            project=self.project,
            name='update-test-spider',
            start_urls_json=['https://example.com'],
            settings_json={'headless': False, 'max_retry': 1}
        )
        
        update_data = {
            'settings_json': {
                'headless': True,
                'max_retry': 5,
                'parallel': 3,
                'cache': True,
                'user_agent': 'Updated Bot'
            }
        }
        
        url = reverse('spider-detail', kwargs={'pk': spider.pk})
        response = self.client.patch(url, data=update_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['settings_json']['headless'], True)
        self.assertEqual(response.data['settings_json']['max_retry'], 5)
        self.assertEqual(response.data['settings_json']['parallel'], 3)
        self.assertEqual(response.data['settings_json']['cache'], True)
        self.assertEqual(response.data['settings_json']['user_agent'], 'Updated Bot')

    def test_get_spider_with_settings(self):
        """Test retrieving spider with structured settings."""
        settings = {
            'block_images': True,
            'tiny_profile': False,
            'profile': 'desktop',
            'headless': True,
            'max_retry': 4,
            'parallel': 2
        }
        
        spider = Spider.objects.create(
            project=self.project,
            name='get-test-spider',
            start_urls_json=['https://example.com'],
            settings_json=settings
        )
        
        url = reverse('spider-detail', kwargs={'pk': spider.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['settings_json'], settings)

    def test_list_spiders_with_settings(self):
        """Test listing spiders includes structured settings."""
        spider1 = Spider.objects.create(
            project=self.project,
            name='list-spider-1',
            start_urls_json=['https://example.com'],
            settings_json={'headless': True, 'max_retry': 2}
        )
        
        url = reverse('spider-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check that the response contains our spider and settings are properly serialized
        response_data = response.data
        if isinstance(response_data, dict) and 'results' in response_data:
            # Handle paginated response
            spiders = response_data['results']
        else:
            # Handle direct list response
            spiders = response_data
        
        # Find our spider in the response
        our_spider = None
        for spider in spiders:
            if spider['name'] == 'list-spider-1':
                our_spider = spider
                break
        
        self.assertIsNotNone(our_spider, "Our test spider should be in the response")
        self.assertEqual(our_spider['settings_json']['headless'], True)
        self.assertEqual(our_spider['settings_json']['max_retry'], 2)
