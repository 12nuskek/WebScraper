"""
Tests for Job views.

This module contains tests for job-related views including
JobViewSet, authentication, permissions, and job management functionality.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from apps.projects.models import Project
from apps.scraper.models import Spider
from apps.jobs.models import Job
from apps.jobs.views import JobViewSet
from .test_core import BaseTestCase

User = get_user_model()


class JobViewSetTestCase(BaseTestCase, APITestCase):
    """Tests for the JobViewSet."""
    
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
            start_urls_json=['https://example1.com']
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
        
        # Create test jobs
        now = timezone.now()
        self.job1 = Job.objects.create(
            spider=self.spider1,
            status='done',
            started_at=now - timedelta(minutes=10),
            finished_at=now - timedelta(minutes=5),
            stats_json={
                'items_scraped': 100,
                'pages_crawled': 20
            }
        )
        self.job2 = Job.objects.create(
            spider=self.spider1,
            status='running',
            started_at=now - timedelta(minutes=2)
        )
        self.job3 = Job.objects.create(
            spider=self.spider2,
            status='queued'
        )
        self.job4 = Job.objects.create(
            spider=self.spider3,
            status='failed',
            started_at=now - timedelta(minutes=5),
            finished_at=now - timedelta(minutes=3),
            stats_json={
                'items_scraped': 10,
                'error_count': 5
            }
        )
        
        # API endpoints
        self.job_list_url = '/jobs/'
        self.job_detail_url = lambda pk: f'/jobs/{pk}/'
    
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
        # List jobs
        response = self.client.get(self.job_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Create job
        data = {
            'spider': self.spider1.id,
            'status': 'queued'
        }
        response = self.client.post(self.job_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Get job detail
        response = self.client.get(self.job_detail_url(self.job1.id))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_list_jobs_authenticated(self):
        """Test listing jobs for authenticated user."""
        self.authenticate_user(self.user1)
        
        response = self.client.get(self.job_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should only see user1's jobs (job1, job2, job3)
        data = response.json()
        self.assertEqual(data['count'], 3)
        
        job_ids = [job['id'] for job in data['results']]
        self.assertIn(self.job1.id, job_ids)
        self.assertIn(self.job2.id, job_ids)
        self.assertIn(self.job3.id, job_ids)
        self.assertNotIn(self.job4.id, job_ids)  # Belongs to user2
    
    def test_list_jobs_user_isolation(self):
        """Test that users only see jobs from their own spiders."""
        # Test user1 sees only their jobs
        self.authenticate_user(self.user1)
        response = self.client.get(self.job_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user1_jobs = response.json()['results']
        self.assertEqual(len(user1_jobs), 3)
        
        # Test user2 sees only their jobs
        self.authenticate_user(self.user2)
        response = self.client.get(self.job_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user2_jobs = response.json()['results']
        self.assertEqual(len(user2_jobs), 1)
        self.assertEqual(user2_jobs[0]['id'], self.job4.id)
    
    def test_get_job_detail(self):
        """Test getting job detail."""
        self.authenticate_user(self.user1)
        
        response = self.client.get(self.job_detail_url(self.job1.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        self.assertEqual(data['id'], self.job1.id)
        self.assertEqual(data['spider'], self.spider1.id)
        self.assertEqual(data['status'], 'done')
        self.assertIsNotNone(data['started_at'])
        self.assertIsNotNone(data['finished_at'])
        self.assertEqual(data['stats_json']['items_scraped'], 100)
        self.assertIsNotNone(data['duration'])
    
    def test_get_job_detail_permission_denied(self):
        """Test that users cannot access other users' jobs."""
        self.authenticate_user(self.user1)
        
        # Try to access user2's job
        response = self.client.get(self.job_detail_url(self.job4.id))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_create_job(self):
        """Test creating a new job."""
        self.authenticate_user(self.user1)
        
        data = {
            'spider': self.spider1.id,
            'status': 'queued'
        }
        
        response = self.client.post(self.job_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify job was created
        created_job = Job.objects.get(id=response.json()['id'])
        self.assertEqual(created_job.spider, self.spider1)
        self.assertEqual(created_job.status, 'queued')
        self.assertIsNone(created_job.started_at)
        self.assertIsNone(created_job.finished_at)
        self.assertIsNone(created_job.stats_json)
        
        # Verify response data
        response_data = response.json()
        self.assertEqual(response_data['spider'], self.spider1.id)
        self.assertEqual(response_data['status'], 'queued')
    
    def test_create_job_with_full_data(self):
        """Test creating job with complete data."""
        self.authenticate_user(self.user1)
        
        now = timezone.now()
        data = {
            'spider': self.spider2.id,
            'status': 'done',
            'started_at': (now - timedelta(minutes=5)).isoformat(),
            'finished_at': now.isoformat(),
            'stats_json': {
                'items_scraped': 75,
                'pages_crawled': 15,
                'duration_seconds': 300,
                'success_rate': 96.5
            }
        }
        
        response = self.client.post(self.job_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        created_job = Job.objects.get(id=response.json()['id'])
        self.assertEqual(created_job.spider, self.spider2)
        self.assertEqual(created_job.status, 'done')
        self.assertIsNotNone(created_job.started_at)
        self.assertIsNotNone(created_job.finished_at)
        self.assertEqual(created_job.stats_json['items_scraped'], 75)
        self.assertEqual(created_job.stats_json['success_rate'], 96.5)
    
    def test_create_job_invalid_spider(self):
        """Test creating job with invalid spider ID."""
        self.authenticate_user(self.user1)
        
        data = {
            'spider': 99999,  # Non-existent spider
            'status': 'queued'
        }
        
        response = self.client.post(self.job_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('spider', response.json())
    
    def test_create_job_other_users_spider(self):
        """Test creating job for another user's spider."""
        self.authenticate_user(self.user1)
        
        data = {
            'spider': self.spider3.id,  # User2's spider
            'status': 'queued'
        }
        
        response = self.client.post(self.job_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_create_job_invalid_status(self):
        """Test creating job with invalid status."""
        self.authenticate_user(self.user1)
        
        data = {
            'spider': self.spider1.id,
            'status': 'invalid_status'
        }
        
        response = self.client.post(self.job_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('status', response.json())
    
    def test_update_job_put(self):
        """Test updating job with PUT (full update)."""
        self.authenticate_user(self.user1)
        
        now = timezone.now()
        data = {
            'spider': self.spider1.id,
            'status': 'running',
            'started_at': now.isoformat(),
            'stats_json': {
                'items_scraped': 25,
                'pages_crawled': 5,
                'current_url': 'https://example.com/page5'
            }
        }
        
        response = self.client.put(
            self.job_detail_url(self.job3.id),  # Use queued job
            data, 
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify job was updated
        updated_job = Job.objects.get(id=self.job3.id)
        self.assertEqual(updated_job.status, 'running')
        self.assertIsNotNone(updated_job.started_at)
        self.assertEqual(updated_job.stats_json['items_scraped'], 25)
        self.assertEqual(updated_job.stats_json['current_url'], 'https://example.com/page5')
    
    def test_update_job_patch(self):
        """Test updating job with PATCH (partial update)."""
        self.authenticate_user(self.user1)
        
        now = timezone.now()
        data = {
            'status': 'done',
            'finished_at': now.isoformat(),
            'stats_json': {
                'items_scraped': 150,
                'final_status': 'completed'
            }
        }
        
        response = self.client.patch(
            self.job_detail_url(self.job2.id),  # Use running job
            data, 
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify only specified fields were updated
        updated_job = Job.objects.get(id=self.job2.id)
        self.assertEqual(updated_job.status, 'done')
        self.assertIsNotNone(updated_job.finished_at)
        self.assertEqual(updated_job.stats_json['items_scraped'], 150)
        self.assertEqual(updated_job.stats_json['final_status'], 'completed')
        
        # Other fields should remain unchanged
        self.assertEqual(updated_job.spider, self.spider1)
        self.assertIsNotNone(updated_job.started_at)  # Should still have original start time
    
    def test_update_job_permission_denied(self):
        """Test updating another user's job is denied."""
        self.authenticate_user(self.user1)
        
        data = {'status': 'canceled'}
        
        response = self.client.patch(
            self.job_detail_url(self.job4.id),  # User2's job
            data, 
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_delete_job(self):
        """Test deleting a job."""
        self.authenticate_user(self.user1)
        
        job_id = self.job3.id
        self.assertTrue(Job.objects.filter(id=job_id).exists())
        
        response = self.client.delete(self.job_detail_url(job_id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify job was deleted
        self.assertFalse(Job.objects.filter(id=job_id).exists())
    
    def test_delete_job_permission_denied(self):
        """Test deleting another user's job is denied."""
        self.authenticate_user(self.user1)
        
        job_id = self.job4.id
        self.assertTrue(Job.objects.filter(id=job_id).exists())
        
        response = self.client.delete(self.job_detail_url(job_id))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
        # Verify job was not deleted
        self.assertTrue(Job.objects.filter(id=job_id).exists())
    
    def test_job_ordering(self):
        """Test that jobs are returned in correct order (newest first)."""
        self.authenticate_user(self.user1)
        
        # Create additional job to test ordering
        job_new = Job.objects.create(
            spider=self.spider1,
            status='queued'
        )
        
        response = self.client.get(self.job_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        jobs = response.json()['results']
        # Should be ordered by created_at descending (newest first)
        self.assertEqual(jobs[0]['id'], job_new.id)
    
    def test_job_list_pagination(self):
        """Test job list pagination."""
        self.authenticate_user(self.user1)
        
        # Create many jobs to test pagination
        for i in range(25):
            Job.objects.create(
                spider=self.spider1,
                status='done' if i % 2 == 0 else 'queued'
            )
        
        response = self.client.get(self.job_list_url)
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
        self.assertEqual(len(page2_data['results']), 8)  # Remaining jobs (25 + 3 original)
    
    def test_job_viewset_queryset_filtering(self):
        """Test that viewset properly filters jobs by user ownership."""
        viewset = JobViewSet()
        
        # Mock request with user1
        class MockRequest:
            def __init__(self, user):
                self.user = user
        
        viewset.request = MockRequest(self.user1)
        queryset = viewset.get_queryset()
        
        # Should only include jobs from spiders in projects owned by user1
        job_ids = [job.id for job in queryset]
        self.assertIn(self.job1.id, job_ids)
        self.assertIn(self.job2.id, job_ids)
        self.assertIn(self.job3.id, job_ids)
        self.assertNotIn(self.job4.id, job_ids)  # Owned by user2
    
    def test_job_status_filtering(self):
        """Test filtering jobs by status."""
        self.authenticate_user(self.user1)
        
        # Filter for running jobs
        response = self.client.get(f'{self.job_list_url}?status=running')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Note: DRF doesn't have built-in filtering, but this tests the endpoint structure
        # In a real implementation, you might add django-filter for query filtering
    
    def test_job_creation_with_perform_create(self):
        """Test that perform_create properly sets the spider."""
        self.authenticate_user(self.user1)
        
        data = {
            'spider': self.spider2.id,
            'status': 'queued'
        }
        
        response = self.client.post(self.job_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        job = Job.objects.get(id=response.json()['id'])
        self.assertEqual(job.spider, self.spider2)
    
    def test_job_lifecycle_simulation_via_api(self):
        """Test complete job lifecycle through API calls."""
        self.authenticate_user(self.user1)
        
        # 1. Create job in queued state
        create_data = {
            'spider': self.spider1.id,
            'status': 'queued'
        }
        
        response = self.client.post(self.job_list_url, create_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        job_id = response.json()['id']
        
        # 2. Start the job
        now = timezone.now()
        start_data = {
            'status': 'running',
            'started_at': now.isoformat(),
            'stats_json': {
                'items_scraped': 0,
                'pages_crawled': 0,
                'start_time': now.isoformat()
            }
        }
        
        response = self.client.patch(
            self.job_detail_url(job_id),
            start_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 3. Update job progress
        progress_data = {
            'stats_json': {
                'items_scraped': 50,
                'pages_crawled': 10,
                'current_url': 'https://example.com/page10'
            }
        }
        
        response = self.client.patch(
            self.job_detail_url(job_id),
            progress_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 4. Complete the job
        end_time = now + timedelta(minutes=10)
        complete_data = {
            'status': 'done',
            'finished_at': end_time.isoformat(),
            'stats_json': {
                'items_scraped': 200,
                'pages_crawled': 25,
                'duration_seconds': 600,
                'success_rate': 98.5,
                'final_status': 'completed'
            }
        }
        
        response = self.client.patch(
            self.job_detail_url(job_id),
            complete_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 5. Verify final state
        response = self.client.get(self.job_detail_url(job_id))
        final_job = response.json()
        
        self.assertEqual(final_job['status'], 'done')
        self.assertIsNotNone(final_job['started_at'])
        self.assertIsNotNone(final_job['finished_at'])
        self.assertEqual(final_job['stats_json']['items_scraped'], 200)
        self.assertEqual(final_job['stats_json']['success_rate'], 98.5)
        self.assertIsNotNone(final_job['duration'])
    
    def test_job_error_handling(self):
        """Test API error handling for various scenarios."""
        self.authenticate_user(self.user1)
        
        # Test missing required field
        data = {
            'status': 'queued'
            # Missing spider
        }
        response = self.client.post(self.job_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('spider', response.json())
        
        # Test accessing non-existent job
        response = self.client.get(self.job_detail_url(99999))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_job_api_with_realistic_data(self):
        """Test job API with realistic web scraping job data."""
        self.authenticate_user(self.user1)
        
        realistic_data = {
            'spider': self.spider1.id,
            'status': 'done',
            'started_at': timezone.now() - timedelta(minutes=30),
            'finished_at': timezone.now(),
            'stats_json': {
                'execution_info': {
                    'spider_name': 'ecommerce-products',
                    'job_id': 'job_12345',
                    'start_reason': 'manual'
                },
                'crawl_stats': {
                    'items_scraped': 1247,
                    'pages_crawled': 156,
                    'requests_made': 178,
                    'response_received': 173,
                    'duplicate_filtered': 23,
                    'item_dropped': 8
                },
                'timing': {
                    'duration_seconds': 1800,
                    'avg_request_time': 1.2,
                    'max_request_time': 8.5,
                    'min_request_time': 0.3
                },
                'data_transfer': {
                    'bytes_downloaded': 52428800,  # ~50MB
                    'bytes_uploaded': 102400,     # ~100KB
                    'avg_page_size': 337408       # ~329KB
                },
                'errors_and_warnings': {
                    'total_errors': 5,
                    'timeout_errors': 2,
                    'http_errors': {'404': 2, '500': 1},
                    'parsing_errors': 0,
                    'warnings': 12
                },
                'final_status': {
                    'success_rate': 96.8,
                    'completion_status': 'finished',
                    'memory_usage_mb': 145.2,
                    'cpu_time_seconds': 89.4
                }
            }
        }
        
        # Create job
        response = self.client.post(self.job_list_url, realistic_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify created job
        job = Job.objects.get(id=response.json()['id'])
        self.assertEqual(job.spider, self.spider1)
        self.assertEqual(job.status, 'done')
        self.assertEqual(job.stats_json['crawl_stats']['items_scraped'], 1247)
        self.assertEqual(job.stats_json['timing']['duration_seconds'], 1800)
        self.assertEqual(job.stats_json['final_status']['success_rate'], 96.8)
        
        # Test retrieving the job
        response = self.client.get(self.job_detail_url(job.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        self.assertIn('execution_info', data['stats_json'])
        self.assertIn('crawl_stats', data['stats_json'])
        self.assertIn('timing', data['stats_json'])