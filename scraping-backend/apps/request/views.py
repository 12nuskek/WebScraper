from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter

from apps.job.models import Job
from .models import RequestQueue
from .serializers import RequestQueueSerializer


@extend_schema_view(
    list=extend_schema(
        tags=['Requests'],
        summary='List requests',
        description='Get a list of all queued requests for jobs owned by the authenticated user',
        parameters=[
            OpenApiParameter('job', description='Filter by job ID', required=False, type=int),
            OpenApiParameter('status', description='Filter by status', required=False, type=str),
            OpenApiParameter('priority_min', description='Minimum priority', required=False, type=int),
        ]
    ),
    create=extend_schema(
        tags=['Requests'],
        summary='Create request',
        description='Add a new HTTP request to the queue'
    ),
    retrieve=extend_schema(
        tags=['Requests'],
        summary='Get request',
        description='Retrieve a specific queued request by ID',
        parameters=[
            OpenApiParameter('id', description='Request ID', required=True, type=int, location=OpenApiParameter.PATH),
        ]
    ),
    update=extend_schema(
        tags=['Requests'],
        summary='Update request',
        description='Update a queued request (full update)',
        parameters=[
            OpenApiParameter('id', description='Request ID', required=True, type=int, location=OpenApiParameter.PATH),
        ]
    ),
    partial_update=extend_schema(
        tags=['Requests'],
        summary='Partial update request',
        description='Partially update a queued request (e.g., update status, priority)',
        parameters=[
            OpenApiParameter('id', description='Request ID', required=True, type=int, location=OpenApiParameter.PATH),
        ]
    ),
    destroy=extend_schema(
        tags=['Requests'],
        summary='Delete request',
        description='Remove a request from the queue',
        parameters=[
            OpenApiParameter('id', description='Request ID', required=True, type=int, location=OpenApiParameter.PATH),
        ]
    ),
)
class RequestQueueViewSet(viewsets.ModelViewSet):
    serializer_class = RequestQueueSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        # For schema generation, return all objects to allow type inference
        if getattr(self, 'swagger_fake_view', False):
            return RequestQueue.objects.all()
        
        queryset = RequestQueue.objects.filter(job__spider__project__owner=self.request.user)
        
        # Filter by job if specified
        job_id = self.request.query_params.get('job')
        if job_id:
            queryset = queryset.filter(job_id=job_id)
            
        # Filter by status if specified
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
            
        # Filter by minimum priority if specified
        priority_min = self.request.query_params.get('priority_min')
        if priority_min:
            try:
                queryset = queryset.filter(priority__gte=int(priority_min))
            except ValueError:
                pass  # Invalid priority, ignore filter
                
        return queryset

    def perform_create(self, serializer):
        job_id = self.request.data.get("job")
        job = get_object_or_404(
            Job, pk=job_id, spider__project__owner=self.request.user
        )
        serializer.save(job=job)
        
    @extend_schema(
        parameters=[
            OpenApiParameter(name='id', type=int, location=OpenApiParameter.PATH, description='Request ID')
        ]
    )
    def retrieve(self, request, *args, **kwargs):
        """Retrieve a specific request by ID."""
        return super().retrieve(request, *args, **kwargs)
        
    @extend_schema(
        parameters=[
            OpenApiParameter(name='id', type=int, location=OpenApiParameter.PATH, description='Request ID')
        ]
    )
    def update(self, request, *args, **kwargs):
        """Update a request."""
        return super().update(request, *args, **kwargs)
        
    @extend_schema(
        parameters=[
            OpenApiParameter(name='id', type=int, location=OpenApiParameter.PATH, description='Request ID')
        ]
    )
    def partial_update(self, request, *args, **kwargs):
        """Partially update a request."""
        return super().partial_update(request, *args, **kwargs)
        
    @extend_schema(
        parameters=[
            OpenApiParameter(name='id', type=int, location=OpenApiParameter.PATH, description='Request ID')
        ]
    )
    def destroy(self, request, *args, **kwargs):
        """Delete a request."""
        return super().destroy(request, *args, **kwargs)
        
    @extend_schema(
        tags=['Requests'],
        summary='Mark request in progress',
        description='Mark a pending request as in progress (dequeue for processing)',
        responses={200: RequestQueueSerializer}
    )
    @action(detail=True, methods=['post'])
    def mark_in_progress(self, request, pk=None):
        """Mark a request as in progress."""
        request_obj = self.get_object()
        if request_obj.status != 'pending':
            return Response(
                {'error': 'Request must be pending to mark as in progress'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        request_obj.mark_in_progress()
        serializer = self.get_serializer(request_obj)
        return Response(serializer.data)
        
    @extend_schema(
        tags=['Requests'],
        summary='Mark request done',
        description='Mark a request as completed successfully',
        responses={200: RequestQueueSerializer}
    )
    @action(detail=True, methods=['post'])
    def mark_done(self, request, pk=None):
        """Mark a request as done."""
        request_obj = self.get_object()
        request_obj.mark_done()
        serializer = self.get_serializer(request_obj)
        return Response(serializer.data)
        
    @extend_schema(
        tags=['Requests'],
        summary='Mark request error',
        description='Mark a request as failed with error',
        responses={200: RequestQueueSerializer}
    )
    @action(detail=True, methods=['post'])
    def mark_error(self, request, pk=None):
        """Mark a request as error."""
        request_obj = self.get_object()
        increment_retry = request.data.get('increment_retry', True)
        request_obj.mark_error(increment_retry=increment_retry)
        serializer = self.get_serializer(request_obj)
        return Response(serializer.data)
        
    @extend_schema(
        tags=['Requests'],
        summary='Retry request',
        description='Reset a failed request for retry if retries are available',
        responses={200: RequestQueueSerializer}
    )
    @action(detail=True, methods=['post'])
    def retry(self, request, pk=None):
        """Retry a failed request."""
        request_obj = self.get_object()
        if not request_obj.can_retry:
            return Response(
                {'error': 'Request has exceeded maximum retry attempts'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        if request_obj.reset_for_retry():
            serializer = self.get_serializer(request_obj)
            return Response(serializer.data)
        else:
            return Response(
                {'error': 'Could not reset request for retry'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
    @extend_schema(
        tags=['Requests'],
        summary='Get next pending requests',
        description='Get the next pending requests for processing (worker endpoint)',
        parameters=[
            OpenApiParameter('limit', description='Number of requests to fetch', required=False, type=int),
            OpenApiParameter('job', description='Filter by specific job ID', required=False, type=int),
        ],
        responses={200: RequestQueueSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def next_pending(self, request):
        """Get next pending requests for processing."""
        limit = int(request.query_params.get('limit', 10))
        job_id = request.query_params.get('job')
        
        queryset = self.get_queryset().filter(status='pending')
        if job_id:
            queryset = queryset.filter(job_id=job_id)
            
        # Get highest priority requests first
        requests = queryset[:limit]
        serializer = self.get_serializer(requests, many=True)
        return Response(serializer.data)