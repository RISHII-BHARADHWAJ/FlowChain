"""Audit admin"""
from django.contrib import admin
from audit.models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'model_name', 'object_repr', 'ip_address', 'is_successful', 'created_at']
    list_filter = ['action', 'model_name', 'is_successful']
    search_fields = ['user__email', 'object_repr', 'ip_address', 'request_path']
    readonly_fields = [f.name for f in AuditLog._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
