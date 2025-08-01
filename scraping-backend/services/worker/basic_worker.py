#!/usr/bin/env python
"""
Simplified Worker for Web Scraping Jobs

Clean and simple structure:
1. Shows incoming job data in JSON format
2. Space for your custom code
3. Space to update job values
4. Loops and waits for next job
"""

import os
import sys
import django
import time
import json
from datetime import datetime
from pathlib import Path
from botasaurus.browser import browser, Driver

# Add the Django project to the Python path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
django.setup()

# Import Django models
from apps.job.models import Job
from django.utils import timezone
from django.db import transaction


@browser
def scrape_heading_task(driver: Driver, data):
    """Scrape heading from Omkar Cloud website."""
    # Visit the Omkar Cloud website
    driver.get("https://www.omkar.cloud/")
    
    # Retrieve the heading element's text
    heading = driver.get_text("h1")
    
    # Return the scraped data
    return {
        "heading": heading
    }


class BasicWorker:
    """Simple worker that processes scraping jobs with clear sections."""
    
    def __init__(self, poll_interval=5):
        """Initialize worker with polling interval."""
        self.poll_interval = poll_interval
        self.running = False
        
    def get_next_job(self):
        """Get the next queued job, oldest first."""
        # Debug: Show current job statuses
        total_jobs = Job.objects.count()
        queued_jobs = Job.objects.filter(status='queued').count()
        running_jobs = Job.objects.filter(status='running').count()
        done_jobs = Job.objects.filter(status='done').count()
        failed_jobs = Job.objects.filter(status='failed').count()
        
        print(f"📊 Jobs: Total={total_jobs}, Queued={queued_jobs}, Running={running_jobs}, Done={done_jobs}, Failed={failed_jobs}")
        
        return Job.objects.filter(status='queued').order_by('created_at').first()
    
    def process_job(self, job):
        """Process a single job with clear sections."""
        
        print("\n" + "="*80)
        print(f"PROCESSING JOB {job.id}")
        print("="*80)
        
        try:
            # ================================================================
            # SECTION 1: INCOMING JOB DATA (JSON FORMAT)
            # ================================================================
            print("\n🔸 INCOMING JOB DATA:")
            job_data = {
                'job_id': job.id,
                'spider_name': job.spider.name,
                'status': job.status,
                'created_at': job.created_at.isoformat(),
                'spider_id': job.spider.id,
                # Add any other job fields you want to see
            }
            print(json.dumps(job_data, indent=2))
            
            # ================================================================
            # SECTION 2: YOUR CUSTOM CODE GOES HERE
            # ================================================================
            print("\n🔸 RUNNING YOUR CUSTOM CODE:")
            
            # Update job status to running
            with transaction.atomic():
                job.status = 'running'
                job.started_at = timezone.now()
                job.save()
            print(f"✓ Job {job.id} marked as running")
            
            # YOUR CODE STARTS HERE - Replace this with your own logic
            print("→ Running scraping task...")
            
            # Run the scraping task and get the data
            scraped_data = scrape_heading_task()
            print(f"→ Scraped data: {scraped_data}")
            
            # Process the scraped data into your result format
            result_data = {
                'message': 'Job processed successfully',
                'processed_at': datetime.now().isoformat(),
                'data': scraped_data
            }
            
            # YOUR CODE ENDS HERE
            
            # ================================================================
            # SECTION 3: UPDATE JOB VALUES
            # ================================================================
            print("\n🔸 UPDATING JOB VALUES:")
            
            # Save your results to a file
            file_path = self.save_results(job, result_data)
            print(f"✓ Results saved to: {file_path}")
            
            # Update job with completion status
            with transaction.atomic():
                job.status = 'done'
                job.finished_at = timezone.now()
                job.stats_json = {
                    'completed_at': timezone.now().isoformat(),
                    'file_path': file_path,
                    'success': True
                }
                job.save()
            print(f"✓ Job {job.id} marked as completed")
            
            # Force a small delay to ensure database transaction is committed
            time.sleep(0.5)
            
        except Exception as e:
            print(f"\n❌ ERROR: {str(e)}")
            # Mark job as failed
            with transaction.atomic():
                job.status = 'failed'
                job.finished_at = timezone.now()
                job.stats_json = {
                    'error': str(e),
                    'failed_at': timezone.now().isoformat()
                }
                job.save()
            print(f"✓ Job {job.id} marked as failed")
            
            # Force a small delay to ensure database transaction is committed
            time.sleep(0.5)
    
    def save_results(self, job, data):
        """Save job results to a JSON file."""
        # Create results directory
        results_dir = BASE_DIR / 'media' / 'job_results'
        results_dir.mkdir(parents=True, exist_ok=True)
        
        # Create filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"job_{job.id}_{timestamp}.json"
        file_path = results_dir / filename
        
        # Save the data
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return str(file_path)



    def start(self):
        """Start the worker loop - keeps running and checking for new jobs."""
        print("\n" + "="*80)
        print("🚀 WORKER STARTING")
        print("="*80)
        print(f"Poll interval: {self.poll_interval} seconds")
        print(f"Press Ctrl+C to stop")
        
        self.running = True
        job_count = 0
        
        while self.running:
            try:
                # Check for next job
                job = self.get_next_job()
                
                if job:
                    job_count += 1
                    print(f"\n📋 Found job {job.id} (Total processed: {job_count})")
                    self.process_job(job)
                    print(f"✅ Job {job.id} completed\n")
                else:
                    print(f"⏳ No jobs found. Waiting {self.poll_interval} seconds...")
                    time.sleep(self.poll_interval)
                    
            except KeyboardInterrupt:
                print("\n🛑 Worker stopped by user (Ctrl+C)")
                self.running = False
                break
            except Exception as e:
                print(f"\n❌ Worker error: {str(e)}")
                print(f"⏳ Waiting {self.poll_interval} seconds before retrying...")
                time.sleep(self.poll_interval)
        
        print(f"\n✅ Worker stopped. Processed {job_count} jobs total.")
    
    def stop(self):
        """Stop the worker."""
        self.running = False


if __name__ == '__main__':
    """
    ================================================================
    SIMPLE WORKER STARTUP
    ================================================================
    """
    try:
        print("🔧 Initializing worker...")
        worker = BasicWorker(poll_interval=5)
        worker.start()
        
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
    except Exception as e:
        print(f"\n💥 Fatal error: {str(e)}")
        sys.exit(1)