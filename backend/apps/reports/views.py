from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Sum, Avg
from django.utils import timezone
from datetime import datetime, timedelta

from .models import DailySummary
from .serializers import DailySummarySerializer, DashboardTodaySerializer, WeeklySummarySerializer


class DailySummaryViewSet(viewsets.ReadOnlyModelViewSet):
    """Daily summary read-only operations"""
    serializer_class = DailySummarySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return DailySummary.objects.filter(user=self.request.user)


class DashboardView(APIView):
    """Today's dashboard data"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """GET /api/reports/dashboard/today"""
        today = timezone.now().date()
        user = request.user
        
        # Get habits with completion status for today
        from apps.habits.models import Habit, HabitCheck
        habits = Habit.objects.filter(user=user, is_active=True)
        habit_checks = HabitCheck.objects.filter(
            habit__in=habits, date=today
        )
        
        # Build habits list with completion status
        habits_data = []
        for habit in habits:
            habit_check = habit_checks.filter(habit=habit).first()
            habits_data.append({
                'id': str(habit.id),
                'name': habit.name,
                'completed': habit_check.completed if habit_check else False
            })
        
        # Get today's meditation total
        from apps.meditations.models import MeditationLog
        meditation_logs = MeditationLog.objects.filter(user=user, date=today)
        meditation_minutes = sum(log.duration_minutes for log in meditation_logs)
        
        # Get today's workout volume
        from apps.workouts.models import WorkoutSession, WorkoutSet
        workouts = WorkoutSession.objects.filter(user=user, date=today)
        workout_volume = 0
        for session in workouts:
            for set_obj in session.sets.all():
                if set_obj.reps and set_obj.weight_kg:
                    workout_volume += float(set_obj.reps * set_obj.weight_kg)
        
        # Get today's nutrition totals
        from apps.nutrition.models import Meal, MealItem
        meals = Meal.objects.filter(user=user, date=today)
        
        total_calories = 0
        total_protein = 0
        total_carbs = 0
        total_fat = 0
        
        for meal in meals:
            for item in meal.items.all():
                if item.custom_calories:
                    total_calories += item.custom_calories
                else:
                    total_calories += int(item.quantity * item.food.calories)
                
                if item.custom_protein_g:
                    total_protein += float(item.custom_protein_g)
                else:
                    total_protein += float(item.quantity * item.food.protein_g)
                
                if item.custom_carbs_g:
                    total_carbs += float(item.custom_carbs_g)
                else:
                    total_carbs += float(item.quantity * item.food.carbs_g)
                
                if item.custom_fat_g:
                    total_fat += float(item.custom_fat_g)
                else:
                    total_fat += float(item.quantity * item.food.fat_g)
        
        # Get user targets
        profile = user.profile
        
        dashboard_data = {
            'date': today.isoformat(),
            'habits': habits_data,
            'meditation_min': meditation_minutes,
            'workout_volume': workout_volume,
            'nutrition': {
                'kcal': total_calories,
                'protein_g': round(total_protein, 1),
                'carbs_g': round(total_carbs, 1),
                'fat_g': round(total_fat, 1),
                'targets': {
                    'kcal': profile.calorie_target,
                    'protein_g': profile.protein_target,
                    'carbs_g': profile.carbs_target,
                    'fat_g': profile.fat_target
                }
            }
        }
        
        return Response(dashboard_data)


class DailySummaryView(APIView):
    """Daily summary endpoint"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """GET /api/reports/summary/daily?start=YYYY-MM-DD&end=YYYY-MM-DD"""
        start_date = request.query_params.get('start')
        end_date = request.query_params.get('end')
        
        if not start_date or not end_date:
            return Response({'error': 'start and end dates required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            return Response({'error': 'Invalid date format'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get or create daily summaries for the date range
        summaries = []
        current_date = start_date
        
        while current_date <= end_date:
            summary, created = DailySummary.objects.get_or_create(
                user=request.user,
                date=current_date
            )
            
            # If summary was just created or is empty, recalculate it
            if created or (summary.calories_consumed == 0 and summary.meditation_minutes == 0):
                from apps.reports.business_logic import DailySummaryBusinessLogic
                summary = DailySummaryBusinessLogic.recalculate_daily_summary(request.user, current_date)
            
            summaries.append({
                'date': current_date.isoformat(),
                'kcal_total': summary.calories_consumed,
                'protein_g': float(summary.protein_g),
                'carbs_g': float(summary.carbs_g),
                'fat_g': float(summary.fat_g),
                'meditation_min': summary.meditation_minutes,
                'workout_volume': float(summary.total_volume_kg),
                'habits_completed': summary.habits_completed,
                'habits_total': summary.habits_total
            })
            
            current_date += timedelta(days=1)
        
        return Response(summaries)


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
