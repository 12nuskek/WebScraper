"""
Tests for Spider model.

This module contains tests for the Spider model including
relationships with Project and User, model methods, and spider-specific functionality.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.utils import timezone
from django.core.exceptions import ValidationError
from apps.projects.models import Project
from apps.scraper.models import Spider
from .test_core import BaseTestCase

User = get_user_model()


class SpiderModelTestCase(BaseTestCase):
    """Tests for the Spider model."""
    
    def setUp(self):
        """Set up test data."""
        super().setUp()
        self.user = self.create_user()
        self.user2 = self.create_user(email='user2@example.com')
        self.project = Project.objects.create(
            owner=self.user,
            name='Test Project',
            notes='Test project for spider tests'
        )
        self.project2 = Project.objects.create(
            owner=self.user2,
            name='Another Project',
            notes='Another test project'
        )
    
    def test_spider_creation(self):
        """Test basic spider creation."""
        spider_data = {
            'project': self.project,
            'name': 'test-spider',
            'start_urls_json': ['https://example.com', 'https://test.com']
        }
        spider = Spider.objects.create(**spider_data)
        
        self.assertIsInstance(spider, Spider)
        self.assertEqual(spider.project, self.project)
        self.assertEqual(spider.name, 'test-spider')
        self.assertEqual(spider.start_urls_json, ['https://example.com', 'https://test.com'])
        self.assertIsNone(spider.settings_json)
        self.assertIsNone(spider.parse_rules_json)
        self.assertIsNotNone(spider.created_at)
    
    def test_spider_creation_with_all_fields(self):
        """Test spider creation with all optional fields."""
        spider_data = {
            'project': self.project,
            'name': 'advanced-spider',
            'start_urls_json': ['https://example.com'],
            'settings_json': {
                'delay': 1,
                'timeout': 30,
                'user_agent': 'Custom Bot 1.0',
                'headers': {'Accept': 'text/html'}
            },
            'parse_rules_json': {
                'title': 'h1',
                'description': 'meta[name="description"]',
                'links': 'a[href]',
                'images': 'img[src]'
            }
        }
        spider = Spider.objects.create(**spider_data)
        
        self.assertEqual(spider.name, 'advanced-spider')
        self.assertEqual(spider.settings_json['delay'], 1)
        self.assertEqual(spider.settings_json['timeout'], 30)
        self.assertEqual(spider.parse_rules_json['title'], 'h1')
        self.assertEqual(spider.parse_rules_json['links'], 'a[href]')
    
    def test_spider_string_representation(self):
        """Test spider __str__ method."""
        spider = Spider.objects.create(
            project=self.project,
            name='test-spider',
            start_urls_json=['https://example.com']
        )
        expected_str = f"{self.project.name} / test-spider"
        self.assertEqual(str(spider), expected_str)
    
    def test_spider_project_relationship(self):
        """Test the relationship between Spider and Project."""
        spider = Spider.objects.create(
            project=self.project,
            name='test-spider',
            start_urls_json=['https://example.com']
        )
        
        # Test forward relationship
        self.assertEqual(spider.project, self.project)
        
        # Test reverse relationship
        self.assertIn(spider, self.project.spiders.all())
        self.assertEqual(self.project.spiders.count(), 1)
    
    def test_spider_unique_name_per_project(self):
        """Test that spider names must be unique within a project."""
        # Create first spider
        Spider.objects.create(
            project=self.project,
            name='unique-spider',
            start_urls_json=['https://example.com']
        )
        
        # Try to create another spider with the same name in the same project
        with self.assertRaises(IntegrityError):
            Spider.objects.create(
                project=self.project,
                name='unique-spider',
                start_urls_json=['https://different.com']
            )
    
    def test_spider_same_name_different_projects(self):
        """Test that spiders can have the same name in different projects."""
        # Create spider in first project
        spider1 = Spider.objects.create(
            project=self.project,
            name='common-spider',
            start_urls_json=['https://example.com']
        )
        
        # Create spider with same name in different project
        spider2 = Spider.objects.create(
            project=self.project2,
            name='common-spider',
            start_urls_json=['https://different.com']
        )
        
        self.assertEqual(spider1.name, spider2.name)
        self.assertNotEqual(spider1.project, spider2.project)
        self.assertNotEqual(spider1.id, spider2.id)
    
    def test_spider_cascade_delete_with_project(self):
        """Test that spiders are deleted when their project is deleted."""
        spider = Spider.objects.create(
            project=self.project,
            name='test-spider',
            start_urls_json=['https://example.com']
        )
        
        spider_id = spider.id
        self.assertTrue(Spider.objects.filter(id=spider_id).exists())
        
        # Delete the project
        self.project.delete()
        
        # Spider should also be deleted
        self.assertFalse(Spider.objects.filter(id=spider_id).exists())
    
    def test_spider_ordering(self):
        """Test that spiders are ordered by creation time (newest first)."""
        # Create spiders with slight delay to ensure different timestamps
        spider1 = Spider.objects.create(
            project=self.project,
            name='first-spider',
            start_urls_json=['https://example.com']
        )
        
        spider2 = Spider.objects.create(
            project=self.project,
            name='second-spider',
            start_urls_json=['https://example2.com']
        )
        
        spider3 = Spider.objects.create(
            project=self.project,
            name='third-spider',
            start_urls_json=['https://example3.com']
        )
        
        # Get all spiders in default order
        spiders = list(Spider.objects.all())
        
        # Should be ordered by created_at descending (newest first)
        self.assertEqual(spiders[0], spider3)  # Most recent
        self.assertEqual(spiders[1], spider2)
        self.assertEqual(spiders[2], spider1)  # Oldest
    
    def test_spider_json_field_types(self):
        """Test that JSON fields accept various data types."""
        spider = Spider.objects.create(
            project=self.project,
            name='json-test-spider',
            start_urls_json=['https://example.com'],
            settings_json={
                'string_setting': 'test',
                'int_setting': 42,
                'float_setting': 3.14,
                'bool_setting': True,
                'list_setting': [1, 2, 3],
                'dict_setting': {'nested': 'value'}
            },
            parse_rules_json={
                'simple_rule': 'h1',
                'complex_rule': {
                    'selector': 'div.content',
                    'attribute': 'text',
                    'transform': 'strip'
                },
                'multiple_rules': ['p', 'span', 'div']
            }
        )
        
        # Verify the data can be retrieved correctly
        retrieved_spider = Spider.objects.get(id=spider.id)
        self.assertEqual(retrieved_spider.settings_json['string_setting'], 'test')
        self.assertEqual(retrieved_spider.settings_json['int_setting'], 42)
        self.assertEqual(retrieved_spider.settings_json['bool_setting'], True)
        self.assertIsInstance(retrieved_spider.settings_json['list_setting'], list)
        self.assertIsInstance(retrieved_spider.settings_json['dict_setting'], dict)
        
        self.assertEqual(retrieved_spider.parse_rules_json['simple_rule'], 'h1')
        self.assertIsInstance(retrieved_spider.parse_rules_json['complex_rule'], dict)
        self.assertIsInstance(retrieved_spider.parse_rules_json['multiple_rules'], list)
    
    def test_spider_empty_json_fields(self):
        """Test spider creation with empty JSON fields."""
        spider = Spider.objects.create(
            project=self.project,
            name='empty-json-spider',
            start_urls_json=[],  # Empty list
            settings_json={},    # Empty dict
            parse_rules_json={}  # Empty dict
        )
        
        self.assertEqual(spider.start_urls_json, [])
        self.assertEqual(spider.settings_json, {})
        self.assertEqual(spider.parse_rules_json, {})
    
    def test_spider_max_name_length(self):
        """Test that spider name respects max length constraint."""
        # Test valid length (within 120 chars)
        valid_name = 'a' * 120
        spider = Spider.objects.create(
            project=self.project,
            name=valid_name,
            start_urls_json=['https://example.com']
        )
        self.assertEqual(len(spider.name), 120)
    
    def test_spider_meta_properties(self):
        """Test Spider model Meta properties."""
        # Test unique_together constraint exists
        meta = Spider._meta
        unique_together = getattr(meta, 'unique_together', [])
        
        # Should have unique_together on (project, name)
        self.assertIn(('project', 'name'), unique_together)
        
        # Test ordering
        self.assertEqual(meta.ordering, ('-created_at',))
    
    def test_spider_required_fields(self):
        """Test that required fields are enforced."""
        from django.db import transaction
        
        # Test missing project - this should raise IntegrityError due to NOT NULL constraint
        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                Spider.objects.create(
                    name='no-project-spider',
                    start_urls_json=['https://example.com']
                )
    
    def test_spider_realistic_data_example(self):
        """Test spider with realistic scraping configuration."""
        spider = Spider.objects.create(
            project=self.project,
            name='ecommerce-product-spider',
            start_urls_json=[
                'https://example-shop.com/products',
                'https://example-shop.com/categories/electronics'
            ],
            settings_json={
                'download_delay': 2,
                'randomize_delay': True,
                'timeout': 30,
                'retry_times': 3,
                'headers': {
                    'User-Agent': 'Mozilla/5.0 (compatible; WebScraper/1.0)',
                    'Accept': 'text/html,application/xhtml+xml',
                    'Accept-Language': 'en-US,en;q=0.9'
                },
                'cookies_enabled': True,
                'respect_robots_txt': True
            },
            parse_rules_json={
                'product_name': {
                    'selector': 'h1.product-title',
                    'attribute': 'text',
                    'required': True
                },
                'price': {
                    'selector': '.price-current',
                    'attribute': 'text',
                    'transform': 'extract_price'
                },
                'description': {
                    'selector': '.product-description p',
                    'attribute': 'text'
                },
                'images': {
                    'selector': '.product-images img',
                    'attribute': 'src',
                    'multiple': True
                },
                'availability': {
                    'selector': '.stock-status',
                    'attribute': 'text',
                    'default': 'unknown'
                },
                'next_page': {
                    'selector': 'a.next-page',
                    'attribute': 'href'
                }
            }
        )
        
        self.assertEqual(spider.name, 'ecommerce-product-spider')
        self.assertEqual(len(spider.start_urls_json), 2)
        self.assertEqual(spider.settings_json['download_delay'], 2)
        self.assertEqual(spider.parse_rules_json['product_name']['selector'], 'h1.product-title')
        self.assertTrue(spider.parse_rules_json['images']['multiple'])