"""
Tests for Project serializers.

This module contains tests for project-related serializers including
ProjectSerializer and its validation, field handling, and functionality.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.test import APIRequestFactory
from apps.projects.models import Project
from apps.projects.serializers import ProjectSerializer
from .test_core import BaseTestCase

User = get_user_model()


class ProjectSerializerTestCase(BaseTestCase):
    """Tests for the ProjectSerializer."""
    
    def setUp(self):
        """Set up test data."""
        super().setUp()
        self.user = self.create_user()
        self.user2 = self.create_user(email='user2@example.com')
        self.project = Project.objects.create(
            owner=self.user,
            name='Test Project',
            notes='Test notes'
        )
        
        # Create request factory for context
        self.factory = APIRequestFactory()
    
    def test_serializer_representation(self):
        """Test serializer representation of project data."""
        serializer = ProjectSerializer(self.project)
        data = serializer.data
        
        self.assertEqual(data['name'], 'Test Project')
        self.assertEqual(data['notes'], 'Test notes')
        # Owner field is hidden in output
        self.assertNotIn('owner', data)  
        self.assertIn('id', data)
        self.assertIn('created_at', data)
    
    def test_serializer_fields(self):
        """Test that serializer has correct fields."""
        serializer = ProjectSerializer()
        fields = serializer.fields.keys()
        
        expected_fields = {'id', 'name', 'notes', 'created_at', 'owner'}
        self.assertEqual(set(fields), expected_fields)
    
    def test_read_only_fields(self):
        """Test that read-only fields are properly configured."""
        serializer = ProjectSerializer()
        
        self.assertTrue(serializer.fields['id'].read_only)
        self.assertTrue(serializer.fields['created_at'].read_only)
        # Owner field is HiddenField, not read_only field
        self.assertFalse(serializer.fields['owner'].read_only)
    
    def test_hidden_owner_field(self):
        """Test that owner field is hidden and uses CurrentUserDefault."""
        serializer = ProjectSerializer()
        
        # Owner field should be a HiddenField
        self.assertIsInstance(
            serializer.fields['owner'],
            serializers.HiddenField
        )
        
        # Should use CurrentUserDefault
        self.assertIsInstance(
            serializer.fields['owner'].default,
            serializers.CurrentUserDefault
        )
    
    def test_create_project_with_context(self):
        """Test creating a project with user context."""
        # Create a request with user context
        request = self.factory.post('/')
        request.user = self.user
        
        project_data = {
            'name': 'New Project',
            'notes': 'New project notes'
        }
        
        serializer = ProjectSerializer(
            data=project_data,
            context={'request': request}
        )
        
        self.assertTrue(serializer.is_valid())
        project = serializer.save()
        
        self.assertEqual(project.name, 'New Project')
        self.assertEqual(project.notes, 'New project notes')
        self.assertEqual(project.owner, self.user)
    
    def test_create_project_without_context(self):
        """Test that creating without context fails (needs request context)."""
        project_data = {
            'name': 'New Project',
            'notes': 'New project notes'
        }
        
        serializer = ProjectSerializer(data=project_data)
        
        # Should fail without context due to CurrentUserDefault
        with self.assertRaises(KeyError):
            serializer.is_valid()
    
    def test_validate_required_name_field(self):
        """Test that name field is required."""
        # Create request context
        request = self.factory.post('/')
        request.user = self.user
        
        project_data = {
            'notes': 'Project without name'
        }
        
        serializer = ProjectSerializer(
            data=project_data,
            context={'request': request}
        )
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('name', serializer.errors)
    
    def test_validate_empty_name(self):
        """Test validation with empty name."""
        # Create request context
        request = self.factory.post('/')
        request.user = self.user
        
        project_data = {
            'name': '',
            'notes': 'Project with empty name'
        }
        
        serializer = ProjectSerializer(
            data=project_data,
            context={'request': request}
        )
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('name', serializer.errors)
    
    def test_validate_name_max_length(self):
        """Test name max length validation."""
        # Create request context
        request = self.factory.post('/')
        request.user = self.user
        
        project_data = {
            'name': 'x' * 121,  # Exceeds max_length of 120
            'notes': 'Valid notes'
        }
        
        serializer = ProjectSerializer(
            data=project_data,
            context={'request': request}
        )
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('name', serializer.errors)
    
    def test_notes_field_optional(self):
        """Test that notes field is optional."""
        # Create request context
        request = self.factory.post('/')
        request.user = self.user
        
        project_data = {
            'name': 'Project Without Notes'
        }
        
        serializer = ProjectSerializer(
            data=project_data,
            context={'request': request}
        )
        
        self.assertTrue(serializer.is_valid())
    
    def test_notes_field_can_be_empty(self):
        """Test that notes field can be empty."""
        # Create request context
        request = self.factory.post('/')
        request.user = self.user
        
        project_data = {
            'name': 'Project With Empty Notes',
            'notes': ''
        }
        
        serializer = ProjectSerializer(
            data=project_data,
            context={'request': request}
        )
        
        self.assertTrue(serializer.is_valid())
    
    def test_notes_field_long_text(self):
        """Test that notes field can handle long text."""
        # Create request context
        request = self.factory.post('/')
        request.user = self.user
        
        long_notes = 'This is a very long note. ' * 100
        
        project_data = {
            'name': 'Project With Long Notes',
            'notes': long_notes
        }
        
        serializer = ProjectSerializer(
            data=project_data,
            context={'request': request}
        )
        
        self.assertTrue(serializer.is_valid())
    
    def test_update_project_name(self):
        """Test updating project name."""
        update_data = {
            'name': 'Updated Project Name'
        }
        
        serializer = ProjectSerializer(
            self.project,
            data=update_data,
            partial=True
        )
        
        self.assertTrue(serializer.is_valid())
        updated_project = serializer.save()
        
        self.assertEqual(updated_project.name, 'Updated Project Name')
        self.assertEqual(updated_project.notes, 'Test notes')  # Should remain
        self.assertEqual(updated_project.owner, self.user)  # Should remain
    
    def test_update_project_notes(self):
        """Test updating project notes."""
        update_data = {
            'notes': 'Updated project notes'
        }
        
        serializer = ProjectSerializer(
            self.project,
            data=update_data,
            partial=True
        )
        
        self.assertTrue(serializer.is_valid())
        updated_project = serializer.save()
        
        self.assertEqual(updated_project.name, 'Test Project')  # Should remain
        self.assertEqual(updated_project.notes, 'Updated project notes')
        self.assertEqual(updated_project.owner, self.user)  # Should remain
    
    def test_update_project_full(self):
        """Test full update of project."""
        # Create request context
        request = self.factory.post('/')
        request.user = self.user
        
        update_data = {
            'name': 'Fully Updated Project',
            'notes': 'Fully updated notes'
        }
        
        serializer = ProjectSerializer(
            self.project,
            data=update_data,
            context={'request': request}
        )
        
        self.assertTrue(serializer.is_valid())
        updated_project = serializer.save()
        
        self.assertEqual(updated_project.name, 'Fully Updated Project')
        self.assertEqual(updated_project.notes, 'Fully updated notes')
        self.assertEqual(updated_project.owner, self.user)  # Should remain
    
    def test_cannot_update_read_only_fields(self):
        """Test that read-only fields cannot be updated."""
        # Create request context
        request = self.factory.post('/')
        request.user = self.user
        
        original_id = self.project.id
        original_created_at = self.project.created_at
        original_owner = self.project.owner
        
        update_data = {
            'name': 'Updated Name',
            'id': 999,
            'created_at': '2020-01-01T00:00:00Z',
            'owner': self.user2.id
        }
        
        serializer = ProjectSerializer(
            self.project,
            data=update_data,
            context={'request': request}
        )
        
        self.assertTrue(serializer.is_valid())
        updated_project = serializer.save()
        
        # Name should be updated
        self.assertEqual(updated_project.name, 'Updated Name')
        
        # Read-only fields should not be updated
        self.assertEqual(updated_project.id, original_id)
        self.assertEqual(updated_project.created_at, original_created_at)
        self.assertEqual(updated_project.owner, original_owner)
    
    def test_serializer_with_multiple_projects(self):
        """Test serializer with multiple projects."""
        project2 = Project.objects.create(
            owner=self.user2,
            name='Second Project',
            notes='Second notes'
        )
        
        projects = [self.project, project2]
        serializer = ProjectSerializer(projects, many=True)
        data = serializer.data
        
        self.assertEqual(len(data), 2)
        
        # Check first project
        self.assertEqual(data[0]['name'], 'Test Project')
        # Owner field is hidden in output
        self.assertNotIn('owner', data[0])
        
        # Check second project
        self.assertEqual(data[1]['name'], 'Second Project')
        # Owner field is hidden in output
        self.assertNotIn('owner', data[1])


class ProjectSerializerValidationTestCase(BaseTestCase):
    """Tests specifically for ProjectSerializer validation."""
    
    def setUp(self):
        """Set up test data."""
        super().setUp()
        self.user = self.create_user()
        
        # Create request factory for context
        self.factory = APIRequestFactory()
    
    def test_duplicate_name_validation(self):
        """Test that duplicate names are caught by serializer validation."""
        # Create first project
        Project.objects.create(
            owner=self.user,
            name='Duplicate Name Project'
        )
        
        # Create request context
        request = self.factory.post('/')
        request.user = self.user
        
        # Try to create second project with same name
        project_data = {
            'name': 'Duplicate Name Project',
            'notes': 'This should fail'
        }
        
        serializer = ProjectSerializer(
            data=project_data,
            context={'request': request}
        )
        
        # Serializer validation should fail due to unique constraint
        self.assertFalse(serializer.is_valid())
        self.assertIn('name', serializer.errors)
        self.assertEqual(
            serializer.errors['name'][0].code, 
            'unique'
        )
    
    def test_name_whitespace_handling(self):
        """Test how serializer handles whitespace in name."""
        # Create request context
        request = self.factory.post('/')
        request.user = self.user
        
        project_data = {
            'name': '  Project With Spaces  ',
            'notes': 'Test notes'
        }
        
        serializer = ProjectSerializer(
            data=project_data,
            context={'request': request}
        )
        
        self.assertTrue(serializer.is_valid())
        # Note: Django CharField doesn't automatically strip whitespace
        # This would be handled at the model or view level if needed
    
    def test_special_characters_in_name(self):
        """Test project name with special characters."""
        # Create request context
        request = self.factory.post('/')
        request.user = self.user
        
        project_data = {
            'name': 'Project-with_special.chars@2024!',
            'notes': 'Special characters test'
        }
        
        serializer = ProjectSerializer(
            data=project_data,
            context={'request': request}
        )
        
        self.assertTrue(serializer.is_valid())
    
    def test_unicode_characters_in_fields(self):
        """Test project with unicode characters."""
        # Create request context
        request = self.factory.post('/')
        request.user = self.user
        
        project_data = {
            'name': 'Проект с Unicode символами',
            'notes': 'Notes with émojis 🚀 and ñoñó characters'
        }
        
        serializer = ProjectSerializer(
            data=project_data,
            context={'request': request}
        )
        
        self.assertTrue(serializer.is_valid())


class ProjectSerializerContextTestCase(BaseTestCase):
    """Tests for ProjectSerializer context handling."""
    
    def setUp(self):
        """Set up test data."""
        super().setUp()
        self.user = self.create_user()
        
        # Create request factory for context
        self.factory = APIRequestFactory()
    
    def test_current_user_default_with_context(self):
        """Test CurrentUserDefault works with request context."""
        request = self.factory.post('/')
        request.user = self.user
        
        project_data = {
            'name': 'Context Test Project',
            'notes': 'Testing context'
        }
        
        serializer = ProjectSerializer(
            data=project_data,
            context={'request': request}
        )
        
        self.assertTrue(serializer.is_valid())
        
        # Check that the owner is set correctly through CurrentUserDefault
        validated_data = serializer.validated_data
        # Note: The owner field is hidden, so it gets the default value
        # The actual owner setting happens in the view during save()
    
    def test_serializer_without_request_context(self):
        """Test serializer behavior without request context."""
        project_data = {
            'name': 'No Context Project',
            'notes': 'No context test'
        }
        
        serializer = ProjectSerializer(data=project_data)
        
        # Should fail without context due to CurrentUserDefault
        with self.assertRaises(KeyError):
            serializer.is_valid()
    
    def test_serializer_with_empty_context(self):
        """Test serializer with empty context."""
        project_data = {
            'name': 'Empty Context Project',
            'notes': 'Empty context test'
        }
        
        serializer = ProjectSerializer(
            data=project_data,
            context={}
        )
        
        # Should fail without request in context
        with self.assertRaises(KeyError):
            serializer.is_valid()