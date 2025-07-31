"""
Test cases for RequestQueue views and API endpoints.
"""

import base64
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from apps.request.models import RequestQueue
from apps.job.models import Job
from apps.spider.models import Spider
from apps.projects.models import Project
from .test_core import BaseTestCase

User = get_user_model()


class RequestQueueViewSetTest(APITestCase, BaseTestCase):
    """Test cases for RequestQueueViewSet API endpoints."""

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
            method='GET',
            priority=5
        )
        
        self.other_request = RequestQueue.objects.create(
            job=self.other_job,
            url='https://other.com/page1',
            method='GET'
        )
        
    def authenticate(self, user=None):
        """Authenticate the client with JWT token."""
        if user is None:
            user = self.user
        refresh = RefreshToken.for_user(user)
        token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
    def test_list_requests_authenticated(self):
        """Test listing requests for authenticated user."""
        self.authenticate()
        
        url = reverse('request-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['id'], self.request_obj.id)
        
    def test_list_requests_unauthenticated(self):
        """Test that unauthenticated users cannot list requests."""
        url = reverse('request-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_list_requests_filtered_by_user(self):
        """Test that users only see requests for their own jobs."""
        self.authenticate()
        
        url = reverse('request-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        
        # Should only see user's own request, not other user's request
        request_ids = [req['id'] for req in response.data['results']]
        self.assertIn(self.request_obj.id, request_ids)
        self.assertNotIn(self.other_request.id, request_ids)
        
    def test_list_requests_filter_by_job(self):
        """Test filtering requests by job ID."""
        self.authenticate()
        
        # Create another request for the same job
        RequestQueue.objects.create(
            job=self.job,
            url='https://example.com/page2',
            method='GET'
        )
        
        url = reverse('request-list')
        response = self.client.get(url, {'job': self.job.id})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        
        # All requests should belong to the specified job
        for req in response.data['results']:
            self.assertEqual(req['job'], self.job.id)
            
    def test_list_requests_filter_by_status(self):
        """Test filtering requests by status."""
        self.authenticate()
        
        # Create requests with different statuses
        RequestQueue.objects.create(
            job=self.job,
            url='https://example.com/done',
            status='done'
        )
        RequestQueue.objects.create(
            job=self.job,
            url='https://example.com/error',
            status='error'
        )
        
        url = reverse('request-list')
        response = self.client.get(url, {'status': 'pending'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Only pending requests (original one)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['status'], 'pending')
        
    def test_list_requests_filter_by_priority(self):
        """Test filtering requests by minimum priority."""
        self.authenticate()
        
        # Create requests with different priorities  
        RequestQueue.objects.create(
            job=self.job,
            url='https://example.com/low',
            priority=1
        )
        RequestQueue.objects.create(
            job=self.job,
            url='https://example.com/high',
            priority=10
        )
        
        url = reverse('request-list')
        response = self.client.get(url, {'priority_min': 5})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should get requests with priority >= 5 (original with priority 5 and high with priority 10)
        self.assertEqual(len(response.data['results']), 2)
        for req in response.data['results']:
            self.assertGreaterEqual(req['priority'], 5)
            
    def test_create_request_authenticated(self):
        """Test creating a request when authenticated."""
        self.authenticate()
        
        url = reverse('request-list')
        data = {
            'job': self.job.id,
            'url': 'https://example.com/new-page',
            'method': 'POST',
            'priority': 3
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['job'], self.job.id)
        self.assertEqual(response.data['url'], 'https://example.com/new-page')
        self.assertEqual(response.data['method'], 'POST')
        self.assertEqual(response.data['priority'], 3)
        
        # Verify request was created in database
        request = RequestQueue.objects.get(id=response.data['id'])
        self.assertEqual(request.job, self.job)
        
    def test_create_request_with_body(self):
        """Test creating a request with body data."""
        self.authenticate()
        
        body_data = b'{"test": "payload"}'
        body_b64 = base64.b64encode(body_data).decode('utf-8')
        
        url = reverse('request-list')
        data = {
            'job': self.job.id,
            'url': 'https://api.example.com/endpoint',
            'method': 'POST',
            'headers_json': {'Content-Type': 'application/json'},
            'body_blob': body_b64
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify body was stored correctly
        request = RequestQueue.objects.get(id=response.data['id'])
        self.assertEqual(request.body_blob, body_data)
        
    def test_create_request_unauthenticated(self):
        """Test that unauthenticated users cannot create requests."""
        url = reverse('request-list')
        data = {
            'job': self.job.id,
            'url': 'https://example.com/page',
            'method': 'GET'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_create_request_other_users_job(self):
        """Test that users cannot create requests for other users' jobs."""
        self.authenticate()
        
        url = reverse('request-list')
        data = {
            'job': self.other_job.id,  # Other user's job
            'url': 'https://example.com/page',
            'method': 'GET'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('job', response.data)
        
    def test_retrieve_request_authenticated(self):
        """Test retrieving a specific request when authenticated."""
        self.authenticate()
        
        url = reverse('request-detail', kwargs={'pk': self.request_obj.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.request_obj.id)
        self.assertEqual(response.data['url'], 'https://example.com/page1')
        
    def test_retrieve_other_users_request(self):
        """Test that users cannot retrieve other users' requests."""
        self.authenticate()
        
        url = reverse('request-detail', kwargs={'pk': self.other_request.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
    def test_update_request_authenticated(self):
        """Test updating a request when authenticated."""
        self.authenticate()
        
        url = reverse('request-detail', kwargs={'pk': self.request_obj.id})
        data = {
            'priority': 10,
            'status': 'in_progress'
        }
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['priority'], 10)
        self.assertEqual(response.data['status'], 'in_progress')
        
        # Verify request was updated in database
        self.request_obj.refresh_from_db()
        self.assertEqual(self.request_obj.priority, 10)
        self.assertEqual(self.request_obj.status, 'in_progress')
        
    def test_delete_request_authenticated(self):
        """Test deleting a request when authenticated."""
        self.authenticate()
        
        # Create a request to delete
        request_to_delete = RequestQueue.objects.create(
            job=self.job,
            url='https://example.com/delete-me',
            method='GET'
        )
        
        url = reverse('request-detail', kwargs={'pk': request_to_delete.id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify request was deleted from database
        with self.assertRaises(RequestQueue.DoesNotExist):
            RequestQueue.objects.get(id=request_to_delete.id)
            
    def test_mark_in_progress_action(self):
        """Test mark_in_progress custom action."""
        self.authenticate()
        
        # Ensure request is pending
        self.request_obj.status = 'pending'
        self.request_obj.save()
        
        url = reverse('request-mark-in-progress', kwargs={'pk': self.request_obj.id})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'in_progress')
        self.assertIsNotNone(response.data['picked_at'])
        
        # Verify in database
        self.request_obj.refresh_from_db()
        self.assertEqual(self.request_obj.status, 'in_progress')
        self.assertIsNotNone(self.request_obj.picked_at)
        
    def test_mark_in_progress_invalid_status(self):
        """Test mark_in_progress with non-pending request."""
        self.authenticate()
        
        # Set request to done status
        self.request_obj.status = 'done'
        self.request_obj.save()
        
        url = reverse('request-mark-in-progress', kwargs={'pk': self.request_obj.id})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        
    def test_mark_done_action(self):
        """Test mark_done custom action."""
        self.authenticate()
        
        url = reverse('request-mark-done', kwargs={'pk': self.request_obj.id})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'done')
        
        # Verify in database
        self.request_obj.refresh_from_db()
        self.assertEqual(self.request_obj.status, 'done')
        
    def test_mark_error_action(self):
        """Test mark_error custom action."""
        self.authenticate()
        
        self.request_obj.retries = 1
        self.request_obj.save()
        
        url = reverse('request-mark-error', kwargs={'pk': self.request_obj.id})
        response = self.client.post(url, {'increment_retry': True}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'error')
        
        # Verify retry was incremented
        self.request_obj.refresh_from_db()
        self.assertEqual(self.request_obj.retries, 2)
        
    def test_retry_action_success(self):
        """Test retry custom action when retries are available."""
        self.authenticate()
        
        # Set up request with failed status but retries available
        self.request_obj.status = 'error'
        self.request_obj.retries = 2
        self.request_obj.max_retries = 5
        self.request_obj.save()
        
        url = reverse('request-retry', kwargs={'pk': self.request_obj.id})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'pending')
        
        # Verify in database
        self.request_obj.refresh_from_db()
        self.assertEqual(self.request_obj.status, 'pending')
        
    def test_retry_action_max_retries_exceeded(self):
        """Test retry custom action when max retries exceeded."""
        self.authenticate()
        
        # Set up request with max retries exceeded
        self.request_obj.status = 'error'
        self.request_obj.retries = 3
        self.request_obj.max_retries = 3
        self.request_obj.save()
        
        url = reverse('request-retry', kwargs={'pk': self.request_obj.id})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        
    def test_next_pending_action(self):
        """Test next_pending custom action for worker endpoints."""
        self.authenticate()
        
        # Create multiple pending requests with different priorities
        req1 = RequestQueue.objects.create(
            job=self.job,
            url='https://example.com/low',
            priority=1,
            status='pending'
        )
        req2 = RequestQueue.objects.create(
            job=self.job,
            url='https://example.com/high',
            priority=10,
            status='pending'
        )
        RequestQueue.objects.create(
            job=self.job,
            url='https://example.com/done',
            status='done'  # Should not be included
        )
        
        url = reverse('request-next-pending')
        response = self.client.get(url, {'limit': 5})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should return pending requests ordered by priority
        results = response.data
        self.assertEqual(len(results), 3)  # 2 new + 1 original pending request
        
        # Highest priority should be first
        self.assertEqual(results[0]['id'], req2.id)
        self.assertEqual(results[0]['priority'], 10)
        
    def test_next_pending_action_with_job_filter(self):
        """Test next_pending action with job filter."""
        self.authenticate()
        
        # Create another job and request
        job2 = Job.objects.create(spider=self.spider, status='running')
        RequestQueue.objects.create(
            job=job2,
            url='https://example.com/other-job',
            status='pending'
        )
        
        url = reverse('request-next-pending')
        response = self.client.get(url, {'job': self.job.id})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should only return requests for specified job
        for req in response.data:
            self.assertEqual(req['job'], self.job.id)