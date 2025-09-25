from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal
import uuid


class Profile(models.Model):
    """User preferences and settings"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    timezone = models.CharField(max_length=50, default='America/New_York')
    units = models.CharField(max_length=10, choices=[('metric', 'Metric'), ('imperial', 'Imperial')], default='metric')
    
    # Macro targets (daily)
    calorie_target = models.PositiveIntegerField(default=1600)
    protein_target = models.PositiveIntegerField(default=140)  # grams
    carbs_target = models.PositiveIntegerField(default=140)    # grams
    fat_target = models.PositiveIntegerField(default=45)        # grams
    
    # Meditation goal
    meditation_goal_minutes = models.PositiveIntegerField(default=20)
    
    # Notification preferences
    habit_reminders_enabled = models.BooleanField(default=True)
    meditation_reminders_enabled = models.BooleanField(default=True)
    reminder_time = models.TimeField(default='09:00')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'profiles'
    
    def __str__(self):
        return f"{self.user.username} Profile"

