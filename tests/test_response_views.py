"""
Test cases for Response views and API endpoints.
"""

import tempfile
from pathlib import Path
from django.test import TestCase, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from apps.response.models import Response
from apps.request.models import RequestQueue
from apps.job.models import Job
from apps.spider.models import Spider
from apps.projects.models import Project
from .test_core import BaseTestCase

User = get_user_model()


class ResponseViewSetTest(APITestCase, BaseTestCase):
    """Test cases for ResponseViewSet API endpoints."""

    def setUp(self):
        """Set up test data."""
        super().setUp()
        self.client = APIClient()
        
        # Create test users
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        self.other_user = User.objects.create_user(
            email='otheruser@example.com',
            password='testpass123',
            first_name='Other',
            last_name='User'
        )
        
        # Create test projects
        self.project = Project.objects.create(
            owner=self.user,
            name='Test Project',
            notes='Test project notes'
        )
        
        self.other_project = Project.objects.create(
            owner=self.other_user,
            name='Other Project',
            notes='Other user project'
        )
        
        # Create test spiders
        self.spider = Spider.objects.create(
            project=self.project,
            name='test-spider',
            start_urls_json=['https://example.com']
        )
        
        self.other_spider = Spider.objects.create(
            project=self.other_project,
            name='other-spider',
            start_urls_json=['https://other.com']
        )
        
        # Create test jobs
        self.job = Job.objects.create(
            spider=self.spider,
            status='running'
        )
        
        self.other_job = Job.objects.create(
            spider=self.other_spider,
            status='running'
        )
        
        # Create test requests
        self.request_obj = RequestQueue.objects.create(
            job=self.job,
            url='https://example.com/page1',
            method='GET'
        )
        
        self.other_request = RequestQueue.objects.create(
            job=self.other_job,
            url='https://other.com/page1',
            method='GET'
        )
        
        # Create test responses
        self.response_obj = Response.objects.create(
            request=self.request_obj,
            final_url='https://example.com/final1',
            status_code=200,
            latency_ms=100
        )
        
        self.other_response = Response.objects.create(
            request=self.other_request,
            final_url='https://other.com/final1',
            status_code=404,
            latency_ms=200
        )
        
    def authenticate(self, user=None):
        """Authenticate the client with JWT token."""
        if user is None:
            user = self.user
        refresh = RefreshToken.for_user(user)
        token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
    def test_list_responses_authenticated(self):
        """Test listing responses for authenticated user."""
        self.authenticate()
        
        url = reverse('response-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['id'], self.response_obj.id)
        
    def test_list_responses_unauthenticated(self):
        """Test that unauthenticated users cannot list responses."""
        url = reverse('response-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_list_responses_filtered_by_user(self):
        """Test that users only see responses for their own requests."""
        self.authenticate()
        
        url = reverse('response-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        
        # Should only see user's own response, not other user's response
        response_ids = [resp['id'] for resp in response.data['results']]
        self.assertIn(self.response_obj.id, response_ids)
        self.assertNotIn(self.other_response.id, response_ids)
        
    def test_list_responses_filter_by_request(self):
        """Test filtering responses by request ID."""
        self.authenticate()
        
        # Create another response for the same user
        request2 = RequestQueue.objects.create(
            job=self.job,
            url='https://example.com/page2'
        )
        Response.objects.create(
            request=request2,
            status_code=404
        )
        
        url = reverse('response-list')
        response = self.client.get(url, {'request': self.request_obj.id})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['request'], self.request_obj.id)
        
    def test_list_responses_filter_by_status_code(self):
        """Test filtering responses by status code."""
        self.authenticate()
        
        # Create responses with different status codes
        request2 = RequestQueue.objects.create(
            job=self.job,
            url='https://example.com/notfound'
        )
        Response.objects.create(
            request=request2,
            status_code=404
        )
        
        url = reverse('response-list')
        response = self.client.get(url, {'status_code': 200})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['status_code'], 200)
        
    def test_list_responses_filter_by_cache(self):
        """Test filtering responses by cache status."""
        self.authenticate()
        
        # Create cached and non-cached responses
        request2 = RequestQueue.objects.create(
            job=self.job,
            url='https://example.com/cached'
        )
        Response.objects.create(
            request=request2,
            status_code=200,
            from_cache=True
        )
        
        url = reverse('response-list')
        response = self.client.get(url, {'from_cache': 'true'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertTrue(response.data['results'][0]['from_cache'])
        
    def test_list_responses_filter_by_latency(self):
        """Test filtering responses by latency range."""
        self.authenticate()
        
        # Create responses with different latencies
        request2 = RequestQueue.objects.create(
            job=self.job,
            url='https://example.com/slow'
        )
        Response.objects.create(
            request=request2,
            status_code=200,
            latency_ms=500
        )
        
        url = reverse('response-list')
        response = self.client.get(url, {'min_latency': 200, 'max_latency': 600})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['latency_ms'], 500)
        
    def test_create_response_authenticated(self):
        """Test creating a response when authenticated."""
        self.authenticate()
        
        # Create a new request since each request can only have one response
        new_request = RequestQueue.objects.create(
            job=self.job,
            url='https://example.com/new-request'
        )
        
        url = reverse('response-list')
        data = {
            'request': new_request.id,
            'final_url': 'https://example.com/new-final',
            'status_code': 201,
            'headers_json': {'Content-Type': 'application/json'},
            'latency_ms': 75
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['request'], new_request.id)
        self.assertEqual(response.data['status_code'], 201)
        self.assertEqual(response.data['latency_ms'], 75)
        
        # Verify response was created in database
        response_obj = Response.objects.get(id=response.data['id'])
        self.assertEqual(response_obj.request, new_request)
        
    def test_create_response_unauthenticated(self):
        """Test that unauthenticated users cannot create responses."""
        url = reverse('response-list')
        data = {
            'request': self.request_obj.id,
            'status_code': 200
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_create_response_other_users_request(self):
        """Test that users cannot create responses for other users' requests."""
        self.authenticate()
        
        url = reverse('response-list')
        data = {
            'request': self.other_request.id,  # Other user's request
            'status_code': 200
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('request', response.data)
        
    def test_retrieve_response_authenticated(self):
        """Test retrieving a specific response when authenticated."""
        self.authenticate()
        
        url = reverse('response-detail', kwargs={'pk': self.response_obj.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.response_obj.id)
        self.assertEqual(response.data['status_code'], 200)
        
    def test_retrieve_other_users_response(self):
        """Test that users cannot retrieve other users' responses."""
        self.authenticate()
        
        url = reverse('response-detail', kwargs={'pk': self.other_response.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
    def test_update_response_authenticated(self):
        """Test updating a response when authenticated."""
        self.authenticate()
        
        url = reverse('response-detail', kwargs={'pk': self.response_obj.id})
        data = {
            'status_code': 202,
            'from_cache': True
        }
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status_code'], 202)
        self.assertTrue(response.data['from_cache'])
        
        # Verify response was updated in database
        self.response_obj.refresh_from_db()
        self.assertEqual(self.response_obj.status_code, 202)
        self.assertTrue(self.response_obj.from_cache)
        
    def test_delete_response_authenticated(self):
        """Test deleting a response when authenticated."""
        self.authenticate()
        
        # Create a new request and response to delete
        request_to_delete = RequestQueue.objects.create(
            job=self.job,
            url='https://example.com/delete-me'
        )
        response_to_delete = Response.objects.create(
            request=request_to_delete,
            status_code=200
        )
        
        url = reverse('response-detail', kwargs={'pk': response_to_delete.id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify response was deleted from database
        with self.assertRaises(Response.DoesNotExist):
            Response.objects.get(id=response_to_delete.id)
            
    @override_settings(MEDIA_ROOT=tempfile.mkdtemp())
    def test_body_endpoint_with_content(self):
        """Test getting response body content."""
        self.authenticate()
        
        # Save body content to response
        body_content = '<html><body><h1>Test Page</h1></body></html>'
        self.response_obj.save_body(body_content)
        self.response_obj.save()  # Save the model after setting body_path
        
        url = reverse('response-body', kwargs={'pk': self.response_obj.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['body'], body_content)
        self.assertIn('content_type', response.data)
        self.assertIn('size', response.data)
        
        # Clean up
        self.response_obj.delete_body_file()
        
    def test_body_endpoint_no_content(self):
        """Test getting response body when no content exists."""
        self.authenticate()
        
        url = reverse('response-body', kwargs={'pk': self.response_obj.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
        
    @override_settings(MEDIA_ROOT=tempfile.mkdtemp())
    def test_body_endpoint_download(self):
        """Test downloading response body as file."""
        self.authenticate()
        
        # Save body content to response
        body_content = '<html><body><h1>Download Test</h1></body></html>'
        self.response_obj.save_body(body_content)
        self.response_obj.save()  # Save the model after setting body_path
        
        url = reverse('response-body', kwargs={'pk': self.response_obj.id})
        response = self.client.get(url, {'download': 'true'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.content, body_content.encode('utf-8'))
        self.assertIn('Content-Disposition', response)
        
        # Clean up
        self.response_obj.delete_body_file()
        
    def test_stats_endpoint(self):
        """Test response statistics endpoint."""
        self.authenticate()
        
        # Create additional responses for statistics
        request2 = RequestQueue.objects.create(
            job=self.job,
            url='https://example.com/error'
        )
        Response.objects.create(
            request=request2,
            status_code=404,
            latency_ms=50,
            from_cache=True
        )
        
        url = reverse('response-stats')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_responses', response.data)
        self.assertIn('successful_responses', response.data)
        self.assertIn('error_responses', response.data)
        self.assertIn('avg_latency_ms', response.data)
        self.assertIn('status_code_distribution', response.data)
        self.assertIn('cache_hit_rate', response.data)
        
        # Check values
        self.assertEqual(response.data['total_responses'], 2)
        self.assertEqual(response.data['successful_responses'], 1)
        self.assertEqual(response.data['error_responses'], 1)
        
    def test_successful_responses_endpoint(self):
        """Test successful responses endpoint."""
        self.authenticate()
        
        # Create mix of successful and error responses
        request2 = RequestQueue.objects.create(
            job=self.job,
            url='https://example.com/success2'
        )
        Response.objects.create(
            request=request2,
            status_code=201
        )
        
        request3 = RequestQueue.objects.create(
            job=self.job,
            url='https://example.com/error'
        )
        Response.objects.create(
            request=request3,
            status_code=404
        )
        
        url = reverse('response-successful')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)  # Two successful responses
        
        for resp in response.data['results']:
            self.assertGreaterEqual(resp['status_code'], 200)
            self.assertLess(resp['status_code'], 300)
            
    def test_error_responses_endpoint(self):
        """Test error responses endpoint."""
        self.authenticate()
        
        # Create mix of successful and error responses
        request2 = RequestQueue.objects.create(
            job=self.job,
            url='https://example.com/notfound'
        )
        Response.objects.create(
            request=request2,
            status_code=404
        )
        
        request3 = RequestQueue.objects.create(
            job=self.job,
            url='https://example.com/server-error'
        )
        Response.objects.create(
            request=request3,
            status_code=500
        )
        
        url = reverse('response-errors')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)  # Two error responses
        
        for resp in response.data['results']:
            self.assertGreaterEqual(resp['status_code'], 400)
            
    @override_settings(MEDIA_ROOT=tempfile.mkdtemp())
    def test_save_body_endpoint(self):
        """Test saving response body via API endpoint."""
        self.authenticate()
        
        body_content = '<html><body><h1>API Saved Content</h1></body></html>'
        
        url = reverse('response-save-body', kwargs={'pk': self.response_obj.id})
        response = self.client.post(url, {'body': body_content}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify body was saved
        self.response_obj.refresh_from_db()
        self.assertIsNotNone(self.response_obj.body_path)
        self.assertIsNotNone(self.response_obj.content_hash)
        
        # Verify content
        saved_content = self.response_obj.read_body_text()
        self.assertEqual(saved_content, body_content)
        
        # Clean up
        self.response_obj.delete_body_file()
        
    def test_save_body_endpoint_no_content(self):
        """Test saving response body with no content."""
        self.authenticate()
        
        url = reverse('response-save-body', kwargs={'pk': self.response_obj.id})
        response = self.client.post(url, {}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)