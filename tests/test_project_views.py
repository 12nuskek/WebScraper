"""
Tests for Project views.

This module contains tests for project-related views including
ProjectViewSet, IsOwner permission, and project management functionality.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from apps.projects.models import Project
from apps.projects.views import IsOwner
from .test_core import BaseTestCase

User = get_user_model()


class IsOwnerPermissionTestCase(BaseTestCase):
    """Tests for the IsOwner permission class."""
    
    def setUp(self):
        """Set up test data."""
        super().setUp()
        self.user1 = self.create_user()
        self.user2 = self.create_user(email='user2@example.com')
        self.project = Project.objects.create(
            owner=self.user1,
            name='Test Project'
        )
        self.permission = IsOwner()
    
    def test_owner_has_permission(self):
        """Test that owner has object permission."""
        # Mock request with user1 (owner)
        class MockRequest:
            def __init__(self, user):
                self.user = user
        
        request = MockRequest(self.user1)
        
        # Mock view (not used in this permission)
        view = None
        
        has_permission = self.permission.has_object_permission(
            request, view, self.project
        )
        
        self.assertTrue(has_permission)
    
    def test_non_owner_no_permission(self):
        """Test that non-owner doesn't have object permission."""
        # Mock request with user2 (not owner)
        class MockRequest:
            def __init__(self, user):
                self.user = user
        
        request = MockRequest(self.user2)
        view = None
        
        has_permission = self.permission.has_object_permission(
            request, view, self.project
        )
        
        self.assertFalse(has_permission)


