"""Notification serializer"""
from rest_framework import serializers
from notifications.models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    notification_type_display = serializers.CharField(source='get_notification_type_display', read_only=True)

    class Meta:
        model = Notification
        fields = [
            'id', 'notification_type', 'notification_type_display', 'title', 'message',
            'priority', 'is_read', 'read_at', 'action_url', 'related_model', 'related_id',
            'sent_via_email', 'sent_via_sms', 'created_at',
        ]
        read_only_fields = fields
