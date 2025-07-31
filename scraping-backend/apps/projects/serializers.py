from rest_framework import serializers
from .models import Project


class ProjectSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Project
        fields = ("id", "name", "notes", "created_at", "owner")
        read_only_fields = ("id", "created_at", "owner")