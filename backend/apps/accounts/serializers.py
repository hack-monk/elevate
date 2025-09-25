from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile


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

