"""Warehouse serializers"""
from rest_framework import serializers
from warehouses.models import Warehouse, WarehouseZone, StockTransfer, StockTransferItem


class WarehouseSerializer(serializers.ModelSerializer):
    utilization_percentage = serializers.FloatField(read_only=True)
    available_capacity = serializers.FloatField(read_only=True)
    manager_name = serializers.CharField(source='manager.get_full_name', read_only=True, allow_null=True)

    class Meta:
        model = Warehouse
        fields = [
            'id', 'code', 'name', 'type', 'description',
            'address_line1', 'address_line2', 'city', 'state', 'country', 'pincode',
            'latitude', 'longitude', 'total_capacity', 'capacity_unit',
            'current_utilization', 'utilization_percentage', 'available_capacity',
            'phone', 'email', 'manager', 'manager_name', 'is_active', 'is_default',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class WarehouseZoneSerializer(serializers.ModelSerializer):
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)

    class Meta:
        model = WarehouseZone
        fields = ['id', 'warehouse', 'warehouse_name', 'code', 'name', 'type', 'capacity',
                  'temperature_controlled', 'min_temperature', 'max_temperature', 'is_active']
        read_only_fields = ['id']


class StockTransferSerializer(serializers.ModelSerializer):
    from_warehouse_name = serializers.CharField(source='from_warehouse.name', read_only=True)
    to_warehouse_name = serializers.CharField(source='to_warehouse.name', read_only=True)
    requested_by_name = serializers.CharField(source='requested_by.get_full_name', read_only=True)

    class Meta:
        model = StockTransfer
        fields = [
            'id', 'transfer_number', 'from_warehouse', 'from_warehouse_name',
            'to_warehouse', 'to_warehouse_name', 'status', 'requested_by',
            'requested_by_name', 'approved_by', 'expected_date', 'completed_date',
            'notes', 'shipping_carrier', 'tracking_number', 'created_at',
        ]
        read_only_fields = ['id', 'transfer_number', 'created_at']
