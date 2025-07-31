from django.db import models
from django.utils import timezone
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
import urllib.parse


class Proxy(models.Model):
    """Model representing a proxy server for rotating and health tracking."""
    
    uri = models.CharField(
        max_length=500,
        unique=True,
        help_text="Proxy URI (scheme://user:pass@host:port)"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this proxy is active for rotation"
    )
    last_ok_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Last time this proxy was successfully used"
    )
    fail_count = models.IntegerField(
        default=0,
        help_text="Number of consecutive failures"
    )
    meta_json = models.JSONField(
        null=True,
        blank=True,
        help_text="Additional metadata for this proxy"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['fail_count', '-last_ok_at']
        indexes = [
            models.Index(fields=['is_active']),
            models.Index(fields=['fail_count']),
            models.Index(fields=['last_ok_at']),
            models.Index(fields=['is_active', 'fail_count']),
        ]
        verbose_name_plural = "Proxies"

    def __str__(self):
        status = "active" if self.is_active else "inactive"
        return f"Proxy {self.id}: {self.masked_uri} ({status})"
        
    def clean(self):
        """Validate proxy URI format."""
        super().clean()
        if not self.uri:
            raise ValidationError({'uri': 'Proxy URI is required.'})
            
        # Basic URI validation
        try:
            parsed = urllib.parse.urlparse(self.uri)
            if not parsed.scheme or not parsed.hostname:
                raise ValidationError({'uri': 'Invalid proxy URI format. Use scheme://host:port or scheme://user:pass@host:port'})
                
            # Check for supported schemes
            if parsed.scheme.lower() not in ['http', 'https', 'socks4', 'socks5']:
                raise ValidationError({'uri': 'Unsupported proxy scheme. Use http, https, socks4, or socks5.'})
                
        except Exception as e:
            raise ValidationError({'uri': f'Invalid proxy URI: {str(e)}'})
            
    @property
    def masked_uri(self):
        """Return URI with masked credentials for display."""
        try:
            parsed = urllib.parse.urlparse(self.uri)
            if parsed.username:
                # Mask the password but show username
                netloc = f"{parsed.username}:***@{parsed.hostname}"
                if parsed.port:
                    netloc += f":{parsed.port}"
                return f"{parsed.scheme}://{netloc}"
            return self.uri
        except:
            return self.uri
            
    @property
    def hostname(self):
        """Extract hostname from URI."""
        try:
            return urllib.parse.urlparse(self.uri).hostname
        except:
            return None
            
    @property
    def port(self):
        """Extract port from URI."""
        try:
            return urllib.parse.urlparse(self.uri).port
        except:
            return None
            
    @property
    def scheme(self):
        """Extract scheme from URI."""
        try:
            return urllib.parse.urlparse(self.uri).scheme
        except:
            return None
            
    @property
    def is_healthy(self):
        """Check if proxy is considered healthy (low fail count)."""
        return self.fail_count < 5  # Consider unhealthy after 5 consecutive failures
        
    @property
    def success_rate(self):
        """Calculate success rate based on metadata."""
        if not self.meta_json:
            return None
            
        total_attempts = self.meta_json.get('total_attempts', 0)
        successful_attempts = self.meta_json.get('successful_attempts', 0)
        
        if total_attempts == 0:
            return None
            
        return (successful_attempts / total_attempts) * 100
        
    def mark_success(self):
        """Mark proxy as successfully used."""
        self.last_ok_at = timezone.now()
        self.fail_count = 0
        self.is_active = True
        
        # Update metadata
        if not self.meta_json:
            self.meta_json = {}
        self.meta_json['total_attempts'] = self.meta_json.get('total_attempts', 0) + 1
        self.meta_json['successful_attempts'] = self.meta_json.get('successful_attempts', 0) + 1
        self.meta_json['last_success_at'] = timezone.now().isoformat()
        
        self.save(update_fields=['last_ok_at', 'fail_count', 'is_active', 'meta_json', 'updated_at'])
        
    def mark_failure(self, error_msg=None):
        """Mark proxy as failed."""
        self.fail_count += 1
        
        # Disable if too many failures
        if self.fail_count >= 10:
            self.is_active = False
            
        # Update metadata
        if not self.meta_json:
            self.meta_json = {}
        self.meta_json['total_attempts'] = self.meta_json.get('total_attempts', 0) + 1
        self.meta_json['last_failure_at'] = timezone.now().isoformat()
        if error_msg:
            self.meta_json['last_error'] = error_msg
            
        self.save(update_fields=['fail_count', 'is_active', 'meta_json', 'updated_at'])
        
    def reset_stats(self):
        """Reset proxy statistics."""
        self.fail_count = 0
        self.is_active = True
        self.meta_json = {}
        self.save(update_fields=['fail_count', 'is_active', 'meta_json', 'updated_at'])
        
    @classmethod
    def get_active_proxies(cls):
        """Get all active proxies."""
        return cls.objects.filter(is_active=True)
        
    @classmethod
    def get_healthy_proxies(cls):
        """Get all healthy active proxies."""
        return cls.objects.filter(is_active=True, fail_count__lt=5)
        
    @classmethod
    def get_next_proxy(cls):
        """Get the next proxy for rotation (lowest fail count, most recent success)."""
        return cls.get_healthy_proxies().first()
        
    @classmethod
    def cleanup_failed_proxies(cls, max_failures=20):
        """Remove proxies with too many failures."""
        return cls.objects.filter(fail_count__gte=max_failures).delete()
