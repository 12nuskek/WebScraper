"""
Management command to start Celery Beat scheduler.
"""
import subprocess
import sys
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Start Celery Beat scheduler for periodic tasks'

    def add_arguments(self, parser):
        parser.add_argument(
            '--loglevel',
            type=str,
            choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
            default='INFO',
            help='Logging level (default: INFO)',
        )

    def handle(self, *args, **options):
        loglevel = options['loglevel']
        
        self.stdout.write(
            self.style.SUCCESS('Starting Celery Beat scheduler')
        )
        
        # Build celery beat command
        cmd = [
            sys.executable, '-m', 'celery',
            '-A', 'config',
            'beat',
            '--loglevel', loglevel,
            '--scheduler', 'django_celery_beat.schedulers:DatabaseScheduler',
        ]
        
        try:
            # Start the beat process
            subprocess.run(cmd, check=True)
        except KeyboardInterrupt:
            self.stdout.write(
                self.style.WARNING('Celery Beat stopped by user')
            )
        except subprocess.CalledProcessError as e:
            self.stdout.write(
                self.style.ERROR(f'Celery Beat failed: {e}')
            )