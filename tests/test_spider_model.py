"""
Test cases for Spider model.
"""

import json
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from apps.spider.models import Spider
from apps.projects.models import Project
from .test_core import BaseTestCase

User = get_user_model()


class SpiderModelTest(BaseTestCase):
    """Test cases for Spider model."""

    def setUp(self):
        """Set up test data."""
        super().setUp()
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.project = Project.objects.create(
            owner=self.user,
            name='Test Project',
            notes='Test project notes'
        )

    def test_spider_creation(self):
        """Test creating a spider."""
        spider = Spider.objects.create(
            project=self.project,
            name='test-spider',
            start_urls_json=['https://example.com', 'https://test.com'],
            settings_json={'delay': 1, 'timeout': 30},
            parse_rules_json={'title': 'h1', 'links': 'a[href]'}
        )
        
        self.assertEqual(spider.name, 'test-spider')
        self.assertEqual(spider.project, self.project)
        self.assertEqual(spider.start_urls_json, ['https://example.com', 'https://test.com'])
        self.assertEqual(spider.settings_json, {'delay': 1, 'timeout': 30})
        self.assertEqual(spider.parse_rules_json, {'title': 'h1', 'links': 'a[href]'})
        self.assertIsNotNone(spider.created_at)
        
    def test_spider_str_representation(self):
        """Test spider string representation."""
        spider = Spider.objects.create(
            project=self.project,
            name='test-spider',
            start_urls_json=['https://example.com']
        )
        expected = f"{self.project.name} / test-spider"
        self.assertEqual(str(spider), expected)
        
    def test_spider_unique_name_per_project(self):
        """Test that spider names must be unique per project."""
        Spider.objects.create(
            project=self.project,
            name='duplicate-spider',
            start_urls_json=['https://example.com']
        )
        
        # Try to create another spider with the same name in the same project
        with self.assertRaises(IntegrityError):
            Spider.objects.create(
                project=self.project,
                name='duplicate-spider',
                start_urls_json=['https://example.com']
            )
            
    def test_spider_same_name_different_projects(self):
        """Test that spiders can have the same name in different projects."""
        project2 = Project.objects.create(
            owner=self.user,
            name='Test Project 2',
            notes='Another test project'
        )
        
        spider1 = Spider.objects.create(
            project=self.project,
            name='same-name',
            start_urls_json=['https://example.com']
        )
        
        spider2 = Spider.objects.create(
            project=project2,
            name='same-name',
            start_urls_json=['https://test.com']
        )
        
        self.assertEqual(spider1.name, spider2.name)
        self.assertNotEqual(spider1.project, spider2.project)
        
    def test_spider_cascade_delete_with_project(self):
        """Test that spiders are deleted when project is deleted."""
        spider = Spider.objects.create(
            project=self.project,
            name='test-spider',
            start_urls_json=['https://example.com']
        )
        
        spider_id = spider.id
        self.project.delete()
        
        with self.assertRaises(Spider.DoesNotExist):
            Spider.objects.get(id=spider_id)
            
    def test_spider_json_fields_optional(self):
        """Test that settings and parse_rules JSON fields are optional."""
        spider = Spider.objects.create(
            project=self.project,
            name='minimal-spider',
            start_urls_json=['https://example.com']
        )
        
        self.assertIsNone(spider.settings_json)
        self.assertIsNone(spider.parse_rules_json)
        
    def test_spider_ordering(self):
        """Test that spiders are ordered by created_at descending."""
        spider1 = Spider.objects.create(
            project=self.project,
            name='spider1',
            start_urls_json=['https://example.com']
        )
        
        spider2 = Spider.objects.create(
            project=self.project,
            name='spider2',
            start_urls_json=['https://test.com']
        )
        
        spiders = list(Spider.objects.all())
        self.assertEqual(spiders[0], spider2)  # Most recent first
        self.assertEqual(spiders[1], spider1)
