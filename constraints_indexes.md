# Database Constraints & Indexes

## Unique Constraints

1. **Profile**: `user` (OneToOne with User)
2. **Habit**: `(user, name)` - Unique habit names per user
3. **HabitCheck**: `(habit, date)` - One check per habit per day
4. **Exercise**: `(name, created_by)` - Unique exercise names per user
5. **Food**: `(name, brand, created_by)` - Unique food entries per user
6. **DailySummary**: `(user, date)` - One summary per user per day
7. **WorkoutSet**: `(session, exercise, set_number)` - Unique set numbers per exercise per session

## Indexes

### Performance Indexes
- `habits(user, is_active)` - Filter active habits per user
- `habits(user, created_at)` - Sort habits by creation date
- `habit_checks(habit, date)` - Query habit checks by habit and date
- `habit_checks(date, completed)` - Query completed checks by date
- `meditation_logs(user, date)` - Query meditation logs by user and date
- `meditation_logs(date, duration_minutes)` - Query meditation by date and duration
- `exercises(category)` - Filter exercises by category
- `exercises(is_custom, created_by)` - Filter custom exercises per user
- `workout_sessions(user, date)` - Query workouts by user and date
- `workout_sessions(date)` - Query workouts by date
- `workout_sets(session, exercise)` - Query sets by session and exercise
- `workout_sets(exercise, weight_kg)` - Query sets by exercise and weight
- `workout_sets(is_pr)` - Query personal records
- `foods(name)` - Search foods by name
- `foods(is_custom, created_by)` - Filter custom foods per user
- `meals(user, date)` - Query meals by user and date
- `meals(date, meal_type)` - Query meals by date and type
- `meal_items(meal)` - Query meal items by meal
- `meal_items(food)` - Query meal items by food
- `daily_summaries(user, date)` - Query summaries by user and date
- `daily_summaries(date)` - Query summaries by date

## Business Logic Constraints

### Habit Streak Logic
- Streak resets when a day is missed
- Streak calculation considers consecutive completed days
- Today's completion affects current streak

### Meditation Validation
- No overlapping sessions on the same date
- Duration between 1-300 minutes
- Custom style required when style is 'custom'

### Workout PR Detection
- PR based on heaviest weight for exercise
- Same weight with more reps also counts as PR
- 1RM calculation using Epley formula

### Nutrition Calculations
- Custom macros override food database values
- Daily targets vs actual consumption
- Remaining macros calculated as target - consumed

### Daily Summary Rollup
- Recalculated nightly via Celery task
- Updated on data changes
- Denormalized for performance

