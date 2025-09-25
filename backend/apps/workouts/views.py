from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q

from .models import Exercise, WorkoutSession, WorkoutSet
from .serializers import ExerciseSerializer, WorkoutSessionSerializer, WorkoutSetSerializer


class ExerciseViewSet(viewsets.ModelViewSet):
    """Exercise library"""
    serializer_class = ExerciseSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Exercise.objects.filter(
            Q(is_custom=False) | Q(created_by=self.request.user)
        )
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, is_custom=True)


class WorkoutSessionViewSet(viewsets.ModelViewSet):
    """Workout session management"""
    serializer_class = WorkoutSessionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return WorkoutSession.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def add_set(self, request, pk=None):
        """POST /workouts/{id}/sets - Add a set to workout"""
        session = self.get_object()
        serializer = WorkoutSetSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(session=session)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def prs(self, request):
        """GET /workouts/prs - Get personal records"""
        prs = WorkoutSet.objects.filter(
            session__user=self.request.user,
            is_pr=True
        ).select_related('exercise', 'session')
        
        return Response(WorkoutSetSerializer(prs, many=True).data)

