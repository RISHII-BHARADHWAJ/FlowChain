"""Purchase serializers"""
from rest_framework import serializers
from purchases.models import PurchaseRequisition, PurchaseOrder, GoodsReceiptNote, VendorInvoice


class PurchaseRequisitionSerializer(serializers.ModelSerializer):
    requested_by_name = serializers.CharField(source='requested_by.get_full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = PurchaseRequisition
        fields = [
            'id', 'pr_number', 'title', 'warehouse', 'requested_by', 'requested_by_name',
            'status', 'status_display', 'required_date', 'priority',
            'justification', 'estimated_cost', 'created_at',
        ]
        read_only_fields = ['id', 'pr_number', 'created_at', 'requested_by']


class PurchaseOrderSerializer(serializers.ModelSerializer):
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    balance_due = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)

    class Meta:
        model = PurchaseOrder
        fields = [
            'id', 'po_number', 'supplier', 'supplier_name', 'warehouse',
            'status', 'status_display', 'priority', 'order_date',
            'expected_delivery_date', 'actual_delivery_date',
            'subtotal', 'discount_amount', 'tax_amount', 'shipping_cost',
            'total_amount', 'paid_amount', 'balance_due',
            'created_by', 'approved_by', 'approved_at', 'payment_terms', 'notes',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'po_number', 'created_at', 'updated_at', 'created_by']


class GoodsReceiptNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsReceiptNote
        fields = [
            'id', 'grn_number', 'purchase_order', 'warehouse', 'supplier',
            'received_date', 'supplier_invoice_number', 'status',
            'received_by', 'notes', 'total_amount', 'created_at',
        ]
        read_only_fields = ['id', 'grn_number', 'created_at']


class VendorInvoiceSerializer(serializers.ModelSerializer):
    balance_due = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)

    class Meta:
        model = VendorInvoice
        fields = [
            'id', 'invoice_number', 'vendor_invoice_number', 'supplier',
            'purchase_order', 'invoice_date', 'due_date',
            'subtotal', 'tax_amount', 'total_amount', 'paid_amount', 'balance_due',
            'status', 'notes', 'created_at',
        ]
        read_only_fields = ['id', 'invoice_number', 'created_at']
