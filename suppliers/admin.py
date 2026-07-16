"""Supplier admin"""
from django.contrib import admin
from suppliers.models import Supplier, SupplierContact, SupplierDocument, SupplierPerformanceRecord


class SupplierContactInline(admin.TabularInline):
    model = SupplierContact
    extra = 0
    fields = ['name', 'designation', 'email', 'phone', 'is_primary']


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'type', 'city', 'rating', 'is_active', 'is_preferred', 'blacklisted']
    list_filter = ['type', 'is_active', 'is_preferred', 'blacklisted', 'is_verified']
    search_fields = ['code', 'name', 'gst_number', 'email']
    inlines = [SupplierContactInline]
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(SupplierPerformanceRecord)
class SupplierPerformanceAdmin(admin.ModelAdmin):
    list_display = ['supplier', 'period', 'overall_score', 'on_time_delivery', 'quality_score']
    list_filter = ['period']
    search_fields = ['supplier__name']
