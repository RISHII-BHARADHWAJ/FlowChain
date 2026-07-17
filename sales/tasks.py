"""Sales Celery tasks"""
from celery import shared_task
import logging

logger = logging.getLogger('scm')


@shared_task(name='sales.tasks.send_invoice_email')
def send_invoice_email(invoice_id):
    from notifications.tasks import send_invoice_email as _send
    _send.delay(invoice_id)


@shared_task(name='sales.tasks.process_overdue_invoices')
def process_overdue_invoices():
    from sales.models import Invoice
    from django.utils import timezone
    updated = Invoice.objects.filter(
        status__in=['sent', 'partial'],
        due_date__lt=timezone.now().date(),
    ).update(status='overdue')
    logger.info(f"Marked {updated} invoices as overdue")
    return updated


@shared_task(name='analytics.tasks.send_daily_analytics_report')
def send_daily_analytics_report():
    logger.info("Daily analytics report triggered")


@shared_task(name='purchases.tasks.check_pending_purchase_orders')
def check_pending_purchase_orders():
    from purchases.models import PurchaseOrder
    from django.utils import timezone
    overdue = PurchaseOrder.objects.filter(
        status__in=['approved', 'sent'],
        expected_delivery_date__lt=timezone.now().date(),
    )
    logger.info(f"Found {overdue.count()} overdue purchase orders")
    return overdue.count()


@shared_task(name='forecasting.tasks.update_all_forecasts')
def update_all_forecasts():
    logger.info("Forecast update triggered")


@shared_task(name='audit.tasks.cleanup_old_audit_logs')
def cleanup_old_audit_logs():
    from audit.models import AuditLog
    from django.utils import timezone
    import datetime
    cutoff = timezone.now() - datetime.timedelta(days=90)
    deleted, _ = AuditLog.objects.filter(created_at__lt=cutoff).delete()
    logger.info(f"Deleted {deleted} old audit logs")
    return deleted


@shared_task(name='reports.tasks.generate_weekly_reports')
def generate_weekly_reports():
    logger.info("Weekly reports generation triggered")


@shared_task(name='core.tasks.health_check')
def health_check():
    from django.db import connection
    connection.ensure_connection()
    return 'ok'
