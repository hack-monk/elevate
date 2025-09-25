"""
Celery tasks for daily summary rollups
"""
from celery import shared_task
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date, timedelta
import logging

from .business_logic import DailySummaryBusinessLogic

logger = logging.getLogger(__name__)


@shared_task
def nightly_rollup():
    """
    Nightly task to recalculate daily summaries for all users
    Runs at midnight in each user's timezone
    """
    today = timezone.now().date()
    users = User.objects.all()
    
    for user in users:
        try:
            # Recalculate today's summary for each user
            DailySummaryBusinessLogic.recalculate_daily_summary(user, today)
            logger.info(f"Updated daily summary for user {user.username} on {today}")
        except Exception as e:
            logger.error(f"Error updating daily summary for user {user.username}: {e}")


@shared_task
def rollup_date_range(user_id, start_date, end_date):
    """
    Recalculate daily summaries for a specific user and date range
    """
    try:
        user = User.objects.get(id=user_id)
        current_date = start_date
        
        while current_date <= end_date:
            DailySummaryBusinessLogic.recalculate_daily_summary(user, current_date)
            current_date += timedelta(days=1)
        
        logger.info(f"Updated daily summaries for user {user.username} from {start_date} to {end_date}")
        return f"Successfully updated summaries for {user.username}"
        
    except User.DoesNotExist:
        logger.error(f"User with id {user_id} not found")
        return f"User with id {user_id} not found"
    except Exception as e:
        logger.error(f"Error updating summaries for user {user_id}: {e}")
        return f"Error: {str(e)}"


@shared_task
def rollup_all_users_date_range(start_date, end_date):
    """
    Recalculate daily summaries for all users in a date range
    """
    users = User.objects.all()
    results = []
    
    for user in users:
        try:
            current_date = start_date
            while current_date <= end_date:
                DailySummaryBusinessLogic.recalculate_daily_summary(user, current_date)
                current_date += timedelta(days=1)
            
            results.append(f"Success: {user.username}")
            logger.info(f"Updated daily summaries for user {user.username} from {start_date} to {end_date}")
            
        except Exception as e:
            error_msg = f"Error updating summaries for user {user.username}: {e}"
            results.append(error_msg)
            logger.error(error_msg)
    
    return results

