"""
Business logic for meditation tracking
"""
from django.db.models import Q, Max
from django.utils import timezone
from datetime import date, timedelta
from .models import MeditationLog


class MeditationBusinessLogic:
    """Business logic for meditation tracking"""
    
    @staticmethod
    def validate_meditation_session(user, date, start_time, duration_minutes):
        """Validate meditation session data"""
        # Check for overlapping sessions
        end_time = start_time + timedelta(minutes=duration_minutes)
        overlapping = MeditationLog.objects.filter(
            user=user,
            start_time__lt=end_time,
            date=date
        ).exclude(
            Q(start_time__gte=end_time) | Q(start_time__lte=start_time)
        )
        
        if overlapping.exists():
            raise ValueError("Meditation session overlaps with existing session")
        
        # Check reasonable duration
        if duration_minutes > 300:  # 5 hours
            raise ValueError("Meditation duration too long")
        
        return True
    
    @staticmethod
    def get_weekly_meditation_summary(user, start_date):
        """Get weekly meditation summary"""
        end_date = start_date + timedelta(days=6)
        
        logs = MeditationLog.objects.filter(
            user=user,
            date__gte=start_date,
            date__lte=end_date
        )
        
        total_minutes = sum(log.duration_minutes for log in logs)
        sessions = logs.count()
        goal_minutes = user.profile.meditation_goal_minutes * 7
        
        return {
            'total_minutes': total_minutes,
            'sessions': sessions,
            'goal_minutes': goal_minutes,
            'goal_achieved': total_minutes >= goal_minutes,
            'average_daily': total_minutes / 7
        }

