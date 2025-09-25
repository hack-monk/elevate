from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'auth', views.AuthViewSet, basename='auth')
router.register(r'habits', views.HabitViewSet)
router.register(r'habit-checks', views.HabitCheckViewSet)
router.register(r'meditation', views.MeditationLogViewSet, basename='meditation')
router.register(r'exercises', views.ExerciseViewSet)
router.register(r'workouts', views.WorkoutSessionViewSet)
router.register(r'foods', views.FoodViewSet)
router.register(r'meals', views.MealViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('dashboard/today/', views.DashboardView.as_view(), name='dashboard-today'),
    path('summary/', views.SummaryView.as_view(), name='summary'),
]
