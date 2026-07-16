"""
Products models: Product, Category, Brand, Unit, ProductImage
"""
import uuid
from django.db import models
from django.utils.text import slugify
from core.models import BaseModel, TimeStampedModel, UUIDModel


class Category(BaseModel):
    """Product category with hierarchical support"""
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    parent = models.ForeignKey(
        'self', null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='children'
    )
    image = models.ImageField(upload_to='categories/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['sort_order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Brand(BaseModel):
    """Product brand"""
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to='brands/', null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Unit(BaseModel):
    """Unit of measurement"""
    name = models.CharField(max_length=100, unique=True)
    abbreviation = models.CharField(max_length=20, unique=True)
    type = models.CharField(max_length=50, choices=[
        ('weight', 'Weight'),
        ('volume', 'Volume'),
        ('length', 'Length'),
        ('area', 'Area'),
        ('piece', 'Piece'),
        ('other', 'Other'),
    ])
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.abbreviation})"


class Product(BaseModel):
    """Main product model with all enterprise fields"""
    # Identification
    sku = models.CharField(max_length=100, unique=True, db_index=True)
    barcode = models.CharField(max_length=100, unique=True, null=True, blank=True, db_index=True)
    qr_code = models.CharField(max_length=255, null=True, blank=True)
    name = models.CharField(max_length=500, db_index=True)
    slug = models.SlugField(max_length=500, unique=True, blank=True)
    description = models.TextField(blank=True)
    short_description = models.CharField(max_length=500, blank=True)

    # Classification
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products')
    brand = models.ForeignKey(Brand, null=True, blank=True, on_delete=models.SET_NULL, related_name='products')
    unit = models.ForeignKey(Unit, on_delete=models.PROTECT, related_name='products')

    # Tax & Compliance
    hsn_code = models.CharField(max_length=20, blank=True, help_text='HSN/SAC code for GST')
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=18.00)

    # Pricing
    cost_price = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    selling_price = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    mrp = models.DecimalField(max_digits=15, decimal_places=2, default=0, help_text='Maximum Retail Price')
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    # Stock levels
    minimum_stock = models.PositiveIntegerField(default=10)
    maximum_stock = models.PositiveIntegerField(default=1000)
    reorder_point = models.PositiveIntegerField(default=20)
    reorder_quantity = models.PositiveIntegerField(default=50)
    safety_stock = models.PositiveIntegerField(default=5)

    # Physical attributes
    weight = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    weight_unit = models.CharField(max_length=10, default='kg')
    length = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    width = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    height = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    dimension_unit = models.CharField(max_length=10, default='cm')

    # Tracking
    is_batch_tracked = models.BooleanField(default=False)
    is_lot_tracked = models.BooleanField(default=False)
    is_expiry_tracked = models.BooleanField(default=False)
    is_serialized = models.BooleanField(default=False)
    shelf_life_days = models.PositiveIntegerField(null=True, blank=True)

    # Image
    image = models.ImageField(upload_to='products/%Y/%m/', null=True, blank=True)

    # Status
    status = models.CharField(max_length=20, choices=[
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('discontinued', 'Discontinued'),
        ('draft', 'Draft'),
    ], default='active', db_index=True)
    is_active = models.BooleanField(default=True)
    is_purchasable = models.BooleanField(default=True)
    is_sellable = models.BooleanField(default=True)

    # Metadata
    tags = models.JSONField(default=list, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        ordering = ['name']
        indexes = [
            models.Index(fields=['sku', 'status']),
            models.Index(fields=['category', 'status']),
            models.Index(fields=['name', 'status']),
        ]

    def __str__(self):
        return f"{self.sku} - {self.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.sku}-{self.name}")
        super().save(*args, **kwargs)

    @property
    def profit_margin(self):
        if self.cost_price > 0:
            return ((self.selling_price - self.cost_price) / self.cost_price) * 100
        return 0

    @property
    def discount_price(self):
        if self.discount_percentage > 0:
            discount = self.selling_price * self.discount_percentage / 100
            return self.selling_price - discount
        return self.selling_price


class ProductImage(TimeStampedModel):
    """Multiple images for a product"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/%Y/%m/')
    alt_text = models.CharField(max_length=255, blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_primary = models.BooleanField(default=False)

    class Meta:
        ordering = ['sort_order']


class ProductDocument(TimeStampedModel):
    """Product documents (specs, datasheets, etc.)"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='documents')
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='product_docs/%Y/%m/')
    file_type = models.CharField(max_length=50, blank=True)
    file_size = models.PositiveIntegerField(default=0)
    uploaded_by = models.ForeignKey(
        'accounts.User', null=True, on_delete=models.SET_NULL
    )

    def __str__(self):
        return f"{self.product.name} - {self.title}"
