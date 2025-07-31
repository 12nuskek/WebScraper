import os
import hashlib
from pathlib import Path
from django.db import models
from django.conf import settings
from django.utils import timezone


class Response(models.Model):
    """Model representing an HTTP response from a processed request."""
    
    request = models.OneToOneField(
        "request.RequestQueue",
        on_delete=models.CASCADE,
        related_name="response",
    )
    final_url = models.URLField(max_length=2000, null=True, blank=True)  # After redirects
    status_code = models.IntegerField(null=True, blank=True)
    headers_json = models.JSONField(null=True, blank=True)
    fetched_at = models.DateTimeField(default=timezone.now)
    latency_ms = models.IntegerField(null=True, blank=True)  # Response time in milliseconds
    from_cache = models.BooleanField(default=False)
    body_path = models.TextField(null=True, blank=True)  # File path of saved body
    content_hash = models.CharField(max_length=64, null=True, blank=True)  # SHA256 hash
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-fetched_at"]
        indexes = [
            models.Index(fields=['request']),
            models.Index(fields=['status_code']),
            models.Index(fields=['fetched_at']),
            models.Index(fields=['content_hash']),
        ]

    def __str__(self):
        status = self.status_code or "Unknown"
        url = self.final_url or self.request.url if self.request else "No URL"
        return f"Response {self.id}: {status} {url[:50]}..."
        
    @property
    def is_success(self):
        """Check if response indicates success (2xx status codes)."""
        return self.status_code and 200 <= self.status_code < 300
        
    @property
    def is_redirect(self):
        """Check if response is a redirect (3xx status codes)."""
        return self.status_code and 300 <= self.status_code < 400
        
    @property
    def is_client_error(self):
        """Check if response is a client error (4xx status codes)."""
        return self.status_code and 400 <= self.status_code < 500
        
    @property
    def is_server_error(self):
        """Check if response is a server error (5xx status codes)."""
        return self.status_code and 500 <= self.status_code < 600
        
    @property
    def body_size(self):
        """Get the size of the stored body file in bytes."""
        if not self.body_path:
            return 0
            
        full_path = Path(settings.MEDIA_ROOT) / self.body_path
        if full_path.exists():
            return os.path.getsize(full_path)
        return 0
        
    def get_body_dir(self):
        """Get the directory for storing response bodies."""
        # Create directory structure: media/responses/YYYY/MM/DD/
        date_path = self.fetched_at.strftime('%Y/%m/%d')
        body_dir = Path(settings.MEDIA_ROOT) / 'responses' / date_path
        body_dir.mkdir(parents=True, exist_ok=True)
        return body_dir
        
    def generate_body_filename(self):
        """Generate a unique filename for the response body."""
        # Use request ID and timestamp to ensure uniqueness
        timestamp = self.fetched_at.strftime('%H%M%S')
        return f"response_{self.request_id}_{timestamp}.html"
        
    def save_body(self, body_content):
        """Save response body to disk and update body_path and content_hash."""
        if not body_content:
            return
            
        # Generate content hash
        if isinstance(body_content, str):
            body_bytes = body_content.encode('utf-8')
        else:
            body_bytes = body_content
            
        self.content_hash = hashlib.sha256(body_bytes).hexdigest()
        
        # Generate file path
        body_dir = self.get_body_dir()
        filename = self.generate_body_filename()
        file_path = body_dir / filename
        
        # Save body to file
        with open(file_path, 'wb') as f:
            f.write(body_bytes)
            
        # Store relative path from MEDIA_ROOT
        self.body_path = str(file_path.relative_to(Path(settings.MEDIA_ROOT)))
        
    def read_body(self):
        """Read response body from disk."""
        if not self.body_path:
            return None
            
        full_path = Path(settings.MEDIA_ROOT) / self.body_path
        if not full_path.exists():
            return None
            
        try:
            with open(full_path, 'rb') as f:
                return f.read()
        except (IOError, OSError):
            return None
            
    def read_body_text(self, encoding='utf-8'):
        """Read response body as text with specified encoding."""
        body_bytes = self.read_body()
        if body_bytes:
            try:
                return body_bytes.decode(encoding)
            except UnicodeDecodeError:
                # Fallback to latin-1 which can decode any byte sequence
                return body_bytes.decode('latin-1')
        return None
        
    def delete_body_file(self):
        """Delete the response body file from disk."""
        if not self.body_path:
            return False
            
        full_path = Path(settings.MEDIA_ROOT) / self.body_path
        if full_path.exists():
            try:
                full_path.unlink()
                return True
            except (IOError, OSError):
                pass
        return False
        
    def delete(self, *args, **kwargs):
        """Override delete to also remove body file."""
        self.delete_body_file()
        super().delete(*args, **kwargs)
        
    @classmethod
    def get_responses_by_status_code(cls, status_code):
        """Get all responses with a specific status code."""
        return cls.objects.filter(status_code=status_code)
        
    @classmethod
    def get_successful_responses(cls):
        """Get all successful responses (2xx status codes)."""
        return cls.objects.filter(status_code__gte=200, status_code__lt=300)
        
    @classmethod
    def get_error_responses(cls):
        """Get all error responses (4xx and 5xx status codes)."""
        return cls.objects.filter(status_code__gte=400)