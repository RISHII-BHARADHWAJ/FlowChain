"""Audit middleware to log all requests"""
import json
import logging
from audit.models import AuditLog

logger = logging.getLogger('scm')


class AuditLogMiddleware:
    """Middleware to capture request details for audit logging"""

    EXCLUDED_PATHS = ['/health/', '/static/', '/media/', '/__debug__/', '/api/schema/']
    EXCLUDED_METHODS = ['GET', 'HEAD', 'OPTIONS']

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Skip excluded paths and read-only methods
        if self._should_skip(request):
            return response

        # Log write operations
        if request.user.is_authenticated:
            try:
                self._create_log(request, response)
            except Exception as e:
                logger.error(f"Audit log error: {e}")

        return response

    def _should_skip(self, request):
        for path in self.EXCLUDED_PATHS:
            if request.path.startswith(path):
                return True
        return request.method in self.EXCLUDED_METHODS

    def _create_log(self, request, response):
        AuditLog.objects.create(
            user=request.user,
            action=self._infer_action(request),
            ip_address=self._get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
            request_method=request.method,
            request_path=request.path[:500],
            response_status=response.status_code,
            is_successful=response.status_code < 400,
        )

    def _infer_action(self, request):
        method_map = {
            'POST': 'create',
            'PUT': 'update',
            'PATCH': 'update',
            'DELETE': 'delete',
        }
        return method_map.get(request.method, 'create')

    def _get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')
