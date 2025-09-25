"""
Business logic for daily summaries and reports
"""
from django.db.models import Q, Max, Sum, Avg
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal
from .models import DailySummary


class DailySummaryBusinessLogic:
    """Business logic for daily summaries"""
    
    @staticmethod
    def recalculate_daily_summary(user, date):
        """Recalculate all daily summary data for a user and date"""
        # Get or create summary
        summary, created = DailySummary.objects.get_or_create(
            user=user, date=date
        )
        
        # Habits
        from apps.habits.models import Habit, HabitCheck
        habits = Habit.objects.filter(user=user, is_active=True)
        habit_checks = HabitCheck.objects.filter(
            habit__in=habits, date=date
        )
        summary.habits_completed = habit_checks.filter(completed=True).count()
        summary.habits_total = habits.count()
        
        # Calculate streak for first habit (simplified)
        if habits.exists():
            from apps.habits.business_logic import HabitBusinessLogic
            summary.habits_streak = HabitBusinessLogic.calculate_streak(habits.first())
        
        # Meditation
        from apps.meditations.models import MeditationLog
        meditation_logs = MeditationLog.objects.filter(user=user, date=date)
        summary.meditation_minutes = sum(log.duration_minutes for log in meditation_logs)
        summary.meditation_sessions = meditation_logs.count()
        
        # Workouts
        from apps.workouts.models import WorkoutSession, WorkoutSet
        from apps.workouts.business_logic import WorkoutBusinessLogic
        workouts = WorkoutSession.objects.filter(user=user, date=date)
        summary.workout_sessions = workouts.count()
        summary.total_volume_kg = sum(
            WorkoutBusinessLogic.get_workout_volume(session) for session in workouts
        )
        summary.prs_achieved = WorkoutSet.objects.filter(
            session__in=workouts, is_pr=True
        ).count()
        
        # Nutrition
        from apps.nutrition.business_logic import NutritionBusinessLogic
        nutrition_summary = NutritionBusinessLogic.update_daily_nutrition_summary(user, date)
        summary.calories_consumed = nutrition_summary.calories_consumed
        summary.protein_g = nutrition_summary.protein_g
        summary.carbs_g = nutrition_summary.carbs_g
        summary.fat_g = nutrition_summary.fat_g
        summary.calories_remaining = nutrition_summary.calories_remaining
        summary.protein_remaining_g = nutrition_summary.protein_remaining_g
        summary.carbs_remaining_g = nutrition_summary.carbs_remaining_g
        summary.fat_remaining_g = nutrition_summary.fat_remaining_g
        
        summary.save()
        return summary
    
    @staticmethod
    def nightly_rollup():
        """Nightly job to recalculate all summaries"""
        from celery import shared_task
        
        @shared_task
        def run_nightly_rollup():
            """Celery task for nightly rollup"""
            from django.contrib.auth.models import User
            import logging
            
            logger = logging.getLogger(__name__)
            today = timezone.now().date()
            users = User.objects.all()
            
            for user in users:
                try:
                    DailySummaryBusinessLogic.recalculate_daily_summary(user, today)
                    logger.info(f"Updated daily summary for user {user.username} on {today}")
                except Exception as e:
                    logger.error(f"Error updating daily summary for user {user.username}: {e}")
        
        return run_nightly_rollup

