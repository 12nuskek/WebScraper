from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Count, Q
from django.utils import timezone
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter

from apps.spider.models import Spider
from .models import Schedule
from .serializers import ScheduleSerializer, ScheduleStatsSerializer, CronExpressionHelpSerializer


@extend_schema_view(
    list=extend_schema(
        tags=['Schedules'],
        summary='List schedules',
        description='Get a list of all schedules for spiders owned by the authenticated user',
        parameters=[
            OpenApiParameter('spider', description='Filter by spider ID', required=False, type=int),
            OpenApiParameter('enabled', description='Filter by enabled status', required=False, type=bool),
            OpenApiParameter('due', description='Filter by due status', required=False, type=bool),
            OpenApiParameter('timezone', description='Filter by timezone', required=False, type=str),
        ]
    ),
    create=extend_schema(
        tags=['Schedules'],
        summary='Create schedule',
        description='Create a new schedule for automated spider execution'
    ),
    retrieve=extend_schema(
        tags=['Schedules'],
        summary='Get schedule',
        description='Retrieve a specific schedule by ID'
    ),
    update=extend_schema(
        tags=['Schedules'],
        summary='Update schedule',
        description='Update a schedule (full update)'
    ),
    partial_update=extend_schema(
        tags=['Schedules'],
        summary='Partial update schedule',
        description='Partially update a schedule (e.g., enable/disable, change cron)'
    ),
    destroy=extend_schema(
        tags=['Schedules'],
        summary='Delete schedule',
        description='Delete a schedule permanently'
    ),
)
class ScheduleViewSet(viewsets.ModelViewSet):
    serializer_class = ScheduleSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        queryset = Schedule.objects.filter(spider__project__owner=self.request.user)
        
        # Filter by spider if specified
        spider_id = self.request.query_params.get('spider')
        if spider_id:
            queryset = queryset.filter(spider_id=spider_id)
            
        # Filter by enabled status if specified
        enabled = self.request.query_params.get('enabled')
        if enabled is not None:
            is_enabled = enabled.lower() in ('true', '1', 'yes')
            queryset = queryset.filter(enabled=is_enabled)
            
        # Filter by due status if specified
        due = self.request.query_params.get('due')
        if due is not None:
            is_due = due.lower() in ('true', '1', 'yes')
            current_time = timezone.now()
            if is_due:
                queryset = queryset.filter(enabled=True, next_run_at__lte=current_time)
            else:
                queryset = queryset.filter(Q(enabled=False) | Q(next_run_at__gt=current_time))
                
        # Filter by timezone if specified
        tz = self.request.query_params.get('timezone')
        if tz:
            queryset = queryset.filter(timezone=tz)
                
        return queryset.select_related('spider__project')

    def perform_create(self, serializer):
        spider_id = self.request.data.get("spider")
        spider = get_object_or_404(
            Spider, pk=spider_id, project__owner=self.request.user
        )
        serializer.save(spider=spider)
        
    @extend_schema(
        tags=['Schedules'],
        summary='Get due schedules',
        description='Get all schedules that are currently due for execution (worker endpoint)',
        responses={200: ScheduleSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def due(self, request):
        """Get all schedules that are due for execution."""
        queryset = self.get_queryset().filter(
            enabled=True,
            next_run_at__lte=timezone.now()
        ).order_by('next_run_at')
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
        
    @extend_schema(
        tags=['Schedules'],
        summary='Get upcoming schedules',
        description='Get schedules due within the next N hours',
        parameters=[
            OpenApiParameter('hours', description='Hours to look ahead (default: 24)', required=False, type=int),
        ],
        responses={200: ScheduleSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Get schedules due within the next N hours."""
        hours = int(request.query_params.get('hours', 24))
        
        current_time = timezone.now()
        future_time = current_time + timezone.timedelta(hours=hours)
        
        queryset = self.get_queryset().filter(
            enabled=True,
            next_run_at__gte=current_time,
            next_run_at__lte=future_time
        ).order_by('next_run_at')
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
        
    @extend_schema(
        tags=['Schedules'],
        summary='Mark schedule executed',
        description='Mark a schedule as executed and calculate next run time',
        responses={200: ScheduleSerializer}
    )
    @action(detail=True, methods=['post'])
    def mark_executed(self, request, pk=None):
        """Mark schedule as executed and update next run time."""
        schedule = self.get_object()
        
        if not schedule.enabled:
            return Response(
                {'error': 'Cannot execute disabled schedule'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        schedule.mark_executed()
        serializer = self.get_serializer(schedule)
        return Response(serializer.data)
        
    @extend_schema(
        tags=['Schedules'],
        summary='Enable schedule',
        description='Enable a disabled schedule and calculate next run time',
        responses={200: ScheduleSerializer}
    )
    @action(detail=True, methods=['post'])
    def enable(self, request, pk=None):
        """Enable a schedule."""
        schedule = self.get_object()
        
        if schedule.enabled:
            return Response(
                {'message': 'Schedule is already enabled'}, 
                status=status.HTTP_200_OK
            )
            
        schedule.enabled = True
        schedule.calculate_next_run()
        schedule.save()
        
        serializer = self.get_serializer(schedule)
        return Response(serializer.data)
        
    @extend_schema(
        tags=['Schedules'],
        summary='Disable schedule',
        description='Disable a schedule and clear next run time',
        responses={200: ScheduleSerializer}
    )
    @action(detail=True, methods=['post'])
    def disable(self, request, pk=None):
        """Disable a schedule."""
        schedule = self.get_object()
        
        if not schedule.enabled:
            return Response(
                {'message': 'Schedule is already disabled'}, 
                status=status.HTTP_200_OK
            )
            
        schedule.enabled = False
        schedule.next_run_at = None
        schedule.save()
        
        serializer = self.get_serializer(schedule)
        return Response(serializer.data)
        
    @extend_schema(
        tags=['Schedules'],
        summary='Recalculate next run',
        description='Manually recalculate the next run time for a schedule',
        responses={200: ScheduleSerializer}
    )
    @action(detail=True, methods=['post'])
    def recalculate(self, request, pk=None):
        """Recalculate next run time for a schedule."""
        schedule = self.get_object()
        
        if schedule.enabled:
            schedule.calculate_next_run()
            schedule.save()
            
        serializer = self.get_serializer(schedule)
        return Response(serializer.data)
        
    @extend_schema(
        tags=['Schedules'],
        summary='Get schedule statistics',
        description='Get statistics about schedules for the authenticated user',
        parameters=[
            OpenApiParameter('spider', description='Filter by specific spider ID', required=False, type=int),
        ],
        responses={200: ScheduleStatsSerializer}
    )
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get schedule statistics."""
        queryset = self.get_queryset()
        
        # Additional filtering for stats
        spider_id = request.query_params.get('spider')
        if spider_id:
            queryset = queryset.filter(spider_id=spider_id)
            
        current_time = timezone.now()
        
        # Calculate statistics
        total_schedules = queryset.count()
        enabled_schedules = queryset.filter(enabled=True).count()
        disabled_schedules = total_schedules - enabled_schedules
        
        due_schedules = queryset.filter(
            enabled=True,
            next_run_at__lte=current_time
        ).count()
        
        overdue_schedules = queryset.filter(
            enabled=True,
            next_run_at__lt=current_time - timezone.timedelta(hours=1)
        ).count()
        
        upcoming_24h = queryset.filter(
            enabled=True,
            next_run_at__gte=current_time,
            next_run_at__lte=current_time + timezone.timedelta(hours=24)
        ).count()
        
        # Timezone distribution
        timezone_distribution = dict(
            queryset.values('timezone').annotate(count=Count('timezone')).values_list('timezone', 'count')
        )
        
        return Response({
            'total_schedules': total_schedules,
            'enabled_schedules': enabled_schedules,
            'disabled_schedules': disabled_schedules,
            'due_schedules': due_schedules,
            'overdue_schedules': overdue_schedules,
            'upcoming_24h': upcoming_24h,
            'timezone_distribution': timezone_distribution,
        })
        
    @extend_schema(
        tags=['Schedules'],
        summary='Get cron expression help',
        description='Get help and examples for cron expressions',
        responses={200: CronExpressionHelpSerializer}
    )
    @action(detail=False, methods=['get'], permission_classes=[])
    def cron_help(self, request):
        """Get cron expression help and examples."""
        help_data = {
            'examples': {
                'Every minute': '* * * * *',
                'Every hour': '0 * * * *',
                'Every 6 hours': '0 */6 * * *',
                'Every day at midnight': '0 0 * * *',
                'Every day at 9 AM': '0 9 * * *',
                'Every Monday at 9 AM': '0 9 * * 1',
                'Every weekday at 9 AM': '0 9 * * 1-5',
                'Every month on 1st at midnight': '0 0 1 * *',
                'Every Sunday at 6 PM': '0 18 * * 0',
                'Every 15 minutes': '*/15 * * * *',
                'Every 2 hours during business hours': '0 9-17/2 * * 1-5',
            },
            'fields': {
                'minute': '0-59',
                'hour': '0-23', 
                'day': '1-31',
                'month': '1-12',
                'weekday': '0-7 (0 and 7 are Sunday)',
            },
            'special_characters': {
                '*': 'Matches any value',
                '*/n': 'Every nth value (e.g., */5 = every 5 minutes)',
                'n-m': 'Range of values (e.g., 1-5 = Monday to Friday)',
                'n,m,o': 'List of values (e.g., 1,3,5 = Monday, Wednesday, Friday)',
            },
            'common_patterns': {
                'Hourly': '0 * * * *',
                'Daily': '0 0 * * *',
                'Weekly': '0 0 * * 0',
                'Monthly': '0 0 1 * *',
                'Business hours': '0 9-17 * * 1-5',
                'Off hours': '0 18-8 * * *',
            }
        }
        
        return Response(help_data)