class ProjectViewSetTestCase(APITestCase, BaseTestCase):
    """Tests for the ProjectViewSet."""
    
    def setUp(self):
        """Set up test data."""
        super().setUp()
        self.projects_url = '/projects/'
        self.user1 = self.create_user()
        self.user2 = self.create_user(email='user2@example.com')
        
        # Create projects for both users
        self.project1 = Project.objects.create(
            owner=self.user1,
            name='User1 Project 1',
            notes='Notes for project 1'
        )
        self.project2 = Project.objects.create(
            owner=self.user1,
            name='User1 Project 2'
        )
        self.project3 = Project.objects.create(
            owner=self.user2,
            name='User2 Project 1'
        )
        
        # Authenticate as user1 by default
        self.authenticate_user(self.user1)
    
    def authenticate_user(self, user):
        """Helper method to authenticate a user."""
        refresh_token = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh_token.access_token}')
    
    def test_list_projects_authenticated(self):
        """Test listing projects for authenticated user."""
        response = self.client.get(self.projects_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)  # Only user1's projects
        
        project_names = [project['name'] for project in response.data['results']]
        self.assertIn('User1 Project 1', project_names)
        self.assertIn('User1 Project 2', project_names)
        self.assertNotIn('User2 Project 1', project_names)
    
    def test_list_projects_unauthenticated(self):
        """Test listing projects without authentication."""
        self.client.credentials()  # Remove authentication
        
        response = self.client.get(self.projects_url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_create_project(self):
        """Test creating a new project."""
        project_data = {
            'name': 'New Project',
            'notes': 'Notes for new project'
        }
        
        response = self.client.post(
            self.projects_url,
            project_data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'New Project')
        self.assertEqual(response.data['notes'], 'Notes for new project')
        # Owner field is hidden in serializer output
        
        # Verify in database
        project = Project.objects.get(name='New Project')
        self.assertEqual(project.owner, self.user1)
    
    def test_create_project_without_authentication(self):
        """Test creating a project without authentication."""
        self.client.credentials()  # Remove authentication
        
        project_data = {
            'name': 'Unauthorized Project',
            'notes': 'This should fail'
        }
        
        response = self.client.post(
            self.projects_url,
            project_data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_create_project_with_duplicate_name(self):
        """Test creating a project with duplicate name."""
        project_data = {
            'name': 'User1 Project 1',  # Already exists
            'notes': 'Duplicate name'
        }
        
        response = self.client.post(
            self.projects_url,
            project_data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)
    
    def test_retrieve_own_project(self):
        """Test retrieving user's own project."""
        url = f'{self.projects_url}{self.project1.id}/'
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'User1 Project 1')
        # Owner field is hidden in serializer output
    
    def test_retrieve_other_users_project(self):
        """Test retrieving another user's project (should fail)."""
        url = f'{self.projects_url}{self.project3.id}/'
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_update_own_project(self):
        """Test updating user's own project."""
        url = f'{self.projects_url}{self.project1.id}/'
        update_data = {
            'name': 'Updated Project Name',
            'notes': 'Updated notes'
        }
        
        response = self.client.put(
            url,
            update_data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Updated Project Name')
        self.assertEqual(response.data['notes'], 'Updated notes')
        
        # Verify in database
        self.project1.refresh_from_db()
        self.assertEqual(self.project1.name, 'Updated Project Name')
        self.assertEqual(self.project1.notes, 'Updated notes')
    
    def test_partial_update_own_project(self):
        """Test partial update of user's own project."""
        url = f'{self.projects_url}{self.project1.id}/'
        update_data = {
            'notes': 'Partially updated notes'
        }
        
        response = self.client.patch(
            url,
            update_data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'User1 Project 1')  # Unchanged
        self.assertEqual(response.data['notes'], 'Partially updated notes')
    
    def test_update_other_users_project(self):
        """Test updating another user's project (should fail)."""
        url = f'{self.projects_url}{self.project3.id}/'
        update_data = {
            'name': 'Unauthorized Update',
            'notes': 'This should fail'
        }
        
        response = self.client.put(
            url,
            update_data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_delete_own_project(self):
        """Test deleting user's own project."""
        url = f'{self.projects_url}{self.project1.id}/'
        
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify project is deleted
        with self.assertRaises(Project.DoesNotExist):
            Project.objects.get(id=self.project1.id)
    
    def test_delete_other_users_project(self):
        """Test deleting another user's project (should fail)."""
        url = f'{self.projects_url}{self.project3.id}/'
        
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
        # Verify project still exists
        Project.objects.get(id=self.project3.id)  # Should not raise DoesNotExist
    
    def test_queryset_filtering(self):
        """Test that queryset only returns user's own projects."""
        # Authenticate as user2
        self.authenticate_user(self.user2)
        
        response = self.client.get(self.projects_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)  # Only user2's project
        self.assertEqual(response.data['results'][0]['name'], 'User2 Project 1')


class ProjectViewSetEdgeCasesTestCase(APITestCase, BaseTestCase):
    """Tests for edge cases in ProjectViewSet."""
    
    def setUp(self):
        """Set up test data."""
        super().setUp()
        self.projects_url = '/projects/'
        self.user = self.create_user()
        self.authenticate_user(self.user)
    
    def authenticate_user(self, user):
        """Helper method to authenticate a user."""
        refresh_token = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh_token.access_token}')
    
    def test_create_project_without_name(self):
        """Test creating a project without name (required field)."""
        project_data = {
            'notes': 'Project without name'
        }
        
        response = self.client.post(
            self.projects_url,
            project_data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)
    
    def test_create_project_with_empty_name(self):
        """Test creating a project with empty name."""
        project_data = {
            'name': '',
            'notes': 'Project with empty name'
        }
        
        response = self.client.post(
            self.projects_url,
            project_data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)
    
    def test_create_project_with_long_name(self):
        """Test creating a project with name exceeding max length."""
        project_data = {
            'name': 'x' * 121,  # Exceeds max_length of 120
            'notes': 'Project with long name'
        }
        
        response = self.client.post(
            self.projects_url,
            project_data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)
    
    def test_create_project_with_only_notes(self):
        """Test that projects can be created with only notes (and name)."""
        project_data = {
            'name': 'Minimal Project'
            # No notes field
        }
        
        response = self.client.post(
            self.projects_url,
            project_data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Minimal Project')
        self.assertEqual(response.data['notes'], '')  # Should default to empty
    
    def test_list_projects_ordering(self):
        """Test that projects are returned in correct order (newest first)."""
        # Create projects with slight delay to ensure different timestamps
        project1 = Project.objects.create(
            owner=self.user,
            name='First Project'
        )
        
        import time
        time.sleep(0.01)
        
        project2 = Project.objects.create(
            owner=self.user,
            name='Second Project'
        )
        
        response = self.client.get(self.projects_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        projects = response.data['results']
        
        # Should be ordered by created_at descending (newest first)
        self.assertEqual(projects[0]['name'], 'Second Project')
        self.assertEqual(projects[1]['name'], 'First Project')
    
    def test_project_read_only_fields(self):
        """Test that read-only fields cannot be modified."""
        project = Project.objects.create(
            owner=self.user,
            name='Test Project'
        )
        
        url = f'{self.projects_url}{project.id}/'
        
        # Try to modify read-only fields
        update_data = {
            'name': 'Updated Name',
            'id': 999,  # Read-only
            'created_at': '2020-01-01T00:00:00Z',  # Read-only
            'owner': 999  # Read-only
        }
        
        response = self.client.put(
            url,
            update_data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify read-only fields weren't changed
        project.refresh_from_db()
        self.assertEqual(project.name, 'Updated Name')  # This should change
        self.assertNotEqual(project.id, 999)  # This should not change
        self.assertEqual(project.owner, self.user)  # This should not change