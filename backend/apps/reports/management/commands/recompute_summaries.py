"""
Management command to recompute daily summaries
"""
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from datetime import datetime, date, timedelta
from apps.reports.tasks import rollup_date_range, rollup_all_users_date_range


class Command(BaseCommand):
    help = 'Recompute daily summaries for a date range'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--start',
            type=str,
            required=True,
            help='Start date in YYYY-MM-DD format'
        )
        parser.add_argument(
            '--end',
            type=str,
            required=True,
            help='End date in YYYY-MM-DD format'
        )
        parser.add_argument(
            '--user-id',
            type=int,
            help='Specific user ID to recompute (optional, recomputes all users if not provided)'
        )
        parser.add_argument(
            '--async',
            action='store_true',
            help='Run asynchronously using Celery (default: synchronous)'
        )
    
    def handle(self, *args, **options):
        start_date_str = options['start']
        end_date_str = options['end']
        user_id = options.get('user_id')
        async_mode = options.get('async', False)
        
        # Parse dates
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            raise CommandError('Invalid date format. Use YYYY-MM-DD')
        
        if start_date > end_date:
            raise CommandError('Start date must be before or equal to end date')
        
        self.stdout.write(f'Recomputing summaries from {start_date} to {end_date}')
        
        if user_id:
            # Recompute for specific user
            try:
                user = User.objects.get(id=user_id)
                self.stdout.write(f'Recomputing for user: {user.username}')
                
                if async_mode:
                    # Run asynchronously
                    task = rollup_date_range.delay(user_id, start_date, end_date)
                    self.stdout.write(f'Task queued with ID: {task.id}')
                else:
                    # Run synchronously
                    from apps.reports.business_logic import DailySummaryBusinessLogic
                    current_date = start_date
                    while current_date <= end_date:
                        DailySummaryBusinessLogic.recalculate_daily_summary(user, current_date)
                        current_date += timedelta(days=1)
                    self.stdout.write(f'Successfully recomputed summaries for {user.username}')
                    
            except User.DoesNotExist:
                raise CommandError(f'User with ID {user_id} not found')
        else:
            # Recompute for all users
            users = User.objects.all()
            self.stdout.write(f'Recomputing for {users.count()} users')
            
            if async_mode:
                # Run asynchronously
                task = rollup_all_users_date_range.delay(start_date, end_date)
                self.stdout.write(f'Task queued with ID: {task.id}')
            else:
                # Run synchronously
                from apps.reports.business_logic import DailySummaryBusinessLogic
                for user in users:
                    self.stdout.write(f'Processing user: {user.username}')
                    current_date = start_date
                    while current_date <= end_date:
                        DailySummaryBusinessLogic.recalculate_daily_summary(user, current_date)
                        current_date += timedelta(days=1)
                
                self.stdout.write('Successfully recomputed summaries for all users')
        
        self.stdout.write(
            self.style.SUCCESS('Summary recomputation completed')
        )
