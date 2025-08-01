from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response as DRFResponse
from django.shortcuts import get_object_or_404
from django.db.models import Avg, Count, Q
from django.http import HttpResponse
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter

from apps.request.models import RequestQueue
from .models import Response
from .serializers import ResponseSerializer, ResponseBodySerializer, ResponseStatsSerializer


@extend_schema_view(
    list=extend_schema(
        tags=['Responses'],
        summary='List responses',
        description='Get a list of all HTTP responses for requests owned by the authenticated user',
        parameters=[
            OpenApiParameter('request', description='Filter by request ID', required=False, type=int),
            OpenApiParameter('status_code', description='Filter by HTTP status code', required=False, type=int),
            OpenApiParameter('from_cache', description='Filter by cache status', required=False, type=bool),
            OpenApiParameter('min_latency', description='Minimum latency in ms', required=False, type=int),
            OpenApiParameter('max_latency', description='Maximum latency in ms', required=False, type=int),
        ]
    ),
    create=extend_schema(
        tags=['Responses'],
        summary='Create response',
        description='Create a new HTTP response record'
    ),
    retrieve=extend_schema(
        tags=['Responses'],
        summary='Get response',
        description='Retrieve a specific HTTP response by ID',
        parameters=[
            OpenApiParameter('id', description='Response ID', required=True, type=int, location=OpenApiParameter.PATH),
        ]
    ),
    update=extend_schema(
        tags=['Responses'],
        summary='Update response',
        description='Update an HTTP response record (full update)',
        parameters=[
            OpenApiParameter('id', description='Response ID', required=True, type=int, location=OpenApiParameter.PATH),
        ]
    ),
    partial_update=extend_schema(
        tags=['Responses'],
        summary='Partial update response',
        description='Partially update an HTTP response record',
        parameters=[
            OpenApiParameter('id', description='Response ID', required=True, type=int, location=OpenApiParameter.PATH),
        ]
    ),
    destroy=extend_schema(
        tags=['Responses'],
        summary='Delete response',
        description='Delete an HTTP response record and its body file',
        parameters=[
            OpenApiParameter('id', description='Response ID', required=True, type=int, location=OpenApiParameter.PATH),
        ]
    ),
)
class ResponseViewSet(viewsets.ModelViewSet):
    serializer_class = ResponseSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        # For schema generation, return all objects to allow type inference
        if getattr(self, 'swagger_fake_view', False):
            return Response.objects.all()
        
        queryset = Response.objects.filter(request__job__spider__project__owner=self.request.user)
        
        # Filter by request if specified
        request_id = self.request.query_params.get('request')
        if request_id:
            queryset = queryset.filter(request_id=request_id)
            
        # Filter by status code if specified
        status_code = self.request.query_params.get('status_code')
        if status_code:
            try:
                queryset = queryset.filter(status_code=int(status_code))
            except ValueError:
                pass  # Invalid status code, ignore filter
                
        # Filter by cache status if specified
        from_cache = self.request.query_params.get('from_cache')
        if from_cache is not None:
            is_cached = from_cache.lower() in ('true', '1', 'yes')
            queryset = queryset.filter(from_cache=is_cached)
            
        # Filter by latency range if specified
        min_latency = self.request.query_params.get('min_latency')
        if min_latency:
            try:
                queryset = queryset.filter(latency_ms__gte=int(min_latency))
            except ValueError:
                pass
                
        max_latency = self.request.query_params.get('max_latency')
        if max_latency:
            try:
                queryset = queryset.filter(latency_ms__lte=int(max_latency))
            except ValueError:
                pass
                
        return queryset

    def perform_create(self, serializer):
        request_id = self.request.data.get("request")
        request_obj = get_object_or_404(
            RequestQueue, pk=request_id, job__spider__project__owner=self.request.user
        )
        serializer.save(request=request_obj)
        
    @extend_schema(
        parameters=[
            OpenApiParameter(name='id', type=int, location=OpenApiParameter.PATH, description='Response ID')
        ]
    )
    def retrieve(self, request, *args, **kwargs):
        """Retrieve a specific response by ID."""
        return super().retrieve(request, *args, **kwargs)
        
    @extend_schema(
        parameters=[
            OpenApiParameter(name='id', type=int, location=OpenApiParameter.PATH, description='Response ID')
        ]
    )
    def update(self, request, *args, **kwargs):
        """Update a response."""
        return super().update(request, *args, **kwargs)
        
    @extend_schema(
        parameters=[
            OpenApiParameter(name='id', type=int, location=OpenApiParameter.PATH, description='Response ID')
        ]
    )
    def partial_update(self, request, *args, **kwargs):
        """Partially update a response."""
        return super().partial_update(request, *args, **kwargs)
        
    @extend_schema(
        parameters=[
            OpenApiParameter(name='id', type=int, location=OpenApiParameter.PATH, description='Response ID')
        ]
    )
    def destroy(self, request, *args, **kwargs):
        """Delete a response."""
        return super().destroy(request, *args, **kwargs)
        
    @extend_schema(
        tags=['Responses'],
        summary='Get response body',
        description='Retrieve the response body content from disk',
        parameters=[
            OpenApiParameter('encoding', description='Text encoding (default: utf-8)', required=False, type=str),
            OpenApiParameter('download', description='Download as file', required=False, type=bool),
        ],
        responses={
            200: ResponseBodySerializer,
            404: None,
        }
    )
    @action(detail=True, methods=['get'])
    def body(self, request, pk=None):
        """Get the response body content."""
        response_obj = self.get_object()
        
        if not response_obj.body_path:
            return DRFResponse(
                {'error': 'No body content available'}, 
                status=status.HTTP_404_NOT_FOUND
            )
            
        # Check if download is requested
        download = request.query_params.get('download', '').lower() in ('true', '1', 'yes')
        
        if download:
            # Return raw file content for download
            body_bytes = response_obj.read_body()
            if body_bytes is None:
                return DRFResponse(
                    {'error': 'Body file not found or could not be read'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
                
            # Determine content type from headers or default
            content_type = 'application/octet-stream'
            if response_obj.headers_json and 'content-type' in response_obj.headers_json:
                content_type = response_obj.headers_json['content-type']
                
            response = HttpResponse(body_bytes, content_type=content_type)
            response['Content-Disposition'] = f'attachment; filename="response_{pk}_body"'
            return response
        else:
            # Return JSON with body text
            encoding = request.query_params.get('encoding', 'utf-8')
            body_text = response_obj.read_body_text(encoding=encoding)
            
            if body_text is None:
                return DRFResponse(
                    {'error': 'Body file not found or could not be read'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
                
            # Determine content type from headers
            content_type = 'text/plain'
            if response_obj.headers_json and 'content-type' in response_obj.headers_json:
                content_type = response_obj.headers_json['content-type']
                
            return DRFResponse({
                'body': body_text,
                'content_type': content_type,
                'encoding': encoding,
                'size': response_obj.body_size
            })
            
    @extend_schema(
        tags=['Responses'],
        summary='Get response statistics',
        description='Get statistics about responses for the authenticated user',
        parameters=[
            OpenApiParameter('job', description='Filter by specific job ID', required=False, type=int),
            OpenApiParameter('spider', description='Filter by specific spider ID', required=False, type=int),
        ],
        responses={200: ResponseStatsSerializer}
    )
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get response statistics."""
        queryset = self.get_queryset()
        
        # Additional filtering for stats
        job_id = request.query_params.get('job')
        if job_id:
            queryset = queryset.filter(request__job_id=job_id)
            
        spider_id = request.query_params.get('spider')
        if spider_id:
            queryset = queryset.filter(request__job__spider_id=spider_id)
            
        # Calculate statistics
        total_responses = queryset.count()
        successful_responses = queryset.filter(status_code__gte=200, status_code__lt=300).count()
        error_responses = queryset.filter(status_code__gte=400).count()
        
        # Average latency (excluding null values)
        avg_latency = queryset.filter(latency_ms__isnull=False).aggregate(
            avg=Avg('latency_ms')
        )['avg'] or 0
        
        # Status code distribution
        status_distribution = queryset.values('status_code').annotate(
            count=Count('status_code')
        ).order_by('status_code')
        
        status_code_distribution = {
            str(item['status_code']): item['count'] 
            for item in status_distribution 
            if item['status_code'] is not None
        }
        
        # Cache hit rate
        cached_responses = queryset.filter(from_cache=True).count()
        cache_hit_rate = (cached_responses / total_responses * 100) if total_responses > 0 else 0
        
        return DRFResponse({
            'total_responses': total_responses,
            'successful_responses': successful_responses,
            'error_responses': error_responses,
            'avg_latency_ms': round(avg_latency, 2),
            'status_code_distribution': status_code_distribution,
            'cache_hit_rate': round(cache_hit_rate, 2)
        })
        
    @extend_schema(
        tags=['Responses'],
        summary='Get successful responses',
        description='Get all responses with 2xx status codes',
        responses={200: ResponseSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def successful(self, request):
        """Get all successful responses (2xx status codes)."""
        queryset = self.get_queryset().filter(status_code__gte=200, status_code__lt=300)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = self.get_serializer(queryset, many=True)
        return DRFResponse(serializer.data)
        
    @extend_schema(
        tags=['Responses'],
        summary='Get error responses',
        description='Get all responses with 4xx and 5xx status codes',
        responses={200: ResponseSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def errors(self, request):
        """Get all error responses (4xx and 5xx status codes)."""
        queryset = self.get_queryset().filter(status_code__gte=400)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = self.get_serializer(queryset, many=True)
        return DRFResponse(serializer.data)
        
    @extend_schema(
        tags=['Responses'],
        summary='Save response body',
        description='Save response body content to disk',
        request={'application/json': {'type': 'object', 'properties': {'body': {'type': 'string'}}}},
        responses={200: ResponseSerializer}
    )
    @action(detail=True, methods=['post'])
    def save_body(self, request, pk=None):
        """Save response body to disk."""
        response_obj = self.get_object()
        body_content = request.data.get('body')
        
        if not body_content:
            return DRFResponse(
                {'error': 'Body content is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            response_obj.save_body(body_content)
            response_obj.save()
            
            serializer = self.get_serializer(response_obj)
            return DRFResponse(serializer.data)
        except Exception as e:
            return DRFResponse(
                {'error': f'Failed to save body: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )