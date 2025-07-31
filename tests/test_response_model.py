"""
Test cases for Response model.
"""

import tempfile
import shutil
from pathlib import Path
from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.response.models import Response
from apps.request.models import RequestQueue
from apps.job.models import Job
from apps.spider.models import Spider
from apps.projects.models import Project
from .test_core import BaseTestCase

User = get_user_model()


class ResponseModelTest(BaseTestCase):
    """Test cases for Response model."""

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
        self.request = RequestQueue.objects.create(
            job=self.job,
            url='https://example.com/page',
            method='GET'
        )

    def test_response_creation(self):
        """Test creating a response."""
        response = Response.objects.create(
            request=self.request,
            final_url='https://example.com/final',
            status_code=200,
            headers_json={'Content-Type': 'text/html'},
            latency_ms=100
        )
        
        self.assertEqual(response.request, self.request)
        self.assertEqual(response.final_url, 'https://example.com/final')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers_json, {'Content-Type': 'text/html'})
        self.assertEqual(response.latency_ms, 100)
        self.assertFalse(response.from_cache)
        self.assertIsNotNone(response.fetched_at)
        
    def test_response_str_representation(self):
        """Test response string representation."""
        response = Response.objects.create(
            request=self.request,
            final_url='https://example.com/very-long-url-that-should-be-truncated',
            status_code=404
        )
        expected = "Response 1: 404 https://example.com/very-long-url-that-should-be-t..."
        self.assertEqual(str(response), expected)
        
    def test_response_status_properties(self):
        """Test response status property methods."""
        # Test successful response (2xx)
        success_response = Response.objects.create(
            request=self.request,
            status_code=200
        )
        self.assertTrue(success_response.is_success)
        self.assertFalse(success_response.is_redirect)
        self.assertFalse(success_response.is_client_error)
        self.assertFalse(success_response.is_server_error)
        
        # Test redirect response (3xx)
        redirect_response = Response.objects.create(
            request=RequestQueue.objects.create(
                job=self.job,
                url='https://example.com/redirect'
            ),
            status_code=301
        )
        self.assertFalse(redirect_response.is_success)
        self.assertTrue(redirect_response.is_redirect)
        self.assertFalse(redirect_response.is_client_error)
        self.assertFalse(redirect_response.is_server_error)
        
        # Test client error response (4xx)
        client_error_response = Response.objects.create(
            request=RequestQueue.objects.create(
                job=self.job,
                url='https://example.com/notfound'
            ),
            status_code=404
        )
        self.assertFalse(client_error_response.is_success)
        self.assertFalse(client_error_response.is_redirect)
        self.assertTrue(client_error_response.is_client_error)
        self.assertFalse(client_error_response.is_server_error)
        
        # Test server error response (5xx)
        server_error_response = Response.objects.create(
            request=RequestQueue.objects.create(
                job=self.job,
                url='https://example.com/error'
            ),
            status_code=500
        )
        self.assertFalse(server_error_response.is_success)
        self.assertFalse(server_error_response.is_redirect)
        self.assertFalse(server_error_response.is_client_error)
        self.assertTrue(server_error_response.is_server_error)
        
    def test_response_with_no_status_code(self):
        """Test response with no status code."""
        response = Response.objects.create(
            request=self.request,
            status_code=None
        )
        self.assertFalse(response.is_success)
        self.assertFalse(response.is_redirect)
        self.assertFalse(response.is_client_error)
        self.assertFalse(response.is_server_error)
        
    @override_settings(MEDIA_ROOT=tempfile.mkdtemp())
    def test_body_saving_and_reading(self):
        """Test saving and reading response body."""
        response = Response.objects.create(
            request=self.request,
            status_code=200
        )
        
        body_content = '<html><body><h1>Test Page</h1></body></html>'
        response.save_body(body_content)
        response.save()  # Save the model after setting body_path
        
        # Check that body_path and content_hash are set
        self.assertIsNotNone(response.body_path)
        self.assertIsNotNone(response.content_hash)
        
        # Check body size
        self.assertEqual(response.body_size, len(body_content.encode('utf-8')))
        
        # Read body back
        read_content = response.read_body_text()
        self.assertEqual(read_content, body_content)
        
        # Read as bytes
        read_bytes = response.read_body()
        self.assertEqual(read_bytes, body_content.encode('utf-8'))
        
        # Clean up
        response.delete_body_file()
        
    @override_settings(MEDIA_ROOT=tempfile.mkdtemp())
    def test_body_saving_binary_content(self):
        """Test saving binary body content."""
        response = Response.objects.create(
            request=self.request,
            status_code=200
        )
        
        binary_content = b'\\x89PNG\\r\\n\\x1a\\n'  # PNG header bytes
        response.save_body(binary_content)
        response.save()  # Save the model after setting body_path
        
        # Check that content was saved
        self.assertIsNotNone(response.body_path)
        self.assertIsNotNone(response.content_hash)
        self.assertEqual(response.body_size, len(binary_content))
        
        # Read back as bytes
        read_bytes = response.read_body()
        self.assertEqual(read_bytes, binary_content)
        
        # Clean up
        response.delete_body_file()
        
    @override_settings(MEDIA_ROOT=tempfile.mkdtemp())
    def test_body_file_deletion(self):
        """Test body file deletion."""
        response = Response.objects.create(
            request=self.request,
            status_code=200
        )
        
        body_content = 'Test content for deletion'
        response.save_body(body_content)
        response.save()  # Save the model after setting body_path
        
        # Verify file exists
        self.assertTrue(response.body_size > 0)
        
        # Delete file
        self.assertTrue(response.delete_body_file())
        
        # Verify file is gone
        self.assertEqual(response.body_size, 0)
        read_content = response.read_body()
        self.assertIsNone(read_content)
        
    @override_settings(MEDIA_ROOT=tempfile.mkdtemp())
    def test_response_deletion_removes_body_file(self):
        """Test that deleting response also removes body file."""
        response = Response.objects.create(
            request=self.request,
            status_code=200
        )
        
        body_content = 'Content to be deleted with response'
        response.save_body(body_content)
        body_path = response.body_path
        
        # Delete response
        response.delete()
        
        # Verify body file is also gone
        from django.conf import settings
        full_path = Path(settings.MEDIA_ROOT) / body_path
        self.assertFalse(full_path.exists())
        
    def test_response_cascade_delete_with_request(self):
        """Test that responses are deleted when request is deleted."""
        response = Response.objects.create(
            request=self.request,
            status_code=200
        )
        response_id = response.id
        
        self.request.delete()
        
        with self.assertRaises(Response.DoesNotExist):
            Response.objects.get(id=response_id)
            
    def test_response_ordering(self):
        """Test that responses are ordered by fetched_at descending."""
        response1 = Response.objects.create(
            request=self.request,
            status_code=200
        )
        
        response2 = Response.objects.create(
            request=RequestQueue.objects.create(
                job=self.job,
                url='https://example.com/page2'
            ),
            status_code=404
        )
        
        responses = list(Response.objects.all())
        # Most recent first
        self.assertEqual(responses[0], response2)
        self.assertEqual(responses[1], response1)
        
    def test_content_hash_generation(self):
        """Test content hash generation."""
        response = Response.objects.create(
            request=self.request,
            status_code=200
        )
        
        content1 = 'Same content'
        content2 = 'Same content'
        content3 = 'Different content'
        
        # Save first content
        response.save_body(content1)
        hash1 = response.content_hash
        
        # Save same content - should have same hash
        response.save_body(content2)
        hash2 = response.content_hash
        self.assertEqual(hash1, hash2)
        
        # Save different content - should have different hash
        response.save_body(content3)
        hash3 = response.content_hash
        self.assertNotEqual(hash1, hash3)
        
    def test_class_methods(self):
        """Test class methods for filtering responses."""
        # Create responses with different status codes
        success_response = Response.objects.create(
            request=self.request,
            status_code=200
        )
        
        not_found_response = Response.objects.create(
            request=RequestQueue.objects.create(
                job=self.job,
                url='https://example.com/notfound'
            ),
            status_code=404
        )
        
        server_error_response = Response.objects.create(
            request=RequestQueue.objects.create(
                job=self.job,
                url='https://example.com/error'
            ),
            status_code=500
        )
        
        # Test get_responses_by_status_code
        responses_200 = Response.get_responses_by_status_code(200)
        self.assertEqual(responses_200.count(), 1)
        self.assertEqual(responses_200.first(), success_response)
        
        # Test get_successful_responses
        successful = Response.get_successful_responses()
        self.assertEqual(successful.count(), 1)
        self.assertEqual(successful.first(), success_response)
        
        # Test get_error_responses
        errors = Response.get_error_responses()
        self.assertEqual(errors.count(), 2)
        self.assertIn(not_found_response, errors)
        self.assertIn(server_error_response, errors)
        
    def test_response_with_cache_flag(self):
        """Test response with cache flag."""
        cached_response = Response.objects.create(
            request=self.request,
            status_code=200,
            from_cache=True
        )
        
        self.assertTrue(cached_response.from_cache)
        
    def test_response_with_headers(self):
        """Test response with various headers."""
        headers = {
            'Content-Type': 'application/json',
            'Content-Length': '1234',
            'Cache-Control': 'max-age=3600',
            'Set-Cookie': 'session=abc123; HttpOnly'
        }
        
        response = Response.objects.create(
            request=self.request,
            status_code=200,
            headers_json=headers
        )
        
        self.assertEqual(response.headers_json, headers)
        
    def test_response_latency_tracking(self):
        """Test response latency tracking."""
        fast_response = Response.objects.create(
            request=self.request,
            status_code=200,
            latency_ms=50
        )
        
        slow_response = Response.objects.create(
            request=RequestQueue.objects.create(
                job=self.job,
                url='https://example.com/slow'
            ),
            status_code=200,
            latency_ms=5000
        )
        
        self.assertEqual(fast_response.latency_ms, 50)
        self.assertEqual(slow_response.latency_ms, 5000)
        
    def test_response_model_indexes(self):
        """Test that proper database indexes exist."""
        indexes = Response._meta.indexes
        self.assertTrue(len(indexes) > 0)
        
        # Check for important indexes
        index_fields = []
        for index in indexes:
            index_fields.extend(index.fields)
            
        self.assertIn('request', index_fields)
        self.assertIn('status_code', index_fields)
        self.assertIn('fetched_at', index_fields)