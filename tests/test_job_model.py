"""
Tests for Job model.

This module contains tests for the Job model including
relationships with Spider and Project, status management, and job lifecycle.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import timedelta
from apps.projects.models import Project
from apps.scraper.models import Spider
from apps.jobs.models import Job
from .test_core import BaseTestCase

User = get_user_model()


class JobModelTestCase(BaseTestCase):
    """Tests for the Job model."""
    
    def setUp(self):
        """Set up test data."""
        super().setUp()
        self.user = self.create_user()
        self.user2 = self.create_user(email='user2@example.com')
        
        # Create test projects
        self.project = Project.objects.create(
            owner=self.user,
            name='Test Project',
            notes='Test project for job tests'
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
    
    def test_job_creation(self):
        """Test basic job creation."""
        job = Job.objects.create(spider=self.spider)
        
        self.assertIsInstance(job, Job)
        self.assertEqual(job.spider, self.spider)
        self.assertEqual(job.status, 'queued')  # Default status
        self.assertIsNone(job.started_at)
        self.assertIsNone(job.finished_at)
        self.assertIsNone(job.stats_json)
        self.assertIsNotNone(job.created_at)
        self.assertFalse(job.is_running())
        self.assertFalse(job.is_completed())
    
    def test_job_creation_with_all_fields(self):
        """Test job creation with all fields specified."""
        now = timezone.now()
        finished_time = now + timedelta(minutes=5)
        
        job_data = {
            'spider': self.spider,
            'status': 'done',
            'started_at': now,
            'finished_at': finished_time,
            'stats_json': {
                'items_scraped': 150,
                'pages_crawled': 25,
                'duration_seconds': 300,
                'errors': 2,
                'warnings': 5,
                'bytes_downloaded': 2048000
            }
        }
        job = Job.objects.create(**job_data)
        
        self.assertEqual(job.spider, self.spider)
        self.assertEqual(job.status, 'done')
        self.assertEqual(job.started_at, now)
        self.assertEqual(job.finished_at, finished_time)
        self.assertEqual(job.stats_json['items_scraped'], 150)
        self.assertEqual(job.stats_json['pages_crawled'], 25)
        self.assertTrue(job.is_completed())
        self.assertFalse(job.is_running())
    
    def test_job_string_representation(self):
        """Test job __str__ method."""
        job = Job.objects.create(spider=self.spider, status='running')
        expected_str = f"Job #{job.id} - test-spider (running)"
        self.assertEqual(str(job), expected_str)
    
    def test_job_spider_relationship(self):
        """Test the relationship between Job and Spider."""
        job = Job.objects.create(spider=self.spider)
        
        # Test forward relationship
        self.assertEqual(job.spider, self.spider)
        
        # Test reverse relationship
        self.assertIn(job, self.spider.jobs.all())
        self.assertEqual(self.spider.jobs.count(), 1)
    
    def test_job_status_choices(self):
        """Test all valid job status choices."""
        statuses = ['queued', 'running', 'done', 'failed', 'canceled']
        
        for status in statuses:
            job = Job.objects.create(spider=self.spider, status=status)
            self.assertEqual(job.status, status)
            # Clean up for next iteration
            job.delete()
    
    def test_job_cascade_delete_with_spider(self):
        """Test that jobs are deleted when their spider is deleted."""
        job = Job.objects.create(spider=self.spider)
        job_id = job.id
        
        self.assertTrue(Job.objects.filter(id=job_id).exists())
        
        # Delete the spider
        self.spider.delete()
        
        # Job should also be deleted due to CASCADE
        self.assertFalse(Job.objects.filter(id=job_id).exists())
    
    def test_job_ordering(self):
        """Test that jobs are ordered by creation time (newest first)."""
        job1 = Job.objects.create(spider=self.spider, status='done')
        job2 = Job.objects.create(spider=self.spider, status='running')
        job3 = Job.objects.create(spider=self.spider, status='queued')
        
        jobs = list(Job.objects.all())
        
        # Should be ordered by created_at descending (newest first)
        self.assertEqual(jobs[0], job3)  # Most recent
        self.assertEqual(jobs[1], job2)
        self.assertEqual(jobs[2], job1)  # Oldest
    
    def test_job_duration_property(self):
        """Test the duration property calculation."""
        now = timezone.now()
        
        # Job without start/finish times
        job1 = Job.objects.create(spider=self.spider)
        self.assertIsNone(job1.duration)
        
        # Job with only start time
        job2 = Job.objects.create(spider=self.spider, started_at=now)
        self.assertIsNone(job2.duration)
        
        # Job with both start and finish times
        finished_time = now + timedelta(minutes=10)
        job3 = Job.objects.create(
            spider=self.spider,
            started_at=now,
            finished_at=finished_time
        )
        expected_duration = timedelta(minutes=10)
        self.assertEqual(job3.duration, expected_duration)
    
    def test_job_is_running_method(self):
        """Test the is_running method."""
        statuses_and_expected = [
            ('queued', False),
            ('running', True),
            ('done', False),
            ('failed', False),
            ('canceled', False),
        ]
        
        for status, expected in statuses_and_expected:
            job = Job.objects.create(spider=self.spider, status=status)
            self.assertEqual(job.is_running(), expected, f"Status '{status}' should return {expected}")
            job.delete()
    
    def test_job_is_completed_method(self):
        """Test the is_completed method."""
        statuses_and_expected = [
            ('queued', False),
            ('running', False),
            ('done', True),
            ('failed', True),
            ('canceled', True),
        ]
        
        for status, expected in statuses_and_expected:
            job = Job.objects.create(spider=self.spider, status=status)
            self.assertEqual(job.is_completed(), expected, f"Status '{status}' should return {expected}")
            job.delete()
    
    def test_job_stats_json_field(self):
        """Test that stats_json field accepts various data types."""
        stats_data = {
            'basic_counters': {
                'items_scraped': 100,
                'pages_crawled': 20,
                'errors': 5
            },
            'timing': {
                'start_time': '2025-01-01T00:00:00Z',
                'end_time': '2025-01-01T01:00:00Z',
                'duration_seconds': 3600
            },
            'data_size': {
                'bytes_downloaded': 5242880,
                'files_saved': 50
            },
            'performance': {
                'avg_response_time': 1.5,
                'requests_per_second': 2.3,
                'success_rate': 95.5
            },
            'flags': {
                'respect_robots_txt': True,
                'use_cache': False,
                'enable_js': None
            },
            'error_details': [
                {'url': 'https://example.com/error1', 'status': 404},
                {'url': 'https://example.com/error2', 'status': 500}
            ]
        }
        
        job = Job.objects.create(spider=self.spider, stats_json=stats_data)
        
        # Verify data can be retrieved correctly
        retrieved_job = Job.objects.get(id=job.id)
        self.assertEqual(retrieved_job.stats_json['basic_counters']['items_scraped'], 100)
        self.assertEqual(retrieved_job.stats_json['timing']['duration_seconds'], 3600)
        self.assertEqual(retrieved_job.stats_json['performance']['avg_response_time'], 1.5)
        self.assertTrue(retrieved_job.stats_json['flags']['respect_robots_txt'])
        self.assertIsNone(retrieved_job.stats_json['flags']['enable_js'])
        self.assertEqual(len(retrieved_job.stats_json['error_details']), 2)
    
    def test_job_model_meta_properties(self):
        """Test Job model Meta properties."""
        meta = Job._meta
        
        # Test ordering
        self.assertEqual(meta.ordering, ('-created_at',))
        
        # Test indexes - should have spider+status index
        index_names = [index.name for index in meta.indexes]
        self.assertIn('idx_job_spider_status', index_names)
        
        # Verify the index fields
        spider_status_index = next(
            index for index in meta.indexes 
            if index.name == 'idx_job_spider_status'
        )
        self.assertEqual(spider_status_index.fields, ['spider', 'status'])
    
    def test_job_required_fields(self):
        """Test that required fields are enforced."""
        from django.db import transaction
        
        # Test missing spider - should raise IntegrityError due to NOT NULL constraint
        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                Job.objects.create(status='queued')
    
    def test_job_empty_stats_json(self):
        """Test job creation with empty stats_json."""
        job = Job.objects.create(spider=self.spider, stats_json={})
        self.assertEqual(job.stats_json, {})
        
        job2 = Job.objects.create(spider=self.spider, stats_json=[])
        self.assertEqual(job2.stats_json, [])
    
    def test_job_lifecycle_simulation(self):
        """Test a complete job lifecycle."""
        # Create job in queued state
        job = Job.objects.create(spider=self.spider)
        self.assertEqual(job.status, 'queued')
        self.assertFalse(job.is_running())
        self.assertFalse(job.is_completed())
        
        # Start the job
        start_time = timezone.now()
        job.status = 'running'
        job.started_at = start_time
        job.save()
        
        self.assertTrue(job.is_running())
        self.assertFalse(job.is_completed())
        self.assertEqual(job.started_at, start_time)
        
        # Complete the job
        end_time = start_time + timedelta(minutes=5)
        job.status = 'done'
        job.finished_at = end_time
        job.stats_json = {
            'items_scraped': 50,
            'duration_seconds': 300,
            'success': True
        }
        job.save()
        
        self.assertFalse(job.is_running())
        self.assertTrue(job.is_completed())
        self.assertEqual(job.finished_at, end_time)
        self.assertIsNotNone(job.duration)
        self.assertEqual(job.duration, timedelta(minutes=5))
        self.assertEqual(job.stats_json['items_scraped'], 50)
    
    def test_job_failure_scenario(self):
        """Test job failure scenario with error stats."""
        start_time = timezone.now()
        end_time = start_time + timedelta(minutes=2)
        error_stats = {
            'items_scraped': 10,
            'error_count': 5,
            'last_error': 'Connection timeout',
            'failed_urls': [
                'https://example.com/page1',
                'https://example.com/page2'
            ],
            'partial_success': True
        }
        
        job = Job.objects.create(
            spider=self.spider,
            status='failed',
            started_at=start_time,
            finished_at=end_time,
            stats_json=error_stats
        )
        
        self.assertEqual(job.status, 'failed')
        self.assertTrue(job.is_completed())
        self.assertFalse(job.is_running())
        self.assertEqual(job.stats_json['error_count'], 5)
        self.assertEqual(job.stats_json['last_error'], 'Connection timeout')
        self.assertEqual(len(job.stats_json['failed_urls']), 2)
    
    def test_multiple_jobs_per_spider(self):
        """Test that a spider can have multiple jobs."""
        # Create multiple jobs for the same spider
        job1 = Job.objects.create(spider=self.spider, status='done')
        job2 = Job.objects.create(spider=self.spider, status='running')
        job3 = Job.objects.create(spider=self.spider, status='queued')
        
        # Verify all jobs are associated with the spider
        spider_jobs = self.spider.jobs.all()
        self.assertEqual(spider_jobs.count(), 3)
        self.assertIn(job1, spider_jobs)
        self.assertIn(job2, spider_jobs)
        self.assertIn(job3, spider_jobs)
        
        # Verify jobs are ordered correctly (newest first)
        ordered_jobs = list(spider_jobs)
        self.assertEqual(ordered_jobs[0], job3)  # Most recent
        self.assertEqual(ordered_jobs[1], job2)
        self.assertEqual(ordered_jobs[2], job1)  # Oldest
    
    def test_job_realistic_stats_example(self):
        """Test job with realistic web scraping statistics."""
        realistic_stats = {
            'execution': {
                'start_timestamp': '2025-01-15T10:00:00Z',
                'end_timestamp': '2025-01-15T10:15:30Z',
                'duration_seconds': 930,
                'spider_name': 'ecommerce-products'
            },
            'requests': {
                'total_requests': 245,
                'successful_requests': 235,
                'failed_requests': 10,
                'retry_requests': 15,
                'avg_response_time_ms': 850,
                'max_response_time_ms': 3200,
                'min_response_time_ms': 120
            },
            'items': {
                'total_items_scraped': 189,
                'valid_items': 185,
                'invalid_items': 4,
                'duplicate_items': 12,
                'items_per_minute': 12.2
            },
            'data_transfer': {
                'bytes_downloaded': 15728640,  # ~15MB
                'bytes_uploaded': 51200,      # ~50KB
                'total_response_size': 14680064,
                'avg_page_size_kb': 62.4
            },
            'errors': {
                'timeout_errors': 3,
                'connection_errors': 2,
                'http_errors': {
                    '404': 3,
                    '500': 1,
                    '503': 1
                },
                'parsing_errors': 4,
                'validation_errors': 4
            },
            'performance': {
                'concurrent_requests': 8,
                'download_delay': 1.5,
                'memory_usage_mb': 127.5,
                'cpu_usage_percent': 23.8
            },
            'coverage': {
                'unique_domains': 1,
                'unique_pages': 235,
                'depth_reached': 4,
                'links_followed': 189,
                'links_filtered': 56
            }
        }
        
        job = Job.objects.create(
            spider=self.spider,
            status='done',
            started_at=timezone.now() - timedelta(minutes=15, seconds=30),
            finished_at=timezone.now(),
            stats_json=realistic_stats
        )
        
        # Verify the complex stats are stored and retrieved correctly
        self.assertEqual(job.stats_json['requests']['total_requests'], 245)
        self.assertEqual(job.stats_json['items']['total_items_scraped'], 189)
        self.assertEqual(job.stats_json['errors']['http_errors']['404'], 3)
        self.assertEqual(job.stats_json['performance']['concurrent_requests'], 8)
        self.assertEqual(job.stats_json['coverage']['unique_domains'], 1)
        
        # Verify derived values make sense
        self.assertTrue(job.is_completed())
        self.assertEqual(job.status, 'done')
        self.assertIsNotNone(job.duration)