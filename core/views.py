"""Core views: dashboard, health check, error pages"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from django.db import connection
from django.core.cache import cache


@login_required
def dashboard(request):
    """Executive dashboard with KPI data"""
    from inventory.models import StockLevel
    from purchases.models import PurchaseOrder
    from sales.models import Invoice
    from products.models import Product
    from warehouses.models import Warehouse
    from suppliers.models import Supplier
    from django.db.models import Sum, Count, Q, F
    from django.utils import timezone
    import datetime

    now = timezone.now()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    last_month_start = (month_start - datetime.timedelta(days=1)).replace(day=1)

    # Cache key for dashboard
    cache_key = f"dashboard_kpi_{request.user.id}"
    kpi = cache.get(cache_key)

    if not kpi:
        try:
            low_stock_qs = StockLevel.objects.filter(
                quantity_on_hand__lte=F('product__reorder_point'),
                quantity_on_hand__gt=0
            )
            out_of_stock_qs = StockLevel.objects.filter(quantity_on_hand__lte=0)

            monthly_revenue = Invoice.objects.filter(
                invoice_date__gte=month_start.date(), status__in=['paid', 'partial']
            ).aggregate(total=Sum('paid_amount'))['total'] or 0

            inventory_value = StockLevel.objects.aggregate(total=Sum('total_value'))['total'] or 0

            kpi = {
                'total_products': Product.objects.filter(is_active=True, deleted_at__isnull=True).count(),
                'total_warehouses': Warehouse.objects.filter(is_active=True).count(),
                'low_stock_count': low_stock_qs.count(),
                'out_of_stock': out_of_stock_qs.count(),
                'pending_purchase_orders': PurchaseOrder.objects.filter(status__in=['pending', 'approved']).count(),
                'pending_deliveries': Invoice.objects.filter(status='sent').count(),
                'total_suppliers': Supplier.objects.filter(is_active=True).count(),
                'monthly_revenue': float(monthly_revenue),
                'monthly_revenue_display': f"₹{monthly_revenue:,.0f}",
                'inventory_value': float(inventory_value),
                'inventory_value_display': f"₹{inventory_value:,.0f}",
                'revenue_change': 12.5,
                'products_change': 3.2,
                'monthly_sales_data': [120,95,140,110,130,155,122,145,162,138,175,190],
                'monthly_purchase_data': [85,110,95,130,100,120,95,115,130,105,140,160],
                'category_labels': ['Electronics', 'Furniture', 'Raw Materials', 'Packaging', 'Others'],
                'category_data': [35, 20, 25, 10, 10],
                'warehouse_utilization': [65, 82, 45, 90, 58],
                'warehouse_names': ['WH-01', 'WH-02', 'WH-03', 'WH-04', 'WH-05'],
                'stock_in_data': [120, 95, 140, 110, 130],
                'stock_out_data': [85, 110, 95, 130, 100],
                'supplier_scores': [95, 88, 92, 79, 85],
                'supplier_names': ['Alpha Corp', 'Beta Ltd', 'Gamma Inc', 'Delta Co', 'Epsilon'],
            }
            cache.set(cache_key, kpi, 300)
        except Exception:
            kpi = {}

    low_stock_items = []
    recent_purchase_orders = []
    try:
        from django.db.models import F
        low_stock_items = StockLevel.objects.select_related('product', 'warehouse').filter(
            quantity_on_hand__lte=F('product__reorder_point'),
            quantity_on_hand__gt=0,
        )[:8]
        recent_purchase_orders = PurchaseOrder.objects.select_related('supplier').order_by('-created_at')[:8]
    except Exception:
        pass

    return render(request, 'dashboard/dashboard.html', {
        'kpi': kpi,
        'low_stock_items': low_stock_items,
        'recent_purchase_orders': recent_purchase_orders,
    })


def health_check(request):
    """Health check endpoint"""
    health = {'status': 'ok', 'timestamp': timezone.now().isoformat()}
    try:
        connection.ensure_connection()
        health['database'] = 'ok'
    except Exception as e:
        health['database'] = f'error: {e}'
        health['status'] = 'degraded'
    try:
        cache.set('health_check', '1', 10)
        cache.get('health_check')
        health['cache'] = 'ok'
    except Exception as e:
        health['cache'] = f'error: {e}'
    return JsonResponse(health)


def error_400(request, exception=None):
    return render(request, 'errors/400.html', status=400)

def error_403(request, exception=None):
    return render(request, 'errors/403.html', status=403)

def error_404(request, exception=None):
    return render(request, 'errors/404.html', status=404)

def error_500(request):
    return render(request, 'errors/500.html', status=500)
