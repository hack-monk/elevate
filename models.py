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


class MeditationLog(models.Model):
    """Meditation session logs"""
    MEDITATION_STYLES = [
        ('mindfulness', 'Mindfulness'),
        ('breathing', 'Breathing'),
        ('mantra', 'Mantra'),
        ('body_scan', 'Body Scan'),
        ('loving_kindness', 'Loving Kindness'),
        ('custom', 'Custom'),
    ]
    
    MOOD_CHOICES = [
        (1, 'Very Low'),
        (2, 'Low'),
        (3, 'Neutral'),
        (4, 'Good'),
        (5, 'Very Good'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='meditation_logs')
    date = models.DateField()
    start_time = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(300)])
    style = models.CharField(max_length=20, choices=MEDITATION_STYLES)
    custom_style = models.CharField(max_length=50, blank=True, null=True)
    pre_mood = models.PositiveSmallIntegerField(choices=MOOD_CHOICES, blank=True, null=True)
    post_mood = models.PositiveSmallIntegerField(choices=MOOD_CHOICES, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'meditation_logs'
        indexes = [
            models.Index(fields=['user', 'date']),
            models.Index(fields=['date', 'duration_minutes']),
        ]
    
    def __str__(self):
        return f"{self.user.username}: {self.duration_minutes}min {self.style} - {self.date}"


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


class Food(models.Model):
    """Food database"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    brand = models.CharField(max_length=50, blank=True, null=True)
    serving_size = models.CharField(max_length=50, default='100g')
    
    # Macros per serving
    calories = models.PositiveIntegerField()
    protein_g = models.DecimalField(max_digits=6, decimal_places=2)
    carbs_g = models.DecimalField(max_digits=6, decimal_places=2)
    fat_g = models.DecimalField(max_digits=6, decimal_places=2)
    
    # Optional micros
    fiber_g = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    sugar_g = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    sodium_mg = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    
    is_custom = models.BooleanField(default=False)  # User-created vs system
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='custom_foods')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'foods'
        unique_together = ['name', 'brand', 'created_by']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['is_custom', 'created_by']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.brand})" if self.brand else self.name


class Meal(models.Model):
    """Meal container"""
    MEAL_TYPES = [
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('dinner', 'Dinner'),
        ('snack', 'Snack'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='meals')
    date = models.DateField()
    meal_type = models.CharField(max_length=20, choices=MEAL_TYPES)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'meals'
        indexes = [
            models.Index(fields=['user', 'date']),
            models.Index(fields=['date', 'meal_type']),
        ]
    
    def __str__(self):
        return f"{self.user.username}: {self.meal_type} - {self.date}"


class MealItem(models.Model):
    """Individual food items within a meal"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE, related_name='items')
    food = models.ForeignKey(Food, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=8, decimal_places=2)  # Multiplier for serving size
    
    # Override macros if custom input provided
    custom_calories = models.PositiveIntegerField(blank=True, null=True)
    custom_protein_g = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    custom_carbs_g = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    custom_fat_g = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'meal_items'
        indexes = [
            models.Index(fields=['meal']),
            models.Index(fields=['food']),
        ]
    
    def __str__(self):
        return f"{self.quantity}x {self.food.name}"


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

