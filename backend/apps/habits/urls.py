from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'habits', views.HabitViewSet)
router.register(r'habit-checks', views.HabitCheckViewSet)

urlpatterns = [
    path('', include(router.urls)),
]

