from rest_framework import viewsets, permissions
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from apps.projects.models import Project
from .models import Spider
from .serializers import SpiderSerializer


@extend_schema(
    tags=['Spiders'],
    parameters=[
        OpenApiParameter(
            name='id',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
            description='Spider ID'
        )
    ]
)
class SpiderViewSet(viewsets.ModelViewSet):
    serializer_class = SpiderSerializer
    permission_classes = (permissions.IsAuthenticated,)   # reuse Project auth
    queryset = Spider.objects.all()  # Add base queryset for schema generation

    def get_queryset(self):
        return Spider.objects.filter(project__owner=self.request.user)

    # optional: /projects/{project_pk}/spiders/ nested route support
    def perform_create(self, serializer):
        project_id = self.request.data.get("project") or self.kwargs.get("project_pk")
        project = get_object_or_404(
            Project, pk=project_id, owner=self.request.user
        )
        serializer.save(project=project)