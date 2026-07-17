"""Sales models: Customer, SalesOrder, Invoice, Payment, SalesReturn"""
import uuid
from django.db import models
from core.models import BaseModel, TimeStampedModel


class Customer(BaseModel):
    code = models.CharField(max_length=20, unique=True, db_index=True)
    name = models.CharField(max_length=255, db_index=True)
    type = models.CharField(max_length=20, choices=[
        ('individual','Individual'),('business','Business'),('government','Government'),
    ], default='business')
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    gst_number = models.CharField(max_length=20, blank=True)
    pan_number = models.CharField(max_length=15, blank=True)
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100, default='India')
    pincode = models.CharField(max_length=20)
    credit_limit = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    payment_terms_days = models.PositiveIntegerField(default=30)
    outstanding_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_orders = models.PositiveIntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.code} - {self.name}"


class SalesOrder(BaseModel):
    ORDER_STATUS = [
        ('draft','Draft'),('confirmed','Confirmed'),('processing','Processing'),
        ('ready','Ready to Dispatch'),('dispatched','Dispatched'),
        ('delivered','Delivered'),('cancelled','Cancelled'),('returned','Returned'),
    ]
    order_number = models.CharField(max_length=50, unique=True, db_index=True)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name='sales_orders')
    warehouse = models.ForeignKey('warehouses.Warehouse', on_delete=models.PROTECT)
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='draft', db_index=True)
    priority = models.CharField(max_length=20, choices=[
        ('low','Low'),('medium','Medium'),('high','High'),('urgent','Urgent')
    ], default='medium')
    order_date = models.DateField()
    required_date = models.DateField(null=True, blank=True)
    dispatch_date = models.DateTimeField(null=True, blank=True)
    delivery_date = models.DateTimeField(null=True, blank=True)
    subtotal = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    shipping_cost = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    paid_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    currency = models.CharField(max_length=10, default='INR')
    salesperson = models.ForeignKey('accounts.User', on_delete=models.PROTECT, related_name='sales_orders')
    shipping_address = models.TextField(blank=True)
    shipping_carrier = models.CharField(max_length=100, blank=True)
    tracking_number = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    cancellation_reason = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status','customer']),
            models.Index(fields=['order_number']),
        ]

    def __str__(self):
        return f"SO-{self.order_number} | {self.customer.name}"

    @property
    def balance_due(self):
        return self.total_amount - self.paid_amount


class SalesOrderItem(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sales_order = models.ForeignKey(SalesOrder, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('products.Product', on_delete=models.PROTECT)
    quantity_ordered = models.DecimalField(max_digits=15, decimal_places=3)
    quantity_dispatched = models.DecimalField(max_digits=15, decimal_places=3, default=0)
    quantity_returned = models.DecimalField(max_digits=15, decimal_places=3, default=0)
    unit_price = models.DecimalField(max_digits=15, decimal_places=2)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    notes = models.CharField(max_length=500, blank=True)


class Invoice(BaseModel):
    INVOICE_STATUS = [
        ('draft','Draft'),('sent','Sent'),
        ('paid','Paid'),('partial','Partially Paid'),
        ('overdue','Overdue'),('cancelled','Cancelled'),
    ]
    invoice_number = models.CharField(max_length=50, unique=True, db_index=True)
    sales_order = models.ForeignKey(SalesOrder, null=True, blank=True, on_delete=models.SET_NULL)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name='invoices')
    invoice_date = models.DateField()
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=INVOICE_STATUS, default='draft', db_index=True)
    subtotal = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    cgst_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    sgst_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    igst_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    paid_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    currency = models.CharField(max_length=10, default='INR')
    created_by = models.ForeignKey('accounts.User', on_delete=models.PROTECT)
    pdf_file = models.FileField(upload_to='invoices/%Y/%m/', null=True, blank=True)
    notes = models.TextField(blank=True)
    terms_conditions = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"INV-{self.invoice_number}"

    @property
    def balance_due(self):
        return self.total_amount - self.paid_amount

    @property
    def is_overdue(self):
        from django.utils import timezone
        if self.status not in ('paid', 'cancelled'):
            return timezone.now().date() > self.due_date
        return False


class Payment(BaseModel):
    PAYMENT_METHODS = [
        ('cash','Cash'),('bank_transfer','Bank Transfer'),
        ('upi','UPI'),('cheque','Cheque'),
        ('credit_card','Credit Card'),('debit_card','Debit Card'),
    ]
    payment_number = models.CharField(max_length=50, unique=True)
    invoice = models.ForeignKey(Invoice, on_delete=models.PROTECT, related_name='payments')
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    payment_date = models.DateField()
    payment_method = models.CharField(max_length=30, choices=PAYMENT_METHODS)
    reference_number = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    received_by = models.ForeignKey('accounts.User', on_delete=models.PROTECT)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"PMT-{self.payment_number}: {self.amount}"


class DeliveryNote(BaseModel):
    dn_number = models.CharField(max_length=50, unique=True)
    sales_order = models.ForeignKey(SalesOrder, on_delete=models.PROTECT, related_name='delivery_notes')
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    dispatch_date = models.DateField()
    expected_delivery_date = models.DateField(null=True, blank=True)
    actual_delivery_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[
        ('prepared','Prepared'),('dispatched','Dispatched'),
        ('delivered','Delivered'),('failed','Failed'),
    ], default='prepared')
    shipping_carrier = models.CharField(max_length=100, blank=True)
    tracking_number = models.CharField(max_length=100, blank=True)
    driver_name = models.CharField(max_length=100, blank=True)
    vehicle_number = models.CharField(max_length=50, blank=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey('accounts.User', on_delete=models.PROTECT)

    def __str__(self):
        return f"DN-{self.dn_number}"


class SalesReturn(BaseModel):
    return_number = models.CharField(max_length=50, unique=True)
    sales_order = models.ForeignKey(SalesOrder, on_delete=models.PROTECT)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    warehouse = models.ForeignKey('warehouses.Warehouse', on_delete=models.PROTECT)
    return_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=[
        ('pending','Pending'),('approved','Approved'),
        ('completed','Completed'),('rejected','Rejected'),
    ], default='pending')
    refund_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    created_by = models.ForeignKey('accounts.User', on_delete=models.PROTECT)

    def __str__(self):
        return f"SR-{self.return_number}"
