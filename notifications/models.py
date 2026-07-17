"""Notification models"""
import uuid
from django.db import models
from core.models import TimeStampedModel


class Notification(TimeStampedModel):
    NOTIFICATION_TYPES = [
        ('low_stock','Low Stock Alert'),
        ('out_of_stock','Out of Stock'),
        ('expiry','Product Expiry Warning'),
        ('po_approval','PO Approval Required'),
        ('po_approved','PO Approved'),
        ('po_rejected','PO Rejected'),
        ('grn_received','GRN Received'),
        ('transfer_request','Transfer Request'),
        ('transfer_approved','Transfer Approved'),
        ('payment_due','Payment Due'),
        ('order_delivered','Order Delivered'),
        ('system','System Alert'),
        ('report','Report Ready'),
    ]
    PRIORITY = [('low','Low'),('medium','Medium'),('high','High'),('critical','Critical')]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipient = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES, db_index=True)
    title = models.CharField(max_length=255)
    message = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITY, default='medium')
    is_read = models.BooleanField(default=False, db_index=True)
    read_at = models.DateTimeField(null=True, blank=True)
    action_url = models.CharField(max_length=500, blank=True)
    related_model = models.CharField(max_length=100, blank=True)
    related_id = models.CharField(max_length=100, blank=True)
    extra_data = models.JSONField(default=dict, blank=True)
    sent_via_email = models.BooleanField(default=False)
    sent_via_sms = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient','is_read','created_at']),
        ]

    def __str__(self):
        return f"{self.notification_type}: {self.title}"

    def mark_as_read(self):
        from django.utils import timezone
        self.is_read = True
        self.read_at = timezone.now()
        self.save(update_fields=['is_read','read_at'])
