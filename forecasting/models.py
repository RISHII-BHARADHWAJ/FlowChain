"""Forecasting models using ML"""
import uuid
from django.db import models
from core.models import BaseModel, TimeStampedModel


class DemandForecast(BaseModel):
    """ML-based demand forecast per product"""
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, related_name='forecasts')
    warehouse = models.ForeignKey('warehouses.Warehouse', on_delete=models.CASCADE)
    forecast_date = models.DateField(db_index=True)
    period_type = models.CharField(max_length=20, choices=[
        ('daily','Daily'),('weekly','Weekly'),('monthly','Monthly'),
    ], default='monthly')
    predicted_demand = models.DecimalField(max_digits=15, decimal_places=3)
    predicted_demand_lower = models.DecimalField(max_digits=15, decimal_places=3, default=0)
    predicted_demand_upper = models.DecimalField(max_digits=15, decimal_places=3, default=0)
    actual_demand = models.DecimalField(max_digits=15, decimal_places=3, null=True, blank=True)
    forecast_accuracy = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    model_used = models.CharField(max_length=50, default='prophet')
    confidence_level = models.DecimalField(max_digits=5, decimal_places=2, default=95)
    safety_stock = models.DecimalField(max_digits=15, decimal_places=3, default=0)
    reorder_quantity = models.DecimalField(max_digits=15, decimal_places=3, default=0)
    lead_time_days = models.PositiveIntegerField(default=7)
    parameters = models.JSONField(default=dict, blank=True)

    class Meta:
        unique_together = ['product','warehouse','forecast_date','period_type']
        ordering = ['-forecast_date']


class StockForecastSnapshot(BaseModel):
    """Future inventory level projections"""
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE)
    warehouse = models.ForeignKey('warehouses.Warehouse', on_delete=models.CASCADE)
    snapshot_date = models.DateField()
    projected_stock = models.DecimalField(max_digits=15, decimal_places=3)
    projected_demand = models.DecimalField(max_digits=15, decimal_places=3)
    projected_reorder = models.BooleanField(default=False)
    stockout_risk = models.CharField(max_length=20, choices=[
        ('none','None'),('low','Low'),('medium','Medium'),('high','High'),('critical','Critical'),
    ], default='none')
    suggested_order_qty = models.DecimalField(max_digits=15, decimal_places=3, default=0)

    class Meta:
        unique_together = ['product','warehouse','snapshot_date']
        ordering = ['snapshot_date']


class ForecastModel(BaseModel):
    """Trained ML model metadata"""
    name = models.CharField(max_length=100)
    algorithm = models.CharField(max_length=50)
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, related_name='forecast_models')
    warehouse = models.ForeignKey('warehouses.Warehouse', on_delete=models.CASCADE)
    trained_at = models.DateTimeField(null=True, blank=True)
    mae = models.FloatField(null=True, blank=True, help_text='Mean Absolute Error')
    mse = models.FloatField(null=True, blank=True, help_text='Mean Squared Error')
    rmse = models.FloatField(null=True, blank=True, help_text='Root Mean Squared Error')
    mape = models.FloatField(null=True, blank=True, help_text='Mean Absolute Percentage Error')
    r2_score = models.FloatField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    model_file = models.CharField(max_length=500, blank=True)
    training_data_points = models.PositiveIntegerField(default=0)
    parameters = models.JSONField(default=dict)

    class Meta:
        ordering = ['-trained_at']
