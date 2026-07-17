"""
Django Admin for Inventory, Suppliers, Purchases, Sales, Audit
"""
# inventory/admin.py
from django.contrib import admin
from inventory.models import StockLevel, StockMovement, Batch, InventoryAdjustment, CycleCounting


@admin.register(StockLevel)
class StockLevelAdmin(admin.ModelAdmin):
    list_display = ['product', 'warehouse', 'quantity_on_hand', 'quantity_reserved', 'average_cost', 'total_value', 'last_movement_at']
    list_filter = ['warehouse']
    search_fields = ['product__sku', 'product__name']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ['product', 'warehouse', 'movement_type', 'quantity', 'quantity_before', 'quantity_after', 'performed_by', 'created_at']
    list_filter = ['movement_type', 'warehouse']
    search_fields = ['product__sku', 'reference_number']
    readonly_fields = ['id', 'created_at']


@admin.register(Batch)
class BatchAdmin(admin.ModelAdmin):
    list_display = ['product', 'warehouse', 'batch_number', 'lot_number', 'expiry_date', 'quantity', 'status']
    list_filter = ['status', 'warehouse']
    search_fields = ['batch_number', 'lot_number', 'product__sku']


@admin.register(InventoryAdjustment)
class InventoryAdjustmentAdmin(admin.ModelAdmin):
    list_display = ['adjustment_number', 'warehouse', 'adjustment_type', 'status', 'adjusted_by', 'created_at']
    list_filter = ['status', 'adjustment_type']
    readonly_fields = ['id', 'created_at']


@admin.register(CycleCounting)
class CycleCountingAdmin(admin.ModelAdmin):
    list_display = ['count_number', 'warehouse', 'count_type', 'status', 'scheduled_date', 'assigned_to']
    list_filter = ['status', 'count_type']
