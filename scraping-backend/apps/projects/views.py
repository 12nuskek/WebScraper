from rest_framework import viewsets, permissions
from drf_spectacular.utils import extend_schema_view, extend_schema
from .models import Project
from .serializers import ProjectSerializer


class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


@extend_schema_view(
    list=extend_schema(
        tags=['Projects'],
        summary='List projects',
        description='Get a list of all projects owned by the authenticated user'
    ),
    create=extend_schema(
        tags=['Projects'],
        summary='Create project',
        description='Create a new project for the authenticated user'
    ),
    retrieve=extend_schema(
        tags=['Projects'],
        summary='Get project',
        description='Retrieve a specific project by ID'
    ),
    update=extend_schema(
        tags=['Projects'],
        summary='Update project',
        description='Update a project (full update)'
    ),
    partial_update=extend_schema(
        tags=['Projects'],
        summary='Partial update project',
        description='Partially update a project'
    ),
    destroy=extend_schema(
        tags=['Projects'],
        summary='Delete project',
        description='Delete a project'
    ),
)
class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = (permissions.IsAuthenticated, IsOwner)

    def get_queryset(self):
        return self.queryset.filter(owner=self.request.user)