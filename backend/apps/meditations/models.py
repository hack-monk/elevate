from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import uuid


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

