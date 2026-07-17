"""
Django Admin for Warehouse app
"""
from django.contrib import admin
from warehouses.models import Warehouse, WarehouseZone, WarehouseLocation, StockTransfer, StockTransferItem


class WarehouseZoneInline(admin.TabularInline):
    model = WarehouseZone
    extra = 0
    fields = ['code', 'name', 'type', 'capacity', 'is_active']


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'city', 'manager', 'total_capacity', 'current_utilization', 'is_active']
    list_filter = ['is_active', 'type', 'country']
    search_fields = ['code', 'name', 'city']
    inlines = [WarehouseZoneInline]
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(StockTransfer)
class StockTransferAdmin(admin.ModelAdmin):
    list_display = ['transfer_number', 'from_warehouse', 'to_warehouse', 'status', 'requested_by', 'created_at']
    list_filter = ['status']
    search_fields = ['transfer_number']
    readonly_fields = ['id', 'created_at']
