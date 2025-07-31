from rest_framework import viewsets, permissions
from django.shortcuts import get_object_or_404

from apps.projects.models import Project
from .models import Spider
from .serializers import SpiderSerializer


class SpiderViewSet(viewsets.ModelViewSet):
    serializer_class = SpiderSerializer
    permission_classes = (permissions.IsAuthenticated,)   # reuse Project auth

    def get_queryset(self):
        return Spider.objects.filter(project__owner=self.request.user)

    # optional: /projects/{project_pk}/spiders/ nested route support
    def perform_create(self, serializer):
        project_id = self.request.data.get("project") or self.kwargs.get("project_pk")
        project = get_object_or_404(
            Project, pk=project_id, owner=self.request.user
        )
        serializer.save(project=project)