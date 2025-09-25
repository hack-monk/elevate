# API Examples - Request/Response JSON

## Authentication

### POST /auth/register
**Request:**
```json
{
  "username": "ashutosh",
  "email": "ashutosh@example.com",
  "password": "securepassword123"
}
```

**Response:**
```json
{
  "message": "User created successfully"
}
```

### POST /auth/login
**Request:**
```json
{
  "username": "ashutosh",
  "password": "securepassword123"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "username": "ashutosh",
    "email": "ashutosh@example.com",
    "first_name": "",
    "last_name": "",
    "date_joined": "2024-01-15T10:30:00Z"
  }
}
```

### GET /auth/me
**Response:**
```json
{
  "user": {
    "id": 1,
    "username": "ashutosh",
    "email": "ashutosh@example.com",
    "first_name": "",
    "last_name": "",
    "date_joined": "2024-01-15T10:30:00Z"
  },
  "profile": {
    "timezone": "America/New_York",
    "units": "metric",
    "calorie_target": 1600,
    "protein_target": 140,
    "carbs_target": 140,
    "fat_target": 45,
    "meditation_goal_minutes": 20,
    "habit_reminders_enabled": true,
    "meditation_reminders_enabled": true,
    "reminder_time": "09:00:00"
  }
}
```

## Habits

### POST /habits/
**Request:**
```json
{
  "name": "Drink 8 glasses of water",
  "description": "Stay hydrated throughout the day",
  "reminder_time": "09:00:00"
}
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Drink 8 glasses of water",
  "description": "Stay hydrated throughout the day",
  "reminder_time": "09:00:00",
  "is_active": true,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z",
  "current_streak": 0
}
```

### POST /habits/{id}/check
**Response:**
```json
{
  "message": "Habit checked successfully"
}
```

### GET /habits/{id}/streak
**Response:**
```json
{
  "streak": 7
}
```

## Meditation

### POST /meditation/
**Request:**
```json
{
  "date": "2024-01-15",
  "start_time": "2024-01-15T07:00:00Z",
  "duration_minutes": 20,
  "style": "mindfulness",
  "pre_mood": 3,
  "post_mood": 4,
  "notes": "Focused on breath awareness"
}
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440001",
  "date": "2024-01-15",
  "start_time": "2024-01-15T07:00:00Z",
  "duration_minutes": 20,
  "style": "mindfulness",
  "custom_style": null,
  "pre_mood": 3,
  "post_mood": 4,
  "notes": "Focused on breath awareness",
  "created_at": "2024-01-15T07:20:00Z",
  "updated_at": "2024-01-15T07:20:00Z"
}
```

### GET /meditation/summary?period=week
**Response:**
```json
{
  "period": "week",
  "start_date": "2024-01-08",
  "end_date": "2024-01-15",
  "total_minutes": 140,
  "total_sessions": 7,
  "average_minutes_per_session": 20.0
}
```

## Workouts

### POST /workouts/
**Request:**
```json
{
  "date": "2024-01-15",
  "start_time": "2024-01-15T18:00:00Z",
  "notes": "Push day - chest and shoulders"
}
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440002",
  "date": "2024-01-15",
  "start_time": "2024-01-15T18:00:00Z",
  "end_time": null,
  "notes": "Push day - chest and shoulders",
  "sets": [],
  "total_sets": 0,
  "total_volume_kg": "0.00",
  "created_at": "2024-01-15T18:00:00Z",
  "updated_at": "2024-01-15T18:00:00Z"
}
```

### POST /workouts/{id}/sets
**Request:**
```json
{
  "exercise": "550e8400-e29b-41d4-a716-446655440003",
  "set_number": 1,
  "reps": 10,
  "weight_kg": 60.0,
  "rpe": 8,
  "notes": "Felt strong"
}
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440004",
  "exercise": "550e8400-e29b-41d4-a716-446655440003",
  "exercise_name": "Bench Press",
  "set_number": 1,
  "reps": 10,
  "weight_kg": "60.00",
  "duration_seconds": null,
  "distance_km": null,
  "rpe": 8,
  "notes": "Felt strong",
  "is_pr": false,
  "created_at": "2024-01-15T18:05:00Z"
}
```

