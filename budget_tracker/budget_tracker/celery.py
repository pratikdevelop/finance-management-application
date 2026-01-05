"""
Celery configuration for budget_tracker project
"""
import os
from celery import Celery
from celery.schedules import crontab

# Set default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'budget_tracker.settings')

app = Celery('budget_tracker')

# Load config from Django settings with CELERY namespace
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks from all registered Django apps
app.autodiscover_tasks()

# Celery Beat schedule for periodic tasks
app.conf.beat_schedule = {
    'process-recurring-transactions-daily': {
        'task': 'budget.tasks.process_recurring_transactions',
        'schedule': crontab(hour=0, minute=0),  # Run daily at midnight
    },
    'send-bill-reminders-daily': {
        'task': 'budget.tasks.send_bill_reminders',
        'schedule': crontab(hour=9, minute=0),  # Run daily at 9 AM
    },
    'update-investment-prices-hourly': {
        'task': 'budget.tasks.update_investment_prices',
        'schedule': crontab(minute=0),  # Run every hour
    },
    'cleanup-old-data-weekly': {
        'task': 'budget.tasks.cleanup_old_data',
        'schedule': crontab(day_of_week=0, hour=2, minute=0),  # Run weekly on Sunday at 2 AM
    },
}

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
