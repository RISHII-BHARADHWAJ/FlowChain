"""Celery tasks for inventory management"""
import logging
from celery import shared_task
from django.utils import timezone
from django.conf import settings

logger = logging.getLogger('scm')


@shared_task(name='inventory.tasks.check_low_stock_levels', bind=True, max_retries=3)
def check_low_stock_levels(self):
    """Check all products for low stock and send alerts"""
    try:
        from inventory.models import StockLevel
        from notifications.services import NotificationService

        low_stock_items = StockLevel.objects.select_related(
            'product', 'warehouse'
        ).filter(
            quantity_on_hand__lte=models.F('product__reorder_point'),
            quantity_on_hand__gt=0,
        )

        for stock in low_stock_items:
            NotificationService.send_low_stock_alert(stock)

        logger.info(f"Low stock check complete. Found {low_stock_items.count()} items.")
        return f"Checked {low_stock_items.count()} low stock items"
    except Exception as exc:
        logger.error(f"Low stock check failed: {exc}")
        raise self.retry(exc=exc, countdown=60)


@shared_task(name='inventory.tasks.check_expiring_products')
def check_expiring_products():
    """Alert for products expiring within 30 days"""
    from inventory.models import Batch
    from notifications.services import NotificationService

    expiry_threshold = timezone.now().date() + timezone.timedelta(days=30)
    expiring_batches = Batch.objects.select_related('product', 'warehouse').filter(
        expiry_date__lte=expiry_threshold,
        expiry_date__gte=timezone.now().date(),
        status='active',
        quantity__gt=0,
    )

    for batch in expiring_batches:
        NotificationService.send_expiry_alert(batch)

    logger.info(f"Expiry check: {expiring_batches.count()} batches near expiry")
    return f"{expiring_batches.count()} batches near expiry"


@shared_task(name='inventory.tasks.create_daily_inventory_snapshot')
def create_daily_inventory_snapshot():
    """Create a daily snapshot of all inventory levels"""
    from inventory.models import StockLevel
    import json

    today = timezone.now().date()
    snapshot_data = list(StockLevel.objects.select_related(
        'product', 'warehouse'
    ).values(
        'product__sku', 'product__name', 'warehouse__code',
        'quantity_on_hand', 'quantity_reserved', 'average_cost', 'total_value'
    ))

    logger.info(f"Daily snapshot created for {today}: {len(snapshot_data)} records")
    return f"Snapshot created: {len(snapshot_data)} records"
