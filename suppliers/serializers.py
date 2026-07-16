"""Supplier serializers"""
from rest_framework import serializers
from suppliers.models import Supplier, SupplierContact


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = [
            'id', 'code', 'name', 'legal_name', 'type', 'gst_number', 'pan_number',
            'email', 'phone', 'website', 'contact_person',
            'address_line1', 'address_line2', 'city', 'state', 'country', 'pincode',
            'payment_terms_days', 'credit_limit', 'currency', 'discount_percentage',
            'rating', 'total_orders', 'on_time_delivery_rate', 'quality_score',
            'outstanding_amount', 'advance_amount',
            'is_active', 'is_verified', 'is_preferred', 'blacklisted', 'notes',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class SupplierContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupplierContact
        fields = ['id', 'supplier', 'name', 'designation', 'email', 'phone', 'is_primary']
        read_only_fields = ['id']
