from rest_framework import viewsets, permissions
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema_view, extend_schema

from apps.spider.models import Spider
from .models import Job
from .serializers import JobSerializer


@extend_schema_view(
    list=extend_schema(
        tags=['Jobs'],
        summary='List jobs',
        description='Get a list of all jobs for spiders owned by the authenticated user'
    ),
    create=extend_schema(
        tags=['Jobs'],
        summary='Create job',
        description='Create a new job to run a spider'
    ),
    retrieve=extend_schema(
        tags=['Jobs'],
        summary='Get job',
        description='Retrieve a specific job by ID'
    ),
    update=extend_schema(
        tags=['Jobs'],
        summary='Update job',
        description='Update a job (full update)'
    ),
    partial_update=extend_schema(
        tags=['Jobs'],
        summary='Partial update job',
        description='Partially update a job (e.g., update status, stats)'
    ),
    destroy=extend_schema(
        tags=['Jobs'],
        summary='Delete job',
        description='Delete a job record'
    ),
)
class JobViewSet(viewsets.ModelViewSet):
    serializer_class = JobSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return Job.objects.filter(spider__project__owner=self.request.user)

    def perform_create(self, serializer):
        spider_id = self.request.data.get("spider")
        spider = get_object_or_404(
            Spider, pk=spider_id, project__owner=self.request.user
        )
        serializer.save(spider=spider)