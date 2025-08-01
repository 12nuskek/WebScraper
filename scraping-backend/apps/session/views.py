from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from django.utils import timezone
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter

from .models import Session
from .serializers import (
    SessionSerializer,
    SessionCreateSerializer,
    SessionListSerializer,
    SessionExtendValiditySerializer
)


@extend_schema_view(
    list=extend_schema(
        tags=['Sessions'],
        summary='List sessions',
        description='Get a list of all spider sessions with filtering options',
        parameters=[
            OpenApiParameter('spider', description='Filter by spider ID', required=False, type=int),
            OpenApiParameter('label', description='Filter by session label', required=False, type=str),
            OpenApiParameter('validity', description='Filter by validity status (valid/expired)', required=False, type=str),
        ]
    ),
    create=extend_schema(
        tags=['Sessions'],
        summary='Create session',
        description='Create a new spider session with cookies and headers'
    ),
    retrieve=extend_schema(
        tags=['Sessions'],
        summary='Get session',
        description='Retrieve a specific session by ID'
    ),
    update=extend_schema(
        tags=['Sessions'],
        summary='Update session',
        description='Update a session (full update)'
    ),
    partial_update=extend_schema(
        tags=['Sessions'],
        summary='Partial update session',
        description='Partially update a session (e.g., update cookies/headers)'
    ),
    destroy=extend_schema(
        tags=['Sessions'],
        summary='Delete session',
        description='Delete a session permanently'
    ),
)
class SessionViewSet(viewsets.ModelViewSet):
    """ViewSet for managing spider sessions."""
    
    queryset = Session.objects.select_related('spider').all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['spider', 'label']
    search_fields = ['label', 'spider__name']
    ordering_fields = ['created_at', 'updated_at', 'valid_until']
    ordering = ['-updated_at']
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'create':
            return SessionCreateSerializer
        elif self.action == 'list':
            return SessionListSerializer
        elif self.action == 'extend_validity':
            return SessionExtendValiditySerializer
        return SessionSerializer
        
    def get_queryset(self):
        """Filter queryset based on query parameters."""
        queryset = super().get_queryset()
        
        # Filter by validity status
        validity = self.request.query_params.get('validity')
        if validity == 'valid':
            current_time = timezone.now()
            queryset = queryset.filter(
                Q(valid_until__isnull=True) | Q(valid_until__gt=current_time)
            )
        elif validity == 'expired':
            current_time = timezone.now()
            queryset = queryset.filter(valid_until__lt=current_time)
            
        return queryset
        
    @extend_schema(
        tags=['Sessions'],
        summary='Extend session validity',
        description='Extend session validity by specified number of hours'
    )
    @action(detail=True, methods=['post'])
    def extend_validity(self, request, pk=None):
        """Extend session validity by specified hours."""
        session = self.get_object()
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            hours = serializer.validated_data['hours']
            session.extend_validity(hours=hours)
            
            return Response({
                'message': f'Session validity extended by {hours} hours',
                'valid_until': session.valid_until,
                'is_valid': session.is_valid
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    @extend_schema(
        tags=['Sessions'],
        summary='Clean up expired sessions',
        description='Delete all expired sessions from the database'
    )
    @action(detail=False, methods=['post'])
    def cleanup_expired(self, request):
        """Clean up all expired sessions."""
        deleted_count, _ = Session.cleanup_expired_sessions()
        
        return Response({
            'message': f'Deleted {deleted_count} expired sessions',
            'deleted_count': deleted_count
        })
        
    @extend_schema(
        tags=['Sessions'],
        summary='Get valid sessions',
        description='Get all currently valid (non-expired) sessions'
    )
    @action(detail=False, methods=['get'])
    def valid_sessions(self, request):
        """Get all valid (non-expired) sessions."""
        valid_sessions = Session.get_valid_sessions().select_related('spider')
        serializer = SessionListSerializer(valid_sessions, many=True)
        
        return Response({
            'count': valid_sessions.count(),
            'results': serializer.data
        })
        
    @extend_schema(
        tags=['Sessions'],
        summary='Get expired sessions',
        description='Get all expired sessions'
    )
    @action(detail=False, methods=['get'])
    def expired_sessions(self, request):
        """Get all expired sessions."""
        expired_sessions = Session.get_expired_sessions().select_related('spider')
        serializer = SessionListSerializer(expired_sessions, many=True)
        
        return Response({
            'count': expired_sessions.count(),
            'results': serializer.data
        })
        
    @extend_schema(
        tags=['Sessions'],
        summary='Get session status',
        description='Get detailed status information for a specific session'
    )
    @action(detail=True, methods=['get'])
    def status(self, request, pk=None):
        """Get session status information."""
        session = self.get_object()
        
        return Response({
            'id': session.id,
            'spider_name': session.spider.name,
            'label': session.label,
            'is_expired': session.is_expired,
            'is_valid': session.is_valid,
            'valid_until': session.valid_until,
            'has_cookies': bool(session.cookies_json),
            'has_headers': bool(session.headers_json),
            'cookie_count': len(session.cookies_json) if session.cookies_json else 0,
            'header_count': len(session.headers_json) if session.headers_json else 0,
        })