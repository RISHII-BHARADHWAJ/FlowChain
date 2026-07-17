"""Inventory ViewSets"""
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend


class StockLevelViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['product', 'warehouse']
    search_fields = ['product__name', 'product__sku']
    ordering_fields = ['quantity_on_hand', 'total_value']

    def get_queryset(self):
        from inventory.models import StockLevel
        from django.db.models import F
        qs = StockLevel.objects.select_related('product', 'warehouse')
        filter_param = self.request.query_params.get('filter')
        if filter_param == 'low_stock':
            qs = qs.filter(quantity_on_hand__lte=F('product__reorder_point'), quantity_on_hand__gt=0)
        elif filter_param == 'out_of_stock':
            qs = qs.filter(quantity_on_hand__lte=0)
        return qs

    def get_serializer_class(self):
        from inventory.serializers import StockLevelSerializer
        return StockLevelSerializer


class StockMovementViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    filterset_fields = ['product', 'warehouse', 'movement_type']
    ordering = ['-created_at']

    def get_queryset(self):
        from inventory.models import StockMovement
        return StockMovement.objects.select_related('product', 'warehouse', 'performed_by')

    def get_serializer_class(self):
        from inventory.serializers import StockMovementSerializer
        return StockMovementSerializer


class BatchViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    filterset_fields = ['product', 'warehouse', 'status']

    def get_queryset(self):
        from inventory.models import Batch
        return Batch.objects.select_related('product', 'warehouse', 'supplier')

    def get_serializer_class(self):
        from inventory.serializers import BatchSerializer
        return BatchSerializer


class InventoryAdjustmentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    filterset_fields = ['status', 'warehouse', 'adjustment_type']

    def get_queryset(self):
        from inventory.models import InventoryAdjustment
        return InventoryAdjustment.objects.select_related('warehouse', 'adjusted_by').filter(deleted_at__isnull=True)

    def get_serializer_class(self):
        from inventory.serializers import InventoryAdjustmentSerializer
        return InventoryAdjustmentSerializer


class CycleCountingViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    filterset_fields = ['status', 'warehouse']

    def get_queryset(self):
        from inventory.models import CycleCounting
        return CycleCounting.objects.select_related('warehouse', 'assigned_to').filter(deleted_at__isnull=True)

    def get_serializer_class(self):
        from inventory.serializers import CycleCountingSerializer
        return CycleCountingSerializer
