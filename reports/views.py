"""Reports ViewSet and Notifications ViewSet"""
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend


class ReportViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def inventory(self, request):
        from inventory.models import StockLevel
        from django.db.models import Sum
        data = StockLevel.objects.select_related('product', 'warehouse').values(
            'product__sku', 'product__name', 'warehouse__name',
            'quantity_on_hand', 'average_cost', 'total_value'
        )
        return Response({'report': 'inventory', 'data': list(data)})

    @action(detail=False, methods=['get'])
    def sales(self, request):
        from sales.models import Invoice
        from django.db.models import Sum
        data = Invoice.objects.values('status').annotate(
            count=Sum('id'), total=Sum('total_amount'), paid=Sum('paid_amount')
        )
        return Response({'report': 'sales', 'data': list(data)})

    @action(detail=False, methods=['get'])
    def purchase(self, request):
        from purchases.models import PurchaseOrder
        data = PurchaseOrder.objects.select_related('supplier').values(
            'supplier__name', 'status'
        ).annotate(count=Sum('id'), total=Sum('total_amount'))
        return Response({'report': 'purchase', 'data': list(data)})
