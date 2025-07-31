"""
Tests for Spider views.

This module contains tests for spider-related views including
SpiderViewSet, authentication, permissions, and spider management functionality.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from apps.projects.models import Project
from apps.scraper.models import Spider
from apps.scraper.views import SpiderViewSet
from .test_core import BaseTestCase

User = get_user_model()


class SpiderViewSetTestCase(BaseTestCase, APITestCase):
    """Tests for the SpiderViewSet."""
    
    def setUp(self):
        """Set up test data."""
        super().setUp()
        self.client = APIClient()
        
        # Create test users
        self.user1 = self.create_user()
        self.user2 = self.create_user(email='user2@example.com')
        
        # Create test projects
        self.project1 = Project.objects.create(
            owner=self.user1,
            name='User1 Project',
            notes='Project owned by user1'
        )
        self.project2 = Project.objects.create(
            owner=self.user2,
            name='User2 Project',
            notes='Project owned by user2'
        )
        
        # Create test spiders
        self.spider1 = Spider.objects.create(
            project=self.project1,
            name='test-spider-1',
            start_urls_json=['https://example1.com'],
            settings_json={'delay': 1},
            parse_rules_json={'title': 'h1'}
        )
        self.spider2 = Spider.objects.create(
            project=self.project1,
            name='test-spider-2',
            start_urls_json=['https://example2.com']
        )
        self.spider3 = Spider.objects.create(
            project=self.project2,
            name='test-spider-3',
            start_urls_json=['https://example3.com']
        )
        
        # API endpoints
        self.spider_list_url = '/spiders/'
        self.spider_detail_url = lambda pk: f'/spiders/{pk}/'
    
    def get_jwt_token(self, user):
        """Helper method to get JWT token for a user."""
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)
    
    def authenticate_user(self, user):
        """Helper method to authenticate a user."""
        token = self.get_jwt_token(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    
    def test_unauthenticated_access_denied(self):
        """Test that unauthenticated requests are denied."""
        # List spiders
        response = self.client.get(self.spider_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Create spider
        data = {
            'project': self.project1.id,
            'name': 'new-spider',
            'start_urls_json': ['https://new.com']
        }
        response = self.client.post(self.spider_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Get spider detail
        response = self.client.get(self.spider_detail_url(self.spider1.id))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_list_spiders_authenticated(self):
        """Test listing spiders for authenticated user."""
        self.authenticate_user(self.user1)
        
        response = self.client.get(self.spider_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should only see user1's spiders
        data = response.json()
        self.assertEqual(data['count'], 2)  # spider1 and spider2
        
        spider_names = [spider['name'] for spider in data['results']]
        self.assertIn('test-spider-1', spider_names)
        self.assertIn('test-spider-2', spider_names)
        self.assertNotIn('test-spider-3', spider_names)  # Belongs to user2
    
    def test_list_spiders_user_isolation(self):
        """Test that users only see their own spiders."""
        # Test user1 sees only their spiders
        self.authenticate_user(self.user1)
        response = self.client.get(self.spider_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user1_spiders = response.json()['results']
        self.assertEqual(len(user1_spiders), 2)
        
        # Test user2 sees only their spiders
        self.authenticate_user(self.user2)
        response = self.client.get(self.spider_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user2_spiders = response.json()['results']
        self.assertEqual(len(user2_spiders), 1)
        self.assertEqual(user2_spiders[0]['name'], 'test-spider-3')
    
    def test_get_spider_detail(self):
        """Test getting spider detail."""
        self.authenticate_user(self.user1)
        
        response = self.client.get(self.spider_detail_url(self.spider1.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        self.assertEqual(data['id'], self.spider1.id)
        self.assertEqual(data['name'], 'test-spider-1')
        self.assertEqual(data['project'], self.project1.id)
        self.assertEqual(data['start_urls_json'], ['https://example1.com'])
        self.assertEqual(data['settings_json']['delay'], 1)
        self.assertEqual(data['parse_rules_json']['title'], 'h1')
    
    def test_get_spider_detail_permission_denied(self):
        """Test that users cannot access other users' spiders."""
        self.authenticate_user(self.user1)
        
        # Try to access user2's spider
        response = self.client.get(self.spider_detail_url(self.spider3.id))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_create_spider(self):
        """Test creating a new spider."""
        self.authenticate_user(self.user1)
        
        data = {
            'project': self.project1.id,
            'name': 'new-spider',
            'start_urls_json': ['https://newsite.com', 'https://another.com'],
            'settings_json': {
                'delay': 2,
                'timeout': 30,
                'headers': {'User-Agent': 'Test Bot'}
            },
            'parse_rules_json': {
                'title': 'h1.main-title',
                'content': 'div.content'
            }
        }
        
        response = self.client.post(self.spider_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify spider was created
        created_spider = Spider.objects.get(name='new-spider')
        self.assertEqual(created_spider.project, self.project1)
        self.assertEqual(created_spider.start_urls_json, ['https://newsite.com', 'https://another.com'])
        self.assertEqual(created_spider.settings_json['delay'], 2)
        self.assertEqual(created_spider.parse_rules_json['title'], 'h1.main-title')
        
        # Verify response data
        response_data = response.json()
        self.assertEqual(response_data['name'], 'new-spider')
        self.assertEqual(response_data['project'], self.project1.id)
    
    def test_create_spider_minimal_data(self):
        """Test creating spider with minimal required data."""
        self.authenticate_user(self.user1)
        
        data = {
            'project': self.project1.id,
            'name': 'minimal-spider',
            'start_urls_json': ['https://minimal.com']
        }
        
        response = self.client.post(self.spider_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        created_spider = Spider.objects.get(name='minimal-spider')
        self.assertEqual(created_spider.project, self.project1)
        self.assertIsNone(created_spider.settings_json)
        self.assertIsNone(created_spider.parse_rules_json)
    
    def test_create_spider_invalid_project(self):
        """Test creating spider with invalid project ID."""
        self.authenticate_user(self.user1)
        
        data = {
            'project': 99999,  # Non-existent project
            'name': 'invalid-project-spider',
            'start_urls_json': ['https://example.com']
        }
        
        response = self.client.post(self.spider_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('project', response.json())
    
    def test_create_spider_other_users_project(self):
        """Test creating spider in another user's project."""
        self.authenticate_user(self.user1)
        
        data = {
            'project': self.project2.id,  # User2's project
            'name': 'unauthorized-spider',
            'start_urls_json': ['https://example.com']
        }
        
        response = self.client.post(self.spider_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_create_spider_duplicate_name_same_project(self):
        """Test creating spider with duplicate name in same project."""
        self.authenticate_user(self.user1)
        
        data = {
            'project': self.project1.id,
            'name': 'test-spider-1',  # Already exists in project1
            'start_urls_json': ['https://example.com']
        }
        
        response = self.client.post(self.spider_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_create_spider_same_name_different_projects(self):
        """Test creating spider with same name in different projects."""
        self.authenticate_user(self.user1)
        
        # Create another project for user1
        project3 = Project.objects.create(
            owner=self.user1,
            name='Another Project',
            notes='Another project for user1'
        )
        
        data = {
            'project': project3.id,
            'name': 'test-spider-1',  # Same name as existing spider in project1
            'start_urls_json': ['https://example.com']
        }
        
        response = self.client.post(self.spider_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Should create successfully since it's in a different project
        created_spider = Spider.objects.get(project=project3, name='test-spider-1')
        self.assertEqual(created_spider.project, project3)
    
    def test_update_spider_put(self):
        """Test updating spider with PUT (full update)."""
        self.authenticate_user(self.user1)
        
        data = {
            'project': self.project1.id,
            'name': 'updated-spider',
            'start_urls_json': ['https://updated.com'],
            'settings_json': {'delay': 3, 'new_setting': 'value'},
            'parse_rules_json': {'title': 'h2'}
        }
        
        response = self.client.put(
            self.spider_detail_url(self.spider1.id), 
            data, 
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify spider was updated
        updated_spider = Spider.objects.get(id=self.spider1.id)
        self.assertEqual(updated_spider.name, 'updated-spider')
        self.assertEqual(updated_spider.start_urls_json, ['https://updated.com'])
        self.assertEqual(updated_spider.settings_json['delay'], 3)
        self.assertEqual(updated_spider.parse_rules_json['title'], 'h2')
    
    def test_update_spider_patch(self):
        """Test updating spider with PATCH (partial update)."""
        self.authenticate_user(self.user1)
        
        data = {
            'name': 'partially-updated',
            'settings_json': {'delay': 5}
        }
        
        response = self.client.patch(
            self.spider_detail_url(self.spider1.id), 
            data, 
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify only specified fields were updated
        updated_spider = Spider.objects.get(id=self.spider1.id)
        self.assertEqual(updated_spider.name, 'partially-updated')
        self.assertEqual(updated_spider.settings_json['delay'], 5)
        
        # Other fields should remain unchanged
        self.assertEqual(updated_spider.start_urls_json, ['https://example1.com'])
        self.assertEqual(updated_spider.project, self.project1)
    
    def test_update_spider_permission_denied(self):
        """Test updating another user's spider is denied."""
        self.authenticate_user(self.user1)
        
        data = {'name': 'hacked-spider'}
        
        response = self.client.patch(
            self.spider_detail_url(self.spider3.id),  # User2's spider
            data, 
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_delete_spider(self):
        """Test deleting a spider."""
        self.authenticate_user(self.user1)
        
        spider_id = self.spider1.id
        self.assertTrue(Spider.objects.filter(id=spider_id).exists())
        
        response = self.client.delete(self.spider_detail_url(spider_id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify spider was deleted
        self.assertFalse(Spider.objects.filter(id=spider_id).exists())
    
    def test_delete_spider_permission_denied(self):
        """Test deleting another user's spider is denied."""
        self.authenticate_user(self.user1)
        
        spider_id = self.spider3.id
        self.assertTrue(Spider.objects.filter(id=spider_id).exists())
        
        response = self.client.delete(self.spider_detail_url(spider_id))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
        # Verify spider was not deleted
        self.assertTrue(Spider.objects.filter(id=spider_id).exists())
    
    def test_spider_ordering(self):
        """Test that spiders are returned in correct order (newest first)."""
        self.authenticate_user(self.user1)
        
        # Create additional spiders to test ordering
        spider_new = Spider.objects.create(
            project=self.project1,
            name='newest-spider',
            start_urls_json=['https://newest.com']
        )
        
        response = self.client.get(self.spider_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        spiders = response.json()['results']
        # Should be ordered by created_at descending (newest first)
        self.assertEqual(spiders[0]['name'], 'newest-spider')
    
    def test_spider_list_pagination(self):
        """Test spider list pagination."""
        self.authenticate_user(self.user1)
        
        # Create many spiders to test pagination
        for i in range(25):
            Spider.objects.create(
                project=self.project1,
                name=f'spider-{i}',
                start_urls_json=[f'https://example{i}.com']
            )
        
        response = self.client.get(self.spider_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        # Default page size should be 20 (from settings)
        self.assertEqual(len(data['results']), 20)
        self.assertIsNotNone(data['next'])
        self.assertIsNone(data['previous'])
        
        # Test second page
        response = self.client.get(data['next'])
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        page2_data = response.json()
        self.assertEqual(len(page2_data['results']), 7)  # Remaining spiders
    
    def test_spider_creation_with_perform_create(self):
        """Test that perform_create properly sets the project."""
        self.authenticate_user(self.user1)
        
        # Test with explicit project in data
        data = {
            'project': self.project1.id,
            'name': 'explicit-project-spider',
            'start_urls_json': ['https://example.com']
        }
        
        response = self.client.post(self.spider_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        spider = Spider.objects.get(name='explicit-project-spider')
        self.assertEqual(spider.project, self.project1)
    
    def test_spider_viewset_queryset_filtering(self):
        """Test that viewset properly filters spiders by user ownership."""
        viewset = SpiderViewSet()
        
        # Mock request with user1
        class MockRequest:
            def __init__(self, user):
                self.user = user
        
        viewset.request = MockRequest(self.user1)
        queryset = viewset.get_queryset()
        
        # Should only include spiders from projects owned by user1
        spider_names = [spider.name for spider in queryset]
        self.assertIn('test-spider-1', spider_names)
        self.assertIn('test-spider-2', spider_names)
        self.assertNotIn('test-spider-3', spider_names)  # Owned by user2
    
    def test_spider_json_field_handling_in_api(self):
        """Test that JSON fields are properly handled in API responses."""
        self.authenticate_user(self.user1)
        
        # Create spider with various JSON data types
        complex_spider = Spider.objects.create(
            project=self.project1,
            name='complex-json-spider',
            start_urls_json=['https://complex.com'],
            settings_json={
                'string': 'value',
                'number': 42,
                'float': 3.14,
                'boolean': True,
                'null_value': None,
                'list': [1, 2, 3],
                'dict': {'nested': 'value'}
            },
            parse_rules_json={
                'simple': 'selector',
                'complex': {
                    'selector': 'div',
                    'attribute': 'text',
                    'transforms': ['strip', 'lower']
                }
            }
        )
        
        response = self.client.get(self.spider_detail_url(complex_spider.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        settings = data['settings_json']
        rules = data['parse_rules_json']
        
        # Verify all data types are preserved
        self.assertEqual(settings['string'], 'value')
        self.assertEqual(settings['number'], 42)
        self.assertEqual(settings['float'], 3.14)
        self.assertTrue(settings['boolean'])
        self.assertIsNone(settings['null_value'])
        self.assertEqual(settings['list'], [1, 2, 3])
        self.assertIsInstance(settings['dict'], dict)
        
        self.assertEqual(rules['simple'], 'selector')
        self.assertIsInstance(rules['complex'], dict)
        self.assertEqual(rules['complex']['selector'], 'div')
    
    def test_spider_api_error_handling(self):
        """Test API error handling for various scenarios."""
        self.authenticate_user(self.user1)
        
        # Test missing required field
        data = {
            'project': self.project1.id,
            'name': 'incomplete-spider'
            # Missing start_urls_json
        }
        response = self.client.post(self.spider_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('start_urls_json', response.json())
        
        # Test invalid JSON data (this should actually work since DRF handles it)
        data = {
            'project': self.project1.id,
            'name': 'valid-spider',
            'start_urls_json': ['https://example.com'],
            'settings_json': {'valid': 'json'}
        }
        response = self.client.post(self.spider_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Test accessing non-existent spider
        response = self.client.get(self.spider_detail_url(99999))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_spider_api_with_realistic_data(self):
        """Test spider API with realistic web scraping configuration."""
        self.authenticate_user(self.user1)
        
        realistic_data = {
            'project': self.project1.id,
            'name': 'ecommerce-product-scraper',
            'start_urls_json': [
                'https://shop.example.com/products',
                'https://shop.example.com/categories/electronics'
            ],
            'settings_json': {
                'download_delay': 2,
                'randomize_delay': True,
                'concurrent_requests': 8,
                'timeout': 30,
                'retry_times': 3,
                'headers': {
                    'User-Agent': 'Mozilla/5.0 (compatible; ShopBot/1.0)',
                    'Accept': 'text/html,application/xhtml+xml',
                    'Accept-Language': 'en-US,en;q=0.9'
                },
                'cookies': True,
                'follow_redirects': True
            },
            'parse_rules_json': {
                'product_info': {
                    'name': {
                        'selector': 'h1.product-name, .product-title',
                        'attribute': 'text',
                        'required': True
                    },
                    'price': {
                        'selector': '.price, .current-price',
                        'attribute': 'text',
                        'transform': 'extract_price'
                    },
                    'description': {
                        'selector': '.product-description',
                        'attribute': 'html'
                    },
                    'images': {
                        'selector': '.product-images img',
                        'attribute': 'src',
                        'multiple': True
                    },
                    'availability': {
                        'selector': '.stock-status',
                        'attribute': 'text'
                    }
                },
                'navigation': {
                    'next_page': {
                        'selector': 'a.next-page, .pagination .next',
                        'attribute': 'href'
                    },
                    'product_links': {
                        'selector': '.product-grid a, .product-list a',
                        'attribute': 'href',
                        'callback': 'parse_product'
                    }
                }
            }
        }
        
        # Create spider
        response = self.client.post(self.spider_list_url, realistic_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify created spider
        spider = Spider.objects.get(name='ecommerce-product-scraper')
        self.assertEqual(len(spider.start_urls_json), 2)
        self.assertEqual(spider.settings_json['download_delay'], 2)
        self.assertTrue(spider.settings_json['randomize_delay'])
        self.assertEqual(spider.parse_rules_json['product_info']['name']['required'], True)
        
        # Test retrieving the spider
        response = self.client.get(self.spider_detail_url(spider.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        self.assertEqual(data['name'], 'ecommerce-product-scraper')
        self.assertIn('product_info', data['parse_rules_json'])
        self.assertIn('navigation', data['parse_rules_json'])