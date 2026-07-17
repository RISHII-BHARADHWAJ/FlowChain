from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from core.utils import paginate_queryset


@login_required
def inventory_list(request):
    from inventory.models import StockLevel
    from warehouses.models import Warehouse
    qs = StockLevel.objects.select_related('product', 'warehouse').filter(product__deleted_at__isnull=True)

    # Filters
    search = request.GET.get('search', '')
    warehouse_id = request.GET.get('warehouse', '')
    stock_status = request.GET.get('status', '')

    if search:
        qs = qs.filter(product__name__icontains=search) | qs.filter(product__sku__icontains=search)
    if warehouse_id:
        qs = qs.filter(warehouse_id=warehouse_id)
    if stock_status == 'low':
        qs = qs.filter(quantity_on_hand__lte=10) # Simple threshold
    elif stock_status == 'out':
        qs = qs.filter(quantity_on_hand=0)

    stock_levels, paginator = paginate_queryset(qs, request.GET.get('page', 1), 25)
    warehouses = Warehouse.objects.filter(is_active=True).order_by('name')

    return render(request, 'inventory/inventory_list.html', {
        'stock_levels': stock_levels,
        'warehouses': warehouses,
        'total_count': paginator.count,
    })
