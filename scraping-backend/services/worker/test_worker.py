#!/usr/bin/env python
"""
Test script to create a sample job and demonstrate the worker functionality.

This script creates a test spider and job that the worker can process.
"""

import os
import sys
import django
from pathlib import Path

# Add the Django project to the Python path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
django.setup()

from apps.projects.models import Project
from apps.spider.models import Spider
from apps.job.models import Job
from apps.auth.models import User


def create_test_job():
    """Create a test job for the worker to process."""
    
    print("Creating test job...")
    
    # Get or create a test user
    user, created = User.objects.get_or_create(
        email='test_worker_user@example.com',
        defaults={
            'first_name': 'Test',
            'last_name': 'Worker'
        }
    )
    if created:
        print(f"Created test user: {user.email}")
    
    # Get or create a test project
    project, created = Project.objects.get_or_create(
        name='Test Worker Project',
        owner=user,
        defaults={
            'notes': 'Project for testing the basic worker'
        }
    )
    if created:
        print(f"Created test project: {project.name}")
    
    # Create a test spider
    spider, created = Spider.objects.get_or_create(
        project=project,
        name='test_spider',
        defaults={
            'start_urls_json': [
                'https://example.com/page1',
                'https://example.com/page2',
                'https://example.com/page3'
            ],
            'settings_json': {
                'display_mode': 'json_info_only',
                'timeout': 30,
                'headers': {
                    'User-Agent': 'BasicWorker/1.0 Display'
                }
            },
            'parse_rules_json': {
                'display_all_info': True,
                'include_relationships': True
            }
        }
    )
    if created:
        print(f"Created test spider: {spider.name}")
        print(f"  Start URLs: {spider.start_urls_json}")
    
    # Create a test job
    job = Job.objects.create(
        spider=spider,
        status='queued'
    )
    print(f"Created test job: {job.id}")
    print(f"  Status: {job.status}")
    print(f"  Created: {job.created_at}")
    
    return job


def check_job_status(job_id):
    """Check the status of a job."""
    try:
        job = Job.objects.get(id=job_id)
        print(f"\nJob {job_id} Status Check:")
        print(f"  Status: {job.status}")
        print(f"  Started: {job.started_at}")
        print(f"  Finished: {job.finished_at}")
        print(f"  Duration: {job.duration} seconds" if job.duration else "  Duration: N/A")
        if job.stats_json:
            print(f"  Stats: {job.stats_json}")
        return job
    except Job.DoesNotExist:
        print(f"Job {job_id} not found")
        return None


def list_all_jobs():
    """List all jobs in the database."""
    jobs = Job.objects.all().order_by('-created_at')
    
    print(f"\nAll Jobs ({jobs.count()}):")
    print("-" * 80)
    print(f"{'ID':<5} {'Spider':<20} {'Status':<10} {'Created':<20} {'Duration':<10}")
    print("-" * 80)
    
    for job in jobs:
        duration = f"{job.duration:.1f}s" if job.duration else "N/A"
        print(f"{job.id:<5} {job.spider.name:<20} {job.status:<10} {job.created_at.strftime('%Y-%m-%d %H:%M:%S'):<20} {duration:<10}")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Test the basic worker')
    parser.add_argument('action', choices=['create', 'status', 'list'], 
                       help='Action to perform')
    parser.add_argument('--job-id', type=int, help='Job ID for status check')
    
    args = parser.parse_args()
    
    if args.action == 'create':
        job = create_test_job()
        print(f"\nTest job created! Run the worker to process job {job.id}")
        print("To start the worker:")
        print("  cd scraping-backend/services/worker")
        print("  python run_worker.py")
        
    elif args.action == 'status':
        if not args.job_id:
            print("Please provide --job-id for status check")
            sys.exit(1)
        check_job_status(args.job_id)
        
    elif args.action == 'list':
        list_all_jobs()