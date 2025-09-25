from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid


class Habit(models.Model):
    """User habits to track daily"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='habits')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    reminder_time = models.TimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'habits'
        unique_together = ['user', 'name']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['user', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username}: {self.name}"


class HabitCheck(models.Model):
    """Daily habit completion records"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    habit = models.ForeignKey(Habit, on_delete=models.CASCADE, related_name='checks')
    date = models.DateField()
    completed = models.BooleanField(default=False)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'habit_checks'
        unique_together = ['habit', 'date']
        indexes = [
            models.Index(fields=['habit', 'date']),
            models.Index(fields=['date', 'completed']),
        ]
    
    def __str__(self):
        return f"{self.habit.name} - {self.date} ({'✓' if self.completed else '✗'})"

