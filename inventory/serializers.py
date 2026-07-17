"""Inventory serializers"""
from rest_framework import serializers
from inventory.models import StockLevel, StockMovement, Batch, InventoryAdjustment, CycleCounting


class StockLevelSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_sku = serializers.CharField(source='product.sku', read_only=True)
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)
    quantity_available = serializers.DecimalField(max_digits=15, decimal_places=3, read_only=True)
    is_low_stock = serializers.BooleanField(read_only=True)
    is_out_of_stock = serializers.BooleanField(read_only=True)

    class Meta:
        model = StockLevel
        fields = [
            'id', 'product', 'product_name', 'product_sku',
            'warehouse', 'warehouse_name', 'quantity_on_hand',
            'quantity_reserved', 'quantity_in_transit', 'quantity_on_order',
            'quantity_available', 'average_cost', 'total_value',
            'is_low_stock', 'is_out_of_stock', 'last_movement_at',
        ]


class StockMovementSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_sku = serializers.CharField(source='product.sku', read_only=True)
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)
    performed_by_name = serializers.CharField(source='performed_by.get_full_name', read_only=True, allow_null=True)

    class Meta:
        model = StockMovement
        fields = [
            'id', 'product', 'product_name', 'product_sku',
            'warehouse', 'warehouse_name', 'movement_type',
            'reference_number', 'quantity', 'quantity_before', 'quantity_after',
            'unit_cost', 'total_cost', 'performed_by', 'performed_by_name',
            'notes', 'created_at',
        ]


class BatchSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    days_to_expiry = serializers.IntegerField(read_only=True, allow_null=True)

    class Meta:
        model = Batch
        fields = [
            'id', 'product', 'product_name', 'warehouse', 'batch_number', 'lot_number',
            'manufacture_date', 'expiry_date', 'quantity', 'unit_cost',
            'supplier', 'status', 'is_expired', 'days_to_expiry', 'created_at',
        ]


class InventoryAdjustmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryAdjustment
        fields = [
            'id', 'adjustment_number', 'warehouse', 'adjustment_type',
            'status', 'reason', 'adjusted_by', 'approved_by', 'approved_at', 'created_at',
        ]
        read_only_fields = ['id', 'adjustment_number', 'created_at']


class CycleCountingSerializer(serializers.ModelSerializer):
    class Meta:
        model = CycleCounting
        fields = [
            'id', 'count_number', 'warehouse', 'count_type',
            'scheduled_date', 'completed_date', 'status',
            'assigned_to', 'variance_value', 'notes', 'created_at',
        ]
        read_only_fields = ['id', 'count_number', 'created_at']
