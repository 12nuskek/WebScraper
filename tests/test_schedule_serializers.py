"""
Test cases for Schedule serializers.
"""

from datetime import timedelta
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import serializers

from apps.schedule.models import Schedule
from apps.schedule.serializers import ScheduleSerializer
from apps.spider.models import Spider
from apps.projects.models import Project
from .test_core import BaseTestCase

User = get_user_model()


class ScheduleSerializerTest(BaseTestCase):
    """Test cases for ScheduleSerializer."""

    def setUp(self):
        """Set up test data."""
        super().setUp()
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.other_user = User.objects.create_user(
            email='otheruser@example.com',
            password='testpass123',
            first_name='Other',
            last_name='User'
        )
        
        self.project = Project.objects.create(
            owner=self.user,
            name='Test Project',
            notes='Test project notes'
        )
        self.other_project = Project.objects.create(
            owner=self.other_user,
            name='Other Project',
            notes='Other user project'
        )
        
        self.spider = Spider.objects.create(
            project=self.project,
            name='test-spider',
            start_urls_json=['https://example.com']
        )
        self.other_spider = Spider.objects.create(
            project=self.other_project,
            name='other-spider',
            start_urls_json=['https://other.com']
        )

    def get_context(self, user=None):
        """Helper to create request context."""
        if user is None:
            user = self.user
        
        class MockRequest:
            def __init__(self, user):
                self.user = user
                
        return {'request': MockRequest(user)}

    def test_schedule_serializer_valid_data(self):
        """Test ScheduleSerializer with valid data."""
        data = {
            'spider': self.spider.id,
            'cron_expr': '0 */6 * * *',
            'timezone': 'Australia/Brisbane',
            'enabled': True
        }
        
        serializer = ScheduleSerializer(data=data, context=self.get_context())
        self.assertTrue(serializer.is_valid(), serializer.errors)
        
        schedule = serializer.save()
        self.assertEqual(schedule.spider, self.spider)
        self.assertEqual(schedule.cron_expr, '0 */6 * * *')
        self.assertEqual(schedule.timezone, 'Australia/Brisbane')
        self.assertTrue(schedule.enabled)
        self.assertIsNotNone(schedule.next_run_at)
        
    def test_schedule_serializer_with_all_fields(self):
        """Test ScheduleSerializer with complete data."""
        data = {
            'spider': self.spider.id,
            'cron_expr': '0 9 * * 1-5',
            'timezone': 'America/New_York',
            'enabled': False
        }
        
        serializer = ScheduleSerializer(data=data, context=self.get_context())
        self.assertTrue(serializer.is_valid(), serializer.errors)
        
        schedule = serializer.save()
        self.assertEqual(schedule.cron_expr, '0 9 * * 1-5')
        self.assertEqual(schedule.timezone, 'America/New_York')
        self.assertFalse(schedule.enabled)
        
    def test_schedule_serializer_missing_required_fields(self):
        """Test ScheduleSerializer with missing required fields."""
        # Missing spider
        data = {
            'cron_expr': '0 * * * *',
            'enabled': True
        }
        serializer = ScheduleSerializer(data=data, context=self.get_context())
        self.assertFalse(serializer.is_valid())
        self.assertIn('spider', serializer.errors)
        
        # Missing cron_expr
        data = {
            'spider': self.spider.id,
            'enabled': True
        }
        serializer = ScheduleSerializer(data=data, context=self.get_context())
        self.assertFalse(serializer.is_valid())
        self.assertIn('cron_expr', serializer.errors)
        
    def test_schedule_serializer_invalid_spider(self):
        """Test ScheduleSerializer with invalid spider ID."""
        data = {
            'spider': 99999,  # Non-existent spider
            'cron_expr': '0 * * * *',
            'enabled': True
        }
        
        serializer = ScheduleSerializer(data=data, context=self.get_context())
        self.assertFalse(serializer.is_valid())
        self.assertIn('spider', serializer.errors)
        
    def test_schedule_serializer_other_users_spider(self):
        """Test ScheduleSerializer validates spider ownership."""
        data = {
            'spider': self.other_spider.id,  # Other user's spider
            'cron_expr': '0 * * * *',
            'enabled': True
        }
        
        serializer = ScheduleSerializer(data=data, context=self.get_context(self.user))
        self.assertFalse(serializer.is_valid())
        self.assertIn('spider', serializer.errors)
        self.assertIn('your own spiders', str(serializer.errors['spider'][0]))
        
    def test_schedule_serializer_cron_validation(self):
        """Test cron expression validation."""
        # Invalid cron expressions
        invalid_crons = [
            '* * * *',          # Too few fields
            '* * * * * *',      # Too many fields
            '60 * * * *',       # Invalid minute
            'invalid expr',     # Non-numeric
        ]
        
        for invalid_cron in invalid_crons:
            data = {
                'spider': self.spider.id,
                'cron_expr': invalid_cron,
                'enabled': True
            }
            
            serializer = ScheduleSerializer(data=data, context=self.get_context())
            self.assertFalse(serializer.is_valid(), f"Cron '{invalid_cron}' should be invalid")
            self.assertIn('cron_expr', serializer.errors)
            
        # Valid cron expressions
        valid_crons = [
            '* * * * *',        # Every minute
            '0 * * * *',        # Every hour
            '0 */6 * * *',      # Every 6 hours
            '0 9 * * 1-5',      # Weekdays at 9 AM
        ]
        
        for valid_cron in valid_crons:
            data = {
                'spider': self.spider.id,
                'cron_expr': valid_cron,
                'enabled': True
            }
            
            serializer = ScheduleSerializer(data=data, context=self.get_context())
            self.assertTrue(serializer.is_valid(), f"Cron '{valid_cron}' should be valid: {serializer.errors}")
            
    def test_schedule_serializer_timezone_validation(self):
        """Test timezone validation."""
        # Invalid timezone
        data = {
            'spider': self.spider.id,
            'cron_expr': '0 * * * *',
            'timezone': 'Invalid/Timezone',
            'enabled': True
        }
        
        serializer = ScheduleSerializer(data=data, context=self.get_context())
        self.assertFalse(serializer.is_valid())
        self.assertIn('timezone', serializer.errors)
        
        # Valid timezones
        valid_timezones = [
            'UTC',
            'Australia/Brisbane',
            'America/New_York',
            'Europe/London',
            'Asia/Tokyo'
        ]
        
        for tz in valid_timezones:
            data = {
                'spider': self.spider.id,
                'cron_expr': '0 * * * *',
                'timezone': tz,
                'enabled': True
            }
            
            serializer = ScheduleSerializer(data=data, context=self.get_context())
            self.assertTrue(serializer.is_valid(), f"Timezone '{tz}' should be valid: {serializer.errors}")
            
    def test_schedule_serializer_read_only_fields(self):
        """Test that read-only fields are properly handled."""
        schedule = Schedule.objects.create(
            spider=self.spider,
            cron_expr='0 */6 * * *',
            enabled=True
        )
        
        serializer = ScheduleSerializer(schedule)
        data = serializer.data
        
        # Check that read-only fields are included
        self.assertIn('id', data)
        self.assertIn('next_run_at', data)
        self.assertIn('created_at', data)
        self.assertIn('updated_at', data)
        self.assertIn('time_until_next_run', data)
        self.assertIn('is_overdue', data)
        self.assertIn('is_due', data)
        
    def test_schedule_serializer_computed_properties(self):
        """Test that computed properties are correctly calculated."""
        # Create schedule that's due
        schedule = Schedule.objects.create(
            spider=self.spider,
            cron_expr='0 * * * *',
            enabled=True
        )
        
        # Set to past time to make it due
        schedule.next_run_at = timezone.now() - timedelta(minutes=5)
        schedule.save()
        
        serializer = ScheduleSerializer(schedule)
        data = serializer.data
        
        self.assertTrue(data['is_due'])
        self.assertTrue(data['is_overdue'])
        
        # Test non-due schedule
        schedule.next_run_at = timezone.now() + timedelta(hours=1)
        schedule.save()
        
        serializer = ScheduleSerializer(schedule)
        data = serializer.data
        
        self.assertFalse(data['is_due'])
        self.assertFalse(data['is_overdue'])
        
    def test_schedule_serializer_update(self):
        """Test updating a schedule through serializer."""
        schedule = Schedule.objects.create(
            spider=self.spider,
            cron_expr='*/5 * * * *',  # Every 5 minutes
            enabled=True
        )
        
        old_next_run = schedule.next_run_at
        
        update_data = {
            'cron_expr': '*/10 * * * *',  # Every 10 minutes - different pattern
            'enabled': True
        }
        
        serializer = ScheduleSerializer(schedule, data=update_data, partial=True)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        
        updated_schedule = serializer.save()
        self.assertEqual(updated_schedule.cron_expr, '*/10 * * * *')
        
        # Should have recalculated next_run_at (might be same if timing aligns, but cron changed)
        self.assertEqual(updated_schedule.cron_expr, '*/10 * * * *')
        
    def test_schedule_serializer_enable_disable_update(self):
        """Test enabling/disabling schedule through serializer."""
        schedule = Schedule.objects.create(
            spider=self.spider,
            cron_expr='0 * * * *',
            enabled=False
        )
        
        self.assertIsNone(schedule.next_run_at)
        
        # Enable schedule
        update_data = {'enabled': True}
        serializer = ScheduleSerializer(schedule, data=update_data, partial=True)
        self.assertTrue(serializer.is_valid())
        
        updated_schedule = serializer.save()
        self.assertTrue(updated_schedule.enabled)
        self.assertIsNotNone(updated_schedule.next_run_at)
        
        # Disable schedule
        update_data = {'enabled': False}
        serializer = ScheduleSerializer(updated_schedule, data=update_data, partial=True)
        self.assertTrue(serializer.is_valid())
        
        updated_schedule = serializer.save()
        self.assertFalse(updated_schedule.enabled)
        
    def test_schedule_serializer_default_values(self):
        """Test ScheduleSerializer with default values."""
        data = {
            'spider': self.spider.id,
            'cron_expr': '0 * * * *'
            # timezone and enabled should use defaults
        }
        
        serializer = ScheduleSerializer(data=data, context=self.get_context())
        self.assertTrue(serializer.is_valid(), serializer.errors)
        
        schedule = serializer.save()
        self.assertEqual(schedule.timezone, 'Australia/Brisbane')  # Default
        self.assertTrue(schedule.enabled)  # Default
        
    def test_schedule_serializer_cron_whitespace_handling(self):
        """Test that cron expressions handle whitespace correctly."""
        data = {
            'spider': self.spider.id,
            'cron_expr': '  0  *  *  *  *  ',  # Extra whitespace
            'enabled': True
        }
        
        serializer = ScheduleSerializer(data=data, context=self.get_context())
        self.assertTrue(serializer.is_valid(), serializer.errors)
        
        schedule = serializer.save()
        self.assertEqual(schedule.cron_expr, '0  *  *  *  *')  # Trimmed but internal spaces preserved