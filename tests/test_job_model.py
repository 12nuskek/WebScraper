"""
Test cases for Job model.
"""

from datetime import datetime, timedelta
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils import timezone

from apps.job.models import Job
from apps.spider.models import Spider
from apps.projects.models import Project
from .test_core import BaseTestCase

User = get_user_model()


class JobModelTest(BaseTestCase):
    """Test cases for Job model."""

    def setUp(self):
        """Set up test data."""
        super().setUp()
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.project = Project.objects.create(
            owner=self.user,
            name='Test Project',
            notes='Test project notes'
        )
        self.spider = Spider.objects.create(
            project=self.project,
            name='test-spider',
            start_urls_json=['https://example.com']
        )

    def test_job_creation(self):
        """Test creating a job."""
        job = Job.objects.create(
            spider=self.spider,
            status='queued'
        )
        
        self.assertEqual(job.spider, self.spider)
        self.assertEqual(job.status, 'queued')
        self.assertIsNone(job.started_at)
        self.assertIsNone(job.finished_at)
        self.assertIsNone(job.stats_json)
        self.assertIsNotNone(job.created_at)
        
    def test_job_str_representation(self):
        """Test job string representation."""
        job = Job.objects.create(
            spider=self.spider,
            status='running'
        )
        expected = f"Job {job.id} ({self.spider.name}) - running"
        self.assertEqual(str(job), expected)
        
    def test_job_status_choices(self):
        """Test job status choices."""
        expected_choices = ['queued', 'running', 'done', 'failed', 'canceled']
        actual_choices = [choice[0] for choice in Job.STATUS_CHOICES]
        self.assertEqual(actual_choices, expected_choices)
        
    def test_job_default_status(self):
        """Test that default status is 'queued'."""
        job = Job.objects.create(spider=self.spider)
        self.assertEqual(job.status, 'queued')
        
    def test_job_with_timing(self):
        """Test job with start and finish times."""
        start_time = timezone.now()
        finish_time = start_time + timedelta(seconds=30)
        
        job = Job.objects.create(
            spider=self.spider,
            status='done',
            started_at=start_time,
            finished_at=finish_time
        )
        
        self.assertEqual(job.started_at, start_time)
        self.assertEqual(job.finished_at, finish_time)
        
    def test_job_duration_property(self):
        """Test job duration calculation."""
        start_time = timezone.now()
        finish_time = start_time + timedelta(seconds=45)
        
        job = Job.objects.create(
            spider=self.spider,
            status='done',
            started_at=start_time,
            finished_at=finish_time
        )
        
        self.assertEqual(job.duration, 45.0)
        
    def test_job_duration_none_when_incomplete(self):
        """Test that duration is None when timing is incomplete."""
        # No start or finish time
        job1 = Job.objects.create(spider=self.spider)
        self.assertIsNone(job1.duration)
        
        # Only start time
        job2 = Job.objects.create(
            spider=self.spider,
            started_at=timezone.now()
        )
        self.assertIsNone(job2.duration)
        
        # Only finish time
        job3 = Job.objects.create(
            spider=self.spider,
            finished_at=timezone.now()
        )
        self.assertIsNone(job3.duration)
        
    def test_job_with_stats(self):
        """Test job with statistics JSON."""
        stats = {
            'pages_scraped': 150,
            'items_extracted': 45,
            'errors': 2,
            'warnings': 5
        }
        
        job = Job.objects.create(
            spider=self.spider,
            status='done',
            stats_json=stats
        )
        
        self.assertEqual(job.stats_json, stats)
        
    def test_job_cascade_delete_with_spider(self):
        """Test that jobs are deleted when spider is deleted."""
        job = Job.objects.create(spider=self.spider)
        job_id = job.id
        
        self.spider.delete()
        
        with self.assertRaises(Job.DoesNotExist):
            Job.objects.get(id=job_id)
            
    def test_job_ordering(self):
        """Test that jobs are ordered by created_at descending."""
        job1 = Job.objects.create(spider=self.spider, status='queued')
        job2 = Job.objects.create(spider=self.spider, status='running')
        
        jobs = list(Job.objects.all())
        self.assertEqual(jobs[0], job2)  # Most recent first
        self.assertEqual(jobs[1], job1)
        
    def test_multiple_jobs_same_spider(self):
        """Test that one spider can have multiple jobs."""
        job1 = Job.objects.create(spider=self.spider, status='done')
        job2 = Job.objects.create(spider=self.spider, status='queued')
        
        self.assertEqual(self.spider.jobs.count(), 2)
        self.assertIn(job1, self.spider.jobs.all())
        self.assertIn(job2, self.spider.jobs.all())
        
    def test_job_status_transitions(self):
        """Test typical job status transitions."""
        job = Job.objects.create(spider=self.spider, status='queued')
        
        # Queued -> Running
        job.status = 'running'
        job.started_at = timezone.now()
        job.save()
        self.assertEqual(job.status, 'running')
        
        # Running -> Done
        job.status = 'done'
        job.finished_at = timezone.now()
        job.save()
        self.assertEqual(job.status, 'done')
        
    def test_job_model_indexes(self):
        """Test that proper database indexes exist."""
        # This is more of a structural test
        indexes = Job._meta.indexes
        self.assertTrue(len(indexes) > 0)
        
        # Check that spider+status index exists
        spider_status_index = None
        for index in indexes:
            if 'spider' in index.fields and 'status' in index.fields:
                spider_status_index = index
                break
                
        self.assertIsNotNone(spider_status_index)