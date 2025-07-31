from rest_framework import viewsets, permissions
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from apps.scraper.models import Spider
from .models import Job
from .serializers import JobSerializer


@extend_schema(
    tags=['Jobs'],
    parameters=[
        OpenApiParameter(
            name='id',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
            description='Job ID'
        )
    ]
)
class JobViewSet(viewsets.ModelViewSet):
    serializer_class = JobSerializer
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Job.objects.all()  # Add base queryset for schema generation

    def get_queryset(self):
        # Users can only see jobs from spiders in their own projects
        return Job.objects.filter(spider__project__owner=self.request.user)

    def perform_create(self, serializer):
        spider_id = self.request.data.get("spider") or self.kwargs.get("spider_pk")
        spider = get_object_or_404(
            Spider, pk=spider_id, project__owner=self.request.user
        )
        serializer.save(spider=spider)