"""
Notifications context processor - injects unread notification count
"""
from django.core.cache import cache


def notifications(request):
    if request.user.is_authenticated:
        cache_key = f"unread_notifications_{request.user.id}"
        count = cache.get(cache_key)
        if count is None:
            try:
                from notifications.models import Notification
                count = Notification.objects.filter(
                    recipient=request.user, is_read=False
                ).count()
                cache.set(cache_key, count, 60)  # Cache for 1 minute
            except Exception:
                count = 0
        return {'unread_notification_count': count}
    return {'unread_notification_count': 0}
