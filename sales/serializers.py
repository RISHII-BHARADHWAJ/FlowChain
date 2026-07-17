"""Sales serializers"""
from rest_framework import serializers
from sales.models import Customer, SalesOrder, Invoice, Payment, DeliveryNote


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = [
            'id', 'code', 'name', 'type', 'email', 'phone', 'gst_number',
            'address_line1', 'city', 'state', 'country', 'pincode',
            'credit_limit', 'payment_terms_days', 'outstanding_amount',
            'total_orders', 'total_revenue', 'is_active', 'notes', 'created_at',
        ]
        read_only_fields = ['id', 'created_at', 'total_orders', 'total_revenue']


class SalesOrderSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    balance_due = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)

    class Meta:
        model = SalesOrder
        fields = [
            'id', 'order_number', 'customer', 'customer_name', 'warehouse',
            'status', 'status_display', 'priority', 'order_date', 'required_date',
            'dispatch_date', 'delivery_date', 'subtotal', 'discount_amount',
            'tax_amount', 'shipping_cost', 'total_amount', 'paid_amount', 'balance_due',
            'salesperson', 'shipping_address', 'tracking_number', 'notes',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'order_number', 'created_at', 'updated_at', 'salesperson']


class InvoiceSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    balance_due = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)

    class Meta:
        model = Invoice
        fields = [
            'id', 'invoice_number', 'sales_order', 'customer', 'customer_name',
            'invoice_date', 'due_date', 'status', 'status_display',
            'subtotal', 'cgst_amount', 'sgst_amount', 'igst_amount',
            'discount_amount', 'total_amount', 'paid_amount', 'balance_due', 'is_overdue',
            'created_by', 'pdf_file', 'notes', 'created_at',
        ]
        read_only_fields = ['id', 'invoice_number', 'created_at', 'created_by']


class PaymentSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.name', read_only=True)

    class Meta:
        model = Payment
        fields = [
            'id', 'payment_number', 'invoice', 'customer', 'customer_name',
            'amount', 'payment_date', 'payment_method', 'reference_number',
            'notes', 'received_by', 'created_at',
        ]
        read_only_fields = ['id', 'payment_number', 'created_at', 'received_by']


class DeliveryNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryNote
        fields = [
            'id', 'dn_number', 'sales_order', 'customer', 'dispatch_date',
            'expected_delivery_date', 'actual_delivery_date', 'status',
            'shipping_carrier', 'tracking_number', 'notes', 'created_at',
        ]
        read_only_fields = ['id', 'dn_number', 'created_at']
