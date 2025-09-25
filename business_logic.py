"""
Business logic and edge cases for the Habit + Meditation + Workout + Nutrition app
"""
from django.db.models import Q, Max
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


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
        summary, created = DailySummary.objects.get_or_create(
            user=habit.user, date=today
        )
        summary.habits_streak = max(summary.habits_streak, streak)
        summary.save()
        
        return streak


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


class WorkoutBusinessLogic:
    """Business logic for workout tracking"""
    
    @staticmethod
    def detect_pr(user, exercise, weight_kg, reps):
        """Detect if this is a personal record"""
        if not weight_kg or not reps:
            return False
        
        # Get previous best for this exercise
        previous_best = WorkoutSet.objects.filter(
            session__user=user,
            exercise=exercise,
            weight_kg__isnull=False,
            reps__isnull=False
        ).exclude(
            weight_kg=0
        ).aggregate(
            max_weight=Max('weight_kg')
        )['max_weight']
        
        if not previous_best:
            return True  # First time doing this exercise
        
        # Check if this is heavier
        if weight_kg > previous_best:
            return True
        
        # Check if same weight but more reps
        if weight_kg == previous_best:
            previous_best_reps = WorkoutSet.objects.filter(
                session__user=user,
                exercise=exercise,
                weight_kg=weight_kg
            ).aggregate(
                max_reps=Max('reps')
            )['max_reps']
            
            if reps > previous_best_reps:
                return True
        
        return False
    
    @staticmethod
    def calculate_1rm(weight_kg, reps):
        """Calculate 1RM using Epley formula"""
        if not weight_kg or not reps or reps == 0:
            return None
        
        # Epley formula: 1RM = weight * (1 + reps/30)
        one_rm = weight_kg * (1 + reps / 30)
        return round(one_rm, 2)
    
    @staticmethod
    def update_workout_prs(session):
        """Update PR flags for all sets in a workout session"""
        for set_obj in session.sets.all():
            if set_obj.weight_kg and set_obj.reps:
                is_pr = WorkoutBusinessLogic.detect_pr(
                    session.user, 
                    set_obj.exercise, 
                    set_obj.weight_kg, 
                    set_obj.reps
                )
                if is_pr != set_obj.is_pr:
                    set_obj.is_pr = is_pr
                    set_obj.save()
    
    @staticmethod
    def get_workout_volume(session):
        """Calculate total volume for a workout session"""
        total_volume = Decimal('0')
        for set_obj in session.sets.all():
            if set_obj.weight_kg and set_obj.reps:
                total_volume += set_obj.weight_kg * set_obj.reps
        return total_volume


class NutritionBusinessLogic:
    """Business logic for nutrition tracking"""
    
    @staticmethod
    def calculate_meal_macros(meal):
        """Calculate total macros for a meal"""
        total_calories = 0
        total_protein = Decimal('0')
        total_carbs = Decimal('0')
        total_fat = Decimal('0')
        
        for item in meal.items.all():
            # Use custom values if provided, otherwise calculate from food
            if item.custom_calories:
                total_calories += item.custom_calories
            else:
                total_calories += int(item.quantity * item.food.calories)
            
            if item.custom_protein_g:
                total_protein += item.custom_protein_g
            else:
                total_protein += item.quantity * item.food.protein_g
            
            if item.custom_carbs_g:
                total_carbs += item.custom_carbs_g
            else:
                total_carbs += item.quantity * item.food.carbs_g
            
            if item.custom_fat_g:
                total_fat += item.custom_fat_g
            else:
                total_fat += item.quantity * item.food.fat_g
        
        return {
            'calories': total_calories,
            'protein_g': total_protein,
            'carbs_g': total_carbs,
            'fat_g': total_fat
        }
    
    @staticmethod
    def update_daily_nutrition_summary(user, date):
        """Update daily nutrition summary"""
        meals = Meal.objects.filter(user=user, date=date)
        
        total_calories = 0
        total_protein = Decimal('0')
        total_carbs = Decimal('0')
        total_fat = Decimal('0')
        
        for meal in meals:
            macros = NutritionBusinessLogic.calculate_meal_macros(meal)
            total_calories += macros['calories']
            total_protein += macros['protein_g']
            total_carbs += macros['carbs_g']
            total_fat += macros['fat_g']
        
        # Get user's targets
        profile = user.profile
        calorie_target = profile.calorie_target
        protein_target = profile.protein_target
        carbs_target = profile.carbs_target
        fat_target = profile.fat_target
        
        # Calculate remaining
        calories_remaining = calorie_target - total_calories
        protein_remaining = protein_target - float(total_protein)
        carbs_remaining = carbs_target - float(total_carbs)
        fat_remaining = fat_target - float(total_fat)
        
        # Update or create daily summary
        summary, created = DailySummary.objects.get_or_create(
            user=user, date=date
        )
        
        summary.calories_consumed = total_calories
        summary.protein_g = total_protein
        summary.carbs_g = total_carbs
        summary.fat_g = total_fat
        summary.calories_remaining = calories_remaining
        summary.protein_remaining_g = protein_remaining
        summary.carbs_remaining_g = carbs_remaining
        summary.fat_remaining_g = fat_remaining
        summary.save()
        
        return summary


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
        habits = Habit.objects.filter(user=user, is_active=True)
        habit_checks = HabitCheck.objects.filter(
            habit__in=habits, date=date
        )
        summary.habits_completed = habit_checks.filter(completed=True).count()
        summary.habits_total = habits.count()
        summary.habits_streak = HabitBusinessLogic.calculate_streak(
            habits.first() if habits.exists() else None
        )
        
        # Meditation
        meditation_logs = MeditationLog.objects.filter(user=user, date=date)
        summary.meditation_minutes = sum(log.duration_minutes for log in meditation_logs)
        summary.meditation_sessions = meditation_logs.count()
        
        # Workouts
        workouts = WorkoutSession.objects.filter(user=user, date=date)
        summary.workout_sessions = workouts.count()
        summary.total_volume_kg = sum(
            WorkoutBusinessLogic.get_workout_volume(session) for session in workouts
        )
        summary.prs_achieved = WorkoutSet.objects.filter(
            session__in=workouts, is_pr=True
        ).count()
        
        # Nutrition
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
            today = timezone.now().date()
            users = User.objects.all()
            
            for user in users:
                try:
                    DailySummaryBusinessLogic.recalculate_daily_summary(user, today)
                    logger.info(f"Updated daily summary for user {user.username} on {today}")
                except Exception as e:
                    logger.error(f"Error updating daily summary for user {user.username}: {e}")
        
        return run_nightly_rollup


class ValidationBusinessLogic:
    """General validation business logic"""
    
    @staticmethod
    def validate_date_not_future(date_value):
        """Validate that date is not in the future"""
        today = timezone.now().date()
        if date_value > today:
            raise ValueError("Cannot log data for future dates")
        return True
    
    @staticmethod
    def validate_positive_number(value, field_name):
        """Validate that a number is positive"""
        if value is not None and value < 0:
            raise ValueError(f"{field_name} cannot be negative")
        return True
    
    @staticmethod
    def validate_reasonable_duration(minutes, max_minutes=300):
        """Validate reasonable duration for activities"""
        if minutes < 1:
            raise ValueError("Duration must be at least 1 minute")
        if minutes > max_minutes:
            raise ValueError(f"Duration cannot exceed {max_minutes} minutes")
        return True

