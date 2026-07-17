"""Purchases admin"""
from django.contrib import admin
from purchases.models import (
    PurchaseRequisition, PurchaseRequisitionItem,
    PurchaseOrder, PurchaseOrderItem,
    GoodsReceiptNote, GoodsReceiptNoteItem, VendorInvoice,
)


class PurchaseOrderItemInline(admin.TabularInline):
    model = PurchaseOrderItem
    extra = 0
    fields = ['product', 'quantity_ordered', 'quantity_received', 'unit_price', 'tax_rate', 'total_amount']
    readonly_fields = ['total_amount']


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ['po_number', 'supplier', 'warehouse', 'status', 'total_amount', 'paid_amount', 'order_date', 'created_by']
    list_filter = ['status', 'priority', 'warehouse']
    search_fields = ['po_number', 'supplier__name']
    inlines = [PurchaseOrderItemInline]
    readonly_fields = ['id', 'po_number', 'created_at', 'updated_at']


@admin.register(PurchaseRequisition)
class PurchaseRequisitionAdmin(admin.ModelAdmin):
    list_display = ['pr_number', 'title', 'warehouse', 'status', 'priority', 'requested_by', 'created_at']
    list_filter = ['status', 'priority']
    search_fields = ['pr_number', 'title']
    readonly_fields = ['id', 'created_at']


@admin.register(GoodsReceiptNote)
class GoodsReceiptNoteAdmin(admin.ModelAdmin):
    list_display = ['grn_number', 'purchase_order', 'supplier', 'warehouse', 'received_date', 'status']
    list_filter = ['status', 'warehouse']
    search_fields = ['grn_number', 'supplier__name']
    readonly_fields = ['id', 'created_at']


@admin.register(VendorInvoice)
class VendorInvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'supplier', 'invoice_date', 'due_date', 'total_amount', 'paid_amount', 'status']
    list_filter = ['status']
    search_fields = ['invoice_number', 'supplier__name']
