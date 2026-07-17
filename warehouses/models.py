"""
Warehouse models: Warehouse, Location, Zone, Transfer
"""
import uuid
from django.db import models
from core.models import BaseModel, TimeStampedModel


class Warehouse(BaseModel):
    """Warehouse/Storage facility model"""
    code = models.CharField(max_length=20, unique=True, db_index=True)
    name = models.CharField(max_length=255, db_index=True)
    type = models.CharField(max_length=30, choices=[
        ('owned', 'Owned'),
        ('leased', 'Leased'),
        ('third_party', 'Third Party'),
        ('virtual', 'Virtual'),
    ], default='owned')
    description = models.TextField(blank=True)

    # Location
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100, default='India')
    pincode = models.CharField(max_length=20)
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)

    # Capacity
    total_capacity = models.DecimalField(max_digits=15, decimal_places=2, help_text='In square feet or cubic feet')
    capacity_unit = models.CharField(max_length=20, default='sqft')
    current_utilization = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    # Contact
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    manager = models.ForeignKey(
        'accounts.User',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='managed_warehouses',
    )

    # Status
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Warehouse'
        ordering = ['name']
        indexes = [models.Index(fields=['code', 'is_active'])]

    def __str__(self):
        return f"{self.code} - {self.name}"

    @property
    def utilization_percentage(self):
        if self.total_capacity > 0:
            return (self.current_utilization / self.total_capacity) * 100
        return 0

    @property
    def available_capacity(self):
        return self.total_capacity - self.current_utilization

    def get_full_address(self):
        parts = [self.address_line1]
        if self.address_line2:
            parts.append(self.address_line2)
        parts.extend([self.city, self.state, self.country, self.pincode])
        return ', '.join(parts)


class WarehouseZone(BaseModel):
    """Zone/Area within a warehouse"""
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='zones')
    code = models.CharField(max_length=20)
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=30, choices=[
        ('storage', 'Storage'),
        ('receiving', 'Receiving'),
        ('dispatch', 'Dispatch'),
        ('quarantine', 'Quarantine'),
        ('cold_storage', 'Cold Storage'),
    ])
    capacity = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    temperature_controlled = models.BooleanField(default=False)
    min_temperature = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    max_temperature = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ['warehouse', 'code']

    def __str__(self):
        return f"{self.warehouse.code}/{self.code} - {self.name}"


class WarehouseLocation(BaseModel):
    """Specific storage location (bin/rack/shelf) in a zone"""
    zone = models.ForeignKey(WarehouseZone, on_delete=models.CASCADE, related_name='locations')
    code = models.CharField(max_length=50)
    barcode = models.CharField(max_length=100, unique=True, null=True, blank=True)
    row = models.CharField(max_length=10, blank=True)
    column = models.CharField(max_length=10, blank=True)
    level = models.CharField(max_length=10, blank=True)
    max_weight = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_occupied = models.BooleanField(default=False)

    class Meta:
        unique_together = ['zone', 'code']

    def __str__(self):
        return f"{self.zone.code}/{self.code}"


class StockTransfer(BaseModel):
    """Stock transfer between warehouses"""
    TRANSFER_STATUS = [
        ('draft', 'Draft'),
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('in_transit', 'In Transit'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ]

    transfer_number = models.CharField(max_length=50, unique=True)
    from_warehouse = models.ForeignKey(
        Warehouse, on_delete=models.PROTECT, related_name='outgoing_transfers'
    )
    to_warehouse = models.ForeignKey(
        Warehouse, on_delete=models.PROTECT, related_name='incoming_transfers'
    )
    status = models.CharField(max_length=20, choices=TRANSFER_STATUS, default='draft', db_index=True)
    requested_by = models.ForeignKey(
        'accounts.User', on_delete=models.PROTECT, related_name='requested_transfers'
    )
    approved_by = models.ForeignKey(
        'accounts.User', null=True, blank=True, on_delete=models.SET_NULL,
        related_name='approved_transfers'
    )
    expected_date = models.DateField(null=True, blank=True)
    completed_date = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    rejection_reason = models.TextField(blank=True)
    shipping_carrier = models.CharField(max_length=100, blank=True)
    tracking_number = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['status', 'from_warehouse', 'to_warehouse'])]

    def __str__(self):
        return f"Transfer {self.transfer_number}: {self.from_warehouse.code} → {self.to_warehouse.code}"


class StockTransferItem(TimeStampedModel):
    """Individual items in a stock transfer"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    transfer = models.ForeignKey(StockTransfer, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('products.Product', on_delete=models.PROTECT)
    quantity_requested = models.DecimalField(max_digits=15, decimal_places=3)
    quantity_shipped = models.DecimalField(max_digits=15, decimal_places=3, default=0)
    quantity_received = models.DecimalField(max_digits=15, decimal_places=3, default=0)
    unit_cost = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    notes = models.CharField(max_length=500, blank=True)

    def __str__(self):
        return f"{self.transfer.transfer_number} - {self.product.name}"
