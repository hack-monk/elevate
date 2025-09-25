"""
Business logic for nutrition tracking
"""
from django.db.models import Q, Max
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal
from .models import Food, Meal, MealItem


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
        from apps.reports.models import DailySummary
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

