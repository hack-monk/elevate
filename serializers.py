from rest_framework import serializers
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import (
    Profile, Habit, HabitCheck, MeditationLog, Exercise, 
    WorkoutSession, WorkoutSet, Food, Meal, MealItem, DailySummary
)
from decimal import Decimal


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = [
            'timezone', 'units', 'calorie_target', 'protein_target', 
            'carbs_target', 'fat_target', 'meditation_goal_minutes',
            'habit_reminders_enabled', 'meditation_reminders_enabled', 'reminder_time'
        ]
    
    def validate_calorie_target(self, value):
        if value < 100 or value > 5000:
            raise serializers.ValidationError("Calorie target must be between 100 and 5000")
        return value
    
    def validate_protein_target(self, value):
        if value < 10 or value > 500:
            raise serializers.ValidationError("Protein target must be between 10 and 500 grams")
        return value


class HabitSerializer(serializers.ModelSerializer):
    current_streak = serializers.SerializerMethodField()
    
    class Meta:
        model = Habit
        fields = [
            'id', 'name', 'description', 'reminder_time', 'is_active', 
            'created_at', 'updated_at', 'current_streak'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'current_streak']
    
    def validate_name(self, value):
        if len(value.strip()) < 2:
            raise serializers.ValidationError("Habit name must be at least 2 characters")
        return value.strip()
    
    def get_current_streak(self, obj):
        # This would be calculated in the business logic
        return obj.current_streak if hasattr(obj, 'current_streak') else 0


