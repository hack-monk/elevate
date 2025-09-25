from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta

from .models import MeditationLog
from .serializers import MeditationLogSerializer


class MeditationLogViewSet(viewsets.ModelViewSet):
    """Meditation logging"""
    serializer_class = MeditationLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return MeditationLog.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """GET /meditation/summary?period=week|month"""
        period = request.query_params.get('period', 'week')
        today = timezone.now().date()
        
        if period == 'week':
            start_date = today - timedelta(days=7)
        else:  # month
            start_date = today - timedelta(days=30)
        
        logs = self.get_queryset().filter(date__gte=start_date)
        
        total_minutes = sum(log.duration_minutes for log in logs)
        total_sessions = logs.count()
        
        return Response({
            'period': period,
            'start_date': start_date,
            'end_date': today,
            'total_minutes': total_minutes,
            'total_sessions': total_sessions,
            'average_minutes_per_session': total_minutes / total_sessions if total_sessions > 0 else 0
        })

