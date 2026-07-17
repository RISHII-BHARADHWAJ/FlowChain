"""Sales admin"""
from django.contrib import admin
from sales.models import Customer, SalesOrder, SalesOrderItem, Invoice, Payment, DeliveryNote, SalesReturn


class SalesOrderItemInline(admin.TabularInline):
    model = SalesOrderItem
    extra = 0
    fields = ['product', 'quantity_ordered', 'quantity_dispatched', 'unit_price', 'tax_rate', 'total_amount']
    readonly_fields = ['total_amount']


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'type', 'city', 'total_orders', 'total_revenue', 'is_active']
    list_filter = ['type', 'is_active']
    search_fields = ['code', 'name', 'email', 'gst_number']
    readonly_fields = ['id', 'created_at']


@admin.register(SalesOrder)
class SalesOrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'customer', 'warehouse', 'status', 'total_amount', 'order_date', 'salesperson']
    list_filter = ['status', 'priority', 'warehouse']
    search_fields = ['order_number', 'customer__name']
    inlines = [SalesOrderItemInline]
    readonly_fields = ['id', 'order_number', 'created_at']


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'customer', 'invoice_date', 'due_date', 'total_amount', 'paid_amount', 'status']
    list_filter = ['status']
    search_fields = ['invoice_number', 'customer__name']
    readonly_fields = ['id', 'invoice_number', 'created_at']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['payment_number', 'customer', 'invoice', 'amount', 'payment_method', 'payment_date', 'received_by']
    list_filter = ['payment_method']
    search_fields = ['payment_number', 'customer__name']
    readonly_fields = ['id', 'payment_number', 'created_at']
