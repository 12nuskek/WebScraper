"""
Celery tasks for job processing.
"""
import time
from celery import shared_task
from celery.utils.log import get_task_logger
from django.db import transaction
from django.utils import timezone

from apps.job.models import Job
from apps.request.models import RequestQueue
from apps.response.models import Response
from apps.session.models import Session
from apps.proxy.models import Proxy
from apps.schedule.models import Schedule

logger = get_task_logger(__name__)


@shared_task(bind=True, name='apps.worker.tasks.process_job')
def process_job(self, job_id, pause_minutes=5):
    """
    Process a specific job by ID and display related information.
    """
    try:
        job = Job.objects.select_related('spider__project__owner').get(id=job_id)
        
        # Mark job as running
        with transaction.atomic():
            job.status = 'running'
            job.started_at = timezone.now()
            job.save(update_fields=['status', 'started_at'])
        
        logger.info(f"Starting job processing for Job {job_id}")
        
        # Display job information
        job_info = display_job_info(job)
        logger.info(job_info)
        
        # Simulate job processing
        logger.info(f"Processing job for {pause_minutes} minutes...")
        time.sleep(pause_minutes * 60)
        
        # Mark job as completed
        with transaction.atomic():
            job.status = 'done'
            job.finished_at = timezone.now()
            job.save(update_fields=['status', 'finished_at'])
        
        logger.info(f"Job {job_id} completed successfully")
        return f"Job {job_id} completed successfully"
        
    except Job.DoesNotExist:
        logger.error(f"Job {job_id} not found")
        return f"Job {job_id} not found"
    except Exception as e:
        logger.error(f"Error processing job {job_id}: {str(e)}")
        if 'job' in locals():
            job.status = 'failed'
            job.finished_at = timezone.now()
            job.save(update_fields=['status', 'finished_at'])
        return f"Job {job_id} failed: {str(e)}"


@shared_task(bind=True, name='apps.worker.tasks.check_queued_jobs')
def check_queued_jobs(self):
    """
    Check for queued jobs and process them asynchronously.
    """
    try:
        # Find next available job
        with transaction.atomic():
            job = Job.objects.select_for_update().filter(
                status='queued'
            ).order_by('created_at').first()
            
            if not job:
                logger.info("No queued jobs available")
                return "No queued jobs available"
        
        # Process the job asynchronously
        result = process_job.delay(job.id)
        logger.info(f"Queued job {job.id} for processing. Task ID: {result.id}")
        return f"Queued job {job.id} for processing"
        
    except Exception as e:
        logger.error(f"Error checking queued jobs: {str(e)}")
        return f"Error: {str(e)}"


@shared_task(bind=True, name='apps.worker.tasks.process_scheduled_jobs')
def process_scheduled_jobs(self):
    """
    Check for due scheduled jobs and create job instances.
    """
    try:
        due_schedules = Schedule.get_due_schedules()
        processed_count = 0
        
        for schedule in due_schedules:
            # Create a new job for this schedule
            job = Job.objects.create(
                spider=schedule.spider,
                status='queued'
            )
            
            # Mark schedule as executed
            schedule.mark_executed()
            
            logger.info(f"Created job {job.id} from schedule {schedule.id}")
            processed_count += 1
        
        if processed_count > 0:
            logger.info(f"Created {processed_count} jobs from due schedules")
        
        return f"Created {processed_count} jobs from due schedules"
        
    except Exception as e:
        logger.error(f"Error processing scheduled jobs: {str(e)}")
        return f"Error: {str(e)}"


