from rest_framework import serializers
from .models import DailySummary


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
    habits = serializers.ListField()
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

