"""
Tests for Spider serializers.

This module contains tests for spider-related serializers including
SpiderSerializer and its validation, field handling, and functionality.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.test import APIRequestFactory
from apps.projects.models import Project
from apps.scraper.models import Spider
from apps.scraper.serializers import SpiderSerializer
from .test_core import BaseTestCase

User = get_user_model()


class SpiderSerializerTestCase(BaseTestCase):
    """Tests for the SpiderSerializer."""
    
    def setUp(self):
        """Set up test data."""
        super().setUp()
        self.user = self.create_user()
        self.user2 = self.create_user(email='user2@example.com')
        self.project = Project.objects.create(
            owner=self.user,
            name='Test Project',
            notes='Test project for spider serializer tests'
        )
        self.project2 = Project.objects.create(
            owner=self.user2,
            name='Another Project',
            notes='Another test project'
        )
        self.spider = Spider.objects.create(
            project=self.project,
            name='test-spider',
            start_urls_json=['https://example.com', 'https://test.com'],
            settings_json={
                'delay': 1,
                'timeout': 30,
                'headers': {'User-Agent': 'Test Bot'}
            },
            parse_rules_json={
                'title': 'h1',
                'links': 'a[href]'
            }
        )
        
        # Create request factory for context
        self.factory = APIRequestFactory()
    
    def test_serializer_representation(self):
        """Test serializer representation of spider data."""
        serializer = SpiderSerializer(self.spider)
        data = serializer.data
        
        self.assertEqual(data['name'], 'test-spider')
        self.assertEqual(data['start_urls_json'], ['https://example.com', 'https://test.com'])
        self.assertEqual(data['settings_json']['delay'], 1)
        self.assertEqual(data['parse_rules_json']['title'], 'h1')
        self.assertEqual(data['project'], self.project.id)
        self.assertIn('id', data)
        self.assertIn('created_at', data)
    
    def test_serializer_fields(self):
        """Test that serializer has correct fields."""
        serializer = SpiderSerializer()
        fields = serializer.fields
        
        expected_fields = {
            'id', 'project', 'name', 'start_urls_json', 
            'settings_json', 'parse_rules_json', 'created_at'
        }
        self.assertEqual(set(fields.keys()), expected_fields)
    
    def test_read_only_fields(self):
        """Test that read-only fields are properly configured."""
        serializer = SpiderSerializer()
        
        # Check read-only fields
        self.assertTrue(serializer.fields['id'].read_only)
        self.assertTrue(serializer.fields['created_at'].read_only)
        
        # Check writable fields
        self.assertFalse(serializer.fields['project'].read_only)
        self.assertFalse(serializer.fields['name'].read_only)
        self.assertFalse(serializer.fields['start_urls_json'].read_only)
    
    def test_valid_serialization(self):
        """Test serialization of valid spider data."""
        data = {
            'project': self.project.id,
            'name': 'new-spider',
            'start_urls_json': ['https://newsite.com'],
            'settings_json': {'delay': 2},
            'parse_rules_json': {'title': 'h2'}
        }
        
        serializer = SpiderSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        
        spider = serializer.save()
        self.assertEqual(spider.name, 'new-spider')
        self.assertEqual(spider.project, self.project)
        self.assertEqual(spider.start_urls_json, ['https://newsite.com'])
    
    def test_minimal_valid_data(self):
        """Test serialization with minimal required data."""
        data = {
            'project': self.project.id,
            'name': 'minimal-spider',
            'start_urls_json': ['https://minimal.com']
        }
        
        serializer = SpiderSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        
        spider = serializer.save()
        self.assertEqual(spider.name, 'minimal-spider')
        self.assertEqual(spider.project, self.project)
        self.assertIsNone(spider.settings_json)
        self.assertIsNone(spider.parse_rules_json)
    
    def test_missing_required_fields(self):
        """Test validation fails when required fields are missing."""
        # Missing project
        data = {
            'name': 'no-project-spider',
            'start_urls_json': ['https://example.com']
        }
        serializer = SpiderSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('project', serializer.errors)
        
        # Missing name
        data = {
            'project': self.project.id,
            'start_urls_json': ['https://example.com']
        }
        serializer = SpiderSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('name', serializer.errors)
        
        # Missing start_urls_json
        data = {
            'project': self.project.id,
            'name': 'no-urls-spider'
        }
        serializer = SpiderSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('start_urls_json', serializer.errors)
    
    def test_invalid_project_reference(self):
        """Test validation fails with invalid project ID."""
        data = {
            'project': 99999,  # Non-existent project ID
            'name': 'invalid-project-spider',
            'start_urls_json': ['https://example.com']
        }
        
        serializer = SpiderSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('project', serializer.errors)
    
    def test_empty_start_urls_json(self):
        """Test validation with empty start_urls_json."""
        data = {
            'project': self.project.id,
            'name': 'empty-urls-spider',
            'start_urls_json': []
        }
        
        serializer = SpiderSerializer(data=data)
        # Empty list should be valid (though not very useful)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        
        spider = serializer.save()
        self.assertEqual(spider.start_urls_json, [])
    
    def test_json_field_validation(self):
        """Test that JSON fields accept valid JSON data."""
        data = {
            'project': self.project.id,
            'name': 'json-spider',
            'start_urls_json': ['https://example.com'],
            'settings_json': {
                'delay': 1.5,
                'timeout': 30,
                'headers': {'User-Agent': 'Test'},
                'enabled': True,
                'retries': None,
                'list_setting': [1, 2, 3]
            },
            'parse_rules_json': {
                'title': 'h1',
                'complex_rule': {
                    'selector': 'div.content',
                    'attribute': 'text'
                },
                'multiple_selectors': ['p', 'span']
            }
        }
        
        serializer = SpiderSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        
        spider = serializer.save()
        self.assertEqual(spider.settings_json['delay'], 1.5)
        self.assertEqual(spider.parse_rules_json['title'], 'h1')
        self.assertIsInstance(spider.parse_rules_json['complex_rule'], dict)
    
    def test_update_spider(self):
        """Test updating an existing spider."""
        new_data = {
            'name': 'updated-spider',
            'start_urls_json': ['https://updated.com', 'https://new.com'],
            'settings_json': {'delay': 3, 'new_setting': 'value'},
            'parse_rules_json': {'title': 'h2', 'content': 'p'}
        }
        
        serializer = SpiderSerializer(self.spider, data=new_data, partial=True)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        
        updated_spider = serializer.save()
        self.assertEqual(updated_spider.name, 'updated-spider')
        self.assertEqual(updated_spider.start_urls_json, ['https://updated.com', 'https://new.com'])
        self.assertEqual(updated_spider.settings_json['delay'], 3)
        self.assertEqual(updated_spider.settings_json['new_setting'], 'value')
        self.assertEqual(updated_spider.parse_rules_json['title'], 'h2')
        
        # Should still be the same spider instance
        self.assertEqual(updated_spider.id, self.spider.id)
        self.assertEqual(updated_spider.project, self.spider.project)
    
    def test_partial_update(self):
        """Test partial update of spider."""
        # Update only the name
        serializer = SpiderSerializer(
            self.spider, 
            data={'name': 'partially-updated'}, 
            partial=True
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        
        updated_spider = serializer.save()
        self.assertEqual(updated_spider.name, 'partially-updated')
        
        # Other fields should remain unchanged
        self.assertEqual(updated_spider.start_urls_json, self.spider.start_urls_json)
        self.assertEqual(updated_spider.settings_json, self.spider.settings_json)
    
    def test_project_queryset_filtering(self):
        """Test that project field uses correct queryset."""
        serializer = SpiderSerializer()
        project_field = serializer.fields['project']
        
        # Should be a PrimaryKeyRelatedField with Project queryset
        self.assertIsInstance(project_field, serializers.PrimaryKeyRelatedField)
        
        # Get the queryset (it should include all projects for now)
        queryset = project_field.get_queryset()
        self.assertIn(self.project, queryset)
        self.assertIn(self.project2, queryset)
    
    def test_complex_json_structures(self):
        """Test handling of complex JSON structures."""
        complex_settings = {
            'basic': {
                'delay': 1,
                'timeout': 30
            },
            'advanced': {
                'retry_policy': {
                    'max_attempts': 3,
                    'backoff_factor': 2,
                    'status_codes': [500, 502, 503, 504]
                },
                'headers': {
                    'User-Agent': 'CustomBot/1.0',
                    'Accept': 'text/html,application/xhtml+xml',
                    'Accept-Language': 'en-US,en;q=0.9'
                }
            },
            'filters': [
                {'type': 'url', 'pattern': r'.*\.pdf$', 'action': 'skip'},
                {'type': 'content', 'pattern': 'blocked', 'action': 'retry'}
            ]
        }
        
        complex_rules = {
            'extract_rules': {
                'title': {
                    'selector': 'h1, h2.main-title',
                    'attribute': 'text',
                    'required': True,
                    'transforms': ['strip', 'normalize_whitespace']
                },
                'content': {
                    'selector': 'div.article-content',
                    'attribute': 'html',
                    'transforms': ['clean_html', 'extract_text']
                }
            },
            'follow_rules': [
                {
                    'selector': 'a.next-page',
                    'attribute': 'href',
                    'callback': 'parse_page'
                },
                {
                    'selector': 'a.category-link',
                    'attribute': 'href',
                    'callback': 'parse_category'
                }
            ],
            'item_pipeline': [
                'validate_item',
                'clean_text',
                'save_to_database'
            ]
        }
        
        data = {
            'project': self.project.id,
            'name': 'complex-spider',
            'start_urls_json': ['https://complex.com'],
            'settings_json': complex_settings,
            'parse_rules_json': complex_rules
        }
        
        serializer = SpiderSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        
        spider = serializer.save()
        self.assertEqual(spider.settings_json['basic']['delay'], 1)
        self.assertEqual(spider.settings_json['advanced']['retry_policy']['max_attempts'], 3)
        self.assertEqual(len(spider.settings_json['filters']), 2)
        self.assertEqual(spider.parse_rules_json['extract_rules']['title']['required'], True)
        self.assertEqual(len(spider.parse_rules_json['follow_rules']), 2)
    
    def test_serializer_validation_edge_cases(self):
        """Test serializer validation with edge cases."""
        # Test with null values in JSON (should be allowed)
        data = {
            'project': self.project.id,
            'name': 'null-values-spider',
            'start_urls_json': ['https://example.com'],
            'settings_json': {'timeout': None, 'delay': 0},
            'parse_rules_json': {'optional_field': None}
        }
        
        serializer = SpiderSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        
        spider = serializer.save()
        self.assertIsNone(spider.settings_json['timeout'])
        self.assertEqual(spider.settings_json['delay'], 0)
    
    def test_serializer_with_very_long_name(self):
        """Test serializer with maximum allowed name length."""
        long_name = 'a' * 120  # Maximum length allowed by model
        data = {
            'project': self.project.id,
            'name': long_name,
            'start_urls_json': ['https://example.com']
        }
        
        serializer = SpiderSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        
        spider = serializer.save()
        self.assertEqual(spider.name, long_name)
        self.assertEqual(len(spider.name), 120)
    
    def test_serializer_representation_with_none_values(self):
        """Test serializer representation when optional fields are None."""
        minimal_spider = Spider.objects.create(
            project=self.project,
            name='minimal-spider',
            start_urls_json=['https://minimal.com'],
            # settings_json and parse_rules_json will be None
        )
        
        serializer = SpiderSerializer(minimal_spider)
        data = serializer.data
        
        self.assertEqual(data['name'], 'minimal-spider')
        self.assertEqual(data['start_urls_json'], ['https://minimal.com'])
        self.assertIsNone(data['settings_json'])
        self.assertIsNone(data['parse_rules_json'])
    
    def test_serializer_create_and_validate_realistic_spider(self):
        """Test creating a realistic spider configuration."""
        realistic_data = {
            'project': self.project.id,
            'name': 'news-article-spider',
            'start_urls_json': [
                'https://news-site.com/articles',
                'https://news-site.com/breaking-news'
            ],
            'settings_json': {
                'download_delay': 1.5,
                'randomize_delay': True,
                'concurrent_requests': 16,
                'timeout': 30,
                'retry_times': 3,
                'headers': {
                    'User-Agent': 'NewsBot/1.0 (+http://example.com/bot)',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en'
                },
                'respect_robots_txt': True,
                'obey_robots_txt': True
            },
            'parse_rules_json': {
                'article_extraction': {
                    'title': {
                        'selector': 'h1.article-title, h1.headline',
                        'attribute': 'text',
                        'required': True
                    },
                    'author': {
                        'selector': '.author-name, .byline',
                        'attribute': 'text'
                    },
                    'publish_date': {
                        'selector': 'time[datetime], .publish-date',
                        'attribute': 'datetime,text',
                        'transform': 'parse_datetime'
                    },
                    'content': {
                        'selector': '.article-body, .content',
                        'attribute': 'text'
                    },
                    'tags': {
                        'selector': '.tags a, .categories a',
                        'attribute': 'text',
                        'multiple': True
                    }
                },
                'pagination': {
                    'next_page': {
                        'selector': 'a.next, .pagination .next',
                        'attribute': 'href'
                    }
                },
                'filtering': {
                    'allowed_domains': ['news-site.com'],
                    'deny_extensions': ['pdf', 'doc', 'docx', 'xls', 'xlsx']
                }
            }
        }
        
        serializer = SpiderSerializer(data=realistic_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        
        spider = serializer.save()
        self.assertEqual(spider.name, 'news-article-spider')
        self.assertEqual(len(spider.start_urls_json), 2)
        self.assertEqual(spider.settings_json['download_delay'], 1.5)
        self.assertTrue(spider.settings_json['randomize_delay'])
        self.assertEqual(spider.parse_rules_json['article_extraction']['title']['required'], True)
        self.assertIn('pagination', spider.parse_rules_json)
        self.assertIn('filtering', spider.parse_rules_json)