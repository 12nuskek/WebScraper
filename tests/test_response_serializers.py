"""
Test cases for Response serializers.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import serializers

from apps.response.models import Response
from apps.response.serializers import ResponseSerializer
from apps.request.models import RequestQueue
from apps.job.models import Job
from apps.spider.models import Spider
from apps.projects.models import Project
from .test_core import BaseTestCase

User = get_user_model()


class ResponseSerializerTest(BaseTestCase):
    """Test cases for ResponseSerializer."""

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
        
        self.request = RequestQueue.objects.create(
            job=self.job,
            url='https://example.com/page',
            method='GET'
        )
        self.other_request = RequestQueue.objects.create(
            job=self.other_job,
            url='https://other.com/page',
            method='GET'
        )

    def get_context(self, user=None):
        """Helper to create request context."""
        if user is None:
            user = self.user
        
        class MockRequest:
            def __init__(self, user):
                self.user = user
                
        return {'request': MockRequest(user)}

    def test_response_serializer_valid_data(self):
        """Test ResponseSerializer with valid data."""
        data = {
            'request': self.request.id,
            'final_url': 'https://example.com/final',
            'status_code': 200,
            'headers_json': {'Content-Type': 'text/html'},
            'latency_ms': 150
        }
        
        serializer = ResponseSerializer(data=data, context=self.get_context())
        self.assertTrue(serializer.is_valid(), serializer.errors)
        
        response = serializer.save()
        self.assertEqual(response.request, self.request)
        self.assertEqual(response.final_url, 'https://example.com/final')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.latency_ms, 150)
        
    def test_response_serializer_with_all_fields(self):
        """Test ResponseSerializer with complete data."""
        headers = {'Content-Type': 'application/json', 'Content-Length': '1234'}
        
        data = {
            'request': self.request.id,
            'final_url': 'https://api.example.com/data',
            'status_code': 201,
            'headers_json': headers,
            'latency_ms': 75,
            'from_cache': True,
            'body_path': 'responses/2023/12/01/response_123.html',
            'content_hash': 'abc123def456'
        }
        
        serializer = ResponseSerializer(data=data, context=self.get_context())
        self.assertTrue(serializer.is_valid(), serializer.errors)
        
        response = serializer.save()
        self.assertEqual(response.headers_json, headers)
        self.assertTrue(response.from_cache)
        self.assertEqual(response.body_path, 'responses/2023/12/01/response_123.html')
        self.assertEqual(response.content_hash, 'abc123def456')
        
    def test_response_serializer_missing_required_fields(self):
        """Test ResponseSerializer with missing required fields."""
        # Missing request
        data = {
            'status_code': 200,
            'final_url': 'https://example.com/page'
        }
        serializer = ResponseSerializer(data=data, context=self.get_context())
        self.assertFalse(serializer.is_valid())
        self.assertIn('request', serializer.errors)
        
    def test_response_serializer_invalid_request(self):
        """Test ResponseSerializer with invalid request ID."""
        data = {
            'request': 99999,  # Non-existent request
            'status_code': 200,
            'final_url': 'https://example.com/page'
        }
        
        serializer = ResponseSerializer(data=data, context=self.get_context())
        self.assertFalse(serializer.is_valid())
        self.assertIn('request', serializer.errors)
        
    def test_response_serializer_other_users_request(self):
        """Test ResponseSerializer validates request ownership."""
        data = {
            'request': self.other_request.id,  # Other user's request
            'status_code': 200,
            'final_url': 'https://example.com/page'
        }
        
        serializer = ResponseSerializer(data=data, context=self.get_context(self.user))
        self.assertFalse(serializer.is_valid())
        self.assertIn('request', serializer.errors)
        self.assertIn('your own requests', str(serializer.errors['request'][0]))
        
    def test_response_serializer_status_code_validation(self):
        """Test status code validation."""
        # Invalid status code (too low)
        data = {
            'request': self.request.id,
            'status_code': 99
        }
        
        serializer = ResponseSerializer(data=data, context=self.get_context())
        self.assertFalse(serializer.is_valid())
        self.assertIn('status_code', serializer.errors)
        
        # Invalid status code (too high)
        data['status_code'] = 600
        serializer = ResponseSerializer(data=data, context=self.get_context())
        self.assertFalse(serializer.is_valid())
        self.assertIn('status_code', serializer.errors)
        
        # Valid status codes
        for valid_code in [100, 200, 301, 404, 500, 599]:
            data['status_code'] = valid_code
            serializer = ResponseSerializer(data=data, context=self.get_context())
            self.assertTrue(serializer.is_valid(), f"Status code {valid_code} should be valid")
            
    def test_response_serializer_latency_validation(self):
        """Test latency validation."""
        # Negative latency
        data = {
            'request': self.request.id,
            'status_code': 200,
            'latency_ms': -100
        }
        
        serializer = ResponseSerializer(data=data, context=self.get_context())
        self.assertFalse(serializer.is_valid())
        self.assertIn('latency_ms', serializer.errors)
        
        # Valid latency
        data['latency_ms'] = 150
        serializer = ResponseSerializer(data=data, context=self.get_context())
        self.assertTrue(serializer.is_valid())
        
    def test_response_serializer_final_url_validation(self):
        """Test final URL validation."""
        # Invalid URL (no protocol)
        data = {
            'request': self.request.id,
            'status_code': 200,
            'final_url': 'example.com/page'
        }
        
        serializer = ResponseSerializer(data=data, context=self.get_context())
        self.assertFalse(serializer.is_valid())
        self.assertIn('final_url', serializer.errors)
        
        # Valid HTTPS URL
        data['final_url'] = 'https://example.com/page'
        serializer = ResponseSerializer(data=data, context=self.get_context())
        self.assertTrue(serializer.is_valid())
        
        # Valid HTTP URL
        data['final_url'] = 'http://example.com/page'
        serializer = ResponseSerializer(data=data, context=self.get_context())
        self.assertTrue(serializer.is_valid())
        
    def test_response_serializer_read_only_fields(self):
        """Test that read-only fields are properly handled."""
        response = Response.objects.create(
            request=self.request,
            status_code=200,
            latency_ms=100
        )
        
        serializer = ResponseSerializer(response)
        data = serializer.data
        
        # Check that read-only fields are included
        self.assertIn('id', data)
        self.assertIn('created_at', data)
        self.assertIn('updated_at', data)
        self.assertIn('is_success', data)
        self.assertIn('is_redirect', data)
        self.assertIn('is_client_error', data)
        self.assertIn('is_server_error', data)
        self.assertIn('body_size', data)
        
        # Status properties should be calculated correctly
        self.assertTrue(data['is_success'])
        self.assertFalse(data['is_redirect'])
        self.assertFalse(data['is_client_error'])
        self.assertFalse(data['is_server_error'])
        
    def test_response_serializer_status_properties(self):
        """Test that status properties are correctly calculated."""
        # Success response
        success_response = Response.objects.create(
            request=self.request,
            status_code=200
        )
        serializer = ResponseSerializer(success_response)
        self.assertTrue(serializer.data['is_success'])
        
        # Redirect response
        redirect_response = Response.objects.create(
            request=RequestQueue.objects.create(
                job=self.job,
                url='https://example.com/redirect'
            ),
            status_code=301
        )
        serializer = ResponseSerializer(redirect_response)
        self.assertTrue(serializer.data['is_redirect'])
        
        # Client error response
        client_error_response = Response.objects.create(
            request=RequestQueue.objects.create(
                job=self.job,
                url='https://example.com/notfound'
            ),
            status_code=404
        )
        serializer = ResponseSerializer(client_error_response)
        self.assertTrue(serializer.data['is_client_error'])
        
        # Server error response
        server_error_response = Response.objects.create(
            request=RequestQueue.objects.create(
                job=self.job,
                url='https://example.com/error'
            ),
            status_code=500
        )
        serializer = ResponseSerializer(server_error_response)
        self.assertTrue(serializer.data['is_server_error'])
        
    def test_response_serializer_update(self):
        """Test updating a response through serializer."""
        response = Response.objects.create(
            request=self.request,
            status_code=200,
            latency_ms=100
        )
        
        update_data = {
            'status_code': 201,
            'latency_ms': 150,
            'from_cache': True
        }
        
        serializer = ResponseSerializer(response, data=update_data, partial=True)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        
        updated_response = serializer.save()
        self.assertEqual(updated_response.status_code, 201)
        self.assertEqual(updated_response.latency_ms, 150)
        self.assertTrue(updated_response.from_cache)
        
    def test_response_serializer_optional_fields(self):
        """Test ResponseSerializer with optional fields as None."""
        data = {
            'request': self.request.id,
            'status_code': None,
            'final_url': None,
            'headers_json': None,
            'latency_ms': None,
            'body_path': None,
            'content_hash': None
        }
        
        serializer = ResponseSerializer(data=data, context=self.get_context())
        self.assertTrue(serializer.is_valid(), serializer.errors)
        
        response = serializer.save()
        self.assertIsNone(response.status_code)
        self.assertIsNone(response.final_url)
        self.assertIsNone(response.headers_json)
        self.assertIsNone(response.latency_ms)
        self.assertIsNone(response.body_path)
        self.assertIsNone(response.content_hash)
        
    def test_response_serializer_complex_headers(self):
        """Test ResponseSerializer with complex headers JSON."""
        complex_headers = {
            'Content-Type': 'application/json; charset=utf-8',
            'Content-Length': '1234',
            'Cache-Control': 'max-age=3600, public',
            'Set-Cookie': ['session=abc123; HttpOnly', 'csrf=def456; Secure'],
            'X-Custom-Header': 'custom value with spaces'
        }
        
        data = {
            'request': self.request.id,
            'status_code': 200,
            'headers_json': complex_headers
        }
        
        serializer = ResponseSerializer(data=data, context=self.get_context())
        self.assertTrue(serializer.is_valid(), serializer.errors)
        
        response = serializer.save()
        self.assertEqual(response.headers_json, complex_headers)
        
    def test_response_serializer_body_size_property(self):
        """Test that body_size property is correctly serialized."""
        response = Response.objects.create(
            request=self.request,
            status_code=200
        )
        
        serializer = ResponseSerializer(response)
        # Should be 0 since no body file exists
        self.assertEqual(serializer.data['body_size'], 0)