### GET /workouts/prs
**Response:**
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440005",
    "exercise": "550e8400-e29b-41d4-a716-446655440003",
    "exercise_name": "Bench Press",
    "set_number": 3,
    "reps": 8,
    "weight_kg": "65.00",
    "duration_seconds": null,
    "distance_km": null,
    "rpe": 9,
    "notes": "New PR!",
    "is_pr": true,
    "created_at": "2024-01-15T18:15:00Z"
  }
]
```

## Nutrition

### POST /foods/
**Request:**
```json
{
  "name": "Chicken Breast",
  "brand": "Generic",
  "serving_size": "100g",
  "calories": 165,
  "protein_g": "31.00",
  "carbs_g": "0.00",
  "fat_g": "3.60",
  "fiber_g": "0.00",
  "sugar_g": "0.00",
  "sodium_mg": "74.00"
}
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440006",
  "name": "Chicken Breast",
  "brand": "Generic",
  "serving_size": "100g",
  "calories": 165,
  "protein_g": "31.00",
  "carbs_g": "0.00",
  "fat_g": "3.60",
  "fiber_g": "0.00",
  "sugar_g": "0.00",
  "sodium_mg": "74.00",
  "is_custom": true,
  "created_at": "2024-01-15T12:00:00Z"
}
```

### GET /foods/search?q=chicken
**Response:**
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440006",
    "name": "Chicken Breast",
    "brand": "Generic",
    "serving_size": "100g",
    "calories": 165,
    "protein_g": "31.00",
    "carbs_g": "0.00",
    "fat_g": "3.60",
    "fiber_g": "0.00",
    "sugar_g": "0.00",
    "sodium_mg": "74.00",
    "is_custom": true,
    "created_at": "2024-01-15T12:00:00Z"
  }
]
```

### POST /meals/
**Request:**
```json
{
  "date": "2024-01-15",
  "meal_type": "lunch",
  "notes": "Post-workout meal"
}
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440007",
  "date": "2024-01-15",
  "meal_type": "lunch",
  "notes": "Post-workout meal",
  "items": [],
  "total_calories": 0,
  "total_protein_g": "0.00",
  "total_carbs_g": "0.00",
  "total_fat_g": "0.00",
  "created_at": "2024-01-15T13:00:00Z",
  "updated_at": "2024-01-15T13:00:00Z"
}
```

### POST /meals/{id}/items
**Request:**
```json
{
  "food": "550e8400-e29b-41d4-a716-446655440006",
  "quantity": "150.00"
}
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440008",
  "food": "550e8400-e29b-41d4-a716-446655440006",
  "food_name": "Chicken Breast",
  "food_brand": "Generic",
  "quantity": "150.00",
  "custom_calories": null,
  "custom_protein_g": null,
  "custom_carbs_g": null,
  "custom_fat_g": null,
  "created_at": "2024-01-15T13:05:00Z"
}
```

## Dashboard

### GET /dashboard/today
**Response:**
```json
{
  "date": "2024-01-15",
  "habits": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "Drink 8 glasses of water",
      "description": "Stay hydrated throughout the day",
      "reminder_time": "09:00:00",
      "is_active": true,
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z",
      "current_streak": 7
    }
  ],
  "habits_completed": 1,
  "habits_total": 1,
  "habits_streak": 7,
  "meditation_minutes": 20,
  "meditation_sessions": 1,
  "meditation_goal_minutes": 20,
  "workout_sessions": 1,
  "total_volume_kg": "600.00",
  "prs_achieved": 1,
  "calories_consumed": 247,
  "calories_target": 1600,
  "calories_remaining": 1353,
  "protein_g": "46.50",
  "protein_target": 140,
  "protein_remaining_g": "93.50",
  "carbs_g": "0.00",
  "carbs_target": 140,
  "carbs_remaining_g": "140.00",
  "fat_g": "5.40",
  "fat_target": 45,
  "fat_remaining_g": "39.60"
}
```

## Summary

### GET /summary?start=2024-01-08&end=2024-01-15
**Response:**
```json
{
  "start_date": "2024-01-08",
  "end_date": "2024-01-15",
  "days": 8,
  "habits": {
    "total_completed": 8,
    "average_daily": 1.0
  },
  "meditation": {
    "total_minutes": 160,
    "average_daily_minutes": 20.0
  },
  "workouts": {
    "total_sessions": 4,
    "total_volume_kg": "2400.00",
    "total_prs": 2
  },
  "nutrition": {
    "average_daily_calories": 1450.0,
    "average_daily_protein": 120.5,
    "average_daily_carbs": 150.0,
    "average_daily_fat": 40.0
  }
}
```

## Error Responses

### 400 Bad Request
```json
{
  "error": "Invalid date format"
}
```

### 401 Unauthorized
```json
{
  "error": "Invalid credentials"
}
```

### 404 Not Found
```json
{
  "detail": "Not found."
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal server error"
}
```

