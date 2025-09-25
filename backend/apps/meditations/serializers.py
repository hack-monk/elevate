from rest_framework import serializers
from .models import MeditationLog


class MeditationLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeditationLog
        fields = [
            'id', 'date', 'start_time', 'duration_minutes', 'style', 
            'custom_style', 'pre_mood', 'post_mood', 'notes', 
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate(self, data):
        if data['style'] == 'custom' and not data.get('custom_style'):
            raise serializers.ValidationError("Custom style requires custom_style field")
        if data['style'] != 'custom' and data.get('custom_style'):
            raise serializers.ValidationError("Custom style field only valid when style is 'custom'")
        return data
    
    def validate_duration_minutes(self, value):
        if value < 1 or value > 300:
            raise serializers.ValidationError("Duration must be between 1 and 300 minutes")
        return value

