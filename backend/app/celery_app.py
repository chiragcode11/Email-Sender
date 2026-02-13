from celery import Celery
from app.config import settings

# Create Celery instance
celery_app = Celery(
    "email_automation",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.tasks.email_tasks",
        "app.tasks.ai_tasks",
    ]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Beat schedule for periodic tasks
celery_app.conf.beat_schedule = {
    "update-warmup-limits": {
        "task": "app.tasks.email_tasks.update_warmup_limits",
        "schedule": 86400.0,  # Run daily (24 hours)
    },
    "check-scheduled-campaigns": {
        "task": "app.tasks.email_tasks.check_scheduled_campaigns",
        "schedule": 60.0,  # Run every minute
    },
}
