from rest_framework import serializers
from .models import Exercise, WorkoutSession, WorkoutSet


class ExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exercise
        fields = ['id', 'name', 'category', 'description', 'is_compound', 'is_custom', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def validate_name(self, value):
        if len(value.strip()) < 2:
            raise serializers.ValidationError("Exercise name must be at least 2 characters")
        return value.strip()


class WorkoutSetSerializer(serializers.ModelSerializer):
    exercise_name = serializers.CharField(source='exercise.name', read_only=True)
    
    class Meta:
        model = WorkoutSet
        fields = [
            'id', 'exercise', 'exercise_name', 'set_number', 'reps', 'weight_kg',
            'duration_seconds', 'distance_km', 'rpe', 'notes', 'is_pr', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def validate(self, data):
        exercise = data.get('exercise')
        if exercise and exercise.category == 'cardio':
            if not data.get('duration_seconds') and not data.get('distance_km'):
                raise serializers.ValidationError("Cardio exercises require duration or distance")
            if data.get('reps') or data.get('weight_kg'):
                raise serializers.ValidationError("Cardio exercises should not have reps or weight")
        else:
            if not data.get('reps'):
                raise serializers.ValidationError("Non-cardio exercises require reps")
            if data.get('duration_seconds') or data.get('distance_km'):
                raise serializers.ValidationError("Non-cardio exercises should not have duration or distance")
        
        return data


class WorkoutSessionSerializer(serializers.ModelSerializer):
    sets = WorkoutSetSerializer(many=True, read_only=True)
    total_sets = serializers.SerializerMethodField()
    total_volume_kg = serializers.SerializerMethodField()
    
    class Meta:
        model = WorkoutSession
        fields = [
            'id', 'date', 'start_time', 'end_time', 'notes', 
            'sets', 'total_sets', 'total_volume_kg', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_total_sets(self, obj):
        return obj.sets.count()
    
    def get_total_volume_kg(self, obj):
        from decimal import Decimal
        total = Decimal('0')
        for set_obj in obj.sets.all():
            if set_obj.reps and set_obj.weight_kg:
                total += set_obj.reps * set_obj.weight_kg
        return total

