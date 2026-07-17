"""
Inventory models: StockLevel, StockMovement, Batch, InventoryAdjustment
"""
import uuid
from django.db import models
from django.utils import timezone
from core.models import BaseModel, TimeStampedModel


class StockLevel(BaseModel):
    """Current stock level for a product in a warehouse"""
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, related_name='stock_levels')
    warehouse = models.ForeignKey('warehouses.Warehouse', on_delete=models.CASCADE, related_name='stock_levels')
    location = models.ForeignKey(
        'warehouses.WarehouseLocation', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='stock_levels'
    )

    # Quantities
    quantity_on_hand = models.DecimalField(max_digits=15, decimal_places=3, default=0)
    quantity_reserved = models.DecimalField(max_digits=15, decimal_places=3, default=0)
    quantity_in_transit = models.DecimalField(max_digits=15, decimal_places=3, default=0)
    quantity_on_order = models.DecimalField(max_digits=15, decimal_places=3, default=0)

    # Valuation
    average_cost = models.DecimalField(max_digits=15, decimal_places=4, default=0)
    total_value = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    # Counts
    last_counted_at = models.DateTimeField(null=True, blank=True)
    last_counted_by = models.ForeignKey(
        'accounts.User', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='stock_counts'
    )
    last_movement_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ['product', 'warehouse']
        verbose_name = 'Stock Level'
        indexes = [
            models.Index(fields=['product', 'warehouse']),
            models.Index(fields=['quantity_on_hand']),
        ]

    def __str__(self):
        return f"{self.product.sku} @ {self.warehouse.code}: {self.quantity_on_hand}"

    @property
    def quantity_available(self):
        return self.quantity_on_hand - self.quantity_reserved

    @property
    def is_low_stock(self):
        return self.quantity_on_hand <= self.product.reorder_point

    @property
    def is_out_of_stock(self):
        return self.quantity_on_hand <= 0

    @property
    def is_over_stocked(self):
        return self.quantity_on_hand > self.product.maximum_stock


class StockMovement(TimeStampedModel):
    """Every stock movement (in/out/adjustment/transfer)"""
    MOVEMENT_TYPES = [
        ('receipt', 'Stock Receipt'),
        ('sale', 'Sale'),
        ('transfer_in', 'Transfer In'),
        ('transfer_out', 'Transfer Out'),
        ('adjustment_add', 'Adjustment - Add'),
        ('adjustment_remove', 'Adjustment - Remove'),
        ('return_in', 'Return In'),
        ('return_out', 'Return Out'),
        ('opening', 'Opening Balance'),
        ('write_off', 'Write Off'),
        ('cycle_count', 'Cycle Count'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, related_name='movements')
    warehouse = models.ForeignKey('warehouses.Warehouse', on_delete=models.CASCADE, related_name='movements')
    movement_type = models.CharField(max_length=30, choices=MOVEMENT_TYPES, db_index=True)
    reference_number = models.CharField(max_length=100, blank=True, db_index=True)
    reference_type = models.CharField(max_length=50, blank=True)  # purchase_order, sale_order, etc.

    # Quantities
    quantity = models.DecimalField(max_digits=15, decimal_places=3)
    quantity_before = models.DecimalField(max_digits=15, decimal_places=3, default=0)
    quantity_after = models.DecimalField(max_digits=15, decimal_places=3, default=0)

    # Costing
    unit_cost = models.DecimalField(max_digits=15, decimal_places=4, default=0)
    total_cost = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    # Batch/Lot
    batch = models.ForeignKey('Batch', null=True, blank=True, on_delete=models.SET_NULL)
    location = models.ForeignKey(
        'warehouses.WarehouseLocation', null=True, blank=True, on_delete=models.SET_NULL
    )

    performed_by = models.ForeignKey(
        'accounts.User', null=True, on_delete=models.SET_NULL, related_name='stock_movements'
    )
    notes = models.TextField(blank=True)
    is_approved = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['product', 'warehouse', 'movement_type']),
            models.Index(fields=['reference_number']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.movement_type} | {self.product.sku} | {self.quantity}"


class Batch(TimeStampedModel):
    """Batch/Lot tracking for products"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, related_name='batches')
    warehouse = models.ForeignKey('warehouses.Warehouse', on_delete=models.CASCADE, related_name='batches')
    batch_number = models.CharField(max_length=100, db_index=True)
    lot_number = models.CharField(max_length=100, blank=True, db_index=True)
    manufacture_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True, db_index=True)
    quantity = models.DecimalField(max_digits=15, decimal_places=3, default=0)
    unit_cost = models.DecimalField(max_digits=15, decimal_places=4, default=0)
    supplier = models.ForeignKey(
        'suppliers.Supplier', null=True, blank=True, on_delete=models.SET_NULL
    )
    status = models.CharField(max_length=20, choices=[
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('quarantine', 'Quarantine'),
        ('consumed', 'Consumed'),
    ], default='active')

    class Meta:
        unique_together = ['product', 'batch_number']
        ordering = ['expiry_date']

    def __str__(self):
        return f"{self.product.sku} | Batch: {self.batch_number}"

    @property
    def is_expired(self):
        if self.expiry_date:
            return timezone.now().date() > self.expiry_date
        return False

    @property
    def days_to_expiry(self):
        if self.expiry_date:
            delta = self.expiry_date - timezone.now().date()
            return delta.days
        return None


class InventoryAdjustment(BaseModel):
    """Manual inventory adjustment"""
    adjustment_number = models.CharField(max_length=50, unique=True)
    warehouse = models.ForeignKey('warehouses.Warehouse', on_delete=models.PROTECT)
    adjustment_type = models.CharField(max_length=30, choices=[
        ('cycle_count', 'Cycle Count'),
        ('damage', 'Damage'),
        ('theft', 'Theft'),
        ('found', 'Found'),
        ('write_off', 'Write Off'),
        ('correction', 'Correction'),
    ])
    status = models.CharField(max_length=20, choices=[
        ('draft', 'Draft'),
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], default='draft')
    reason = models.TextField()
    adjusted_by = models.ForeignKey(
        'accounts.User', on_delete=models.PROTECT, related_name='adjustments'
    )
    approved_by = models.ForeignKey(
        'accounts.User', null=True, blank=True, on_delete=models.SET_NULL,
        related_name='approved_adjustments'
    )
    approved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']


class InventoryAdjustmentItem(TimeStampedModel):
    """Items in an inventory adjustment"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    adjustment = models.ForeignKey(InventoryAdjustment, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('products.Product', on_delete=models.PROTECT)
    quantity_before = models.DecimalField(max_digits=15, decimal_places=3)
    quantity_after = models.DecimalField(max_digits=15, decimal_places=3)
    reason = models.CharField(max_length=500, blank=True)

    @property
    def quantity_difference(self):
        return self.quantity_after - self.quantity_before


class CycleCounting(BaseModel):
    """Cycle counting / physical inventory count"""
    count_number = models.CharField(max_length=50, unique=True)
    warehouse = models.ForeignKey('warehouses.Warehouse', on_delete=models.PROTECT)
    count_type = models.CharField(max_length=20, choices=[
        ('full', 'Full Count'),
        ('partial', 'Partial Count'),
        ('abc_a', 'ABC - Class A'),
        ('abc_b', 'ABC - Class B'),
        ('abc_c', 'ABC - Class C'),
    ])
    scheduled_date = models.DateField()
    completed_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], default='scheduled')
    assigned_to = models.ForeignKey(
        'accounts.User', null=True, on_delete=models.SET_NULL
    )
    variance_value = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']
