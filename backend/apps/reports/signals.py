"""
Django signals for automatic daily summary updates
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone

from apps.habits.models import HabitCheck
from apps.meditations.models import MeditationLog
from apps.workouts.models import WorkoutSession, WorkoutSet
from apps.nutrition.models import Meal, MealItem
from apps.reports.business_logic import DailySummaryBusinessLogic


@receiver(post_save, sender=HabitCheck)
@receiver(post_delete, sender=HabitCheck)
def update_summary_on_habit_check(sender, instance, **kwargs):
    """Update daily summary when habit check is created/updated/deleted"""
    DailySummaryBusinessLogic.recalculate_daily_summary(
        instance.habit.user, 
        instance.date
    )


@receiver(post_save, sender=MeditationLog)
@receiver(post_delete, sender=MeditationLog)
def update_summary_on_meditation_log(sender, instance, **kwargs):
    """Update daily summary when meditation log is created/updated/deleted"""
    DailySummaryBusinessLogic.recalculate_daily_summary(
        instance.user, 
        instance.date
    )


@receiver(post_save, sender=WorkoutSession)
@receiver(post_delete, sender=WorkoutSession)
def update_summary_on_workout_session(sender, instance, **kwargs):
    """Update daily summary when workout session is created/updated/deleted"""
    DailySummaryBusinessLogic.recalculate_daily_summary(
        instance.user, 
        instance.date
    )


@receiver(post_save, sender=WorkoutSet)
@receiver(post_delete, sender=WorkoutSet)
def update_summary_on_workout_set(sender, instance, **kwargs):
    """Update daily summary when workout set is created/updated/deleted"""
    DailySummaryBusinessLogic.recalculate_daily_summary(
        instance.session.user, 
        instance.session.date
    )


@receiver(post_save, sender=Meal)
@receiver(post_delete, sender=Meal)
def update_summary_on_meal(sender, instance, **kwargs):
    """Update daily summary when meal is created/updated/deleted"""
    DailySummaryBusinessLogic.recalculate_daily_summary(
        instance.user, 
        instance.date
    )


@receiver(post_save, sender=MealItem)
@receiver(post_delete, sender=MealItem)
def update_summary_on_meal_item(sender, instance, **kwargs):
    """Update daily summary when meal item is created/updated/deleted"""
    DailySummaryBusinessLogic.recalculate_daily_summary(
        instance.meal.user, 
        instance.meal.date
    )

