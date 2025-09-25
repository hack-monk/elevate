"""
Business logic for habit tracking
"""
from django.db.models import Q, Max
from django.utils import timezone
from datetime import date, timedelta
from .models import Habit, HabitCheck


class HabitBusinessLogic:
    """Business logic for habit tracking"""
    
    @staticmethod
    def calculate_streak(habit):
        """Calculate current streak for a habit"""
        today = timezone.now().date()
        streak = 0
        
        # Get all checks for this habit, ordered by date descending
        checks = habit.checks.filter(date__lte=today).order_by('-date')
        
        if not checks.exists():
            return 0
        
        # Check if today is completed
        if checks.first().date == today and checks.first().completed:
            streak = 1
            # Count consecutive completed days
            for check in checks[1:]:
                if check.completed:
                    streak += 1
                else:
                    break
        else:
            # Today not completed, check yesterday
            yesterday = today - timedelta(days=1)
            yesterday_check = checks.filter(date=yesterday).first()
            if yesterday_check and yesterday_check.completed:
                streak = 1
                # Count consecutive completed days before yesterday
                for check in checks[1:]:
                    if check.completed:
                        streak += 1
                    else:
                        break
        
        return streak
    
    @staticmethod
    def update_habit_streak(habit):
        """Update streak for a habit and save to daily summary"""
        streak = HabitBusinessLogic.calculate_streak(habit)
        today = timezone.now().date()
        
        # Update daily summary
        from apps.reports.models import DailySummary
        summary, created = DailySummary.objects.get_or_create(
            user=habit.user, date=today
        )
        summary.habits_streak = max(summary.habits_streak, streak)
        summary.save()
        
        return streak

