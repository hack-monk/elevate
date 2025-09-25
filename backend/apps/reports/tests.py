"""
Tests for reports app
"""
import pytest
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from datetime import date, timedelta
from decimal import Decimal

from apps.accounts.models import Profile
from apps.habits.models import Habit, HabitCheck
from apps.meditations.models import MeditationLog
from apps.workouts.models import Exercise, WorkoutSession, WorkoutSet
from apps.nutrition.models import Food, Meal, MealItem
from apps.reports.models import DailySummary
from apps.reports.business_logic import DailySummaryBusinessLogic


class DashboardViewTest(APITestCase):
    """Test dashboard endpoint"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.profile = Profile.objects.create(
            user=self.user,
            calorie_target=1600,
            protein_target=140,
            carbs_target=140,
            fat_target=45
        )
        self.client.force_authenticate(user=self.user)
    
    def test_dashboard_today_empty(self):
        """Test dashboard with no data"""
        url = reverse('dashboard-today')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        
        self.assertEqual(data['date'], date.today().isoformat())
        self.assertEqual(data['habits'], [])
        self.assertEqual(data['meditation_min'], 0)
        self.assertEqual(data['workout_volume'], 0)
        self.assertEqual(data['nutrition']['kcal'], 0)
        self.assertEqual(data['nutrition']['targets']['kcal'], 1600)
    
    def test_dashboard_with_habits(self):
        """Test dashboard with habits"""
        # Create habit
        habit = Habit.objects.create(
            user=self.user,
            name='Drink Water',
            is_active=True
        )
        
        # Mark as completed today
        HabitCheck.objects.create(
            habit=habit,
            date=date.today(),
            completed=True
        )
        
        url = reverse('dashboard-today')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        
        self.assertEqual(len(data['habits']), 1)
        self.assertEqual(data['habits'][0]['name'], 'Drink Water')
        self.assertTrue(data['habits'][0]['completed'])
    
    def test_dashboard_with_meditation(self):
        """Test dashboard with meditation"""
        MeditationLog.objects.create(
            user=self.user,
            date=date.today(),
            start_time='2024-01-15T07:00:00Z',
            duration_minutes=20,
            style='mindfulness'
        )
        
        url = reverse('dashboard-today')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        
        self.assertEqual(data['meditation_min'], 20)
    
    def test_dashboard_with_workout(self):
        """Test dashboard with workout"""
        # Create exercise
        exercise = Exercise.objects.create(
            name='Bench Press',
            category='push',
            is_custom=False
        )
        
        # Create workout session
        session = WorkoutSession.objects.create(
            user=self.user,
            date=date.today(),
            start_time='2024-01-15T18:00:00Z'
        )
        
        # Add sets
        WorkoutSet.objects.create(
            session=session,
            exercise=exercise,
            set_number=1,
            reps=10,
            weight_kg=Decimal('60.0')
        )
        
        WorkoutSet.objects.create(
            session=session,
            exercise=exercise,
            set_number=2,
            reps=8,
            weight_kg=Decimal('65.0')
        )
        
        url = reverse('dashboard-today')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        
        # Expected volume: (10 * 60) + (8 * 65) = 600 + 520 = 1120
        self.assertEqual(data['workout_volume'], 1120.0)
    
    def test_dashboard_with_nutrition(self):
        """Test dashboard with nutrition"""
        # Create food
        food = Food.objects.create(
            name='Chicken Breast',
            calories=165,
            protein_g=Decimal('31.0'),
            carbs_g=Decimal('0.0'),
            fat_g=Decimal('3.6'),
            is_custom=False
        )
        
        # Create meal
        meal = Meal.objects.create(
            user=self.user,
            date=date.today(),
            meal_type='lunch'
        )
        
        # Add food item
        MealItem.objects.create(
            meal=meal,
            food=food,
            quantity=Decimal('150.0')  # 1.5x serving
        )
        
        url = reverse('dashboard-today')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        
        # Expected: 165 * 1.5 = 247.5 calories
        self.assertEqual(data['nutrition']['kcal'], 247)
        self.assertEqual(data['nutrition']['protein_g'], 46.5)  # 31 * 1.5


class DailySummaryViewTest(APITestCase):
    """Test daily summary endpoint"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.profile = Profile.objects.create(user=self.user)
        self.client.force_authenticate(user=self.user)
    
    def test_daily_summary_empty_range(self):
        """Test daily summary with no data"""
        url = reverse('daily-summary')
        response = self.client.get(url, {
            'start': '2024-01-01',
            'end': '2024-01-03'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        
        self.assertEqual(len(data), 3)  # 3 days
        for day in data:
            self.assertEqual(day['kcal_total'], 0)
            self.assertEqual(day['meditation_min'], 0)
            self.assertEqual(day['workout_volume'], 0)
    
    def test_daily_summary_with_data(self):
        """Test daily summary with data"""
        # Create some data for today
        habit = Habit.objects.create(
            user=self.user,
            name='Test Habit',
            is_active=True
        )
        HabitCheck.objects.create(
            habit=habit,
            date=date.today(),
            completed=True
        )
        
        MeditationLog.objects.create(
            user=self.user,
            date=date.today(),
            start_time='2024-01-15T07:00:00Z',
            duration_minutes=20,
            style='mindfulness'
        )
        
        url = reverse('daily-summary')
        response = self.client.get(url, {
            'start': date.today().isoformat(),
            'end': date.today().isoformat()
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        
        self.assertEqual(len(data), 1)
        today_data = data[0]
        self.assertEqual(today_data['date'], date.today().isoformat())
        self.assertEqual(today_data['habits_completed'], 1)
        self.assertEqual(today_data['meditation_min'], 20)
    
    def test_daily_summary_invalid_dates(self):
        """Test daily summary with invalid dates"""
        url = reverse('daily-summary')
        
        # Missing dates
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Invalid date format
        response = self.client.get(url, {
            'start': 'invalid-date',
            'end': '2024-01-01'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class DailySummaryBusinessLogicTest(TestCase):
    """Test daily summary business logic"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.profile = Profile.objects.create(
            user=self.user,
            calorie_target=1600,
            protein_target=140,
            carbs_target=140,
            fat_target=45
        )
    
    def test_recalculate_daily_summary_empty(self):
        """Test recalculating empty daily summary"""
        today = date.today()
        summary = DailySummaryBusinessLogic.recalculate_daily_summary(self.user, today)
        
        self.assertEqual(summary.user, self.user)
        self.assertEqual(summary.date, today)
        self.assertEqual(summary.habits_completed, 0)
        self.assertEqual(summary.habits_total, 0)
        self.assertEqual(summary.meditation_minutes, 0)
        self.assertEqual(summary.calories_consumed, 0)
    
    def test_recalculate_daily_summary_with_habits(self):
        """Test recalculating with habits"""
        today = date.today()
        
        # Create habits
        habit1 = Habit.objects.create(
            user=self.user,
            name='Habit 1',
            is_active=True
        )
        habit2 = Habit.objects.create(
            user=self.user,
            name='Habit 2',
            is_active=True
        )
        
        # Mark one as completed
        HabitCheck.objects.create(
            habit=habit1,
            date=today,
            completed=True
        )
        
        summary = DailySummaryBusinessLogic.recalculate_daily_summary(self.user, today)
        
        self.assertEqual(summary.habits_total, 2)
        self.assertEqual(summary.habits_completed, 1)
    
    def test_recalculate_daily_summary_with_meditation(self):
        """Test recalculating with meditation"""
        today = date.today()
        
        MeditationLog.objects.create(
            user=self.user,
            date=today,
            start_time='2024-01-15T07:00:00Z',
            duration_minutes=20,
            style='mindfulness'
        )
        
        MeditationLog.objects.create(
            user=self.user,
            date=today,
            start_time='2024-01-15T19:00:00Z',
            duration_minutes=10,
            style='breathing'
        )
        
        summary = DailySummaryBusinessLogic.recalculate_daily_summary(self.user, today)
        
        self.assertEqual(summary.meditation_minutes, 30)
        self.assertEqual(summary.meditation_sessions, 2)
    
    def test_recalculate_daily_summary_with_workout(self):
        """Test recalculating with workout"""
        today = date.today()
        
        # Create exercise
        exercise = Exercise.objects.create(
            name='Bench Press',
            category='push',
            is_custom=False
        )
        
        # Create workout session
        session = WorkoutSession.objects.create(
            user=self.user,
            date=today,
            start_time='2024-01-15T18:00:00Z'
        )
        
        # Add sets
        WorkoutSet.objects.create(
            session=session,
            exercise=exercise,
            set_number=1,
            reps=10,
            weight_kg=Decimal('60.0')
        )
        
        summary = DailySummaryBusinessLogic.recalculate_daily_summary(self.user, today)
        
        self.assertEqual(summary.workout_sessions, 1)
        self.assertEqual(summary.total_volume_kg, Decimal('600.0'))
    
    def test_recalculate_daily_summary_with_nutrition(self):
        """Test recalculating with nutrition"""
        today = date.today()
        
        # Create food
        food = Food.objects.create(
            name='Chicken Breast',
            calories=165,
            protein_g=Decimal('31.0'),
            carbs_g=Decimal('0.0'),
            fat_g=Decimal('3.6'),
            is_custom=False
        )
        
        # Create meal
        meal = Meal.objects.create(
            user=self.user,
            date=today,
            meal_type='lunch'
        )
        
        # Add food item
        MealItem.objects.create(
            meal=meal,
            food=food,
            quantity=Decimal('150.0')  # 1.5x serving
        )
        
        summary = DailySummaryBusinessLogic.recalculate_daily_summary(self.user, today)
        
        self.assertEqual(summary.calories_consumed, 247)  # 165 * 1.5
        self.assertEqual(summary.protein_g, Decimal('46.5'))  # 31 * 1.5
        self.assertEqual(summary.carbs_g, Decimal('0.0'))
        self.assertEqual(summary.fat_g, Decimal('5.4'))  # 3.6 * 1.5


class CeleryTasksTest(TestCase):
    """Test Celery tasks"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.profile = Profile.objects.create(user=self.user)
    
    def test_rollup_date_range_task(self):
        """Test rollup_date_range task"""
        from apps.reports.tasks import rollup_date_range
        
        start_date = date.today()
        end_date = start_date + timedelta(days=2)
        
        # Create some data
        habit = Habit.objects.create(
            user=self.user,
            name='Test Habit',
            is_active=True
        )
        HabitCheck.objects.create(
            habit=habit,
            date=start_date,
            completed=True
        )
        
        result = rollup_date_range(self.user.id, start_date, end_date)
        
        self.assertIn('Successfully updated summaries', result)
        
        # Check that summaries were created
        summaries = DailySummary.objects.filter(
            user=self.user,
            date__gte=start_date,
            date__lte=end_date
        )
        self.assertEqual(summaries.count(), 3)  # 3 days
    
    def test_rollup_all_users_date_range_task(self):
        """Test rollup_all_users_date_range task"""
        from apps.reports.tasks import rollup_all_users_date_range
        
        start_date = date.today()
        end_date = start_date + timedelta(days=1)
        
        result = rollup_all_users_date_range(start_date, end_date)
        
        self.assertIsInstance(result, list)
        self.assertIn('Success', result[0])
        
        # Check that summaries were created
        summaries = DailySummary.objects.filter(
            date__gte=start_date,
            date__lte=end_date
        )
        self.assertEqual(summaries.count(), 2)  # 1 user * 2 days

