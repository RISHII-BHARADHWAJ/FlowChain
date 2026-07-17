"""Audit serializers"""
from rest_framework import serializers
from audit.models import AuditLog


class AuditLogSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True, allow_null=True)
    action_display = serializers.CharField(source='get_action_display', read_only=True)

    class Meta:
        model = AuditLog
        fields = [
            'id', 'user', 'user_name', 'action', 'action_display',
            'model_name', 'object_id', 'object_repr', 'changes',
            'ip_address', 'request_method', 'request_path',
            'response_status', 'is_successful', 'created_at',
        ]
        read_only_fields = fields
