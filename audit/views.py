"""Audit views"""
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from audit.models import AuditLog
from accounts.permissions import IsSuperAdmin


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated, IsSuperAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['action', 'model_name', 'user', 'is_successful']
    search_fields = ['object_repr', 'user__email', 'request_path']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        return AuditLog.objects.select_related('user').all()

    def get_serializer_class(self):
        from audit.serializers import AuditLogSerializer
        return AuditLogSerializer
