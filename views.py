from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db.models import Q, Sum, Count, Max, Avg
from django.utils import timezone
from datetime import datetime, timedelta, date
from decimal import Decimal
import jwt
from django.conf import settings

from .models import (
    Profile, Habit, HabitCheck, MeditationLog, Exercise, 
    WorkoutSession, WorkoutSet, Food, Meal, MealItem, DailySummary
)
from .serializers import (
    UserSerializer, ProfileSerializer, HabitSerializer, HabitCheckSerializer,
    MeditationLogSerializer, ExerciseSerializer, WorkoutSessionSerializer,
    WorkoutSetSerializer, FoodSerializer, MealSerializer, MealItemSerializer,
    DailySummarySerializer, DashboardTodaySerializer, WeeklySummarySerializer
)


class AuthViewSet(viewsets.ViewSet):
    """Authentication endpoints"""
    
    @action(detail=False, methods=['post'])
    def register(self, request):
        """POST /auth/register"""
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')
        
        if User.objects.filter(username=username).exists():
            return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)
        
        if User.objects.filter(email=email).exists():
            return Response({'error': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = User.objects.create_user(username=username, email=email, password=password)
        Profile.objects.create(user=user)
        
        return Response({'message': 'User created successfully'}, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['post'])
    def login(self, request):
        """POST /auth/login"""
        username = request.data.get('username')
        password = request.data.get('password')
        
        user = authenticate(username=username, password=password)
        if not user:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        
        # Generate JWT tokens
        access_token = self._generate_access_token(user)
        refresh_token = self._generate_refresh_token(user)
        
        response = Response({
            'access_token': access_token,
            'user': UserSerializer(user).data
        })
        
        # Set refresh token in HTTP-only cookie
        response.set_cookie(
            'refresh_token', 
            refresh_token, 
            httponly=True, 
            secure=True, 
            samesite='Strict',
            max_age=7*24*60*60  # 7 days
        )
        
        return response
    
    @action(detail=False, methods=['post'])
    def refresh(self, request):
        """POST /auth/refresh"""
        refresh_token = request.COOKIES.get('refresh_token')
        if not refresh_token:
            return Response({'error': 'No refresh token'}, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=['HS256'])
            user = User.objects.get(id=payload['user_id'])
            access_token = self._generate_access_token(user)
            return Response({'access_token': access_token})
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, User.DoesNotExist):
            return Response({'error': 'Invalid refresh token'}, status=status.HTTP_401_UNAUTHORIZED)
    
    @action(detail=False, methods=['post'])
    def logout(self, request):
        """POST /auth/logout"""
        response = Response({'message': 'Logged out successfully'})
        response.delete_cookie('refresh_token')
        return response
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        """GET /auth/me"""
        return Response({
            'user': UserSerializer(request.user).data,
            'profile': ProfileSerializer(request.user.profile).data
        })
    
    def _generate_access_token(self, user):
        payload = {
            'user_id': user.id,
            'username': user.username,
            'exp': datetime.utcnow() + timedelta(hours=1)
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    
    def _generate_refresh_token(self, user):
        payload = {
            'user_id': user.id,
            'exp': datetime.utcnow() + timedelta(days=7)
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')


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


class FoodViewSet(viewsets.ModelViewSet):
    """Food database"""
    serializer_class = FoodSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Food.objects.filter(
            Q(is_custom=False) | Q(created_by=self.request.user)
        )
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, is_custom=True)
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """GET /foods/search?q=query - Search foods"""
        query = request.query_params.get('q', '')
        foods = self.get_queryset().filter(
            Q(name__icontains=query) | Q(brand__icontains=query)
        )[:20]
        return Response(FoodSerializer(foods, many=True).data)


class MealViewSet(viewsets.ModelViewSet):
    """Meal management"""
    serializer_class = MealSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Meal.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def add_item(self, request, pk=None):
        """POST /meals/{id}/items - Add food item to meal"""
        meal = self.get_object()
        serializer = MealItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(meal=meal)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DashboardView(APIView):
    """Today's dashboard data"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """GET /dashboard/today"""
        today = timezone.now().date()
        user = request.user
        
        # Get or create daily summary
        summary, created = DailySummary.objects.get_or_create(
            user=user, date=today
        )
        
        # Get habits for today
        habits = Habit.objects.filter(user=user, is_active=True)
        habit_checks = HabitCheck.objects.filter(
            habit__in=habits, date=today
        )
        
        # Get today's meditation
        meditation_logs = MeditationLog.objects.filter(user=user, date=today)
        
        # Get today's workouts
        workouts = WorkoutSession.objects.filter(user=user, date=today)
        
        # Get today's meals
        meals = Meal.objects.filter(user=user, date=today)
        
        dashboard_data = {
            'date': today,
            'habits': HabitSerializer(habits, many=True).data,
            'habits_completed': habit_checks.filter(completed=True).count(),
            'habits_total': habits.count(),
            'habits_streak': summary.habits_streak,
            'meditation_minutes': sum(log.duration_minutes for log in meditation_logs),
            'meditation_sessions': meditation_logs.count(),
            'meditation_goal_minutes': user.profile.meditation_goal_minutes,
            'workout_sessions': workouts.count(),
            'total_volume_kg': sum(
                sum(set_obj.reps * set_obj.weight_kg for set_obj in session.sets.all() 
                    if set_obj.reps and set_obj.weight_kg) 
                for session in workouts
            ),
            'prs_achieved': WorkoutSet.objects.filter(
                session__in=workouts, is_pr=True
            ).count(),
            'calories_consumed': summary.calories_consumed,
            'calories_target': user.profile.calorie_target,
            'calories_remaining': summary.calories_remaining,
            'protein_g': float(summary.protein_g),
            'protein_target': user.profile.protein_target,
            'protein_remaining_g': float(summary.protein_remaining_g),
            'carbs_g': float(summary.carbs_g),
            'carbs_target': user.profile.carbs_target,
            'carbs_remaining_g': float(summary.carbs_remaining_g),
            'fat_g': float(summary.fat_g),
            'fat_target': user.profile.fat_target,
            'fat_remaining_g': float(summary.fat_remaining_g),
        }
        
        return Response(dashboard_data)


class SummaryView(APIView):
    """Weekly/monthly summaries"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """GET /summary?start=YYYY-MM-DD&end=YYYY-MM-DD"""
        start_date = request.query_params.get('start')
        end_date = request.query_params.get('end')
        
        if not start_date or not end_date:
            return Response({'error': 'start and end dates required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            return Response({'error': 'Invalid date format'}, status=status.HTTP_400_BAD_REQUEST)
        
        summaries = DailySummary.objects.filter(
            user=request.user,
            date__gte=start_date,
            date__lte=end_date
        )
        
        # Calculate aggregates
        total_habits_completed = summaries.aggregate(Sum('habits_completed'))['habits_completed__sum'] or 0
        total_meditation_minutes = summaries.aggregate(Sum('meditation_minutes'))['meditation_minutes__sum'] or 0
        total_workout_sessions = summaries.aggregate(Sum('workout_sessions'))['workout_sessions__sum'] or 0
        total_volume_kg = summaries.aggregate(Sum('total_volume_kg'))['total_volume_kg__sum'] or 0
        total_prs = summaries.aggregate(Sum('prs_achieved'))['prs_achieved__sum'] or 0
        
        days = (end_date - start_date).days + 1
        
        return Response({
            'start_date': start_date,
            'end_date': end_date,
            'days': days,
            'habits': {
                'total_completed': total_habits_completed,
                'average_daily': total_habits_completed / days if days > 0 else 0
            },
            'meditation': {
                'total_minutes': total_meditation_minutes,
                'average_daily_minutes': total_meditation_minutes / days if days > 0 else 0
            },
            'workouts': {
                'total_sessions': total_workout_sessions,
                'total_volume_kg': float(total_volume_kg),
                'total_prs': total_prs
            },
            'nutrition': {
                'average_daily_calories': summaries.aggregate(Avg('calories_consumed'))['calories_consumed__avg'] or 0,
                'average_daily_protein': float(summaries.aggregate(Avg('protein_g'))['protein_g__avg'] or 0),
                'average_daily_carbs': float(summaries.aggregate(Avg('carbs_g'))['carbs_g__avg'] or 0),
                'average_daily_fat': float(summaries.aggregate(Avg('fat_g'))['fat_g__avg'] or 0)
            }
        })

