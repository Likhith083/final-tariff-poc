"""
Celery Application for ATLAS Enterprise
Background task processing configuration.
"""

from celery import Celery
from celery.schedules import crontab

from ..core.config import settings

# Create Celery instance
celery_app = Celery(
    "atlas_enterprise",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=[
        "backend.tasks.document_tasks",
        "backend.tasks.data_tasks", 
        "backend.tasks.analytics_tasks"
    ]
)

# Celery configuration
celery_app.conf.update(
    # Task routing
    task_routes={
        "backend.tasks.document_tasks.*": {"queue": "documents"},
        "backend.tasks.data_tasks.*": {"queue": "data"},
        "backend.tasks.analytics_tasks.*": {"queue": "analytics"},
    },
    
    # Task serialization
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    
    # Timezone
    timezone="UTC",
    enable_utc=True,
    
    # Task execution
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_reject_on_worker_lost=True,
    
    # Result backend settings
    result_expires=3600,  # 1 hour
    result_backend_transport_options={
        "master_name": "atlas-redis",
    },
    
    # Worker settings
    worker_max_tasks_per_child=1000,
    worker_disable_rate_limits=False,
    
    # Monitoring
    worker_send_task_events=True,
    task_send_sent_event=True,
    
    # Beat schedule for periodic tasks
    beat_schedule={
        # Update exchange rates every hour
        "update-exchange-rates": {
            "task": "backend.tasks.data_tasks.update_exchange_rates_task",
            "schedule": crontab(minute=0),  # Every hour
        },
        
        # Generate daily analytics reports
        "daily-analytics": {
            "task": "backend.tasks.analytics_tasks.generate_daily_reports",
            "schedule": crontab(hour=6, minute=0),  # 6 AM UTC
        },
        
        # Clean up old documents weekly
        "cleanup-documents": {
            "task": "backend.tasks.document_tasks.cleanup_old_documents",
            "schedule": crontab(hour=2, minute=0, day_of_week=0),  # Sunday 2 AM
        },
        
        # Refresh tariff data monthly
        "refresh-tariff-data": {
            "task": "backend.tasks.data_tasks.refresh_tariff_data_task",
            "schedule": crontab(hour=3, minute=0, day_of_month=1),  # 1st of month, 3 AM
        },
        
        # Calculate user metrics daily
        "user-metrics": {
            "task": "backend.tasks.analytics_tasks.calculate_user_metrics",
            "schedule": crontab(hour=7, minute=0),  # 7 AM UTC
        },
    },
)

# Task configuration
@celery_app.task(bind=True)
def debug_task(self):
    """Debug task for testing Celery setup."""
    print(f"Request: {self.request!r}")
    return "Celery is working!" 