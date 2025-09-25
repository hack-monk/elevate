from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
import uuid


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

