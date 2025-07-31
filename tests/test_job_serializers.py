"""
Test cases for Job serializers.
"""

from datetime import timedelta
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import serializers

from apps.job.models import Job
from apps.job.serializers import JobSerializer
from apps.spider.models import Spider
from apps.projects.models import Project
from .test_core import BaseTestCase

User = get_user_model()


class JobSerializerTest(BaseTestCase):
    """Test cases for JobSerializer."""

    def setUp(self):
        """Set up test data."""
        super().setUp()
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

    def get_context(self, user=None):
        """Helper to create request context."""
        if user is None:
            user = self.user
        
        class MockRequest:
            def __init__(self, user):
                self.user = user
                
        return {'request': MockRequest(user)}

    def test_job_serializer_valid_data(self):
        """Test JobSerializer with valid data."""
        data = {
            'spider': self.spider.id,
            'status': 'queued'
        }
        
        serializer = JobSerializer(data=data, context=self.get_context())
        self.assertTrue(serializer.is_valid())
        
        job = serializer.save()
        self.assertEqual(job.spider, self.spider)
        self.assertEqual(job.status, 'queued')
        
    def test_job_serializer_with_timing_and_stats(self):
        """Test JobSerializer with complete data."""
        start_time = timezone.now()
        finish_time = start_time + timedelta(seconds=30)
        stats = {'pages': 10, 'items': 5}
        
        data = {
            'spider': self.spider.id,
            'status': 'done',
            'started_at': start_time.isoformat(),
            'finished_at': finish_time.isoformat(),
            'stats_json': stats
        }
        
        serializer = JobSerializer(data=data, context=self.get_context())
        self.assertTrue(serializer.is_valid())
        
        job = serializer.save()
        self.assertEqual(job.status, 'done')
        self.assertEqual(job.stats_json, stats)
        
    def test_job_serializer_missing_required_fields(self):
        """Test JobSerializer with missing required fields."""
        # Missing spider
        data = {'status': 'queued'}
        serializer = JobSerializer(data=data, context=self.get_context())
        self.assertFalse(serializer.is_valid())
        self.assertIn('spider', serializer.errors)
        
    def test_job_serializer_invalid_spider(self):
        """Test JobSerializer with invalid spider ID."""
        data = {
            'spider': 99999,  # Non-existent spider
            'status': 'queued'
        }
        
        serializer = JobSerializer(data=data, context=self.get_context())
        self.assertFalse(serializer.is_valid())
        self.assertIn('spider', serializer.errors)
        
    def test_job_serializer_other_users_spider(self):
        """Test JobSerializer validates spider ownership."""
        data = {
            'spider': self.other_spider.id,  # Other user's spider
            'status': 'queued'
        }
        
        serializer = JobSerializer(data=data, context=self.get_context(self.user))
        self.assertFalse(serializer.is_valid())
        self.assertIn('spider', serializer.errors)
        self.assertIn('your own spiders', str(serializer.errors['spider'][0]))
        
    def test_job_serializer_read_only_fields(self):
        """Test that read-only fields are properly handled."""
        job = Job.objects.create(
            spider=self.spider,
            status='done',
            started_at=timezone.now(),
            finished_at=timezone.now() + timedelta(seconds=30)
        )
        
        serializer = JobSerializer(job)
        data = serializer.data
        
        # Check that read-only fields are included in serialized data
        self.assertIn('id', data)
        self.assertIn('created_at', data)
        self.assertIn('duration', data)
        
        # Duration should be calculated
        self.assertIsNotNone(data['duration'])
        
    def test_job_serializer_duration_calculation(self):
        """Test that duration is properly calculated and serialized."""
        start_time = timezone.now()
        finish_time = start_time + timedelta(seconds=45)
        
        job = Job.objects.create(
            spider=self.spider,
            status='done',
            started_at=start_time,
            finished_at=finish_time
        )
        
        serializer = JobSerializer(job)
        self.assertEqual(serializer.data['duration'], 45.0)
        
    def test_job_serializer_duration_none(self):
        """Test duration is None when timing is incomplete."""
        job = Job.objects.create(spider=self.spider, status='queued')
        
        serializer = JobSerializer(job)
        self.assertIsNone(serializer.data['duration'])
        
    def test_job_serializer_update(self):
        """Test updating a job through serializer."""
        job = Job.objects.create(
            spider=self.spider,
            status='queued'
        )
        
        update_data = {
            'status': 'running',
            'started_at': timezone.now().isoformat()
        }
        
        serializer = JobSerializer(job, data=update_data, partial=True)
        self.assertTrue(serializer.is_valid())
        
        updated_job = serializer.save()
        self.assertEqual(updated_job.status, 'running')
        self.assertIsNotNone(updated_job.started_at)
        
    def test_job_serializer_invalid_status(self):
        """Test JobSerializer with invalid status."""
        data = {
            'spider': self.spider.id,
            'status': 'invalid_status'
        }
        
        serializer = JobSerializer(data=data, context=self.get_context())
        self.assertFalse(serializer.is_valid())
        self.assertIn('status', serializer.errors)
        
    def test_job_serializer_json_stats(self):
        """Test JobSerializer handles complex JSON stats."""
        stats = {
            'scraped': {
                'pages': 100,
                'items': 250
            },
            'errors': {
                'http_errors': 5,
                'parse_errors': 2
            },
            'timing': {
                'avg_response_time': 1.5,
                'total_time': 300
            }
        }
        
        data = {
            'spider': self.spider.id,
            'status': 'done',
            'stats_json': stats
        }
        
        serializer = JobSerializer(data=data, context=self.get_context())
        self.assertTrue(serializer.is_valid())
        
        job = serializer.save()
        self.assertEqual(job.stats_json, stats)
        
        # Test serialization back
        serializer = JobSerializer(job)
        self.assertEqual(serializer.data['stats_json'], stats)