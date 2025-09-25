from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'summaries', views.DailySummaryViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('dashboard/today/', views.DashboardView.as_view(), name='dashboard-today'),
    path('summary/daily/', views.DailySummaryView.as_view(), name='daily-summary'),
    path('summary/', views.SummaryView.as_view(), name='summary'),
]
