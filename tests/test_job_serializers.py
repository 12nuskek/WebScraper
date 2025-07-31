"""
Tests for Job serializers.

This module contains tests for job-related serializers including
JobSerializer and its validation, field handling, and functionality.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from rest_framework import serializers
from rest_framework.test import APIRequestFactory
from apps.projects.models import Project
from apps.scraper.models import Spider
from apps.jobs.models import Job
from apps.jobs.serializers import JobSerializer
from .test_core import BaseTestCase

User = get_user_model()


class JobSerializerTestCase(BaseTestCase):
    """Tests for the JobSerializer."""
    
    def setUp(self):
        """Set up test data."""
        super().setUp()
        self.user = self.create_user()
        self.user2 = self.create_user(email='user2@example.com')
        
        # Create test projects
        self.project = Project.objects.create(
            owner=self.user,
            name='Test Project',
            notes='Test project for job serializer tests'
        )
        self.project2 = Project.objects.create(
            owner=self.user2,
            name='Another Project',
            notes='Another test project'
        )
        
        # Create test spiders
        self.spider = Spider.objects.create(
            project=self.project,
            name='test-spider',
            start_urls_json=['https://example.com']
        )
        self.spider2 = Spider.objects.create(
            project=self.project2,
            name='another-spider',
            start_urls_json=['https://another.com']
        )
        
        # Create test job
        now = timezone.now()
        self.job = Job.objects.create(
            spider=self.spider,
            status='done',
            started_at=now - timedelta(minutes=5),
            finished_at=now,
            stats_json={
                'items_scraped': 100,
                'pages_crawled': 20,
                'duration_seconds': 300
            }
        )
        
        # Create request factory for context
        self.factory = APIRequestFactory()
    
    def test_serializer_representation(self):
        """Test serializer representation of job data."""
        serializer = JobSerializer(self.job)
        data = serializer.data
        
        self.assertEqual(data['spider'], self.spider.id)
        self.assertEqual(data['status'], 'done')
        self.assertIsNotNone(data['started_at'])
        self.assertIsNotNone(data['finished_at'])
        self.assertEqual(data['stats_json']['items_scraped'], 100)
        self.assertIn('id', data)
        self.assertIn('created_at', data)
        self.assertIn('duration', data)
        self.assertIsNotNone(data['duration'])
    
    def test_serializer_fields(self):
        """Test that serializer has correct fields."""
        serializer = JobSerializer()
        fields = serializer.fields
        
        expected_fields = {
            'id', 'spider', 'status', 'started_at', 'finished_at', 
            'stats_json', 'created_at', 'duration'
        }
        self.assertEqual(set(fields.keys()), expected_fields)
    
    def test_read_only_fields(self):
        """Test that read-only fields are properly configured."""
        serializer = JobSerializer()
        
        # Check read-only fields
        self.assertTrue(serializer.fields['id'].read_only)
        self.assertTrue(serializer.fields['created_at'].read_only)
        self.assertTrue(serializer.fields['duration'].read_only)
        
        # Check writable fields
        self.assertFalse(serializer.fields['spider'].read_only)
        self.assertFalse(serializer.fields['status'].read_only)
        self.assertFalse(serializer.fields['started_at'].read_only)
        self.assertFalse(serializer.fields['finished_at'].read_only)
        self.assertFalse(serializer.fields['stats_json'].read_only)
    
    def test_valid_serialization_minimal(self):
        """Test serialization with minimal required data."""
        data = {
            'spider': self.spider.id,
            'status': 'queued'
        }
        
        serializer = JobSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        
        job = serializer.save()
        self.assertEqual(job.spider, self.spider)
        self.assertEqual(job.status, 'queued')
        self.assertIsNone(job.started_at)
        self.assertIsNone(job.finished_at)
        self.assertIsNone(job.stats_json)
    
    def test_valid_serialization_complete(self):
        """Test serialization with all fields."""
        now = timezone.now()
        start_time = now - timedelta(minutes=10)
        end_time = now
        
        data = {
            'spider': self.spider.id,
            'status': 'done',
            'started_at': start_time.isoformat(),
            'finished_at': end_time.isoformat(),
            'stats_json': {
                'items_scraped': 50,
                'pages_crawled': 10,
                'errors': 2,
                'duration_seconds': 600
            }
        }
        
        serializer = JobSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        
        job = serializer.save()
        self.assertEqual(job.spider, self.spider)
        self.assertEqual(job.status, 'done')
        self.assertIsNotNone(job.started_at)
        self.assertIsNotNone(job.finished_at)
        self.assertEqual(job.stats_json['items_scraped'], 50)
    
    def test_missing_required_fields(self):
        """Test validation fails when required fields are missing."""
        # Missing spider
        data = {
            'status': 'queued'
        }
        serializer = JobSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('spider', serializer.errors)
        
        # Missing status should use default
        data = {
            'spider': self.spider.id
        }
        serializer = JobSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
    
    def test_invalid_spider_reference(self):
        """Test validation fails with invalid spider ID."""
        data = {
            'spider': 99999,  # Non-existent spider ID
            'status': 'queued'
        }
        
        serializer = JobSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('spider', serializer.errors)
    
    def test_valid_status_choices(self):
        """Test that all valid status choices are accepted."""
        valid_statuses = ['queued', 'running', 'done', 'failed', 'canceled']
        
        for status in valid_statuses:
            data = {
                'spider': self.spider.id,
                'status': status
            }
            serializer = JobSerializer(data=data)
            self.assertTrue(serializer.is_valid(), f"Status '{status}' should be valid: {serializer.errors}")
            
            job = serializer.save()
            self.assertEqual(job.status, status)
            job.delete()  # Clean up for next iteration
    
    def test_invalid_status_choice(self):
        """Test that invalid status choices are rejected."""
        data = {
            'spider': self.spider.id,
            'status': 'invalid_status'
        }
        
        serializer = JobSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('status', serializer.errors)
    
    def test_update_job(self):
        """Test updating an existing job."""
        now = timezone.now()
        new_data = {
            'status': 'running',
            'started_at': now.isoformat(),
            'stats_json': {
                'items_scraped': 25,
                'pages_crawled': 5,
                'current_url': 'https://example.com/page5'
            }
        }
        
        serializer = JobSerializer(self.job, data=new_data, partial=True)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        
        updated_job = serializer.save()
        self.assertEqual(updated_job.status, 'running')
        self.assertIsNotNone(updated_job.started_at)
        self.assertEqual(updated_job.stats_json['items_scraped'], 25)
        self.assertEqual(updated_job.stats_json['current_url'], 'https://example.com/page5')
        
        # Should still be the same job instance
        self.assertEqual(updated_job.id, self.job.id)
        self.assertEqual(updated_job.spider, self.job.spider)
    
    def test_partial_update(self):
        """Test partial update of job."""
        # Update only the status
        serializer = JobSerializer(
            self.job, 
            data={'status': 'failed'}, 
            partial=True
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        
        updated_job = serializer.save()
        self.assertEqual(updated_job.status, 'failed')
        
        # Other fields should remain unchanged
        self.assertEqual(updated_job.spider, self.job.spider)
        self.assertEqual(updated_job.started_at, self.job.started_at)
        self.assertEqual(updated_job.finished_at, self.job.finished_at)
    
    def test_json_field_validation(self):
        """Test that stats_json field accepts valid JSON data."""
        complex_stats = {
            'counters': {
                'items_scraped': 200,
                'pages_crawled': 50,
                'errors': 5,
                'warnings': 10
            },
            'timing': {
                'start_time': '2025-01-01T00:00:00Z',
                'end_time': '2025-01-01T01:00:00Z',
                'duration_seconds': 3600,
                'avg_request_time': 1.5
            },
            'data_transfer': {
                'bytes_downloaded': 10485760,
                'requests_made': 150,
                'avg_page_size': 69905
            },
            'boolean_flags': {
                'completed_successfully': True,
                'had_errors': False,
                'used_cache': None
            },
            'error_list': [
                {'url': 'https://example.com/error1', 'code': 404},
                {'url': 'https://example.com/error2', 'code': 500}
            ]
        }
        
        data = {
            'spider': self.spider.id,
            'status': 'done',
            'stats_json': complex_stats
        }
        
        serializer = JobSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        
        job = serializer.save()
        self.assertEqual(job.stats_json['counters']['items_scraped'], 200)
        self.assertEqual(job.stats_json['timing']['duration_seconds'], 3600)
        self.assertTrue(job.stats_json['boolean_flags']['completed_successfully'])
        self.assertIsNone(job.stats_json['boolean_flags']['used_cache'])
        self.assertEqual(len(job.stats_json['error_list']), 2)
    
    def test_spider_queryset_filtering(self):
        """Test that spider field uses correct queryset."""
        serializer = JobSerializer()
        spider_field = serializer.fields['spider']
        
        # Should be a PrimaryKeyRelatedField with Spider queryset
        self.assertIsInstance(spider_field, serializers.PrimaryKeyRelatedField)
        
        # Get the queryset (it should include all spiders for now)
        queryset = spider_field.get_queryset()
        self.assertIn(self.spider, queryset)
        self.assertIn(self.spider2, queryset)
    
    def test_duration_field_calculation(self):
        """Test that duration field is calculated correctly."""
        now = timezone.now()
        start_time = now - timedelta(minutes=30)
        end_time = now
        
        job_with_duration = Job.objects.create(
            spider=self.spider,
            status='done',
            started_at=start_time,
            finished_at=end_time
        )
        
        serializer = JobSerializer(job_with_duration)
        data = serializer.data
        
        # Duration should be present and represent the time difference
        self.assertIn('duration', data)
        self.assertIsNotNone(data['duration'])
        # Duration should be approximately 30 minutes (1800 seconds)
        # Note: The exact format depends on DurationField serialization
        
        # Test job without duration
        job_without_duration = Job.objects.create(
            spider=self.spider,
            status='queued'
        )
        
        serializer2 = JobSerializer(job_without_duration)
        data2 = serializer2.data
        
        self.assertIn('duration', data2)
        self.assertIsNone(data2['duration'])
    
    def test_serializer_with_null_timestamps(self):
        """Test serializer handles null timestamps correctly."""
        data = {
            'spider': self.spider.id,
            'status': 'queued',
            'started_at': None,
            'finished_at': None,
            'stats_json': None
        }
        
        serializer = JobSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        
        job = serializer.save()
        self.assertIsNone(job.started_at)
        self.assertIsNone(job.finished_at)
        self.assertIsNone(job.stats_json)
    
    def test_serializer_representation_with_none_values(self):
        """Test serializer representation when optional fields are None."""
        minimal_job = Job.objects.create(
            spider=self.spider,
            status='queued'
        )
        
        serializer = JobSerializer(minimal_job)
        data = serializer.data
        
        self.assertEqual(data['status'], 'queued')
        self.assertEqual(data['spider'], self.spider.id)
        self.assertIsNone(data['started_at'])
        self.assertIsNone(data['finished_at'])
        self.assertIsNone(data['stats_json'])
        self.assertIsNone(data['duration'])
    
    def test_serializer_realistic_job_lifecycle(self):
        """Test serializer with realistic job lifecycle data."""
        # Queued job
        queued_data = {
            'spider': self.spider.id,
            'status': 'queued'
        }
        
        serializer = JobSerializer(data=queued_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        job = serializer.save()
        
        # Start the job
        now = timezone.now()
        running_data = {
            'status': 'running',
            'started_at': now.isoformat(),
            'stats_json': {
                'items_scraped': 0,
                'pages_crawled': 0,
                'current_url': 'https://example.com/start',
                'start_time': now.isoformat()
            }
        }
        
        serializer = JobSerializer(job, data=running_data, partial=True)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        job = serializer.save()
        
        # Complete the job
        end_time = now + timedelta(minutes=15)
        completed_data = {
            'status': 'done',
            'finished_at': end_time.isoformat(),
            'stats_json': {
                'items_scraped': 150,
                'pages_crawled': 30,
                'duration_seconds': 900,
                'success_rate': 98.5,
                'errors_encountered': 2,
                'final_status': 'completed_successfully',
                'end_time': end_time.isoformat()
            }
        }
        
        serializer = JobSerializer(job, data=completed_data, partial=True)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        completed_job = serializer.save()
        
        # Verify final state
        self.assertEqual(completed_job.status, 'done')
        self.assertIsNotNone(completed_job.started_at)
        self.assertIsNotNone(completed_job.finished_at)
        self.assertEqual(completed_job.stats_json['items_scraped'], 150)
        self.assertEqual(completed_job.stats_json['pages_crawled'], 30)
        self.assertEqual(completed_job.stats_json['success_rate'], 98.5)
    
    def test_serializer_error_scenarios(self):
        """Test serializer with error scenarios."""
        # Job that failed due to network issues
        error_stats = {
            'items_scraped': 25,
            'pages_crawled': 8,
            'error_type': 'network_timeout',
            'error_message': 'Connection timed out after 30 seconds',
            'failed_urls': [
                'https://example.com/timeout1',
                'https://example.com/timeout2'
            ],
            'recovery_attempted': True,
            'final_error_count': 15
        }
        
        data = {
            'spider': self.spider.id,
            'status': 'failed',
            'started_at': timezone.now().isoformat(),
            'finished_at': (timezone.now() + timedelta(minutes=3)).isoformat(),
            'stats_json': error_stats
        }
        
        serializer = JobSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        
        failed_job = serializer.save()
        self.assertEqual(failed_job.status, 'failed')
        self.assertEqual(failed_job.stats_json['error_type'], 'network_timeout')
        self.assertEqual(failed_job.stats_json['final_error_count'], 15)
        self.assertTrue(failed_job.stats_json['recovery_attempted'])
    
    def test_serializer_validation_edge_cases(self):
        """Test serializer validation with edge cases."""
        # Test with empty stats_json
        data1 = {
            'spider': self.spider.id,
            'status': 'done',
            'stats_json': {}
        }
        serializer1 = JobSerializer(data=data1)
        self.assertTrue(serializer1.is_valid(), serializer1.errors)
        
        # Test with array as stats_json
        data2 = {
            'spider': self.spider.id,
            'status': 'done',
            'stats_json': ['item1', 'item2', 'item3']
        }
        serializer2 = JobSerializer(data=data2)
        self.assertTrue(serializer2.is_valid(), serializer2.errors)
        
        # Test with very large stats_json
        large_stats = {f'key_{i}': f'value_{i}' for i in range(1000)}
        data3 = {
            'spider': self.spider.id,
            'status': 'done',
            'stats_json': large_stats
        }
        serializer3 = JobSerializer(data=data3)
        self.assertTrue(serializer3.is_valid(), serializer3.errors)