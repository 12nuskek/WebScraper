"""
Test cases for RequestQueue serializers.
"""

import base64
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import serializers

from apps.request.models import RequestQueue
from apps.request.serializers import RequestQueueSerializer
from apps.job.models import Job
from apps.spider.models import Spider
from apps.projects.models import Project
from .test_core import BaseTestCase

User = get_user_model()


class RequestQueueSerializerTest(BaseTestCase):
    """Test cases for RequestQueueSerializer."""

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
        
        self.job = Job.objects.create(
            spider=self.spider,
            status='running'
        )
        self.other_job = Job.objects.create(
            spider=self.other_spider,
            status='running'
        )

    def get_context(self, user=None):
        """Helper to create request context."""
        if user is None:
            user = self.user
        
        class MockRequest:
            def __init__(self, user):
                self.user = user
                
        return {'request': MockRequest(user)}

    def test_request_serializer_valid_data(self):
        """Test RequestQueueSerializer with valid data."""
        data = {
            'job': self.job.id,
            'url': 'https://example.com/page',
            'method': 'GET'
        }
        
        serializer = RequestQueueSerializer(data=data, context=self.get_context())
        self.assertTrue(serializer.is_valid(), serializer.errors)
        
        request = serializer.save()
        self.assertEqual(request.job, self.job)
        self.assertEqual(request.url, 'https://example.com/page')
        self.assertEqual(request.method, 'GET')
        
    def test_request_serializer_with_all_fields(self):
        """Test RequestQueueSerializer with complete data."""
        headers = {'Content-Type': 'application/json'}
        body_data = b'{"test": "data"}'
        body_b64 = base64.b64encode(body_data).decode('utf-8')
        
        data = {
            'job': self.job.id,
            'url': 'https://api.example.com/endpoint',
            'method': 'POST',
            'headers_json': headers,
            'body_blob': body_b64,
            'priority': 5,
            'depth': 2,
            'max_retries': 5
        }
        
        serializer = RequestQueueSerializer(data=data, context=self.get_context())
        self.assertTrue(serializer.is_valid(), serializer.errors)
        
        request = serializer.save()
        self.assertEqual(request.headers_json, headers)
        self.assertEqual(request.body_blob, body_data)
        self.assertEqual(request.priority, 5)
        self.assertEqual(request.depth, 2)
        self.assertEqual(request.max_retries, 5)
        
    def test_request_serializer_missing_required_fields(self):
        """Test RequestQueueSerializer with missing required fields."""
        # Missing job
        data = {
            'url': 'https://example.com/page',
            'method': 'GET'
        }
        serializer = RequestQueueSerializer(data=data, context=self.get_context())
        self.assertFalse(serializer.is_valid())
        self.assertIn('job', serializer.errors)
        
        # Missing URL
        data = {
            'job': self.job.id,
            'method': 'GET'
        }
        serializer = RequestQueueSerializer(data=data, context=self.get_context())
        self.assertFalse(serializer.is_valid())
        self.assertIn('url', serializer.errors)
        
    def test_request_serializer_invalid_job(self):
        """Test RequestQueueSerializer with invalid job ID."""
        data = {
            'job': 99999,  # Non-existent job
            'url': 'https://example.com/page',
            'method': 'GET'
        }
        
        serializer = RequestQueueSerializer(data=data, context=self.get_context())
        self.assertFalse(serializer.is_valid())
        self.assertIn('job', serializer.errors)
        
    def test_request_serializer_other_users_job(self):
        """Test RequestQueueSerializer validates job ownership."""
        data = {
            'job': self.other_job.id,  # Other user's job
            'url': 'https://example.com/page',
            'method': 'GET'
        }
        
        serializer = RequestQueueSerializer(data=data, context=self.get_context(self.user))
        self.assertFalse(serializer.is_valid())
        self.assertIn('job', serializer.errors)
        self.assertIn('your own jobs', str(serializer.errors['job'][0]))
        
    def test_request_serializer_url_validation(self):
        """Test URL validation."""
        # Invalid URL (no protocol)
        data = {
            'job': self.job.id,
            'url': 'example.com/page',
            'method': 'GET'
        }
        
        serializer = RequestQueueSerializer(data=data, context=self.get_context())
        self.assertFalse(serializer.is_valid())
        self.assertIn('url', serializer.errors)
        
        # Valid HTTPS URL
        data['url'] = 'https://example.com/page'
        serializer = RequestQueueSerializer(data=data, context=self.get_context())
        self.assertTrue(serializer.is_valid())
        
    def test_request_serializer_priority_validation(self):
        """Test priority validation."""
        # Priority too low
        data = {
            'job': self.job.id,
            'url': 'https://example.com/page',
            'priority': -150
        }
        
        serializer = RequestQueueSerializer(data=data, context=self.get_context())
        self.assertFalse(serializer.is_valid())
        self.assertIn('priority', serializer.errors)
        
        # Priority too high
        data['priority'] = 150
        serializer = RequestQueueSerializer(data=data, context=self.get_context())
        self.assertFalse(serializer.is_valid())
        self.assertIn('priority', serializer.errors)
        
        # Valid priority
        data['priority'] = 50
        serializer = RequestQueueSerializer(data=data, context=self.get_context())
        self.assertTrue(serializer.is_valid())
        
    def test_request_serializer_max_retries_validation(self):
        """Test max_retries validation."""
        # Negative retries
        data = {
            'job': self.job.id,
            'url': 'https://example.com/page',
            'max_retries': -1
        }
        
        serializer = RequestQueueSerializer(data=data, context=self.get_context())
        self.assertFalse(serializer.is_valid())
        self.assertIn('max_retries', serializer.errors)
        
        # Too many retries
        data['max_retries'] = 15
        serializer = RequestQueueSerializer(data=data, context=self.get_context())
        self.assertFalse(serializer.is_valid())
        self.assertIn('max_retries', serializer.errors)
        
        # Valid retries
        data['max_retries'] = 5
        serializer = RequestQueueSerializer(data=data, context=self.get_context())
        self.assertTrue(serializer.is_valid())
        
    def test_request_serializer_body_blob_handling(self):
        """Test body_blob base64 encoding/decoding."""
        original_data = b'{"json": "data", "number": 123}'
        
        # Create request with binary data
        request = RequestQueue.objects.create(
            job=self.job,
            url='https://api.example.com/data',
            method='POST',
            body_blob=original_data
        )
        
        # Serialize
        serializer = RequestQueueSerializer(request)
        serialized_body = serializer.data['body_blob']
        
        # Should be base64 encoded
        self.assertIsInstance(serialized_body, str)
        decoded_data = base64.b64decode(serialized_body)
        self.assertEqual(decoded_data, original_data)
        
    def test_request_serializer_body_blob_deserialization(self):
        """Test body_blob deserialization from base64."""
        original_data = b'{"test": "payload"}'
        body_b64 = base64.b64encode(original_data).decode('utf-8')
        
        data = {
            'job': self.job.id,
            'url': 'https://api.example.com/post',
            'method': 'POST',
            'body_blob': body_b64
        }
        
        serializer = RequestQueueSerializer(data=data, context=self.get_context())
        self.assertTrue(serializer.is_valid(), serializer.errors)
        
        request = serializer.save()
        self.assertEqual(request.body_blob, original_data)
        
    def test_request_serializer_invalid_base64(self):
        """Test invalid base64 body_blob handling."""
        data = {
            'job': self.job.id,
            'url': 'https://api.example.com/post',
            'method': 'POST',
            'body_blob': 'invalid-base64!'
        }
        
        serializer = RequestQueueSerializer(data=data, context=self.get_context())
        self.assertFalse(serializer.is_valid())
        self.assertIn('body_blob', serializer.errors)
        
    def test_request_serializer_read_only_fields(self):
        """Test that read-only fields are properly handled."""
        request = RequestQueue.objects.create(
            job=self.job,
            url='https://example.com/page',
            priority=5,
            retries=2,
            max_retries=5
        )
        
        serializer = RequestQueueSerializer(request)
        data = serializer.data
        
        # Check that read-only fields are included
        self.assertIn('id', data)
        self.assertIn('fingerprint', data)
        self.assertIn('created_at', data)
        self.assertIn('updated_at', data)
        self.assertIn('can_retry', data)
        
        # can_retry should be calculated correctly
        self.assertTrue(data['can_retry'])
        
    def test_request_serializer_can_retry_calculation(self):
        """Test that can_retry is properly calculated."""
        # Request that can retry
        request = RequestQueue.objects.create(
            job=self.job,
            url='https://example.com/page',
            retries=2,
            max_retries=5
        )
        
        serializer = RequestQueueSerializer(request)
        self.assertTrue(serializer.data['can_retry'])
        
        # Request that cannot retry
        request.retries = 5
        request.save()
        
        serializer = RequestQueueSerializer(request)
        self.assertFalse(serializer.data['can_retry'])
        
    def test_request_serializer_update(self):
        """Test updating a request through serializer."""
        request = RequestQueue.objects.create(
            job=self.job,
            url='https://example.com/page',
            status='pending',
            priority=0
        )
        
        update_data = {
            'status': 'in_progress',
            'priority': 10,
            'picked_at': timezone.now().isoformat()
        }
        
        serializer = RequestQueueSerializer(request, data=update_data, partial=True)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        
        updated_request = serializer.save()
        self.assertEqual(updated_request.status, 'in_progress')
        self.assertEqual(updated_request.priority, 10)
        
    def test_request_serializer_invalid_status(self):
        """Test RequestQueueSerializer with invalid status."""
        data = {
            'job': self.job.id,
            'url': 'https://example.com/page',
            'status': 'invalid_status'
        }
        
        serializer = RequestQueueSerializer(data=data, context=self.get_context())
        self.assertFalse(serializer.is_valid())
        self.assertIn('status', serializer.errors)
        
    def test_request_serializer_invalid_method(self):
        """Test RequestQueueSerializer with invalid HTTP method."""
        data = {
            'job': self.job.id,
            'url': 'https://example.com/page',
            'method': 'INVALID'
        }
        
        serializer = RequestQueueSerializer(data=data, context=self.get_context())
        self.assertFalse(serializer.is_valid())
        self.assertIn('method', serializer.errors)