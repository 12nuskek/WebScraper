"""
Utility functions for the worker app.
"""
import logging
from typing import Dict, Any, Optional
from django.utils import timezone
from apps.job.models import Job
from apps.spider.models import Spider

logger = logging.getLogger(__name__)


def get_job_stats() -> Dict[str, int]:
    """Get statistics about jobs in the system."""
    return {
        'queued': Job.objects.filter(status='queued').count(),
        'running': Job.objects.filter(status='running').count(),
        'done': Job.objects.filter(status='done').count(),
        'failed': Job.objects.filter(status='failed').count(),
        'canceled': Job.objects.filter(status='canceled').count(),
    }


def get_next_job() -> Optional[Job]:
    """Get the next job to process (oldest queued job)."""
    return Job.objects.filter(status='queued').order_by('created_at').first()


def create_job_for_spider(spider: Spider) -> Job:
    """Create a new job for a spider."""
    job = Job.objects.create(
        spider=spider,
        status='queued'
    )
    logger.info(f"Created job {job.id} for spider {spider.name}")
    return job


def reset_stuck_jobs(max_running_time_hours: int = 2):
    """
    Reset jobs that have been running for too long back to queued status.
    This is useful for handling worker crashes or hung processes.
    """
    from datetime import timedelta
    
    cutoff_time = timezone.now() - timedelta(hours=max_running_time_hours)
    
    stuck_jobs = Job.objects.filter(
        status='running',
        started_at__lt=cutoff_time
    )
    
    count = stuck_jobs.count()
    if count > 0:
        stuck_jobs.update(
            status='queued',
            started_at=None
        )
        logger.warning(f"Reset {count} stuck jobs back to queued status")
    
    return count


def get_worker_health_info() -> Dict[str, Any]:
    """Get health information about the worker system."""
    job_stats = get_job_stats()
    
    # Check for stuck jobs (running for more than 2 hours)
    stuck_count = reset_stuck_jobs(max_running_time_hours=2)
    
    return {
        'job_stats': job_stats,
        'stuck_jobs_reset': stuck_count,
        'total_jobs': sum(job_stats.values()),
        'healthy': job_stats['running'] < 10,  # Consider unhealthy if too many running jobs
        'timestamp': timezone.now().isoformat()
    }