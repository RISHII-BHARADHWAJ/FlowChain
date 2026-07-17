"""Stub ViewSets for all remaining apps"""
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend


# ── WAREHOUSES ──────────────────────────────────────
class WarehouseViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['name', 'code', 'city']
    filterset_fields = ['is_active', 'type']

    def get_queryset(self):
        from warehouses.models import Warehouse
        return Warehouse.objects.select_related('manager').filter(deleted_at__isnull=True)

    def get_serializer_class(self):
        from warehouses.serializers import WarehouseSerializer
        return WarehouseSerializer


class WarehouseZoneViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        from warehouses.models import WarehouseZone
        return WarehouseZone.objects.select_related('warehouse').filter(deleted_at__isnull=True)

    def get_serializer_class(self):
        from warehouses.serializers import WarehouseZoneSerializer
        return WarehouseZoneSerializer


class StockTransferViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    filterset_fields = ['status', 'from_warehouse', 'to_warehouse']

    def get_queryset(self):
        from warehouses.models import StockTransfer
        return StockTransfer.objects.select_related(
            'from_warehouse', 'to_warehouse', 'requested_by'
        ).filter(deleted_at__isnull=True)

    def get_serializer_class(self):
        from warehouses.serializers import StockTransferSerializer
        return StockTransferSerializer
