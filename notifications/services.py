"""Notification service layer"""
import logging
from django.conf import settings

logger = logging.getLogger('scm')


class NotificationService:
    """Central service for creating and dispatching notifications"""

    @classmethod
    def create(cls, recipient, notification_type, title, message,
                priority='medium', action_url='', related_model='', related_id='',
                send_email=False, send_sms=False, extra_data=None):
        from notifications.models import Notification
        notif = Notification.objects.create(
            recipient=recipient,
            notification_type=notification_type,
            title=title,
            message=message,
            priority=priority,
            action_url=action_url,
            related_model=related_model,
            related_id=str(related_id),
            extra_data=extra_data or {},
            sent_via_email=send_email,
            sent_via_sms=send_sms,
        )
        # Push via WebSocket
        cls._push_websocket(notif)
        # Invalidate cache
        cls._invalidate_cache(recipient)
        if send_email:
            from notifications.tasks import send_notification_email
            send_notification_email.delay(str(notif.id))
        return notif

    @classmethod
    def send_low_stock_alert(cls, stock_level):
        from accounts.models import User, UserRole
        managers = User.objects.filter(
            role__in=[UserRole.INVENTORY_MANAGER, UserRole.WAREHOUSE_MANAGER, UserRole.SUPER_ADMIN],
            is_active=True,
        )
        for manager in managers:
            cls.create(
                recipient=manager,
                notification_type='low_stock',
                title=f'Low Stock: {stock_level.product.name}',
                message=(f'{stock_level.product.name} (SKU: {stock_level.product.sku}) '
                         f'is at {stock_level.quantity_on_hand} units in {stock_level.warehouse.name}. '
                         f'Reorder point: {stock_level.product.reorder_point}'),
                priority='high',
                action_url=f'/inventory/?product={stock_level.product.id}',
                related_model='StockLevel',
                related_id=stock_level.id,
            )

    @classmethod
    def send_expiry_alert(cls, batch):
        from accounts.models import User, UserRole
        managers = User.objects.filter(
            role__in=[UserRole.INVENTORY_MANAGER, UserRole.WAREHOUSE_MANAGER, UserRole.SUPER_ADMIN],
            is_active=True,
        )
        for manager in managers:
            days = batch.days_to_expiry
            cls.create(
                recipient=manager,
                notification_type='expiry',
                title=f'Expiry Alert: {batch.product.name}',
                message=f'Batch {batch.batch_number} of {batch.product.name} expires in {days} days.',
                priority='high' if days <= 7 else 'medium',
                related_model='Batch',
                related_id=batch.id,
            )

    @classmethod
    def _push_websocket(cls, notif):
        try:
            from channels.layers import get_channel_layer
            from asgiref.sync import async_to_sync
            channel_layer = get_channel_layer()
            group_name = f'notifications_{notif.recipient.id}'
            async_to_sync(channel_layer.group_send)(group_name, {
                'type': 'notification_message',
                'id': str(notif.id),
                'title': notif.title,
                'message': notif.message,
                'notification_type': notif.notification_type,
                'priority': notif.priority,
                'action_url': notif.action_url,
                'created_at': notif.created_at.isoformat(),
            })
        except Exception as e:
            logger.debug(f"WebSocket push failed: {e}")

    @classmethod
    def _invalidate_cache(cls, user):
        from django.core.cache import cache
        cache.delete(f"unread_notifications_{user.id}")
