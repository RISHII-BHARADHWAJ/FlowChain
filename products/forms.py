from django import forms
from products.models import Product


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'sku', 'barcode', 'name', 'description', 'short_description',
            'category', 'brand', 'unit', 'hsn_code', 'tax_rate',
            'cost_price', 'selling_price', 'mrp', 'discount_percentage',
            'minimum_stock', 'maximum_stock', 'reorder_point', 'reorder_quantity',
            'safety_stock', 'weight', 'weight_unit', 'length', 'width',
            'height', 'dimension_unit', 'is_batch_tracked', 'is_lot_tracked',
            'is_expiry_tracked', 'is_serialized', 'shelf_life_days',
            'image', 'status', 'is_active', 'is_purchasable', 'is_sellable',
            'notes'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'notes': forms.Textarea(attrs={'rows': 2}),
        }
