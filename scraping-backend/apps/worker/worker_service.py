"""
Main worker service for processing scraping jobs using Playwright.
"""
import asyncio
import json
import logging
import time
from typing import Optional, Dict, Any, List
from django.utils import timezone
from django.db import transaction
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from apps.job.models import Job
from apps.spider.models import Spider
from apps.request.models import RequestQueue
from .api_clients import RequestAPIClient, ResponseAPIClient

logger = logging.getLogger(__name__)


class WorkerService:
    """Service class for processing web scraping jobs with Playwright."""
    
    def __init__(self, browser_type: str = 'chromium', headless: bool = True, 
                 concurrent_jobs: int = 1, job_timeout: int = 300):
        """
        Initialize the worker service.
        
        Args:
            browser_type: Type of browser to use ('chromium', 'firefox', 'webkit')
            headless: Whether to run browser in headless mode
            concurrent_jobs: Number of jobs to process concurrently
            job_timeout: Timeout for each job in seconds
        """
        self.browser_type = browser_type
        self.headless = headless
        self.concurrent_jobs = concurrent_jobs
        self.job_timeout = job_timeout
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.is_running = False
        
    async def start(self):
        """Start the worker service."""
        logger.info("Starting worker service...")
        self.is_running = True
        
        async with async_playwright() as playwright:
            # Launch browser
            browser_launcher = getattr(playwright, self.browser_type)
            self.browser = await browser_launcher.launch(headless=self.headless)
            
            try:
                # Main processing loop
                while self.is_running:
                    await self._process_jobs()
                    await asyncio.sleep(5)  # Wait 5 seconds before checking for new jobs
                    
            except KeyboardInterrupt:
                logger.info("Received interrupt signal, shutting down...")
            finally:
                await self._cleanup()
    
    async def stop(self):
        """Stop the worker service."""
        logger.info("Stopping worker service...")
        self.is_running = False
        
    async def _cleanup(self):
        """Clean up browser resources."""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        logger.info("Worker service stopped.")
    
    async def _process_jobs(self):
        """Process available jobs from the queue."""
        try:
            # Get next queued job
            job = Job.objects.filter(status='queued').order_by('created_at').first()
            
            if not job:
                return  # No jobs available
                
            logger.info(f"Processing job {job.id} for spider {job.spider.name}")
            
            # Update job status
            with transaction.atomic():
                job.status = 'running'
                job.started_at = timezone.now()
                job.save()
            
            try:
                await self._process_single_job(job)
                
                # Mark job as completed
                with transaction.atomic():
                    job.status = 'done'
                    job.finished_at = timezone.now()
                    job.save()
                    
                logger.info(f"Completed job {job.id}")
                    
            except Exception as e:
                logger.error(f"Job {job.id} failed: {e}")
                
                # Mark job as failed
                with transaction.atomic():
                    job.status = 'failed'
                    job.finished_at = timezone.now()
                    job.save()
                    
        except Exception as e:
            logger.error(f"Error in job processing loop: {e}")
    
    async def _process_single_job(self, job: Job):
        """Process a single scraping job."""
        spider = job.spider
        start_urls = spider.start_urls_json
        
        if not start_urls or not isinstance(start_urls, list):
            raise ValueError(f"Invalid start_urls for spider {spider.name}")
        
        # Create browser context for this job
        context = await self.browser.new_context()
        
        try:
            # Process each start URL
            for url in start_urls:
                await self._process_url(job, context, url)
                
            # Process any additional requests in the queue
            await self._process_request_queue(job, context)
            
        finally:
            await context.close()
    
    async def _process_url(self, job: Job, context: BrowserContext, url: str):
        """Process a single URL."""
        start_time = time.time()
        page = None
        
        try:
            # Create request record
            request = RequestAPIClient.create_request(
                job=job,
                url=url,
                method='GET',
                priority=1  # Start URLs have high priority
            )
            
            # Create new page
            page = await context.new_page()
            
            # Set up request/response monitoring
            responses = []
            
            async def handle_response(response):
                responses.append({
                    'url': response.url,
                    'status': response.status,
                    'headers': dict(response.headers),
                    'ok': response.ok
                })
            
            page.on('response', handle_response)
            
            # Navigate to URL
            logger.info(f"Navigating to {url}")
            response = await page.goto(url, timeout=30000)  # 30 second timeout
            
            if not response:
                raise Exception(f"Failed to load page: {url}")
            
            # Wait for page to load
            await page.wait_for_load_state('networkidle', timeout=10000)
            
            # Get page content
            content = await page.content()
            final_url = page.url
            
            # Calculate latency
            latency_ms = int((time.time() - start_time) * 1000)
            
            # Create response record
            ResponseAPIClient.create_response(
                request=request,
                status_code=response.status,
                headers=dict(response.headers),
                body_content=content,
                final_url=final_url,
                latency_ms=latency_ms
            )
            
            # Mark request as completed
            request.mark_done()
            
            logger.info(f"Successfully processed {url} - Status: {response.status}")
            
        except Exception as e:
            logger.error(f"Error processing {url}: {e}")
            
            # Create error response
            if 'request' in locals():
                ResponseAPIClient.update_response_error(request, str(e))
                request.mark_error()
            
        finally:
            if page:
                await page.close()
    
    async def _process_request_queue(self, job: Job, context: BrowserContext):
        """Process additional requests in the queue for this job."""
        while True:
            # Get next pending request
            request = RequestAPIClient.get_next_pending_request(job)
            
            if not request:
                break  # No more pending requests
            
            try:
                await self._process_request(context, request)
                request.mark_done()
                
            except Exception as e:
                logger.error(f"Error processing request {request.id}: {e}")
                ResponseAPIClient.update_response_error(request, str(e))
                request.mark_error()
    
    async def _process_request(self, context: BrowserContext, request: RequestQueue):
        """Process a single request from the queue."""
        start_time = time.time()
        page = await context.new_page()
        
        try:
            # Handle different HTTP methods
            if request.method == 'GET':
                response = await page.goto(request.url, timeout=30000)
            else:
                # For non-GET requests, we might need to use page.evaluate
                # or page.route for more complex scenarios
                response = await page.goto(request.url, timeout=30000)
            
            if not response:
                raise Exception(f"Failed to load page: {request.url}")
            
            # Wait for page to load
            await page.wait_for_load_state('networkidle', timeout=10000)
            
            # Get page content
            content = await page.content()
            final_url = page.url
            
            # Calculate latency
            latency_ms = int((time.time() - start_time) * 1000)
            
            # Create response record
            ResponseAPIClient.create_response(
                request=request,
                status_code=response.status,
                headers=dict(response.headers),
                body_content=content,
                final_url=final_url,
                latency_ms=latency_ms
            )
            
            logger.info(f"Successfully processed request {request.id}: {request.url}")
            
        finally:
            await page.close()


class WorkerManager:
    """Manager class for running the worker service."""
    
    def __init__(self, **kwargs):
        self.service = WorkerService(**kwargs)
    
    async def run(self):
        """Run the worker service."""
        try:
            await self.service.start()
        except KeyboardInterrupt:
            logger.info("Shutting down worker...")
        finally:
            await self.service.stop()
    
    def run_sync(self):
        """Run the worker service synchronously."""
        asyncio.run(self.run())