from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from core.utils import paginate_queryset


@login_required
def warehouse_list(request):
    from warehouses.models import Warehouse
    qs = Warehouse.objects.select_related('manager').filter(deleted_at__isnull=True)

    # Filters
    search = request.GET.get('search', '')
    w_type = request.GET.get('type', '')
    status = request.GET.get('status', '')

    if search:
        qs = qs.filter(name__icontains=search) | qs.filter(code__icontains=search) | qs.filter(city__icontains=search)
    if w_type:
        qs = qs.filter(type=w_type)
    if status == 'active':
        qs = qs.filter(is_active=True)
    elif status == 'inactive':
        qs = qs.filter(is_active=False)

    warehouses, paginator = paginate_queryset(qs, request.GET.get('page', 1), 25)

    return render(request, 'warehouses/warehouse_list.html', {
        'warehouses': warehouses,
        'total_count': paginator.count,
    })
