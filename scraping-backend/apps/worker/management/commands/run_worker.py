"""
Django management command to run the web scraping worker.
"""
import logging
import signal
import sys
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from apps.worker.worker_service import WorkerManager

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Run the web scraping worker process'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--browser',
            choices=['chromium', 'firefox', 'webkit'],
            default='chromium',
            help='Browser type to use (default: chromium)'
        )
        parser.add_argument(
            '--headless',
            action='store_true',
            default=True,
            help='Run browser in headless mode (default: True)'
        )
        parser.add_argument(
            '--headed',
            action='store_true',
            help='Run browser in headed mode (opposite of --headless)'
        )
        parser.add_argument(
            '--concurrent-jobs',
            type=int,
            default=1,
            help='Number of jobs to process concurrently (default: 1)'
        )
        parser.add_argument(
            '--job-timeout',
            type=int,
            default=300,
            help='Timeout for each job in seconds (default: 300)'
        )
        parser.add_argument(
            '--log-level',
            choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
            default='INFO',
            help='Set the logging level (default: INFO)'
        )
    
    def handle(self, *args, **options):
        # Set up logging
        log_level = getattr(logging, options['log_level'])
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler('worker.log')
            ]
        )
        
        # Determine headless mode
        headless = options['headless'] and not options['headed']
        
        # Validate options
        if options['concurrent_jobs'] < 1:
            raise CommandError('concurrent-jobs must be at least 1')
        
        if options['job_timeout'] < 1:
            raise CommandError('job-timeout must be at least 1 second')
        
        # Create worker manager
        worker_manager = WorkerManager(
            browser_type=options['browser'],
            headless=headless,
            concurrent_jobs=options['concurrent_jobs'],
            job_timeout=options['job_timeout']
        )
        
        # Set up signal handlers for graceful shutdown
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, shutting down gracefully...")
            # The worker service handles KeyboardInterrupt for graceful shutdown
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Display startup information
        self.stdout.write(
            self.style.SUCCESS(
                f"Starting worker with the following configuration:\n"
                f"  Browser: {options['browser']}\n"
                f"  Headless: {headless}\n"
                f"  Concurrent Jobs: {options['concurrent_jobs']}\n"
                f"  Job Timeout: {options['job_timeout']}s\n"
                f"  Log Level: {options['log_level']}\n"
            )
        )
        
        try:
            # Run the worker
            worker_manager.run_sync()
            
        except KeyboardInterrupt:
            self.stdout.write(
                self.style.WARNING("Worker interrupted by user")
            )
        except Exception as e:
            logger.error(f"Worker failed with error: {e}")
            raise CommandError(f"Worker failed: {e}")
        
        self.stdout.write(
            self.style.SUCCESS("Worker stopped successfully")
        )