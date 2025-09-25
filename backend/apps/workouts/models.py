from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal
import uuid


class Exercise(models.Model):
    """Exercise library"""
    EXERCISE_CATEGORIES = [
        ('push', 'Push'),
        ('pull', 'Pull'),
        ('legs', 'Legs'),
        ('cardio', 'Cardio'),
        ('mobility', 'Mobility'),
        ('core', 'Core'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=EXERCISE_CATEGORIES)
    description = models.TextField(blank=True, null=True)
    is_compound = models.BooleanField(default=False)  # For PR detection
    is_custom = models.BooleanField(default=False)    # User-created vs system
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='custom_exercises')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'exercises'
        unique_together = ['name', 'created_by']  # Allow same name for different users
        indexes = [
            models.Index(fields=['category']),
            models.Index(fields=['is_custom', 'created_by']),
        ]
    
    def __str__(self):
        return self.name


class WorkoutSession(models.Model):
    """Workout session container"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='workout_sessions')
    date = models.DateField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'workout_sessions'
        indexes = [
            models.Index(fields=['user', 'date']),
            models.Index(fields=['date']),
        ]
    
    def __str__(self):
        return f"{self.user.username}: Workout - {self.date}"


class WorkoutSet(models.Model):
    """Individual exercise sets within a workout"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(WorkoutSession, on_delete=models.CASCADE, related_name='sets')
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    set_number = models.PositiveIntegerField()
    reps = models.PositiveIntegerField(blank=True, null=True)
    weight_kg = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    duration_seconds = models.PositiveIntegerField(blank=True, null=True)  # For cardio
    distance_km = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)  # For cardio
    rpe = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)], blank=True, null=True)  # Rate of Perceived Exertion
    notes = models.TextField(blank=True, null=True)
    is_pr = models.BooleanField(default=False)  # Personal record flag
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'workout_sets'
        unique_together = ['session', 'exercise', 'set_number']
        indexes = [
            models.Index(fields=['session', 'exercise']),
            models.Index(fields=['exercise', 'weight_kg']),
            models.Index(fields=['is_pr']),
        ]
    
    def __str__(self):
        return f"{self.exercise.name} - Set {self.set_number}"

