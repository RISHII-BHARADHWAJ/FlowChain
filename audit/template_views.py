from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from core.utils import paginate_queryset


@login_required
def audit_list(request):
    from audit.models import AuditLog
    qs = AuditLog.objects.select_related('user').order_by('-created_at')

    # Filters
    search = request.GET.get('search', '')
    action_type = request.GET.get('action_type', '')

    if search:
        qs = qs.filter(object_repr__icontains=search) | qs.filter(user__email__icontains=search)
    if action_type:
        qs = qs.filter(action_type=action_type)

    logs, paginator = paginate_queryset(qs, request.GET.get('page', 1), 25)

    return render(request, 'audit/audit_list.html', {
        'logs': logs,
        'total_count': paginator.count,
    })
