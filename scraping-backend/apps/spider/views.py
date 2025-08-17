from rest_framework import viewsets, permissions
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter

from apps.projects.models import Project
from .models import Spider
from .serializers import SpiderSerializer


@extend_schema_view(
    list=extend_schema(
        tags=['Spiders'],
        summary='List spiders',
        description='Get a list of all spiders belonging to projects owned by the authenticated user'
    ),
    create=extend_schema(
        tags=['Spiders'],
        summary='Create spider',
        description='Create a new spider configuration for web scraping'
    ),
    retrieve=extend_schema(
        tags=['Spiders'],
        summary='Get spider',
        description='Retrieve a specific spider configuration by ID',
        parameters=[
            OpenApiParameter(name='id', type=int, location=OpenApiParameter.PATH, description='Spider ID')
        ]
    ),
    update=extend_schema(
        tags=['Spiders'],
        summary='Update spider',
        description='Update a spider configuration (full update)',
        parameters=[
            OpenApiParameter(name='id', type=int, location=OpenApiParameter.PATH, description='Spider ID')
        ]
    ),
    partial_update=extend_schema(
        tags=['Spiders'],
        summary='Partial update spider',
        description='Partially update a spider configuration',
        parameters=[
            OpenApiParameter(name='id', type=int, location=OpenApiParameter.PATH, description='Spider ID')
        ]
    ),
    destroy=extend_schema(
        tags=['Spiders'],
        summary='Delete spider',
        description='Delete a spider configuration',
        parameters=[
            OpenApiParameter(name='id', type=int, location=OpenApiParameter.PATH, description='Spider ID')
        ]
    ),
)
class SpiderViewSet(viewsets.ModelViewSet):
    serializer_class = SpiderSerializer
    permission_classes = (permissions.IsAuthenticated,)   # reuse Project auth

    def get_queryset(self):
        return Spider.objects.filter(project__owner=self.request.user)

    # optional: /projects/{project_pk}/spiders/ nested route support
    def perform_create(self, serializer):
        project_id = (
            self.request.data.get("project")
            or (self.request.data.get("Spider") or {}).get("Project")
            or self.kwargs.get("project_pk")
        )
        project = get_object_or_404(
            Project, pk=project_id, owner=self.request.user
        )
        serializer.save(project=project)