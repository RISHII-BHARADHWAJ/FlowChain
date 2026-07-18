"""Analytics views"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count, Avg, F, Q
from django.utils import timezone
import datetime


class AnalyticsDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from inventory.models import StockLevel
        from sales.models import Invoice, SalesOrder
        from purchases.models import PurchaseOrder

        period = request.query_params.get('period', 'month')
        now = timezone.now()

        if period == 'month':
            start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        elif period == 'quarter':
            month = ((now.month - 1) // 3) * 3 + 1
            start = now.replace(month=month, day=1, hour=0, minute=0, second=0)
        else:
            start = now.replace(month=1, day=1, hour=0, minute=0, second=0)

        revenue = Invoice.objects.filter(
            invoice_date__gte=start.date(), status__in=['paid', 'partial']
        ).aggregate(total=Sum('paid_amount'))['total'] or 0

        purchase_cost = PurchaseOrder.objects.filter(
            order_date__gte=start.date(), status__in=['completed', 'approved']
        ).aggregate(total=Sum('total_amount'))['total'] or 0

        inventory_value = StockLevel.objects.aggregate(total=Sum('total_value'))['total'] or 0

        return Response({
            'period': period,
            'revenue': float(revenue),
            'purchase_cost': float(purchase_cost),
            'gross_profit': float(revenue - purchase_cost),
            'inventory_value': float(inventory_value),
            'generated_at': now.isoformat(),
        })


class ABCAnalysisView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from products.models import Product
        from inventory.models import StockLevel
        from django.db.models import Sum

        products = StockLevel.objects.select_related('product').values(
            'product__id', 'product__name', 'product__sku'
        ).annotate(
            total_value=Sum('total_value')
        ).order_by('-total_value')

        total = sum(p['total_value'] or 0 for p in products)
        cumulative = 0
        results = []
        for p in products:
            val = p['total_value'] or 0
            cumulative += val
            pct = (cumulative / total * 100) if total else 0
            category = 'A' if pct <= 80 else ('B' if pct <= 95 else 'C')
            results.append({
                'product_id': str(p['product__id']),
                'product_name': p['product__name'],
                'sku': p['product__sku'],
                'total_value': float(val),
                'cumulative_percentage': round(pct, 2),
                'abc_category': category,
            })

        return Response({'analysis': results, 'total_value': float(total)})


class InventoryTurnoverView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from inventory.models import StockLevel, StockMovement
        from django.db.models import Sum

        days = int(request.query_params.get('days', 365))
        start = timezone.now() - datetime.timedelta(days=days)

        cogs = StockMovement.objects.filter(
            movement_type='sale', created_at__gte=start
        ).aggregate(total=Sum('total_cost'))['total'] or 0

        avg_inventory = StockLevel.objects.aggregate(avg=Avg('total_value'))['avg'] or 0
        turnover = float(cogs) / float(avg_inventory) if avg_inventory else 0

        return Response({
            'period_days': days,
            'cogs': float(cogs),
            'average_inventory_value': float(avg_inventory),
            'inventory_turnover_ratio': round(turnover, 2),
            'days_inventory_outstanding': round(days / turnover, 1) if turnover else 0,
        })
