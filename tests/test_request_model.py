"""
Test cases for RequestQueue model.
"""

import hashlib
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils import timezone

from apps.request.models import RequestQueue
from apps.job.models import Job
from apps.spider.models import Spider
from apps.projects.models import Project
from .test_core import BaseTestCase

User = get_user_model()


class RequestQueueModelTest(BaseTestCase):
    """Test cases for RequestQueue model."""

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
        self.job = Job.objects.create(
            spider=self.spider,
            status='running'
        )

    def test_request_creation(self):
        """Test creating a request."""
        request = RequestQueue.objects.create(
            job=self.job,
            url='https://example.com/page',
            method='GET'
        )
        
        self.assertEqual(request.job, self.job)
        self.assertEqual(request.url, 'https://example.com/page')
        self.assertEqual(request.method, 'GET')
        self.assertEqual(request.status, 'pending')
        self.assertEqual(request.priority, 0)
        self.assertEqual(request.depth, 0)
        self.assertEqual(request.retries, 0)
        self.assertEqual(request.max_retries, 3)
        self.assertIsNotNone(request.fingerprint)
        self.assertIsNotNone(request.scheduled_at)
        
    def test_request_str_representation(self):
        """Test request string representation."""
        request = RequestQueue.objects.create(
            job=self.job,
            url='https://example.com/very-long-url-that-should-be-truncated',
            method='POST',
            status='in_progress'
        )
        expected = "Request 1: POST https://example.com/very-long-url-that-should-be-t... (in_progress)"
        self.assertEqual(str(request), expected)
        
    def test_request_status_choices(self):
        """Test request status choices."""
        expected_choices = ['pending', 'in_progress', 'done', 'error', 'skipped']
        actual_choices = [choice[0] for choice in RequestQueue.STATUS_CHOICES]
        self.assertEqual(actual_choices, expected_choices)
        
    def test_request_method_choices(self):
        """Test request method choices."""
        expected_methods = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'HEAD', 'OPTIONS']
        actual_methods = [choice[0] for choice in RequestQueue.METHOD_CHOICES]
        self.assertEqual(actual_methods, expected_methods)
        
    def test_request_default_status(self):
        """Test that default status is 'pending'."""
        request = RequestQueue.objects.create(
            job=self.job,
            url='https://example.com'
        )
        self.assertEqual(request.status, 'pending')
        
    def test_request_with_headers_and_body(self):
        """Test request with headers and body data."""
        headers = {'Content-Type': 'application/json', 'User-Agent': 'TestBot'}
        body_data = b'{"key": "value"}'
        
        request = RequestQueue.objects.create(
            job=self.job,
            url='https://api.example.com/data',
            method='POST',
            headers_json=headers,
            body_blob=body_data
        )
        
        self.assertEqual(request.headers_json, headers)
        self.assertEqual(request.body_blob, body_data)
        
    def test_fingerprint_generation(self):
        """Test fingerprint generation."""
        request = RequestQueue.objects.create(
            job=self.job,
            url='https://example.com/page',
            method='GET'
        )
        
        # Fingerprint should be generated automatically
        self.assertIsNotNone(request.fingerprint)
        self.assertEqual(len(request.fingerprint), 32)  # MD5 hash length
        
        # Same URL and method should generate same fingerprint
        request2 = RequestQueue(
            job=self.job,
            url='https://example.com/page',
            method='GET'
        )
        fingerprint2 = request2.generate_fingerprint()
        self.assertEqual(request.fingerprint, fingerprint2)
        
    def test_fingerprint_with_body(self):
        """Test fingerprint generation with body data."""
        body_data = b'{"test": "data"}'
        request = RequestQueue.objects.create(
            job=self.job,
            url='https://example.com/api',
            method='POST',
            body_blob=body_data
        )
        
        # Different body should create different fingerprint
        request2 = RequestQueue(
            job=self.job,
            url='https://example.com/api',
            method='POST',
            body_blob=b'{"different": "data"}'
        )
        fingerprint2 = request2.generate_fingerprint()
        self.assertNotEqual(request.fingerprint, fingerprint2)
        
    def test_unique_job_fingerprint_constraint(self):
        """Test that job+fingerprint combination must be unique."""
        RequestQueue.objects.create(
            job=self.job,
            url='https://example.com/page',
            method='GET'
        )
        
        # Creating another request with same job and URL should fail
        with self.assertRaises(IntegrityError):
            RequestQueue.objects.create(
                job=self.job,
                url='https://example.com/page',
                method='GET'
            )
            
    def test_can_retry_property(self):
        """Test can_retry property."""
        request = RequestQueue.objects.create(
            job=self.job,
            url='https://example.com/page',
            retries=2,
            max_retries=3
        )
        
        self.assertTrue(request.can_retry)
        
        request.retries = 3
        request.save()
        self.assertFalse(request.can_retry)
        
    def test_mark_in_progress(self):
        """Test marking request as in progress."""
        request = RequestQueue.objects.create(
            job=self.job,
            url='https://example.com/page',
            status='pending'
        )
        
        self.assertIsNone(request.picked_at)
        request.mark_in_progress()
        
        request.refresh_from_db()
        self.assertEqual(request.status, 'in_progress')
        self.assertIsNotNone(request.picked_at)
        
    def test_mark_done(self):
        """Test marking request as done."""
        request = RequestQueue.objects.create(
            job=self.job,
            url='https://example.com/page',
            status='in_progress'
        )
        
        request.mark_done()
        request.refresh_from_db()
        self.assertEqual(request.status, 'done')
        
    def test_mark_error(self):
        """Test marking request as error."""
        request = RequestQueue.objects.create(
            job=self.job,
            url='https://example.com/page',
            status='in_progress',
            retries=0
        )
        
        request.mark_error(increment_retry=True)
        request.refresh_from_db()
        self.assertEqual(request.status, 'error')
        self.assertEqual(request.retries, 1)
        
        # Test without incrementing retry
        request.mark_error(increment_retry=False)
        request.refresh_from_db()
        self.assertEqual(request.retries, 1)  # Should not increment
        
    def test_mark_skipped(self):
        """Test marking request as skipped."""
        request = RequestQueue.objects.create(
            job=self.job,
            url='https://example.com/page',
            status='pending'
        )
        
        request.mark_skipped()
        request.refresh_from_db()
        self.assertEqual(request.status, 'skipped')
        
    def test_reset_for_retry(self):
        """Test resetting request for retry."""
        request = RequestQueue.objects.create(
            job=self.job,
            url='https://example.com/page',
            status='error',
            retries=2,
            max_retries=3
        )
        request.mark_in_progress()  # Set picked_at
        
        # Should be able to retry
        result = request.reset_for_retry()
        self.assertTrue(result)
        
        request.refresh_from_db()
        self.assertEqual(request.status, 'pending')
        self.assertIsNone(request.picked_at)
        
        # Exceed max retries
        request.retries = 3
        request.save()
        result = request.reset_for_retry()
        self.assertFalse(result)
        
    def test_request_cascade_delete_with_job(self):
        """Test that requests are deleted when job is deleted."""
        request = RequestQueue.objects.create(
            job=self.job,
            url='https://example.com/page'
        )
        request_id = request.id
        
        self.job.delete()
        
        with self.assertRaises(RequestQueue.DoesNotExist):
            RequestQueue.objects.get(id=request_id)
            
    def test_request_ordering(self):
        """Test that requests are ordered by priority and scheduled_at."""
        # Create requests with different priorities
        request1 = RequestQueue.objects.create(
            job=self.job,
            url='https://example.com/page1',
            priority=1
        )
        request2 = RequestQueue.objects.create(
            job=self.job,
            url='https://example.com/page2',
            priority=5
        )
        request3 = RequestQueue.objects.create(
            job=self.job,
            url='https://example.com/page3',
            priority=1
        )
        
        requests = list(RequestQueue.objects.all())
        # Higher priority should come first
        self.assertEqual(requests[0], request2)  # priority 5
        # Same priority should be ordered by scheduled_at (FIFO)
        self.assertIn(request1, requests[1:])
        self.assertIn(request3, requests[1:])
        
    def test_priority_validation_range(self):
        """Test priority can be negative and positive."""
        # Negative priority (lower)
        request1 = RequestQueue.objects.create(
            job=self.job,
            url='https://example.com/low',
            priority=-10
        )
        self.assertEqual(request1.priority, -10)
        
        # High priority
        request2 = RequestQueue.objects.create(
            job=self.job,
            url='https://example.com/high',
            priority=50
        )
        self.assertEqual(request2.priority, 50)
        
    def test_request_model_indexes(self):
        """Test that proper database indexes exist."""
        indexes = RequestQueue._meta.indexes
        self.assertTrue(len(indexes) > 0)
        
        # Check for main composite index
        main_index = None
        for index in indexes:
            if ('job' in index.fields and 'status' in index.fields and 
                '-priority' in index.fields and 'scheduled_at' in index.fields):
                main_index = index
                break
                
        self.assertIsNotNone(main_index)