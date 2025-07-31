"""
Test cases for Job views and API endpoints.
"""

from datetime import timedelta
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from apps.job.models import Job
from apps.spider.models import Spider
from apps.projects.models import Project
from .test_core import BaseTestCase

User = get_user_model()


class JobViewSetTest(APITestCase, BaseTestCase):
    """Test cases for JobViewSet API endpoints."""

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
            status='done',
            stats_json={'pages': 10, 'items': 5}
        )
        
        self.other_job = Job.objects.create(
            spider=self.other_spider,
            status='queued'
        )
        
    def authenticate(self, user=None):
        """Authenticate the client with JWT token."""
        if user is None:
            user = self.user
        refresh = RefreshToken.for_user(user)
        token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
    def test_list_jobs_authenticated(self):
        """Test listing jobs for authenticated user."""
        self.authenticate()
        
        url = reverse('job-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['id'], self.job.id)
        
    def test_list_jobs_unauthenticated(self):
        """Test that unauthenticated users cannot list jobs."""
        url = reverse('job-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_list_jobs_filtered_by_user(self):
        """Test that users only see jobs for their own spiders."""
        self.authenticate()
        
        url = reverse('job-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        
        # Should only see user's own job, not other user's job
        job_ids = [job['id'] for job in response.data['results']]
        self.assertIn(self.job.id, job_ids)
        self.assertNotIn(self.other_job.id, job_ids)
        
    def test_create_job_authenticated(self):
        """Test creating a job when authenticated."""
        self.authenticate()
        
        url = reverse('job-list')
        data = {
            'spider': self.spider.id,
            'status': 'queued'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['spider'], self.spider.id)
        self.assertEqual(response.data['status'], 'queued')
        
        # Verify job was created in database
        job = Job.objects.get(id=response.data['id'])
        self.assertEqual(job.spider, self.spider)
        
    def test_create_job_unauthenticated(self):
        """Test that unauthenticated users cannot create jobs."""
        url = reverse('job-list')
        data = {
            'spider': self.spider.id,
            'status': 'queued'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_create_job_other_users_spider(self):
        """Test that users cannot create jobs for other users' spiders."""
        self.authenticate()
        
        url = reverse('job-list')
        data = {
            'spider': self.other_spider.id,  # Other user's spider
            'status': 'queued'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('spider', response.data)
        
    def test_create_job_with_stats(self):
        """Test creating a job with statistics."""
        self.authenticate()
        
        url = reverse('job-list')
        stats = {
            'pages_scraped': 50,
            'items_extracted': 25,
            'duration': 120
        }
        data = {
            'spider': self.spider.id,
            'status': 'done',
            'stats_json': stats
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['stats_json'], stats)
        
    def test_retrieve_job_authenticated(self):
        """Test retrieving a specific job when authenticated."""
        self.authenticate()
        
        url = reverse('job-detail', kwargs={'pk': self.job.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.job.id)
        self.assertEqual(response.data['status'], 'done')
        
    def test_retrieve_other_users_job(self):
        """Test that users cannot retrieve other users' jobs."""
        self.authenticate()
        
        url = reverse('job-detail', kwargs={'pk': self.other_job.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
    def test_update_job_authenticated(self):
        """Test updating a job when authenticated."""
        self.authenticate()
        
        # Create a job in queued status
        job = Job.objects.create(spider=self.spider, status='queued')
        
        url = reverse('job-detail', kwargs={'pk': job.id})
        data = {
            'status': 'running',
            'started_at': timezone.now().isoformat()
        }
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'running')
        
        # Verify job was updated in database
        job.refresh_from_db()
        self.assertEqual(job.status, 'running')
        
    def test_update_other_users_job(self):
        """Test that users cannot update other users' jobs."""
        self.authenticate()
        
        url = reverse('job-detail', kwargs={'pk': self.other_job.id})
        data = {'status': 'running'}
        
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
    def test_delete_job_authenticated(self):
        """Test deleting a job when authenticated."""
        self.authenticate()
        
        # Create a job to delete
        job = Job.objects.create(spider=self.spider, status='failed')
        
        url = reverse('job-detail', kwargs={'pk': job.id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify job was deleted from database
        with self.assertRaises(Job.DoesNotExist):
            Job.objects.get(id=job.id)
            
    def test_delete_other_users_job(self):
        """Test that users cannot delete other users' jobs."""
        self.authenticate()
        
        url = reverse('job-detail', kwargs={'pk': self.other_job.id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
        # Verify job still exists
        self.assertTrue(Job.objects.filter(id=self.other_job.id).exists())
        
    def test_create_job_invalid_data(self):
        """Test creating job with invalid data."""
        self.authenticate()
        
        url = reverse('job-list')
        
        # Missing required field
        data = {
            'status': 'queued'
            # Missing spider
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('spider', response.data)
        
    def test_job_duration_in_response(self):
        """Test that job duration is included in API response."""
        # Create job with timing
        start_time = timezone.now()
        finish_time = start_time + timedelta(seconds=60)
        job = Job.objects.create(
            spider=self.spider,
            status='done',
            started_at=start_time,
            finished_at=finish_time
        )
        
        self.authenticate()
        
        url = reverse('job-detail', kwargs={'pk': job.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['duration'], 60.0)
        
    def test_job_status_transitions(self):
        """Test typical job status transitions through API."""
        self.authenticate()
        
        # Create a queued job
        job = Job.objects.create(spider=self.spider, status='queued')
        url = reverse('job-detail', kwargs={'pk': job.id})
        
        # Queued -> Running
        data = {
            'status': 'running',
            'started_at': timezone.now().isoformat()
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'running')
        
        # Running -> Done
        data = {
            'status': 'done',
            'finished_at': timezone.now().isoformat(),
            'stats_json': {'pages': 100, 'items': 50}
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'done')
        self.assertEqual(response.data['stats_json']['pages'], 100)