from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from core.utils import paginate_queryset


@login_required
def supplier_list(request):
    from suppliers.models import Supplier
    qs = Supplier.objects.filter(deleted_at__isnull=True)

    # Filters
    search = request.GET.get('search', '')
    supplier_type = request.GET.get('type', '')

    if search:
        qs = qs.filter(name__icontains=search) | qs.filter(code__icontains=search) | qs.filter(email__icontains=search)
    if supplier_type:
        qs = qs.filter(type=supplier_type)

    suppliers, paginator = paginate_queryset(qs, request.GET.get('page', 1), 25)

    return render(request, 'suppliers/supplier_list.html', {
        'suppliers': suppliers,
        'total_count': paginator.count,
    })
