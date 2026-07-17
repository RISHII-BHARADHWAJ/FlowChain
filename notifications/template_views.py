from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required


@login_required
def notification_list(request):
    from notifications.models import Notification
    notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')[:50]
    return render(request, 'notifications/notification_list.html', {
        'notifications': notifications
    })


@login_required
def mark_all_read(request):
    from notifications.models import Notification
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    return redirect('notifications:notification_list')
