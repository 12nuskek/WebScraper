"""
API clients for interacting with request and response models.
"""
import logging
from typing import Optional, Dict, Any
from django.utils import timezone
from apps.request.models import RequestQueue
from apps.response.models import Response

logger = logging.getLogger(__name__)


class RequestAPIClient:
    """Client for managing request queue operations."""
    
    @staticmethod
    def create_request(job, url: str, method: str = 'GET', headers: Optional[Dict] = None, 
                      body: Optional[bytes] = None, priority: int = 0, depth: int = 0) -> RequestQueue:
        """Create a new request in the queue."""
        try:
            request = RequestQueue.objects.create(
                job=job,
                url=url,
                method=method,
                headers_json=headers,
                body_blob=body,
                priority=priority,
                depth=depth,
                status='pending'
            )
            logger.info(f"Created request {request.id}: {method} {url}")
            return request
        except Exception as e:
            logger.error(f"Failed to create request for {url}: {e}")
            raise
    
    @staticmethod
    def get_next_pending_request(job) -> Optional[RequestQueue]:
        """Get the next pending request for a job, ordered by priority and schedule."""
        try:
            request = RequestQueue.objects.filter(
                job=job,
                status='pending',
                scheduled_at__lte=timezone.now()
            ).first()
            
            if request:
                request.mark_in_progress()
                logger.info(f"Picked up request {request.id}: {request.url}")
            
            return request
        except Exception as e:
            logger.error(f"Failed to get next pending request: {e}")
            return None


class ResponseAPIClient:
    """Client for managing response operations."""
    
    @staticmethod
    def create_response(request: RequestQueue, status_code: Optional[int] = None,
                       headers: Optional[Dict] = None, body_content: Optional[str] = None,
                       final_url: Optional[str] = None, latency_ms: Optional[int] = None,
                       from_cache: bool = False) -> Response:
        """Create a new response record."""
        try:
            response = Response.objects.create(
                request=request,
                final_url=final_url or request.url,
                status_code=status_code,
                headers_json=headers,
                latency_ms=latency_ms,
                from_cache=from_cache,
                fetched_at=timezone.now()
            )
            
            # Save body content if provided
            if body_content:
                response.save_body(body_content)
                response.save()
            
            logger.info(f"Created response {response.id} for request {request.id}: {status_code}")
            return response
        except Exception as e:
            logger.error(f"Failed to create response for request {request.id}: {e}")
            raise
    
    @staticmethod
    def update_response_error(request: RequestQueue, error_message: str) -> Optional[Response]:
        """Create a response record for an error case."""
        try:
            response = Response.objects.create(
                request=request,
                final_url=request.url,
                status_code=None,  # No status code for errors
                headers_json={'error': error_message},
                fetched_at=timezone.now()
            )
            
            # Save error message as body
            response.save_body(f"Error: {error_message}")
            response.save()
            
            logger.warning(f"Created error response {response.id} for request {request.id}: {error_message}")
            return response
        except Exception as e:
            logger.error(f"Failed to create error response for request {request.id}: {e}")
            return None