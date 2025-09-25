from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone

from .models import Habit, HabitCheck
from .serializers import HabitSerializer, HabitCheckSerializer


class HabitViewSet(viewsets.ModelViewSet):
    """Habit CRUD operations"""
    serializer_class = HabitSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Habit.objects.filter(user=self.request.user, is_active=True)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def check(self, request, pk=None):
        """POST /habits/{id}/check - Mark habit as completed for today"""
        habit = self.get_object()
        today = timezone.now().date()
        
        habit_check, created = HabitCheck.objects.get_or_create(
            habit=habit,
            date=today,
            defaults={'completed': True}
        )
        
        if not created:
            habit_check.completed = True
            habit_check.save()
        
        return Response({'message': 'Habit checked successfully'})
    
    @action(detail=True, methods=['get'])
    def streak(self, request, pk=None):
        """GET /habits/{id}/streak - Get current streak"""
        habit = self.get_object()
        # Business logic to calculate streak would go here
        return Response({'streak': 0})


class HabitCheckViewSet(viewsets.ModelViewSet):
    """Habit check operations"""
    serializer_class = HabitCheckSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return HabitCheck.objects.filter(habit__user=self.request.user)

