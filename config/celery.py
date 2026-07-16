"""
Celery configuration for FlowChain Platform
"""
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

app = Celery('scm')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# ===================== PERIODIC TASKS =====================
app.conf.beat_schedule = {
    # Check low stock every 2 hours
    'check-low-stock': {
        'task': 'inventory.tasks.check_low_stock_levels',
        'schedule': crontab(minute=0, hour='*/2'),
    },
    # Generate daily inventory snapshot at midnight
    'daily-inventory-snapshot': {
        'task': 'inventory.tasks.create_daily_inventory_snapshot',
        'schedule': crontab(minute=0, hour=0),
    },
    # Check expired products every day at 8 AM
    'check-expiry': {
        'task': 'inventory.tasks.check_expiring_products',
        'schedule': crontab(minute=0, hour=8),
    },
    # Send daily analytics report at 9 AM
    'daily-analytics-report': {
        'task': 'analytics.tasks.send_daily_analytics_report',
        'schedule': crontab(minute=0, hour=9),
    },
    # Update stock forecasts weekly
    'update-forecasts': {
        'task': 'forecasting.tasks.update_all_forecasts',
        'schedule': crontab(minute=0, hour=2, day_of_week=1),
    },
    # Process pending purchase orders
    'check-purchase-orders': {
        'task': 'purchases.tasks.check_pending_purchase_orders',
        'schedule': crontab(minute=0, hour='*/4'),
    },
    # Clean up old audit logs (keep 90 days)
    'cleanup-audit-logs': {
        'task': 'audit.tasks.cleanup_old_audit_logs',
        'schedule': crontab(minute=0, hour=3, day_of_week=0),
    },
    # Generate weekly reports
    'weekly-reports': {
        'task': 'reports.tasks.generate_weekly_reports',
        'schedule': crontab(minute=0, hour=7, day_of_week=1),
    },
    # Health check
    'health-check': {
        'task': 'core.tasks.health_check',
        'schedule': crontab(minute='*/15'),
    },
}


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
