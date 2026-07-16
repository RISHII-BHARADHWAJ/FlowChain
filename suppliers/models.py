"""
Supplier models: Supplier, SupplierContact, SupplierDocument, SupplierPerformance
"""
import uuid
from django.db import models
from core.models import BaseModel, TimeStampedModel


class Supplier(BaseModel):
    """Supplier / Vendor model"""
    code = models.CharField(max_length=20, unique=True, db_index=True)
    name = models.CharField(max_length=255, db_index=True)
    legal_name = models.CharField(max_length=255, blank=True)
    type = models.CharField(max_length=30, choices=[
        ('manufacturer', 'Manufacturer'),
        ('distributor', 'Distributor'),
        ('wholesaler', 'Wholesaler'),
        ('retailer', 'Retailer'),
        ('importer', 'Importer'),
    ], default='distributor')

    # Tax & Legal
    gst_number = models.CharField(max_length=20, blank=True, db_index=True)
    pan_number = models.CharField(max_length=15, blank=True)
    tax_id = models.CharField(max_length=50, blank=True)

    # Contact
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    website = models.URLField(blank=True)
    contact_person = models.CharField(max_length=255, blank=True)

    # Address
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100, default='India')
    pincode = models.CharField(max_length=20)

    # Banking
    bank_name = models.CharField(max_length=100, blank=True)
    bank_account_number = models.CharField(max_length=50, blank=True)
    bank_ifsc_code = models.CharField(max_length=20, blank=True)
    bank_branch = models.CharField(max_length=100, blank=True)

    # Terms
    payment_terms_days = models.PositiveIntegerField(default=30)
    credit_limit = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    currency = models.CharField(max_length=10, default='INR')
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    # Rating & Performance
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0)
    total_orders = models.PositiveIntegerField(default=0)
    on_time_delivery_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    quality_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    # Balances
    outstanding_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    advance_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    # Status
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    is_preferred = models.BooleanField(default=False)
    blacklisted = models.BooleanField(default=False)
    blacklist_reason = models.TextField(blank=True)

    notes = models.TextField(blank=True)
    tags = models.JSONField(default=list, blank=True)

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['code', 'is_active']),
            models.Index(fields=['gst_number']),
        ]

    def __str__(self):
        return f"{self.code} - {self.name}"


class SupplierContact(TimeStampedModel):
    """Multiple contacts for a supplier"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='contacts')
    name = models.CharField(max_length=255)
    designation = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20)
    is_primary = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} ({self.supplier.name})"


class SupplierDocument(TimeStampedModel):
    """Documents associated with a supplier"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='documents')
    title = models.CharField(max_length=255)
    document_type = models.CharField(max_length=50, choices=[
        ('contract', 'Contract'),
        ('license', 'License'),
        ('certificate', 'Certificate'),
        ('tax_document', 'Tax Document'),
        ('other', 'Other'),
    ])
    file = models.FileField(upload_to='supplier_docs/%Y/%m/')
    expiry_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    uploaded_by = models.ForeignKey('accounts.User', null=True, on_delete=models.SET_NULL)


class SupplierPerformanceRecord(TimeStampedModel):
    """Periodic performance evaluation for suppliers"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='performance_records')
    period = models.CharField(max_length=20)  # e.g., "2024-Q1"
    on_time_delivery = models.DecimalField(max_digits=5, decimal_places=2)
    quality_score = models.DecimalField(max_digits=5, decimal_places=2)
    pricing_score = models.DecimalField(max_digits=5, decimal_places=2)
    communication_score = models.DecimalField(max_digits=5, decimal_places=2)
    overall_score = models.DecimalField(max_digits=5, decimal_places=2)
    total_orders = models.PositiveIntegerField(default=0)
    total_value = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    defect_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    return_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    evaluated_by = models.ForeignKey('accounts.User', null=True, on_delete=models.SET_NULL)

    class Meta:
        unique_together = ['supplier', 'period']
        ordering = ['-period']
