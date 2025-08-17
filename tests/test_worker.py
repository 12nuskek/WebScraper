"""
Test cases for BasicWorker and worker functionality.
"""

import os
import json
import time
import tempfile
from unittest.mock import patch, MagicMock, call
from datetime import datetime, timedelta
from pathlib import Path

from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import transaction
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from apps.job.models import Job
from apps.spider.models import Spider
from apps.projects.models import Project
from .test_core import BaseTestCase

# Import the worker class - need to handle the path properly
import sys
worker_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'scraping-backend', 'services', 'worker')
if worker_path not in sys.path:
    sys.path.insert(0, worker_path)

from basic_worker import BasicWorker, scrape_heading_task

User = get_user_model()


class BasicWorkerUnitTest(BaseTestCase):
    """Unit tests for BasicWorker class methods."""

    def setUp(self):
        """Set up test data."""
        super().setUp()
        self.worker = BasicWorker(poll_interval=1)  # Shorter interval for testing
        
        # Create test user, project, spider, and jobs
        self.user = User.objects.create_user(
            email='worker_test@example.com',
            password='testpass123',
            first_name='Worker',
            last_name='Test'
        )
        
        self.project = Project.objects.create(
            owner=self.user,
            name='Worker Test Project',
            notes='Test project for worker tests'
        )
        
        self.spider = Spider.objects.create(
            project=self.project,
            name='worker-test-spider',
            start_urls_json=['https://example.com']
        )

    def test_worker_initialization(self):
        """Test worker initialization."""
        worker = BasicWorker(poll_interval=10)
        self.assertEqual(worker.poll_interval, 10)
        self.assertFalse(worker.running)

    def test_get_next_job_no_jobs(self):
        """Test get_next_job when no jobs exist."""
        job = self.worker.get_next_job()
        self.assertIsNone(job)

    def test_get_next_job_no_queued_jobs(self):
        """Test get_next_job when no queued jobs exist."""
        # Create jobs with different statuses
        Job.objects.create(spider=self.spider, status='running')
        Job.objects.create(spider=self.spider, status='done')
        Job.objects.create(spider=self.spider, status='failed')
        
        job = self.worker.get_next_job()
        self.assertIsNone(job)

    def test_get_next_job_returns_oldest_queued(self):
        """Test get_next_job returns oldest queued job."""
        # Create jobs with different timestamps
        old_job = Job.objects.create(spider=self.spider, status='queued')
        old_job.created_at = timezone.now() - timedelta(hours=2)
        old_job.save()
        
        middle_job = Job.objects.create(spider=self.spider, status='queued')
        middle_job.created_at = timezone.now() - timedelta(hours=1)
        middle_job.save()
        
        new_job = Job.objects.create(spider=self.spider, status='queued')
        
        # Should return the oldest job
        next_job = self.worker.get_next_job()
        self.assertEqual(next_job.id, old_job.id)

    def test_get_next_job_ignores_non_queued(self):
        """Test get_next_job ignores non-queued jobs."""
        # Create older non-queued job
        old_job = Job.objects.create(spider=self.spider, status='running')
        old_job.created_at = timezone.now() - timedelta(hours=2)
        old_job.save()
        
        # Create newer queued job
        queued_job = Job.objects.create(spider=self.spider, status='queued')
        
        # Should return the queued job, not the older non-queued one
        next_job = self.worker.get_next_job()
        self.assertEqual(next_job.id, queued_job.id)

    def test_save_results_creates_file(self):
        """Test save_results creates a JSON file with correct data."""
        job = Job.objects.create(spider=self.spider, status='running')
        test_data = {
            'message': 'Test completed',
            'data': {'pages': 5, 'items': 10}
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Mock the BASE_DIR to use temp directory
            with patch('basic_worker.BASE_DIR', Path(temp_dir)):
                file_path = self.worker.save_results(job, test_data)
                
                # Check file was created
                self.assertTrue(os.path.exists(file_path))
                
                # Check file contents
                with open(file_path, 'r') as f:
                    saved_data = json.load(f)
                
                self.assertEqual(saved_data, test_data)
                
                # Check filename format
                filename = os.path.basename(file_path)
                self.assertTrue(filename.startswith(f'job_{job.id}_'))
                self.assertTrue(filename.endswith('.json'))

    @patch('basic_worker.scrape_heading_task')
    def test_process_job_success(self, mock_scrape):
        """Test successful job processing."""
        # Setup mock
        mock_scraper_result = {'heading': 'Test Heading'}
        mock_scrape.return_value = mock_scraper_result
        
        job = Job.objects.create(spider=self.spider, status='queued')
        original_created_at = job.created_at
        
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('basic_worker.BASE_DIR', Path(temp_dir)):
                self.worker.process_job(job)
        
        # Refresh job from database
        job.refresh_from_db()
        
        # Check job status and timing
        self.assertEqual(job.status, 'done')
        self.assertIsNotNone(job.started_at)
        self.assertIsNotNone(job.finished_at)
        self.assertGreater(job.started_at, original_created_at)
        self.assertGreater(job.finished_at, job.started_at)
        
        # Check stats
        self.assertIsNotNone(job.stats_json)
        self.assertTrue(job.stats_json['success'])
        self.assertIn('completed_at', job.stats_json)
        self.assertIn('file_path', job.stats_json)

    @patch('basic_worker.scrape_heading_task')
    def test_process_job_failure(self, mock_scrape):
        """Test job processing when scraping fails."""
        # Setup mock to raise exception
        mock_scrape.side_effect = Exception("Scraping failed")
        
        job = Job.objects.create(spider=self.spider, status='queued')
        
        self.worker.process_job(job)
        
        # Refresh job from database
        job.refresh_from_db()
        
        # Check job marked as failed
        self.assertEqual(job.status, 'failed')
        self.assertIsNotNone(job.started_at)
        self.assertIsNotNone(job.finished_at)
        
        # Check error in stats
        self.assertIsNotNone(job.stats_json)
        self.assertIn('error', job.stats_json)
        self.assertIn('failed_at', job.stats_json)
        self.assertEqual(job.stats_json['error'], 'Scraping failed')

    def test_process_job_status_transitions(self):
        """Test job goes through correct status transitions."""
        job = Job.objects.create(spider=self.spider, status='queued')
        
        # Track status changes
        statuses = []
        
        def track_status(*args, **kwargs):
            job.refresh_from_db()
            statuses.append(job.status)
        
        with patch('basic_worker.scrape_heading_task', return_value={'test': 'data'}):
            with patch('basic_worker.time.sleep', side_effect=track_status):
                with tempfile.TemporaryDirectory() as temp_dir:
                    with patch('basic_worker.BASE_DIR', Path(temp_dir)):
                        self.worker.process_job(job)
        
        job.refresh_from_db()
        final_status = job.status
        
        # Should end with 'done' status
        self.assertEqual(final_status, 'done')


class BasicWorkerIntegrationTest(BaseTestCase):
    """Integration tests for worker functionality."""

    def setUp(self):
        """Set up test data."""
        super().setUp()
        self.worker = BasicWorker(poll_interval=0.1)  # Very short interval for testing
        
        # Create test user, project, and spider
        self.user = User.objects.create_user(
            email='integration_test@example.com',
            password='testpass123',
            first_name='Integration',
            last_name='Test'
        )
        
        self.project = Project.objects.create(
            owner=self.user,
            name='Integration Test Project',
            notes='Test project for integration tests'
        )
        
        self.spider = Spider.objects.create(
            project=self.project,
            name='integration-test-spider',
            start_urls_json=['https://example.com']
        )

    @patch('basic_worker.scrape_heading_task')
    def test_worker_processes_single_job(self, mock_scrape):
        """Test worker processes a single job end-to-end."""
        mock_scrape.return_value = {'heading': 'Integration Test'}
        
        # Create a queued job
        job = Job.objects.create(spider=self.spider, status='queued')
        
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('basic_worker.BASE_DIR', Path(temp_dir)):
                # Instead of threading, just simulate the worker flow
                # Get the next job (like worker would)
                next_job = self.worker.get_next_job()
                self.assertEqual(next_job.id, job.id)
                
                # Process the job (like worker would)
                self.worker.process_job(next_job)
                
                # Verify job was processed
                job.refresh_from_db()
                self.assertEqual(job.status, 'done')
                self.assertIsNotNone(job.started_at)
                self.assertIsNotNone(job.finished_at)
                self.assertIsNotNone(job.stats_json)
                
                # Verify no more jobs are available
                no_more_jobs = self.worker.get_next_job()
                self.assertIsNone(no_more_jobs)

    @patch('basic_worker.scrape_heading_task')
    def test_worker_processes_multiple_jobs_in_order(self, mock_scrape):
        """Test worker processes multiple jobs in correct order."""
        mock_scrape.return_value = {'heading': 'Test'}
        
        # Create multiple jobs with different timestamps
        job1 = Job.objects.create(spider=self.spider, status='queued')
        job1.created_at = timezone.now() - timedelta(minutes=3)
        job1.save()
        
        job2 = Job.objects.create(spider=self.spider, status='queued')
        job2.created_at = timezone.now() - timedelta(minutes=2)
        job2.save()
        
        job3 = Job.objects.create(spider=self.spider, status='queued')
        job3.created_at = timezone.now() - timedelta(minutes=1)
        job3.save()
        
        processed_jobs = []
        
        def track_processing(*args, **kwargs):
            # Find which job is currently running
            running_job = Job.objects.filter(status='running').first()
            if running_job and running_job.id not in processed_jobs:
                processed_jobs.append(running_job.id)
            return {'heading': f'Test {len(processed_jobs)}'}
        
        mock_scrape.side_effect = track_processing
        
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('basic_worker.BASE_DIR', Path(temp_dir)):
                # Process jobs one by one
                for _ in range(3):
                    next_job = self.worker.get_next_job()
                    if next_job:
                        self.worker.process_job(next_job)
                
                # Verify jobs were processed in correct order (oldest first)
                expected_order = [job1.id, job2.id, job3.id]
                self.assertEqual(processed_jobs, expected_order)
                
                # Verify all jobs are done
                job1.refresh_from_db()
                job2.refresh_from_db()
                job3.refresh_from_db()
                
                self.assertEqual(job1.status, 'done')
                self.assertEqual(job2.status, 'done')
                self.assertEqual(job3.status, 'done')

    def test_worker_handles_no_jobs_gracefully(self):
        """Test worker handles case when no jobs are available."""
        # Start with no jobs
        self.assertEqual(Job.objects.filter(status='queued').count(), 0)
        
        # Get next job should return None
        job = self.worker.get_next_job()
        self.assertIsNone(job)
        
        # Worker should handle this gracefully
        # This is tested implicitly by the worker loop handling None jobs

    @patch('basic_worker.scrape_heading_task')
    def test_worker_handles_mixed_job_statuses(self, mock_scrape):
        """Test worker only processes queued jobs, ignoring others."""
        mock_scrape.return_value = {'heading': 'Test'}
        
        # Create jobs with different statuses
        queued_job = Job.objects.create(spider=self.spider, status='queued')
        running_job = Job.objects.create(spider=self.spider, status='running')
        done_job = Job.objects.create(spider=self.spider, status='done')
        failed_job = Job.objects.create(spider=self.spider, status='failed')
        
        # Worker should only pick up the queued job
        next_job = self.worker.get_next_job()
        self.assertEqual(next_job.id, queued_job.id)
        
        # Process the job
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('basic_worker.BASE_DIR', Path(temp_dir)):
                self.worker.process_job(next_job)
        
        # Verify only the queued job was affected
        queued_job.refresh_from_db()
        running_job.refresh_from_db()
        done_job.refresh_from_db()
        failed_job.refresh_from_db()
        
        self.assertEqual(queued_job.status, 'done')
        self.assertEqual(running_job.status, 'running')  # Unchanged
        self.assertEqual(done_job.status, 'done')  # Unchanged
        self.assertEqual(failed_job.status, 'failed')  # Unchanged


class WorkerErrorHandlingTest(BaseTestCase):
    """Test worker error handling scenarios."""

    def setUp(self):
        """Set up test data."""
        super().setUp()
        self.worker = BasicWorker(poll_interval=1)
        
        self.user = User.objects.create_user(
            email='error_test@example.com',
            password='testpass123'
        )
        
        self.project = Project.objects.create(
            owner=self.user,
            name='Error Test Project'
        )
        
        self.spider = Spider.objects.create(
            project=self.project,
            name='error-test-spider',
            start_urls_json=['https://example.com']
        )

    @patch('basic_worker.scrape_heading_task')
    def test_worker_handles_scraping_timeout(self, mock_scrape):
        """Test worker handles scraping timeout errors."""
        mock_scrape.side_effect = TimeoutError("Request timed out")
        
        job = Job.objects.create(spider=self.spider, status='queued')
        
        self.worker.process_job(job)
        
        job.refresh_from_db()
        self.assertEqual(job.status, 'failed')
        self.assertIn('Request timed out', job.stats_json['error'])

    @patch('basic_worker.scrape_heading_task')
    def test_worker_handles_connection_error(self, mock_scrape):
        """Test worker handles connection errors."""
        mock_scrape.side_effect = ConnectionError("Connection failed")
        
        job = Job.objects.create(spider=self.spider, status='queued')
        
        self.worker.process_job(job)
        
        job.refresh_from_db()
        self.assertEqual(job.status, 'failed')
        self.assertIn('Connection failed', job.stats_json['error'])

    @patch('basic_worker.scrape_heading_task')
    @patch('basic_worker.BasicWorker.save_results')
    def test_worker_handles_file_save_error(self, mock_save, mock_scrape):
        """Test worker handles file saving errors."""
        mock_scrape.return_value = {'heading': 'Test'}
        mock_save.side_effect = IOError("Cannot write file")
        
        job = Job.objects.create(spider=self.spider, status='queued')
        
        self.worker.process_job(job)
        
        job.refresh_from_db()
        self.assertEqual(job.status, 'failed')
        self.assertIn('Cannot write file', job.stats_json['error'])

    def test_worker_stop_functionality(self):
        """Test worker stop functionality."""
        self.assertTrue(self.worker.running is False)
        
        # Start worker
        self.worker.running = True
        self.assertTrue(self.worker.running)
        
        # Stop worker
        self.worker.stop()
        self.assertFalse(self.worker.running)


class WorkerStatsAndReportingTest(BaseTestCase):
    """Test worker statistics and reporting functionality."""

    def setUp(self):
        """Set up test data."""
        super().setUp()
        self.worker = BasicWorker(poll_interval=1)
        
        self.user = User.objects.create_user(
            email='stats_test@example.com',
            password='testpass123'
        )
        
        self.project = Project.objects.create(
            owner=self.user,
            name='Stats Test Project'
        )
        
        self.spider = Spider.objects.create(
            project=self.project,
            name='stats-test-spider',
            start_urls_json=['https://example.com']
        )

    def test_get_next_job_reports_statistics(self):
        """Test get_next_job method reports job statistics."""
        # Create jobs with different statuses
        Job.objects.create(spider=self.spider, status='queued')
        Job.objects.create(spider=self.spider, status='queued')
        Job.objects.create(spider=self.spider, status='running')
        Job.objects.create(spider=self.spider, status='done')
        Job.objects.create(spider=self.spider, status='failed')
        
        # Capture print output to verify statistics are reported
        with patch('builtins.print') as mock_print:
            job = self.worker.get_next_job()
            
            # Check that statistics were printed
            stats_call = None
            for call_args in mock_print.call_args_list:
                if 'Jobs: Total=' in str(call_args):
                    stats_call = call_args
                    break
            
            self.assertIsNotNone(stats_call)
            stats_message = str(stats_call)
            self.assertIn('Total=5', stats_message)
            self.assertIn('Queued=2', stats_message)
            self.assertIn('Running=1', stats_message)
            self.assertIn('Done=1', stats_message)
            self.assertIn('Failed=1', stats_message)

    @patch('basic_worker.scrape_heading_task')
    def test_job_timing_accuracy(self, mock_scrape):
        """Test job timing is recorded accurately."""
        # Add delay to scraping to test timing
        def delayed_scrape():
            time.sleep(0.1)  # 100ms delay
            return {'heading': 'Test'}
        
        mock_scrape.side_effect = delayed_scrape
        
        job = Job.objects.create(spider=self.spider, status='queued')
        start_time = timezone.now()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('basic_worker.BASE_DIR', Path(temp_dir)):
                self.worker.process_job(job)
        
        job.refresh_from_db()
        
        # Check timing is reasonable
        self.assertIsNotNone(job.started_at)
        self.assertIsNotNone(job.finished_at)
        self.assertGreaterEqual(job.started_at, start_time)
        self.assertGreater(job.finished_at, job.started_at)
        
        # Check duration property
        duration = job.duration
        self.assertIsNotNone(duration)
        self.assertGreaterEqual(duration, 0.1)  # At least the sleep time
        self.assertLess(duration, 1.0)  # But not too long


class FullWorkflowIntegrationTest(APITestCase, BaseTestCase):
    """Comprehensive end-to-end integration test for the complete workflow."""
    
    def setUp(self):
        """Set up test data."""
        super().setUp()
        self.client = APIClient()
        self.worker = BasicWorker(poll_interval=0.1)  # Very short interval for testing
        
        # API endpoints
        self.register_url = '/auth/register/'
        self.login_url = '/auth/login/'
        self.projects_url = '/projects/'
        self.spiders_url = '/spiders/'
        self.jobs_url = '/jobs/'
    
    @patch('basic_worker.scrape_heading_task')
    def test_complete_user_to_job_workflow(self, mock_scrape):
        """Test complete workflow: user registration → project → spider → job → worker processing."""
        mock_scrape.return_value = {'heading': 'End-to-End Test Success'}
        
        # Step 1: Register a new user via API
        registration_data = {
            'email': 'workflow@example.com',
            'password': 'secure123',
            'password_confirm': 'secure123',
            'first_name': 'Workflow',
            'last_name': 'Test'
        }
        
        register_response = self.client.post(
            self.register_url,
            registration_data,
            format='json'
        )
        
        self.assertEqual(register_response.status_code, status.HTTP_201_CREATED)
        self.assertIn('message', register_response.data)
        self.assertIn('user', register_response.data)
        
        # Step 2: Login to get authentication token
        login_data = {
            'email': 'workflow@example.com',
            'password': 'secure123'
        }
        
        login_response = self.client.post(
            self.login_url,
            login_data,
            format='json'
        )
        
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        self.assertIn('access', login_response.data)
        access_token = login_response.data['access']
        
        # Set authentication header for subsequent requests
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        
        # Step 3: Create a project via API
        project_data = {
            'name': 'End-to-End Test Project',
            'notes': 'Project created through complete workflow integration test'
        }
        
        project_response = self.client.post(
            self.projects_url,
            project_data,
            format='json'
        )
        
        self.assertEqual(project_response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', project_response.data)
        self.assertEqual(project_response.data['name'], 'End-to-End Test Project')
        project_id = project_response.data['id']
        
        # Step 4: Create a spider via API
        spider_payload = {
            'Spider': {
                'Name': 'end-to-end-spider',
                'Project': project_id
            },
            'Target': {
                'URL': 'https://httpbin.org/html'
            },
            'Execution': {
                'Parallel_Instances': 1
            }
        }
        spider_response = self.client.post(self.spiders_url, spider_payload, format='json')
        
        self.assertEqual(spider_response.status_code, status.HTTP_201_CREATED)
        self.assertIn('Spider', spider_response.data)
        self.assertEqual(spider_response.data['Spider']['Name'], 'end-to-end-spider')
        # Fetch created spider ID via DB lookup since response schema changed
        spider_id = Spider.objects.get(name='end-to-end-spider', project_id=project_id).id
        
        # Step 5: Create a job via API
        job_data = {
            'spider': spider_id,
            'status': 'queued'
        }
        
        job_response = self.client.post(
            self.jobs_url,
            job_data,
            format='json'
        )
        
        self.assertEqual(job_response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', job_response.data)
        self.assertEqual(job_response.data['status'], 'queued')
        job_id = job_response.data['id']
        
        # Step 6: Process the job with the worker
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('basic_worker.BASE_DIR', Path(temp_dir)):
                # Get the job (like worker would)
                job = Job.objects.get(id=job_id)
                self.assertEqual(job.status, 'queued')
                
                # Process the job (like worker would)
                next_job = self.worker.get_next_job()
                self.assertEqual(next_job.id, job_id)
                
                self.worker.process_job(next_job)
                
                # Step 7: Verify job was processed successfully
                job.refresh_from_db()
                self.assertEqual(job.status, 'done')
                self.assertIsNotNone(job.started_at)
                self.assertIsNotNone(job.finished_at)
                self.assertIsNotNone(job.stats_json)
                
                # Verify stats contain expected data
                stats = job.stats_json
                self.assertIn('success', stats)
                self.assertTrue(stats['success'])
                self.assertIn('file_path', stats)
                
                # Step 8: Verify via API that job is completed
                job_detail_response = self.client.get(f'{self.jobs_url}{job_id}/')
                self.assertEqual(job_detail_response.status_code, status.HTTP_200_OK)
                self.assertEqual(job_detail_response.data['status'], 'done')
                self.assertIsNotNone(job_detail_response.data['duration'])
                
                # Step 9: Verify result file was created and contains expected data
                if 'file_path' in stats:
                    result_file_path = stats['file_path']
                    self.assertTrue(os.path.exists(result_file_path))
                    
                    with open(result_file_path, 'r') as f:
                        result_data = json.load(f)
                    
                    self.assertIn('message', result_data)
                    self.assertIn('data', result_data)
                    self.assertEqual(result_data['data']['heading'], 'End-to-End Test Success')
        
        # Step 10: Verify database relationships are correct
        # Verify user was created
        user = User.objects.get(email='workflow@example.com')
        self.assertEqual(user.first_name, 'Workflow')
        self.assertEqual(user.last_name, 'Test')
        
        # Verify project belongs to user
        project = Project.objects.get(id=project_id)
        self.assertEqual(project.owner, user)
        self.assertEqual(project.name, 'End-to-End Test Project')
        
        # Verify spider belongs to project
        spider = Spider.objects.get(id=spider_id)
        self.assertEqual(spider.project, project)
        self.assertEqual(spider.name, 'end-to-end-spider')
        
        # Verify job belongs to spider
        final_job = Job.objects.get(id=job_id)
        self.assertEqual(final_job.spider, spider)
        self.assertEqual(final_job.status, 'done')
        
        print("✅ Complete workflow test passed: User → Project → Spider → Job → Worker Processing")
    
    def test_workflow_with_authentication_required(self):
        """Test that all API endpoints require proper authentication."""
        # Try to create project without authentication
        project_data = {'name': 'Unauthorized Project'}
        
        response = self.client.post(self.projects_url, project_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Try to create spider without authentication
        spider_data = {
            'name': 'unauthorized-spider',
            'project': 1,
            'start_urls_json': ['https://example.com']
        }
        
        response = self.client.post(self.spiders_url, spider_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Try to create job without authentication
        job_data = {'spider': 1, 'status': 'queued'}
        
        response = self.client.post(self.jobs_url, job_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)