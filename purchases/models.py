"""
Purchase models: PurchaseRequisition, PurchaseOrder, GRN, PurchaseReturn
"""
import uuid
from django.db import models
from core.models import BaseModel, TimeStampedModel


class PurchaseRequisition(BaseModel):
    PR_STATUS = [
        ('draft','Draft'),('pending','Pending Approval'),
        ('approved','Approved'),('rejected','Rejected'),
        ('po_created','PO Created'),('cancelled','Cancelled'),
    ]
    pr_number = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=255)
    warehouse = models.ForeignKey('warehouses.Warehouse', on_delete=models.PROTECT)
    requested_by = models.ForeignKey('accounts.User', on_delete=models.PROTECT, related_name='requisitions')
    approved_by = models.ForeignKey('accounts.User', null=True, blank=True, on_delete=models.SET_NULL, related_name='approved_requisitions')
    status = models.CharField(max_length=20, choices=PR_STATUS, default='draft', db_index=True)
    required_date = models.DateField(null=True, blank=True)
    priority = models.CharField(max_length=20, choices=[('low','Low'),('medium','Medium'),('high','High'),('urgent','Urgent')], default='medium')
    justification = models.TextField(blank=True)
    rejection_reason = models.TextField(blank=True)
    estimated_cost = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"PR-{self.pr_number}: {self.title}"


class PurchaseRequisitionItem(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    requisition = models.ForeignKey(PurchaseRequisition, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('products.Product', on_delete=models.PROTECT)
    quantity = models.DecimalField(max_digits=15, decimal_places=3)
    unit_price = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    notes = models.CharField(max_length=500, blank=True)


class PurchaseOrder(BaseModel):
    PO_STATUS = [
        ('draft','Draft'),('pending','Pending Approval'),('approved','Approved'),
        ('sent','Sent to Supplier'),('partial','Partially Received'),
        ('completed','Completed'),('rejected','Rejected'),('cancelled','Cancelled'),
    ]
    po_number = models.CharField(max_length=50, unique=True, db_index=True)
    supplier = models.ForeignKey('suppliers.Supplier', on_delete=models.PROTECT, related_name='purchase_orders')
    warehouse = models.ForeignKey('warehouses.Warehouse', on_delete=models.PROTECT)
    requisition = models.ForeignKey(PurchaseRequisition, null=True, blank=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=20, choices=PO_STATUS, default='draft', db_index=True)
    priority = models.CharField(max_length=20, choices=[('low','Low'),('medium','Medium'),('high','High'),('urgent','Urgent')], default='medium')
    order_date = models.DateField()
    expected_delivery_date = models.DateField(null=True, blank=True)
    actual_delivery_date = models.DateField(null=True, blank=True)
    subtotal = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    shipping_cost = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    paid_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    currency = models.CharField(max_length=10, default='INR')
    created_by = models.ForeignKey('accounts.User', on_delete=models.PROTECT, related_name='created_purchase_orders')
    approved_by = models.ForeignKey('accounts.User', null=True, blank=True, on_delete=models.SET_NULL, related_name='approved_purchase_orders')
    approved_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    payment_terms = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['status','supplier']), models.Index(fields=['po_number'])]

    def __str__(self):
        return f"PO-{self.po_number} | {self.supplier.name}"

    @property
    def balance_due(self):
        return self.total_amount - self.paid_amount


class PurchaseOrderItem(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('products.Product', on_delete=models.PROTECT)
    quantity_ordered = models.DecimalField(max_digits=15, decimal_places=3)
    quantity_received = models.DecimalField(max_digits=15, decimal_places=3, default=0)
    unit_price = models.DecimalField(max_digits=15, decimal_places=2)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    notes = models.CharField(max_length=500, blank=True)


class GoodsReceiptNote(BaseModel):
    grn_number = models.CharField(max_length=50, unique=True)
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.PROTECT, related_name='grns')
    warehouse = models.ForeignKey('warehouses.Warehouse', on_delete=models.PROTECT)
    supplier = models.ForeignKey('suppliers.Supplier', on_delete=models.PROTECT)
    received_date = models.DateField()
    supplier_invoice_number = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=[
        ('draft','Draft'),('pending','Pending QC'),('approved','Approved'),('rejected','Rejected'),
    ], default='pending')
    received_by = models.ForeignKey('accounts.User', on_delete=models.PROTECT, related_name='received_grns')
    notes = models.TextField(blank=True)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    def __str__(self):
        return f"GRN-{self.grn_number}"


class GoodsReceiptNoteItem(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    grn = models.ForeignKey(GoodsReceiptNote, on_delete=models.CASCADE, related_name='items')
    po_item = models.ForeignKey(PurchaseOrderItem, on_delete=models.PROTECT)
    product = models.ForeignKey('products.Product', on_delete=models.PROTECT)
    quantity_received = models.DecimalField(max_digits=15, decimal_places=3)
    quantity_accepted = models.DecimalField(max_digits=15, decimal_places=3, default=0)
    quantity_rejected = models.DecimalField(max_digits=15, decimal_places=3, default=0)
    unit_price = models.DecimalField(max_digits=15, decimal_places=2)
    batch_number = models.CharField(max_length=100, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    rejection_reason = models.CharField(max_length=500, blank=True)


class VendorInvoice(BaseModel):
    invoice_number = models.CharField(max_length=100, unique=True)
    vendor_invoice_number = models.CharField(max_length=100)
    supplier = models.ForeignKey('suppliers.Supplier', on_delete=models.PROTECT)
    purchase_order = models.ForeignKey(PurchaseOrder, null=True, blank=True, on_delete=models.SET_NULL)
    invoice_date = models.DateField()
    due_date = models.DateField()
    subtotal = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    paid_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=[
        ('pending','Pending'),('partial','Partially Paid'),
        ('paid','Paid'),('overdue','Overdue'),('disputed','Disputed'),
    ], default='pending')
    notes = models.TextField(blank=True)

    @property
    def balance_due(self):
        return self.total_amount - self.paid_amount
