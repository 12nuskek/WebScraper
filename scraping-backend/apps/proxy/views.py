from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q

from .models import Proxy
from .serializers import (
    ProxySerializer,
    ProxyCreateSerializer,
    ProxyListSerializer,
    ProxyStatsSerializer,
    ProxyMarkResultSerializer
)


class ProxyViewSet(viewsets.ModelViewSet):
    """ViewSet for managing proxy servers."""
    
    queryset = Proxy.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_active']
    search_fields = ['uri']
    ordering_fields = ['created_at', 'updated_at', 'last_ok_at', 'fail_count']
    ordering = ['fail_count', '-last_ok_at']
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'create':
            return ProxyCreateSerializer
        elif self.action == 'list':
            return ProxyListSerializer
        elif self.action in ['stats', 'active_proxies', 'healthy_proxies']:
            return ProxyStatsSerializer
        elif self.action in ['mark_success', 'mark_failure']:
            return ProxyMarkResultSerializer
        return ProxySerializer
        
    def get_queryset(self):
        """Filter queryset based on query parameters."""
        queryset = super().get_queryset()
        
        # Filter by health status
        health = self.request.query_params.get('health')
        if health == 'healthy':
            queryset = queryset.filter(fail_count__lt=5)
        elif health == 'unhealthy':
            queryset = queryset.filter(fail_count__gte=5)
            
        # Filter by failure count
        max_failures = self.request.query_params.get('max_failures')
        if max_failures:
            try:
                queryset = queryset.filter(fail_count__lte=int(max_failures))
            except ValueError:
                pass
                
        return queryset
        
    @action(detail=True, methods=['post'])
    def mark_success(self, request, pk=None):
        """Mark proxy as successfully used."""
        proxy = self.get_object()
        proxy.mark_success()
        
        return Response({
            'message': 'Proxy marked as successful',
            'fail_count': proxy.fail_count,
            'is_active': proxy.is_active,
            'last_ok_at': proxy.last_ok_at
        })
        
    @action(detail=True, methods=['post'])
    def mark_failure(self, request, pk=None):
        """Mark proxy as failed."""
        proxy = self.get_object()
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            error_msg = serializer.validated_data.get('error_message')
            proxy.mark_failure(error_msg=error_msg)
            
            return Response({
                'message': 'Proxy marked as failed',
                'fail_count': proxy.fail_count,
                'is_active': proxy.is_active
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    @action(detail=True, methods=['post'])
    def reset_stats(self, request, pk=None):
        """Reset proxy statistics."""
        proxy = self.get_object()
        proxy.reset_stats()
        
        return Response({
            'message': 'Proxy statistics reset',
            'fail_count': proxy.fail_count,
            'is_active': proxy.is_active,
            'meta_json': proxy.meta_json
        })
        
    @action(detail=False, methods=['get'])
    def active_proxies(self, request):
        """Get all active proxies."""
        active_proxies = Proxy.get_active_proxies()
        serializer = self.get_serializer(active_proxies, many=True)
        
        return Response({
            'count': active_proxies.count(),
            'results': serializer.data
        })
        
    @action(detail=False, methods=['get'])
    def healthy_proxies(self, request):
        """Get all healthy proxies."""
        healthy_proxies = Proxy.get_healthy_proxies()
        serializer = self.get_serializer(healthy_proxies, many=True)
        
        return Response({
            'count': healthy_proxies.count(),
            'results': serializer.data
        })
        
    @action(detail=False, methods=['get'])
    def next_proxy(self, request):
        """Get the next proxy for rotation."""
        next_proxy = Proxy.get_next_proxy()
        
        if next_proxy:
            serializer = ProxySerializer(next_proxy)
            return Response(serializer.data)
        else:
            return Response({
                'message': 'No healthy proxies available'
            }, status=status.HTTP_404_NOT_FOUND)
            
    @action(detail=False, methods=['post'])
    def cleanup_failed(self, request):
        """Clean up proxies with too many failures."""
        max_failures = request.data.get('max_failures', 20)
        try:
            max_failures = int(max_failures)
        except (ValueError, TypeError):
            max_failures = 20
            
        deleted_count, _ = Proxy.cleanup_failed_proxies(max_failures=max_failures)
        
        return Response({
            'message': f'Deleted {deleted_count} proxies with {max_failures}+ failures',
            'deleted_count': deleted_count
        })
        
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get proxy statistics overview."""
        total_proxies = Proxy.objects.count()
        active_proxies = Proxy.objects.filter(is_active=True).count()
        healthy_proxies = Proxy.objects.filter(is_active=True, fail_count__lt=5).count()
        failed_proxies = Proxy.objects.filter(fail_count__gte=10).count()
        
        return Response({
            'total_proxies': total_proxies,
            'active_proxies': active_proxies,
            'healthy_proxies': healthy_proxies,
            'failed_proxies': failed_proxies,
            'health_percentage': (healthy_proxies / total_proxies * 100) if total_proxies > 0 else 0
        })
        
    @action(detail=True, methods=['get'])
    def health_check(self, request, pk=None):
        """Get detailed health information for a proxy."""
        proxy = self.get_object()
        
        return Response({
            'id': proxy.id,
            'masked_uri': proxy.masked_uri,
            'is_active': proxy.is_active,
            'is_healthy': proxy.is_healthy,
            'fail_count': proxy.fail_count,
            'last_ok_at': proxy.last_ok_at,
            'success_rate': proxy.success_rate,
            'total_attempts': proxy.meta_json.get('total_attempts', 0) if proxy.meta_json else 0,
            'successful_attempts': proxy.meta_json.get('successful_attempts', 0) if proxy.meta_json else 0,
            'last_error': proxy.meta_json.get('last_error') if proxy.meta_json else None,
        })