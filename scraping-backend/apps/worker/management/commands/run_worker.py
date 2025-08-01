import time
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.job.models import Job
from apps.request.models import RequestQueue
from apps.response.models import Response
from apps.session.models import Session
from apps.proxy.models import Proxy
from apps.schedule.models import Schedule


class Command(BaseCommand):
    help = 'Run worker to process scraping jobs'

    def add_arguments(self, parser):
        parser.add_argument(
            '--continuous',
            action='store_true',
            help='Run continuously in a loop',
        )
        parser.add_argument(
            '--pause-minutes',
            type=int,
            default=5,
            help='Minutes to pause between job processing (default: 5)',
        )

    def handle(self, *args, **options):
        continuous = options['continuous']
        pause_minutes = options['pause_minutes']
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Starting worker process (pause: {pause_minutes} minutes, continuous: {continuous})'
            )
        )
        
        if continuous:
            while True:
                self.process_next_job(pause_minutes)
        else:
            self.process_next_job(pause_minutes)

    def process_next_job(self, pause_minutes):
        """Process the next available job and display related information."""
        
        try:
            # Select next available job with atomic transaction
            with transaction.atomic():
                job = Job.objects.select_for_update().filter(
                    status='queued'
                ).order_by('created_at').first()
                
                if not job:
                    self.stdout.write(
                        self.style.WARNING('No queued jobs available')
                    )
                    self.stdout.write(f'Waiting {pause_minutes} minutes before checking again...')
                    time.sleep(pause_minutes * 60)
                    return
                
                # Mark job as running
                job.status = 'running'
                job.started_at = timezone.now()
                job.save(update_fields=['status', 'started_at'])
            
            # Display job and related information
            self.display_job_info(job)
            
            # Simulate job processing - in real implementation, this would do actual scraping
            self.stdout.write(
                self.style.WARNING(f'Processing job for {pause_minutes} minutes...')
            )
            time.sleep(pause_minutes * 60)
            
            # Mark job as completed (for demo purposes)
            with transaction.atomic():
                job.status = 'done'
                job.finished_at = timezone.now()
                job.save(update_fields=['status', 'finished_at'])
            
            self.stdout.write(
                self.style.SUCCESS(f'Job {job.id} completed successfully')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error processing job: {str(e)}')
            )
            if 'job' in locals():
                job.status = 'failed'
                job.finished_at = timezone.now()
                job.save(update_fields=['status', 'finished_at'])

    def display_job_info(self, job):
        """Display comprehensive information about the job and related objects."""
        
        self.stdout.write('=' * 80)
        self.stdout.write(self.style.SUCCESS('JOB PROCESSING STARTED'))
        self.stdout.write('=' * 80)
        
        # Project Information
        project = job.spider.project
        self.stdout.write(self.style.HTTP_INFO('PROJECT INFORMATION:'))
        self.stdout.write(f'  ID: {project.id}')
        self.stdout.write(f'  Name: {project.name}')
        # Safely access owner email
        owner_email = getattr(project.owner, 'email', 'Unknown') if project.owner else 'No owner'
        self.stdout.write(f'  Owner: {owner_email}')
        self.stdout.write(f'  Notes: {project.notes or "No notes"}')
        self.stdout.write(f'  Created: {project.created_at}')
        self.stdout.write()
        
        # Spider Information
        spider = job.spider
        self.stdout.write(self.style.HTTP_INFO('SPIDER INFORMATION:'))
        self.stdout.write(f'  ID: {spider.id}')
        self.stdout.write(f'  Name: {spider.name}')
        self.stdout.write(f'  Start URLs: {spider.start_urls_json}')
        self.stdout.write(f'  Settings: {spider.settings_json or "No settings"}')
        self.stdout.write(f'  Parse Rules: {spider.parse_rules_json or "No parse rules"}')
        self.stdout.write(f'  Created: {spider.created_at}')
        self.stdout.write()
        
        # Job Information
        self.stdout.write(self.style.HTTP_INFO('JOB INFORMATION:'))
        self.stdout.write(f'  ID: {job.id}')
        self.stdout.write(f'  Status: {job.status}')
        self.stdout.write(f'  Started At: {job.started_at or "Not started"}')
        self.stdout.write(f'  Finished At: {job.finished_at or "Not finished"}')
        self.stdout.write(f'  Stats: {job.stats_json or "No stats"}')
        self.stdout.write(f'  Created: {job.created_at}')
        self.stdout.write(f'  Duration: {job.duration or "N/A"} seconds')
        self.stdout.write()
        
        # Request Queue Information
        requests = RequestQueue.objects.filter(job=job)
        self.stdout.write(self.style.HTTP_INFO('REQUEST QUEUE INFORMATION:'))
        self.stdout.write(f'  Total Requests: {requests.count()}')
        
        # Show status breakdown
        status_counts = {}
        for status, _ in RequestQueue.STATUS_CHOICES:
            count = requests.filter(status=status).count()
            if count > 0:
                status_counts[status] = count
        
        if status_counts:
            self.stdout.write(f'  Status Breakdown: {status_counts}')
        
        if requests.exists():
            for request in requests[:5]:  # Show first 5 requests
                self.stdout.write(f'    Request {request.id}:')
                self.stdout.write(f'      URL: {request.url[:100]}{"..." if len(request.url) > 100 else ""}')
                self.stdout.write(f'      Method: {request.method}')
                self.stdout.write(f'      Status: {request.status}')
                self.stdout.write(f'      Priority: {request.priority}')
                self.stdout.write(f'      Retries: {request.retries}/{request.max_retries}')
                self.stdout.write(f'      Depth: {request.depth}')
                self.stdout.write(f'      Scheduled At: {request.scheduled_at}')
                self.stdout.write(f'      Picked At: {request.picked_at or "Not picked"}')
                header_count = len(request.headers_json) if request.headers_json else 0
                self.stdout.write(f'      Headers: {header_count} headers')
                self.stdout.write()
            
            if requests.count() > 5:
                self.stdout.write(f'    ... and {requests.count() - 5} more requests')
        else:
            self.stdout.write('    No requests found for this job')
        self.stdout.write()
        
        # Session Information
        sessions = Session.objects.filter(spider=spider)
        self.stdout.write(self.style.HTTP_INFO('SESSION INFORMATION:'))
        self.stdout.write(f'  Total Sessions: {sessions.count()}')
        
        if sessions.exists():
            for session in sessions:
                self.stdout.write(f'    Session {session.id}:')
                self.stdout.write(f'      Label: {session.label or "default"}')
                self.stdout.write(f'      Valid Until: {session.valid_until or "No expiration"}')
                self.stdout.write(f'      Is Valid: {session.is_valid}')
                self.stdout.write(f'      Cookies: {len(session.cookies_json or {}) if session.cookies_json else 0} cookies')
                self.stdout.write(f'      Headers: {len(session.headers_json or {}) if session.headers_json else 0} headers')
                self.stdout.write(f'      Created: {session.created_at}')
                self.stdout.write()
        else:
            self.stdout.write('    No sessions found for this spider')
        self.stdout.write()
        
        # Proxy Information
        proxies = Proxy.get_active_proxies()[:5]  # Show first 5 active proxies
        self.stdout.write(self.style.HTTP_INFO('PROXY POOL INFORMATION:'))
        self.stdout.write(f'  Total Active Proxies: {Proxy.get_active_proxies().count()}')
        self.stdout.write(f'  Total Healthy Proxies: {Proxy.get_healthy_proxies().count()}')
        
        if proxies.exists():
            for proxy in proxies:
                self.stdout.write(f'    Proxy {proxy.id}:')
                self.stdout.write(f'      URI: {proxy.masked_uri}')
                self.stdout.write(f'      Hostname: {proxy.hostname}')
                self.stdout.write(f'      Port: {proxy.port}')
                self.stdout.write(f'      Scheme: {proxy.scheme}')
                self.stdout.write(f'      Is Active: {proxy.is_active}')
                self.stdout.write(f'      Is Healthy: {proxy.is_healthy}')
                self.stdout.write(f'      Fail Count: {proxy.fail_count}')
                self.stdout.write(f'      Last OK: {proxy.last_ok_at or "Never"}')
                self.stdout.write(f'      Success Rate: {proxy.success_rate or "N/A"}%')
                self.stdout.write()
                
            total_proxies = Proxy.get_active_proxies().count()
            if total_proxies > 5:
                self.stdout.write(f'    ... and {total_proxies - 5} more active proxies')
        else:
            self.stdout.write('    No active proxies found')
        self.stdout.write()
        
        # Response Information
        responses = Response.objects.filter(request__job=job)
        self.stdout.write(self.style.HTTP_INFO('RESPONSE INFORMATION:'))
        self.stdout.write(f'  Total Responses: {responses.count()}')
        
        if responses.exists():
            # Status code breakdown
            success_count = responses.filter(status_code__gte=200, status_code__lt=300).count()
            redirect_count = responses.filter(status_code__gte=300, status_code__lt=400).count() 
            client_error_count = responses.filter(status_code__gte=400, status_code__lt=500).count()
            server_error_count = responses.filter(status_code__gte=500).count()
            
            self.stdout.write(f'  Success (2xx): {success_count}')
            self.stdout.write(f'  Redirects (3xx): {redirect_count}')
            self.stdout.write(f'  Client Errors (4xx): {client_error_count}')
            self.stdout.write(f'  Server Errors (5xx): {server_error_count}')
            
            # Show sample responses
            for response in responses[:3]:  # Show first 3 responses
                self.stdout.write(f'    Response {response.id}:')
                self.stdout.write(f'      Request ID: {response.request.id}')
                self.stdout.write(f'      Final URL: {(response.final_url or "N/A")[:100]}{"..." if response.final_url and len(response.final_url) > 100 else ""}')
                self.stdout.write(f'      Status Code: {response.status_code or "N/A"}')
                self.stdout.write(f'      Latency: {response.latency_ms or "N/A"} ms')
                self.stdout.write(f'      Body Size: {response.body_size or 0} bytes')
                self.stdout.write(f'      From Cache: {response.from_cache}')
                self.stdout.write(f'      Fetched At: {response.fetched_at}')
                self.stdout.write()
                
            if responses.count() > 3:
                self.stdout.write(f'    ... and {responses.count() - 3} more responses')
        else:
            self.stdout.write('    No responses found for this job')
        self.stdout.write()
        
        # Schedule Information (if spider has schedules)
        schedules = Schedule.objects.filter(spider=spider)
        if schedules.exists():
            self.stdout.write(self.style.HTTP_INFO('SCHEDULE INFORMATION:'))
            self.stdout.write(f'  Total Schedules: {schedules.count()}')
            
            for schedule in schedules:
                self.stdout.write(f'    Schedule {schedule.id}:')
                self.stdout.write(f'      Cron Expression: {schedule.cron_expr}')
                self.stdout.write(f'      Timezone: {schedule.timezone}')
                self.stdout.write(f'      Enabled: {schedule.enabled}')
                self.stdout.write(f'      Next Run: {schedule.next_run_at or "Not scheduled"}')
                if schedule.next_run_at:
                    self.stdout.write(f'      Time Until Next Run: {schedule.time_until_next_run or "N/A"}')
                    self.stdout.write(f'      Is Overdue: {schedule.is_overdue}')
                self.stdout.write()
        
        self.stdout.write('=' * 80)