"""
Django Admin registrations for Products app
"""
from django.contrib import admin
from products.models import Category, Brand, Unit, Product, ProductImage, ProductDocument


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'parent', 'is_active', 'sort_order']
    list_filter = ['is_active', 'parent']
    search_fields = ['name', 'code']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ['name', 'abbreviation', 'type', 'is_active']
    list_filter = ['type', 'is_active']


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ['image', 'alt_text', 'sort_order', 'is_primary']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['sku', 'name', 'category', 'brand', 'cost_price', 'selling_price', 'status', 'is_active']
    list_filter = ['status', 'is_active', 'category', 'brand', 'is_batch_tracked', 'is_expiry_tracked']
    search_fields = ['sku', 'name', 'barcode', 'hsn_code']
    readonly_fields = ['id', 'slug', 'created_at', 'updated_at']
    inlines = [ProductImageInline]
    fieldsets = (
        ('Identification', {'fields': ('id', 'sku', 'barcode', 'qr_code', 'name', 'slug', 'description', 'short_description')}),
        ('Classification', {'fields': ('category', 'brand', 'unit', 'tags')}),
        ('Tax & Compliance', {'fields': ('hsn_code', 'tax_rate')}),
        ('Pricing', {'fields': ('cost_price', 'selling_price', 'mrp', 'discount_percentage')}),
        ('Stock Levels', {'fields': ('minimum_stock', 'maximum_stock', 'reorder_point', 'reorder_quantity', 'safety_stock')}),
        ('Physical', {'fields': ('weight', 'weight_unit', 'length', 'width', 'height', 'dimension_unit')}),
        ('Tracking', {'fields': ('is_batch_tracked', 'is_lot_tracked', 'is_expiry_tracked', 'is_serialized', 'shelf_life_days')}),
        ('Status', {'fields': ('status', 'is_active', 'is_purchasable', 'is_sellable')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )
