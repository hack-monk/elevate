# Elevate - Personal Wellness Tracking App

A comprehensive Django REST API application for tracking habits, meditation, workouts, and nutrition with advanced analytics and reporting.

## 🎯 Overview

Elevate is a personal wellness tracking application designed to help users build and maintain healthy habits across four key pillars:

- **Habits**: Daily habit tracking with streak calculation
- **Meditation**: Session logging with mood tracking and progress analytics
- **Workouts**: Exercise library, workout sessions, and personal record detection
- **Nutrition**: Food database, meal logging, and macro tracking

## 🏗️ Architecture

### Tech Stack
- **Backend**: Django 4.2 + Django REST Framework
- **Database**: PostgreSQL
- **Cache/Queue**: Redis + Celery
- **Authentication**: JWT with refresh tokens
- **Deployment**: Docker Compose (dev), AWS/Render (prod)

### Project Structure
```
backend/
├── apps/
│   ├── accounts/          # User authentication & profiles
│   ├── habits/            # Daily habit tracking
│   ├── meditations/       # Meditation session logging
│   ├── workouts/          # Exercise library & workout tracking
│   ├── nutrition/         # Food database & meal logging
│   └── reports/           # Analytics & dashboard
├── urls.py               # Main URL routing
└── settings.py           # Django configuration
```

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- PostgreSQL 13+
- Redis 6+
- Docker & Docker Compose (optional)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Elevate
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your database and Redis settings
   ```

5. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Start development server**
   ```bash
   python manage.py runserver
   ```

### Docker Setup (Alternative)

```bash
# Build and start all services
docker-compose up --build

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser
```

## 📊 API Endpoints

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

### Reports & Analytics (`/api/reports/`)
- `GET /api/reports/dashboard/today/` - Today's dashboard
- `GET /api/reports/summary/daily/` - Daily summaries for date range
- `GET /api/reports/summary/` - Weekly/monthly summaries
- `GET /api/reports/summaries/` - List daily summaries

## 🎯 Key Features

### Dashboard
Real-time dashboard showing today's progress across all pillars:
```json
{
  "date": "2025-01-15",
  "habits": [{"id": "uuid", "name": "Drink Water", "completed": true}],
  "meditation_min": 20,
  "workout_volume": 12000,
  "nutrition": {
    "kcal": 1580, "protein_g": 135, "carbs_g": 142, "fat_g": 44,
    "targets": {"kcal": 1600, "protein_g": 140, "carbs_g": 140, "fat_g": 45}
  }
}
```

### Habit Tracking
- Daily habit completion tracking
- Automatic streak calculation
- Streak reset logic for missed days
- Reminder notifications

### Meditation Logging
- Session duration and style tracking
- Pre/post mood assessment
- Weekly/monthly progress summaries
- Goal tracking (default: 20 min/day)

### Workout Management
- Exercise library with categories
- Workout session tracking
- Set/rep/weight logging
- Personal record detection
- Volume calculations

### Nutrition Tracking
- Food database with macro information
- Meal logging with custom overrides
- Daily macro targets vs actual
- Macro breakdown (protein, carbs, fats)

### Analytics & Reporting
- Daily summaries with rollup data
- Weekly/monthly trend analysis
- Progress tracking across all pillars
- Export capabilities (CSV)

## 🔧 Management Commands

### Recompute Daily Summaries
```bash
# Recompute for all users
python manage.py recompute_summaries --start=2024-01-01 --end=2024-01-31

# Recompute for specific user
python manage.py recompute_summaries --start=2024-01-01 --end=2024-01-31 --user-id=1

# Run asynchronously with Celery
python manage.py recompute_summaries --start=2024-01-01 --end=2024-01-31 --async
```

## 🧪 Testing

Run the test suite:
```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test apps.reports

# Run with coverage
coverage run --source='.' manage.py test
coverage report
coverage html
```

## 📈 Background Tasks

### Celery Tasks
- **Nightly Rollup**: Recalculates daily summaries for all users
- **Date Range Rollup**: Recalculates summaries for specific date ranges
- **User-specific Rollup**: Recalculates summaries for individual users

### Django Signals
Automatic summary updates when data changes:
- Habit checks → Update summary
- Meditation logs → Update summary
- Workout sessions/sets → Update summary
- Meals/meal items → Update summary

## 🗄️ Database Schema

### Key Models
- **User/Profile**: Authentication and user preferences
- **Habit/HabitCheck**: Daily habit tracking with streaks
- **MeditationLog**: Meditation session logging
- **Exercise/WorkoutSession/WorkoutSet**: Workout tracking and PR detection
- **Food/Meal/MealItem**: Nutrition tracking with macro calculations
- **DailySummary**: Denormalized rollup data for performance

### Indexes & Performance
- User-based filtering on all models
- Date-based queries for time-series data
- Unique constraints for data integrity
- Performance indexes for common queries

## 🔐 Security

- JWT authentication with refresh tokens
- HTTP-only cookies for refresh tokens
- User data isolation (no cross-user data access)
- Input validation and sanitization
- CORS configuration for frontend integration

## 🚀 Deployment

### Development
```bash
# Using Docker Compose
docker-compose up --build

# Using local environment
python manage.py runserver
```

### Production
- Configure environment variables
- Set up PostgreSQL and Redis
- Configure Celery workers
- Set up reverse proxy (nginx)
- Configure SSL certificates

## 📝 Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/elevate

# Redis
REDIS_URL=redis://localhost:6379/0

# Django
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=your-domain.com

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the documentation
- Review the API examples

## 🗺️ Roadmap

- [ ] Frontend React application
- [ ] Mobile app (React Native)
- [ ] Advanced analytics and insights
- [ ] Social features and challenges
- [ ] Integration with fitness trackers
- [ ] AI-powered recommendations
- [ ] Export to health platforms

---

**Built with ❤️ for personal wellness and habit tracking**