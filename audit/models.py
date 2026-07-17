"""Audit log models"""
import uuid
from django.db import models
from core.models import TimeStampedModel


class AuditLog(TimeStampedModel):
    """Tracks every significant action in the system"""
    ACTION_TYPES = [
        ('login','Login'),('logout','Logout'),
        ('create','Create'),('update','Update'),('delete','Delete'),
        ('approve','Approve'),('reject','Reject'),
        ('stock_in','Stock In'),('stock_out','Stock Out'),
        ('transfer','Transfer'),('adjustment','Adjustment'),
        ('export','Export'),('import','Import'),
        ('email','Email Sent'),('report','Report Generated'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('accounts.User', null=True, on_delete=models.SET_NULL, related_name='audit_logs')
    action = models.CharField(max_length=30, choices=ACTION_TYPES, db_index=True)
    model_name = models.CharField(max_length=100, blank=True, db_index=True)
    object_id = models.CharField(max_length=100, blank=True, db_index=True)
    object_repr = models.CharField(max_length=500, blank=True)
    changes = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    request_method = models.CharField(max_length=10, blank=True)
    request_path = models.CharField(max_length=500, blank=True)
    response_status = models.PositiveIntegerField(null=True, blank=True)
    extra_data = models.JSONField(default=dict, blank=True)
    is_successful = models.BooleanField(default=True)
    error_message = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Audit Log'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user','action','created_at']),
            models.Index(fields=['model_name','object_id']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        user = self.user.get_full_name() if self.user else 'System'
        return f"{user} | {self.action} | {self.model_name} | {self.created_at}"
