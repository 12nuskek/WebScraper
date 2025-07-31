"""
Tests for Project model.

This module contains tests for the Project model including
relationships with User, model methods, and project-specific functionality.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.utils import timezone
from apps.projects.models import Project
from .test_core import BaseTestCase

User = get_user_model()


class ProjectModelTestCase(BaseTestCase):
    """Tests for the Project model."""
    
    def setUp(self):
        """Set up test data."""
        super().setUp()
        self.user = self.create_user()
        self.user2 = self.create_user(email='user2@example.com')
    
    def test_project_creation(self):
        """Test basic project creation."""
        project = Project.objects.create(
            owner=self.user,
            name='Test Project'
        )
        self.assertIsInstance(project, Project)
        self.assertEqual(project.owner, self.user)
        self.assertEqual(project.name, 'Test Project')
        self.assertEqual(project.notes, '')
        self.assertIsNotNone(project.created_at)
    
    def test_project_creation_with_notes(self):
        """Test project creation with notes."""
        project = Project.objects.create(
            owner=self.user,
            name='Test Project',
            notes='These are test notes for the project.'
        )
        self.assertEqual(project.notes, 'These are test notes for the project.')
    
    def test_project_string_representation(self):
        """Test project __str__ method."""
        project = Project.objects.create(
            owner=self.user,
            name='Test Project'
        )
        self.assertEqual(str(project), 'Test Project')
    
    def test_project_name_uniqueness(self):
        """Test that project names must be unique."""
        Project.objects.create(
            owner=self.user,
            name='Unique Project'
        )
        
        # Attempting to create another project with the same name should fail
        with self.assertRaises(IntegrityError):
            Project.objects.create(
                owner=self.user2,  # Even with different owner
                name='Unique Project'
            )
    
    def test_project_owner_relationship(self):
        """Test foreign key relationship with User model."""
        project = Project.objects.create(
            owner=self.user,
            name='Test Project'
        )
        
        # Test forward relationship
        self.assertEqual(project.owner, self.user)
        
        # Test reverse relationship
        self.assertIn(project, self.user.projects.all())
    
    def test_project_cascade_delete(self):
        """Test that projects are deleted when owner is deleted."""
        project = Project.objects.create(
            owner=self.user,
            name='Test Project'
        )
        project_id = project.id
        
        # Delete the owner
        self.user.delete()
        
        # Project should also be deleted
        with self.assertRaises(Project.DoesNotExist):
            Project.objects.get(id=project_id)
    
    def test_project_created_at_auto_set(self):
        """Test that created_at is automatically set."""
        before_creation = timezone.now()
        project = Project.objects.create(
            owner=self.user,
            name='Test Project'
        )
        after_creation = timezone.now()
        
        self.assertGreaterEqual(project.created_at, before_creation)
        self.assertLessEqual(project.created_at, after_creation)
    
    def test_project_ordering(self):
        """Test that projects are ordered by created_at descending."""
        # Create projects with slight delay to ensure different timestamps
        project1 = Project.objects.create(
            owner=self.user,
            name='First Project'
        )
        
        import time
        time.sleep(0.01)  # Small delay
        
        project2 = Project.objects.create(
            owner=self.user,
            name='Second Project'
        )
        
        # Get all projects
        projects = list(Project.objects.all())
        
        # Should be ordered by created_at descending (newest first)
        self.assertEqual(projects[0], project2)  # Newest first
        self.assertEqual(projects[1], project1)  # Older second
    
    def test_project_name_max_length(self):
        """Test project name max length validation."""
        long_name = 'x' * 121  # 121 characters, exceeds max_length of 120
        
        project = Project(
            owner=self.user,
            name=long_name
        )
        
        with self.assertRaises(Exception):  # ValidationError on full_clean()
            project.full_clean()
    
    def test_project_notes_text_field(self):
        """Test that notes can store long text."""
        long_notes = 'These are very long notes. ' * 100  # Very long text
        
        project = Project.objects.create(
            owner=self.user,
            name='Test Project',
            notes=long_notes
        )
        
        self.assertEqual(project.notes, long_notes)
        # Should not raise validation errors
        project.full_clean()
    
    def test_project_notes_blank_allowed(self):
        """Test that notes can be blank."""
        project = Project.objects.create(
            owner=self.user,
            name='Test Project',
            notes=''
        )
        
        # Should not raise validation errors
        project.full_clean()
        self.assertEqual(project.notes, '')
    
    def test_multiple_projects_same_owner(self):
        """Test that one user can own multiple projects."""
        project1 = Project.objects.create(
            owner=self.user,
            name='First Project'
        )
        project2 = Project.objects.create(
            owner=self.user,
            name='Second Project'
        )
        
        user_projects = self.user.projects.all()
        self.assertEqual(user_projects.count(), 2)
        self.assertIn(project1, user_projects)
        self.assertIn(project2, user_projects)
    
    def test_multiple_projects_different_owners(self):
        """Test projects with different owners."""
        project1 = Project.objects.create(
            owner=self.user,
            name='User1 Project'
        )
        project2 = Project.objects.create(
            owner=self.user2,
            name='User2 Project'
        )
        
        self.assertEqual(project1.owner, self.user)
        self.assertEqual(project2.owner, self.user2)
        self.assertNotEqual(project1.owner, project2.owner)
        
        # Check that each user only sees their own projects
        self.assertEqual(self.user.projects.count(), 1)
        self.assertEqual(self.user2.projects.count(), 1)
        self.assertIn(project1, self.user.projects.all())
        self.assertNotIn(project2, self.user.projects.all())
    
    def test_project_related_name(self):
        """Test that the related_name 'projects' works correctly."""
        project = Project.objects.create(
            owner=self.user,
            name='Test Project'
        )
        
        # Should be accessible via the related_name
        self.assertIn(project, self.user.projects.all())
        
        # Should not be accessible via default related_name
        with self.assertRaises(AttributeError):
            self.user.project_set.all()
    
    def test_project_model_meta_ordering(self):
        """Test model meta ordering option."""
        self.assertEqual(Project._meta.ordering, ('-created_at',))
    
    def test_project_required_fields(self):
        """Test that owner and name are required fields."""
        from django.db import transaction
        
        # Test missing owner - should raise IntegrityError
        try:
            with transaction.atomic():
                project = Project(name='Test Project')
                project.save()
            self.fail("IntegrityError should have been raised for missing owner")
        except IntegrityError:
            pass  # Expected
        
        # Test empty name - CharField allows empty string by default  
        # Empty string is actually allowed, so this won't raise IntegrityError
        project = Project(owner=self.user, name='')
        project.save()  # This should succeed
        self.assertEqual(project.name, '')