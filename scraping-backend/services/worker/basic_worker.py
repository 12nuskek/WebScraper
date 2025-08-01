#!/usr/bin/env python
"""
Basic Worker for Web Scraping Jobs

This worker runs independently and picks up the next queued job from the database.
It processes jobs by displaying all job and related record information as JSON.
No Redis or Celery required - just a simple polling mechanism.
"""

import os
import sys
import django
import time
import logging
from datetime import datetime
from pathlib import Path

# Add the Django project to the Python path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
django.setup()

# Now we can import Django models
from apps.job.models import Job
from apps.spider.models import Spider
from django.utils import timezone
from django.db import transaction
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('worker.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class BasicWorker:
    """Basic worker that processes scraping jobs."""
    
    def __init__(self, poll_interval=5):
        """
        Initialize the worker.
        
        Args:
            poll_interval (int): Seconds to wait between checking for new jobs
        """
        self.poll_interval = poll_interval
        self.running = False
        
    def get_next_job(self):
        """Get the next queued job, ordered by creation time (oldest first)."""
        return Job.objects.filter(status='queued').order_by('created_at').first()
    
    def print_job_information(self, job):
        """Print all job and related record information as JSON."""
        
        # Get all related information
        spider = job.spider
        project = spider.project
        owner = project.owner
        
        # Build comprehensive information structure
        job_info = {
            'job': {
                'id': job.id,
                'status': job.status,
                'started_at': job.started_at.isoformat() if job.started_at else None,
                'finished_at': job.finished_at.isoformat() if job.finished_at else None,
                'created_at': job.created_at.isoformat(),
                'stats_json': job.stats_json,
                'duration_seconds': job.duration
            },
            'spider': {
                'id': spider.id,
                'name': spider.name,
                'start_urls_json': spider.start_urls_json,
                'settings_json': spider.settings_json,
                'parse_rules_json': spider.parse_rules_json,
                'created_at': spider.created_at.isoformat()
            },
            'project': {
                'id': project.id,
                'name': project.name,
                'notes': project.notes,
                'created_at': project.created_at.isoformat()
            },
            'owner': {
                'id': owner.id,
                'email': owner.email,
                'first_name': owner.first_name,
                'last_name': owner.last_name,
                'date_joined': owner.date_joined.isoformat()
            }
        }
        
        # Print as formatted JSON
        print("\n" + "="*80)
        print("JOB AND RELATED RECORDS INFORMATION")
        print("="*80)
        print(json.dumps(job_info, indent=2, ensure_ascii=False))
        print("="*80 + "\n")
        
        return job_info
    
    def save_job_data_to_json(self, job, job_info):
        """
        Save job and related data to a JSON file in the media directory.
        
        Args:
            job (Job): The job instance
            job_info (dict): The comprehensive job information dictionary
        """
        try:
            # Create media directory path
            media_dir = BASE_DIR / 'media' / 'job_results'
            media_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate filename with job ID and timestamp
            timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
            filename = f"job_{job.id}_{timestamp}.json"
            file_path = media_dir / filename
            
            # Add metadata to the job info
            enhanced_job_info = {
                'metadata': {
                    'exported_at': timezone.now().isoformat(),
                    'worker_version': '1.0',
                    'file_format': 'json',
                    'job_id': job.id
                },
                'data': job_info
            }
            
            # Write to JSON file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(enhanced_job_info, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Job data saved to: {file_path}")
            return str(file_path)
            
        except Exception as e:
            logger.error(f"Failed to save job data to JSON file: {str(e)}")
            return None
    
    def process_job(self, job):
        """
        Process a single job.
        
        Args:
            job (Job): The job to process
        """
        logger.info(f"Processing job {job.id} for spider '{job.spider.name}' - displaying JSON information")
        
        try:
            # Update job status to running
            with transaction.atomic():
                job.status = 'running'
                job.started_at = timezone.now()
                job.save()
            
            # Get spider configuration
            spider = job.spider
            start_urls = spider.start_urls_json or []
            settings = spider.settings_json or {}
            parse_rules = spider.parse_rules_json or {}
            
            # Print all job and related information as JSON
            job_info = self.print_job_information(job)
            
            # Save job data to JSON file in media directory
            json_file_path = self.save_job_data_to_json(job, job_info)
            
            # Basic scraping logic (you can expand this)
            results = self.execute_spider(start_urls, settings, parse_rules)
            
            # Update job as completed
            with transaction.atomic():
                job.status = 'done'
                job.finished_at = timezone.now()
                job.stats_json = {
                    'urls_processed': len(start_urls),
                    'information_displayed': len(results),
                    'duration_seconds': (job.finished_at - job.started_at).total_seconds(),
                    'json_file_saved': json_file_path is not None,
                    'json_file_path': json_file_path
                }
                job.save()
                
            if json_file_path:
                logger.info(f"Job {job.id} completed successfully. Displayed information for {len(results)} URLs. JSON saved to: {json_file_path}")
            else:
                logger.info(f"Job {job.id} completed successfully. Displayed information for {len(results)} URLs. (JSON save failed)")
            
        except Exception as e:
            logger.error(f"Job {job.id} failed: {str(e)}")
            
            # Update job as failed
            with transaction.atomic():
                job.status = 'failed'
                job.finished_at = timezone.now()
                job.stats_json = {
                    'error': str(e),
                    'duration_seconds': (job.finished_at - job.started_at).total_seconds() if job.started_at else 0
                }
                job.save()
    
    def execute_spider(self, start_urls, settings, parse_rules):
        """
        Process job information (JSON display only).
        
        Args:
            start_urls (list): List of URLs from spider
            settings (dict): Spider settings
            parse_rules (dict): Parsing rules
            
        Returns:
            list: Mock results for job completion
        """
        # Return mock results indicating the job was "processed" (displayed)
        results = []
        for url in start_urls:
            results.append({
                'url': url,
                'action': 'displayed_in_json',
                'processed_at': timezone.now().isoformat()
            })
        
        return results
    
    def extract_data(self, html_content, parse_rules):
        """
        Extract data based on parse rules.
        
        Args:
            html_content (str): HTML content to parse
            parse_rules (dict): Rules for data extraction
            
        Returns:
            dict: Extracted data
        """
        # This is a placeholder for more sophisticated parsing
        # You could integrate BeautifulSoup, lxml, or other parsing libraries here
        extracted = {
            'content_preview': html_content[:200] + '...' if len(html_content) > 200 else html_content,
            'rules_applied': list(parse_rules.keys()) if parse_rules else []
        }
        
        return extracted
    
    def start(self):
        """Start the worker loop."""
        logger.info("Starting basic worker...")
        self.running = True
        
        while self.running:
            try:
                # Get next job
                job = self.get_next_job()
                
                if job:
                    self.process_job(job)
                else:
                    logger.debug(f"No queued jobs found. Waiting {self.poll_interval} seconds...")
                    time.sleep(self.poll_interval)
                    
            except KeyboardInterrupt:
                logger.info("Worker interrupted by user")
                self.running = False
                break
            except Exception as e:
                logger.error(f"Worker error: {str(e)}")
                time.sleep(self.poll_interval)
        
        logger.info("Worker stopped")
    
    def stop(self):
        """Stop the worker."""
        self.running = False


if __name__ == '__main__':
    # Create and start the worker
    worker = BasicWorker(poll_interval=5)
    
    try:
        worker.start()
    except KeyboardInterrupt:
        logger.info("Shutting down worker...")
        worker.stop()