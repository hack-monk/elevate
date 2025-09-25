from rest_framework import serializers
from .models import Habit, HabitCheck


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

