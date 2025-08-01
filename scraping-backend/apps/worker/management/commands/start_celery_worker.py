"""
Management command to start Celery worker with proper configuration.
"""
import subprocess
import sys
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Start Celery worker for job processing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--concurrency',
            type=int,
            default=4,
            help='Number of concurrent worker processes (default: 4)',
        )
        parser.add_argument(
            '--queues',
            type=str,
            default='job_processing,job_monitoring',
            help='Comma-separated list of queues to consume (default: job_processing,job_monitoring)',
        )
        parser.add_argument(
            '--loglevel',
            type=str,
            choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
            default='INFO',
            help='Logging level (default: INFO)',
        )

    def handle(self, *args, **options):
        concurrency = options['concurrency']
        queues = options['queues']
        loglevel = options['loglevel']
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Starting Celery worker with {concurrency} processes for queues: {queues}'
            )
        )
        
        # Build celery worker command
        cmd = [
            sys.executable, '-m', 'celery',
            '-A', 'config',
            'worker',
            '--concurrency', str(concurrency),
            '--queues', queues,
            '--loglevel', loglevel,
            '--events',  # Enable monitoring events
        ]
        
        try:
            # Start the worker process
            subprocess.run(cmd, check=True)
        except KeyboardInterrupt:
            self.stdout.write(
                self.style.WARNING('Celery worker stopped by user')
            )
        except subprocess.CalledProcessError as e:
            self.stdout.write(
                self.style.ERROR(f'Celery worker failed: {e}')
            )