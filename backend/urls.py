from django.urls import path, include

urlpatterns = [
    path('api/accounts/', include('apps.accounts.urls')),
    path('api/habits/', include('apps.habits.urls')),
    path('api/meditations/', include('apps.meditations.urls')),
    path('api/workouts/', include('apps.workouts.urls')),
    path('api/nutrition/', include('apps.nutrition.urls')),
    path('api/reports/', include('apps.reports.urls')),
]

