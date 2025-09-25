# Django Apps Project Structure

## Project Layout

```
backend/
├── apps/
│   ├── accounts/
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   ├── models.py          # User, Profile
│   │   ├── serializers.py     # UserSerializer, ProfileSerializer
│   │   ├── views.py           # AuthViewSet, ProfileViewSet
│   │   ├── urls.py            # /api/accounts/
│   │   └── business_logic.py  # (if needed)
│   │
│   ├── habits/
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   ├── models.py          # Habit, HabitCheck
│   │   ├── serializers.py     # HabitSerializer, HabitCheckSerializer
│   │   ├── views.py           # HabitViewSet, HabitCheckViewSet
│   │   ├── urls.py            # /api/habits/
│   │   └── business_logic.py # HabitBusinessLogic
│   │
│   ├── meditations/
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   ├── models.py          # MeditationLog
│   │   ├── serializers.py     # MeditationLogSerializer
│   │   ├── views.py           # MeditationLogViewSet
│   │   ├── urls.py            # /api/meditations/
│   │   └── business_logic.py # MeditationBusinessLogic
│   │
│   ├── workouts/
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   ├── models.py          # Exercise, WorkoutSession, WorkoutSet
│   │   ├── serializers.py     # ExerciseSerializer, WorkoutSessionSerializer, WorkoutSetSerializer
│   │   ├── views.py           # ExerciseViewSet, WorkoutSessionViewSet
│   │   ├── urls.py            # /api/workouts/
│   │   └── business_logic.py # WorkoutBusinessLogic
│   │
│   ├── nutrition/
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   ├── models.py          # Food, Meal, MealItem
│   │   ├── serializers.py     # FoodSerializer, MealSerializer, MealItemSerializer
│   │   ├── views.py           # FoodViewSet, MealViewSet
│   │   ├── urls.py            # /api/nutrition/
│   │   └── business_logic.py # NutritionBusinessLogic
│   │
│   └── reports/
│       ├── __init__.py
│       ├── apps.py
│       ├── models.py          # DailySummary
│       ├── serializers.py     # DailySummarySerializer, DashboardTodaySerializer, WeeklySummarySerializer
│       ├── views.py           # DailySummaryViewSet, DashboardView, SummaryView
│       ├── urls.py            # /api/reports/
│       └── business_logic.py # DailySummaryBusinessLogic
│
├── urls.py                    # Main URL routing
└── settings.py               # Django settings
```

## API Endpoints

### Authentication (`/api/accounts/`)
- `POST /api/accounts/auth/register/` - User registration
- `POST /api/accounts/auth/login/` - User login
- `POST /api/accounts/auth/refresh/` - Refresh access token
- `POST /api/accounts/auth/logout/` - User logout
- `GET /api/accounts/auth/me/` - Get current user info
- `GET /api/accounts/profiles/` - Get user profile
- `PUT /api/accounts/profiles/` - Update user profile

### Habits (`/api/habits/`)
- `GET /api/habits/habits/` - List user habits
- `POST /api/habits/habits/` - Create new habit
- `GET /api/habits/habits/{id}/` - Get habit details
- `PUT /api/habits/habits/{id}/` - Update habit
- `DELETE /api/habits/habits/{id}/` - Delete habit
- `POST /api/habits/habits/{id}/check/` - Mark habit as completed
- `GET /api/habits/habits/{id}/streak/` - Get habit streak
- `GET /api/habits/habit-checks/` - List habit checks

### Meditations (`/api/meditations/`)
- `GET /api/meditations/meditation/` - List meditation logs
- `POST /api/meditations/meditation/` - Log meditation session
- `GET /api/meditations/meditation/{id}/` - Get meditation log
- `PUT /api/meditations/meditation/{id}/` - Update meditation log
- `DELETE /api/meditations/meditation/{id}/` - Delete meditation log
- `GET /api/meditations/meditation/summary/` - Get meditation summary

### Workouts (`/api/workouts/`)
- `GET /api/workouts/exercises/` - List exercises
- `POST /api/workouts/exercises/` - Create custom exercise
- `GET /api/workouts/workouts/` - List workout sessions
- `POST /api/workouts/workouts/` - Create workout session
- `GET /api/workouts/workouts/{id}/` - Get workout session
- `POST /api/workouts/workouts/{id}/add_set/` - Add set to workout
- `GET /api/workouts/workouts/prs/` - Get personal records

### Nutrition (`/api/nutrition/`)
- `GET /api/nutrition/foods/` - List foods
- `POST /api/nutrition/foods/` - Create custom food
- `GET /api/nutrition/foods/search/` - Search foods
- `GET /api/nutrition/meals/` - List meals
- `POST /api/nutrition/meals/` - Create meal
- `POST /api/nutrition/meals/{id}/add_item/` - Add food item to meal

### Reports (`/api/reports/`)
- `GET /api/reports/summaries/` - List daily summaries
- `GET /api/reports/dashboard/today/` - Today's dashboard
- `GET /api/reports/summary/` - Date range summary

## Key Features

### Models
- **Accounts**: User authentication and profile management
- **Habits**: Daily habit tracking with streak calculation
- **Meditations**: Meditation session logging with mood tracking
- **Workouts**: Exercise library, workout sessions, and PR detection
- **Nutrition**: Food database, meal logging, and macro tracking
- **Reports**: Daily summaries and analytics

### Business Logic
- **Habit Streaks**: Automatic calculation and reset logic
- **PR Detection**: Personal record detection for workouts
- **Macro Tracking**: Daily nutrition target vs actual tracking
- **Daily Summaries**: Denormalized rollup data for performance

### API Design
- **RESTful**: Standard CRUD operations with ViewSets
- **Authentication**: JWT with refresh tokens in HTTP-only cookies
- **Validation**: Comprehensive input validation and error handling
- **Performance**: Optimized queries with proper indexing

## Database Schema

### Key Relationships
- User → Profile (OneToOne)
- User → Habits (ForeignKey)
- Habit → HabitCheck (ForeignKey)
- User → MeditationLog (ForeignKey)
- User → WorkoutSession (ForeignKey)
- WorkoutSession → WorkoutSet (ForeignKey)
- Exercise → WorkoutSet (ForeignKey)
- User → Meal (ForeignKey)
- Meal → MealItem (ForeignKey)
- Food → MealItem (ForeignKey)
- User → DailySummary (ForeignKey)

### Indexes
- User-based filtering on all models
- Date-based queries for time-series data
- Unique constraints for data integrity
- Performance indexes for common queries

## Next Steps

1. **Django Settings**: Configure apps in INSTALLED_APPS
2. **Database Migration**: Run `python manage.py makemigrations` and `python manage.py migrate`
3. **Admin Interface**: Register models in admin.py files
4. **Testing**: Create test files for each app
5. **Documentation**: Add docstrings and API documentation
6. **Deployment**: Configure for production environment
