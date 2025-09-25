"""
Business logic for workout tracking
"""
from django.db.models import Q, Max
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal
from .models import Exercise, WorkoutSession, WorkoutSet


class WorkoutBusinessLogic:
    """Business logic for workout tracking"""
    
    @staticmethod
    def detect_pr(user, exercise, weight_kg, reps):
        """Detect if this is a personal record"""
        if not weight_kg or not reps:
            return False
        
        # Get previous best for this exercise
        previous_best = WorkoutSet.objects.filter(
            session__user=user,
            exercise=exercise,
            weight_kg__isnull=False,
            reps__isnull=False
        ).exclude(
            weight_kg=0
        ).aggregate(
            max_weight=Max('weight_kg')
        )['max_weight']
        
        if not previous_best:
            return True  # First time doing this exercise
        
        # Check if this is heavier
        if weight_kg > previous_best:
            return True
        
        # Check if same weight but more reps
        if weight_kg == previous_best:
            previous_best_reps = WorkoutSet.objects.filter(
                session__user=user,
                exercise=exercise,
                weight_kg=weight_kg
            ).aggregate(
                max_reps=Max('reps')
            )['max_reps']
            
            if reps > previous_best_reps:
                return True
        
        return False
    
    @staticmethod
    def calculate_1rm(weight_kg, reps):
        """Calculate 1RM using Epley formula"""
        if not weight_kg or not reps or reps == 0:
            return None
        
        # Epley formula: 1RM = weight * (1 + reps/30)
        one_rm = weight_kg * (1 + reps / 30)
        return round(one_rm, 2)
    
    @staticmethod
    def update_workout_prs(session):
        """Update PR flags for all sets in a workout session"""
        for set_obj in session.sets.all():
            if set_obj.weight_kg and set_obj.reps:
                is_pr = WorkoutBusinessLogic.detect_pr(
                    session.user, 
                    set_obj.exercise, 
                    set_obj.weight_kg, 
                    set_obj.reps
                )
                if is_pr != set_obj.is_pr:
                    set_obj.is_pr = is_pr
                    set_obj.save()
    
    @staticmethod
    def get_workout_volume(session):
        """Calculate total volume for a workout session"""
        total_volume = Decimal('0')
        for set_obj in session.sets.all():
            if set_obj.weight_kg and set_obj.reps:
                total_volume += set_obj.weight_kg * set_obj.reps
        return total_volume