def display_job_info(job):
    """
    Generate comprehensive information about the job and related objects.
    Returns a formatted string instead of printing to stdout.
    """
    lines = []
    lines.append('=' * 80)
    lines.append('JOB PROCESSING STARTED')
    lines.append('=' * 80)
    
    # Project Information
    project = job.spider.project
    lines.append('PROJECT INFORMATION:')
    lines.append(f'  ID: {project.id}')
    lines.append(f'  Name: {project.name}')
    owner_email = getattr(project.owner, 'email', 'Unknown') if project.owner else 'No owner'
    lines.append(f'  Owner: {owner_email}')
    lines.append(f'  Notes: {project.notes or "No notes"}')
    lines.append(f'  Created: {project.created_at}')
    lines.append('')
    
    # Spider Information
    spider = job.spider
    lines.append('SPIDER INFORMATION:')
    lines.append(f'  ID: {spider.id}')
    lines.append(f'  Name: {spider.name}')
    lines.append(f'  Start URLs: {spider.start_urls_json}')
    lines.append(f'  Settings: {spider.settings_json or "No settings"}')
    lines.append(f'  Parse Rules: {spider.parse_rules_json or "No parse rules"}')
    lines.append(f'  Created: {spider.created_at}')
    lines.append('')
    
    # Job Information
    lines.append('JOB INFORMATION:')
    lines.append(f'  ID: {job.id}')
    lines.append(f'  Status: {job.status}')
    lines.append(f'  Started At: {job.started_at or "Not started"}')
    lines.append(f'  Finished At: {job.finished_at or "Not finished"}')
    lines.append(f'  Stats: {job.stats_json or "No stats"}')
    lines.append(f'  Created: {job.created_at}')
    lines.append(f'  Duration: {job.duration or "N/A"} seconds')
    lines.append('')
    
    # Request Queue Information
    requests = RequestQueue.objects.filter(job=job)
    lines.append('REQUEST QUEUE INFORMATION:')
    lines.append(f'  Total Requests: {requests.count()}')
    
    # Show status breakdown
    status_counts = {}
    for status, _ in RequestQueue.STATUS_CHOICES:
        count = requests.filter(status=status).count()
        if count > 0:
            status_counts[status] = count
    
    if status_counts:
        lines.append(f'  Status Breakdown: {status_counts}')
    
    if requests.exists():
        for request in requests[:5]:  # Show first 5 requests
            lines.append(f'    Request {request.id}:')
            lines.append(f'      URL: {request.url[:100]}{"..." if len(request.url) > 100 else ""}')
            lines.append(f'      Method: {request.method}')
            lines.append(f'      Status: {request.status}')
            lines.append(f'      Priority: {request.priority}')
            lines.append(f'      Retries: {request.retries}/{request.max_retries}')
            lines.append(f'      Depth: {request.depth}')
            lines.append(f'      Scheduled At: {request.scheduled_at}')
            lines.append(f'      Picked At: {request.picked_at or "Not picked"}')
            header_count = len(request.headers_json) if request.headers_json else 0
            lines.append(f'      Headers: {header_count} headers')
            lines.append('')
        
        if requests.count() > 5:
            lines.append(f'    ... and {requests.count() - 5} more requests')
    else:
        lines.append('    No requests found for this job')
    lines.append('')
    
    # Session Information
    sessions = Session.objects.filter(spider=spider)
    lines.append('SESSION INFORMATION:')
    lines.append(f'  Total Sessions: {sessions.count()}')
    
    if sessions.exists():
        for session in sessions:
            lines.append(f'    Session {session.id}:')
            lines.append(f'      Label: {session.label or "default"}')
            lines.append(f'      Valid Until: {session.valid_until or "No expiration"}')
            lines.append(f'      Is Valid: {session.is_valid}')
            lines.append(f'      Cookies: {len(session.cookies_json or {}) if session.cookies_json else 0} cookies')
            lines.append(f'      Headers: {len(session.headers_json or {}) if session.headers_json else 0} headers')
            lines.append(f'      Created: {session.created_at}')
            lines.append('')
    else:
        lines.append('    No sessions found for this spider')
    lines.append('')
    
    # Proxy Information
    proxies = Proxy.get_active_proxies()[:5]  # Show first 5 active proxies
    lines.append('PROXY POOL INFORMATION:')
    lines.append(f'  Total Active Proxies: {Proxy.get_active_proxies().count()}')
    lines.append(f'  Total Healthy Proxies: {Proxy.get_healthy_proxies().count()}')
    
    if proxies.exists():
        for proxy in proxies:
            lines.append(f'    Proxy {proxy.id}:')
            lines.append(f'      URI: {proxy.masked_uri}')
            lines.append(f'      Hostname: {proxy.hostname}')
            lines.append(f'      Port: {proxy.port}')
            lines.append(f'      Scheme: {proxy.scheme}')
            lines.append(f'      Is Active: {proxy.is_active}')
            lines.append(f'      Is Healthy: {proxy.is_healthy}')
            lines.append(f'      Fail Count: {proxy.fail_count}')
            lines.append(f'      Last OK: {proxy.last_ok_at or "Never"}')
            lines.append(f'      Success Rate: {proxy.success_rate or "N/A"}%')
            lines.append('')
            
        total_proxies = Proxy.get_active_proxies().count()
        if total_proxies > 5:
            lines.append(f'    ... and {total_proxies - 5} more active proxies')
    else:
        lines.append('    No active proxies found')
    lines.append('')
    
    # Response Information
    responses = Response.objects.filter(request__job=job)
    lines.append('RESPONSE INFORMATION:')
    lines.append(f'  Total Responses: {responses.count()}')
    
    if responses.exists():
        # Status code breakdown
        success_count = responses.filter(status_code__gte=200, status_code__lt=300).count()
        redirect_count = responses.filter(status_code__gte=300, status_code__lt=400).count() 
        client_error_count = responses.filter(status_code__gte=400, status_code__lt=500).count()
        server_error_count = responses.filter(status_code__gte=500).count()
        
        lines.append(f'  Success (2xx): {success_count}')
        lines.append(f'  Redirects (3xx): {redirect_count}')
        lines.append(f'  Client Errors (4xx): {client_error_count}')
        lines.append(f'  Server Errors (5xx): {server_error_count}')
        
        # Show sample responses
        for response in responses[:3]:  # Show first 3 responses
            lines.append(f'    Response {response.id}:')
            lines.append(f'      Request ID: {response.request.id}')
            lines.append(f'      Final URL: {(response.final_url or "N/A")[:100]}{"..." if response.final_url and len(response.final_url) > 100 else ""}')
            lines.append(f'      Status Code: {response.status_code or "N/A"}')
            lines.append(f'      Latency: {response.latency_ms or "N/A"} ms')
            lines.append(f'      Body Size: {response.body_size or 0} bytes')
            lines.append(f'      From Cache: {response.from_cache}')
            lines.append(f'      Fetched At: {response.fetched_at}')
            lines.append('')
            
        if responses.count() > 3:
            lines.append(f'    ... and {responses.count() - 3} more responses')
    else:
        lines.append('    No responses found for this job')
    lines.append('')
    
    # Schedule Information (if spider has schedules)
    schedules = Schedule.objects.filter(spider=spider)
    if schedules.exists():
        lines.append('SCHEDULE INFORMATION:')
        lines.append(f'  Total Schedules: {schedules.count()}')
        
        for schedule in schedules:
            lines.append(f'    Schedule {schedule.id}:')
            lines.append(f'      Cron Expression: {schedule.cron_expr}')
            lines.append(f'      Timezone: {schedule.timezone}')
            lines.append(f'      Enabled: {schedule.enabled}')
            lines.append(f'      Next Run: {schedule.next_run_at or "Not scheduled"}')
            if schedule.next_run_at:
                lines.append(f'      Time Until Next Run: {schedule.time_until_next_run or "N/A"}')
                lines.append(f'      Is Overdue: {schedule.is_overdue}')
            lines.append('')
    
    lines.append('=' * 80)
    
    return '\n'.join(lines)