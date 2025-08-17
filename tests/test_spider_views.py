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
        """Test creating a spider via API with nested settings."""
        payload = {
            'Spider': {
                'Name': 'api-test-spider',
                'Project': self.project.id,
            },
            'Target': {
                'URL': 'https://example.com'
            },
            'Execution': {
                'Block_Images': True,
                'Headless_Mode': False,
                'Parallel_Instances': 2,
                'User_Agent': 'API Test Bot',
                'Window_Size': '1920x1080'
            },
            'RetryPolicy': {
                'Max_Retries': 3
            },
            'Output': {
                'Filename': 'out',
                'Formats': ['json']
            }
        }
        url = reverse('spider-list')
        response = self.client.post(url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(response.data['Spider']['Name'], 'api-test-spider')
        self.assertEqual(response.data['Execution']['Block_Images'], True)
        self.assertEqual(response.data['Execution']['User_Agent'], 'API Test Bot')

    def test_create_spider_with_invalid_settings(self):
        """Test creating a spider with invalid nested settings structure."""
        payload = {
            'Spider': {
                'Name': 'invalid-spider',
                'Project': self.project.id,
            },
            'Target': {
                'URL': 'https://example.com'
            },
            'Execution': {
                'Parallel_Instances': 0,
                'Headless_Mode': 'nope'
            }
        }
        url = reverse('spider-list')
        response = self.client.post(url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Execution', response.data)

    def test_create_spider_with_null_settings(self):
        """Test creating a spider with minimal nested payload."""
        payload = {
            'Spider': {
                'Name': 'null-settings-spider',
                'Project': self.project.id,
            },
            'Target': {
                'URL': 'https://example.com'
            },
            'Execution': {}
        }
        url = reverse('spider-list')
        response = self.client.post(url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['Target']['URL'], 'https://example.com')

    def test_update_spider_settings(self):
        """Test updating spider settings via API using nested blocks."""
        spider = Spider.objects.create(
            project=self.project,
            name='update-test-spider',
            start_urls_json=['https://example.com'],
            settings_json={'headless': False, 'max_retry': 1}
        )
        update_payload = {
            'Execution': {
                'Headless_Mode': True,
                'Parallel_Instances': 3,
                'User_Agent': 'Updated Bot'
            },
            'RetryPolicy': {
                'Max_Retries': 5
            }
        }
        url = reverse('spider-detail', kwargs={'pk': spider.pk})
        response = self.client.patch(url, data=update_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data['Execution']['Headless_Mode'], True)
        self.assertEqual(response.data['Execution']['Parallel_Instances'], 3)
        self.assertEqual(response.data['Execution']['User_Agent'], 'Updated Bot')
        self.assertEqual(response.data['RetryPolicy']['Max_Retries'], 5)

    def test_get_spider_with_settings(self):
        """Test retrieving spider returns nested blocks mapping from settings_json."""
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
        self.assertEqual(response.data['Spider']['Name'], 'get-test-spider')
        self.assertEqual(response.data['Execution']['Headless_Mode'], True)
        self.assertEqual(response.data['Execution']['Parallel_Instances'], 2)

    def test_list_spiders_with_settings(self):
        """Test listing spiders includes nested blocks and derived values."""
        Spider.objects.create(
            project=self.project,
            name='list-spider-1',
            start_urls_json=['https://example.com'],
            settings_json={'headless': True, 'max_retry': 2}
        )
        url = reverse('spider-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.data
        spiders = response_data['results'] if isinstance(response_data, dict) and 'results' in response_data else response_data
        our_spider = None
        for sp in spiders:
            if sp['Spider']['Name'] == 'list-spider-1':
                our_spider = sp
                break
        self.assertIsNotNone(our_spider, "Our test spider should be in the response")
        self.assertEqual(our_spider['Execution']['Headless_Mode'], True)
        self.assertEqual(our_spider['RetryPolicy']['Max_Retries'], 2)
