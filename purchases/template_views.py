from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from core.utils import paginate_queryset


@login_required
def purchase_order_list(request):
    from purchases.models import PurchaseOrder
    from suppliers.models import Supplier
    qs = PurchaseOrder.objects.select_related('supplier', 'warehouse').filter(deleted_at__isnull=True)

    # Filters
    search = request.GET.get('search', '')
    supplier_id = request.GET.get('supplier', '')
    status = request.GET.get('status', '')

    if search:
        qs = qs.filter(po_number__icontains=search)
    if supplier_id:
        qs = qs.filter(supplier_id=supplier_id)
    if status:
        qs = qs.filter(status=status)

    orders, paginator = paginate_queryset(qs, request.GET.get('page', 1), 25)
    suppliers = Supplier.objects.filter(deleted_at__isnull=True).order_by('name')

    return render(request, 'purchases/purchase_order_list.html', {
        'orders': orders,
        'suppliers': suppliers,
        'total_count': paginator.count,
    })