class HabitCheckSerializer(serializers.ModelSerializer):
    class Meta:
        model = HabitCheck
        fields = ['id', 'habit', 'date', 'completed', 'notes', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_date(self, value):
        from django.utils import timezone
        if value > timezone.now().date():
            raise serializers.ValidationError("Cannot check habits for future dates")
        return value


class MeditationLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeditationLog
        fields = [
            'id', 'date', 'start_time', 'duration_minutes', 'style', 
            'custom_style', 'pre_mood', 'post_mood', 'notes', 
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate(self, data):
        if data['style'] == 'custom' and not data.get('custom_style'):
            raise serializers.ValidationError("Custom style requires custom_style field")
        if data['style'] != 'custom' and data.get('custom_style'):
            raise serializers.ValidationError("Custom style field only valid when style is 'custom'")
        return data
    
    def validate_duration_minutes(self, value):
        if value < 1 or value > 300:
            raise serializers.ValidationError("Duration must be between 1 and 300 minutes")
        return value


class ExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exercise
        fields = ['id', 'name', 'category', 'description', 'is_compound', 'is_custom', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def validate_name(self, value):
        if len(value.strip()) < 2:
            raise serializers.ValidationError("Exercise name must be at least 2 characters")
        return value.strip()


class WorkoutSetSerializer(serializers.ModelSerializer):
    exercise_name = serializers.CharField(source='exercise.name', read_only=True)
    
    class Meta:
        model = WorkoutSet
        fields = [
            'id', 'exercise', 'exercise_name', 'set_number', 'reps', 'weight_kg',
            'duration_seconds', 'distance_km', 'rpe', 'notes', 'is_pr', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def validate(self, data):
        exercise = data.get('exercise')
        if exercise and exercise.category == 'cardio':
            if not data.get('duration_seconds') and not data.get('distance_km'):
                raise serializers.ValidationError("Cardio exercises require duration or distance")
            if data.get('reps') or data.get('weight_kg'):
                raise serializers.ValidationError("Cardio exercises should not have reps or weight")
        else:
            if not data.get('reps'):
                raise serializers.ValidationError("Non-cardio exercises require reps")
            if data.get('duration_seconds') or data.get('distance_km'):
                raise serializers.ValidationError("Non-cardio exercises should not have duration or distance")
        
        return data


class WorkoutSessionSerializer(serializers.ModelSerializer):
    sets = WorkoutSetSerializer(many=True, read_only=True)
    total_sets = serializers.SerializerMethodField()
    total_volume_kg = serializers.SerializerMethodField()
    
    class Meta:
        model = WorkoutSession
        fields = [
            'id', 'date', 'start_time', 'end_time', 'notes', 
            'sets', 'total_sets', 'total_volume_kg', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_total_sets(self, obj):
        return obj.sets.count()
    
    def get_total_volume_kg(self, obj):
        total = Decimal('0')
        for set_obj in obj.sets.all():
            if set_obj.reps and set_obj.weight_kg:
                total += set_obj.reps * set_obj.weight_kg
        return total


class FoodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Food
        fields = [
            'id', 'name', 'brand', 'serving_size', 'calories', 'protein_g',
            'carbs_g', 'fat_g', 'fiber_g', 'sugar_g', 'sodium_mg',
            'is_custom', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def validate_calories(self, value):
        if value < 0:
            raise serializers.ValidationError("Calories cannot be negative")
        return value
    
    def validate_protein_g(self, value):
        if value < 0:
            raise serializers.ValidationError("Protein cannot be negative")
        return value


class MealItemSerializer(serializers.ModelSerializer):
    food_name = serializers.CharField(source='food.name', read_only=True)
    food_brand = serializers.CharField(source='food.brand', read_only=True)
    
    class Meta:
        model = MealItem
        fields = [
            'id', 'food', 'food_name', 'food_brand', 'quantity',
            'custom_calories', 'custom_protein_g', 'custom_carbs_g', 'custom_fat_g',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than 0")
        return value


class MealSerializer(serializers.ModelSerializer):
    items = MealItemSerializer(many=True, read_only=True)
    total_calories = serializers.SerializerMethodField()
    total_protein_g = serializers.SerializerMethodField()
    total_carbs_g = serializers.SerializerMethodField()
    total_fat_g = serializers.SerializerMethodField()
    
    class Meta:
        model = Meal
        fields = [
            'id', 'date', 'meal_type', 'notes', 'items',
            'total_calories', 'total_protein_g', 'total_carbs_g', 'total_fat_g',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_total_calories(self, obj):
        total = 0
        for item in obj.items.all():
            if item.custom_calories:
                total += item.custom_calories
            else:
                total += item.quantity * item.food.calories
        return total
    
    def get_total_protein_g(self, obj):
        total = Decimal('0')
        for item in obj.items.all():
            if item.custom_protein_g:
                total += item.custom_protein_g
            else:
                total += item.quantity * item.food.protein_g
        return total
    
    def get_total_carbs_g(self, obj):
        total = Decimal('0')
        for item in obj.items.all():
            if item.custom_carbs_g:
                total += item.custom_carbs_g
            else:
                total += item.quantity * item.food.carbs_g
        return total
    
    def get_total_fat_g(self, obj):
        total = Decimal('0')
        for item in obj.items.all():
            if item.custom_fat_g:
                total += item.custom_fat_g
            else:
                total += item.quantity * item.fat_g
        return total


class DailySummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = DailySummary
        fields = [
            'id', 'date', 'habits_completed', 'habits_total', 'habits_streak',
            'meditation_minutes', 'meditation_sessions', 'workout_sessions',
            'total_volume_kg', 'prs_achieved', 'calories_consumed', 'protein_g',
            'carbs_g', 'fat_g', 'calories_remaining', 'protein_remaining_g',
            'carbs_remaining_g', 'fat_remaining_g', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class DashboardTodaySerializer(serializers.Serializer):
    """Today's dashboard data"""
    date = serializers.DateField()
    
    # Habits
    habits = HabitSerializer(many=True)
    habits_completed = serializers.IntegerField()
    habits_total = serializers.IntegerField()
    habits_streak = serializers.IntegerField()
    
    # Meditation
    meditation_minutes = serializers.IntegerField()
    meditation_sessions = serializers.IntegerField()
    meditation_goal_minutes = serializers.IntegerField()
    
    # Workouts
    workout_sessions = serializers.IntegerField()
    total_volume_kg = serializers.DecimalField(max_digits=10, decimal_places=2)
    prs_achieved = serializers.IntegerField()
    
    # Nutrition
    calories_consumed = serializers.IntegerField()
    calories_target = serializers.IntegerField()
    calories_remaining = serializers.IntegerField()
    protein_g = serializers.DecimalField(max_digits=8, decimal_places=2)
    protein_target = serializers.IntegerField()
    protein_remaining_g = serializers.DecimalField(max_digits=8, decimal_places=2)
    carbs_g = serializers.DecimalField(max_digits=8, decimal_places=2)
    carbs_target = serializers.IntegerField()
    carbs_remaining_g = serializers.DecimalField(max_digits=8, decimal_places=2)
    fat_g = serializers.DecimalField(max_digits=8, decimal_places=2)
    fat_target = serializers.IntegerField()
    fat_remaining_g = serializers.DecimalField(max_digits=8, decimal_places=2)


class WeeklySummarySerializer(serializers.Serializer):
    """Weekly summary data"""
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    
    # Habits
    total_habits_completed = serializers.IntegerField()
    average_daily_completion = serializers.FloatField()
    longest_streak = serializers.IntegerField()
    
    # Meditation
    total_meditation_minutes = serializers.IntegerField()
    average_daily_minutes = serializers.FloatField()
    sessions_completed = serializers.IntegerField()
    
    # Workouts
    total_workout_sessions = serializers.IntegerField()
    total_volume_kg = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_prs = serializers.IntegerField()
    
    # Nutrition
    average_daily_calories = serializers.FloatField()
    average_daily_protein = serializers.FloatField()
    average_daily_carbs = serializers.FloatField()
    average_daily_fat = serializers.FloatField()
