from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'meditation', views.MeditationLogViewSet, basename='meditation')

urlpatterns = [
    path('', include(router.urls)),
]

