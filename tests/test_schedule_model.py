"""
Test cases for Schedule model.
"""

from datetime import datetime, timedelta
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
import zoneinfo

from apps.schedule.models import Schedule
from apps.spider.models import Spider
from apps.projects.models import Project
from .test_core import BaseTestCase

User = get_user_model()


class ScheduleModelTest(BaseTestCase):
    """Test cases for Schedule model."""

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
        self.spider = Spider.objects.create(
            project=self.project,
            name='test-spider',
            start_urls_json=['https://example.com']
        )

    def test_schedule_creation(self):
        """Test creating a schedule."""
        schedule = Schedule.objects.create(
            spider=self.spider,
            cron_expr='0 */6 * * *',
            timezone='Australia/Brisbane',
            enabled=True
        )
        
        self.assertEqual(schedule.spider, self.spider)
        self.assertEqual(schedule.cron_expr, '0 */6 * * *')
        self.assertEqual(schedule.timezone, 'Australia/Brisbane')
        self.assertTrue(schedule.enabled)
        self.assertIsNotNone(schedule.next_run_at)
        
    def test_schedule_str_representation(self):
        """Test schedule string representation."""
        schedule = Schedule.objects.create(
            spider=self.spider,
            cron_expr='0 9 * * 1-5',
            enabled=True
        )
        expected = f"Schedule {schedule.id}: {self.spider.name} (0 9 * * 1-5) - enabled"
        self.assertEqual(str(schedule), expected)
        
    def test_cron_expression_validation(self):
        """Test cron expression validation."""
        # Valid expressions
        valid_expressions = [
            '* * * * *',      # Every minute
            '0 * * * *',      # Every hour
            '0 */6 * * *',    # Every 6 hours
            '0 9 * * 1-5',    # Weekdays at 9 AM
            '*/15 * * * *',   # Every 15 minutes
            '0 0 1 * *',      # Monthly
            '0,30 * * * *',   # Twice hourly
            '0 9-17 * * 1-5', # Business hours
        ]
        
        for expr in valid_expressions:
            self.assertTrue(
                Schedule.is_valid_cron_expression(expr),
                f"Expression '{expr}' should be valid"
            )
            
        # Invalid expressions
        invalid_expressions = [
            '',              # Empty
            '* * * *',       # Too few fields
            '* * * * * *',   # Too many fields
            '60 * * * *',    # Invalid minute
            '* 24 * * *',    # Invalid hour
            '* * 0 * *',     # Invalid day
            '* * * 0 *',     # Invalid month
            '* * * * 8',     # Invalid weekday
            'invalid expr',  # Non-numeric
        ]
        
        for expr in invalid_expressions:
            self.assertFalse(
                Schedule.is_valid_cron_expression(expr),
                f"Expression '{expr}' should be invalid"
            )
            
    def test_cron_field_validation(self):
        """Test individual cron field validation."""
        # Test minute field (0-59)
        self.assertTrue(Schedule.is_valid_cron_field('0', (0, 59)))
        self.assertTrue(Schedule.is_valid_cron_field('59', (0, 59)))
        self.assertTrue(Schedule.is_valid_cron_field('*/15', (0, 59)))
        self.assertTrue(Schedule.is_valid_cron_field('0-30', (0, 59)))
        self.assertTrue(Schedule.is_valid_cron_field('0,15,30,45', (0, 59)))
        self.assertFalse(Schedule.is_valid_cron_field('60', (0, 59)))
        self.assertFalse(Schedule.is_valid_cron_field('-1', (0, 59)))
        
    def test_timezone_validation(self):
        """Test timezone validation."""
        # Valid schedule with good timezone
        schedule = Schedule(
            spider=self.spider,
            cron_expr='0 * * * *',
            timezone='Australia/Brisbane',
            enabled=True
        )
        schedule.clean()  # Should not raise
        
        # Invalid timezone
        schedule.timezone = 'Invalid/Timezone'
        with self.assertRaises(ValidationError):
            schedule.clean()
            
    def test_schedule_disabled_by_default_calculation(self):
        """Test that disabled schedules don't calculate next_run_at."""
        schedule = Schedule.objects.create(
            spider=self.spider,
            cron_expr='0 * * * *',
            enabled=False
        )
        self.assertIsNone(schedule.next_run_at)
        
    def test_next_run_calculation(self):
        """Test next run time calculation."""
        # Create schedule for every hour
        schedule = Schedule.objects.create(
            spider=self.spider,
            cron_expr='0 * * * *',  # Every hour
            timezone='UTC',
            enabled=True
        )
        
        # Should have calculated next run time
        self.assertIsNotNone(schedule.next_run_at)
        
        # Next run should be in the future
        self.assertGreater(schedule.next_run_at, timezone.now())
        
    def test_time_until_next_run(self):
        """Test time until next run calculation."""
        schedule = Schedule.objects.create(
            spider=self.spider,
            cron_expr='0 * * * *',
            enabled=True
        )
        
        time_until = schedule.time_until_next_run
        self.assertIsNotNone(time_until)
        self.assertIsInstance(time_until, timedelta)
        self.assertGreater(time_until.total_seconds(), 0)
        
    def test_is_due_method(self):
        """Test is_due method."""
        # Create schedule that should be due
        past_time = timezone.now() - timedelta(minutes=5)
        schedule = Schedule.objects.create(
            spider=self.spider,
            cron_expr='* * * * *',
            enabled=True
        )
        
        # Manually set next_run_at to past time
        schedule.next_run_at = past_time
        schedule.save()
        
        self.assertTrue(schedule.is_due())
        
        # Test disabled schedule
        schedule.enabled = False
        schedule.save()
        self.assertFalse(schedule.is_due())
        
    def test_is_overdue_property(self):
        """Test is_overdue property."""
        schedule = Schedule.objects.create(
            spider=self.spider,
            cron_expr='* * * * *',
            enabled=True
        )
        
        # Initially should not be overdue
        self.assertFalse(schedule.is_overdue)
        
        # Set to past time
        schedule.next_run_at = timezone.now() - timedelta(minutes=5)
        self.assertTrue(schedule.is_overdue)
        
    def test_mark_executed(self):
        """Test mark_executed method."""
        schedule = Schedule.objects.create(
            spider=self.spider,
            cron_expr='*/5 * * * *',  # Every 5 minutes to ensure different times
            enabled=True
        )
        
        old_next_run = schedule.next_run_at
        
        # Wait a small amount to ensure time difference
        import time
        time.sleep(0.1)
        
        schedule.mark_executed()
        
        # Should have updated next_run_at
        self.assertNotEqual(schedule.next_run_at, old_next_run)
        self.assertGreater(schedule.next_run_at, old_next_run)
        
    def test_enable_disable_schedule(self):
        """Test enabling and disabling schedules."""
        schedule = Schedule.objects.create(
            spider=self.spider,
            cron_expr='0 * * * *',
            enabled=False
        )
        
        self.assertIsNone(schedule.next_run_at)
        
        # Enable schedule
        schedule.enabled = True
        schedule.calculate_next_run()
        schedule.save()
        
        self.assertIsNotNone(schedule.next_run_at)
        
        # Disable schedule
        schedule.enabled = False
        schedule.update_next_run()
        
        self.assertIsNone(schedule.next_run_at)
        
    def test_get_due_schedules_classmethod(self):
        """Test get_due_schedules class method."""
        # Create schedule that's due
        past_time = timezone.now() - timedelta(minutes=5)
        due_schedule = Schedule.objects.create(
            spider=self.spider,
            cron_expr='* * * * *',
            enabled=True
        )
        due_schedule.next_run_at = past_time
        due_schedule.save()
        
        # Create schedule that's not due
        future_time = timezone.now() + timedelta(hours=1)
        not_due_schedule = Schedule.objects.create(
            spider=self.spider,
            cron_expr='0 * * * *',
            enabled=True
        )
        not_due_schedule.next_run_at = future_time
        not_due_schedule.save()
        
        due_schedules = Schedule.get_due_schedules()
        self.assertIn(due_schedule, due_schedules)
        self.assertNotIn(not_due_schedule, due_schedules)
        
    def test_get_upcoming_schedules_classmethod(self):
        """Test get_upcoming_schedules class method."""
        # Create schedule within next 24 hours
        near_future = timezone.now() + timedelta(hours=12)
        upcoming_schedule = Schedule.objects.create(
            spider=self.spider,
            cron_expr='0 * * * *',
            enabled=True
        )
        upcoming_schedule.next_run_at = near_future
        upcoming_schedule.save()
        
        # Create schedule beyond 24 hours
        far_future = timezone.now() + timedelta(hours=48)
        distant_schedule = Schedule.objects.create(
            spider=self.spider,
            cron_expr='0 0 * * *',
            enabled=True
        )
        distant_schedule.next_run_at = far_future
        distant_schedule.save()
        
        upcoming_schedules = Schedule.get_upcoming_schedules(hours=24)
        self.assertIn(upcoming_schedule, upcoming_schedules)
        self.assertNotIn(distant_schedule, upcoming_schedules)
        
    def test_cascade_delete_with_spider(self):
        """Test that schedules are deleted when spider is deleted."""
        schedule = Schedule.objects.create(
            spider=self.spider,
            cron_expr='0 * * * *',
            enabled=True
        )
        schedule_id = schedule.id
        
        self.spider.delete()
        
        with self.assertRaises(Schedule.DoesNotExist):
            Schedule.objects.get(id=schedule_id)
            
    def test_schedule_ordering(self):
        """Test that schedules are ordered by next_run_at then created_at."""
        schedule1 = Schedule.objects.create(
            spider=self.spider,
            cron_expr='0 * * * *',
            enabled=True
        )
        
        schedule2 = Schedule.objects.create(
            spider=self.spider,
            cron_expr='0 */2 * * *',
            enabled=True
        )
        
        schedules = list(Schedule.objects.all())
        # Should be ordered by next_run_at
        self.assertLessEqual(schedules[0].next_run_at, schedules[1].next_run_at)
        
    def test_cron_time_matching(self):
        """Test cron time matching logic."""
        schedule = Schedule.objects.create(
            spider=self.spider,
            cron_expr='0 9 * * 1-5',  # Weekdays at 9 AM
            enabled=True
        )
        
        # Test a Monday at 9 AM (should match)
        monday_9am = datetime(2023, 12, 4, 9, 0)  # Monday
        self.assertTrue(
            schedule._matches_cron_time(monday_9am, '0', '9', '*', '*', '1-5')
        )
        
        # Test a Saturday at 9 AM (should not match)
        saturday_9am = datetime(2023, 12, 2, 9, 0)  # Saturday
        self.assertFalse(
            schedule._matches_cron_time(saturday_9am, '0', '9', '*', '*', '1-5')
        )
        
        # Test a Monday at 10 AM (should not match)
        monday_10am = datetime(2023, 12, 4, 10, 0)  # Monday
        self.assertFalse(
            schedule._matches_cron_time(monday_10am, '0', '9', '*', '*', '1-5')
        )
        
    def test_schedule_model_indexes(self):
        """Test that proper database indexes exist."""
        indexes = Schedule._meta.indexes
        self.assertTrue(len(indexes) > 0)
        
        # Check for important indexes
        index_fields = []
        for index in indexes:
            index_fields.extend(index.fields)
            
        self.assertIn('spider', index_fields)
        self.assertIn('enabled', index_fields)
        self.assertIn('next_run_at', index_fields)