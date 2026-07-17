from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from core.utils import paginate_queryset


@login_required
def sales_order_list(request):
    from sales.models import SalesOrder, Customer
    qs = SalesOrder.objects.select_related('customer').filter(deleted_at__isnull=True)

    # Filters
    search = request.GET.get('search', '')
    customer_id = request.GET.get('customer', '')
    status = request.GET.get('status', '')

    if search:
        qs = qs.filter(order_number__icontains=search)
    if customer_id:
        qs = qs.filter(customer_id=customer_id)
    if status:
        qs = qs.filter(status=status)

    orders, paginator = paginate_queryset(qs, request.GET.get('page', 1), 25)
    customers = Customer.objects.filter(deleted_at__isnull=True).order_by('name')

    return render(request, 'sales/sales_order_list.html', {
        'orders': orders,
        'customers': customers,
        'total_count': paginator.count,
    })


@login_required
def invoice_list(request):
    from sales.models import Invoice, Customer
    qs = Invoice.objects.select_related('sales_order__customer').filter(deleted_at__isnull=True)

    search = request.GET.get('search', '')
    status = request.GET.get('status', '')

    if search:
        qs = qs.filter(invoice_number__icontains=search) | qs.filter(sales_order__order_number__icontains=search)
    if status:
        qs = qs.filter(status=status)

    invoices, paginator = paginate_queryset(qs, request.GET.get('page', 1), 25)

    return render(request, 'sales/invoice_list.html', {
        'invoices': invoices,
        'total_count': paginator.count,
    })

