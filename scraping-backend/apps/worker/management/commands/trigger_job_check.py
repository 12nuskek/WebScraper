"""
Management command to manually trigger job checking.
"""
from django.core.management.base import BaseCommand
from apps.worker.tasks import check_queued_jobs, process_scheduled_jobs


class Command(BaseCommand):
    help = 'Manually trigger job checking and processing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--check-scheduled',
            action='store_true',
            help='Also check for scheduled jobs',
        )

    def handle(self, *args, **options):
        check_scheduled = options['check_scheduled']
        
        self.stdout.write(
            self.style.SUCCESS('Triggering job check...')
        )
        
        # Trigger job check
        result = check_queued_jobs.delay()
        self.stdout.write(f'Queued job check task: {result.id}')
        
        if check_scheduled:
            self.stdout.write(
                self.style.SUCCESS('Triggering scheduled job check...')
            )
            scheduled_result = process_scheduled_jobs.delay()
            self.stdout.write(f'Queued scheduled job check task: {scheduled_result.id}')
        
        self.stdout.write(
            self.style.SUCCESS('Tasks queued successfully!')
        )