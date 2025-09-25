from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
import uuid


class DailySummary(models.Model):
    """Denormalized daily rollup for performance"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='daily_summaries')
    date = models.DateField()
    
    # Habits
    habits_completed = models.PositiveIntegerField(default=0)
    habits_total = models.PositiveIntegerField(default=0)
    habits_streak = models.PositiveIntegerField(default=0)
    
    # Meditation
    meditation_minutes = models.PositiveIntegerField(default=0)
    meditation_sessions = models.PositiveIntegerField(default=0)
    
    # Workouts
    workout_sessions = models.PositiveIntegerField(default=0)
    total_volume_kg = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    prs_achieved = models.PositiveIntegerField(default=0)
    
    # Nutrition
    calories_consumed = models.PositiveIntegerField(default=0)
    protein_g = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    carbs_g = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    fat_g = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    
    # Computed fields
    calories_remaining = models.IntegerField(default=0)
    protein_remaining_g = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    carbs_remaining_g = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    fat_remaining_g = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'daily_summaries'
        unique_together = ['user', 'date']
        indexes = [
            models.Index(fields=['user', 'date']),
            models.Index(fields=['date']),
        ]
    
    def __str__(self):
        return f"{self.user.username}: {self.date} Summary"

