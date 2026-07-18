"""Forecasting serializers"""
from rest_framework import serializers
from forecasting.models import DemandForecast, StockForecastSnapshot


class DemandForecastSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)

    class Meta:
        model = DemandForecast
        fields = [
            'id', 'product', 'product_name', 'warehouse', 'warehouse_name',
            'forecast_date', 'period_type', 'predicted_demand',
            'predicted_demand_lower', 'predicted_demand_upper',
            'actual_demand', 'forecast_accuracy', 'model_used',
            'confidence_level', 'safety_stock', 'reorder_quantity', 'lead_time_days',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']


class StockForecastSnapshotSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = StockForecastSnapshot
        fields = [
            'id', 'product', 'product_name', 'warehouse', 'snapshot_date',
            'projected_stock', 'projected_demand', 'projected_reorder',
            'stockout_risk', 'suggested_order_qty', 'created_at',
        ]
