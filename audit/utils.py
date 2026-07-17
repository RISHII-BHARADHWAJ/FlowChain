"""Audit utility for logging actions"""
from audit.models import AuditLog


def log_action(user, action, obj=None, description='', request=None, changes=None):
    """Utility to create audit log entries"""
    try:
        kwargs = {
            'user': user,
            'action': action,
            'extra_data': {'description': description},
        }
        if obj is not None:
            kwargs['model_name'] = obj.__class__.__name__
            kwargs['object_id'] = str(obj.pk)
            kwargs['object_repr'] = str(obj)[:500]
        if changes:
            kwargs['changes'] = changes
        if request:
            kwargs['ip_address'] = _get_ip(request)
            kwargs['user_agent'] = request.META.get('HTTP_USER_AGENT', '')[:500]
        AuditLog.objects.create(**kwargs)
    except Exception:
        pass


def _get_ip(request):
    xff = request.META.get('HTTP_X_FORWARDED_FOR')
    return xff.split(',')[0].strip() if xff else request.META.get('REMOTE_ADDR')
